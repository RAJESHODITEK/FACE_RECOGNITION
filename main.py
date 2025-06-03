import threading
import torch
from FR_Detection.merge import mainfun
from FlowControl.main import Controller
from Interface.main import Interface
from Core.main import Core
# from FR_Detection.sample import main
# from FR_Detection.Recognition import FaceProcessor
# from shared_queue import shared_data




def gui_of_ALPR():
    obj_Interface = Interface()
    obj_core = Core()
    obj_Controller = Controller(obj_core, obj_Interface)
    obj_Controller.start_application()
    obj_Interface.start_mainloop()

# def check_pkl_status(obj_faceprocess:FaceProcessor):
#     while True:
#         if shared_data["pkl_file_update_status"]:
#             print("pkl change detected!")
#             if shared_data['op']==0:
#                 obj_faceprocess.add_person( shared_data["id"], shared_data["name"],shared_data['image'])
#             elif shared_data['op']==1:
#                 obj_faceprocess.update_person_name(shared_data["id"], shared_data["name"])
#             elif shared_data['op']==2:
#                 for id in shared_data['id_list']:
#                     obj_faceprocess.delete_person(id)
#
#             shared_data["pkl_file_update_status"] = False
#
#
#
#         time.sleep(1)
def main():
    thread_camera_check = threading.Thread(target=mainfun, daemon=True)
    thread_camera_check.start()

    # thread_pkl_check = threading.Thread(target=check_pkl_status,args=(obj_faceprocess,), daemon=True)
    # thread_pkl_check.start()

    gui_of_ALPR()
    thread_camera_check.join()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("error ",e)
        input("exit")
    # thread_pkl_check.join()