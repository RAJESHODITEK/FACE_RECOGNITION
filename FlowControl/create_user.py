from Core.main import Core
from Interface.main import Interface


class CreateUserController:

    def __init__(self, Core: Core, Interface: Interface):

        self.obj_Core = Core
        self.obj_Interface = Interface
        self.obj_CreateUserInterface = self.obj_Interface.dict_frames["create_user"]

        self.bind_buttons()

        self.obj_CreateUserInterface.entry_username.bind("<KeyRelease>", self.validate_user_name)
        self.obj_CreateUserInterface.entry_email.bind("<KeyRelease>", self.validate_email)
        self.obj_CreateUserInterface.entry_phonenum.bind("<KeyRelease>", self.validate_phoneNum)
        self.obj_CreateUserInterface.entry_password.bind("<KeyRelease>", self.validate_password)

    def bind_buttons(self) -> None:
        self.obj_CreateUserInterface.button_create_user.configure(command=self.create_user)
        self.obj_CreateUserInterface.button_cancel.configure(command=self.onclick_cancel)

    def onclick_cancel(self) -> None:
        self.obj_CreateUserInterface.reset_interface()

    def create_user(self) -> None:
        bool_is_valid_data = self.validate_user_name(None)
        bool_is_valid_data = self.validate_email(None) and bool_is_valid_data
        bool_is_valid_data = self.validate_phoneNum(None) and bool_is_valid_data
        bool_is_valid_data = self.validate_password(None) and bool_is_valid_data

        if bool_is_valid_data:
            str_username = self.obj_CreateUserInterface.entry_username.get()
            str_email_id = self.obj_CreateUserInterface.entry_email.get()
            str_phone_number = self.obj_CreateUserInterface.entry_phonenum.get()
            str_password = self.obj_CreateUserInterface.entry_password.get()

            self.obj_CreateUserInterface.update_signup_Button("Loading...", "disable")
            dict_status = self.obj_Core.obj_Authentication.create_account(str_username, str_email_id, str_phone_number,
                                                                          str_password)
            self.obj_CreateUserInterface.update_signup_Button("Create account", "normal")

            if (dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == ""):
                self.obj_CreateUserInterface.reset_interface()
                self.obj_Interface.on_error(
                    "create_user",
                    "Account Created Successfully",
                    "",
                    "#6AE580",
                    50
                )
            else:
                self.obj_Interface.on_error(
                    "create_user",
                    dict_status["str_error_msg_heading"],
                    dict_status["str_error_msg"],
                    "#FF4B4B"
                )
        else:
            self.obj_Interface.on_error(
                "create_user",
                "Error! Invalid Data",
                "Check if the entered data fulfill the required conditions.",
                "#FF4B4B"
            )

    def validate_user_name(self, event) -> bool:

        str_user_name = self.obj_CreateUserInterface.entry_username.get()
        str_error_msg = self.obj_Core.obj_Authentication.validate_user_name(str_user_name)

        if len(str_error_msg) == 0:
            self.obj_CreateUserInterface.update_on_input_changed(self.obj_CreateUserInterface.entry_username,
                                                                 self.obj_CreateUserInterface.label_username_error,
                                                                 str_error_msg, "#DEDEDE")
            return True
        else:
            self.obj_CreateUserInterface.update_on_input_changed(self.obj_CreateUserInterface.entry_username,
                                                                 self.obj_CreateUserInterface.label_username_error,
                                                                 str_error_msg, "#FF0000")
            return False

    def validate_email(self, event) -> bool:

        str_email_id = self.obj_CreateUserInterface.entry_email.get()
        str_error_msg = self.obj_Core.obj_Authentication.validate_email(str_email_id)

        if len(str_error_msg) == 0:
            self.obj_CreateUserInterface.update_on_input_changed(self.obj_CreateUserInterface.entry_email,
                                                                 self.obj_CreateUserInterface.label_email_error,
                                                                 str_error_msg, "#DEDEDE")
            return True
        else:
            self.obj_CreateUserInterface.update_on_input_changed(self.obj_CreateUserInterface.entry_email,
                                                                 self.obj_CreateUserInterface.label_email_error,
                                                                 str_error_msg, "#FF0000")
            return False

    def validate_phoneNum(self, event) -> bool:

        str_phone_number = self.obj_CreateUserInterface.entry_phonenum.get()
        str_error_msg = self.obj_Core.obj_Authentication.validate_phone_number(str_phone_number)

        if len(str_error_msg) == 0:
            self.obj_CreateUserInterface.update_on_input_changed(self.obj_CreateUserInterface.entry_phonenum,
                                                                 self.obj_CreateUserInterface.label_phone_error,
                                                                 str_error_msg, "#DEDEDE")
            return True
        else:
            self.obj_CreateUserInterface.update_on_input_changed(self.obj_CreateUserInterface.entry_phonenum,
                                                                 self.obj_CreateUserInterface.label_phone_error,
                                                                 str_error_msg, "#FF0000")
            return False

    def validate_password(self, event) -> bool:

        str_password = self.obj_CreateUserInterface.entry_password.get()
        str_error_msg = self.obj_Core.obj_Authentication.validate_password(str_password)

        if len(str_error_msg) == 0:
            self.obj_CreateUserInterface.update_on_input_changed(self.obj_CreateUserInterface.entry_password,
                                                                 self.obj_CreateUserInterface.label_password_error,
                                                                 str_error_msg, "#DEDEDE")
            return True
        else:
            self.obj_CreateUserInterface.update_on_input_changed(self.obj_CreateUserInterface.entry_password,
                                                                 self.obj_CreateUserInterface.label_password_error,
                                                                 str_error_msg, "#FF0000")
            return False