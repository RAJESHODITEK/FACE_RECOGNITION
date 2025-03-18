from Core.main import Core
from Interface.main import Interface


class LiveEventController:

    def __init__(self, Core: Core, Interface: Interface):
        self.obj_Core = Core
        self.obj_Interface = Interface
        self.obj_LiveEventInterface = self.obj_Interface.dict_frames["live_feed"]
        self.bind_buttons()
        self.obj_LiveEventInterface.entry_selected_camera.bind("<KeyRelease>", self.obj_HomeInterface.onclick_selectCamera)

    def bind_buttons(self):
        pass