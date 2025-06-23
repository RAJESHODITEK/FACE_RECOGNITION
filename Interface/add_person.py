from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCanvas, CTkImage, CTkScrollableFrame
from PIL import Image
from tkinter import StringVar

class AddpersonInteface(CTkFrame):

    def __init__(self, *args, root_width : int = 1920, root_height : int = 1080, **kwargs):

        super().__init__(*args, **kwargs)

        self.configure(fg_color = "#F1F5FA", corner_radius = 0)

        self.bool_dropdown_opened = False
        self.list_company = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen", "Hyundai", "Nissan"]
        self.list_vehicl_type = ["Personal", "Truck", "Motorcycle", "Bus", "Van", "Auto", "Taxi"]
        self.list_widgets = []

        i_form_width = int( (int(root_width * 0.89))* 0.885)
        i_form_height = int((int (root_height * 0.88)) * 0.78)

        x = int(i_form_height * 0.07952286282306163)

        self.frame_form = CTkFrame(
            self,
            width = i_form_width,
            height = i_form_height,
            fg_color = "#FFFFFF",
            corner_radius=10
        )
        self.frame_form.columnconfigure(0, weight = 1, uniform ='a')
        self.frame_form.columnconfigure(1, weight = 1, uniform = 'a')
        self.frame_form.rowconfigure(2, weight = 1)
        self.frame_form.grid_propagate(False)
        self.frame_form.pack(side="top", expand=False, padx=10, pady=(30,0))

        self.label_heading = CTkLabel(
            self.frame_form,
            text="Add New person",
            text_color="#2C2C2C",
            font = ("", 18, "bold"),
            anchor="w"
        )
        self.label_heading.grid(row=0, column=0, columnspan=2, padx=25, pady=(25,10), sticky="ew")

        self.canvas_underline = CTkCanvas(
            self.frame_form, 
            height=1, 
            bg="#D2D2D2", 
            bd=0, 
            highlightthickness=0
            )
        self.canvas_underline.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        self.frame_form_lcol = CTkFrame(
            self.frame_form,
            fg_color = "transparent",
        )
        self.frame_form_lcol.columnconfigure(0, weight=1)
        self.frame_form_lcol.grid(row = 2, column = 0, sticky = "nsew")

        self.frame_form_rcol = CTkFrame(
            self.frame_form,
            fg_color = "transparent",
        )
        self.frame_form_rcol.columnconfigure(0, weight=1)
        self.frame_form_rcol.grid(row = 2, column = 1, sticky = "nsew")
        
        self.frame_company_label = CTkFrame(
          self.frame_form_lcol,
          height=30,
          fg_color="transparent"  
        )
        self.frame_company_label.grid(row=0, column=0, padx=(25,12.5), pady=(20,0), sticky="ew")

        self.label_company = CTkLabel(
            self.frame_company_label,
            text="person Comapny",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_company.pack(side="left")

        self.label_company_error = CTkLabel(
            self.frame_company_label,
            text="",
            text_color="#FF0000",
            font=("", 12),
        )
        self.label_company_error.pack(side="left", padx=(10,0))

        self.frame_company_dropdown = CTkFrame(
            self.frame_form_lcol,
            height=x,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_company_dropdown.columnconfigure(0, weight = 1)
        self.frame_company_dropdown.rowconfigure(0, weight = 1)
        self.frame_company_dropdown.grid(row=1, column=0, padx=(25,12.5), sticky="ew")

        self.entry_selected_company = CTkEntry(
            self.frame_company_dropdown,
            height = x,
            fg_color = "#F6F6F6",
            textvariable = StringVar(value="Select an option"),
            text_color="#828282",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14),
            state="disabled"
        )
        self.entry_selected_company.grid(row = 0, column = 0, sticky = "nsew")

        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.button_select_company = CTkButton(
            self.frame_company_dropdown,
            image=img_down_arraow,
            height = 35,
            width = 35,
            text = "",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
            command=lambda: self.popup_dropdown(self.list_company, entry_destination = self.entry_selected_company,i_row = 2)
        )
        self.button_select_company.grid(row = 0, column = 0, sticky = "e", padx=3, pady=1.5)



        self.frame_model_label = CTkFrame(
            self.frame_form_rcol,
            height = 30,
            fg_color = "transparent"
        )
        self.frame_model_label.grid(row=0, column=0, padx=(12.5,25), pady=(20,0), sticky="ew")

        self.label_model = CTkLabel(
            self.frame_model_label,
            text="person Model",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_model.pack(side="left")

        self.label_model_error = CTkLabel(
            self.frame_model_label,
            text="",
            text_color="#FF0000",
            font=("", 12),
        )
        self.label_model_error.pack(side="left", padx=(10,0))

        self.entry_model = CTkEntry(
            self.frame_form_rcol,
            height = x,
            fg_color = "#F6F6F6",
            placeholder_text = "Enter person Model",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_model.grid(row=1, column=0, padx=(12.5, 25), sticky="ew")



        self.frame_type_label = CTkFrame(
            self.frame_form_lcol,
            height = 30,
            fg_color="transparent",
        )
        self.frame_type_label.grid(row=2, column=0, padx=(25,12.5), pady=(10,0), sticky="ew")

        self.label_type = CTkLabel(
            self.frame_type_label,
            text="person Type",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_type.pack(side="left")

        self.label_type_error = CTkLabel(
            self.frame_type_label,
            text="",
            text_color="#FF0000",
            font=("", 12),
        )
        self.label_type_error.pack(side="left", padx=(10,0))

        self.frame_type = CTkFrame(
            self.frame_form_lcol,
            height=x,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_type.columnconfigure(0, weight = 1)
        self.frame_type.rowconfigure(0, weight = 1)
        self.frame_type.grid(row=3, column=0, padx=(25,12.5), sticky="ew")

        self.entry_selected_type = CTkEntry(
            self.frame_type,
            height = x,
            fg_color = "#F6F6F6",
            textvariable = StringVar(value="Select an option"),
            text_color="#828282",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14),
            state="disabled"
        )
        self.entry_selected_type.grid(row = 0, column = 0, sticky = "nsew")

        img_down_arraow_new = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.button_select_type = CTkButton(
            self.frame_type,
            image=img_down_arraow_new,
            height = 35,
            width = 35,
            text = "",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
            command=lambda: self.popup_dropdown(self.list_vehicl_type, entry_destination = self.entry_selected_type, i_row = 4)
        )
        self.button_select_type.grid(row = 0, column = 0, sticky = "e", padx=4, pady=1.5)



        self.frame_number_label = CTkFrame(
            self.frame_form_rcol,
            height = 30,
            fg_color="transparent",
        )
        self.frame_number_label.grid(row=2, column=0, padx=(12.5,25), pady=(10,0), sticky="ew")

        self.label_number = CTkLabel(
            self.frame_number_label,
            text="person Number",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_number.pack(side = "left")

        self.label_number_error = CTkLabel(
            self.frame_number_label,
            text="",
            text_color="#FF0000",
            font=("", 12),
        )
        self.label_number_error.pack(side="left", padx=(10,0))

        self.entry_number = CTkEntry(
            self.frame_form_rcol,
            height = x,
            fg_color = "#F6F6F6",
            placeholder_text = "Enter person Number",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_number.grid(row=3, column=0, padx=(12.5, 25), sticky="ew")


        self.frame_color_label = CTkFrame(
            self.frame_form_lcol,
            height = 30,
            fg_color="transparent",
        )
        self.frame_color_label.grid(row=4, column=0, padx=(25, 12.5), pady=(10,0), sticky="ew")

        self.label_color = CTkLabel(
            self.frame_color_label,
            text="person Color",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_color.pack(side="left")

        self.label_color_error = CTkLabel(
            self.frame_color_label,
            text="",
            text_color="#FF0000",
            font=("", 12),
        )
        self.label_color_error.pack(side="left", padx=(10,0))

        self.entry_color = CTkEntry(
            self.frame_form_lcol,
            height = x,
            fg_color = "#F6F6F6",
            placeholder_text = "Enter person Color",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_color.grid(row=5, column=0, padx=(25, 12.5), sticky="ew")


        self.frame_date_label = CTkFrame(
            self.frame_form_rcol,
            height = 30,
            fg_color="transparent",
        )
        self.frame_date_label.grid(row=4, column=0, padx=(12.5, 25), pady=(10,0), sticky="ew")

        self.label_date = CTkLabel(
            self.frame_date_label,
            text="Manufacturing Year",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_date.pack(side="left")

        self.label_date_error = CTkLabel(
            self.frame_date_label,
            text="",
            text_color="#FF0000",
            font=("", 12),
        )
        self.label_date_error.pack(side="left", padx=(10,0))

        self.entry_date = CTkEntry(
            self.frame_form_rcol,
            height=x,
            fg_color = "#F6F6F6",
            placeholder_text = "Enter Manufacturing Year",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_date.grid(row=5, column=0, padx=(12.5, 25), sticky="ew")



        self.frame_owner_label = CTkFrame(
            self.frame_form_lcol,
            height = 30,
            fg_color="transparent",
        )
        self.frame_owner_label.grid(row=6, column=0, padx=(25, 12.5), pady=(10,0), sticky="ew")

        self.label_owner = CTkLabel(
            self.frame_owner_label,
            text="person Owner",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_owner.pack(side="left")

        self.label_owner_error = CTkLabel(
            self.frame_owner_label,
            text="",
            text_color="#FF0000",
            font=("", 12),
        )
        self.label_owner_error.pack(side="left", padx=(10,0))

        self.entry_owner = CTkEntry(
            self.frame_form_lcol,
            height = x,
            fg_color = "#F6F6F6",
            placeholder_text = "Enter person Owner Number",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_owner.grid(row=7, column=0, padx=(25, 12.5), sticky="ew")

        self.label_empty = CTkLabel(
            self.frame_form_rcol,
            text="",
        )
        self.label_empty.grid(row=6, column=0, padx=(12.5, 25), pady=(10,0), sticky="ew")

        self.entry_empty = CTkEntry(
            self.frame_form_rcol,
            height=x,
            fg_color = "transparent",
            placeholder_text = "",
            border_width = 0,
            corner_radius = 0,
            state="disabled"
        )
        self.entry_empty.grid(row=7, column=0, padx=(12.5, 25), sticky="ew")

        self.entry_owner = CTkEntry(
            self.frame_form_lcol,
            height = x,
            fg_color = "#F6F6F6",
            placeholder_text = "Enter person Owner",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_owner.grid(row=7, column=0, padx=(25, 12.5), sticky="ew")

        self.button_save = CTkButton(
            self.frame_form_lcol,
            height = 38,
            width = 100,
            text = "Save", 
            text_color = "#FFFFFF", 
            fg_color = "#3A36F5", 
            border_color="#3A36F5",
            font=("", 14),
            cursor="hand2",
            hover=False
        )
        self.button_save.grid(row=8, column=0, padx=(25, 3.125), pady=(30,25), sticky="e")

        self.button_cancel = CTkButton(
            self.frame_form_rcol,
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
        self.button_cancel.grid(row=8, column=0, padx=(3.125, 25), pady=(30,25), sticky="w")

        self.frame_maindropdown_window = CTkFrame(
                self.frame_form_lcol,
                fg_color="#DEDEDE",
                height = x,
                corner_radius = 5
            )
        self.frame_maindropdown_window.columnconfigure(0, weight = 1)
        self.frame_maindropdown_window.rowconfigure(0, weight=1)
        self.frame_maindropdown_window.grid_propagate(False)

        self.frame_popup_table = CTkScrollableFrame(
            self.frame_maindropdown_window,
            fg_color="#FFFFFF",
            height=x,
            corner_radius = 5
        )
        self.frame_popup_table.columnconfigure(0, weight = 1)
        self.frame_popup_table.grid(row = 0, column = 0, padx=(1,5), pady=(1,3), sticky="nsew")

        self.bind_widgets(self)

    def get_all_children(self, parent):
            children = parent.winfo_children()
            all_children = [] + children
            for child in children:
                all_children.extend(self.get_all_children(child))
            return all_children
    
    def bind_widgets(self, parent):
        self.list_widgets = self.get_all_children(parent)
        
        for widget in self.list_widgets:
            if (widget == self.button_select_company or widget == self.button_select_type):
                continue
            if isinstance(widget, (CTkLabel, CTkButton, CTkFrame, CTkEntry)):
                widget.bind("<Button-1>", self.close_dropdown)

    def popup_dropdown(self, list_data : list = [], entry_destination : CTkEntry = None, i_row : int = None):
        if self.bool_dropdown_opened is False:
            for index, row_data in enumerate(list_data):
                button_options = CTkButton(
                    self.frame_popup_table,
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
            self.frame_maindropdown_window.grid(row=i_row, column=0, rowspan=4, sticky="nsew", padx=(25, 12.5), pady=(5,0))
            
            self.frame_maindropdown_window.tkraise()
        else:
            self.frame_maindropdown_window.grid_forget()
        
        self.bool_dropdown_opened = not self.bool_dropdown_opened

    def close_dropdown(self, event):
        self.frame_maindropdown_window.grid_forget()
        self.bool_dropdown_opened = False

    def select_option(self, selected_option: str, entry_destination : CTkEntry):

        self.update_on_input_changed(entry_input_field = entry_destination, str_border_color = "#DEDEDE")
         
        entry_destination.configure(state="normal", text_color = "#414141")
        entry_destination.delete(0, "end")
        entry_destination.insert(0, selected_option)
        entry_destination.configure(state="disabled")

        self.frame_maindropdown_window.grid_forget()
        self.bool_dropdown_opened = False
    
    def update_on_input_changed(self, entry_input_field : CTkEntry = None, label_error : CTkLabel = None, str_error : str = "", str_border_color : str = None):
        if(entry_input_field is not None):
            if(str_border_color is not None):
                entry_input_field.configure(border_color = str_border_color)
            if(label_error is None):
                if entry_input_field == self.entry_selected_company:
                    label_error = self.label_company_error
                elif entry_input_field == self.entry_selected_type:
                    label_error = self.label_type_error

        if(label_error is not None):
            label_error.configure(text=str_error)
        self.update()

    def reset_interface(self):
        self.entry_selected_company.configure(state="normal", text_color = "#828282", border_color = "#DEDEDE")
        self.entry_selected_company.delete(0, "end")
        self.entry_selected_company.insert(0, "Select an option")
        self.entry_selected_company.configure(state="disabled")

        self.entry_selected_type.configure(state="normal", text_color = "#828282", border_color = "#DEDEDE")
        self.entry_selected_type.delete(0, "end")
        self.entry_selected_type.insert(0, "Select an option")
        self.entry_selected_type.configure(state="disabled")

        for widget in [self.entry_model, self.entry_number, self.entry_color, self.entry_date, self.entry_owner]:
            widget.delete(0, "end")
            widget.configure(border_color = "#DEDEDE")
        
        self.entry_model.configure(placeholder_text = "Enter person Model")
        self.entry_number.configure(placeholder_text = "Enter person Number")
        self.entry_color.configure(placeholder_text = "Enter person Color")
        self.entry_date.configure(placeholder_text = "Enter Manufacturing Year")
        self.entry_owner.configure(placeholder_text = "Enter person Owner")

        for widget in [self.label_company_error, self.label_model_error, self.label_type_error, 
                       self.label_number_error, self.label_color_error, self.label_date_error, 
                       self.label_owner_error]:
            widget.configure(text="")

        self.frame_maindropdown_window.grid_forget()
        self.bool_dropdown_opened = False
    
        self.frame_form.focus()

