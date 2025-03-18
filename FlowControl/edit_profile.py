from Core.main import Core
from Interface.main import Interface

class EditProfileController:
    
    def __init__(self, Core : Core, Interface : Interface):
        
        self.obj_Core = Core
        self.obj_Interface = Interface
        self.obj_EditUserInterface = self.obj_Interface.dict_frames["edit_user"]
        
        self.bind_buttons()

    def bind_buttons(self) -> None:
        self.obj_EditUserInterface.button_save.configure(command=self.onclick_save)
        # self.obj_EditUserInterface.button_cancel.configure(command=self.onclick_cancel)

    def onclick_save(self):
        bool_is_valid_data = self.validate_user_name(None)
        # bool_is_valid_data = self.validate_phoneNum(None) and bool_is_valid_data
        bool_is_valid_data = self.validate_password(None) and bool_is_valid_data

        if(bool_is_valid_data):
            str_username =  self.obj_EditUserInterface.Entry_username.get()
            # str_phone_number =  self.obj_EditUserInterface.Entry_phoneno.get()
            str_password =  self.obj_EditUserInterface.Entry_pasword.get()
            # str_email=self.obj_EditUserInterface.Entry_email.get()

            dict_status = self.obj_Core.obj_Authentication.update_details(str_username, str_password)

            if (dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == ""):
                self.obj_Interface.dict_frames["home"].update_user_popup_data(self.obj_Core.dict_user_data["str_user_name"])
                self.obj_Interface.on_error(
                    "home",
                    "Data Updated Successfully", 
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

    def validate_user_name(self, event) -> bool:

        str_user_name = self.obj_EditUserInterface.Entry_username.get()
        str_error_msg = self.obj_Core.obj_Authentication.validate_user_name(str_user_name)

        if len(str_error_msg) == 0:
            return True
        else:
            return False    
        
    # def validate_phoneNum(self, event) -> bool:
        
    #     str_pasword = self.obj_EditUserInterface.Entry_pasword.get()
    #     str_error_msg = self.obj_Core.obj_Authentication.validate_password(str_pasword)
        
    #     if len(str_error_msg) == 0:
    #         return True
    #     else:
    #         return False
        
    def validate_password(self, event) -> bool:

        str_password = self.obj_EditUserInterface.Entry_pasword.get()
        str_error_msg = self.obj_Core.obj_Authentication.validate_password(str_password)

        if  len(str_error_msg) == 0:
            return True
        else:
            return False