from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCanvas, CTkScrollableFrame, CTkImage, CTkCheckBox, \
    CTkToplevel
from tkinter import StringVar, Toplevel
from PIL import Image

class VehicleListInteface(CTkFrame):

    def __init__(self, *args, root_width : int = 1920, root_height : int = 1080, **kwargs):

        super().__init__(*args, **kwargs)

        self.vehicle_data = []
        self.bool_filter_popup = False
        self.bool_owner_dropdown_opened = False
        self.bool_type_dropdown_opened = False
        self.bool_color_dropdown_opened = False
        self.active_dropdown_frame=False

        self.configure(fg_color = "#F1F5FA", corner_radius = 0)

        self.dict_columns_buttons = {}
        self.selected_vehicle_set=set() # stored the selected vehicle in checkbox dt :18-03-2025

        try:
            # Load arrow images - ensure these paths are correct
            self.img_arrow_up = CTkImage(Image.open("Resources/images/img_arrow_up.png"),
                                         size=(20, 20))
            self.img_arrow_down = CTkImage(Image.open("Resources/images/img_arrow_down.png"),
                                           size=(20, 20))
            self.img_arrow_neutral = CTkImage(Image.open("Resources/images/noSort_arrow.png"),
                                              size=(20, 20))
        except Exception as e:
            print(f"Error loading images: {e}")
            # Provide fallback images if needed
            self.img_arrow_up = CTkImage(Image.new('RGB', (12, 12), color='white'), size=(15, 15))
            self.img_arrow_down = CTkImage(Image.new('RGB', (12, 12), color='white'), size=(15, 15))
            self.img_arrow_neutral = CTkImage(Image.new('RGB', (12, 12), color='white'), size=(15, 15))

        self.i_start_index = 0
        self.i_end_index = 0
        self.i_total_data = 0
        self.dict_filter_criteria = {
            "str_owner" : "%",
            "str_type" : "%",
            "str_color" : "%",
            "str_vehicle_number": ""
        }

        i_form_width = int( (int(root_width * 0.89))* 0.885)
        i_form_height = int((int (root_height * 0.88)) * 0.9)

        self.frame_form = CTkFrame(
            self,
            width = i_form_width,
            height = i_form_height,
            fg_color = "#FFFFFF",
            corner_radius=10
        )
        self.frame_form.columnconfigure(0, weight = 1, uniform="a")
        self.frame_form.rowconfigure(3, weight=1)
        self.frame_form.grid_propagate(False)
        self.frame_form.pack(side="top", expand=False, padx=10, pady=30)

        self.frame_header = CTkFrame(
            self.frame_form,
            height = int(i_form_height * 0.12),
            fg_color = "transparent",
            corner_radius=10
        )
        self.frame_header.columnconfigure(0, weight = 1)
        self.frame_header.columnconfigure(1, weight = 2)
        self.frame_header.columnconfigure(2, weight = 2)
        self.frame_header.grid(column = 0, row = 0, sticky="we", padx = 5, pady = (5,5))

        self.label_heading = CTkLabel(
            self.frame_header,
            text="Vehicle List",
            text_color = "#2C2C2C",
            height = 38,
            font = ("", 18, "bold"),
            corner_radius = 10,
            anchor="w",
            fg_color="transparent"
        )
        self.label_heading.grid(row=0, column=0, padx=10, pady=(15,0), sticky="ew")

        self.frame_header_rcol = CTkFrame(
            self.frame_header,
            height = int (i_form_height * 0.07),
            fg_color = "transparent",
            corner_radius=10
        )
        self.frame_header_rcol.rowconfigure(0, weight = 1)
        self.frame_header_rcol.grid(row = 0, column = 1, columnspan = 2,  sticky = "nsew")

        self.button_filter = CTkButton(
            self.frame_header_rcol,
            height = 38,
            width = 100,
            text = "Filter",
            text_color = "white",
            fg_color = "#5A616B",
            font=("", 14),
            cursor="hand2",
            anchor = "center",
            hover=True,
            hover_color='#313A46',
            command=self.reset_filter_form

        )
        self.button_filter.pack(side="right", padx=(4,15), pady=(15,0))

        self.button_Delete_selected = CTkButton(
            self.frame_header_rcol,
            height = 38,
            width = 100,
            text = "Delete",
            text_color = "white",
            fg_color = "#e6e6ff",
            font=("", 14),
            cursor="hand2",
            anchor = "center",
            hover=True,
            state="disabled"
        )
        self.button_Delete_selected.pack(side="right", padx=4, pady=(15,0))

        self.button_Edit = CTkButton(
            self.frame_header_rcol,
            height = 38,
            width = 100,
            text = "Edit",
            text_color = "white",
            fg_color = "#e6e6ff",
            font=("", 14),
            cursor="hand2",
            anchor = "center",
            hover=True,
            state="disabled"
        )
        self.button_Edit.pack(side="right", padx=4, pady=(15,0))

        self.button_Add = CTkButton(
            self.frame_header_rcol,
            height = 38,
            width = 100,
            text = "Add",
            text_color = "white",
            fg_color = "#5A616B",
            font=("", 14),
            cursor="hand2",
            anchor = "center",
            hover=True,
            state="normal"
        )
        self.button_Add.pack(side="right", padx=4, pady=(15,0))

        self.table_search_frame = CTkFrame(
            self.frame_header_rcol,
            height = 38,
            fg_color = "transparent",
            border_width = 2,
            border_color = "#313A46",
            corner_radius = 7,
        )
        self.table_search_frame.pack_propagate(False)
        self.table_search_frame.pack(side="right", padx=(0,4), pady=(15,0))

        img_search_icon = CTkImage(Image.open(".\\Resources\\images\\search_icon.png"), size=(15, 15))
        self.label_search_icon = CTkLabel(
            self.table_search_frame,
            image=img_search_icon,
            text="",
            width = 20,
            height = 30,
            fg_color="transparent"
        )
        self.label_search_icon.pack(side="left", padx = (10,0))

        self.entry_search = CTkEntry(
            self.table_search_frame,
            height = 30,
            placeholder_text="Enter Vehicle Number..",
            placeholder_text_color="#A2B1C7",
            text_color = "#414141",
            border_width=0,
            font = ("", 13),
            fg_color = "transparent",
            corner_radius = 10,
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0,10),pady=(0,1))

        self.canvas_underline = CTkCanvas(
            self.frame_form,
            height=1,
            bg="#D2D2D2",
            bd=0,
            highlightthickness=0
            )
        self.canvas_underline.grid(row=1, column=0, columnspan=2, pady=0, sticky="ew")

        self.frame_table_heading = CTkFrame(
            self.frame_form,
            height = 44,
            fg_color = "#444C57"
        )
        self.frame_table_heading.columnconfigure((0,1,2,3,4), weight = 1, uniform="a")
        self.frame_table_heading.grid_propagate(False)
        self.frame_table_heading.grid(row = 2, column = 0, padx=(15,19), pady=(20,0), sticky = "nsew")

        self.table_headers = ["Vehicle Number", "Vehicle Type", "Vehicle Color", "Owner Name", "Manufacturing Year"]

        for col, value in enumerate(self.table_headers):
            # Create a frame for header content
            header_frame = CTkFrame(
                self.frame_table_heading,
                fg_color="transparent",
                height=45
            )
            header_frame.grid(row=0, column=col, sticky="nsew")
            header_frame.grid_propagate(False)

            # Set initial image - down arrow for Vehicle Number, neutral for others
            initial_image = self.img_arrow_down if value == "Vehicle Number" else self.img_arrow_neutral

            # Create the button
            button = CTkButton(
                header_frame,
                text=f"{value}  ",  # Added extra space for logo
                height=45,
                fg_color="#444C57",
                text_color="#FFFFFF",
                anchor="w",
                font=("", 15, "bold"),
                hover=True,
                hover_color="#313A46",
                corner_radius=0,
                cursor="hand2",
                compound="right",  # Place image to the right of text
                image=initial_image,
            )
            # button.configure(command=lambda btn=button, col=col: self.toggle_sort(btn, col))
            button.pack(side="left", fill="both", expand=True, padx=5)

            # Store the button reference and initial sort state - set Vehicle Number to sorted
            self.dict_columns_buttons[value] = [
                button,
                True if value == "Vehicle Number" else False
            ]
            self.dict_columns_buttons["Vehicle Number"][1] = True

            # Store the button reference and initial sort state - DON'T OVERWRITE THIS
            self.dict_columns_buttons[value] = {
                'button': button,
                'sort_state': 'neutral'
            }
            self.dict_columns_buttons[value] = [button, False]

            self.frame_table_rows = CTkScrollableFrame(
            self.frame_form,
            fg_color = "transparent",
            corner_radius=0
        )
        self.frame_table_rows.columnconfigure((0,1,2,3,4), weight = 1, uniform = "a")
        self.frame_table_rows.grid(row = 3, column = 0, padx=(15,2), pady=(0,20), sticky = "nsew")

        self.label_data_count = CTkLabel(
            self.frame_form,
            text="No Records Found!",
            text_color="#FF0000",
            font = ("", 14),
        )
        self.label_data_count.grid(row = 4, column = 0, padx=15, pady=(0,10), sticky = "w")

        self.button_next = CTkButton(
            self.frame_form,
            height = 38,
            width = 100,
            text="Next",
            text_color = "white",
            fg_color="#444C57",
            border_color="#444C57",
            font=("", 14),
            cursor="hand2",
            anchor = "center",
            hover=False,
        )
        self.button_next.grid(row = 4, column = 0, padx=15, pady=(0,10), sticky = "e")

        self.button_previous = CTkButton(
            self.frame_form,
            height = 38,
            width = 100,
            text ="Previous",
            text_color = "white",
            fg_color="#444C57",
            border_color="#444C57",
            font=("", 14),
            cursor="hand2",
            anchor = "center",
            hover=False,
        )
        self.button_previous.grid(row = 4, column = 0, padx=(15,120), pady=(0,10), sticky = "e")

        self.frame_filter = CTkFrame(
            self.frame_form,
            width = 350,
            height = 450,
            fg_color="#DEDEDE",
            corner_radius=5
        )
        self.frame_filter.columnconfigure(0, weight = 1)
        self.frame_filter.rowconfigure(0, weight=1)
        self.frame_filter.grid_propagate(False)

        self.frame_filter_form = CTkFrame(
            self.frame_filter,
            fg_color="#FFFFFF",
            corner_radius = 4
        )
        self.frame_filter_form.columnconfigure((0,1), weight = 1)
        self.frame_filter_form.rowconfigure((9), weight = 1)
        self.frame_filter_form.grid(row = 0, column = 0, padx=(2,6), pady=(2,5), sticky="nsew")

        self.label_filter_heading = CTkLabel(
            self.frame_filter_form,
            text="Filter Vehicle",
            text_color="#2c2c2c",
            font = ("", 18, "bold"),
            anchor="w"
        )
        self.label_filter_heading.grid(row=0, column=0, columnspan=2, padx=15, pady=(25,10), sticky="ew")

        self.canvas_filter_underline = CTkCanvas(
            self.frame_filter_form,
            height=1,
            bg="#D2D2D2",
            bd=0,
            highlightthickness=0
            )
        self.canvas_filter_underline.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        self.label_filter_owner = CTkLabel(
            self.frame_filter_form,
            text="Owner Name",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w",
        )
        self.label_filter_owner.grid(row=2, column=0, columnspan = 2, padx=15, pady=(5,0), sticky="ew")

        self.frame_owner_dropdown = CTkFrame(
            self.frame_filter_form,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_owner_dropdown.columnconfigure(0, weight = 1)
        self.frame_owner_dropdown.rowconfigure(0, weight = 1)
        self.frame_owner_dropdown.grid(row=3, column=0, columnspan = 2, padx=15, pady=(2,0), sticky="ew")

        self.entry_selected_owner = CTkEntry(
            self.frame_owner_dropdown,
            height=40,
            fg_color="#F6F6F6",
            textvariable=StringVar(value="All"),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
        )
        self.entry_selected_owner.grid(row=0, column=0, sticky="nsew")
        self.entry_selected_owner.bind('<FocusIn>',
                                       lambda e: self.on_entry_focus_in(self.entry_selected_owner, "All"))
        self.entry_selected_owner.bind('<FocusOut>', lambda e: self.on_entry_focus_out(self.entry_selected_owner,
                                                                                       "All"))


        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.button_select_owner = CTkButton(
            self.frame_owner_dropdown,
            image=img_down_arraow,
            height = 35,
            width = 35,
            text = "",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_owner.grid(row = 0, column = 0, sticky = "e", padx=3, pady=1.5)

        self.label_filter_type = CTkLabel(
            self.frame_filter_form,
            text="Vehicle Type",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w",
        )
        self.label_filter_type.grid(row=4, column=0, columnspan = 2, padx=15, pady=(15,0), sticky="ew")

        self.frame_type_dropdown = CTkFrame(
            self.frame_filter_form,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_type_dropdown.columnconfigure(0, weight = 1)
        self.frame_type_dropdown.rowconfigure(0, weight = 1)
        self.frame_type_dropdown.grid(row=5, column=0, columnspan = 2, padx=15, pady=(2,0), sticky="ew")

        self.entry_selected_type = CTkEntry(
            self.frame_type_dropdown,
            height=40,
            fg_color="#F6F6F6",
            textvariable=StringVar(value="All"),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
            state="normal"
        )
        self.entry_selected_type.grid(row=0, column=0, sticky="nsew")
        self.entry_selected_type.bind('<FocusIn>',
                                      lambda e: self.on_entry_focus_in(self.entry_selected_type, "All"))
        self.entry_selected_type.bind('<FocusOut>', lambda e: self.on_entry_focus_out(self.entry_selected_type,
                                                                                      "All"))

        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.button_select_type = CTkButton(
            self.frame_type_dropdown,
            image=img_down_arraow,
            height = 35,
            width = 35,
            text = "",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_type.grid(row = 0, column = 0, sticky = "e", padx=3, pady=1.5)

        self.label_filter_color = CTkLabel(
            self.frame_filter_form,
            text="Vehicle Color",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w",
        )
        self.label_filter_color.grid(row=6, column=0, columnspan = 2, padx=15, pady=(15,0), sticky="ew")

        self.frame_color_dropdown = CTkFrame(
            self.frame_filter_form,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_color_dropdown.columnconfigure(0, weight = 1)
        self.frame_color_dropdown.rowconfigure(0, weight = 1)
        self.frame_color_dropdown.grid(row=7, column=0, columnspan = 2, padx=15, pady=(2,0), sticky="ew")

        self.entry_selected_color = CTkEntry(
            self.frame_color_dropdown,
            height=40,
            fg_color="#F6F6F6",
            textvariable=StringVar(value="All"),
            text_color="#828282",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
        )
        self.entry_selected_color.grid(row=0, column=0, sticky="nsew")
        self.entry_selected_color.bind('<FocusIn>', lambda e: self.on_entry_focus_in(self.entry_selected_color,
                                                                                     "All"))
        self.entry_selected_color.bind('<FocusOut>', lambda e: self.on_entry_focus_out(self.entry_selected_color,
                                                                                       "All"))

        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.button_select_color = CTkButton(
            self.frame_color_dropdown,
            image=img_down_arraow,
            height = 35,
            width = 35,
            text = "",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_color.grid(row = 0, column = 0, sticky = "e", padx=3, pady=1.5)

        self.button_ok = CTkButton(
            self.frame_filter_form,
            height=38,
            width=100,
            text="OK",
            text_color="#FFFFFF",
            fg_color="#444C57",
            font=("", 14, "bold"),
            cursor="hand2",
            corner_radius=5,
            hover_color="#313A46"
        )
        self.button_ok.grid(row=8, column=0, padx=15, pady=(25, 10), sticky="ew")

        self.button_cancel = CTkButton(
            self.frame_filter_form,
            height=38,
            width=100,
            text="Cancel",
            text_color="#313A46",
            fg_color="#FFFFFF",
            border_width=2,
            border_color="#313A46",
            font=("", 14),
            cursor="hand2",
            corner_radius=5,
            hover=False
        )
        self.button_cancel.grid(row=8, column=1, padx=15, pady=(25, 10), sticky="ew")
        self.button_cancel.bind("<Enter>", lambda e: self.button_cancel.configure(fg_color="#313A46", text_color = "#FFFFFF"))
        if self.button_cancel.winfo_exists():
         self.button_cancel.configure(fg_color="#FFFFFF", text_color="#313A46")


        # Set up Filter Popup
        self.button_filter.configure(command=self.show_filter_popup)

        self.frame_maindropdown_window = CTkFrame(
            self.frame_filter_form,
            fg_color="#DEDEDE",
            height=40,
            corner_radius=5
        )
        self.frame_maindropdown_window.columnconfigure(0, weight=1)
        self.frame_maindropdown_window.rowconfigure(0, weight=1)
        self.frame_maindropdown_window.grid_propagate(False)

    def toggle_sort(self, column_index):
        """Toggle sort direction indicator for the column"""
        header = self.table_headers[column_index]
        button = self.dict_columns_buttons[header][0]
        is_sorted = self.dict_columns_buttons[header][1]

        # Reset other columns to neutral
        for other_header in self.table_headers:
            if other_header != header:
                self.dict_columns_buttons[other_header][0].configure(image=self.img_arrow_neutral)
                self.dict_columns_buttons[other_header][1] = False

        if not is_sorted:
            # First click - show down arrow (descending)
            button.configure(image=self.img_arrow_down)
            self.dict_columns_buttons[header][1] = True
            return False  # Descending sort
        else:
            # Second click - show up arrow (ascending)
            button.configure(image=self.img_arrow_up)
            self.dict_columns_buttons[header][1] = False
            return True  # Ascending sort

    def close_filter_dropdown(self):
        if self.bool_filter_popup:
            self.frame_filter.grid_forget()
            self.bool_filter_popup = False


    def show_filter_popup(self):
        """Toggles the filter popup visibility."""
        if self.bool_filter_popup:
            self.frame_filter.grid_forget()
            self.bool_filter_popup = False
        else:
            self.frame_filter.grid(row=0, column=1, sticky="ne", padx=10, pady=10)
            self.bool_filter_popup = True

    def on_entry_focus_in(self, entry, placeholder):
        """Clears placeholder text on entry focus."""
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.configure(text_color="#000000")

    def on_entry_focus_out(self, entry, placeholder):
        """Preserves typed text or restores placeholder if empty."""
        current_text = entry.get().strip()
        has_real_text = False
        if entry == self.entry_selected_owner:
            has_real_text = self.owner_has_real_text
        elif entry == self.entry_selected_type:
            has_real_text = self.type_has_real_text
        elif entry == self.entry_selected_color:
            has_real_text = self.color_has_real_text

        if not current_text or not has_real_text:
            entry.delete(0, "end")
            entry.insert(0, placeholder)
            entry.configure(text_color="#828282")
            if entry == self.entry_selected_owner:
                self.owner_has_real_text = False
            elif entry == self.entry_selected_type:
                self.type_has_real_text = False
            elif entry == self.entry_selected_color:
                self.color_has_real_text = False
        else:
            entry.configure(text_color="#000000")


    def update_table(self, list_vehicle_data : list):

        for child in self.frame_table_rows.winfo_children():
            child.destroy()

        self.current_selected_vehicle = None


        for row_index, row_data in enumerate(list_vehicle_data):
            row_bg_color = "transparent" if row_index % 2 == 0 else "#F7F9FB"

            vehicle_number = row_data.get("vehicle_number", "")


            for col_index, cell_data in enumerate(row_data.values()):
                rows = CTkLabel(
                    self.frame_table_rows,
                    text=cell_data,
                    height=40,
                    fg_color=row_bg_color,
                    anchor="w",
                    font=("", 14),
                    padx=12,
                    text_color="#2c2c2c"
                )
                rows.grid(row=row_index*2, column=col_index, padx=0, sticky="nsew")

                if(col_index == 4) : break

            checkbox = CTkCheckBox(
                self.frame_table_rows,
                text="",
                border_width=1.5,
                corner_radius=2,
                fg_color="#2C2C2C",
                width=10,
                height=10,
                hover=False,
                # command=lambda data=row_data: self.handle_checkbox_click(data),
                command=lambda vn=vehicle_number, rd=row_data, idx=row_index: self.on_checkbox_click(vn,rd, idx)
            )
            checkbox.grid(row=row_index*2, column=col_index, padx=(0,5), sticky="e")
            if vehicle_number in self.selected_vehicle_set: # check whether the vehicle is selected or not  dt :18-03-2025
                checkbox.select()


            canvas_underline = CTkCanvas(
                self.frame_table_rows,
                height=1,
                bg="#D7DDE5",
                bd=0,
                highlightthickness=0
            )
            canvas_underline.grid(row=row_index*2 + 1, column=0, columnspan=len(row_data), padx=0, pady=0, sticky="ew")

        self.on_page_change()


    def toggle_filter_popup(self):
        if (self.bool_filter_popup is False): # Popup is closed, need to opened it
            self.frame_filter.grid_propagate(False)
            self.frame_filter.grid(row=2, column = 0, rowspan = 2, sticky = "ne", padx=19, pady=(2,80))
            self.frame_filter.tkraise()
        else:                               # Popup is opened, need to closed it
            self.frame_filter.grid_forget()

        self.bool_filter_popup = not self.bool_filter_popup

    def popup_dropdown(self, list_data: list = [], entry_destination: CTkEntry = None, i_row: int = None,
                       i_rowspan: int = 2):
        # First, make sure any existing dropdown is closed
        self.close_filter_dropdown(None)

        frame_dropdown_table = CTkScrollableFrame(
            self.frame_maindropdown_window,
            fg_color="#FFFFFF",
            height=40,
            corner_radius=5
        )
        frame_dropdown_table.columnconfigure(0, weight=1)
        frame_dropdown_table.grid(row=0, column=0, padx=(1, 5), pady=(1, 3), sticky="nsew")
        if list_data:
            i_last_idx = len(list_data) - 1
        else:
            i_last_idx = 0

        for index, row_data in enumerate(list_data):
            button_options = CTkButton(
                frame_dropdown_table,
                text=f"    {row_data}",
                height=20,
                fg_color="transparent",
                text_color="#414141",
                font=("", 14),
                corner_radius=0,
                hover_color="#F6F6F6",
                anchor="w",
                command=lambda selected_option=row_data: self.select_option_filter(selected_option, entry_destination)
            )
            button_options.grid(row=index, column=0, sticky="nsew")

            if index == i_last_idx:
                button_options.configure(font=("", 14, "bold"))

        self.frame_maindropdown_window.grid_propagate(False)
        self.frame_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, columnspan=2, sticky="nsew",
                                            padx=15, pady=(5, 2))
        self.frame_maindropdown_window.tkraise()

    def close_filter_dropdown(self, event):
        if hasattr(self, 'frame_maindropdown_window') and self.frame_maindropdown_window is not None:
            self.frame_maindropdown_window.grid_forget()
            for child in self.frame_maindropdown_window.winfo_children():
                child.destroy()
                #self.reset_filter_form()

    def on_key_press(self, entry, field_type):
        """Track when real text has been entered"""
        if field_type == "owner":
            self.owner_has_real_text = True
        elif field_type == "type":
            self.type_has_real_text = True
        elif field_type == "color":
            self.color_has_real_text = True


    def select_option_filter(self, selected_option: str, entry_destination: CTkEntry):
        """Handle selection from dropdown"""
        entry_destination.configure(state="normal", text_color="#414141")
        entry_destination.delete(0, "end")
        entry_destination.insert(0, selected_option)

        # Set the real text flag when selecting from dropdown
        if entry_destination == self.entry_selected_owner:
            self.owner_has_real_text = True


            self.bool_owner_dropdown_opened = False
        elif entry_destination == self.entry_selected_type:
            self.type_has_real_text = True
            self.bool_type_dropdown_opened = False
        elif entry_destination == self.entry_selected_color:
            self.color_has_real_text = True
            self.bool_color_dropdown_opened = False

        self.close_filter_dropdown(None)

    def reset_interface(self):
        # Add safety check
        if hasattr(self, 'frame_maindropdown_window') and self.frame_maindropdown_window is not None:
            self.close_filter_dropdown(None)

        self.reset_filter_form()

        self.entry_search.delete(0, "end")
        self.entry_search.configure(placeholder_text="Enter Vehicle Number..")

        if self.bool_filter_popup is True:
            self.toggle_filter_popup()

        for child in self.frame_table_rows.winfo_children():
            child.destroy()

        # Reset column sort indicators - Add this code
        for header in self.table_headers:
            if header == "Vehicle Number":
                # Set default sorting on Vehicle Number (descending)
                self.dict_columns_buttons[header][0].configure(image=self.img_arrow_down)
                self.dict_columns_buttons[header][1] = True
            else:
                # Reset all other columns to neutral
                self.dict_columns_buttons[header][0].configure(image=self.img_arrow_neutral)
                self.dict_columns_buttons[header][1] = False

        self.i_start_index = 0
        self.i_end_index = 0


    def clear_focus(self):
        self.focus_set()

    def reset_filter_form(self):
        """Reset all filters and their real text flags"""
        self.owner_has_real_text = False
        self.type_has_real_text = False
        self.color_has_real_text = False

        self.entry_selected_owner.configure(text_color="#828282", border_color="#DEDEDE")
        self.entry_selected_owner.delete(0, "end")
        self.entry_selected_owner.insert(0, "All")
        self.entry_selected_owner.configure(textvariable=StringVar(value="All"), state="normal")
        self.close_filter_dropdown(None)
       # self.entry_selected_owner.configure(textvariable=(value="All"), state="normal")

        self.entry_selected_type.configure(text_color="#828282", border_color="#DEDEDE")
        self.entry_selected_type.delete(0, "end")
        self.entry_selected_type.insert(0, "All")
        self.entry_selected_type.configure(textvariable=StringVar(value="All"), state="normal")

        self.entry_selected_color.configure(text_color="#828282", border_color="#DEDEDE")
        self.entry_selected_color.delete(0, "end")
        self.entry_selected_color.insert(0, "All")
        self.entry_selected_color.configure(textvariable=StringVar(value="All"), state="normal")

    def on_page_change(self):
        if self.i_total_data == 0:
            self.label_data_count.configure(
                text="No Records Found!",
                text_color="#FF0000"
            )
        else:
            self.label_data_count.configure(
                text=f"Showing {self.i_start_index} - {self.i_end_index} of {self.i_total_data} entries",
                text_color="#2c2c2c"
            )

        self.update_button_state(
            button=self.button_previous,
            state="disabled" if self.i_start_index <= 1 else "normal",
            cursor="X_cursor" if self.i_start_index <= 1 else "hand2",
            fg_color="#e6e6ff" if self.i_start_index <= 1 else "#444C57",
            hover_color="#313A46" if self.i_start_index <= 1 else "#313A46",
        )

        self.update_button_state(
            button=self.button_next,
            state="disabled" if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else "normal",
            cursor="X_cursor" if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else "hand2",
            fg_color="#e6e6ff" if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else "#444C57",
            hover_color="#313A46" if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else "#313A46",
        )


    def update_button_state(self, button, state, cursor, fg_color, hover_color):
        button.configure(state=state, cursor=cursor, fg_color=fg_color)
        button.unbind("<Enter>")
        button.unbind("<Leave>")
        if state == "normal":
            button.bind("<Enter>", lambda e: button.configure(fg_color=hover_color))
            button.bind("<Leave>", lambda e: button.configure(fg_color=fg_color))

    def reset_filter_criteria(self):
        self.dict_filter_criteria["str_owner"] = "%"
        self.dict_filter_criteria["str_type"] = "%"
        self.dict_filter_criteria["str_color"] = "%"
        self.dict_filter_criteria["str_vehicle_number"] = ""

    def on_checkbox_click(self, vehicle_number,row_data, row_index):

        if vehicle_number in self.selected_vehicle_set:
            self.selected_vehicle_set.remove(vehicle_number)

        else:
            self.selected_vehicle_set.add(vehicle_number)

        if self.current_selected_vehicle is not None and self.current_selected_vehicle != row_index:
            try:
                previous_checkbox = self.frame_table_rows.grid_slaves(row=self.current_selected_vehicle * 2, column=5)[0]
            except Exception as e:
                print(e)
        self.update_button_states()

    def reset_checkbox(self):
        self.selected_vehicle_set.clear()
        self.update_button_states()
        self.destroy_add_vehicle_form()
        self.destroy_edit_vehicle_form()



    def update_button_states(self):
        num_selected = len(self.selected_vehicle_set)

        if num_selected == 0:
            self.button_Add.configure(
                state="normal",
                fg_color="#5A616B",
                text_color="#FFFFFF",
                hover_color="#313A46"
            )
            self.button_Edit.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )
            self.button_Delete_selected.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )

        elif num_selected == 1:
            self.button_Add.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )
            self.button_Edit.configure(
                state="normal",
                fg_color="#5A616B",
                text_color="#FFFFFF",
                 hover_color="#313A46"
            )
            self.button_Delete_selected.configure(
                state="normal",
                fg_color="#5A616B",
                text_color="#FFFFFF",
               hover_color="#313A46"
            )

        else:  # num_selected > 1
            self.button_Add.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )
            self.button_Edit.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                 hover_color="#313A46"
            )
            self.button_Delete_selected.configure(
                state="normal",
                fg_color="#5A616B",
                text_color="#FFFFFF",
                 hover_color="#313A46"
            )


