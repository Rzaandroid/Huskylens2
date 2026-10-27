import time
import os
import sys
import mmap
import fcntl
import ctypes
import cv2
import numpy as np
from touchscreen import start_touchscreen, get_touch
import fnmatch

a=255
gap=50

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

    start_touchscreen()
    # Create a black canvas (no camera required)
    screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    dir_path = r'/root/MyProjects'
    filenames = fnmatch.filter(os.listdir(dir_path), '*.sh')
    for filename in filenames:
        print(filename)

    print('File Count:', len(filenames))                           
    count = len(filenames)
    print('File Count:', count)

    while True:
        touch = get_touch()

        if touch is not None:
            x, y = touch

            print("Screen touch:", x, y)

            if(x<480-50 and x>480-50-100 and y>50 and y<50+100):
                a=0
                print("TOUCHED")
                os.system(filenames[0])

            if(x<480-50 and x>480-50-100 and y>50+gap and y<50+100+gap):
                a=0
                print("TOUCHED")   
                os.system(filenames[1]) 

            # Draw a red circle where the touch was detected
            cv2.circle(screen, (x, y), 10, (0, 0, 255), -1)
        
        for n in range(count):
            cv2.rectangle(screen, (480-50, 50+gap), (480-50-100, 50+100+gap), (a, 255, a), 3)                                           
            cv2.putText(screen,filenames[n],(480-50-100,50+100+20+gap),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),2,cv2.LINE_AA) 
            if gap<150*3-1:
                gap = gap+100

        # Convert BGR to BGRA
        frame_bgra = cv2.cvtColor(screen, cv2.COLOR_BGR2BGRA)

        # Copy the image into your existing DRM framebuffer
        destination[:, :WIDTH * 4] = frame_bgra.reshape(
            HEIGHT, WIDTH * 4
        )

        time.sleep(0.03)

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
