from Core.main import Core
from Interface.main import Interface

class DeletepersonController:
    
    def __init__(self, Core : Core, Interface : Interface):
        
        self.obj_core = Core
        self.obj_Interface = Interface
        self.obj_DeletepersonInterface = self.obj_Interface.dict_frames["delete_person"]
        
        self.bind_buttons()

        self.obj_DeletepersonInterface.entry_password.bind("<KeyRelease>", self.validate_password)

    def bind_buttons(self):
        self.obj_DeletepersonInterface.button_delete.configure(command=self.delete)
        self.obj_DeletepersonInterface.button_cancel.configure(command=self.cancel)
        self.obj_DeletepersonInterface.button_select_person.configure(command=self.popup_dropdown)
        
    def popup_dropdown(self):
        if(self.obj_DeletepersonInterface.bool_dropdown_opened is True):
            self.obj_DeletepersonInterface.popup_dropdown(entry_destination = self.obj_DeletepersonInterface.entry_selected_person, 
                                                           i_row = 2)
        else:
            dict_status = self.obj_core.obj_person.get_user_added_persons()
            if(dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == ""):
                if dict_status["list_persons"]:
                    self.obj_DeletepersonInterface.popup_dropdown(list_data = dict_status["list_persons"], 
                                                                   entry_destination = self.obj_DeletepersonInterface.entry_selected_person, 
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

        bool_is_valid_data = self.validate_person(None)
        bool_is_valid_data = self.validate_password(None) and bool_is_valid_data

        if bool_is_valid_data:
            str_user_person = self.obj_DeletepersonInterface.entry_selected_person.get()
            str_password = self.obj_DeletepersonInterface.entry_password.get()

            dict_status = self.obj_core.obj_person.delete_person(str_user_person, str_password)

            if (dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == ""):
                self.obj_DeletepersonInterface.reset_interface(),
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
        self.obj_DeletepersonInterface.reset_interface()

    def validate_person(self, event) -> bool:
        str_user_person = self.obj_DeletepersonInterface.entry_selected_person.get()
        str_error_msg = self.obj_core.obj_person.validate_user_person(str_user_person)

        if len(str_error_msg) == 0:
            self.obj_DeletepersonInterface.update_on_input_changed(self.obj_DeletepersonInterface.entry_selected_person, 
                                                                 self.obj_DeletepersonInterface.label_person_error, 
                                                                 str_error_msg, 
                                                                 "#DEDEDE")
            return True
        else:
            self.obj_DeletepersonInterface.update_on_input_changed(self.obj_DeletepersonInterface.entry_selected_person, 
                                                                 self.obj_DeletepersonInterface.label_person_error, 
                                                                 str_error_msg, 
                                                                 "#FF0000")
            return False
        
    
    def validate_password(self, event) -> bool:
        str_password = self.obj_DeletepersonInterface.entry_password.get()
        str_error_msg = self.obj_core.obj_person.validate_password(str_password)

        if len(str_error_msg) == 0:
            self.obj_DeletepersonInterface.update_on_input_changed(self.obj_DeletepersonInterface.entry_password, 
                                                                 self.obj_DeletepersonInterface.label_password_error, 
                                                                 str_error_msg, 
                                                                 "#DEDEDE")
            return True
        else:
            self.obj_DeletepersonInterface.update_on_input_changed(self.obj_DeletepersonInterface.entry_password, 
                                                                 self.obj_DeletepersonInterface.label_password_error, 
                                                                 str_error_msg, 
                                                                 "#FF0000")
            return False