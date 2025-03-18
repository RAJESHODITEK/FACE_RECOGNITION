from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkCanvas, StringVar


class EditUserInterface(CTkFrame):
    def __init__(self, *args, root_width: int = 1920, root_height: int = 1080, **kwargs):
        super().__init__(*args, **kwargs)

        self.configure(fg_color="#F1F5FA", corner_radius=0)

        i_form_width = int((int(root_width * 0.89)) * 0.4)
        i_form_height = int((int(root_height * 0.88)) * 0.55)

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
            text="Edit Profile",
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

        # Username field
        self.label_username = CTkLabel(
            self.frame_form,
            text="Update Username",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_username.grid(row=2, column=0, columnspan=2, padx=25, pady=(20, 0), sticky="ew")

        self.Entry_username = CTkEntry(
            self.frame_form,
            height=40,
            fg_color="#F6F6F6",
            placeholder_text="Enter Updated User Name",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Entry_username.grid(row=3, column=0, columnspan=2, padx=25, sticky="ew")

        # Phone number field
        self.label_phoneno = CTkLabel(
            self.frame_form,
            text="Update phone number",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_phoneno.grid(row=4, column=0, columnspan=2, padx=25, pady=(10, 0), sticky="ew")

        self.Entry_phoneno = CTkEntry(
            self.frame_form,
            height=40,
            fg_color="#F6F6F6",
            placeholder_text="Enter Updated Phone Number",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Entry_phoneno.grid(row=5, column=0, columnspan=2, padx=25, sticky="ew")

        # # Password field
        # self.label_password = CTkLabel(
        #     self.frame_form,
        #     text="New Password",
        #     text_color="#2C2C2C",
        #     font=("", 14),
        #     anchor="w"
        # )
        # self.label_password.grid(row=6, column=0, columnspan=2, padx=25, pady=(10, 0), sticky="ew")

        # self.Entry_password = CTkEntry(
        #     self.frame_form,
        #     height=40,
        #     fg_color="#F6F6F6",
        #     placeholder_text="Enter New Password",
        #     placeholder_text_color="#828282",
        #     text_color="#414141",
        #     border_color="#DEDEDE",
        #     border_width=2,
        #     corner_radius=5,
        #     font=("", 14),
        #     show="*"  # Hide password characters
        # )
        # self.Entry_password.grid(row=7, column=0, columnspan=2, padx=25, sticky="ew")

        # # Confirm Password field (new)
        # self.label_confirm_password = CTkLabel(
        #     self.frame_form,
        #     text="Confirm Password",
        #     text_color="#2C2C2C",
        #     font=("", 14),
        #     anchor="w"
        # )
        # self.label_confirm_password.grid(row=8, column=0, columnspan=2, padx=25, pady=(10, 0), sticky="ew")

        # self.Entry_confirm_password = CTkEntry(
        #     self.frame_form,
        #     height=40,
        #     fg_color="#F6F6F6",
        #     placeholder_text="Confirm New Password",
        #     placeholder_text_color="#828282",
        #     text_color="#414141",
        #     border_color="#DEDEDE",
        #     border_width=2,
        #     corner_radius=5,
        #     font=("", 14),
        #     show="*"  # Hide password characters
        # )
        # self.Entry_confirm_password.grid(row=9, column=0, columnspan=2, padx=25, sticky="ew")

        # Buttons
        self.button_save = CTkButton(
            self.frame_form,
            height=38,
            text="Update Profile",
            text_color="#FFFFFF",
            fg_color="#3A36F5",
            border_color="#3A36F5",
            font=("", 14),
            cursor="hand2",
            hover=False
        )
        self.button_save.grid(row=6, column=0, padx=(25, 3.125), pady=(30, 25), sticky="e")

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
            hover=False
        )
        self.button_cancel.grid(row=6, column=1, padx=(3.125, 25), pady=(30, 25), sticky="w")

    def user_details_update(self, str_username: str, str_phone: str):
        self.Entry_username.delete(0, 'end')
        self.Entry_username.insert(0, str_username)

        self.Entry_phoneno.delete(0, 'end')
        self.Entry_phoneno.insert(0, str_phone)

    # def reset_edit_form(self):
