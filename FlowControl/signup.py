from Core.main import Core
from Interface.main import Interface

class SignUpController:
    

    def __init__(self, Core : Core, Interface : Interface):
        
        self.obj_Core = Core
        self.obj_Interface = Interface
        self.obj_SignupInterface = self.obj_Interface.dict_frames["signup"]

        self.bind_buttons()

        self.obj_SignupInterface.entry_username.bind("<KeyRelease>", self.validate_user_name)
        self.obj_SignupInterface.entry_email.bind("<KeyRelease>", self.validate_email)
        self.obj_SignupInterface.entry_phonenum.bind("<KeyRelease>", self.validate_phoneNum)
        self.obj_SignupInterface.entry_password.bind("<KeyRelease>", self.validate_password)       


    def bind_buttons(self) -> None:
        self.obj_SignupInterface.button_signup.configure(command=self.signup)
        self.obj_SignupInterface.button_signin.configure(command=self.signin)


    def signin(self) -> None:
        self.obj_SignupInterface.reset_interface()
        self.obj_Interface.switch_frames("signin")


    def signup(self) -> None:
        bool_is_valid_data = self.validate_user_name(None)
        bool_is_valid_data = self.validate_email(None) and bool_is_valid_data
        bool_is_valid_data = self.validate_phoneNum(None) and bool_is_valid_data
        bool_is_valid_data = self.validate_password(None) and bool_is_valid_data

        if bool_is_valid_data:
            str_username =  self.obj_SignupInterface.entry_username.get()
            str_email_id =  self.obj_SignupInterface.entry_email.get()
            str_phone_number =  self.obj_SignupInterface.entry_phonenum.get()
            str_password =  self.obj_SignupInterface.entry_password.get()

            self.obj_SignupInterface.update_signup_Button("Loading...", "disable")
            dict_status = self.obj_Core.obj_Authentication.create_account(str_username, str_email_id, str_phone_number, str_password)
            self.obj_SignupInterface.update_signup_Button("Signup", "normal")

            if (dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == ""):
                self.obj_SignupInterface.reset_interface()
                self.obj_Interface.switch_frames("signin")
                self.obj_Interface.on_error(
                    "signin",
                    "Account Created Successfully", 
                    "",
                    "#63CA6D",
                    50
                )
            else:
                self.obj_Interface.on_error(
                    "signup",
                    dict_status["str_error_msg_heading"], 
                    dict_status["str_error_msg"],
                    "#FF4B4B"
                )
        else:
            self.obj_Interface.on_error(
                "signup",
                "Error! Invalid Data", 
                "Check if the entered data fulfill the required conditions.",
                "#FF4B4B"
            )


    def validate_user_name(self, event) -> bool:

        str_user_name = self.obj_SignupInterface.entry_username.get()
        str_error_msg = self.obj_Core.obj_Authentication.validate_user_name(str_user_name)

        if len(str_error_msg) == 0:
            self.obj_SignupInterface.update_on_input_changed(self.obj_SignupInterface.entry_username, self.obj_SignupInterface.label_username_error, str_error_msg, "#828282")
            return True
        else:
            self.obj_SignupInterface.update_on_input_changed(self.obj_SignupInterface.entry_username, self.obj_SignupInterface.label_username_error, str_error_msg, "#FF0000")
            return False


    def validate_email(self, event) -> bool:

        str_email_id = self.obj_SignupInterface.entry_email.get()
        str_error_msg = self.obj_Core.obj_Authentication.validate_email(str_email_id)
        
        if len(str_error_msg) == 0:
            self.obj_SignupInterface.update_on_input_changed(self.obj_SignupInterface.entry_email, self.obj_SignupInterface.label_email_error, str_error_msg, "#828282")
            return True
        else:
            self.obj_SignupInterface.update_on_input_changed(self.obj_SignupInterface.entry_email, self.obj_SignupInterface.label_email_error, str_error_msg, "#FF0000")
            return False


    def validate_phoneNum(self, event) -> bool:
        
        str_phone_number = self.obj_SignupInterface.entry_phonenum.get()
        str_error_msg = self.obj_Core.obj_Authentication.validate_phone_number(str_phone_number)
        
        if len(str_error_msg) == 0:
            self.obj_SignupInterface.update_on_input_changed(self.obj_SignupInterface.entry_phonenum, self.obj_SignupInterface.label_phone_error, str_error_msg, "#828282")
            return True
        else:
            self.obj_SignupInterface.update_on_input_changed(self.obj_SignupInterface.entry_phonenum, self.obj_SignupInterface.label_phone_error, str_error_msg, "#FF0000")
            return False
    

    def validate_password(self, event) -> bool:

        str_password = self.obj_SignupInterface.entry_password.get()
        str_error_msg = self.obj_Core.obj_Authentication.validate_password(str_password)

        if  len(str_error_msg) == 0:
            self.obj_SignupInterface.update_on_input_changed(self.obj_SignupInterface.entry_password, self.obj_SignupInterface.label_password_error, str_error_msg, "#828282")
            return True
        else:
            self.obj_SignupInterface.update_on_input_changed(self.obj_SignupInterface.entry_password, self.obj_SignupInterface.label_password_error, str_error_msg, "#FF0000")
            return False