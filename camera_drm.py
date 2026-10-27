import os
import sys
import mmap
import fcntl
import ctypes
import cv2
import numpy as np

# HUSKYLENS 2 display configuration
WIDTH = 480
HEIGHT = 640
VIDEO_DEVICE = "/dev/video2"

# DRM identifiers from your device's modetest output
DRM_DEVICE = "/dev/dri/card0"
PLANE_ID = 34
CRTC_ID = 52

# Linux ioctl helpers
def ioc(direction, kind, number, size):
    return (
        (direction << 30)
        | (size << 16)
        | (kind << 8)
        | number
    )

def iowr(number, size):
    return ioc(3, ord("d"), number, size)

# DRM dumb-buffer structures
class CreateDumb(ctypes.Structure):
    _fields_ = [
        ("height", ctypes.c_uint32),
        ("width", ctypes.c_uint32),
        ("bpp", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("handle", ctypes.c_uint32),
        ("pitch", ctypes.c_uint32),
        ("size", ctypes.c_uint64),
    ]

class MapDumb(ctypes.Structure):
    _fields_ = [
        ("handle", ctypes.c_uint32),
        ("pad", ctypes.c_uint32),
        ("offset", ctypes.c_uint64),
    ]

class DestroyDumb(ctypes.Structure):
    _fields_ = [
        ("handle", ctypes.c_uint32),
        ("pad", ctypes.c_uint32),
    ]

CREATE_DUMB = iowr(0xB2, ctypes.sizeof(CreateDumb))
MAP_DUMB = iowr(0xB3, ctypes.sizeof(MapDumb))
DESTROY_DUMB = iowr(0xB4, ctypes.sizeof(DestroyDumb))

# DRM pixel format: ARGB8888
def fourcc(a, b, c, d):
    return (
        ord(a)
        | (ord(b) << 8)
        | (ord(c) << 16)
        | (ord(d) << 24)
    )

FORMAT_ARGB8888 = fourcc("A", "R", "2", "4")

libdrm = ctypes.CDLL("libdrm.so")

libdrm.drmModeAddFB2.argtypes = [
    ctypes.c_int,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_uint32,
]
libdrm.drmModeAddFB2.restype = ctypes.c_int

libdrm.drmModeSetPlane.argtypes = [
    ctypes.c_int,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_int32,
    ctypes.c_int32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
]
libdrm.drmModeSetPlane.restype = ctypes.c_int

drm_fd = None
camera = None
fb_map = None
fb_id = ctypes.c_uint32(0)
buffer = None
handle = 0

try:
    # Open the camera
    print("Opening camera:", VIDEO_DEVICE)
    camera = cv2.VideoCapture(VIDEO_DEVICE, cv2.CAP_V4L2)

    if not camera.isOpened():
        raise RuntimeError(
            f"Cannot open {VIDEO_DEVICE}. Try /dev/video2 or /dev/video3."
        )

    ok, test_frame = camera.read()
    if not ok or test_frame is None:
        raise RuntimeError("Camera opened, but no frame was received.")

    print("Camera frame:", test_frame.shape)

    # Open DRM device
    drm_fd = os.open(DRM_DEVICE, os.O_RDWR | os.O_CLOEXEC)

    # Allocate a 32-bit dumb buffer
    create = CreateDumb()
    create.width = WIDTH
    create.height = HEIGHT
    create.bpp = 32

    fcntl.ioctl(drm_fd, CREATE_DUMB, create, True)

    handle = create.handle
    pitch = create.pitch
    buffer_size = create.size

    print("DRM buffer:", WIDTH, "x", HEIGHT)
    print("Pitch:", pitch, "bytes")
    print("Buffer size:", buffer_size, "bytes")

    # Map the buffer into Python
    mapping = MapDumb()
    mapping.handle = handle

    fcntl.ioctl(drm_fd, MAP_DUMB, mapping, True)

    fb_map = mmap.mmap(
        drm_fd,
        buffer_size,
        flags=mmap.MAP_SHARED,
        prot=mmap.PROT_READ | mmap.PROT_WRITE,
        offset=mapping.offset,
    )

    # Register the buffer as a framebuffer
    handles = (ctypes.c_uint32 * 4)(handle, 0, 0, 0)
    pitches = (ctypes.c_uint32 * 4)(pitch, 0, 0, 0)
    offsets = (ctypes.c_uint32 * 4)(0, 0, 0, 0)

    result = libdrm.drmModeAddFB2(
        drm_fd,
        WIDTH,
        HEIGHT,
        FORMAT_ARGB8888,
        handles,
        pitches,
        offsets,
        ctypes.byref(fb_id),
        0,
    )

    if result != 0:
        raise RuntimeError(f"drmModeAddFB2 failed: {result}")

    # Display the framebuffer on the screen
    result = libdrm.drmModeSetPlane(
        drm_fd,
        PLANE_ID,
        CRTC_ID,
        fb_id.value,
        0,
        0,
        0,
        WIDTH,
        HEIGHT,
        0,
        0,
        WIDTH << 16,
        HEIGHT << 16,
    )

    if result != 0:
        raise RuntimeError(f"drmModeSetPlane failed: {result}")

    # Each row includes any padding required by DRM
    destination = np.ndarray(
        shape=(HEIGHT, pitch),
        dtype=np.uint8,
        buffer=fb_map,
    )

    print("Live camera feed running. Press Ctrl+C to stop.")

    while True:
        ok, frame = camera.read()

        if not ok or frame is None:
            continue

        # Rotate the camera image for the portrait display
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        blur = cv2.GaussianBlur(frame, (5,5), 10)
        edges = cv2.Canny(blur, threshold1=71, threshold2=64)

        # Resize camera image to the left half
        camera_img = cv2.resize(frame, (240, 320))
        camera_img1 = cv2.resize(blur, (240, 320))
        camera_img2 = cv2.resize(frame, (240, 320))
        camera_img3 = cv2.resize(frame, (240, 320))

        # Create a black 480x640 canvas
        screen = np.zeros((640, 480, 3), dtype=np.uint8)

        # Put the camera image on the left
        screen[0:320, 0:240] = camera_img
        screen[0:320, 240:480] = camera_img1
        screen[320:640, 0:240] = camera_img2
        screen[320:640, 240:480] = camera_img3

        # Convert BGR to BGRA for the DRM framebuffer
        frame_bgra = cv2.cvtColor(screen, cv2.COLOR_BGR2BGRA)

        # Write the complete screen image
        destination[:, :WIDTH * 4] = frame_bgra.reshape(
        HEIGHT, WIDTH * 4
        )

except KeyboardInterrupt:
    print("\nStopping camera feed.")

except Exception as exc:
    print("ERROR:", exc)
    sys.exit_code = 1

finally:
    if camera is not None:
        camera.release()

    if fb_map is not None:
        fb_map.close()

    if drm_fd is not None:
        if fb_id.value:
            libdrm.drmModeRmFB(drm_fd, fb_id.value)

        if handle:
            destroy = DestroyDumb()
            destroy.handle = handle
            try:
                fcntl.ioctl(drm_fd, DESTROY_DUMB, destroy, True)
            except OSError:
                pass

        os.close(drm_fd)
