import evdev
import threading
import queue

TOUCH_DEVICE = "/dev/input/event0"

# Display dimensions
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640

touch_queue = queue.Queue()

def touch_worker():
    device = evdev.InputDevice(TOUCH_DEVICE)

    raw_x = 0
    raw_y = 0
    touching = False

    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            if event.code == evdev.ecodes.ABS_MT_POSITION_X:
                raw_x = event.value

            elif event.code == evdev.ecodes.ABS_MT_POSITION_Y:
                raw_y = event.value

            elif event.code == evdev.ecodes.ABS_X:
                raw_x = event.value

            elif event.code == evdev.ecodes.ABS_Y:
                raw_y = event.value

        elif event.type == evdev.ecodes.EV_KEY:
            if event.code == evdev.ecodes.BTN_TOUCH:
                touching = bool(event.value)

                if touching:
                    # Rotate raw landscape coordinates to portrait.
                    x = SCREEN_WIDTH - 1 - round(
                        raw_y * (SCREEN_WIDTH - 1) / 479
                    )
                    y = round(
                        raw_x * (SCREEN_HEIGHT - 1) / 639
                    )

                    touch_queue.put((x, y))

def start_touchscreen():
    thread = threading.Thread(target=touch_worker, daemon=True)
    thread.start()

def get_touch():
    """Return the latest touch as (x, y), or None."""
    latest = None

    while not touch_queue.empty():
        latest = touch_queue.get_nowait()

    return latest
