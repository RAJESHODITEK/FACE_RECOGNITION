import base64
from io import BytesIO
import io
import os
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCanvas, CTkScrollableFrame, CTkImage, CTkCheckBox
from tkinter import StringVar, Toplevel, filedialog, messagebox

from tkinter import PhotoImage
from PIL import Image, ImageTk
import cv2


class PersonListInteface(CTkFrame):

    def __init__(self, *args, root_width: int = 1920, root_height: int = 1080, **kwargs):

        super().__init__(*args, **kwargs)

        self.person_data = []
        self.bool_filter_popup = False
        self.bool_owner_dropdown_opened = False
        self.bool_type_dropdown_opened = False
        self.bool_color_dropdown_opened = False
        self.active_dropdown_frame = False
        self.person = {}
        self.photos = []
        self.photolength = 0

        self.configure(fg_color="#F1F5FA", corner_radius=0)

        self.dict_columns_buttons = {}

        self.selected_face_set = set()
        self.selected_rows = set()
        self.selected_id = set()

        self.i_start_index = 0
        self.i_end_index = 0
        self.i_total_data = 0
        self.dict_filter_criteria = {
            "gender": "%",
            "status": "%",
            "full_name": "",
            'str_person_number': 0
        }

        i_form_width = int((int(root_width * 0.89)) * 0.885)
        i_form_height = int((int(root_height * 0.88)) * 0.9)
        self.page_height = i_form_height

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
        sort_icon = CTkImage(Image.open(".\\Resources\\images\\sort3.png"), size=(15, 15))
        self.current_sort = {"column": None, "order": None}
        self.column_buttons = {}
        sort_default_icon = CTkImage(Image.open(".\\Resources\\images\\normal.png"), size=(15, 15))
        sort_asc_icon = CTkImage(Image.open(".\\Resources\\images\\asc.png"), size=(15, 15))
        sort_desc_icon = CTkImage(Image.open(".\\Resources\\images\\desc.png"), size=(15, 15))

        self.table_headers = ["Name", "Age", "Gender", "Status", "Registered Face"]
        for col, value in enumerate(self.table_headers):
            if value == "Registered Face":
                sort_default_icon = ""
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
            if value != "Registered Face":
                self.dict_columns_buttons[value] = [button, False]

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
            state="disabled"
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
            height=30,
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
            state="disabled"
        )
        self.entry_selected_type.grid(row=0, column=0, sticky="nsew")
        self.entry_selected_type.bind('<FocusIn>',
                                      lambda e: self.on_entry_focus_in(self.entry_selected_type, "All"))
        self.entry_selected_type.bind('<FocusOut>', lambda e: self.on_entry_focus_out(self.entry_selected_type,
                                                                                      "All"))
        self.entry_selected_type.configure(state="readonly")

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

    def sort_column(self, column_name, order):
        if column_name in self.dict_columns_buttons:

            # Get the button corresponding to the column
            button = self.dict_columns_buttons[column_name][0]  # Assuming [0] accesses the button

            # Load the image and resize it to 15x15 pixels using PIL
            if order:  # If order is True, use descending sort icon
                image_path = "Resources/images/asc.png"
                image = Image.open(image_path)
                image = image.resize((18, 18))  # Resize image to 15x15 pixels
                sort_desc_icon = ImageTk.PhotoImage(image)
                button.configure(image=sort_desc_icon)
                button.image = sort_desc_icon  # Keep a reference to the image
            else:  # If order is False, use ascending sort icon
                image_path = "Resources/images/desc.png"
                image = Image.open(image_path)
                image = image.resize((18, 18))  # Resize image to 15x15 pixels
                sort_asc_icon = ImageTk.PhotoImage(image)
                button.configure(image=sort_asc_icon)
                button.image = sort_asc_icon  # Keep a reference to the image
        else:
            print(f"Column {column_name} not found in dict_columns_buttons!")

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

    def highlight_selected_row(self, selected_row_index, row_data):
        id = row_data.get("id")

        max_rows = len(self.frame_table_rows.grid_slaves()) // 6  # 6 columns per row

        for row_idx in range(max_rows):
            row_bg_color = "lightblue" if row_idx == selected_row_index else "white"
            if row_idx in self.selected_rows:
                row_bg_color = "lightblue"  # Keep highlighted if selected"

            else:
                row_bg_color = "white"  # Default color when not selected

            for col_widget in self.frame_table_rows.grid_slaves(row=row_idx * 2):
                if isinstance(col_widget, CTkCheckBox):
                    # Check if the checkbox is selected
                    if col_widget.get():  # If checked
                        col_widget.configure(fg_color="black")  # Set color to black if checked
                        row_bg_color = "lightblue"

                    else:
                        col_widget.configure(fg_color=row_bg_color)  # Default behavior when not checked
                else:
                    # Set color based on the row selection for non-checkbox widgets
                    col_widget.configure(fg_color=row_bg_color)

    def update_table(self, list_person_data: list):

        # Clear existing rows
        for child in self.frame_table_rows.winfo_children():
            child.destroy()

        self.current_selected_person = None
        hover_bg_color = "white"  # Define the hover background color

        def on_hover(event, row_index, row_data, is_enter):
            # Get the row ID from the row data
            id = row_data.get("id")

            # If the ID is in the selected IDs, do nothing and return early
            if id in self.selected_id:
                return  # Skip any color change or updates if the ID is in selected_id

            # Set default row background color based on hover state
            row_bg_color = hover_bg_color if is_enter else '#F0F8FF'

            # If the row is selected, keep it highlighted in lightblue
            if row_index in self.selected_rows:
                row_bg_color = "lightblue"  # Keep highlighted if selected
            else:
                # Loop through each widget in the specified row
                for col_index, row_label in enumerate(self.frame_table_rows.grid_slaves(row=row_index * 2)):
                    # Check if the widget is a CTkCheckBox
                    if isinstance(row_label, CTkCheckBox):
                        # If the checkbox is selected, don't change the color
                        if row_label.get():  # This checks if the checkbox is selected
                            continue  # Skip color change if checkbox is selected

                    # Change the background color for non-checkbox widgets
                    row_label.configure(fg_color=row_bg_color)
                # Function to handle row click

        def on_row_click(event, row_index, row_data):

            self.current_selected_row = row_index
            self.current_selected_data = row_data

            # print(f"Row {row_index} clicked: {row_data.get('full_name', 'Unknown')}")
            self.highlight_selected_row(row_index, row_data)

        for row_index, row_data in enumerate(list_person_data):
            row_bg_color = "transparent"
            full_name = row_data.get("full_name", "")
            photo = row_data.get('photo_path', "")
            id = row_data.get('id', "")

            # Create a properly sized image for display in the table
            image = None
            if photo:
                try:
                    image_data = base64.b64decode(photo)
                    pil_img = Image.open(BytesIO(image_data))
                    pil_img = pil_img.resize((100, 100), Image.LANCZOS)
                    image = CTkImage(light_image=pil_img, dark_image=pil_img, size=(100, 100))
                except Exception as e:
                    print(f"Error processing image: {e}")

            row_height = 100
            if (self.page_height > 800):
                row_height = int(self.page_height / 5) - 40

            # Display regular cell data for each column
            for col_index, (column_name, cell_data) in enumerate(row_data.items()):
                colr = 0
                if col_index > 0:
                    colr = 20
                if id in self.selected_id:
                    row_bg_color = "lightblue"
                if column_name == "status":
                    colr = 40
                if column_name == "gender":
                    colr = 30

                rows = CTkLabel(
                    self.frame_table_rows,
                    text=cell_data,
                    height=row_height,
                    fg_color=row_bg_color,
                    anchor="w",
                    font=("", 14),
                    padx=colr,
                    text_color="#2c2c2c"
                )
                rows.grid(row=row_index * 2, column=col_index, padx=0, sticky="nsew")

                # Bind hover events
                rows.bind("<Leave>", lambda event, ri=row_index, rd=row_data: on_hover(event, ri, rd, True))
                rows.bind("<Enter>", lambda event, ri=row_index, rd=row_data: on_hover(event, ri, rd, False))

                rows.bind("<Button-1>", lambda event, ri=row_index, rd=row_data: on_row_click(event, ri, rd))

                if col_index == 3:
                    break

            # Add image after the data columns
            if image:
                img_label = CTkLabel(
                    self.frame_table_rows,
                    image=image,
                    text="",
                    fg_color=row_bg_color
                )
                img_label.grid(row=row_index * 2, column=4, padx=(0, 5), sticky="nsew")

                # Bind hover events
                # img_label.bind("<Leave>", lambda event, ri=row_index: on_hover(event, ri, True))
                # img_label.bind("<Enter>", lambda event, ri=row_index: on_hover(event, ri, False))

                # # Bind click event to the image
                # img_label.bind("<Button-1>", lambda event, ri=row_index, rd=row_data: on_row_click(event, ri, rd))

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

            # Bind click event to the checkbox (optional, if you want checkbox click to also select the row)
            checkbox.bind("<Button-1>", lambda event, ri=row_index, rd=row_data: on_row_click(event, ri, rd))
            checkbox.bind("<Leave>", lambda event, ri=row_index, rd=row_data: on_hover(event, ri, rd, True))
            checkbox.bind("<Enter>", lambda event, ri=row_index, rd=row_data: on_hover(event, ri, rd, False))
            if full_name in self.selected_face_set:
                checkbox.select()

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
                height=30,
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

    def on_page_change(self):
        self.selected_rows.clear()
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
        # self.dict_filter_criteria["str_color"] = "%"

    def on_checkbox_click(self, full_name, row_data, row_index):
        id = row_data.get('id', '')
        # for x in row_data:
        #     print(x,"data")

        # print(row_data,"***************row data on chekcbox clic")

        # Check if the full_name is already in the selected set
        if full_name in self.selected_face_set:
            self.selected_face_set.remove(full_name)  # Remove from selected_face_set
            # self.selected_rows.remove(row_index)  # Remove from selected_rows (only row index)
            # self.selected_id.remove(row_data["id"])
        if row_index in self.selected_rows:
            self.selected_rows.remove(row_index)

        if id in self.selected_id:
            self.selected_id.remove(id)


        else:
            self.selected_face_set.add(full_name)  # Add to selected_face_set
            self.selected_rows.add(row_index)  # Add to selected_rows (only row index)
            self.selected_id.add(id)

        # Ensure that if the current selected person is not the one just clicked, it resets its checkbox state
        if self.current_selected_person is not None and self.current_selected_person != row_index:
            try:
                # Reset the checkbox of the previous selected row
                previous_checkbox = self.frame_table_rows.grid_slaves(row=self.current_selected_person * 2, column=5)[
                    0]
                previous_checkbox.configure(fg_color="white")  # Unhighlight the previous checkbox
            except Exception as e:
                print(e)

        # Update button states or any other relevant UI elements
        self.update_button_states()

    def reset_checkbox(self):
        self.selected_face_set.clear()
        self.update_button_states()
        self.destroy_registration_form()
        self.destroy_edit_person_form()
        # self.update_table(self.person_data)

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
        popup_height = 750
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

        self.popup.geometry(f"{popup_width}x{popup_height}+{x_position + 100}+{y_position + 50}")
        self.popup.title("Add New Face")
        # self.popup.overrideredirect(True)
        self.popup.configure(bg="#FFFFFF")
        self.popup.attributes("-topmost", True)
        self.popup.resizable(False, False)
        self.popup.protocol("WM_DELETE_WINDOW", self.on_close)

        self.popup.columnconfigure((0, 1), weight=1, uniform="a")

        data = {'vechike_name': '',
                'heading': 'Face_registration_form',
                'state': 'normal'
                }
        self.Add_Form(data, num)

    def Add_Form(self, data=[], user_id=None):
        self.i_form_width = 600  # Width of parent popup
        self.i_form_height = 750  # Increased height to accommodate new fields
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
            self.popup,
            fg_color="#D9D9D9",
            width=200,
            height=200,
            border_width=2,
            border_color="#2c2c2c",
            corner_radius=5
        )
        self.frame_photo.grid(row=1, column=0, columnspan=2, pady=(10, 0), padx=25)
        self.frame_photo.grid_propagate(False)

        # Create a frame for the upload options
        self.frame_upload_options = CTkFrame(
            self.frame_photo,
            fg_color="transparent",
        )
        self.frame_upload_options.place(relx=0.5, rely=0.5, anchor="center")

        # Upload from file button
        self.img_file_upload = CTkImage(Image.open(".\\Resources\\images\\Group 405.png"), size=(25, 25))
        self.button_file_upload = CTkButton(
            self.frame_upload_options,
            image=self.img_file_upload,
            text="From File",
            height=30,
            width=100,
            fg_color="#3A36F5",
            text_color="white",
            font=("", 12),
            cursor="hand2",
            command=self.upload_from_file,
            compound="left"
        )
        self.button_file_upload.grid(row=0, column=0, pady=(0, 10), padx=5)

        # Upload from webcam button
        self.img_webcam = CTkImage(Image.open(".\\Resources\\images\\webcam_icon.png"), size=(25, 25))
        self.button_webcam = CTkButton(
            self.frame_upload_options,
            image=self.img_webcam,
            text="From Webcam",
            height=30,
            width=100,
            fg_color="#3A36F5",
            text_color="white",
            font=("", 12),
            cursor="hand2",
            command=self.open_webcam,
            compound="left"
        )
        self.button_webcam.grid(row=1, column=0, pady=(0, 0), padx=5)

        # Load and resize default image
        image_path = "Resources\\images\\no_photo.png"
        default_image = Image.open(image_path).resize((80, 80))  # Match the frame size for perfect fit
        default_photo = ImageTk.PhotoImage(default_image)

        # Thumbnail frame for demo faces
        self.Add_thumbnail_frame = CTkFrame(
            self.popup,
            fg_color="transparent",
            height=70
        )
        self.Add_thumbnail_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=28, pady=(5, 10))

        # Create 5 thumbnail slots
        self.Add_thumb_frames = []
        self.Add_thumb_labels = []

        for i in range(5):
            # Create thumbnail frame
            Add_thumb_frame = CTkFrame(
                self.Add_thumbnail_frame,
                fg_color="#D9D9D9",  # Cleaner background
                width=80,
                height=80,
                corner_radius=5
            )
            Add_thumb_frame.grid(row=0, column=i, padx=(10,10))
            Add_thumb_frame.grid_propagate(False)

            # Create thumbnail label
            Add_thumb_label = CTkLabel(
                Add_thumb_frame,
                text="",  # No text so image takes full space
                fg_color="transparent",  # So you see only image/frame color
                width=60,
                height=60,
                corner_radius=5,
                image=default_photo,
                compound="center"  # ✅ ensures image is centered and not offset
            )
            Add_thumb_label.grid(row=0, column=0, sticky="nsew")
            Add_thumb_label.image = default_photo
            Add_thumb_label.bind("<Button-1>", lambda event, idx=i: self.thumbnail_clicked(idx))

            self.Add_thumb_frames.append(Add_thumb_frame)
            self.Add_thumb_labels.append(Add_thumb_label)

        # Store multiple images
        # self.photos = []
        self.current_photo_index = 0
        self.max_photos = 5
        self.thumbnail_labels = []

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
        self.frame_details.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=25, pady=(10, 0))

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

        self.label_middle_name = CTkLabel(
            self.frame_form_lcol,
            text="Middle Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_middle_name.grid(row=2, column=0, sticky="ew", padx=(10, 5), pady=(5, 1))

        # self.label_middle_name.grid(row=2, column=0, sticky="ew", padx=(5,10), pady=(5,1))

        self.entry_middle_name = CTkEntry(
            self.frame_form_lcol,
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
        self.entry_middle_name.grid(row=3, column=0, sticky="ew", padx=(10, 5))

        self.label_last_name = CTkLabel(
            self.frame_form_lcol,
            text="Last Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_last_name.grid(row=4, column=0, sticky="ew", padx=(10, 5), pady=(5, 1))

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
        self.entry_last_name.grid(row=5, column=0, sticky="ew", padx=(10, 5))

        # Gender Dropdown
        self.label_gender = CTkLabel(
            self.frame_form_rcol,
            text="Gender",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_gender.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=(5, 1))

        self.frame_gender_dropdown = CTkFrame(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_gender_dropdown.columnconfigure(0, weight=1)
        self.frame_gender_dropdown.grid(row=1, column=0, padx=(5, 10), sticky="ew")

        self.entry_selected_gender = CTkEntry(
            self.frame_gender_dropdown,
            height=35,
            fg_color="#F6F6F6",
            # placeholder_text="Select Gender",
            # placeholder_text_color="#828282",
            textvariable=StringVar(value="Select Gender"),
            text_color="#828282",

            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
            state="disabled"
        )
        self.entry_selected_gender.grid(row=0, column=0, sticky="nsew")
        self.entry_selected_gender.bind('<Button-1>',
                                        lambda event: self.popup_Add_dropdown(self.frame_form_rcol, self.list_gender,
                                                                              entry_destination=self.entry_selected_gender,
                                                                              i_row=2, i_rowspan=2, type=1)
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
                                                    i_row=2, i_rowspan=2, type=1)
        )
        self.button_select_gender.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)
        img_uplaod = CTkImage(Image.open(".\\Resources\\images\\Group 405.png"), size=(25, 25))

        # Status Dropdown
        self.label_status = CTkLabel(
            self.frame_form_rcol,
            text="Status",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_status.grid(row=2, column=0, sticky="ew", padx=(5, 10), pady=(5, 1))

        self.frame_status_dropdown = CTkFrame(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_status_dropdown.columnconfigure(0, weight=1)
        self.frame_status_dropdown.grid(row=3, column=0, padx=(5, 10), sticky="ew")

        self.entry_selected_status = CTkEntry(
            self.frame_status_dropdown,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value="Select Status"),
            text_color="#828282",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
            state="disabled"
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
                                                    i_row=4, i_rowspan=2, type=1)
        )
        self.button_select_status.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)

        self.label_age = CTkLabel(
            self.frame_form_rcol,
            text="Age",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_age.grid(row=4, column=0, sticky="ew", padx=(5, 10), pady=(5, 1))

        self.entry_age = CTkEntry(
            self.frame_form_rcol,
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
        self.entry_age.grid(row=5, column=0, sticky="ew", padx=(5, 10))

        self.label_error = CTkLabel(
            self.frame_details,
            text="",
            text_color="#FF0000",
            font=("", 12),
            anchor="center",
            height=15,
            wraplength=350
        )
        self.label_error.grid(column=0, row=1, columnspan=2, sticky="ew", pady=(5, 20), padx=(20, 20))

        # self.label_error = CTkLabel(
        #     self.frame_form_rcol,
        #     fg_color="transparent",
        #     text="",
        #     text_color="red",
        #     font=("", 14),
        #     height=20,
        #     anchor="w",
        #     wraplength=300
        # )
        # self.label_error.grid(row=6,columnspan=2, padx=(15,1))

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
        self.button_add_save.grid(row=4, column=0, padx=4, pady=(25, 25), sticky="e")

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
        self.button_cancel.grid(row=4, column=1, padx=4, pady=(25, 25), sticky="w")

        if hasattr(self, 'on_form_add_ready'):
            self.on_form_add_ready()

        self.bind_Add_widgets(self)
        # self.frame_form_lcol.bind('<Button-1>', self.handle_outside_click)
        # self.frame_form_rcol.bind('<Button-1>', self.handle_outside_click)
        # self.popup.bind('<Button-1>', self.handle_outside_click)

    def upload_from_file(self):
        """Handle multiple photo uploads from file (up to 4 images), storing Base64 strings."""
        # Ensure the dialog is on top and focused
        file_types = [('Image Files', '*.png *.jpg *.jpeg *.gif *.bmp *.jfif' )]

        # Use .lift() and .focus_force() to bring the dialog to the foreground
        self.popup.lift()
        self.popup.focus_force()

        # Open file dialog for multiple selection
        file_paths = filedialog.askopenfilenames(
            filetypes=file_types,
            title="Select Photos (Up to 5)",
            parent=self.popup
        )

        # Limit to a maximum of 4 images
        if file_paths:
            if len(file_paths) > self.max_photos:
                self.label_error.configure(text="You can only select up to 5 photos.")
                return

            # if len(self.photos)==5 :
            #     self.photos = []

            for file_path in file_paths:
                try:
                    # Open and resize the image
                    image = Image.open(file_path).convert('RGB')
                    image2 = image.resize((190, 190), Image.Resampling.LANCZOS)

                    # Convert the image to Base64 encoding
                    buffered = BytesIO()
                    image2.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

                    # Store the Base64 encoded image and the CTkImage for display
                    photo = CTkImage(image2, size=(190, 190))  # Used for displaying the image

                    self.photos.append({
                        "photo_base64": img_base64,  # Store Base64 encoded photo
                        "image": image,  # Store PIL Image object
                        "photo": photo  # Store CTkImage for display
                    })
                except Exception as e:
                    print(e)
                    self.label_error.configure(text=f"Error uploading photo: {str(e)}")

            # Display the first photo
            if self.photos:
                self.current_photo_index = 0
                self.display_current_photo()

    def open_webcam(self):
        """Open webcam for capturing photos directly in the photo frame"""
        # if(len(self.photos)>0):
          # self.photos.clear()
        try:
            self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                self.label_error.configure(text="Error: Could not open webcam")
                return

            # Clear existing widgets in the photo frame
            for widget in self.frame_photo.winfo_children():
                if widget != self.frame_upload_options:
                    widget.grid_forget()  # Use grid_forget instead of destroy to maintain layout integrity

            # Hide the upload options
            self.frame_upload_options.grid_forget()

            # Create video display label in the photo frame
            self.label_video = CTkLabel(
                self.frame_photo,
                text="",
                fg_color="#D9D9D9"
            )
            self.label_video.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")  # Fill the grid cell

            # Create control frame at the bottom of the photo frame
            control_frame = CTkFrame(
                self.frame_photo,
                fg_color="#D9D9D9",
                corner_radius=5
            )
            control_frame.grid(row=1, column=0, sticky="ew")  # Align controls horizontally

            # Configure grid weights for responsiveness
            self.frame_photo.grid_rowconfigure(0, weight=1)
            self.frame_photo.grid_rowconfigure(1, weight=0)
            self.frame_photo.grid_columnconfigure(0, weight=1)

            # Capture button
            self.button_capture = CTkButton(
                control_frame,
                text="Click",
                width=30,
                height=25,
                fg_color="#3A36F5",
                hover_color="#2A26C5",
                command=self.capture_image_from_webcam
            )
            self.button_capture.grid(row=0, column=0, padx=5, pady=5)

            # Status label
            self.label_capture_status = CTkLabel(
                control_frame,
                text=f"Photos: {len(self.photos)}/{self.max_photos}",
                fg_color="#3A36F5",
                text_color="white",
                width=10,
                corner_radius=5
            )
            self.label_capture_status.grid(row=0, column=1, padx=5, pady=5)

            # Done button
            self.button_done = CTkButton(
                control_frame,
                text="Close",
                width=30,
                height=25,
                fg_color="#3A36F5",
                hover_color="#2A26C5",
                command=self.close_webcam
            )
            self.button_done.grid(row=0, column=2, padx=5, pady=5)

            # Start updating webcam feed
            self.update_webcam()

        except ImportError:
            self.label_error.configure(text="Error: OpenCV (cv2) is required for webcam functionality")
        except Exception as e:
            self.label_error.configure(text=f"Error opening webcam: {str(e)}")

    def show_upload_option_temp(self):
        for widget in self.frame_photo.winfo_children():
            if widget != self.frame_upload_options:
                widget.destroy()
        self.frame_upload_options.place(relx=0.5, rely=0.5, anchor="center")

    def thumbnail_clicked(self, index):
        """Handle thumbnail click event"""
        print("clicked index is ", index)
        for widget in self.frame_photo.winfo_children():
            if widget != self.frame_upload_options:
                widget.destroy()

        # Create and pack new image label
        img_label = CTkLabel(self.frame_photo, image=self.photos[index]["photo"], text="")
        img_label.pack(expand=True)
        self.img_file_upload1= CTkImage(Image.open(".\\Resources\\images\\Group 405.png"), size=(25, 25))

        upload_button = CTkButton(
            self.frame_photo,
            image=self.img_file_upload1,
            # text="Upload",
            # font=("Helvetica", 13, "bold"),
            width=25,
            height=25,
            corner_radius=0,
            fg_color="#3A36F5",
            hover_color="#2A26C5",
            command=self.show_upload_option_temp
        )
        upload_button.place(relx=0.8, rely=0.8)

        clear_button = CTkButton(
            self.frame_photo,
            text="✖",  # Stylish cross instead of plain "X"
            font=("Helvetica", 16, "bold"),  # Custom bold font
            width=20,
            height=20,
            corner_radius=5,  # Rounded button
            fg_color="red",  # Dark gray button
            text_color="white",
            hover_color="#ff4c4c",  # Bright red on hover
            command=self.clear_photo
        )
        clear_button.place(relx=0.82, rely=0.03)

    def update_main_photo_display(self, index):
        if 0 <= index < len(self.photos):
            # self.current_photo_index = index
            self.img_label.configure(image=self.photos[index]["ctk_image_main"], text="")
            # Update thumbnails to highlight the selected one
            self.update_Add_thumbnail_display()

    def capture_image_from_webcam(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)

        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_full = Image.fromarray(frame_rgb)
        self.current_photo_index= len(self.photos)

        # Create a resized version for thumbnail (don't overwrite the original!)
        img_thumb = img_full.resize((80, 80), Image.LANCZOS)  # High-quality resize

        # Create image for UI display (thumbnail)
        thumb_photo = ImageTk.PhotoImage(img_thumb)

        if self.current_photo_index < len(self.Add_thumb_labels):
            thumb_label = self.Add_thumb_labels[self.current_photo_index]
            thumb_label.configure(image=thumb_photo, text="")
            thumb_label.image = thumb_photo

            self.label_capture_status.configure(
                text=f"Photos: {self.current_photo_index + 1}/{self.max_photos}"
            )

            # Convert full-size image to base64
            buffered = io.BytesIO()
            img_full.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Store both base64 and full-size image for display
            self.photos.append({
                "photo_base64": img_base64,
                "image": img_full,
                "photo": CTkImage(img_full, size=(190, 190))
            })

            self.current_photo_index += 1

        else:
            self.current_photo_index = 4
            thumb_label = self.Add_thumb_labels[self.current_photo_index]
            thumb_label.configure(image=thumb_photo, text="")
            thumb_label.image = thumb_photo

            self.label_capture_status.configure(
                text=f"Photos: {self.current_photo_index + 1}/{self.max_photos}"
            )

            # Convert full-size image to base64
            buffered = io.BytesIO()
            img_full.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            self.photos = self.photos[-4:]
            # Store both base64 and full-size image for display
            self.photos.append({
                "photo_base64": img_base64,
                "image": img_full,
                "photo": CTkImage(img_full, size=(190, 190))
            })


    def on_close(self):
        self.destroy_registration_form()

    def clear_photo(self):
        self.close_webcam()
        self.photos.clear()
        self.thumbnail_labels.clear()
        self.current_photo_index = 0


        for widget in self.frame_photo.winfo_children():
            if widget != self.frame_upload_options:
                widget.destroy()

        image_path = "Resources\\images\\no_photo.png"
        default_image = Image.open(image_path).resize((80, 80))
        photo = ImageTk.PhotoImage(default_image)

        for i in range(5):
            thumb_label = self.Add_thumb_labels[i]
            thumb_label.configure(image=photo, text="")
            # thumb_label.image=photo

        # Show upload options again
        self.frame_upload_options.place(relx=0.5, rely=0.5, anchor="center")

        # try:
        #     # Stop the video capturing if it exists
        #     if hasattr(self, 'cap') and self.cap is not None:
        #         self.cap.release()
        #         self.cap = None  # Clear the reference
        #
        #     # Destroy any OpenCV windows if used
        #     cv2.destroyAllWindows()
        #
        #     # Stop any after() callbacks related to webcam (if used)
        #     if hasattr(self, 'webcam_update_job'):
        #         self.frame_photo.after_cancel(self.webcam_update_job)
        #         self.webcam_update_job = None
        #
        #     # Close the webcam display window (Tkinter)
        #     if hasattr(self, 'webcam_window') and self.webcam_window.winfo_exists():
        #         self.webcam_window.destroy()
        #         self.webcam_window = None
        #
        # except Exception as e:
        #     print(f"Error closing webcam: {e}")

    def update_webcam(self):

        """Update webcam feed in the window"""
        if hasattr(self, 'label_video') and self.label_video.winfo_exists():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)

                # Get actual frame dimensions
                frame_width = self.frame_photo.winfo_width() - 20
                frame_height = self.frame_photo.winfo_height() - 60

                # Maintain aspect ratio
                img_width, img_height = img.size
                aspect_ratio = img_width / img_height

                if frame_width / frame_height > aspect_ratio:
                    # Frame is wider than needed
                    new_width = int(frame_height * aspect_ratio)
                    new_height = frame_height
                else:
                    # Frame is taller than needed
                    new_width = frame_width
                    new_height = int(frame_width / aspect_ratio)

                # Resize image
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image=img)

                # Update label
                self.label_video.configure(image=photo)
                self.label_video.image = photo

                # Schedule next update
                self.master.after(10, self.update_webcam)

            else:
                self.label_error.configure(text="Error: Could not read from webcam")
                self.close_webcam()

    # def capture_photo(self):
    #
    #     """Capture a photo from webcam and store as Base64-encoded string."""
    #     if len(self.photos) >= self.max_photos:
    #         messagebox.showinfo("Limit Reached", f"You can only capture up to {self.max_photos} photos.")
    #         return
    #
    #     ret, frame = self.cap.read()
    #     if ret:
    #         # Convert frame to PIL Image
    #         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         img = Image.fromarray(frame)
    #         img = img.resize((190, 190), Image.Resampling.LANCZOS)
    #
    #         # Convert the image to Base64 encoding
    #         buffered = io.BytesIO()
    #         img.save(buffered, format="PNG")
    #         img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")  # Base64 encoded string
    #
    #         # Add the Base64 string to the photos list (instead of file paths)
    #         self.photos.append({
    #             "photo_base64": img_base64,  # Store the Base64 encoded photo
    #             "image": img,
    #             "photo": CTkImage(img, size=(190, 190))  # Display image (if needed)
    #         })
    #
    #         # Update status
    #         self.label_capture_status.configure(text=f"Photos: {len(self.photos)}/{self.max_photos}")
    #         self.update_Add_thumbnails()
    #
    #
    #     else:
    #         messagebox.showerror("Capture Error", "Failed to capture image from webcam")

    def close_webcam(self):
        try:
            # Stop the video capturing if it exists
            if hasattr(self, 'cap') and self.cap is not None:
                self.cap.release()
                self.cap = None

            # Destroy any OpenCV windows if used

            # cv2.destroyAllWindows()

            # Stop any after() callbacks related to webcam (if used)
            if hasattr(self, 'webcam_update_job'):
                self.frame_photo.after_cancel(self.webcam_update_job)
                self.webcam_update_job = None

            # Close the webcam display window (Tkinter)
            if hasattr(self, 'webcam_window') and self.webcam_window.winfo_exists():
                self.webcam_window.destroy()
                self.webcam_window = None

            self.show_upload_option_temp()

        except Exception as e:
            print(f"Error closing webcam: {e}")


    # def photo_click_complete(self):
    #     self.close_webcam()
    #     img_label = CTkLabel(self.frame_photo, image=self.photos[0]["photo"], text="")
    #     img_label.pack(expand=True)

    def display_current_photo(self):
        self.update_Add_thumbnails()

        """Display the current photo in the photo frame"""
        if not self.photos:
            return

        if len(self.photos) > 5:
            self.photos = self.photos[-5:]

        # Clear existing widgets
        for widget in self.frame_photo.winfo_children():
            if widget != self.frame_upload_options:
                widget.destroy()

        # Hide the upload options
        self.frame_upload_options.place_forget()

        # Get current photo
        photo_data = self.photos[self.current_photo_index]

        # Display photo
        photo_label = CTkLabel(
            self.frame_photo,
            image=photo_data["photo"],
            text="",
            fg_color="transparent"
        )
        photo_label.place(relx=0.5, rely=0.5, anchor="center")

        for i in range(5):
            thumb_label = self.Add_thumb_labels[i]
            original_pil_image = self.photos[i]['image']  # ✅ correct: this is a PIL image

            resized_pil_image = original_pil_image.resize((80, 80), Image.LANCZOS)
            resized_ctk_image = CTkImage(resized_pil_image, size=(80, 80))

            thumb_label.configure(image=resized_ctk_image, text="")
            thumb_label.image = resized_ctk_image  # ✅ keep reference to avoid garbage collection

        # # # Create navigation frame
        # nav_frame = CTkFrame(
        #     self.frame_photo,
        #     fg_color="transparent",
        #     corner_radius=5
        # )
        # nav_frame.place(relx=0.2, rely=0.9, anchor="center")


        upload_button = CTkButton(
            self.frame_photo,
            image=self.img_file_upload,
            # text="Upload",
            # font=("Helvetica", 13, "bold"),
            width=25,
            height=25,
            corner_radius=0,
            fg_color="#3A36F5",
            hover_color="#2A26C5",
            command=self.show_upload_option_temp
        )
        upload_button.place(relx=0.8, rely=0.8)

        clear_button = CTkButton(
            self.frame_photo,
            text="✖",  # Stylish cross instead of plain "X"
            font=("Helvetica", 16, "bold"),  # Custom bold font
            width=20,
            height=20,
            corner_radius=5,  # Rounded button
            fg_color="red",  # Dark gray button
            text_color="white",
            hover_color="#ff4c4c",  # Bright red on hover
            command=self.clear_photo
        )
        clear_button.place(relx=0.82, rely=0.03)

        # # Photo counter
        # counter_label = CTkLabel(
        #     nav_frame,
        #     text=f"{self.current_photo_index + 1}/{self.photolength}",
        #     fg_color="#3A36F5",
        #     text_color="white",
        #     width=50
        # )
        # counter_label.grid(row=0, column=1)

        # # Next button
        # if len(self.photos) > 1:
        #     next_button = CTkButton(
        #         nav_frame,
        #         text=">",
        #         width=30,
        #         height=25,
        #         fg_color="#3A36F5",
        #         hover_color="#2A26C5",
        #         command=self.next_photo
        #     )
        #     next_button.grid(row=0, column=2, padx=(0, 2))

        # # Add image button
        # add_button = CTkButton(
        #     nav_frame,
        #     text="",
        #     width=30,
        #     height=25,
        #     fg_color="red",
        #     hover_color="#2A26C5",
        #     command=self.show_upload_options
        # )
        # add_button.grid(row=0, column=3, padx=(5, 2))
        # self.update_Add_thumbnails()

        # """Show the previous photo"""
        # if self.photos:
        #     self.current_photo_index = (self.current_photo_index - 1) % len(self.photos)
        #     self.display_current_photo()

    # def next_photo(self):
    #     """Show the next photo"""
    #     if self.photos:
    #         self.current_photo_index = (self.current_photo_index + 1) % len(self.photos)
    #         self.display_current_photo()

    # def show_upload_options(self):
    #     """Show the upload options"""
    #     # Clear existing widgets except frame_upload_options
    #     # self.photos.clear()
    #     for widget in self.frame_photo.winfo_children():
    #         if widget != self.frame_upload_options:
    #             widget.destroy()
    #
    #     # Show the upload options
    #     self.frame_upload_options.place(relx=0.5, rely=0.5, anchor="center")

    # Modify the original upload_photo method to call upload_from_file
    # def upload_photo(self):
    #     self.upload_from_file()

    def close_active_dropdown(self, event=None):
        """Helper method to close the currently active dropdown"""
        if self.active_dropdown_frame and self.active_dropdown_frame.winfo_exists():
            self.active_dropdown_frame.grid_forget()

        self.active_dropdown_frame = None
        self.current_open_dropdown = None

    # def close_dropdown(self, event):
    #     # self.frame_maindropdown_window.grid_forget()
    #     if(self.active_dropdown_frame != None):
    #      self.active_dropdown_frame.grid_forget()
    #      self.active_dropdown_frame = None
    #      self.current_open_dropdown = None
    def get_all_children(self, parent):
        children = parent.winfo_children()
        all_children = [] + children
        for child in children:
            all_children.extend(self.get_all_children(child))
        return all_children

    def bind_Add_widgets(self, parent):
        self.list_widgets = self.get_all_children(parent)

        for widget in self.list_widgets:
            if (widget == self.button_select_gender or widget == self.button_select_status):
                continue
            if isinstance(widget, (CTkLabel, CTkButton, CTkFrame, CTkEntry)):
                widget.bind("<Button-1>", self.close_active_dropdown)

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
                    height=42,
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

            for index, row_data in enumerate(list_data):
                button_options = CTkButton(
                    frame_Add_popup_table,
                    text=f"    {row_data}",
                    height=30,
                    fg_color="transparent",
                    text_color="#414141",
                    font=("", 14),
                    corner_radius=0,
                    hover_color="#e6e6ff",
                    anchor="w",
                    command=lambda selected_option=row_data: self.select_option(selected_option, entry_destination,
                                                                                frame_Add_maindropdown_window)
                )
                button_options.grid(row=index, column=0, sticky="nsew", padx=1)

                # Show the dropdown
                frame_Add_maindropdown_window.grid_propagate(False)
                frame_Add_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(5, 7),
                                                   pady=(0, 0))
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

        if dropdown_frame.winfo_exists():
            dropdown_frame.grid_forget()
            self.active_dropdown_frame = None
            self.bool_dropdown_opened = False

    def update_Add_thumbnails(self):
        """Update the 5 thumbnail preview images."""

        # Store image references to prevent garbage collection
        self.thumbnail_images = []

        for i in range(5):
            # if i < len(self.photos):
                # Get photo from list and resize
                if isinstance(self.photos[i], dict):
                    img = self.photos[i]["image"]  # Assuming PIL.Image
                else:
                    img = self.photos[i]

                resized_img = img.resize((60, 60), Image.Resampling.LANCZOS)

                # Create CTkImage and store in reference list
                ctk_img = CTkImage(light_image=resized_img, dark_image=resized_img, size=(80, 80))
                self.thumbnail_images.append(ctk_img)

                self.Add_thumb_labels[i].configure(image=ctk_img, text="")
                self.Add_thumb_labels[i].image = ctk_img  # Optional but safe

            # else:
            #     # Clear remaining thumbnails
            #     self.Add_thumb_labels[i].configure(image=None, text="")
            #     self.Add_thumb_labels[i].image = None

    def thumbnail_Add_clicked(self, index):
        """Handle thumbnail click: swap photo to main frame or show upload options"""
        if index < len(self.photos):
            self.current_Add_photo_index = index
            self.display_Add_current_photo()
        else:
            self.show_Add_upload_options()

    def display_Add_current_photo(self):
        """Display the current photo in the main photo frame"""
        if not self.photos:
            self.img_label.configure(image=None, text="No image available")
            self.frame_upload_options.place(relx=0.5, rely=0.5, anchor="center")
            self.update_thumbnails()
            return

        # Hide upload options
        self.frame_upload_options.place_forget()

        # Display the current photo
        photo_data = self.photos[self.current_Add_photo_index]
        self.img_label.configure(image=photo_data["photo"], text="")
        self.update_thumbnails()

    # def edit_reset(self, person=[]):
    #     # Use initial_values if person is not provided
    #     if not person and hasattr(self, 'initial_values'):
    #         person = self.initial_values
    #
    #     # Ensure that person is valid
    #     if not person:
    #         return
    #
    #     self.entry_edit_number.configure(state="normal")
    #     self.entry_edit_number.delete(0, "end")
    #     self.entry_edit_number.insert(0, person.get("person_number", ""))
    #     self.entry_edit_number.configure(state="disabled")
    #     self.entry_edit_number.configure(border_color="#DEDEDE")  # Reset border color to default
    #     self.label_error.configure(text="")
    #
    #     # Reset the status field
    #     self.entry_edit_selected_status.configure(state="normal")
    #     self.entry_edit_selected_status.delete(0, "end")
    #     self.entry_edit_selected_status.insert(0, "white-list" if person.get("person_status") == 0 else "black-list")
    #     self.entry_edit_selected_status.configure(state="disabled")
    #     self.entry_edit_selected_status.configure(border_color="#DEDEDE")  # Reset border color to default
    #     self.label_error.configure(text="")
    #
    #     # Reset the company field
    #     self.entry_edit_selected_company.configure(state="normal")
    #     self.entry_edit_selected_company.delete(0, "end")
    #     self.entry_edit_selected_company.insert(0, person.get("person_company", ""))
    #     self.entry_edit_selected_company.configure(border_color="#DEDEDE")  # Reset border color to default
    #     self.label_error.configure(text="")
    #
    #     # Reset the type field
    #     self.entry_edit_type.configure(state="normal")
    #     self.entry_edit_type.delete(0, "end")
    #     self.entry_edit_type.insert(0, person.get("person_type", ""))
    #     self.entry_edit_type.configure(border_color="#DEDEDE")  # Reset border color to default
    #     self.label_error.configure(text="")
    #
    #     # Reset the model field
    #     self.entry_edit_model.configure(state="normal")
    #     self.entry_edit_model.delete(0, "end")
    #     self.entry_edit_model.insert(0, person.get("person_model", ""))
    #     self.entry_edit_model.configure(border_color="#DEDEDE")  # Reset border color to default
    #     self.label_error.configure(text="")
    #
    #     # Reset the color field
    #     self.entry_edit_color.configure(state="normal")
    #     self.entry_edit_color.delete(0, "end")
    #     self.entry_edit_color.insert(0, person.get("person_color", ""))
    #     self.entry_edit_color.configure(border_color="#DEDEDE")  # Reset border color to default
    #     self.label_error.configure(text="")
    #
    #     # Reset the manufacturing year field
    #     self.entry_edit_date.configure(state="normal")
    #     self.entry_edit_date.delete(0, "end")
    #     self.entry_edit_date.insert(0, person.get("manufacturing_year", ""))
    #     self.entry_edit_date.configure(border_color="#DEDEDE")  # Reset border color to default
    #     self.label_error.configure(text="")
    #
    #     # Reset the owner field
    #     self.entry_edit_owner.configure(state="normal")
    #     self.entry_edit_owner.delete(0, "end")
    #     self.entry_edit_owner.insert(0, person.get("person_owner", ""))
    #     self.entry_edit_owner.configure(border_color="#DEDEDE")  # Reset border color to default
    #     self.label_error.configure(text="")

    def destroy_registration_form(self):
        self.close_webcam()

        """Helper method to destroy the add person form."""
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()  # Destroy the popup (form) window
            self.photos.clear()

    def destroy_edit_person_form(self):
        """Helper method to destroy the add person form."""
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()  # Destroy the popup (form) window

    # ___________________________________________________________________[edit vechile]_______________________________________________________________________________________

    def edit_selected_person(self):
        """Handle editing of selected camera and ensure proper state reset"""
        if len(self.selected_face_set) == 1:
            Name = next(iter(self.selected_face_set))

            self.person = next((cam for cam in self.person_data if cam['full_name'] == Name), None)

            if self.person:
                self.edit_Face_Form(self.person)
                # self.edit_reset_vechile(person)

    def edit_Face_Form(self, person=None):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        popup_width = 600
        popup_height = 750
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

        # self.popup.geometry(f"{popup_width}x{popup_height}+{x_position+200}+{y_position+150}")
        self.popup.geometry(f"{popup_width}x{popup_height}+{x_position + 100}+{y_position + 50}")

        self.popup.title("Edit Face")
        # self.popup.overrideredirect(True)
        self.popup.configure(bg="#FFFFFF")
        self.popup.attributes("-topmost", True)
        self.popup.resizable(False, False)

        self.popup.columnconfigure((0, 1), weight=1, uniform="a")
        self.popup.protocol("WM_DELETE_WINDOW", self.on_close)

        self.edit_vechile(person)

    def edit_vechile(self, person):
        self.upload_target_index = 0

        self.i_form_width = 600  # Width of parent popup
        self.i_form_height = 750  # Increased height to accommodate new fields
        self.bool_dropdown_opened = False
        self.list_gender = ["Male", "Female", "Other"]
        self.list_status = ["WhiteList", "BlackList"]
        self.current_open_button = None
        self.photo_path = None

        photo = person.get('photo_path', "")
        self.old_photo = person.get('photo_path', "")

        # Main heading
        self.Edit_label_heading = CTkLabel(
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

        # Get all photos from person data
        photo_keys = [
            person.get('photo_path', ""),
            person.get('photo_path2', ""),
            person.get('photo_path3', ""),
            person.get('photo_path4', ""),
            person.get('photo_path5', "")
        ]

        # Count valid photos
        self.photolength = 0
        for photo_path in photo_keys:
            if photo_path is not None and photo_path != "":
                self.photolength += 1

        print("total image get is ", self.photolength, "-----------------------------------------------")

        # Initialize photo navigation variables
        self.Edit_photos = []
        self.current_Edit_photo_index = 0
        self.Edit_max_photos = 5  # Maximum number of photos allowed

        # Process existing photos from person data
        for i, encoded_photo in enumerate(photo_keys):
            if encoded_photo and encoded_photo != "":
                try:
                    # Decode base64 image
                    image_data = base64.b64decode(encoded_photo)
                    pil_img = Image.open(BytesIO(image_data))

                    # Resize image for main display
                    pil_img_main = pil_img.resize((190, 190), Image.LANCZOS)
                    ctk_img_main = CTkImage(light_image=pil_img_main, dark_image=pil_img_main, size=(190, 190))

                    # Resize image for thumbnail
                    pil_img_thumb = pil_img.resize((60, 60), Image.LANCZOS)
                    ctk_img_thumb = CTkImage(light_image=pil_img_thumb, dark_image=pil_img_thumb, size=(80, 80))

                    # Add to the photos list
                    self.Edit_photos.append({
                        "photo_base64": encoded_photo,
                        "image": pil_img,
                        "ctk_image_main": ctk_img_main,
                        "ctk_image_thumb": ctk_img_thumb,
                        "index": i
                    })
                except Exception as e:
                    print(f"Error processing image: {e}")

        # Create main photo frame
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
        self.Edit_frame_photo.grid_propagate(False)

        # Configure grid for main photo frame
        self.Edit_frame_photo.columnconfigure(0, weight=1)
        self.Edit_frame_photo.rowconfigure(0, weight=1)

        # Image label to display current photo
        self.Edit_img_label = CTkLabel(
            self.Edit_frame_photo,
            text="",
            fg_color="#D9D9D9",
            corner_radius=5
        )
        self.Edit_img_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        update_Edit_button = CTkButton(
            self.Edit_frame_photo,
            text="Upload",
            font=("Helvetica", 13, "bold"),
            width=80,
            height=25,
            corner_radius=0,
            fg_color="#3A36F5",
            hover_color="#2A26C5",
            command=self.onclick_update_btn_edit_form
        )
        update_Edit_button.place(relx=0.3, rely=0.8)

        # clear_Edit_button = CTkButton(
        #    self.Edit_frame_photo,
        #     text="✖",  # Stylish cross instead of plain "X"
        #     font=("Helvetica", 16, "bold"),  # Custom bold font
        #     width=20,
        #     height=20,
        #     corner_radius=5,  # Rounded button
        #     fg_color="red",  # Dark gray button
        #     text_color="white",
        #     hover_color="#ff4c4c",  # Bright red on hover
        #     command=self.clear_photo
        # )
        # clear_Edit_button.place(relx=0.82, rely=0.03)

        # Create thumbnail frame below main photo
        self.Edit_thumbnail_frame = CTkFrame(
            self.popup,
            fg_color="transparent",
            height=70
        )
        self.Edit_thumbnail_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=25, pady=(5, 10))

        # Create 5 thumbnail slots
        self.thumb_frames = []
        self.thumb_labels = []

        for i in range(5):
            # Create thumbnail frame
            thumb_frame = CTkFrame(
                self.Edit_thumbnail_frame,
                fg_color="#D9D9D9",
                width=80,
                height=80,
                border_width=1,
                border_color="#2c2c2c",
                corner_radius=5
            )
            thumb_frame.grid(row=0, column=i,  padx=(10,20))
            thumb_frame.grid_propagate(False)

            # Create thumbnail label
            thumb_label = CTkLabel(
                thumb_frame,
                text="",
                fg_color="#D9D9D9",
                corner_radius=5
            )
            thumb_label.grid(row=0, column=0, sticky="nsew")
            thumb_label.bind("<Button-1>", lambda event, idx=i: self.thumbnail_Edit_clicked(idx))

            self.thumb_frames.append(thumb_frame)
            self.thumb_labels.append(thumb_label)

        # Create hidden replacement options frame

        # # Cancel button
        # self.Edit_button_cancel_replace = CTkButton(
        #     self.Edit_replace_options,
        #     text="Cancel",
        #     width=70,
        #     height=30,
        #     fg_color="#6C757D",
        #     hover_color="#5C656D",
        #     # command=self.hide_Edit_replace_options
        # )
        # self.Edit_button_cancel_replace.grid(row=0, column=2, padx=5, pady=5)

        # Main details frame
        self.Edit_frame_details = CTkFrame(
            self.popup,
            fg_color="transparent",
            border_color="#D2D2D2",
            border_width=2,
            corner_radius=5,
        )
        self.Edit_frame_details.columnconfigure((0, 1), weight=1, uniform="a")
        self.Edit_frame_details.rowconfigure(0, weight=1)
        self.Edit_frame_details.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=25, pady=(10, 0))

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

        full_name = person.get("full_name", "")

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
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Edit_entry_first_name.grid(row=1, column=0, sticky="ew", padx=(10, 5))

        self.Edit_label_middle_name = CTkLabel(
            self.frame_form_lcol,
            text="Middle Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_middle_name.grid(row=2, column=0, sticky="ew", padx=(10, 5), pady=(5, 1))

        self.Edit_entry_middle_name = CTkEntry(
            self.frame_form_lcol,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value=middle_name),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Edit_entry_middle_name.grid(row=3, column=0, sticky="ew", padx=(10, 5))

        self.Edit_label_last_name = CTkLabel(
            self.frame_form_lcol,
            text="Last Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_last_name.grid(row=4, column=0, sticky="ew", padx=(10, 5), pady=(5, 1))

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
        self.Edit_entry_last_name.grid(row=5, column=0, sticky="ew", padx=(10, 5))

        # Gender Dropdown
        self.Edit_label_gender = CTkLabel(
            self.frame_form_rcol,
            text="Gender",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_gender.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=(5, 1))

        self.Edit_frame_gender_dropdown = CTkFrame(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.Edit_frame_gender_dropdown.columnconfigure(0, weight=1)
        self.Edit_frame_gender_dropdown.grid(row=1, column=0, padx=(5, 10), sticky="ew")

        self.Edit_entry_selected_gender = CTkEntry(
            self.Edit_frame_gender_dropdown,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value=person["gender"]),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
            state="disabled"
        )
        self.Edit_entry_selected_gender.grid(row=0, column=0, sticky="nsew")
        self.Edit_entry_selected_gender.bind('<Button-1>',
                                             lambda event: self.popup_Edit_dropdown(self.frame_form_rcol,
                                                                                    self.list_gender,
                                                                                    entry_destination=self.Edit_entry_selected_gender,
                                                                                    i_row=2, i_rowspan=2, type=1)
                                             )

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
                                                     i_row=2, i_rowspan=2, type=1)
        )
        self.Edit_button_select_gender.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)
        img_uplaod = CTkImage(Image.open(".\\Resources\\images\\Group 405.png"), size=(25, 25))

        # Status Dropdown
        self.Edit_label_status = CTkLabel(
            self.frame_form_rcol,
            text="Status",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_status.grid(row=2, column=0, sticky="ew", padx=(5, 10), pady=(5, 1))

        self.Edit_frame_status_dropdown = CTkFrame(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.Edit_frame_status_dropdown.columnconfigure(0, weight=1)
        self.Edit_frame_status_dropdown.grid(row=3, column=0, padx=(5, 10), sticky="ew")

        self.Edit_entry_selected_status = CTkEntry(
            self.Edit_frame_status_dropdown,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value=person["status"]),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
            state="disabled"
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
                                                     i_row=4, i_rowspan=2, type=1)
        )
        self.Edit_button_select_status.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)

        self.Edit_label_age = CTkLabel(
            self.frame_form_rcol,
            text="Age",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.Edit_label_age.grid(row=4, column=0, sticky="ew", padx=(5, 10), pady=(5, 1))

        self.Edit_entry_age = CTkEntry(
            self.frame_form_rcol,
            height=35,
            fg_color="#F6F6F6",
            textvariable=StringVar(value=person["age"]),
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.Edit_entry_age.grid(row=5, column=0, sticky="ew", padx=(5, 10))

        self.Edit_label_error = CTkLabel(
            self.Edit_frame_details,
            text="",
            text_color="#FF0000",
            font=("", 12),
            anchor="center",
            height=15,
            wraplength=350
        )
        self.Edit_label_error.grid(column=0, row=1, columnspan=2, sticky="ew", pady=(5, 20), padx=(20, 20))

        self.Edit_button_add_save = CTkButton(
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
        self.Edit_button_add_save.grid(row=4, column=0, padx=4, pady=(25, 25), sticky="e")

        self.Edit_button_cancel = CTkButton(
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
        self.Edit_button_cancel.grid(row=4, column=1, padx=4, pady=(25, 25), sticky="w")

        # Initialize thumbnail display
        self.update_Edit_thumbnail_display()

        # Initialize main photo display
        if self.Edit_photos:
            self.update_Edit_main_photo_display(0)

        if hasattr(self, 'on_form_add_ready'):
            self.on_form_edit_ready()

        # self.bind_widgets(self)

    def get_all_children(self, parent):
        children = parent.winfo_children()
        all_children = [] + children
        for child in children:
            all_children.extend(self.get_all_children(child))
        return all_children

    def bind_widgets(self, parent):
        self.list_widgets = self.get_all_children(parent)

        for widget in self.list_widgets:
            if (widget == self.Edit_button_select_gender or widget == self.Edit_button_select_status):
                continue
            if isinstance(widget, (CTkLabel, CTkButton, CTkFrame, CTkEntry)):
                widget.bind("<Button-1>", self.close_active_dropdown)

    def close_active_dropdown(self, event=None):
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
                    height=50,
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
                    height=48,
                    width=28,
                    corner_radius=5
                )
                frame_Edit_popup_table.columnconfigure(0, weight=1)
                # frame_Edit_popup_table.grid(row=0, column=0, columnspan=2, padx=(10, 10), pady=(1, 3), sticky="nsew")
                frame_Edit_popup_table.grid(row=0, column=0, columnspan=2, padx=(1, 4), pady=(1, 0), sticky="nsew")

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
                        height=28,
                        fg_color="transparent",
                        text_color="#414141",
                        font=("", 14),
                        corner_radius=0,
                        hover_color="#e6e6ff",
                        anchor="w",
                        command=lambda selected_option=row_data: self.Edit_select_option(selected_option,
                                                                                         entry_destination,
                                                                                         frame_Edit_maindropdown_window)
                    )
                    button_options.grid(row=index, column=0, sticky="nsew", padx=1)

                # Show the dropdown
                frame_Edit_maindropdown_window.grid_propagate(False)
                # frame_Edit_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(14, 7), pady=(5, 0))
                frame_Edit_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, sticky="nsew", padx=(5, 7),
                                                    pady=(0, 0))

                frame_Edit_maindropdown_window.tkraise()

                # Update state tracking variables to manage the currently open dropdown
                self.current_open_dropdown = entry_destination
                self.active_dropdown_frame = frame_Edit_maindropdown_window

    def update_Edit_thumbnail_display(self):
        """Update all thumbnail images"""
        for i in range(5):
            self.thumb_labels[i].configure(image=None, text="")
            if i < self.photolength:
                self.thumb_labels[i].configure(image=self.Edit_photos[i]["ctk_image_thumb"], text="")
                self.thumb_labels[i].image = self.Edit_photos[i]["ctk_image_thumb"]  # Keep reference
                if i == self.current_Edit_photo_index:
                    self.thumb_frames[i].configure(border_color="#3A36F5", border_width=2)
                else:
                    self.thumb_frames[i].configure(border_color="#2c2c2c", border_width=1)
            elif i == self.photolength:
                upload_icon = CTkImage(Image.open(".\\Resources\\images\\Group 405.png"), size=(25, 25))
                self.thumb_labels[i].configure(image=upload_icon, text="Upload")
                self.thumb_labels[i].bind("<Button-1>", lambda event, idx=i: self.show_Edit_upload_options(idx))


    def update_Edit_main_photo_display(self, index):
        if 0 <= index < len(self.Edit_photos):
            self.current_Edit_photo_index = index
            if not hasattr(self, "Edit_img_label"):
                self.Edit_img_label = CTkLabel(
                    self.Edit_frame_photo,
                    text="",
                    fg_color="#D9D9D9",
                    corner_radius=5
                )
                self.Edit_img_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.Edit_img_label.configure(image=self.Edit_photos[index]["ctk_image_main"], text="")
            self.Edit_img_label.image = self.Edit_photos[index][
                "ctk_image_main"]  # Keep reference to avoid garbage collection
            self.update_Edit_thumbnail_display()


    def thumbnail_Edit_clicked(self, index):
        self.upload_target_index = index
        """Handle thumbnail click event"""
        if index < self.photolength:
            # If clicking on a photo thumbnail, update the main display
            self.update_Edit_main_photo_display(index)
        else:
            # If clicking on the upload button or empty space, show upload options
            self.show_Edit_upload_options(index)

    def show_Edit_upload_options(self, index):
        """Show upload options for the specified thumbnail index"""
        # Store the index where we want to add the new photo
        self.upload_target_index = index

        # Position the upload options frame over the thumbnail
        self.Edit_replace_options.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Show upload options in a dialog or near the thumbnail
        self.Edit_replace_options.place(
            in_=self.thumb_frames[index],
            anchor="center",
            relx=0.5,
            rely=0.5
        )

        self.Edit_replace_options.lift()  # Bring to front

    def hide_replace_options(self):
        """Hide the replacement options"""
        self.Edit_replace_options.place_forget()

    def upload_Edit_photo(self):
        file_types = [('Image Files', '*.png *.jpg *.jpeg *.gif *.bmp *.jfif')]
        self.popup.lift()
        self.popup.focus_force()
        file_path = filedialog.askopenfilename(filetypes=file_types, title="Select Photo", parent=self.popup)
        if file_path:
            try:
                image = Image.open(file_path)
                img_main = image.resize((190, 190), Image.Resampling.LANCZOS)
                ctk_img_main = CTkImage(light_image=img_main, dark_image=img_main, size=(190, 190))
                img_thumb = image.resize((80, 80), Image.Resampling.LANCZOS)
                ctk_img_thumb = CTkImage(light_image=img_thumb, dark_image=img_thumb, size=(80, 80))
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                print(f"Uploaded photo: {file_path}, base64 length: {len(img_base64)}")  # Log success
                if self.upload_target_index < len(self.Edit_photos):
                    self.Edit_photos[self.upload_target_index] = {
                        "photo_base64": img_base64,
                        "image": image,
                        "ctk_image_main": ctk_img_main,
                        "ctk_image_thumb": ctk_img_thumb,
                        "index": self.upload_target_index
                    }
                else:
                    self.Edit_photos.append({
                        "photo_base64": img_base64,
                        "image": image,
                        "ctk_image_main": ctk_img_main,
                        "ctk_image_thumb": ctk_img_thumb,
                        "index": len(self.Edit_photos)
                    })
                    self.photolength += 1
                print(f"Edit_photos length: {len(self.Edit_photos)}")  # Log photo list
                self.update_Edit_thumbnail_display()
                self.update_Edit_main_photo_display(self.upload_target_index)
                self.clear_updated_photo_from_edit_frame()
            except Exception as e:
                print(f"Error in upload_Edit_photo: {e}")
                self.Edit_label_error.configure(text=f"Error uploading photo: {str(e)}")
            # """Upload a new photo from file"""



    def open_edit_webcam(self):
        try:
            self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                self.Edit_label_error.configure(text="Error: Could not open webcam")
                return

            # Clear existing widgets in Edit_frame_photo, except Edit_frame_photo itself
            for widget in self.Edit_frame_photo.winfo_children():
                if widget != self.Edit_frame_photo:
                    widget.grid_forget()

            # Hide update_Edit_button explicitly
            if hasattr(self, "update_Edit_button") and self.update_Edit_button.winfo_exists():
                self.update_Edit_button.place_forget()

            # Ensure Edit_frame_photo is visible
            self.Edit_frame_photo.grid(row=1, column=0, columnspan=2, pady=(0, 0), padx=25)

            # Configure grid weights to prioritize video feed
            self.Edit_frame_photo.grid_rowconfigure(0, weight=1)
            self.Edit_frame_photo.grid_columnconfigure(0, weight=1)

            # Create video display label to fill the frame
            self.label_video = CTkLabel(
                self.Edit_frame_photo,
                text="",
                fg_color="#D9D9D9",
                corner_radius=5
            )
            self.label_video.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

            # Capture button
            self.button_Edit_capture = CTkButton(
                self.Edit_frame_photo,
                text="Click",
                width=80,
                height=25,
                fg_color="#3A36F5",
                hover_color="#2A26C5",
                text_color="white",
                corner_radius=5,
                command=self.capture_image_from_Edit_webcam
            )
            self.button_Edit_capture.place(relx=0.25, rely=0.85, anchor="center")

            # Cancel button
            self.button_Edit_done = CTkButton(
                self.Edit_frame_photo,
                text="Cancel",
                width=80,
                height=25,
                fg_color="#6C757D",  # Gray to distinguish from Click
                hover_color="#5C656D",
                text_color="white",
                command=self.close_Edit_webcam
            )
            self.button_Edit_done.place(relx=0.75, rely=0.85, anchor="center")

            # Start updating webcam feed
            self.update_Edit_webcam_feed()

        except ImportError:
            self.Edit_label_error.configure(text="Error: OpenCV (cv2) is required for webcam functionality")
        except Exception as e:
            self.Edit_label_error.configure(text=f"Error opening webcam: {str(e)}")

    def update_Edit_webcam_feed(self):
        """Update the webcam feed in the Edit_frame_photo"""
        if hasattr(self, 'cap') and self.cap.isOpened() and hasattr(self, 'label_video'):
            ret, frame = self.cap.read()
            if ret:
                # Convert frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert to PIL Image
                img = Image.fromarray(frame_rgb)

                # Resize to match main display size
                img = img.resize((190, 190), Image.Resampling.LANCZOS)

                # Convert to CTkImage
                ctk_img = CTkImage(light_image=img, dark_image=img, size=(190, 190))

                # Update the label
                self.label_video.configure(image=ctk_img)

                # Keep reference to prevent garbage collection
                self.label_video.image = ctk_img

                # Schedule next update
                self.Edit_frame_photo.after(10, self.update_Edit_webcam_feed)
            else:
                self.close_webcam()

    def capture_image_from_Edit_webcam(self):
        """Capture a single photo from the webcam and update Edit_photos at upload_target_index"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                try:
                    # Convert frame to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Convert to PIL Image
                    img = Image.fromarray(frame_rgb)

                    # Resize for main display
                    img_main = img.resize((190, 190), Image.Resampling.LANCZOS)
                    ctk_img_main = CTkImage(light_image=img_main, dark_image=img_main, size=(190, 190))

                    # Resize for thumbnail
                    img_thumb = img.resize((60, 60), Image.Resampling.LANCZOS)
                    ctk_img_thumb = CTkImage(light_image=img_thumb, dark_image=img_thumb, size=(80, 80))

                    # Convert to base64 for storage
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()

                    # Update Edit_photos at upload_target_index
                    photo_data = {
                        "photo_base64": img_base64,
                        "image": img,
                        "ctk_image_main": ctk_img_main,
                        "ctk_image_thumb": ctk_img_thumb,
                        "index": self.upload_target_index
                    }

                    if self.upload_target_index < len(self.Edit_photos):
                        # Replace existing photo
                        self.Edit_photos[self.upload_target_index]['photo_base64'] = photo_data.get('photo_base64')
                        self.Edit_photos[self.upload_target_index]['image'] = photo_data.get('image')
                        self.Edit_photos[self.upload_target_index]['ctk_image_main'] = photo_data.get('ctk_image_main')
                        self.Edit_photos[self.upload_target_index]['ctk_image_thumb'] = photo_data.get(
                            'ctk_image_thumb')
                        self.Edit_photos[self.upload_target_index]['index'] = photo_data.get('index')
                        self.update_Edit_thumbnail_display()
                        self.update_Edit_main_photo_display(self.upload_target_index)
                        self.close_Edit_webcam()
                    else:
                        # Add new photo
                        self.Edit_photos.append(photo_data)
                        self.photolength = len(self.Edit_photos)

                    print(f"Captured photo at index {self.upload_target_index}")

                    # Close webcam after capture
                    self.close_webcam()

                except Exception as e:
                    self.Edit_label_error.configure(text=f"Error capturing photo: {str(e)}")
                    print(f"Error capturing photo: {e}")
            else:
                self.Edit_label_error.configure(text="Error: Failed to capture image")
                self.close_Edit_webcam()

    def close_Edit_webcam(self):
        """Close the webcam and restore the Edit_frame_photo UI"""
        # Release webcam
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            print("Webcam released")

        # Clear webcam-related widgets
        if hasattr(self, 'label_video') and self.label_video.winfo_exists():
            self.label_video.grid_forget()
            print("label_video removed")
        if hasattr(self, 'button_Edit_capture') and self.button_Edit_capture.winfo_exists():
            self.button_Edit_capture.place_forget()
            print("button_Edit_capture removed")
        if hasattr(self, 'button_Edit_done') and self.button_Edit_done.winfo_exists():
            self.button_Edit_done.place_forget()
            print("button_Edit_done removed")

        # Restore Edit_img_label
        if not hasattr(self, "Edit_img_label") or not self.Edit_img_label.winfo_exists():
            self.Edit_img_label = CTkLabel(
                self.Edit_frame_photo,
                text="",
                fg_color="#D9D9D9",
                corner_radius=5
            )
        self.Edit_img_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        print("Edit_img_label restored")

        # Restore update_Edit_button
        if not hasattr(self, "update_Edit_button") or not self.update_Edit_button.winfo_exists():
            self.update_Edit_button = CTkButton(
                self.Edit_frame_photo,
                text="Upload",
                font=("Helvetica", 13, "bold"),
                width=80,
                height=25,
                corner_radius=0,
                fg_color="#3A36F5",
                hover_color="#2A26C5",
                command=self.onclick_update_btn_edit_form
            )
        self.update_Edit_button.place(relx=0.3, rely=0.8)
        print("update_Edit_button restored")

        # Update main and thumbnail displays
        if self.Edit_photos:
            self.update_Edit_main_photo_display(self.upload_target_index)
            self.update_Edit_thumbnail_display()
        else:
            self.Edit_img_label.configure(image=None, text="No Image")
        print(f"Edit_photos length: {len(self.Edit_photos)}, current index: {self.upload_target_index}")

        # Reset grid configuration
        self.Edit_frame_photo.grid_rowconfigure(0, weight=1)
        self.Edit_frame_photo.grid_columnconfigure(0, weight=1)
        self.Edit_frame_photo.grid(row=1, column=0, columnspan=2, pady=(0, 0), padx=25)

        # Force UI refresh
        self.Edit_frame_photo.update_idletasks()
        self.popup.update_idletasks()
        print("Webcam UI restored")

    def onclick_update_btn_edit_form(self):
        # for widget in self.Edit_frame_photo.winfo_children():
        #     if widget != self.Edit_frame_photo or widget != self.Edit_img_label :
        #         widget.destroy()

        # self.Edit_replace_options = CTkFrame(
        #     self.Edit_frame_photo,
        #     fg_color="#3A36F5",
        #     corner_radius=5
        # )

        # File upload button
        # Container to hold both buttons
        # self.Edit_button_container = CTkFrame(
        #     self.Edit_frame_photo,
        #     fg_color="#D9D9D9",  # Gray background
        #     corner_radius=5
        # )
        # self.Edit_button_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # From File button
        self.Edit_img_file = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(20, 20))
        self.Edit_button_file = CTkButton(
            self.Edit_frame_photo,
            image=self.Edit_img_file,
            text="From File",
            width=80,
            height=30,
            fg_color="#2A26C5",
            hover_color="#1A16B5",
            text_color="white",
            font=("Arial", 12),
            command=self.upload_Edit_photo
        )
        self.Edit_button_file.grid(row=0, column=0, padx=10, pady=(10, 5))
        self.Edit_img_webcam = CTkImage(Image.open(".\\Resources\\images\\webcam_icon.png"), size=(20, 20))
        self.Edit_button_webcam = CTkButton(
            self.Edit_frame_photo,
            image=self.Edit_img_webcam,
            text="From webcam",
            width=80,
            height=30,
            fg_color="#2A26C5",
            hover_color="#1A16B5",
            text_color="white",
            font=("Arial", 12),
            command=self.open_edit_webcam
        )
        self.Edit_button_webcam.grid(row=0, column=0, padx=10, pady=(80, 5))

        # # From Webcam button
        # self.Edit_img_webcam = CTkImage(Image.open(".\\Resources\\images\\webcam_icon.png"), size=(20, 20))
        # self.Edit_button_webcam = CTkButton(
        #     self.Edit_frame_photo,
        #     image=self.Edit_img_webcam,
        #     text="From Webcam",
        #     width=120,
        #     height=30,
        #     fg_color="#2A26C5",
        #     hover_color="#1A16B5",
        #     text_color="white",
        #     font=("Arial", 12),
        #     command=self.open_edit_webcam
        # )
        # self.Edit_button_webcam.grid(row=1, column=0, padx=10, pady=(40, 10))
        # clear_update_button = CTkButton(
        #    self.Edit_frame_photo,
        #     text="✖",  # Stylish cross instead of plain "X"
        #     font=("Helvetica", 16, "bold"),  # Custom bold font
        #     width=20,
        #     height=20,
        #     corner_radius=5,  # Rounded button
        #     fg_color="red",  # Dark gray button
        #     text_color="white",
        #     hover_color="#ff4c4c",  # Bright red on hover
        #     command=self.clear_updated_photo_from_edit_frame
        # )
        # clear_update_button.place(relx=0.82, rely=0.03)

        # self.Edit_frame_photo.place(relx=0.5, rely=0.5, anchor="center")

    def clear_updated_photo_from_edit_frame(self):
        if hasattr(self, "Edit_button_file") and self.Edit_button_file.winfo_exists():
            self.Edit_button_file.grid_forget()
            print("Edit_button_file removed")

        # Remove Edit_button_webcam
        if hasattr(self, "Edit_button_webcam") and self.Edit_button_webcam.winfo_exists():
            self.Edit_button_webcam.grid_forget()
            print("Edit_button_webcam removed")

        # Optionally remove clear_update_button
        if hasattr(self, "clear_update_button") and self.clear_update_button.winfo_exists():
            self.clear_update_button.place_forget()
            print("clear_update_button removed")

        # Ensure Edit_img_label is visible and updated
        if hasattr(self, "Edit_img_label") and self.Edit_img_label.winfo_exists():
            self.Edit_img_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            if self.Edit_photos:
                self.update_Edit_main_photo_display(self.current_Edit_photo_index)
            else:
                self.Edit_img_label.configure(image=None, text="No Image")
            print("Edit_img_label refreshed")

        # Force UI refresh
        self.Edit_frame_photo.update_idletasks()
        print("Edit_frame_photo updated")


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


