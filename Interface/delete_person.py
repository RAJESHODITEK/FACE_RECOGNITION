from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkImage, CTkScrollableFrame
from tkinter import StringVar
from PIL import Image

class DeletepersonInteface(CTkFrame):

    def __init__(self, *args, root_width : int = 1920, root_height : int = 1080, **kwargs):

        super().__init__(*args, **kwargs)

        self.configure(fg_color = "#F1F5FA", corner_radius = 0)

        self.bool_dropdown_opened = False
 
        self.label_heading = CTkLabel(
            self,
            text="Delete person",
            text_color="#2C2C2C",
            font=("", 18, "bold")
        )
        self.label_heading.pack(pady=(50, 10))

        i_form_width = int(root_width * 0.33)
        i_form_height = int(root_height * 0.35)

        self.frame_form = CTkFrame(
            self,
            width=i_form_width,
            height=i_form_height,
            fg_color="#FFFFFF",
            corner_radius=10
        )
        self.frame_form.columnconfigure(0, weight=1)
        self.frame_form.columnconfigure(1, weight=1)
        self.frame_form.grid_propagate(False)
        self.frame_form.pack(side="top", expand=False, padx=10, pady=(20,30))

        self.frame_person_label = CTkFrame(
            self.frame_form,
            height=30,
            fg_color="transparent"  
        )
        self.frame_person_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20,0), sticky="ew")

        self.label_person = CTkLabel(
            self.frame_person_label,
            text="person",
            font=("", 14),
            text_color="#2C2C2C"
        )
        self.label_person.pack(side="left")

        self.label_person_error = CTkLabel(
            self.frame_person_label,
            text="",
            text_color="#FF0000",
            font=("", 12),
        )
        self.label_person_error.pack(side="left", padx=(10,0))

        self.frame_person_dropdown = CTkFrame(
            self.frame_form,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_person_dropdown.columnconfigure(0, weight = 1)
        self.frame_person_dropdown.rowconfigure(0, weight = 1)
        self.frame_person_dropdown.grid(row=1, column=0, columnspan=2, padx=20, sticky="ew")

        self.entry_selected_person = CTkEntry(
            self.frame_person_dropdown,
            height = 40,
            fg_color = "#F6F6F6",
            textvariable = StringVar(value="Select an option"),
            text_color="#828282",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14),
            state="disabled"
        )
        self.entry_selected_person.grid(row = 0, column = 0, sticky = "nsew")

        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.button_select_person = CTkButton(
            self.frame_person_dropdown,
            image=img_down_arraow,
            height = 35,
            width = 35,
            text = "",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_person.grid(row = 0, column = 0, sticky = "e", padx=3, pady=1.5)

        self.frame_password_label = CTkFrame(
            self.frame_form,
            height=30,
            fg_color="transparent"  
        )
        self.frame_password_label.grid(row=2, column=0, columnspan=2,  padx=20, pady=(10,0), sticky="ew")

        self.label_password = CTkLabel(
            self.frame_password_label,
            text="Password",
            font=("", 14),
            text_color="#2C2C2C"
        )
        self.label_password.pack(side="left")

        self.label_password_error = CTkLabel(
            self.frame_password_label,
            text="",
            text_color="#FF0000",
            font=("", 12),
        )
        self.label_password_error.pack(side="left", padx=(10,0))

        self.entry_password = CTkEntry(
            self.frame_form,
            height = 40,
            fg_color = "#F6F6F6",
            placeholder_text = "Enter Passwrd",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_password.grid(row=3, column=0, columnspan=2, padx=20, sticky="ew")

        self.button_delete = CTkButton(
            self.frame_form,
            height = 38,
            width = 100,
            text = "Delete", 
            text_color = "#FFFFFF", 
            fg_color = "#3A36F5", 
            border_color="#3A36F5",
            font=("", 14),
            cursor="hand2",
            hover=False
        )
        self.button_delete.grid(row=4, column=0, padx=(25, 3.125), pady=(20,25), sticky="e")

        self.button_cancel = CTkButton(
            self.frame_form,
            height = 38,
            width = 100,
            text = "Cancel", 
            text_color = "#FFFFFF", 
            fg_color = "#6C757D", 
            border_color="#6C757D",
            font=("", 14),
            cursor="hand2",
            hover=False
        )
        self.button_cancel.grid(row=4, column=1, padx=(3.125, 25), pady=(20,25), sticky="w")

        self.frame_maindropdown_window = CTkFrame(
                self.frame_form,
                fg_color="#DEDEDE",
                height = 40,
                corner_radius = 5
            )
        self.frame_maindropdown_window.columnconfigure(0, weight = 1)
        self.frame_maindropdown_window.rowconfigure(0, weight=1)
        self.frame_maindropdown_window.grid_propagate(False)

        self.frame_dropdown_table = CTkScrollableFrame(
            self.frame_maindropdown_window,
            fg_color="#FFFFFF",
            height=40,
            corner_radius = 5
        )
        self.frame_dropdown_table.columnconfigure(0, weight = 1)
        self.frame_dropdown_table.grid(row = 0, column = 0, padx=(1,5), pady=(1,3), sticky="nsew")

    def popup_dropdown(self, list_data : list = [], entry_destination : CTkEntry = None, i_row : int = None):
            if self.bool_dropdown_opened is False:
                for index, row_data in enumerate(list_data):
                    button_options = CTkButton(
                        self.frame_dropdown_table,
                        text = f"    {row_data}",
                        height = 20,
                        fg_color = "transparent",
                        text_color="#414141",
                        font = ("", 14),
                        corner_radius = 0,
                        hover_color = "#F6F6F6",
                        anchor = "w",
                        command=lambda selected_option=row_data: self.select_option(selected_option, entry_destination)
                    )
                    button_options.grid(row = index, column = 0, sticky = "nsew")

                self.frame_maindropdown_window.grid_propagate(False)
                self.frame_maindropdown_window.grid(row=i_row, column=0, rowspan=3, columnspan = 2, sticky="nsew", padx=20, pady=(5,0))

                self.frame_maindropdown_window.tkraise()
            else:
                self.frame_maindropdown_window.grid_forget()
            
            self.bool_dropdown_opened = not self.bool_dropdown_opened



    def select_option(self, selected_option: str, entry_destination : CTkEntry):

        self.update_on_input_changed(entry_input_field = entry_destination, str_border_color = "#DEDEDE")
         
        entry_destination.configure(state="normal", text_color = "#414141")
        entry_destination.delete(0, "end")
        entry_destination.insert(0, selected_option)
        entry_destination.configure(state="disabled")
        self.close_dropdown(None)



    def close_dropdown(self, event):
        self.frame_maindropdown_window.grid_forget()
        self.bool_dropdown_opened = False

        for child in self.frame_dropdown_table.winfo_children():
            child.destroy()


    def update_on_input_changed(self, entry_input_field : CTkEntry = None, label_error : CTkLabel = None, str_error : str = "", str_border_color : str = None):
        if(entry_input_field is not None):
            if(str_border_color is not None):
                entry_input_field.configure(border_color = str_border_color)
            if(label_error is None):
                if entry_input_field == self.entry_selected_person:
                    label_error = self.label_person_error

        if(label_error is not None):
            label_error.configure(text=str_error)
        self.update()

    def reset_interface(self):
        self.entry_selected_person.configure(state="normal", text_color = "#828282", border_color = "#DEDEDE")
        self.entry_selected_person.delete(0, "end")
        self.entry_selected_person.insert(0, "Select an option")
        self.entry_selected_person.configure(state="disabled")
        
        self.entry_password.delete(0, "end")
        self.entry_password.configure(placeholder_text = "Enter Password", border_color = "#DEDEDE")

        self.label_person_error.configure(text="")
        self.label_password_error.configure(text="")

        self.close_dropdown(None)
        self.frame_form.focus()