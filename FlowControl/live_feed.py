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
        self.obj_LiveEventInterface.on_form_ready = self.bind_events


    def bind_events(self):
        if hasattr(self.obj_LiveEventInterface, 'video_label'):
            self.obj_LiveEventInterface.video_label.bind("<Button-1>", self.obj_LiveEventInterface.on_box_click)

    def check_notification(self):
        if self.obj_LiveEventInterface.restricted_person_caught_signal:
            self.obj_Interface.dict_frames['home'].dot_label.configure(text="●")

            self.obj_LiveEventInterface.restricted_person_caught_signal=False

        # Schedule the function to run again after 1000ms (1 second)
        self.obj_LiveEventInterface.after(3000, self.check_notification)

