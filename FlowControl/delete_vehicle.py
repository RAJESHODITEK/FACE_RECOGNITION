from Core.main import Core
from Interface.main import Interface

class DeleteVehicleController:
    
    def __init__(self, Core : Core, Interface : Interface):
        
        self.obj_core = Core
        self.obj_Interface = Interface
        self.obj_DeleteVehicleInterface = self.obj_Interface.dict_frames["delete_vehicle"]
        
        self.bind_buttons()

        self.obj_DeleteVehicleInterface.entry_password.bind("<KeyRelease>", self.validate_password)

    def bind_buttons(self):
        self.obj_DeleteVehicleInterface.button_delete.configure(command=self.delete)
        self.obj_DeleteVehicleInterface.button_cancel.configure(command=self.cancel)
        self.obj_DeleteVehicleInterface.button_select_vehicle.configure(command=self.popup_dropdown)
        
    def popup_dropdown(self):
        if(self.obj_DeleteVehicleInterface.bool_dropdown_opened is True):
            self.obj_DeleteVehicleInterface.popup_dropdown(entry_destination = self.obj_DeleteVehicleInterface.entry_selected_vehicle, 
                                                           i_row = 2)
        else:
            dict_status = self.obj_core.obj_Vehicle.get_user_added_vehicles()
            if(dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == ""):
                if dict_status["list_vehicles"]:
                    self.obj_DeleteVehicleInterface.popup_dropdown(list_data = dict_status["list_vehicles"], 
                                                                   entry_destination = self.obj_DeleteVehicleInterface.entry_selected_vehicle, 
                                                                   i_row = 2)
                else:
                    self.obj_Interface.on_error(
                        "home",
                        dict_status["str_error_msg_heading"], 
                        dict_status["str_error_msg"],
                        "#FF4B4B"
                    )
            else:
                self.obj_Interface.on_error(
                        "home",
                        dict_status["str_error_msg_heading"], 
                        dict_status["str_error_msg"],
                        "#FF4B4B"
                    )

    def delete(self):

        bool_is_valid_data = self.validate_vehicle(None)
        bool_is_valid_data = self.validate_password(None) and bool_is_valid_data

        if bool_is_valid_data:
            str_user_vehicle = self.obj_DeleteVehicleInterface.entry_selected_vehicle.get()
            str_password = self.obj_DeleteVehicleInterface.entry_password.get()

            dict_status = self.obj_core.obj_Vehicle.delete_vehicle(str_user_vehicle, str_password)

            if (dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == ""):
                self.obj_DeleteVehicleInterface.reset_interface(),
                self.obj_Interface.on_error(
                        "home",
                        "Data deleted Successfullly", 
                        "",
                        "#63CA6D",
                        50
                    )
            else:
                self.obj_Interface.on_error(
                    "home",
                    dict_status["str_error_msg_heading"], 
                    dict_status["str_error_msg"],
                    "#FF4B4B"
                )
        else:
            self.obj_Interface.on_error(
                "home",
                "Error! Invalid Data", 
                "Check if the entered data fulfill the required conditions.",
                "#FF4B4B"
            )

    def cancel(self):
        self.obj_DeleteVehicleInterface.reset_interface()

    def validate_vehicle(self, event) -> bool:
        str_user_vehicle = self.obj_DeleteVehicleInterface.entry_selected_vehicle.get()
        str_error_msg = self.obj_core.obj_Vehicle.validate_user_vehicle(str_user_vehicle)

        if len(str_error_msg) == 0:
            self.obj_DeleteVehicleInterface.update_on_input_changed(self.obj_DeleteVehicleInterface.entry_selected_vehicle, 
                                                                 self.obj_DeleteVehicleInterface.label_vehicle_error, 
                                                                 str_error_msg, 
                                                                 "#DEDEDE")
            return True
        else:
            self.obj_DeleteVehicleInterface.update_on_input_changed(self.obj_DeleteVehicleInterface.entry_selected_vehicle, 
                                                                 self.obj_DeleteVehicleInterface.label_vehicle_error, 
                                                                 str_error_msg, 
                                                                 "#FF0000")
            return False
        
    
    def validate_password(self, event) -> bool:
        str_password = self.obj_DeleteVehicleInterface.entry_password.get()
        str_error_msg = self.obj_core.obj_Vehicle.validate_password(str_password)

        if len(str_error_msg) == 0:
            self.obj_DeleteVehicleInterface.update_on_input_changed(self.obj_DeleteVehicleInterface.entry_password, 
                                                                 self.obj_DeleteVehicleInterface.label_password_error, 
                                                                 str_error_msg, 
                                                                 "#DEDEDE")
            return True
        else:
            self.obj_DeleteVehicleInterface.update_on_input_changed(self.obj_DeleteVehicleInterface.entry_password, 
                                                                 self.obj_DeleteVehicleInterface.label_password_error, 
                                                                 str_error_msg, 
                                                                 "#FF0000")
            return False