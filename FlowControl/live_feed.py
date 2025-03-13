from Core.main import Core
from FlowControl.notification import NotificationController
from Interface.main import Interface


class LiveEventController:

    def __init__(self, Core: Core, Interface: Interface):
        self.obj_Core = Core
        self.obj_Interface = Interface
        self.obj_NotificationController= NotificationController(Core,Interface)
        self.obj_LiveEventInterface = self.obj_Interface.dict_frames["live_feed"]
        self.check_notification()
        #self.obj_LiveEventInterface.entry_selected_camera.bind("<KeyRelease>", self.obj_HomeInterface.onclick_selectCamera)

    def check_notification(self):
        if self.obj_LiveEventInterface.restricted_vehicle_caught_signal:
            self.obj_Interface.dict_frames['home'].dot_label.configure(text="●")

            self.obj_LiveEventInterface.restricted_vehicle_caught_signal=False

        # Schedule the function to run again after 1000ms (1 second)
        self.obj_LiveEventInterface.after(3000, self.check_notification)

