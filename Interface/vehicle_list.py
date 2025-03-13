import base64
from io import BytesIO
import os
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCanvas, CTkScrollableFrame, CTkImage, CTkCheckBox
from tkinter import StringVar, Toplevel, filedialog
from PIL import Image


class VehicleListInteface(CTkFrame):

    def __init__(self, *args, root_width: int = 1920, root_height: int = 1080, **kwargs):

        super().__init__(*args, **kwargs)

        self.vehicle_data = []
        self.bool_filter_popup = False
        self.bool_owner_dropdown_opened = False
        self.bool_type_dropdown_opened = False
        self.bool_color_dropdown_opened = False
        self.active_dropdown_frame = False

        self.configure(fg_color="#F1F5FA", corner_radius=0)

        self.dict_columns_buttons = {}

        self.selected_face_set = set()

        self.i_start_index = 0
        self.i_end_index = 0
        self.i_total_data = 0
        self.dict_filter_criteria = {
            "gender": "%",
            "status": "%",
            "full_name": ""
        }

        i_form_width = int((int(root_width * 0.89)) * 0.885)
        i_form_height = int((int(root_height * 0.88)) * 0.9)

        self.frame_form = CTkFrame(
            self,
            width=i_form_width,
            height=i_form_height,
            fg_color="#FFFFFF",
            corner_radius=10
        )
        self.frame_form.columnconfigure(0, weight=1, uniform="a")
        self.frame_form.rowconfigure(3, weight=1)
        self.frame_form.grid_propagate(False)
        self.frame_form.pack(side="top", expand=False, padx=10, pady=30)

        self.frame_header = CTkFrame(
            self.frame_form,
            height=int(i_form_height * 0.12),
            fg_color="transparent",
            corner_radius=10
        )
        self.frame_header.columnconfigure(0, weight=1)
        self.frame_header.columnconfigure(1, weight=2)
        self.frame_header.columnconfigure(2, weight=2)
        self.frame_header.grid(column=0, row=0, sticky="we", padx=5, pady=(5, 5))

        self.label_heading = CTkLabel(
            self.frame_header,
            text="Registered Person",
            text_color="#2C2C2C",
            height=38,
            font=("", 18, "bold"),
            corner_radius=10,
            anchor="w",
            fg_color="transparent"
        )
        self.label_heading.grid(row=0, column=0, padx=10, pady=(15, 0), sticky="ew")

        self.frame_header_rcol = CTkFrame(
            self.frame_header,
            height=int(i_form_height * 0.07),
            fg_color="transparent",
            corner_radius=10
        )
        self.frame_header_rcol.rowconfigure(0, weight=1)
        self.frame_header_rcol.grid(row=0, column=1, columnspan=2, sticky="nsew")

        self.button_filter = CTkButton(
            self.frame_header_rcol,
            height=38,
            width=100,
            text="Filter",
            text_color="white",
            fg_color="#5A616B",
            border_width=2,
            border_color="#313A46",
            font=("", 14),
            cursor="hand2",
            anchor="center",
            hover=True,
            # command=self.reset_filter_form

        )
        self.button_filter.pack(side="right", padx=(4, 15), pady=(15, 0))

        self.button_Delete_selected = CTkButton(
            self.frame_header_rcol,
            height=38,
            width=100,
            text="Delete",
            text_color="white",
            fg_color="#e6e6ff",
            border_width=2,
            border_color="#313A46",
            font=("", 14),
            cursor="hand2",
            anchor="center",
            hover=True,
            state="disabled"
        )
        self.button_Delete_selected.pack(side="right", padx=4, pady=(15, 0))

        self.button_Edit = CTkButton(
            self.frame_header_rcol,
            height=38,
            width=100,
            text="Edit",
            text_color="white",
            fg_color="#e6e6ff",
            border_width=2,
            border_color="#313A46",
            font=("", 14),
            cursor="hand2",
            anchor="center",
            hover=True,
            # state="disabled"
        )
        self.button_Edit.pack(side="right", padx=4, pady=(15, 0))

        self.button_Add = CTkButton(
            self.frame_header_rcol,
            height=38,
            width=100,
            text="Add",
            text_color="white",
            fg_color="#5A616B",
            border_width=2,
            border_color="#313A46",
            font=("", 14),
            cursor="hand2",
            anchor="center",
            hover=True,
            state="normal"
        )
        self.button_Add.pack(side="right", padx=4, pady=(15, 0))

        self.table_search_frame = CTkFrame(
            self.frame_header_rcol,
            height=38,
            fg_color="transparent",
            border_width=2,
            border_color="#313A46",
            corner_radius=7,
        )
        self.table_search_frame.pack_propagate(False)
        self.table_search_frame.pack(side="right", padx=(0, 4), pady=(15, 0))

        img_search_icon = CTkImage(Image.open(".\\Resources\\images\\search_icon.png"), size=(15, 15))
        self.label_search_icon = CTkLabel(
            self.table_search_frame,
            image=img_search_icon,
            text="",
            width=20,
            height=30,
            fg_color="transparent"
        )
        self.label_search_icon.pack(side="left", padx=(10, 0))

        self.entry_search = CTkEntry(
            self.table_search_frame,
            height=30,
            placeholder_text="Enter Name..",
            placeholder_text_color="#A2B1C7",
            text_color="#414141",
            border_width=0,
            font=("", 13),
            fg_color="transparent",
            corner_radius=10,
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=(0, 1))

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
            height=44,
            fg_color="#444C57"
        )
        self.frame_table_heading.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="a")
        self.frame_table_heading.grid_propagate(False)
        self.frame_table_heading.grid(row=2, column=0, padx=(15, 19), pady=(20, 0), sticky="nsew")
        # icon = CTkImage(light_image=icon_img, dark_image=icon_img, size=(20, 20))
        sort_icon = CTkImage(Image.open("C:\\Users\\ITLP 93\\Downloads\\up.png.jpg"), size=(15, 15))
        self.current_sort = {"column": None, "order": None}
        self.column_buttons = {}
        sort_default_icon = CTkImage(Image.open("C:\\Users\\ITLP 93\\Downloads\\up.png.jpg"), size=(15, 15))
        sort_asc_icon = CTkImage(Image.open("C:\\Users\\ITLP 93\\Downloads\\up.png.jpg"), size=(15, 15))
        sort_desc_icon = CTkImage(Image.open("C:\\Users\\ITLP 93\\Downloads\\up.png.jpg"), size=(15, 15))

        def sort_column(self, column_name):
            if self.current_sort["column"] == column_name:
                print(" def sort_column(self,column_name):")
                # Cycle through sort orders for the same column
                if self.current_sort["order"] == "asc":
                    # Change to descending
                    self.current_sort["order"] = "desc"
                    self.column_buttons[column_name].configure(image=sort_desc_icon)
                else:
                    # Reset sorting
                    self.current_sort["column"] = None
                    self.current_sort["order"] = None
                    self.column_buttons[column_name].configure(image=sort_default_icon)
            else:
                # Reset previous column's icon if there was a sort
                if self.current_sort["column"]:
                    self.column_buttons[self.current_sort["column"]].configure(image=sort_default_icon)

                # Set new sort column to ascending
                # self.current_sort["column"] = column_name
                # self.current_sort["order"] = "asc"
                # self.column_buttons[column_name].configure(image=sort_asc_icon)

        self.table_headers = ["Name", "Age", "Gender", "Status", "Registered Face"]
        for col, value in enumerate(self.table_headers):
            button = CTkButton(
                self.frame_table_heading,
                text=value,
                height=45,
                image=sort_default_icon,
                compound="right",
                fg_color="#444C57",
                text_color="#FFFFFF",
                anchor="w",
                font=("", 15, "bold"),
                hover=True,
                hover_color="#313A46",
                corner_radius=0,
                cursor="hand2",
            )
            button.grid(row=0, column=col, sticky="nsew", padx=5)
            self.dict_columns_buttons[value] = [button, False]
            # sort_column(value)

            # sort_default_icon = CTkImage(Image.open(".\\Resources\\images\\normal.png"), size=(15, 15))
            # sort_asc_icon = CTkImage(Image.open(".\\Resources\\images\\asc.png"), size=(15, 15))
            # sort_desc_icon = CTkImage(Image.open(".\\Resources\\images\\desc.png"), size=(15, 15))

            # # Track current sorting state for each column
            # self.current_sort = {"column": None, "order": None}
            # self.column_buttons = {}

            # # # Function to handle sorting when a header is clicked
            # def sort_column(self,column_name):
            #     if self.current_sort["column"] == column_name:
            #         print("hello")
            #         # Cycle through sort orders for the same column
            #         if self.current_sort["order"] == "asc":
            #             # Change to descending
            #             self.current_sort["order"] = "desc"
            #             self.column_buttons[column_name].configure(image=sort_desc_icon)
            #         else:
            #             # Reset sorting
            #             self.current_sort["column"] = None
            #             self.current_sort["order"] = None
            #             self.column_buttons[column_name].configure(image=sort_default_icon)
            #     else:
            #         # Reset previous column's icon if there was a sort
            #         if self.current_sort["column"]:
            #             self.column_buttons[self.current_sort["column"]].configure(image=sort_default_icon)

            #         # Set new sort column to ascending
            #         self.current_sort["column"] = column_name
            #         self.current_sort["order"] = "asc"
            #         self.column_buttons[column_name].configure(image=sort_asc_icon)

            # Add your sorting logic here
            # sort_table_data(column_name, self.current_sort["order"])

            # Create header buttons with sorting functionality
            # self.table_headers = ["Vehicle Number", "Vehicle Type", "Vehicle Color", "Owner Name", "Manufacturing Year"]
            # for col, value in enumerate(self.table_headers):
            #     button = CTkButton(
            #         self.frame_table_heading,
            #         text=value,
            #         height=45,
            #         image=sort_default_icon,
            #         compound="right",
            #         fg_color="#444C57",
            #         text_color="#FFFFFF",
            #         anchor="w",
            #         font=("", 15, "bold"),
            #         hover=True,
            #         hover_color="#313A46",
            #         corner_radius=0,
            #         cursor="hand2",
            #         # command=lambda col_name=value: sort_column(col_name)  # Use lambda to pass column name
            #     )
            #     button.grid(row=0, column=col, sticky="nsew", padx=5)
            # self.column_buttons[value] = button

            self.frame_table_rows = CTkScrollableFrame(
                self.frame_form,
                fg_color="transparent",
                corner_radius=0
            )
        self.frame_table_rows.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="a")
        self.frame_table_rows.grid(row=3, column=0, padx=(15, 2), pady=(0, 20), sticky="nsew")

        self.label_data_count = CTkLabel(
            self.frame_form,
            text="No Records Found!",
            text_color="#FF0000",
            font=("", 14),
        )
        self.label_data_count.grid(row=4, column=0, padx=15, pady=(0, 10), sticky="w")

        self.button_next = CTkButton(
            self.frame_form,
            height=38,
            width=100,
            text="Next",
            text_color="white",
            fg_color="#444C57",
            border_color="#444C57",
            font=("", 14),
            cursor="hand2",
            anchor="center",
            hover=False,
        )
        self.button_next.grid(row=4, column=0, padx=15, pady=(0, 10), sticky="e")

        self.button_previous = CTkButton(
            self.frame_form,
            height=38,
            width=100,
            text="Previous",
            text_color="white",
            fg_color="#444C57",
            border_color="#444C57",
            font=("", 14),
            cursor="hand2",
            anchor="center",
            hover=False,
        )
        self.button_previous.grid(row=4, column=0, padx=(15, 120), pady=(0, 10), sticky="e")

        self.frame_filter = CTkFrame(
            self.frame_form,
            width=350,
            height=320,
            fg_color="#DEDEDE",
            corner_radius=5
        )
        self.frame_filter.columnconfigure(0, weight=1)
        self.frame_filter.rowconfigure(0, weight=1)
        self.frame_filter.grid_propagate(False)

        self.frame_filter_form = CTkFrame(
            self.frame_filter,
            fg_color="#FFFFFF",
            corner_radius=4
        )
        self.frame_filter_form.columnconfigure((0, 1), weight=1)
        self.frame_filter_form.rowconfigure((9), weight=1)
        self.frame_filter_form.grid(row=0, column=0, padx=(2, 6), pady=(2, 5), sticky="nsew")

        self.label_filter_heading = CTkLabel(
            self.frame_filter_form,
            text="Filter Person",
            text_color="#2c2c2c",
            font=("", 18, "bold"),
            anchor="w"
        )
        self.label_filter_heading.grid(row=0, column=0, columnspan=2, padx=15, pady=(25, 10), sticky="ew")

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
            text="Gender",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w",
        )
        self.label_filter_owner.grid(row=2, column=0, columnspan=2, padx=15, pady=(5, 0), sticky="ew")

        self.frame_owner_dropdown = CTkFrame(
            self.frame_filter_form,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_owner_dropdown.columnconfigure(0, weight=1)
        self.frame_owner_dropdown.rowconfigure(0, weight=1)
        self.frame_owner_dropdown.grid(row=3, column=0, columnspan=2, padx=15, pady=(2, 0), sticky="ew")

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
            height=35,
            width=35,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_owner.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)

        self.label_filter_type = CTkLabel(
            self.frame_filter_form,
            text="Status",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w",
        )
        self.label_filter_type.grid(row=4, column=0, columnspan=2, padx=15, pady=(15, 0), sticky="ew")

        self.frame_type_dropdown = CTkFrame(
            self.frame_filter_form,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_type_dropdown.columnconfigure(0, weight=1)
        self.frame_type_dropdown.rowconfigure(0, weight=1)
        self.frame_type_dropdown.grid(row=5, column=0, columnspan=2, padx=15, pady=(2, 0), sticky="ew")

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
            height=35,
            width=35,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_type.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)

        # self.label_filter_color = CTkLabel(
        #     self.frame_filter_form,
        #     text="",
        #     text_color="#2C2C2C",
        #     font = ("", 14),
        #     anchor="w",
        # )
        # self.label_filter_color.grid(row=6, column=0, columnspan = 2, padx=15, pady=(15,0), sticky="ew")

        # self.frame_color_dropdown = CTkFrame(
        #     self.frame_filter_form,
        #     height=40,
        #     fg_color="#F6F6F6",
        #     corner_radius=5,
        # )
        # self.frame_color_dropdown.columnconfigure(0, weight = 1)
        # self.frame_color_dropdown.rowconfigure(0, weight = 1)
        # self.frame_color_dropdown.grid(row=7, column=0, columnspan = 2, padx=15, pady=(2,0), sticky="ew")

        # self.entry_selected_color = CTkEntry(
        #     self.frame_color_dropdown,
        #     height=40,
        #     fg_color="#F6F6F6",
        #     textvariable=StringVar(value="All"),
        #     text_color="#828282",
        #     border_color="#DEDEDE",
        #     border_width=2,
        #     corner_radius=5,
        #     font=("", 14),
        # )
        # self.entry_selected_color.grid(row=0, column=0, sticky="nsew")
        # self.entry_selected_color.bind('<FocusIn>', lambda e: self.on_entry_focus_in(self.entry_selected_color,
        #                                                                              "All"))
        # self.entry_selected_color.bind('<FocusOut>', lambda e: self.on_entry_focus_out(self.entry_selected_color,
        #                                                                                "All"))

        # img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        # self.button_select_color = CTkButton(
        #     self.frame_color_dropdown,
        #     image=img_down_arraow,
        #     height = 35,
        #     width = 35,
        #     text = "",
        #     fg_color="transparent",
        #     cursor="hand2",
        #     border_width=0,
        #     hover=False,
        # )
        # self.button_select_color.grid(row = 0, column = 0, sticky = "e", padx=3, pady=1.5)

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
        self.button_cancel.bind("<Enter>",
                                lambda e: self.button_cancel.configure(fg_color="#313A46", text_color="#FFFFFF"))
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
        print(current_text, "_________current_text*********************************")
        has_real_text = False
        if entry == self.entry_selected_owner:
            has_real_text = self.owner_has_real_text
        elif entry == self.entry_selected_type:
            has_real_text = self.type_has_real_text
        # elif entry == self.entry_selected_color:
        #     has_real_text = self.color_has_real_text

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

    def update_table(self, list_vehicle_data: list):
        for child in self.frame_table_rows.winfo_children():
            child.destroy()

        self.current_selected_vehicle = None

        for row_index, row_data in enumerate(list_vehicle_data):
            row_bg_color = "transparent" if row_index % 2 == 0 else "#F7F9FB"

            full_name = row_data.get("full_name", "")
            photo = row_data.get('photo_path', "")

            # Create a properly sized image for display in the table
            image = None
            if photo:
                try:
                    # Decode base64 image
                    image_data = base64.b64decode(photo)
                    pil_img = Image.open(BytesIO(image_data))

                    # Resize image to consistent dimensions
                    pil_img = pil_img.resize((100, 100), Image.LANCZOS)

                    # Convert to CTkImage directly
                    image = CTkImage(light_image=pil_img, dark_image=pil_img, size=(100, 100))

                except Exception as e:
                    print(f"Error processing image: {e}")

            # Display regular cell data for each column
            for col_index, (column_name, cell_data) in enumerate(row_data.items()):
                rows = CTkLabel(
                    self.frame_table_rows,
                    text=cell_data,
                    height=100,
                    fg_color=row_bg_color,
                    anchor="w",
                    font=("", 14),
                    padx=10,
                    text_color="#2c2c2c"
                )

                rows.grid(row=row_index * 2, column=col_index, padx=0, sticky="nsew")

                # Stop after displaying the essential columns
                if col_index == 3:
                    break

            # Add image after the data columns but before the checkbox
            if image:
                img_label = CTkLabel(
                    self.frame_table_rows,
                    image=image,
                    text="",
                    fg_color=row_bg_color
                )
                img_label.grid(row=row_index * 2, column=4, padx=(5, 5), sticky="nsew")

            # Add checkbox after the image
            checkbox = CTkCheckBox(
                self.frame_table_rows,
                text="",
                border_width=1.5,
                corner_radius=2,
                fg_color="#2C2C2C",
                width=10,
                height=10,
                hover=False,
                command=lambda vn=full_name, rd=row_data, idx=row_index: self.on_checkbox_click(vn, rd, idx)
            )
            checkbox.grid(row=row_index * 2, column=5, padx=(5, 12), sticky="e")

            # Add a horizontal line underneath each row
            canvas_underline = CTkCanvas(
                self.frame_table_rows,
                height=1,
                bg="#D7DDE5",
                bd=0,
                highlightthickness=0
            )
            canvas_underline.grid(row=row_index * 2 + 1, column=0, columnspan=6, padx=0, pady=0, sticky="ew")

        self.on_page_change()

    def toggle_filter_popup(self):
        if (self.bool_filter_popup is False):  # Popup is closed, need to opened it
            self.frame_filter.grid_propagate(False)
            self.frame_filter.grid(row=2, column=0, rowspan=2, sticky="ne", padx=19, pady=(2, 80))
            self.frame_filter.tkraise()
        else:  # Popup is opened, need to closed it
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
                # self.reset_filter_form()

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
        self.entry_search.configure(placeholder_text="Enter Person Name..")

        if self.bool_filter_popup is True:
            self.toggle_filter_popup()

        for child in self.frame_table_rows.winfo_children():
            child.destroy()

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

        # self.entry_selected_color.configure(text_color="#828282", border_color="#DEDEDE")
        # self.entry_selected_color.delete(0, "end")
        # self.entry_selected_color.insert(0, "All")
        # self.entry_selected_color.configure(textvariable=StringVar(value="All"), state="normal")

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
            hover_color="#909090" if self.i_start_index <= 1 else "#313A46",
        )

        self.update_button_state(
            button=self.button_next,
            state="disabled" if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else "normal",
            cursor="X_cursor" if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else "hand2",
            fg_color="#e6e6ff" if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else "#444C57",
            hover_color="#909090" if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else "#313A46",
        )

    def update_button_state(self, button, state, cursor, fg_color, hover_color):
        button.configure(state=state, cursor=cursor, fg_color=fg_color)
        button.unbind("<Enter>")
        button.unbind("<Leave>")
        if state == "normal":
            button.bind("<Enter>", lambda e: button.configure(fg_color=hover_color))
            button.bind("<Leave>", lambda e: button.configure(fg_color=fg_color))

    def reset_filter_criteria(self):
        self.dict_filter_criteria["gender"] = "%"
        self.dict_filter_criteria["status"] = "%"
        self.dict_filter_criteria["str_color"] = "%"

    # def on_checkbox_click(self, vehicle_number,row_data, row_index):

    #     if vehicle_number in self.selected_vehicle_set:
    #         self.selected_vehicle_set.remove(vehicle_number)

    #     else:
    #         self.selected_vehicle_set.add(vehicle_number)

    #     if self.current_selected_vehicle is not None and self.current_selected_vehicle != row_index:
    #         try:
    #             previous_checkbox = self.frame_table_rows.grid_slaves(row=self.current_selected_vehicle * 2, column=5)[0]
    #         except Exception as e:
    #             print(e)
    #     self.update_button_states()

    def on_checkbox_click(self, full_name, row_data, row_index):

        if full_name in self.selected_face_set:
            self.selected_face_set.remove(full_name)

        else:
            self.selected_face_set.add(full_name)

        if self.current_selected_vehicle is not None and self.current_selected_vehicle != row_index:
            try:
                previous_checkbox = self.frame_table_rows.grid_slaves(row=self.current_selected_vehicle * 2, column=5)[
                    0]
            except Exception as e:
                print(e)
        self.update_button_states()

    def reset_checkbox(self):
        self.selected_face_set.clear()
        self.update_button_states()
        self.destroy_registration_form()
        self.destroy_edit_vehicle_form()
        self.update_table(self.vehicle_data)

    def update_button_states(self):
        num_selected = len(self.selected_face_set)

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
                hover_color="313A46"
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

    # ----------------------------------------------------[Add Vechile]---------------------------------------------------------------------------------------------------

    def Add_Face_Form(self, num=None):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        popup_width = 600
        popup_height = 810
        self.current_open_dropdown = None  # Keep track of the currently open dropdown
        self.bool_dropdown_opened = False

        # Calculate position to center the popup on the screen
        x_position = (screen_width - popup_width) // 2  # Center horizontally
        y_position = (screen_height - popup_height) // 2  # Center vertically

        # Set the geometry for the popup
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()
        # Create a popup window
        self.popup = Toplevel(self)

        self.popup.geometry(f"{popup_width}x{popup_height}+{x_position + 200}+{y_position + 80}")
        self.popup.title("Add New Face")
        # self.popup.overrideredirect(True)
        self.popup.configure(bg="#FFFFFF")
        self.popup.attributes("-topmost", True)

        self.popup.columnconfigure((0, 1), weight=1, uniform="a")

        data = {'vechike_name': '',
                'heading': 'Face_registration_form',
                'state': 'normal'
                }
        self.Add_Form(data, num)

    def Add_Form(self, data=[], user_id=None):
        self.i_form_width = 600  # Width of parent popup
        self.i_form_height = 810  # Increased height to accommodate new fields
        self.bool_dropdown_opened = False
        self.list_gender = ["Male", "Female", "Other"]
        self.list_status = ["WhiteList", "BlackList"]
        self.current_open_button = None
        self.photo_path = None

        # Main heading
        self.label_heading = CTkLabel(
            # self.frame_inside,
            self.popup,
            text="Face Registration",
            text_color="#2C2C2C",
            height=38,
            font=("", 20, "bold"),
            corner_radius=10,
            anchor="center",
            fg_color="transparent"
        )
        self.label_heading.grid(row=0, column=0, columnspan=2, pady=(15, 0), padx=(10, 10), sticky="nsew")

        self.frame_photo = CTkFrame(
            # self.frame_inside,
            self.popup,
            fg_color="#D9D9D9",
            width=200,
            height=200,
            border_width=2,
            border_color="#2c2c2c",
            corner_radius=5
        )
        self.frame_photo.grid(row=1, column=0, columnspan=2, pady=(10, 0), padx=25)
        self.img_uplaod = CTkImage(Image.open("C:\\Users\\ITLP 93\\Downloads\\up.png.jpg"), size=(25, 25))
        self.frame_photo.grid_propagate(False)

        self.button_upload1 = CTkButton(
            self.frame_photo,
            image=self.img_uplaod,
            text="Upload Photo",
            height=30,
            width=30,
            fg_color="transparent",
            text_color="black",
            font=("", 12),
            cursor="hand2",
            command=self.upload_photo,
            compound="right"
        )
        self.button_upload1.grid(row=1, column=0, columnspan=2, pady=(160, 0), padx=25, sticky="nsew")
        # Main details frame
        self.frame_details = CTkFrame(
            # self.frame_inside,
            self.popup,
            fg_color="transparent",
            border_color="#D2D2D2",
            border_width=2,
            corner_radius=5,
        )
        self.frame_details.columnconfigure((0, 1), weight=1, uniform="a")
        self.frame_details.rowconfigure(0, weight=1)
        self.frame_details.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=25, pady=(10, 0))

        # Left Column
        self.frame_form_lcol = CTkFrame(
            self.frame_details,
            fg_color="transparent",
        )
        self.frame_form_lcol.columnconfigure(0, weight=1)
        self.frame_form_lcol.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=(5, 10))

        # Right Column
        self.frame_form_rcol = CTkFrame(
            self.frame_details,
            fg_color="transparent",
        )
        self.frame_form_rcol.columnconfigure(0, weight=1)
        self.frame_form_rcol.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=(5, 10))

        # First Name Field
        self.label_first_name = CTkLabel(
            self.frame_form_lcol,
            text="First Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_first_name.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=(5, 1))

        self.entry_first_name = CTkEntry(
            self.frame_form_lcol,
            height=35,
            fg_color="#F6F6F6",
            placeholder_text="Enter First Name",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_first_name.grid(row=1, column=0, sticky="ew", padx=(10, 5))

        # Last Name Field
        self.label_middle_name = CTkLabel(
            self.frame_form_rcol,
            text="Middle Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_middle_name.grid(row=0, column=0, sticky="ew", padx=(5, 10), pady=(5, 1))

        self.entry_middle_name = CTkEntry(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            placeholder_text="Enter Middle Name",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_middle_name.grid(row=1, column=0, sticky="ew", padx=(5, 10))

        self.label_last_name = CTkLabel(
            self.frame_form_lcol,
            text="Last Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_last_name.grid(row=2, column=0, sticky="ew", padx=(10, 5), pady=(15, 1))

        self.entry_last_name = CTkEntry(
            self.frame_form_lcol,
            height=35,
            fg_color="#F6F6F6",
            placeholder_text="Enter Last Name",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_last_name.grid(row=3, column=0, sticky="ew", padx=(10, 5))

        # Gender Dropdown
        self.label_gender = CTkLabel(
            self.frame_form_rcol,
            text="Gender",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_gender.grid(row=2, column=0, sticky="ew", padx=(5, 10), pady=(15, 1))

        self.frame_gender_dropdown = CTkFrame(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_gender_dropdown.columnconfigure(0, weight=1)
        self.frame_gender_dropdown.grid(row=3, column=0, padx=(5, 10), sticky="ew")

        self.entry_selected_gender = CTkEntry(
            self.frame_gender_dropdown,
            height=35,
            fg_color="#F6F6F6",
            placeholder_text="Select Gender",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_selected_gender.grid(row=0, column=0, sticky="nsew")
        self.entry_selected_gender.bind('<Button-1>',
                                        lambda event: self.popup_Add_dropdown(self.frame_form_rcol, self.list_gender,
                                                                              entry_destination=self.entry_selected_gender,
                                                                              i_row=4, i_rowspan=2, type=1)
                                        )

        img_down_arrow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.button_select_gender = CTkButton(
            self.frame_gender_dropdown,
            image=img_down_arrow,
            height=30,
            width=30,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
            command=lambda: self.popup_Add_dropdown(self.frame_form_rcol, self.list_gender,
                                                    entry_destination=self.entry_selected_gender,
                                                    i_row=4, i_rowspan=2, type=1)
        )
        self.button_select_gender.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)
        img_uplaod = CTkImage(Image.open("C:\\Users\\ITLP 93\\Downloads\\up.png.jpg"), size=(25, 25))

        self.label_age = CTkLabel(
            self.frame_form_lcol,
            text="Age",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_age.grid(row=4, column=0, sticky="ew", padx=(10, 5), pady=(15, 1))

        self.entry_age = CTkEntry(
            self.frame_form_lcol,
            height=35,
            fg_color="#F6F6F6",
            placeholder_text="Enter Age",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_age.grid(row=5, column=0, sticky="ew", padx=(10, 5))

        # Status Dropdown
        self.label_status = CTkLabel(
            self.frame_form_rcol,
            text="Status",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_status.grid(row=4, column=0, sticky="ew", padx=(5, 10), pady=(15, 1))

        self.frame_status_dropdown = CTkFrame(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_status_dropdown.columnconfigure(0, weight=1)
        self.frame_status_dropdown.grid(row=5, column=0, padx=(5, 10), sticky="ew")

        self.entry_selected_status = CTkEntry(
            self.frame_status_dropdown,
            height=35,
            fg_color="#F6F6F6",
            placeholder_text="Select Status",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_selected_status.grid(row=0, column=0, sticky="nsew")

        self.button_select_status = CTkButton(
            self.frame_status_dropdown,
            image=img_down_arrow,
            height=30,
            width=30,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
            command=lambda: self.popup_Add_dropdown(self.frame_form_rcol, self.list_status,
                                                    entry_destination=self.entry_selected_status,
                                                    i_row=6, i_rowspan=2, type=1)
        )
        self.button_select_status.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)
        self.label_error = CTkLabel(
            self.frame_form_rcol,
            text="",
            text_color="#2C2C2C",
            font=("", 14),
            height=40,
            anchor="w"
        )
        self.label_error.grid(row=7, column=0, sticky="ew", padx=(5, 10), pady=(15, 1))

        # Save and Cancel Buttons
        self.button_add_save = CTkButton(
            # self.frame_inside,
            self.popup,
            height=38,
            width=100,
            text="Save",
            text_color="#FFFFFF",
            fg_color="#3A36F5",
            border_color="#3A36F5",
            font=("", 14),
            cursor="hand2",
            hover=False,
            # command=self.save_registration
        )
        self.button_add_save.grid(row=3, column=0, padx=4, pady=(25, 25), sticky="e")

        self.button_cancel = CTkButton(
            # self.frame_inside,
            self.popup,
            height=38,
            width=100,
            text="Cancel",
            text_color="#FFFFFF",
            fg_color="#6C757D",
            border_color="#6C757D",
            font=("", 14),
            cursor="hand2",
            hover=False,
            command=self.destroy_registration_form
        )
        self.button_cancel.grid(row=3, column=1, padx=4, pady=(25, 25), sticky="w")
        if hasattr(self, 'on_form_add_ready'):
            self.on_form_add_ready()

        # Bind click events
        # self.frame_form_lcol.bind('<Button-1>', self.handle_outside_click)
        # self.popup.bind('<Button-1>', self.handle_outside_click)

    def upload_photo(self):
        """Handle photo upload with a focused dialog"""
        # Ensure the dialog is on top and focused
        file_types = [('Image Files', '*.png *.jpg *.jpeg *.gif *.bmp')]

        # Use .lift() and .focus_force() to bring the dialog to the foreground
        self.popup.lift()  # Lift the main window
        self.popup.focus_force()  # Force focus on the main window

        # Open file dialog
        file_path = filedialog.askopenfilename(
            filetypes=file_types,
            title="Select Photo",  # Add a title to the dialog
            parent=self.popup  # Set parent to ensure it's on top of the main window
        )

        if file_path:
            try:
                # Open and resize image
                image = Image.open(file_path)
                image = image.resize((190, 190), Image.Resampling.LANCZOS)
                photo = CTkImage(image, size=(190, 190))

                # Remove existing widgets in photo frame
                for widget in self.frame_photo.winfo_children():
                    widget.destroy()

                # Display new photo
                photo_label = CTkLabel(
                    self.frame_photo,
                    image=photo,
                    text="",
                    fg_color="#3A36F5"
                )
                photo_label.image = photo  # Keep a reference
                photo_label.place(relx=0.5, rely=0.5, anchor="center")

                # Add a button with an icon to upload another image
                self.upload_icon = CTkImage(Image.open("C:\\Users\\ITLP 93\\Downloads\\up.png.jpg"), size=(25, 25))

                upload_button = CTkButton(
                    self.frame_photo,
                    image=self.upload_icon,
                    fg_color="#3A36F5",
                    border_color="#2c2c2c",
                    text="Upload Photo",
                    command=self.upload_photo,  # You can call the same function to allow re-upload
                    compound="right"
                )
                upload_button.image = self.upload_icon  # Keep a reference
                upload_button.place(relx=0.5, rely=0.9, anchor="center")

                # Update photo path
                self.photo_path = file_path

            except Exception as e:
                print(e)
                self.label_error.configure(text=f"Error uploading photo: {str(e)}")

    def handle_entry_click(self, event):
        #     """Handle clicks on entry fields"""
        if not self.active_dropdown_frame:
            self.popup_Add_dropdown(self.parent_frame, self.dropdown_data, event.widget, row=0, i_rowspan=3)

    def handle_outside_click(self, event):
        print("hiiiii")
        """Handle clicks outside the dropdown"""
        if not self.active_dropdown_frame:            return

        # Get the clicked widget
        clicked_widget = event.widget

        # Check if click is within dropdown or dropdown buttons
        if not self.is_click_in_dropdown(event.x_root, event.y_root):
            self.close_active_dropdown()

    def is_click_in_dropdown(self, x, y):
        """Check if click coordinates are within the dropdown area"""
        print("is_click_in_dropdown")
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
            for btn in [self.button_edit_select_status, self.entry_edit_selected_company, self.entry_edit_type]:
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

    def popup_Add_dropdown(self, parent_frame: CTkFrame, list_data: list = [], entry_destination: CTkEntry = None,
                           i_row: int = None, i_rowspan: int = 3, type: int = 0):
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
                frame_Add_maindropdown_window = CTkFrame(
                    parent_frame,
                    fg_color="#DEDEDE",
                    height=40,
                    width=30,
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
                    width=28,
                    corner_radius=5
                )
                frame_Add_popup_table.columnconfigure(0, weight=1)
                frame_Add_popup_table.grid(row=0, column=0, columnspan=2, padx=(10, 10), pady=(1, 3), sticky="nsew")
                text_entered = entry_destination.get().strip()
                # Check if the entry field is empty
                # if text_entered  and text_entered not in self.list_blacklist:
                # #     # Filter the list_data based on the entered text
                #    filtered_data = [row_data for row_data in list_data if text_entered.lower() in row_data.lower()]
                # else:
                # filtered_data=list_data

                # Add options to the dropdowns
                for index, row_data in enumerate(list_data):
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
                frame_Add_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(14, 7),
                                                   pady=(5, 0))
                frame_Add_maindropdown_window.tkraise()

                # Update state tracking variables to manage the currently open dropdown
                self.current_open_dropdown = entry_destination
                self.active_dropdown_frame = frame_Add_maindropdown_window
                # self.popup.bind('<Button-1>', self.handle_outside_click)
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
            # Get the entered text in the entry field
            text_entered = entry_destination.get().strip()

            # Check if the entry field is empty
            if text_entered and text_entered not in self.list_blacklist and text_entered != "Select Status":
                # Filter the list_data based on the entered text
                filtered_data = [row_data for row_data in list_data if text_entered.lower() in row_data.lower()]
            else:
                # If the entry is empty, or contains "Select Status" or blacklist entry, show all options
                filtered_data = list_data

            # Add filtered options to the dropdown
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
            frame_Add_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(14, 7),
                                               pady=(5, 0))
            frame_Add_maindropdown_window.tkraise()

            # Update state tracking variables to manage the currently open dropdown
            self.current_open_dropdown = entry_destination
            self.active_dropdown_frame = frame_Add_maindropdown_window

    def select_option(self, selected_option: str, entry_destination: CTkEntry, dropdown_frame: CTkFrame):

        """Method to handle the selection of an option from the dropdown"""
        if (selected_option == "All"):
            self.label_error.configure(text="Dropdown entries cant selecte All")
            entry_destination.configure(state="normal", text_color="#414141", border_color="red")
        else:
            self.label_error.configure(text="")
            entry_destination.configure(state="normal", text_color="#414141", border_color="green")
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

    def destroy_registration_form(self):
        """Helper method to destroy the add vehicle form."""
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()  # Destroy the popup (form) window

    def destroy_edit_vehicle_form(self):
        """Helper method to destroy the add vehicle form."""
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()  # Destroy the popup (form) window

    # ___________________________________________________________________[edit vechile]_______________________________________________________________________________________

    def edit_selected_Vehicle(self):
        """Handle editing of selected camera and ensure proper state reset"""
        if len(self.selected_face_set) == 1:
            Name = next(iter(self.selected_face_set))
            print(Name, "NAME in slected vehcile *******************")
            self.vehicle = next((cam for cam in self.vehicle_data if cam['full_name'] == Name), None)

            if self.vehicle:
                self.edit_Face_Form(self.vehicle)
                # self.edit_reset_vechile(vehicle)

    def edit_Face_Form(self, vehicle=[]):
        print(self.vehicle, "************************")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        popup_width = 600
        popup_height = 810
        self.current_open_dropdown = None  # Keep track of the currently open dropdown
        self.bool_dropdown_opened = False

        # Calculate position to center the popup on the screen
        x_position = (screen_width - popup_width) // 2  # Center horizontally
        y_position = (screen_height - popup_height) // 2  # Center vertically

        # Set the geometry for the popup
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()
        # Create a popup window
        self.popup = Toplevel(self)

        self.popup.geometry(f"{popup_width}x{popup_height}+{x_position + 200}+{y_position + 80}")
        self.popup.title("Edit Face")
        # self.popup.overrideredirect(True)
        self.popup.configure(bg="#FFFFFF")
        self.popup.attributes("-topmost", True)

        self.popup.columnconfigure((0, 1), weight=1, uniform="a")

        data = {'vechike_name': '',
                'heading': 'Face_registration_form',
                'state': 'normal'
                }
        self.edit_vechile(data)

    def edit_vechile(self, vehicle=[]):

        self.i_form_width = 600  # Width of parent popup
        self.i_form_height = 810  # Increased height to accommodate new fields
        self.bool_dropdown_opened = False
        self.list_gender = ["Male", "Female", "Other"]
        self.list_status = ["WhiteList", "BlackList"]
        self.current_open_button = None
        self.photo_path = None

        photo = self.vehicle.get('photo_path', "")
        self.old_photo = self.vehicle.get('photo_path', "")

        # Create a properly sized image for display in the table

        # Main heading
        self.Edit_label_heading = CTkLabel(
            # self.frame_inside,
            self.popup,
            text="Edit Register Face ",
            text_color="#2C2C2C",
            height=38,
            font=("", 20, "bold"),
            corner_radius=10,
            anchor="center",
            fg_color="transparent"
        )
        self.Edit_label_heading.grid(row=0, column=0, columnspan=2, pady=(15, 0), padx=(10, 10), sticky="nsew")
        photo = self.vehicle.get('photo_path', "")

        # Create a properly sized image for display in the table
        image = None
        if photo:
            try:
                # Decode base64 image
                image_data = base64.b64decode(photo)
                pil_img = Image.open(BytesIO(image_data))

                # Resize image to consistent dimensions
                pil_img = pil_img.resize((190, 190), Image.LANCZOS)

                # Convert to CTkImage directly
                image = CTkImage(light_image=pil_img, dark_image=pil_img, size=(190, 190))

            except Exception as e:
                print(f"Error processing image: {e}")

        self.Edit_frame_photo = CTkFrame(
            self.popup,
            fg_color="#D9D9D9",
            width=200,
            height=200,
            border_width=2,
            border_color="#2c2c2c",
            corner_radius=5
        )
        self.Edit_frame_photo.grid(row=1, column=0, columnspan=2, pady=(0, 0), padx=25)
        self.Edit_img_uplaod = CTkImage(Image.open("C:\\Users\\ITLP 93\\Downloads\\up.png.jpg"), size=(25, 25))
        self.Edit_frame_photo.grid_propagate(False)
        img_label = CTkLabel(
            self.Edit_frame_photo,
            image=image,
            text="",
            fg_color="#3A36F5"
        )
        img_label.grid(row=1, column=0, padx=(5, 5), sticky="nsew")

        self.Edit_button_upload1 = CTkButton(
            self.Edit_frame_photo,
            image=self.Edit_img_uplaod,
            text="Replace Photo",
            height=30,
            width=30,
            fg_color="#3A36F5",
            text_color="white",
            font=("", 12),
            cursor="hand2",
            command=self.upload_Edit_photo,
            compound="right"
        )
        self.Edit_button_upload1.grid(row=1, column=0, columnspan=2, pady=(160, 0), padx=25, sticky="nsew")
        # Main details frame
        self.Edit_frame_details = CTkFrame(
            # self.frame_inside,
            self.popup,
            fg_color="transparent",
            border_color="#D2D2D2",
            border_width=2,
            corner_radius=5,
        )
        self.Edit_frame_details.columnconfigure((0, 1), weight=1, uniform="a")
        self.Edit_frame_details.rowconfigure(0, weight=1)
        self.Edit_frame_details.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=25, pady=(10, 0))

        # Left Column
        self.frame_form_lcol = CTkFrame(
            self.Edit_frame_details,
            fg_color="transparent",
        )
        self.frame_form_lcol.columnconfigure(0, weight=1)
        self.frame_form_lcol.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=(5, 10))

        # Right Column
        self.frame_form_rcol = CTkFrame(
            self.Edit_frame_details,
            fg_color="transparent",
        )
        self.frame_form_rcol.columnconfigure(0, weight=1)
        self.frame_form_rcol.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=(5, 10))

        # First Name Field
        self.Edit_label_first_name = CTkLabel(
            self.frame_form_lcol,
            text="First Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_first_name.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=(5, 1))
        full_name = self.vehicle.get("full_name", "")

        # Split the full name into words
        name_parts = full_name.split()

        # Check how many parts we have
        if len(name_parts) == 2:
            # First name and last name provided, no middle name
            first_name = name_parts[0]
            middle_name = None
            last_name = name_parts[1]
        elif len(name_parts) == 3:
            # First name, middle name, and last name provided
            first_name = name_parts[0]
            middle_name = name_parts[1]
            last_name = name_parts[2]

        self.Edit_entry_first_name = CTkEntry(
            self.frame_form_lcol,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value=first_name),
            text_color="#414141",
            # placeholder_text="Enter First Name",
            # placeholder_text_color="#828282",
            # text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Edit_entry_first_name.grid(row=1, column=0, sticky="ew", padx=(10, 5))

        # Last Name Field
        self.Edit_label_middle_name = CTkLabel(
            self.frame_form_rcol,
            text="Middle Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_middle_name.grid(row=0, column=0, sticky="ew", padx=(5, 10), pady=(5, 1))

        self.Edit_entry_middle_name = CTkEntry(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value=middle_name),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Edit_entry_middle_name.grid(row=1, column=0, sticky="ew", padx=(5, 10))

        self.Edit_label_last_name = CTkLabel(
            self.frame_form_lcol,
            text="Last Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_last_name.grid(row=2, column=0, sticky="ew", padx=(10, 5), pady=(15, 1))

        self.Edit_entry_last_name = CTkEntry(
            self.frame_form_lcol,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value=last_name),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Edit_entry_last_name.grid(row=3, column=0, sticky="ew", padx=(10, 5))

        # Gender Dropdown
        self.Edit_label_gender = CTkLabel(
            self.frame_form_rcol,
            text="Edit Gender",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_gender.grid(row=2, column=0, sticky="ew", padx=(5, 10), pady=(15, 1))

        self.Edit_frame_gender_dropdown = CTkFrame(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.Edit_frame_gender_dropdown.columnconfigure(0, weight=1)
        self.Edit_frame_gender_dropdown.grid(row=3, column=0, padx=(5, 10), sticky="ew")

        self.Edit_entry_selected_gender = CTkEntry(
            self.Edit_frame_gender_dropdown,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value=self.vehicle["gender"]),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Edit_entry_selected_gender.grid(row=0, column=0, sticky="nsew")

        img_down_arrow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(22, 22))
        self.Edit_button_select_gender = CTkButton(
            self.Edit_frame_gender_dropdown,
            image=img_down_arrow,
            height=30,
            width=30,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
            command=lambda: self.popup_Edit_dropdown(self.frame_form_rcol, self.list_gender,
                                                     entry_destination=self.Edit_entry_selected_gender,
                                                     i_row=4, i_rowspan=2, type=1)
        )
        self.Edit_button_select_gender.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)
        img_uplaod = CTkImage(Image.open("C:\\Users\\ITLP 93\\Downloads\\up.png.jpg"), size=(25, 25))

        self.Edit_label_age = CTkLabel(
            self.frame_form_lcol,
            text="Edit Age",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_age.grid(row=4, column=0, sticky="ew", padx=(10, 5), pady=(15, 1))

        self.Edit_entry_age = CTkEntry(
            self.frame_form_lcol,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value=self.vehicle["age"]),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Edit_entry_age.grid(row=5, column=0, sticky="ew", padx=(10, 5))

        # Status Dropdown
        self.Edit_label_status = CTkLabel(
            self.frame_form_rcol,
            text="Edit Status",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_status.grid(row=4, column=0, sticky="ew", padx=(5, 10), pady=(15, 1))

        self.Edit_frame_status_dropdown = CTkFrame(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.Edit_frame_status_dropdown.columnconfigure(0, weight=1)
        self.Edit_frame_status_dropdown.grid(row=5, column=0, padx=(5, 10), sticky="ew")

        self.Edit_entry_selected_status = CTkEntry(
            self.Edit_frame_status_dropdown,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value=self.vehicle["status"]),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Edit_entry_selected_status.grid(row=0, column=0, sticky="nsew")

        self.Edit_button_select_status = CTkButton(
            self.Edit_frame_status_dropdown,
            image=img_down_arrow,
            height=30,
            width=30,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
            command=lambda: self.popup_Edit_dropdown(self.frame_form_rcol, self.list_status,
                                                     entry_destination=self.Edit_entry_selected_status,
                                                     i_row=6, i_rowspan=2, type=1)
        )
        self.Edit_button_select_status.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)

        # Error Label
        self.Edit_label_error = CTkLabel(
            self.Edit_frame_details,
            text="",
            text_color="#FF0000",
            font=("", 12),
            anchor="center",
            height=15,
            wraplength=350
        )
        self.Edit_label_error.grid(column=0, row=8, columnspan=2, sticky="ew", pady=(5, 20), padx=(20, 20))

        # Save and Cancel Buttons
        self.Edit_button_add_save = CTkButton(
            # self.frame_inside,
            self.Edit_frame_details,
            # self.popup,
            height=38,
            width=100,
            text="Save",
            text_color="#FFFFFF",
            fg_color="#3A36F5",
            border_color="#3A36F5",
            font=("", 14),
            cursor="hand2",
            hover=False,
            # command=self.save_registration
        )
        self.Edit_button_add_save.grid(row=3, column=0, padx=4, pady=(25, 25), sticky="e")

        self.Edit_button_cancel = CTkButton(
            # self.frame_inside,
            # self.popup,
            self.Edit_frame_details,
            height=38,
            width=100,
            text="Cancel",
            text_color="#FFFFFF",
            fg_color="#6C757D",
            border_color="#6C757D",
            font=("", 14),
            cursor="hand2",
            hover=False,
            command=self.destroy_edit_vehicle_form
        )
        self.Edit_button_cancel.grid(row=3, column=1, padx=4, pady=(25, 25), sticky="w")
        if hasattr(self, 'on_form_add_ready'):
            self.on_form_edit_ready()

        # Bind click events
        # self.frame_form_lcol.bind('<Button-1>', self.handle_outside_click)
        # self.frame_form_rcol.bind('<Button-1>', self.handle_outside_click)
        # self.popup.bind('<Button-1>', self.handle_outside_click)

    def upload_Edit_photo(self):
        file_types = [('Image Files', '*.png *.jpg *.jpeg *.gif *.bmp')]

        # Use .lift() and .focus_force() to bring the dialog to the foreground
        self.popup.lift()  # Lift the main window
        self.popup.focus_force()  # Force focus on the main window

        # Open file dialog
        file_path = filedialog.askopenfilename(
            filetypes=file_types,
            title="Select Photo",  # Add a title to the dialog
            parent=self.popup  # Set parent to ensure it's on top of the main window
        )

        if file_path:
            try:
                # Open and resize image
                image = Image.open(file_path)
                image = image.resize((190, 190), Image.Resampling.LANCZOS)
                photo = CTkImage(image, size=(190, 190))

                # Remove existing widgets in photo frame
                for widget in self.Edit_frame_photo.winfo_children():
                    widget.destroy()

                # Display new photo
                photo_label = CTkLabel(
                    self.Edit_frame_photo,
                    image=photo,
                    text="",
                    fg_color="#3A36F5"
                )
                photo_label.image = photo  # Keep a reference
                photo_label.place(relx=0.5, rely=0.5, anchor="center")

                # Add a button with an icon to upload another image
                self.upload_icon = CTkImage(Image.open("C:\\Users\\ITLP 93\\Downloads\\up.png.jpg"), size=(25, 25))
                # self.upload_icon = CTkImage(Image.open(".\\Resources\\images\\Group 405.png"), size=(25, 25))
                # upload_icon = Image.open("path_to_upload_icon.png")  # Add the correct path for your icon
                # self.upload_icon = self.upload_icon.resize((30, 30), Image.Resampling.LANCZOS)
                # self.upload_icon = CTkImage(self.upload_icon, size=(30, 30))

                upload_Edit_button = CTkButton(
                    self.Edit_frame_photo,
                    image=self.upload_icon,
                    fg_color="#3A36F5",
                    border_color="black",
                    text="Uplaod Photo",
                    command=self.upload_Edit_photo,  # You can call the same function to allow re-upload
                    compound="right"
                )
                upload_Edit_button.image = self.upload_icon  # Keep a reference
                upload_Edit_button.place(relx=0.5, rely=0.9, anchor="center")  # Adjust the position if needed

                # Update photo path
                self.photo_path = file_path

            except Exception as e:
                print(e)
                self.Edit_label_error.configure(text=f"Error uploading photo: {str(e)}")

    # def upload_Edit_photo(self):
    #     """Handle photo upload"""
    #     file_types = [('Image Files', '*.png *.jpg *.jpeg *.gif *.bmp')]
    #     file_path = filedialog.askopenfilename(filetypes=file_types)

    #     if file_path:
    #         try:
    #             # Open and resize image
    #             image = Image.open(file_path)
    #             image = image.resize((190, 190), Image.Resampling.LANCZOS)
    #             photo = CTkImage(image, size=(190, 190))

    #             # Remove existing widgets in photo frame
    #             for widget in self.Edit_frame_photo.winfo_children():
    #                 widget.destroy()

    #             # Display new photo
    #             photo_label = CTkLabel(
    #                 self.Edit_frame_photo,
    #                 image=photo,
    #                 text="",
    #                 fg_color="#3A36F5"
    #             )
    #             photo_label.image = photo  # Keep a reference
    #             photo_label.place(relx=0.5, rely=0.5, anchor="center")

    #             # Add a button with an icon to upload another image
    #             self.upload_icon = CTkImage(Image.open(".\\Resources\\images\\Group 405.png"), size=(25, 25))
    #             # self.upload_icon = CTkImage(Image.open(".\\Resources\\images\\Group 405.png"), size=(25, 25))
    #             # upload_icon = Image.open("path_to_upload_icon.png")  # Add the correct path for your icon
    #             # self.upload_icon = self.upload_icon.resize((30, 30), Image.Resampling.LANCZOS)
    #             # self.upload_icon = CTkImage(self.upload_icon, size=(30, 30))

    #             upload_Edit_button = CTkButton(
    #                 self.Edit_frame_photo,
    #                 image=self.upload_icon,
    #                 fg_color="#3A36F5",
    #                 border_color="black",
    #                 text="Uplaod Photo",
    #                 command=self.upload_Edit_photo,  # You can call the same function to allow re-upload
    #                 compound="right"
    #             )
    #             upload_Edit_button.image = self.upload_icon  # Keep a reference
    #             upload_Edit_button.place(relx=0.5, rely=0.9, anchor="center")  # Adjust the position if needed

    #             # Update photo path
    #             self.photo_path= file_path

    #         except Exception as e:
    #             print(e)
    #             self.Edit_label_error.configure(text=f"Error uploading photo: {str(e)}")

    def handle_entry_click(self, event):
        """Handle clicks on entry fields"""
        if self.active_dropdown_frame:
            self.close_active_dropdown()

    def handle_outside_click(self, event):
        """Handle clicks outside the dropdown"""
        if not self.active_dropdown_frame:            return

        # Get the clicked widget
        clicked_widget = event.widget
        # if(self.handle_entry_click(event)):
        #     self.close_active_dropdown()

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
            for btn in [self.button_edit_select_status, self.entry_edit_selected_company, self.entry_edit_type]:
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

    def popup_Edit_dropdown(self, parent_frame: CTkFrame, list_data: list = [], entry_destination: CTkEntry = None,
                            i_row: int = None, i_rowspan: int = 3, type: int = 0):
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
                    width=30,
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
                    width=28,
                    corner_radius=5
                )
                frame_Edit_popup_table.columnconfigure(0, weight=1)
                frame_Edit_popup_table.grid(row=0, column=0, columnspan=2, padx=(10, 10), pady=(1, 3), sticky="nsew")
                # text_entered = entry_destination.get().strip()
                # Check if the entry field is empty
                # if text_entered  and text_entered not in self.list_blacklist:
                #     # Filter the list_data based on the entered text
                #     filtered_data = [row_data for row_data in list_data if text_entered.lower() in row_data.lower()]
                # else:
                #  filtered_data=list_data

                # Add options to the dropdowns
                for index, row_data in enumerate(list_data):
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
                        command=lambda selected_option=row_data: self.Edit_select_option(selected_option,
                                                                                         entry_destination,
                                                                                         frame_Edit_maindropdown_window)
                    )
                    button_options.grid(row=index, column=0, sticky="nsew", padx=1)

                # Show the dropdown
                frame_Edit_maindropdown_window.grid_propagate(False)
                frame_Edit_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(14, 7),
                                                    pady=(5, 0))
                frame_Edit_maindropdown_window.tkraise()

                # Update state tracking variables to manage the currently open dropdown
                self.current_open_dropdown = entry_destination
                self.active_dropdown_frame = frame_Edit_maindropdown_window

    def Edit_select_option(self, selected_option: str, entry_destination: CTkEntry, dropdown_frame: CTkFrame):

        """Method to handle the selection of an option from the dropdown"""
        if (selected_option == "All"):
            self.Edit_label_error.configure(text="Dropdown entries cant selecte All")
            entry_destination.configure(state="normal", text_color="#414141", border_color="red")
        else:
            self.Edit_label_error.configure(text="")
            entry_destination.configure(state="normal", text_color="#414141", border_color="green")
        entry_destination.delete(0, "end")  # Clear the current text

        # Insert the selected option into the entry field
        if selected_option:
            entry_destination.insert(0, selected_option)  # Insert the selected option

        # If the entry is entry_selected_status, disable it for further editing
        if entry_destination == self.Edit_entry_selected_status:
            entry_destination.configure(state="disabled")  # Disable the entry field to prevent editing

        # Close the dropdown after selection
        if dropdown_frame.winfo_exists():
            dropdown_frame.grid_forget()

        # Reset dropdown state tracking variables
        self.current_open_dropdown = None
        self.active_dropdown_frame = None



