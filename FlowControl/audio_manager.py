import threading

from Core.main import Core
from Interface.main import Interface


class AudioManagerController:
    def __init__(self, Core: Core, Interface: Interface):
        self.obj_Core = Core
        self.obj_Interface = Interface
        self.obj_audio_manager_interface = self.obj_Interface.dict_frames["audio_manager"]








