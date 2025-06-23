



import threading
import time

from Core.audio import AudioThreadManager
from FlowControl.main import Controller
from Interface.main import Interface
from Core.main import Core
from object_detection_and_tracking import main

event_stop_signal = threading.Event()
camera_available_event = threading.Event()
frame_reader = None
track_capture = None
detection_inference_obj = None
frame_reader_thread = None
detection_inference_thread = None
track_capture_thread = None
monitor_thread = None
tracker_class = None





def gui_of_ALPR():
    """
    GUI thread: Starts the application and runs the main UI loop.
    """
    global tracker_class
    obj_Interface = Interface()
    obj_core = Core()
    obj_Controller = Controller(obj_core, obj_Interface)
    obj_Controller.start_application()
    obj_Interface.start_mainloop()


def _main():
    global tracker_class
    try:
        obj_audio= AudioThreadManager()
        thread_audio_handle = threading.Thread(target=obj_audio.run, daemon=True)
        thread_audio_handle.start()

        thread_gui = threading.Thread(target=gui_of_ALPR, daemon=True)
        thread_gui.start()

        time.sleep(2)
        thread_gui_object = threading.Thread(target=main, daemon=True)
        thread_gui_object.start()

        # Monitor for a termination signal (e.g., Ctrl+C)
        while thread_gui.is_alive():
            thread_gui.join(timeout=1.0)
            if event_stop_signal.is_set():
                break

    except KeyboardInterrupt:
        print("Received termination signal, shutting down...")
        event_stop_signal.set()  # Signal all threads to stop
    finally:
        # Wait for threads to finish
        thread_gui_object.join(timeout=2.0)
        thread_gui.join(timeout=2.0)
        thread_audio_handle.join(timeout=2.0)

        print("All threads terminated")

if __name__ == "__main__":
    _main()


