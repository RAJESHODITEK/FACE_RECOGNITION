from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton
from tkinter import Canvas
from PIL import Image, ImageTk

class SignUpInterface(CTkFrame):

    def __init__(self, *args, root_width : int = 1920, root_height : int = 1080, **kwargs):
        super().__init__(*args, **kwargs)

        self.configure(fg_color = "white")

        self.columnconfigure(0, weight = 1, uniform = 'a')
        self.columnconfigure(1, weight = 1, uniform = 'a')
        self.rowconfigure(0, weight = 1)

        self.img_signin_bg_original = Image.open(".\\Resources\\images\\welcome_bg_img.png")
        self.img_signin_bg_display = None

        self.cnv_image = Canvas(self, bd = 0, highlightthickness = 0, relief = 'ridge')
        self.cnv_image.grid(column = 0, row = 0, sticky = "nsew")
        self.cnv_image.bind('<Configure>', self.updateImage)

        i_form_width = int(root_width * 0.29)
        i_form_height = int(root_height * 0.5)

        self.frame_form = CTkFrame(
            self, 
            height = i_form_height, 
            width = i_form_width, 
            fg_color="white"
        )
        self.frame_form.grid(column = 1,row = 0)

        self.label_welcome = CTkLabel(
            self.frame_form, 
            text = "Let's Get Started!", 
            text_color = "#2c2c2c", 
            font = ("Segoe UI", 24, "bold")
        )
        self.label_welcome.grid(row = 0, column = 0)

        self.label_welcome_msg = CTkLabel(
            self.frame_form,  
            text = "Don't have an account? Please enter your details", 
            text_color = "#828282", 
            font = ("", 13.9)
        )
        self.label_welcome_msg.grid(row = 1, column = 0, pady=(5,0))

        self.frame_username = CTkFrame(
            self.frame_form, 
            fg_color="#FFFFFF"
        )
        self.frame_username.grid(row=2, column=0, pady=(10, 0), sticky="ew")

        self.label_username = CTkLabel(
            self.frame_username,
            text="Username", 
            text_color = "#2c2c2c",
            font = ("",14)
        )
        self.label_username.pack(side="left")

        self.label_username_error = CTkLabel(
            self.frame_username,
            text="",
            text_color="#FF0000",
            font=("", 12)
        )
        self.label_username_error.pack(side="left", padx=(10,0))

        self.entry_username = CTkEntry(
            self.frame_form,
            width = i_form_width,
            height = 45 ,
            corner_radius = 35,
            border_width=2,
            border_color="#828282",
            fg_color = "white",
            placeholder_text = "Enter Username",
            text_color = "#414141",
            font = ("", 13.5)
        )
        self.entry_username.grid(row=3, column=0)

        self.frame_email = CTkFrame(
            self.frame_form, 
            fg_color="#FFFFFF"
        )
        self.frame_email.grid(row=4, column=0, pady=(10, 0), sticky="ew")

        self.label_email = CTkLabel(
            self.frame_email, 
            text="Email Id", 
            text_color = "#2c2c2c",
            font = ("", 14)
        )
        self.label_email.pack(side="left")

        self.label_email_error = CTkLabel(
            self.frame_email,
            text="",
            text_color="#FF0000",
            font=("", 12)
        )
        self.label_email_error.pack(side="left", padx=(10, 0))

        self.entry_email = CTkEntry(
            self.frame_form, 
            width = i_form_width,
            height = 45 ,
            corner_radius = 35,
            border_width=2,
            border_color="#828282",
            fg_color = "white",
            placeholder_text = "Enter your email id",
            text_color = "#414141",
            font = ("", 13.5)
        )
        self.entry_email.grid(row=5, column=0)

        self.frame_phone = CTkFrame(
            self.frame_form, 
            fg_color="#FFFFFF"
        )
        self.frame_phone.grid(row=6, column=0, pady=(10, 0), sticky="ew")

        self.label_phonenum = CTkLabel(
            self.frame_phone, 
            text="Phone Number", 
            text_color = "#2c2c2c",
            font = ("", 14)
        )
        self.label_phonenum.pack(side="left")

        self.label_phone_error = CTkLabel(
            self.frame_phone,
            text="",
            text_color="#FF0000",
            font=("", 12)
        )
        self.label_phone_error.pack(side="left", padx=(10, 0))

        self.entry_phonenum = CTkEntry(
            self.frame_form, 
            width = i_form_width,
            height = 45 ,
            corner_radius = 35,
            border_width=2,
            border_color="#828282",
            fg_color = "white",
            placeholder_text = "Enter your phone number",
            text_color = "#414141",
            font = ("", 13.5)
            )
        self.entry_phonenum.grid(row=7, column=0)

        self.frame_password = CTkFrame(
            self.frame_form, 
            fg_color="#FFFFFF"
        )
        self.frame_password.grid(row=8, column=0, pady=(10, 0), sticky="ew")

        self.label_password = CTkLabel(
            self.frame_password,
            text="Password", 
            text_color = "#2c2c2c",
            font = ("", 14)
        )
        self.label_password.pack(side="left")

        self.label_password_error = CTkLabel(
            self.frame_password,
            text="",
            text_color="#FF0000",
            font=("", 12)
        )
        self.label_password_error.pack(side="left", padx=(10, 0))

        self.entry_password = CTkEntry(
            self.frame_form, 
            width = i_form_width,
            height = 45 ,
            corner_radius = 35,
            border_width=2,
            border_color="#828282",
            fg_color = "white",
            placeholder_text = "Enter Password",
            text_color = "#414141",
            font = ("", 13.5)
        )
        self.entry_password.grid(row=9, column=0)

        self.button_signup = CTkButton(
            self.frame_form,
            width = i_form_width,
            height = 40 ,
            corner_radius = 35,
            border_color= "#3A36F5",
            fg_color = "#3A36F5",
            text = "Sign Up", 
            text_color = "white",  
            font=("", 14),
            cursor="hand2",
            hover=False
        )
        self.button_signup.grid(row=10, column=0, pady=(28,0))

        self.frame_Signin_msg = CTkFrame(
            self.frame_form, 
            width=i_form_width,
            height = 40 ,
            fg_color="white"
        )
        self.frame_Signin_msg.grid(row=11, column=0, pady=(15, 0))

        self.frame_Signin_msg.columnconfigure(0, weight = 2)
        self.frame_Signin_msg.columnconfigure(1, weight = 1)
        self.frame_Signin_msg.rowconfigure(0, weight = 1)

        self.label_signin_msg = CTkLabel(
            self.frame_Signin_msg, 
            text="Already have an account?", 
            text_color = "#828282",
            font = ("", 14)
        )
        self.label_signin_msg.grid(row=0, column=0,  sticky="e")

        self.button_signin = CTkButton(
            self.frame_Signin_msg,
            width=10,
            text = "Sign In", 
            fg_color = "white", 
            text_color = "#3A36F5",  
            font=("", 14, "underline"),
            cursor="hand2",
            hover=False
        )
        self.button_signin.grid(row=0, column=1, pady=(2,0), sticky="w")

    def updateImage(self, event) -> None:
        image_resized = self.img_signin_bg_original.resize((event.width, event.height))
        self.img_signin_bg_display = ImageTk.PhotoImage(image_resized)
        self.cnv_image.create_image(0, 0, image = self.img_signin_bg_display, anchor = 'nw')

    def update_on_input_changed(self, entry_input_field : CTkEntry = None, label_error : CTkLabel = None, str_error : str = "", str_border_color : str = None):
        if(entry_input_field is not None):
            if(str_border_color is not None):
                entry_input_field.configure(border_color = str_border_color)
        if(label_error is not None):
            label_error.configure(text=str_error)
        self.update()

    def update_signup_Button(self, button_text : str = None ,button_state : str = None):
        if(button_state is not None):
            self.button_signup.configure(text = button_text, state = button_state)
        self.update()

    def reset_interface(self):
        for widget in [self.label_username_error, self.label_email_error, self.label_phone_error,self.label_password_error]:
            widget.configure(text="")

        for widget in [self.entry_username, self.entry_email, self.entry_phonenum, self.entry_password]:
            widget.delete(0, "end")
            widget.configure(border_color = "#828282")

        self.entry_username.configure(placeholder_text = "Enter Username")
        self.entry_email.configure(placeholder_text = "Enter your email id")
        self.entry_phonenum.configure(placeholder_text = "Enter your phone number")
        self.entry_password.configure(placeholder_text = "Enter Password")

        self.frame_form.focus()