#----------------------------------------------------[Add Vechile]---------------------------------------------------------------------------------------------------

    def add_Vechile(self,num=None):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        popup_width = 550
        popup_height = 550
        self.current_open_dropdown = None  # Keep track of the currently open dropdown
        self.bool_dropdown_opened = False

        # Calculate position to center the popup on the screen
        x_position = (screen_width - popup_width) // 2  # Center horizontally
        y_position = (screen_height - popup_height) // 2  # Center vertically

        # Set the geometry for the popup
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()
        # Create a popup window
        self.popup =  Toplevel(self)


        self.popup.geometry(f"{popup_width}x{popup_height}+{x_position+200}+{y_position+80}")
        self.popup.title("Add New Vehicle")
        #self.popup.overrideredirect(True)
        self.popup.configure(bg="#FFFFFF")
        self.popup.attributes("-topmost", True)
        self.popup.resizable(False, False)

        self.popup.columnconfigure((0,1), weight = 1, uniform="a")

        data={'vechike_name':'',
              'heading':'Add Vechile',
              'state':'normal'
            }
        self.Add_Veihcle_form(data,num)

    def Add_Veihcle_form(self, data=[], num= None):
        self.i_form_width = 650  # Width of parent popup
        self.i_form_height = 560  # Height of parent popup
        self.bool_dropdown_opened = False
        self.list_company = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen", "Hyundai", "Nissan"]

        self.list_vehicle_type = ["Personal", "Truck", "Motorcycle", "Bus", "Van", "Auto", "Taxi",
                          "All", "Commercial", "Electric", "SUV"]
        self.list_blacklist=["BlackList","WhiteList"]
        self.current_open_button = None  # Track the active button

        self.label_heading = CTkLabel(
            self.popup,
            text="Add Vehicle",
            text_color = "#2C2C2C",
            height = 38,
            font = ("", 20, "bold"),
            corner_radius = 10,
            anchor="center",
            fg_color="transparent"
        )
        self.label_heading.grid(row=0, column=0, columnspan = 2, pady=(15,0), sticky="ew")

        self.frame_details = CTkFrame(
            self.popup,
            fg_color = "transparent",
            border_color="#D2D2D2",
            border_width = 2,
            corner_radius = 5,
        )
        self.frame_details.columnconfigure((0,1), weight = 1, uniform="a")
        self.frame_details.rowconfigure(0, weight = 1)
        self.frame_details.grid(row=1, column=0, columnspan=2, sticky="nsew", padx = 25, pady = (10,0))

        self.frame_form_lcol = CTkFrame(
           self.frame_details,
            fg_color = "transparent",
        )
        self.frame_form_lcol.columnconfigure(0, weight=1)
        self.frame_form_lcol.grid(row = 0, column = 0, sticky = "nsew", padx=(5,0), pady = 5)

        self.frame_form_rcol = CTkFrame(
            self.frame_details,
            fg_color = "transparent",
        )
        self.frame_form_rcol.columnconfigure(0, weight=1)
        self.frame_form_rcol.grid(row = 0, column = 1, sticky = "nsew", padx=(0,5), pady = 5)

        self.label_number = CTkLabel(
            self.frame_form_lcol,
            text="Vehicle Number",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_number.grid(row = 0, column = 0, sticky = "ew", padx=(10,5), pady=(5,1))

        self.entry_number = CTkEntry(
            self.frame_form_lcol,
            height=35,
            fg_color="#F6F6F6",
            placeholder_text="Enter Vehicle Number" if num is None else "",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )

        self.entry_number.grid(row=1, column=0, sticky="ew", padx=(10, 5))

        # If num is provided, insert it into the entry
        if num is not None:
            self.entry_number.insert(0, num)

        self.label_status = CTkLabel(
            self.frame_form_rcol,
            text="Vehicle Status",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_status.grid(row = 0, column = 0, sticky = "ew", padx=(5,10), pady=(5,1))

        self.frame_status_dropdown = CTkFrame(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_status_dropdown.columnconfigure(0, weight = 1)
        self.frame_status_dropdown.rowconfigure(0, weight = 1)
        self.frame_status_dropdown.grid(row=1, column=0, padx=(5,10), sticky="ew")

        self.entry_selected_status = CTkEntry(
            self.frame_status_dropdown,
            height = 35,
            fg_color = "#F6F6F6",
            textvariable = StringVar(value="Select Status"),
            # placeholder_text_color =  "#828282",
            text_color="#828282",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14),
            state="disabled"
        )
        self.entry_selected_status.grid(row = 0, column = 0, sticky = "nsew")

        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.button_select_status = CTkButton(
            self.frame_status_dropdown,
            image=img_down_arraow,
            height = 30,
            width = 30,
            text = "",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
            command=lambda: self.popup_Add_dropdown(self.frame_form_rcol,self.list_blacklist, entry_destination = self.entry_selected_status, i_row = 2, i_rowspan=2,type=1 )
        )
        self.button_select_status.grid(row = 0, column = 0, sticky = "e", padx=3, pady=1.5)

        self.label_company = CTkLabel(
            self.frame_form_lcol,
            text="Vehicle Company",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_company.grid(row = 2, column = 0, sticky = "ew", padx=(10,5), pady=(15,1))

        self.frame_company_dropdown = CTkFrame(
            self.frame_form_lcol,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_company_dropdown.columnconfigure(0, weight = 1)
        self.frame_company_dropdown.rowconfigure(0, weight = 1)
        self.frame_company_dropdown.grid(row=3, column=0, padx=(10,5), sticky="ew")

        self.entry_selected_company = CTkEntry(
            self.frame_company_dropdown,
            height = 35,
            fg_color = "#F6F6F6",
            # textvariable = StringVar(value="Select Company"),
            text_color="#414141",
            placeholder_text = "Select Company",
            placeholder_text_color =  "#828282",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14),
            # state="disabled"
        )
        self.entry_selected_company.grid(row = 0, column = 0, sticky = "nsew")

        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.button_select_company = CTkButton(
            self.frame_company_dropdown,
            image=img_down_arraow,
            height = 30,
            width = 30,
            text = "",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
            command=lambda: self.popup_Add_dropdown(self.frame_form_lcol,self.list_company, entry_destination = self.entry_selected_company, i_row = 4, i_rowspan=3 ,type=1)
        )
        self.button_select_company.grid(row = 0, column = 0, sticky = "e", padx=3, pady=1.5)

        self.label_type = CTkLabel(
            self.frame_form_rcol,
            text="Vehicle Type",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_type.grid(row = 2, column = 0, sticky="ew", padx=(5,10), pady=(15,1))

        self.frame_type = CTkFrame(
            self.frame_form_rcol,
            height=30,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_type.columnconfigure(0, weight = 1)
        self.frame_type.rowconfigure(0, weight = 1)
        self.frame_type.grid(row=3, column=0, padx=(5,10), sticky="ew")

        self.entry_type = CTkEntry(
            self.frame_type,
            height = 35,
            fg_color = "#F6F6F6",
            # textvariable = StringVar(value="Select Type "),
            text_color="#414141",
            placeholder_text = "Select Type",
            placeholder_text_color =  "#828282",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14),
            # state="disabled"
        )
        self.entry_type.grid(row = 0, column = 0, sticky = "nsew")

        img_down_arraow_new = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.button_type = CTkButton(
            self.frame_type,
            image=img_down_arraow_new,
            height = 30,
            width = 30,
            text = "",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
            command=lambda: self.popup_Add_dropdown(self.frame_form_rcol,self.list_vehicle_type, entry_destination = self.entry_type, i_row = 4, i_rowspan=3 ,type=1)

        )
        self.button_type.grid(row = 0, column = 0, sticky = "e", padx=4, pady=1.5)

        self.label_model = CTkLabel(
            self.frame_form_lcol,
            text="Vehicle Model",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_model.grid(row = 4, column = 0, sticky="ew", padx=(10,5), pady=(15,1))

        self.entry_model = CTkEntry(
            self.frame_form_lcol,
            height = 35,
            fg_color = "#F6F6F6",
            placeholder_text = "Vehicle Model",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_model.grid(row=5, column=0, sticky="ew", padx=(10, 5))

        self.label_color = CTkLabel(
            self.frame_form_rcol,
            text="Vehicle Color",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_color.grid(row = 4, column = 0, sticky="ew", padx=(5,10), pady=(15,1))

        self.entry_color = CTkEntry(
            self.frame_form_rcol,
            height = 35,
            fg_color = "#F6F6F6",
            placeholder_text = "Vehicle Color",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_color.grid(row=5, column=0, sticky="ew", padx=(5, 10))

        self.label_date = CTkLabel(
            self.frame_form_lcol,
            text="Manufacturing Year",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_date.grid(row = 6, column = 0, sticky="ew", padx=(10,5), pady=(15,1))

        self.entry_date = CTkEntry(
            self.frame_form_lcol,
            height = 35,
            fg_color = "#F6F6F6",
            placeholder_text = "Manufacturing Year",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_date.grid(row=7, column=0, sticky="ew", padx=(10, 5), pady=(0,10))

        self.label_owner = CTkLabel(
            self.frame_form_rcol,
            text="Vehicle Owner",
            text_color="#2C2C2C",
            font = ("", 14),
            anchor="w"
        )
        self.label_owner.grid(row = 6, column = 0, sticky="ew", padx=(10,5), pady=(15,1))


        self.entry_owner = CTkEntry(
            self.frame_form_rcol,
            height = 35,
            fg_color = "#F6F6F6",
            placeholder_text = "Enter Owner Name",
            placeholder_text_color =  "#828282",
            text_color="#414141",
            border_color = "#DEDEDE",
            border_width = 2,
            corner_radius = 5,
            font = ("", 14)
        )
        self.entry_owner.grid(row=7, column=0, sticky="ew", padx=(5, 10), pady=(0,10))


        self.label_error = CTkLabel(
                self.frame_details,
                text="",
                text_color="#FF0000",
                font=("", 12),
                anchor="center",
                height=15,
                wraplength=350
            )
        self.label_error.grid(column=0, row=1, columnspan=2, sticky="ew", pady=(5,20),padx=(20,20))

        self.button_add_save = CTkButton(
            self.popup,
            height = 38,
            width = 100,
            text = "Save",
            text_color = "#FFFFFF",
            fg_color = "#444C57",
            border_color="#3A36F5",
            font=("", 14),
            cursor="hand2",
            hover=False
        )
        self.button_add_save.grid(row=2, column=0, padx=4, pady=(25,25), sticky="e")

        self.button_cancel= CTkButton(
            self.popup,
            height = 38,
            width = 100,
            text = "Cancel",
            text_color = "#FFFFFF",
            fg_color = "#6C757D",
            border_color="#6C757D",
            font=("", 14),
            cursor="hand2",
            hover=False,

        )
        self.button_cancel.grid(row=2, column=1, padx=4, pady=(25,25), sticky="w")

        self.frame_form_lcol.bind('<Button-1>', self.handle_outside_click)
        self.frame_form_rcol.bind('<Button-1>', self.handle_outside_click)
        self.popup.bind('<Button-1>', self.handle_outside_click)


        if hasattr(self, 'on_form_add_ready'):
            self.on_form_add_ready()
        # self.bind_widgets(self)

    def handle_entry_click(self, event):
        """Handle clicks on entry fields"""
        # Ensure the dropdown stays open when clicking on the entry box
        if not self.active_dropdown_frame:
            self.popup_Add_dropdown(self.parent_frame, self.dropdown_data, event.widget, row=0, i_rowspan=3)



    def handle_outside_click(self, event):
        """Handle clicks outside the dropdown"""
        if not self.active_dropdown_frame:
            return

        # Get the clicked widget
        clicked_widget = event.widget

        # Check if click is within dropdown or dropdown buttons
        if not self.is_click_in_dropdown(event.x_root, event.y_root):
            self.close_active_dropdown()


    def is_click_in_dropdown(self, x, y):
        """Check if click coordinates are within the dropdown area"""
        if not self.active_dropdown_frame:
            return False

        try:
            # Get dropdown coordinates
            dropdown = self.active_dropdown_frame
            dx = dropdown.winfo_rootx()
            dy = dropdown.winfo_rooty()
            dw = dropdown.winfo_width()
            dh = dropdown.winfo_height()

            # Check if click is within dropdown bounds
            if dx <= x <= dx + dw and dy <= y <= dy + dh:
                return True

            # Check if click is on a dropdown button
            for btn in [ self.button_select_status,self.button_select_company, self.button_type]:
                bx = btn.winfo_rootx()
                by = btn.winfo_rooty()
                bw = btn.winfo_width()
                bh = btn.winfo_height()
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    print(bx,by,bw,bh)
                    return True

            return False
        except:
            return False


    def close_active_dropdown(self):
            """Helper method to close the currently active dropdown"""
            if self.active_dropdown_frame and self.active_dropdown_frame.winfo_exists():
                self.active_dropdown_frame.grid_forget()

            self.active_dropdown_frame = None
            self.current_open_dropdown = None

    def popup_Add_dropdown(self, parent_frame: CTkFrame, list_data: list = [], entry_destination: CTkEntry = None,
                           i_row: int = None, i_rowspan: int = 3, type: int = 0):
        """Modified function to handle button dropdown with toggle functionality"""

        # Handle type 1 as button dropdown toggle
        if type == 1:
            # Check if the dropdown is already open for the same entry
            if self.current_open_dropdown == entry_destination:
                # Close dropdown if already open
                self.close_active_dropdown()
                return
            else:
                # Open new dropdown for button click
                entry_destination.focus_set()  # Keep focus on the entry field

                # If a different dropdown is open, close it before opening a new one
                if self.active_dropdown_frame:
                    self.close_active_dropdown()

                # Create the dropdown frame for the new dropdown
                frame_Add_maindropdown_window = CTkFrame(
                    parent_frame,
                    fg_color="#DEDEDE",
                    height=40,
                    corner_radius=5
                )
                frame_Add_maindropdown_window.columnconfigure(0, weight=1)
                frame_Add_maindropdown_window.rowconfigure(0, weight=1)
                frame_Add_maindropdown_window.grid_propagate(False)

                # Create the scrollable frame to hold the dropdown options
                frame_Add_popup_table = CTkScrollableFrame(
                    frame_Add_maindropdown_window,
                    fg_color="#FFFFFF",
                    height=40,
                    corner_radius=5
                )
                frame_Add_popup_table.columnconfigure(0, weight=1)
                frame_Add_popup_table.grid(row=0, column=0, columnspan=2, padx=(1, 4), pady=(1, 3), sticky="nsew")
                text_entered = entry_destination.get().strip()
                # Check if the entry field is empty
                if text_entered and text_entered not in self.list_blacklist and text_entered != "Select Status":
                    filtered_data = [row_data for row_data in list_data if text_entered.lower() in row_data.lower()]
                else:
                    filtered_data = list_data

                # Add options to the dropdown
                for index, row_data in enumerate(filtered_data):
                    button_options = CTkButton(
                        frame_Add_popup_table,
                        text=f"    {row_data}",
                        height=20,
                        fg_color="transparent",
                        text_color="#414141",
                        font=("", 14),
                        corner_radius=0,
                        hover_color="#F6F6F6",
                        anchor="w",
                        command=lambda selected_option=row_data: self.select_option(selected_option, entry_destination,
                                                                                    frame_Add_maindropdown_window)
                    )
                    button_options.grid(row=index, column=0, sticky="nsew", padx=1)

                # Show the dropdown
                frame_Add_maindropdown_window.grid_propagate(False)
                frame_Add_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(5, 10),
                                                   pady=(5, 0))
                if entry_destination == self.entry_selected_company:
                    frame_Add_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew",
                                                       padx=(10, 5),
                                                       pady=(5, 0))
                frame_Add_maindropdown_window.tkraise()

                # Update state tracking variables to manage the currently open dropdown
                self.current_open_dropdown = entry_destination
                self.active_dropdown_frame = frame_Add_maindropdown_window

        else:
            entry_destination.focus_set()  # Keep focus on the entry field

            # If a different dropdown is open, close it before opening a new one
            if self.active_dropdown_frame:
                self.close_active_dropdown()

            # Create and setup the dropdown frame (same logic as before for non-button dropdown)
            frame_Add_maindropdown_window = CTkFrame(
                parent_frame,
                fg_color="#DEDEDE",
                height=40,
                corner_radius=5
            )
            frame_Add_maindropdown_window.columnconfigure(0, weight=1)
            frame_Add_maindropdown_window.rowconfigure(0, weight=1)
            frame_Add_maindropdown_window.grid_propagate(False)

            # Create the scrollable frame to hold the dropdown options
            frame_Add_popup_table = CTkScrollableFrame(
                frame_Add_maindropdown_window,
                fg_color="#FFFFFF",
                height=40,
                corner_radius=5
            )
            frame_Add_popup_table.columnconfigure(0, weight=1)
            frame_Add_popup_table.grid(row=0, column=0, columnspan=2, padx=(1, 4), pady=(1, 3), sticky="nsew")
            text_entered = entry_destination.get().strip()

            # Check if the entry field is empty
            if text_entered and text_entered not in self.list_blacklist and text_entered != "Select Status":
                filtered_data = [row_data for row_data in list_data if text_entered.lower() in row_data.lower()]
            else:
                filtered_data = list_data

            # Add options to the dropdown
            for index, row_data in enumerate(filtered_data):
                button_options = CTkButton(
                    frame_Add_popup_table,
                    text=f"    {row_data}",
                    height=20,
                    fg_color="transparent",
                    text_color="#414141",
                    font=("", 14),
                    corner_radius=0,
                    hover_color="#F6F6F6",
                    anchor="w",
                    command=lambda selected_option=row_data: self.select_option(selected_option, entry_destination,
                                                                                frame_Add_maindropdown_window)
                )
                button_options.grid(row=index, column=0, sticky="nsew", padx=1)

            frame_Add_maindropdown_window.grid_propagate(False)
            frame_Add_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(5, 10),
                                                pady=(5, 0))
            if entry_destination == self.entry_selected_company:
                frame_Add_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew",
                                                    padx=(10, 5),
                                                    pady=(5, 0))
            frame_Add_maindropdown_window.tkraise()

            # Update state tracking variables to manage the currently open dropdown
            self.current_open_dropdown = entry_destination
            self.active_dropdown_frame = frame_Add_maindropdown_window


    def select_option(self, selected_option: str, entry_destination: CTkEntry, dropdown_frame: CTkFrame):
        """Method to handle the selection of an option from the dropdown"""

        # Clear any placeholder text if an option is selected
        if(selected_option=="All"):
            self.label_error.configure(text="All can not be selcetd")
            entry_destination.configure(state="normal", text_color="#414141",border_color="red")
        else:
            self.label_error.configure(text="")
            entry_destination.configure(state="normal", text_color="#414141",border_color="green")
        entry_destination.delete(0, "end")  # Clear the current text

        # Insert the selected option into the entry field
        if selected_option:
            entry_destination.insert(0, selected_option)  # Insert the selected option

        # If the entry is entry_selected_status, disable it for further editing
        if entry_destination == self.entry_selected_status:
            entry_destination.configure(state="disabled")  # Disable the entry field to prevent editing

        # Close the dropdown after selection
        if dropdown_frame.winfo_exists():
            dropdown_frame.grid_forget()

        # Reset dropdown state tracking variables
        self.current_open_dropdown = None
        self.active_dropdown_frame = None


    def destroy_add_vehicle_form(self):
        """Helper method to destroy the add vehicle form."""
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()  # Destroy the popup (form) window

    def destroy_edit_vehicle_form(self):
        """Helper method to destroy the add vehicle form."""
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()  # Destroy the popup (form) window














    #___________________________________________________________________[edit vechile]_______________________________________________________________________________________

    def edit_selected_Vehicle(self):
        """Handle editing of selected camera and ensure proper state reset"""
        if len(self.selected_vehicle_set) == 1:
            vechile_number = next(iter(self.selected_vehicle_set))
            self.vehicle = next((cam for cam in self.vehicle_data if cam['vehicle_number'] == vechile_number), None)
            if self.vehicle:
                self.edit_vechile(self.vehicle)
                # self.edit_reset_vechile(vehicle)





    def edit_vechile(self, vehicle=[]):
        # Handle edit camera logic here
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set the desired width and height for the popup
        popup_width = 600
        popup_height = 550

        # Calculate position to center the popup on the screen
        x_position = (screen_width - popup_width) // 2  # Center horizontally
        y_position = (screen_height - popup_height) // 2  # Center vertically

        # Set the geometry for the popup
        data = {'heading': 'Edit Vechile',
                'state': 'disabled'
               }

        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()

        # Create a popup window
        self.popup = Toplevel(self)
        self.popup.geometry(f"{popup_width}x{popup_height}+{x_position+200}+{y_position+80}")
        self.popup.title("Edit Vechile")
        self.popup.configure(bg="#FFFFFF")
        self.popup.attributes("-topmost", True)
        self.popup.resizable(False, False)
        self.popup.columnconfigure((0,1), weight = 1, uniform="a")
        self.vehicle_form(data,vehicle)


    def vehicle_form(self, data=[],vehicle=[]):
            self.i_form_width = 650  # Width of parent popup
            self.i_form_height = 560  # Height of parent popup
            self.bool_dropdown_opened = False
            self.current_open_dropdown = None  # Keep track of the currently open dropdown
            self.list_company = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen", "Hyundai", "Nissan"]
            self.list_vehicle_type = ["Personal", "Truck", "Motorcycle", "Bus", "Van", "Auto", "Taxi",
                          "All", "Commercial", "Electric", "SUV"]
            self.list_blacklist=["BlackList","WhiteList"]

            self.label_heading = CTkLabel(
                self.popup,
                text="Edit Vehicle",
                text_color = "#2C2C2C",
                height = 38,
                font = ("", 20, "bold"),
                corner_radius = 10,
                anchor="center",
                fg_color="transparent"
            )
            self.label_heading.grid(row=0, column=0, columnspan = 2, pady=(15,0), sticky="ew")

            self.frame_details = CTkFrame(
                self.popup,
                fg_color = "transparent",
                border_color="#D2D2D2",
                border_width = 1,
                corner_radius = 5,
            )
            self.frame_details.columnconfigure((0,1), weight = 1, uniform="a")
            self.frame_details.rowconfigure(0, weight = 1)
            self.frame_details.grid(row=1, column=0, columnspan=2, sticky="nsew", padx = 25, pady = (10,0))

            self.frame_form_lcol = CTkFrame(
            self.frame_details,
                fg_color = "transparent",
            )
            self.frame_form_lcol.columnconfigure(0, weight=1)
            self.frame_form_lcol.grid(row = 0, column = 0, sticky = "nsew", padx=(5,0), pady = 5)

            self.frame_form_rcol = CTkFrame(
                self.frame_details,
                fg_color = "transparent",
            )
            self.frame_form_rcol.columnconfigure(0, weight=1)
            self.frame_form_rcol.grid(row = 0, column = 1, sticky = "nsew", padx=(0,5), pady = 5)

            self.label_number = CTkLabel(
                self.frame_form_lcol,
                text="Vehicle Number",
                text_color="#2C2C2C",
                font = ("", 14),
                anchor="w"
            )
            self.label_number.grid(row = 0, column = 0, sticky = "ew", padx=(10,5), pady=(5,1))

            self.entry_edit_number = CTkEntry(
                self.frame_form_lcol,
                height = 35,
                fg_color = "#F6F6F6",
                textvariable = StringVar(value=vehicle["vehicle_number"]),
                text_color="#414141",
                border_color = "#DEDEDE",
                border_width = 2,
                corner_radius = 5,
                state="readonly",
                font = ("", 14)
            )
            self.entry_edit_number.grid(row=1, column=0, sticky="ew", padx=(10, 5))

            self.label_status = CTkLabel(
                self.frame_form_rcol,
                text="Vehicle Status",
                text_color="#2C2C2C",
                font = ("", 14),
                anchor="w"
            )
            self.label_status.grid(row = 0, column = 0, sticky = "ew", padx=(5,10), pady=(5,1))

            self.frame_status_dropdown = CTkFrame(
                self.frame_form_rcol,
                height=35,
                fg_color="#F6F6F6",
                corner_radius=5,
            )
            self.frame_status_dropdown.columnconfigure(0, weight = 1)
            self.frame_status_dropdown.rowconfigure(0, weight = 1)
            self.frame_status_dropdown.grid(row=1, column=0, padx=(5,10), sticky="ew")

            self.entry_edit_selected_status = CTkEntry(
                self.frame_status_dropdown,
                height = 35,
                fg_color = "#F6F6F6",
                textvariable = StringVar(value="WhiteList" if vehicle["vehicle_status"] == 0 else "BlackList"),
                text_color="#414141",
                border_color = "#DEDEDE",
                border_width = 2,
                corner_radius = 5,
                font = ("", 14),
                state="disabled"
            )
            self.entry_edit_selected_status.grid(row = 0, column = 0, sticky = "nsew")


            img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
            self.button_edit_select_status = CTkButton(
                self.frame_status_dropdown,
                image=img_down_arraow,
                height = 30,
                width = 30,
                text = "",
                fg_color="transparent",
                cursor="hand2",
                border_width=0,
                hover=False,
                command=lambda: self.popup_Edit_dropdown(self.frame_form_rcol,self.list_blacklist, entry_destination = self.entry_edit_selected_status, i_row = 2, i_rowspan=2,type=1)
            )
            self.button_edit_select_status.grid(row = 0, column = 0, sticky = "e", padx=3, pady=1.5)

            self.label_company = CTkLabel(
                self.frame_form_lcol,
                text="Vehicle Company",
                text_color="#2C2C2C",
                font = ("", 14),
                anchor="w"
            )
            self.label_company.grid(row = 2, column = 0, sticky = "ew", padx=(10,5), pady=(15,1))

            self.frame_company_dropdown = CTkFrame(
                self.frame_form_lcol,
                height=35,
                fg_color="#F6F6F6",
                corner_radius=5,
            )
            self.frame_company_dropdown.columnconfigure(0, weight = 1)
            self.frame_company_dropdown.rowconfigure(0, weight = 1)
            self.frame_company_dropdown.grid(row=3, column=0, padx=(10,5), sticky="ew")

            self.entry_edit_selected_company = CTkEntry(
                self.frame_company_dropdown,
                height = 35,
                fg_color = "#F6F6F6",
                textvariable = StringVar(value=vehicle["vehicle_company"]),
                text_color="#414141",
                border_color = "#DEDEDE",
                border_width = 2,
                corner_radius = 5,
                font = ("", 14)
            )
            self.entry_edit_selected_company.grid(row = 0, column = 0, sticky = "nsew")

            img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
            self.button_edit_select_company = CTkButton(
                self.frame_company_dropdown,
                image=img_down_arraow,
                height = 30,
                width = 30,
                text = "",
                fg_color="transparent",
                cursor="hand2",
                border_width=0,
                hover=False,
                command=lambda: self.popup_Edit_dropdown(self.frame_form_lcol,self.list_company, entry_destination = self.entry_edit_selected_company, i_row = 4, i_rowspan=3,type=1)
            )
            self.button_edit_select_company.grid(row = 0, column = 0, sticky = "e", padx=3, pady=1.5)

            self.label_type = CTkLabel(
                self.frame_form_rcol,
                text="Vehicle Type",
                text_color="#2C2C2C",
                font = ("", 14),
                anchor="w"
            )
            self.label_type.grid(row = 2, column = 0, sticky="ew", padx=(5,10), pady=(15,1))

            self.frame_type = CTkFrame(
                self.frame_form_rcol,
                height=30,
                fg_color="#F6F6F6",
                corner_radius=5,
            )
            self.frame_type.columnconfigure(0, weight = 1)
            self.frame_type.rowconfigure(0, weight = 1)
            self.frame_type.grid(row=3, column=0, padx=(5,10), sticky="ew")

            self.entry_edit_type = CTkEntry(
                self.frame_type,
                height = 35,
                fg_color = "#F6F6F6",
                textvariable = StringVar(value=vehicle["vehicle_type"]),
                text_color="#414141",
                border_color = "#DEDEDE",
                border_width = 2,
                corner_radius = 5,
                font = ("", 14)
            )
            self.entry_edit_type.grid(row = 0, column = 0, sticky = "nsew")

            img_down_arraow_new = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
            self.button_edit_type = CTkButton(
                self.frame_type,
                image=img_down_arraow_new,
                height = 30,
                width = 30,
                text = "",
                fg_color="transparent",
                cursor="hand2",
                border_width=0,
                hover=False,
                command=lambda: self.popup_Edit_dropdown(self.frame_form_rcol,self.list_vehicle_type, entry_destination = self.entry_edit_type, i_row = 4, i_rowspan=3,type=1 )
            )
            self.button_edit_type.grid(row = 0, column = 0, sticky = "e", padx=4, pady=1.5)

            self.label_model = CTkLabel(
                self.frame_form_lcol,
                text="Vehicle Model",
                text_color="#2C2C2C",
                font = ("", 14),
                anchor="w"
            )
            self.label_model.grid(row = 4, column = 0, sticky="ew", padx=(10,5), pady=(15,1))

            self.entry_edit_model = CTkEntry(
                self.frame_form_lcol,
                height = 35,
                fg_color = "#F6F6F6",
                textvariable = StringVar(value=vehicle["vehicle_model"]),
                text_color="#414141",
                border_color = "#DEDEDE",
                border_width = 2,
                corner_radius = 5,
                font = ("", 14)
            )
            self.entry_edit_model.grid(row=5, column=0, sticky="ew", padx=(10, 5))

            self.label_color = CTkLabel(
                self.frame_form_rcol,
                text="Vehicle Color",
                text_color="#2C2C2C",
                font = ("", 14),
                anchor="w"
            )
            self.label_color.grid(row = 4, column = 0, sticky="ew", padx=(5,10), pady=(15,1))

            self.entry_edit_color = CTkEntry(
                self.frame_form_rcol,
                height = 35,
                fg_color = "#F6F6F6",
                textvariable = StringVar(value=vehicle["vehicle_color"]),
                text_color="#414141",
                border_color = "#DEDEDE",
                border_width = 2,
                corner_radius = 5,
                font = ("", 14)
            )
            self.entry_edit_color.grid(row=5, column=0, sticky="ew", padx=(5, 10))

            self.label_date = CTkLabel(
                self.frame_form_lcol,
                text="Manufacturing Year",
                text_color="#2C2C2C",
                font = ("", 14),
                anchor="w"
            )
            self.label_date.grid(row = 6, column = 0, sticky="ew", padx=(10,5), pady=(15,1))

            self.entry_edit_date = CTkEntry(
                self.frame_form_lcol,
                height = 35,
                fg_color = "#F6F6F6",
                textvariable = StringVar(value=vehicle["manufacturing_year"]),
                text_color="#414141",
                border_color = "#DEDEDE",
                border_width = 2,
                corner_radius = 5,
                font = ("", 14)
            )
            self.entry_edit_date.grid(row=7, column=0, sticky="ew", padx=(10, 5), pady=(0,10))

            self.label_owner = CTkLabel(
                self.frame_form_rcol,
                text="Vehicle Owner",
                text_color="#2C2C2C",
                font = ("", 14),
                anchor="w"
            )
            self.label_owner.grid(row = 6, column = 0, sticky="ew", padx=(10,5), pady=(15,1))

            self.entry_edit_owner = CTkEntry(
                self.frame_form_rcol,
                height = 35,
                fg_color = "#F6F6F6",
                textvariable = StringVar(value=vehicle["vehicle_owner"]),
                text_color="#414141",
                border_color = "#DEDEDE",
                border_width = 2,
                corner_radius = 5,
                font = ("", 14)
            )
            self.entry_edit_owner.grid(row=7, column=0, sticky="ew", padx=(5, 10), pady=(0,10))

            self.label_error = CTkLabel(
                self.frame_details,
                text="",
                text_color="#FF0000",
                font=("", 12),
                anchor="center",
                height=15,
                wraplength=350
            )
            self.label_error.grid(column=0, row=1, columnspan=2, sticky="ew", pady=(5,20),padx=(20,20))

            self.button_edit_save = CTkButton(
                self.popup,
                height = 38,
                width = 100,
                text = "Save",
                text_color = "#FFFFFF",
                fg_color = "#444C57",
                border_color="#3A36F5",
                font=("", 14),
                cursor="hand2",
                hover=False
            )
            self.button_edit_save.grid(row=2, column=0, padx=4, pady=(25,25), sticky="e")

            self.button_edit_cancel = CTkButton(
                self.popup,
                height = 38,
                width = 100,
                text = "Reset",
                text_color = "#FFFFFF",
                fg_color = "#6C757D",
                border_color="#6C757D",
                font=("", 14),
                cursor="hand2",
                hover=False,
                command=lambda: self.edit_reset_vechile(vehicle)
            )
            self.button_edit_cancel.grid(row=2, column=1, padx=4, pady=(25,25), sticky="w")

            if hasattr(self, 'on_form_edit_ready'):
             self.on_form_edit_ready()

             self.frame_form_lcol.bind('<Button-1>', self.handle_outside_Exit_click)
             self.frame_form_rcol.bind('<Button-1>', self.handle_outside_Exit_click)
             self.popup.bind('<Button-1>', self.handle_outside_Exit_click)



    def edit_reset_vechile(self,vehicle=[]):
                 # Use initial_values if vehicle is not provided
        if not vehicle and hasattr(self, 'initial_values'):
            vehicle = self.initial_values

        # Ensure that vehicle is valid
        if not vehicle:
            return

        self.entry_edit_number.configure(state="normal")
        self.entry_edit_number.delete(0, "end")
        self.entry_edit_number.insert(0, vehicle.get("vehicle_number", ""))
        self.entry_edit_number.configure(state="disabled")
        self.entry_edit_number.configure(border_color="#DEDEDE")  # Reset border color to default
        self.label_error.configure(text="")

        # Reset the status field
        self.entry_edit_selected_status.configure(state="normal")
        self.entry_edit_selected_status.delete(0, "end")
        self.entry_edit_selected_status.insert(0, "white-list" if vehicle.get("vehicle_status") == 0 else "black-list")
        self.entry_edit_selected_status.configure(state="disabled")
        self.entry_edit_selected_status.configure(border_color="#DEDEDE")  # Reset border color to default
        self.label_error.configure(text="")

        # Reset the company field
        self.entry_edit_selected_company.configure(state="normal")
        self.entry_edit_selected_company.delete(0, "end")
        self.entry_edit_selected_company.insert(0, vehicle.get("vehicle_company", ""))
        self.entry_edit_selected_company.configure(border_color="#DEDEDE")  # Reset border color to default
        self.label_error.configure(text="")

        # Reset the type field
        self.entry_edit_type.configure(state="normal")
        self.entry_edit_type.delete(0, "end")
        self.entry_edit_type.insert(0, vehicle.get("vehicle_type", ""))
        self.entry_edit_type.configure(border_color="#DEDEDE")  # Reset border color to default
        self.label_error.configure(text="")

        # Reset the model field
        self.entry_edit_model.configure(state="normal")
        self.entry_edit_model.delete(0, "end")
        self.entry_edit_model.insert(0, vehicle.get("vehicle_model", ""))
        self.entry_edit_model.configure(border_color="#DEDEDE")  # Reset border color to default
        self.label_error.configure(text="")

        # Reset the color field
        self.entry_edit_color.configure(state="normal")
        self.entry_edit_color.delete(0, "end")
        self.entry_edit_color.insert(0, vehicle.get("vehicle_color", ""))
        self.entry_edit_color.configure(border_color="#DEDEDE")  # Reset border color to default
        self.label_error.configure(text="")

        # Reset the manufacturing year field
        self.entry_edit_date.configure(state="normal")
        self.entry_edit_date.delete(0, "end")
        self.entry_edit_date.insert(0, vehicle.get("manufacturing_year", ""))
        self.entry_edit_date.configure(border_color="#DEDEDE")  # Reset border color to default
        self.label_error.configure(text="")

        # Reset the owner field
        self.entry_edit_owner.configure(state="normal")
        self.entry_edit_owner.delete(0, "end")
        self.entry_edit_owner.insert(0, vehicle.get("vehicle_owner", ""))
        self.entry_edit_owner.configure(border_color="#DEDEDE")  # Reset border color to default
        self.label_error.configure(text="")




    def handle_entry_Exit_click(self, event):
        """Handle clicks on entry fields"""
        if self.active_dropdown_frame:
            self.close_active_dropdown()

    def handle_outside_Exit_click(self, event):
        """Handle clicks outside the dropdown"""
        if not self.active_dropdown_frame:
            return

        # Get the clicked widget
        clicked_widget = event.widget

        # Check if click is within dropdown or dropdown buttons
        if not self.is_click_in_Exit_dropdown(event.x_root, event.y_root):
            self.close_active_dropdown()


    def is_click_in_Exit_dropdown(self, x, y):
        """Check if click coordinates are within the dropdown area"""
        if not self.active_dropdown_frame:
            return False

        try:
            # Get dropdown coordinates
            dropdown = self.active_dropdown_frame
            dx = dropdown.winfo_rootx()
            dy = dropdown.winfo_rooty()
            dw = dropdown.winfo_width()
            dh = dropdown.winfo_height()

            # Check if click is within dropdown bounds
            if dx <= x <= dx + dw and dy <= y <= dy + dh:
                return True

            # Check if click is on a dropdown button
            for btn in [ self.button_edit_select_status,self.entry_edit_selected_company, self.entry_edit_type]:
                bx = btn.winfo_rootx()
                by = btn.winfo_rooty()
                bw = btn.winfo_width()
                bh = btn.winfo_height()
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    return True

            return False
        except:
            return False
    def close_active_dropdown(self):
            """Helper method to close the currently active dropdown"""
            if self.active_dropdown_frame and self.active_dropdown_frame.winfo_exists():
                self.active_dropdown_frame.grid_forget()

            self.active_dropdown_frame = None
            self.current_open_dropdown = None

    def popup_Edit_dropdown(self, parent_frame: CTkFrame, list_data: list = [], entry_destination: CTkEntry = None, i_row: int = None, i_rowspan: int = 3, type: int = 0):
        """Modified function to handle button dropdown with toggle functionality"""
        if type == 1:
            # Check if the dropdown is already open for the same entry
            if self.current_open_dropdown == entry_destination:
                # Close dropdown if already open
                self.close_active_dropdown()
                return
            else:
                # Open new dropdown for button click
                entry_destination.focus_set()  # Keep focus on the entry field

                # If a different dropdown is open, close it before opening a new one
                if self.active_dropdown_frame:
                    self.close_active_dropdown()

                # Create the dropdown frame for the new dropdown
                frame_Edit_maindropdown_window = CTkFrame(
                    parent_frame,
                    fg_color="#DEDEDE",
                    height=40,
                    corner_radius=5
                )
                frame_Edit_maindropdown_window.columnconfigure(0, weight=1)
                frame_Edit_maindropdown_window.rowconfigure(0, weight=1)
                frame_Edit_maindropdown_window.grid_propagate(False)

                # Create the scrollable frame to hold the dropdown options
                frame_Edit_popup_table = CTkScrollableFrame(
                    frame_Edit_maindropdown_window,
                    fg_color="#FFFFFF",
                    height=40,
                    corner_radius=5
                )
                frame_Edit_popup_table.columnconfigure(0, weight=1)
                frame_Edit_popup_table.grid(row=0, column=0, columnspan=2, padx=(1, 4), pady=(1, 3), sticky="nsew")
                text_entered = entry_destination.get().strip()
                # Check if the entry field is empty
                if text_entered  and text_entered not in self.list_blacklist:
                    # Filter the list_data based on the entered text
                    filtered_data = [row_data for row_data in list_data if text_entered.lower() in row_data.lower()]
                else:
                 filtered_data=list_data

                # Add options to the dropdown
                for index, row_data in enumerate(filtered_data):
                    button_options = CTkButton(
                        frame_Edit_popup_table,
                        text=f"    {row_data}",
                        height=20,
                        fg_color="transparent",
                        text_color="#414141",
                        font=("", 14),
                        corner_radius=0,
                        hover_color="#F6F6F6",
                        anchor="w",
                        command=lambda selected_option=row_data: self.select_option_Edit(selected_option, entry_destination, frame_Edit_maindropdown_window)
                    )
                    button_options.grid(row=index, column=0, sticky="nsew", padx=1)

                # Show the dropdown
                frame_Edit_maindropdown_window.grid_propagate(False)
                frame_Edit_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(5, 10), pady=(5, 0))
                if entry_destination == self.entry_edit_selected_company:
                    frame_Edit_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew",
                                                        padx=(10, 5),
                                                        pady=(5, 0))
                frame_Edit_maindropdown_window.tkraise()

                # Update state tracking variables to manage the currently open dropdown
                self.current_open_dropdown = entry_destination
                self.active_dropdown_frame = frame_Edit_maindropdown_window

        else:
            entry_destination.focus_set()  # Keep focus on the entry field

            # If a different dropdown is open, close it before opening a new one
            if self.active_dropdown_frame:
                self.close_active_dropdown()

            # Create and setup the dropdown frame (same logic as before for non-button dropdown)
            frame_Edit_maindropdown_window = CTkFrame(
                parent_frame,
                fg_color="#DEDEDE",
                height=40,
                corner_radius=5
            )
            frame_Edit_maindropdown_window.columnconfigure(0, weight=1)
            frame_Edit_maindropdown_window.rowconfigure(0, weight=1)
            frame_Edit_maindropdown_window.grid_propagate(False)

            # Create the scrollable frame to hold the dropdown options
            frame_Edit_popup_table = CTkScrollableFrame(
                frame_Edit_maindropdown_window,
                fg_color="#FFFFFF",
                height=40,
                corner_radius=5
            )
            frame_Edit_popup_table.columnconfigure(0, weight=1)
            frame_Edit_popup_table.grid(row=0, column=0, columnspan=2, padx=(1, 4), pady=(1, 3), sticky="nsew")
            text_entered = entry_destination.get().strip()

            # Check if the entry field is empty
            if text_entered  and text_entered not in self.list_blacklist:
                # Filter the list_data based on the entered text
                filtered_data = [row_data for row_data in list_data if text_entered.lower() in row_data.lower()]
            else:
               filtered_data=list_data


            # Add options to the dropdown
            for index, row_data in enumerate(filtered_data):
                button_options = CTkButton(
                    frame_Edit_popup_table,
                    text=f"    {row_data}",
                    height=20,
                    fg_color="transparent",
                    text_color="#414141",
                    font=("", 14),
                    corner_radius=0,
                    hover_color="#F6F6F6",
                    anchor="w",
                    command=lambda selected_option=row_data: self.select_option_Edit(selected_option, entry_destination, frame_Edit_maindropdown_window)
                )
                button_options.grid(row=index, column=0, sticky="nsew", padx=1)

            frame_Edit_maindropdown_window.grid_propagate(False)
            frame_Edit_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(5, 10), pady=(5, 0))
            if entry_destination== self.entry_edit_selected_company:
                frame_Edit_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(10, 5),
                                                    pady=(5, 0))
            frame_Edit_maindropdown_window.tkraise()

            # Update state tracking variables to manage the currently open dropdown
            self.current_open_dropdown = entry_destination
            self.active_dropdown_frame = frame_Edit_maindropdown_window



    def select_option_Edit(self, selected_option: str, entry_destination: CTkEntry, dropdown_frame: CTkFrame):
        """Method to handle the selection of an option from the dropdown"""
        if(selected_option=="All"):
            self.label_error.configure(text="Dropdown entries cant selecte All")
            entry_destination.configure(state="normal", text_color="#414141",border_color="red")
        else:
            self.label_error.configure(text="")
            entry_destination.configure(state="normal", text_color="#414141",border_color="green")
        entry_destination.delete(0, "end")  # Clear the current text

        # Insert the selected option into the entry field
        if selected_option:
            entry_destination.insert(0, selected_option)  # Insert the selected option

        # If the entry is entry_selected_status, disable it for further editing
        if entry_destination == self.entry_edit_selected_status:
            entry_destination.configure(state="disabled")  # Disable the entry field to prevent editing

        # Close the dropdown after selection
        if dropdown_frame.winfo_exists():
            dropdown_frame.grid_forget()

        # Reset dropdown state tracking variables
        self.current_open_dropdown = None
        self.active_dropdown_frame = None








