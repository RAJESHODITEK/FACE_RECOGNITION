#import threading
import threading

from FlowControl.main import Controller
from Interface.main import Interface
from Core.main import Core
# from DetectionTrackingMainAPP import DetectionTrackingMain
#from Core.Recognistion_process.LicensePlateRecognizer import LicensePlateRecognizer

# tracker_class = DetectionTrackingMain()
# recogniser = LicensePlateRecognizer()


def gui_of_ALPR():
    obj_Interface = Interface()
    obj_core = Core()
    obj_Controller = Controller(obj_core, obj_Interface)
    obj_Controller.start_application()
    obj_Interface.start_mainloop()
    # tracker_class.stop_event.set()
    # recogniser.stop_event.set()



def main():
    thread3 = threading.Thread(target=gui_of_ALPR, daemon=True)
    thread3.start()

    # thread1 = threading.Thread(target=tracker_class.detection_tracking_main, daemon=True)  # This is a daemon thread
    # thread2 = threading.Thread(target=recogniser.main, daemon=True)  # This is a daemon thread

    # thread1.start()
    # thread2.start()

    # thread1.join()
    # thread2.join()
    thread3.join()


if __name__ == "__main__":
    main()