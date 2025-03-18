from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCanvas, StringVar

class CreateUserInterface(CTkFrame):

    def __init__(self, *args, root_width : int = 1920, root_height : int = 1080, **kwargs):
        super().__init__(*args, **kwargs)

        self.configure(fg_color="#F1F5FA", corner_radius=0)

        i_form_width = 500
        i_form_height = 550

        self.frame_form = CTkFrame(
            self,
            width=i_form_width,
            height=i_form_height,
            fg_color="#FFFFFF",
            corner_radius=10
        )
        self.frame_form.columnconfigure(0, weight=1, uniform='a')
        self.frame_form.columnconfigure(1, weight=1, uniform='a')
        self.frame_form.grid_propagate(False)
        self.frame_form.pack(side="top", expand=False, padx=10, pady=(30, 0))

        self.label_heading = CTkLabel(
            self.frame_form,
            text="Create an account",
            text_color = "#2C2C2C",
            font=("", 18, "bold"),
            anchor="w"
        )
        self.label_heading.grid(row=0, column=0, columnspan=2, padx=25, pady=(25, 10), sticky="ew")

        self.canvas_underline = CTkCanvas(
            self.frame_form,
            height=1,
            bg="#D2D2D2",
            bd=0,
            highlightthickness=0
        )
        self.canvas_underline.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        self.frame_username = CTkFrame(
            self.frame_form,
            fg_color="#FFFFFF"
        )
        self.frame_username.grid(row=2, column=0, columnspan=2, padx=25, pady=(20, 0), sticky="ew")

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
            height = 40 ,
            corner_radius = 5,
            border_width=2,
            border_color="#DEDEDE",
            fg_color = "#F6F6F6",
            placeholder_text = "Enter Username",
            placeholder_text_color="#828282",
            text_color = "#414141",
            font = ("", 13.5)
        )
        self.entry_username.grid(row=3, column=0, columnspan=2, padx=25, sticky="ew")

        self.frame_email = CTkFrame(
            self.frame_form,
            fg_color="#FFFFFF"
        )
        self.frame_email.grid(row=4, column=0, columnspan=2, padx=25, pady=(10, 0), sticky="ew")

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
            height = 40 ,
            corner_radius = 5,
            border_width=2,
            border_color="#DEDEDE",
            fg_color = "#F6F6F6",
            placeholder_text = "Enter your email id",
            placeholder_text_color="#828282",
            text_color = "#414141",
            font = ("", 13.5)
        )
        self.entry_email.grid(row=5, column=0, columnspan=2, padx=25, sticky="ew")

        self.frame_phone = CTkFrame(
            self.frame_form,
            fg_color="#FFFFFF"
        )
        self.frame_phone.grid(row=6, column=0, columnspan=2, padx=25, pady=(10, 0), sticky="ew")

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
            height = 40 ,
            corner_radius = 5,
            border_width=2,
            border_color="#DEDEDE",
            fg_color = "#F6F6F6",
            placeholder_text = "Enter your phone number",
            placeholder_text_color="#828282",
            text_color = "#414141",
            font = ("", 13.5)
            )
        self.entry_phonenum.grid(row=7, column=0, columnspan=2, padx=25, sticky="ew")

        self.frame_password = CTkFrame(
            self.frame_form,
            fg_color="#FFFFFF"
        )
        self.frame_password.grid(row=8, column=0, columnspan=2, padx=25, pady=(10, 0), sticky="ew")

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
            height = 40 ,
            corner_radius = 5,
            border_width=2,
            border_color="#DEDEDE",
            fg_color = "#F6F6F6",
            placeholder_text = "Enter Password",
            placeholder_text_color="#828282",
            text_color = "#414141",
            font = ("", 13.5)
        )
        self.entry_password.grid(row=9, column=0, columnspan=2, padx=25, sticky="ew")

        self.button_create_user = CTkButton(
            self.frame_form,
            height=38,
            text="Create account",
            text_color="#FFFFFF",
            fg_color="#3A36F5",
            border_color="#3A36F5",
            font=("", 14),
            cursor="hand2",
            hover=False
        )
        self.button_create_user.grid(row=10, column=0, padx=(25, 3.125), pady=(30, 25), sticky="e")

        self.button_cancel = CTkButton(
            self.frame_form,
            height=38,
            width=100,
            text="Cancel",
            text_color="#FFFFFF",
            fg_color="#6C757D",
            border_color="#6C757D",
            font=("", 14),
            cursor="hand2",
            hover=False,
            command=self.createUSerDestroy(),
        )
        self.button_cancel.grid(row=10, column=1, padx=(3.125, 25), pady=(30, 25), sticky="w")

    def createUSerDestroy(self):
        print("destroy this ")
    def update_on_input_changed(self, entry_input_field : CTkEntry = None, label_error : CTkLabel = None, str_error : str = "", str_border_color : str = None):
        if(entry_input_field is not None):
            if(str_border_color is not None):
                entry_input_field.configure(border_color = str_border_color)
        if(label_error is not None):
            label_error.configure(text=str_error)
        self.update()

    def update_signup_Button(self, button_text : str = None ,button_state : str = None):
        if(button_state is not None):
            self.button_create_user.configure(text = button_text, state = button_state)
        self.update()

    def reset_interface(self):
        for widget in [self.label_username_error, self.label_email_error, self.label_phone_error,self.label_password_error]:
            widget.configure(text="")

        for widget in [self.entry_username, self.entry_email, self.entry_phonenum, self.entry_password]:
            widget.delete(0, "end")
            widget.configure(border_color = "#DEDEDE")

        self.entry_username.configure(placeholder_text = "Enter Username")
        self.entry_email.configure(placeholder_text = "Enter your email id")
        self.entry_phonenum.configure(placeholder_text = "Enter your phone number")
        self.entry_password.configure(placeholder_text = "Enter Password")

        self.frame_form.focus()