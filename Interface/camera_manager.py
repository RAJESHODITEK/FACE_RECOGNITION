from tkinter import Toplevel

from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, StringVar, CTkToplevel, CTkImage, CTkScrollableFrame, \
    CTkCheckBox, CTkCanvas
from PIL import Image

from Core.main import Core


class CameramanagerInterface(CTkFrame):
    def __init__(self, *args, root_width: int = 1920, root_height: int = 1080, **kwargs):
        super().__init__(*args, **kwargs)
        self.obj_Core=Core()
        self.dropdown_window = None
        self.frame_popup_table = None
        self.selected_cameras = set()  # Using set for efficient camera selection tracking
        self.overlay = None
        self.bool_dropdown_opened = False
        self.is_popup_open = False
        self.check_direction = False

        # Basic configuration
        self.configure(fg_color="#F1F5FA", corner_radius=0)

        i_form_width = int((int(root_width * 0.89)) * 0.885)
        i_form_height = int((int(root_height * 0.88)) * 0.9)

        # Main form frame
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

        # Header section
        self.frame_header = CTkFrame(
            self.frame_form,
            height=int(i_form_height * 0.12),
            fg_color="transparent",
            corner_radius=10
        )
        self.frame_header.columnconfigure(0, weight=1)
        self.frame_header.columnconfigure(1, weight=2)
        self.frame_header.grid(column=0, row=0, sticky="we", padx=5, pady=(5, 5))

        # Title
        self.label_heading = CTkLabel(
            self.frame_header,
            text="Camera Manager",
            text_color="#2C2C2C",
            height=38,
            font=("", 18, "bold"),
            corner_radius=10,
            anchor="w",
            fg_color="transparent"
        )
        self.label_heading.grid(row=0, column=0, padx=10, pady=(15, 0), sticky="ew")

        # Action buttons frame
        self.frame_header_rcol = CTkFrame(
            self.frame_header,
            height=int(i_form_height * 0.07),
            fg_color="transparent",
            corner_radius=10
        )
        self.frame_header_rcol.rowconfigure(0, weight=1)
        self.frame_header_rcol.grid(row=0, column=1, columnspan=2, sticky="nsew")

        self.button_delete = CTkButton(
            self.frame_header_rcol,
            height=38,
            width=100,
            text="Delete",
            text_color="#FFFFFF",
            fg_color="#313A46",
            border_width=0,
            font=("", 14),
            cursor="hand2",
            state="disabled",
            hover_color="#404c5c"
        )
        self.button_delete.pack(side="right", padx=5, pady=(15, 0))

        self.button_roi = CTkButton(
            self.frame_header_rcol,
            height=38,
            width=100,
            text="ROI",
            text_color="#FFFFFF",
            fg_color="#313A46",
            border_width=0,
            font=("", 14),
            cursor="hand2",
            state="disabled",
            hover_color="#404c5c"
        )
        self.button_roi.pack(side="right", padx=5, pady=(15, 0))

        self.button_edit = CTkButton(
            self.frame_header_rcol,
            height=38,
            width=100,
            text="Edit",
            text_color="#FFFFFF",
            fg_color="#313A46",
            border_width=0,
            font=("", 14),
            cursor="hand2",
            state="disabled",
            hover_color="#404c5c"
        )
        self.button_edit.pack(side="right", padx=5, pady=(15, 0))

        self.button_add = CTkButton(
            self.frame_header_rcol,
            height=38,
            width=100,
            text="Add Camera",
            text_color="#FFFFFF",
            fg_color="#313A46",
            border_width=0,
            font=("", 14),
            cursor="hand2",
            state="normal",
            command=self.add_camera,
            hover_color="#404c5c"
        )
        self.button_add.pack(side="right", padx=5, pady=(15, 0))

        # Underline after header
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
            fg_color="#313A46"
        )
        # Update column weights
        self.frame_table_heading.columnconfigure(0, weight=1, uniform="col")  # Sl No
        self.frame_table_heading.columnconfigure(1, weight=3, uniform="col")  # Camera Name
        self.frame_table_heading.columnconfigure(2, weight=5, uniform="col")  # URL
        self.frame_table_heading.columnconfigure(3, weight=2, uniform="col")  # Direction
        self.frame_table_heading.columnconfigure(4, weight=3, uniform="col")  # ROI
        self.frame_table_heading.columnconfigure(5, weight=1, uniform="col")  # Select
        self.frame_table_heading.grid_propagate(False)
        self.frame_table_heading.grid(row=2, column=0, padx=(15, 19), pady=(20, 0), sticky="nsew")

        # Table headers with fixed alignment
        self.table_headers = ["SL.No", "Camera Name", "URL", "Direction", "ROI Percentage", "Select"]
        header_configs = [
            {"text": "SL.No", "anchor": "center", "sticky": "ew", "padx": 14},
            {"text": "Camera Name", "anchor": "w", "sticky": "w", "padx": 8},
            {"text": "URL", "anchor": "w", "sticky": "w", "padx": 8},
            {"text": "Direction", "anchor": "center", "sticky": "ew", "padx": 8},
            {"text": "ROI Percentage", "anchor": "center", "sticky": "ew", "padx": 5},
            {"text": "Select", "anchor": "center", "sticky": "ew", "padx": 5}
        ]

        for col, config in enumerate(header_configs):
            frame = CTkFrame(
                self.frame_table_heading,
                fg_color="transparent"
            )
            frame.grid(row=0, column=col, sticky=config["sticky"], padx=config["padx"])

            button = CTkButton(
                frame,
                text=config["text"],
                height=45,
                fg_color="transparent",
                text_color="#FFFFFF",
                anchor=config["anchor"],
                font=("", 15, "bold"),
                hover=False,
                corner_radius=0,
                cursor="hand2"
            )
            button.pack(fill="x", expand=True)

        # Scrollable table content
        self.frame_table_rows = CTkScrollableFrame(
            self.frame_form,
            fg_color="transparent",
            corner_radius=0
        )
        # Match the column weights
        self.frame_table_rows.columnconfigure(0, weight=1, uniform="col")
        self.frame_table_rows.columnconfigure(1, weight=3, uniform="col")
        self.frame_table_rows.columnconfigure(2, weight=5, uniform="col")
        self.frame_table_rows.columnconfigure(3, weight=2, uniform="col")
        self.frame_table_rows.columnconfigure(4, weight=3, uniform="col")
        self.frame_table_rows.columnconfigure(5, weight=1, uniform="col")
        self.frame_table_rows.grid(row=3, column=0, padx=(15, 2), pady=(0, 20), sticky="nsew")

        # Sample data
        self.dummy_camera_details = []

        # Initial population of table
        self.update_table(self.dummy_camera_details)

    def create_percentage_axis(self, parent, camera_data):
        """Create an enhanced visual ROI representation showing camera view"""
        # Create main frame with reduced height
        frame = CTkFrame(parent, height=130, fg_color="transparent")

        # Create canvas
        canvas = CTkCanvas(frame, height=110, width=250, bg="white", highlightthickness=0)
        canvas.pack(fill="x", expand=True, padx=5)

        # Canvas dimensions
        width = 190
        height = 90
        margin = 20

        # Create gradient background effect
        for i in range(margin, height - margin):
            color_val = min(240, max(200, 200 + (i - margin)))
            color = f'#{color_val:02x}{color_val:02x}{color_val:02x}'
            canvas.create_line(margin, i, width - margin, i, fill=color)

        # Draw border frame
        canvas.create_rectangle(margin, margin, width - margin, height - margin)


        # Get percentage values
        width_start = camera_data.get('width_start_percentage', camera_data['width_start_percentage'])
        width_end = camera_data.get('width_end_percentage', camera_data['width_end_percentage'])
        height_start = camera_data.get('height_start_percentage', camera_data['height_start_percentage'])
        height_end = camera_data.get('height_end_percentage', camera_data['height_end_percentage'])

        # Calculate ROI coordinates
        plot_width = width - 2 * margin
        plot_height = height - 2 * margin

        roi_x1 = margin + (plot_width * width_start / 100)
        roi_y1 = margin + (plot_height * height_start / 100)
        roi_x2 = margin + (plot_width * width_end / 100)
        roi_y2 = margin + (plot_height * height_end / 100)

        # Draw crosshair lines
        canvas.create_line(roi_x1, margin, roi_x1, height - margin, fill="red", dash=(2, 2))
        canvas.create_line(roi_x2, margin, roi_x2, height - margin, fill="red", dash=(2, 2))
        canvas.create_line(margin, roi_y1, width - margin, roi_y1, fill="red", dash=(2, 2))
        canvas.create_line(margin, roi_y2, width - margin, roi_y2, fill="red", dash=(2, 2))

        # Draw ROI rectangle with gradient fill
        if roi_y2 > roi_y1:
            for y in range(int(roi_y1), int(roi_y2)):
                progress = (y - roi_y1) / (roi_y2 - roi_y1)
                blue = min(255, max(0, int(180 + progress * 75)))
                color = f'#c8d8{blue:02x}'
                canvas.create_line(roi_x1, y, roi_x2, y, fill=color)

        # Draw ROI border
        canvas.create_rectangle(roi_x1, roi_y1, roi_x2, roi_y2,
                                outline="blue", width=2)

        # Add percentage labels
        for i in range(0, 101, 20):
            # Width percentages
            x_pos = margin + (plot_width * i / 100)
            canvas.create_text(x_pos, height - 5,
                               text=f"{i}%", anchor="s",
                               font=("Arial", 8, "bold"))

            # Height percentages with background
            if i > 0 and i < 100:
                y_pos = margin + (plot_height * i / 100)
                canvas.create_rectangle(margin - 20, y_pos - 7, margin - 2, y_pos + 7,
                                        fill="white", outline="gray75")
                canvas.create_text(margin - 11, y_pos,
                                   text=f"{i}%", anchor="center",
                                   font=("Arial", 7, "bold"))

        # Add direction indicator with arrow
        direction = camera_data.get('direction', 'Unknown')
        arrow_chars = {"Entry": "↓", "Exit": "↑"}
        arrow = arrow_chars.get(direction, "")
        canvas.create_text(width / 2, 10,
                           text=f"{arrow} {direction}",
                           font=("Arial", 9, "bold"))

        # Create single-line labels frame below the canvas
        labels_frame = CTkFrame(frame, fg_color="transparent")
        labels_frame.pack(fill="x", padx=5, pady=(1, 0))

        # Create a single label with both width and height information
        roi_text = f"Width %: {width_start}% - {width_end}%  |  Height %: {height_start}% - {height_end}%"
        roi_label = CTkLabel(labels_frame, text=roi_text, font=("Arial", 11, "bold"), text_color='#2C2C2C')
        roi_label.pack(anchor="w")

        return frame

    def update_table(self, camera_list: list):
        # Clear existing content
        for child in self.frame_table_rows.winfo_children():
            child.destroy()

        # Populate table
        for row_index, camera in enumerate(camera_list):
            row_bg_color = "transparent" if row_index % 2 == 0 else "#FFFFFF"

            # Cell configurations
            cell_configs = [
                {"text": camera['sl_no'], "anchor": "center", "sticky": "ew", "padx": 14},
                {"text": camera['name'], "anchor": "w", "sticky": "w", "padx": 8},
                {"text": camera['url'], "anchor": "w", "sticky": "w", "padx": 8},
                {"text": camera['direction'], "anchor": "center", "sticky": "ew", "padx": 8},
            ]

            # Create frames for each cell
            for col_index, config in enumerate(cell_configs):
                frame = CTkFrame(
                    self.frame_table_rows,
                    fg_color=row_bg_color,
                    height=70
                )
                frame.grid(row=row_index * 2, column=col_index, sticky=config["sticky"])
                frame.grid_propagate(False)

                cell = CTkLabel(
                    frame,
                    text=config["text"],
                    fg_color="transparent",
                    anchor=config["anchor"],
                    font=("", 14),
                    text_color="#000000",
                    padx=config["padx"]
                )
                cell.pack(fill="both", expand=True)

            # ROI visualization
            percentage_axis = self.create_percentage_axis(
                self.frame_table_rows,
                camera
            )
            percentage_axis.grid(row=row_index * 2, column=4, sticky="nsew", padx=5)

            # Checkbox with center alignment
            checkbox_frame = CTkFrame(
                self.frame_table_rows,
                fg_color=row_bg_color,
                height=70
            )
            checkbox_frame.grid(row=row_index * 2, column=5, sticky="ew")
            checkbox_frame.grid_propagate(False)

            checkbox = CTkCheckBox(
                checkbox_frame,
                text="",
                command=lambda cam=camera: self.handle_checkbox_click(cam),
                border_width=1.5,
                corner_radius=2,
                fg_color="#2C2C2C",
                width=20,
                height=20,
                hover = "None"
            )
            checkbox.pack(expand=True)

            # Set checkbox state based on selected_cameras
            if camera['name'] in self.selected_cameras:
                checkbox.select()
            else:
                checkbox.deselect()

            # Separator line
            canvas_underline = CTkCanvas(
                self.frame_table_rows,
                height=1,
                bg="#D7DDE5",
                bd=0,
                highlightthickness=0
            )
            canvas_underline.grid(row=row_index * 2 + 1, column=0, columnspan=6, pady=0, sticky="ew")

        # Update button states based on current selections
        self.update_button_states()

    def handle_checkbox_click(self, camera):
        """
        Handle checkbox click events and manage button states based on camera selection
        """
        current_camera = camera['name']
        if current_camera in self.selected_cameras:
            self.selected_cameras.remove(current_camera)
        else:
            self.selected_cameras.add(current_camera)
        print("selected camera :", self.selected_cameras)

        self.update_button_states()

    def reset_interface(self):
        """
        Reset the interface state completely
        """
        self.selected_cameras.clear()
        self.update_button_states()
        self.update_table(self.dummy_camera_details)
        if hasattr(self, 'popup'):
            self.close_dropdown()
            self.popup.destroy()

    def update_button_states(self):
        """
        Update button states based on the number of selected cameras
        """
        num_selected = len(self.selected_cameras)

        if num_selected == 0:
            self.button_add.configure(
                state="normal",
                fg_color="#5A616B",
                text_color="#FFFFFF",
                hover_color="#313A46"
            )
            self.button_edit.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )
            self.button_delete.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )
            self.button_roi.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )
        elif num_selected == 1:
            self.button_add.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )
            self.button_edit.configure(
                state="normal",
                fg_color="#5A616B",
                text_color="#FFFFFF",
                hover_color="#313A46"
            )
            self.button_delete.configure(
                state="normal",
                fg_color="#5A616B",
                text_color="#FFFFFF",
                hover_color="#313A46"
            )
            self.button_roi.configure(
                state="normal",
                fg_color="#5A616B",
                text_color="#FFFFFF",
                hover_color="#313A46"
            )
        else:  # num_selected > 1
            self.button_add.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )
            self.button_edit.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )
            self.button_delete.configure(
                state="normal",
                fg_color="#5A616B",
                text_color="#FFFFFF",
                hover_color="#313A46"
            )
            self.button_roi.configure(
                state="disabled",
                fg_color="#e6e6ff",
                text_color="#A0A0A0",
                hover_color="#313A46"
            )

    def delete_selected_cameras(self):
        self.dummy_camera_details = [cam for cam in self.dummy_camera_details
                                     if cam['name'] not in self.selected_cameras]

        self.update_table(self.dummy_camera_details)
        # Reset all button states after deletion
        # self.edit_button.configure(state="disabled")
        # self.delete_button.configure(state="disabled")
        # self.add_button.configure(state="normal")  # Re-enable Add button after deletion

    def close_popup_outside(self, event, popup):
        if not popup.winfo_containing(event.x_root, event.y_root):
            self.cancel()

    def edit_camera(self, camera):
        # Handle edit camera logic here
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        popup_width = 500
        popup_height = 650

        x_position = (screen_width - popup_width) // 2
        y_position = (screen_height - popup_height) // 2

        data = {'heading': 'Edit Camera',
                'camera_name': camera['name'],
                'direction': camera['direction'],
                'url': camera['url'],
                'state': 'disable',
                'cancel_button': 'reset',
                'save_button': 'Update'
                }

        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.lift()
            return

        self.popup = CTkToplevel(self)
        self.popup.geometry(f"{popup_width}x{popup_height}+{x_position + 200}+{y_position}")
        self.popup.title("Edit Camera")
        self.popup.configure(bg="#232E51")
        self.popup.attributes("-topmost", True)


        self.camera_form(data)

    def on_popup_close(self):
        """Handle popup window closing"""
        if hasattr(self, 'popup'):
            self.popup.destroy()

    def clear_selections(self):
        """Clear all camera selections and reset button states"""

        for child in self.frame_table_rows.winfo_children():
            if isinstance(child, CTkCheckBox):
                child.deselect()


        self.button_add.configure(state="normal")
        self.button_edit.configure(state="disabled")
        self.button_delete.configure(state="disabled")
        self.button_roi.configure(state="disabled")

    def cancel(self):
        """Handle cancel button click in popup"""

        if hasattr(self, 'popup'):
            self.close_dropdown()
            self.popup.destroy()

    def add_camera(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        popup_width = 500
        popup_height = 650

        x_position = (screen_width - popup_width) // 2
        y_position = (screen_height - popup_height) // 2

        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()
            return

        self.popup = CTkToplevel(self)
        self.popup.geometry(f"{popup_width}x{popup_height}+{x_position + 200}+{y_position}")
        self.popup.title("Add New Camera")
        self.popup.configure(bg="#232E51")
        self.popup.attributes("-topmost", True)

        data = {'camera_name': '',
                'heading': 'Add Camera',
                'direction': 'Select direction',
                'url': '',
                'state': 'normal',
                'cancel_button': 'cancel',
                'save_button': 'Save'
                }
        self.camera_form(data)

    def close_popup(self):

        self.close_dropdown()
        self.popup.destroy()

    def set_entry_text(self, entry, value, placeholder, state='normal'):
        if value:
            entry.configure(textvariable=StringVar(value=value))
        else:
            entry.configure(placeholder_text=placeholder)

        entry.configure(state=state)

    def camera_form(self, data=[]):
        self.i_form_width = 500
        self.i_form_height = 650
        self.list_direction = ["Entry", "Exit"]
        self.bool_dropdown_opened = False


        self.frame_form = CTkFrame(
            self.popup,
            width=self.i_form_width,
            height=self.i_form_height,
            fg_color="#FFFFFF",
            corner_radius=10
        )
        self.frame_form.columnconfigure(0, weight=1, uniform='a')
        self.frame_form.columnconfigure(1, weight=1, uniform='a')
        self.frame_form.grid_propagate(False)
        self.frame_form.pack(side="top", expand=False, padx=0, pady=(0, 0))


        self.label_heading = CTkLabel(
            self.frame_form,
            text=data['heading'] if 'heading' in data else "Add Camera",
            text_color="#2C2C2C",
            font=("", 24, "bold"),
            anchor="center"
        )
        self.label_heading.grid(row=0, column=0, columnspan=2, padx=25, pady=(10, 10), sticky="ew")


        self.camera_basic_frame = CTkFrame(
            self.frame_form,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E5E7EB",
            corner_radius=8
        )
        self.camera_basic_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        self.label_camera_information = CTkLabel(
            self.camera_basic_frame,
            text="Basic Camera Details",
            text_color="#2C2C2C",
            font=("", 14, "bold"),
            anchor="w"
        )
        self.label_camera_information.grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 5), sticky="w")
        self.label_camera_error = CTkLabel(
            self.camera_basic_frame,
            text="",
            text_color="red",
            font=("", 14),
            anchor="w"
        )
        self.label_camera_error.grid(row=0, column=1, columnspan=2, padx=10, pady=(5, 5), sticky="w")


        self.label_camera_name = CTkLabel(
            self.camera_basic_frame,
            text="Camera Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_camera_name.grid(row=1, column=0, padx=(15, 10), pady=(5, 5), sticky="w")


        self.entry_camera_name = CTkEntry(
            self.camera_basic_frame,
            height=35,
            width=200,
            fg_color="#F6F6F6",
            text_color="#2C2C2C",
            border_color="#DEDEDE",
            state=data['state'] if data['state'] else 'normal',
            border_width=2,
            corner_radius=5,
        )

        self.entry_camera_name.grid(row=2, column=0, padx=(15, 10), pady=(0, 15), sticky="w")
        self.set_entry_text(self.entry_camera_name, data.get('camera_name', 'Enter camera name'), "Enter camera name",
                            data['state'] if data['state'] else 'normal')



        self.label_direction = CTkLabel(
            self.camera_basic_frame,
            text="Camera Direction",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_direction.grid(row=1, column=1, padx=(25, 15), pady=(5, 5), sticky="w")


        self.frame_direction_dropdown = CTkFrame(
            self.camera_basic_frame,
            height=35,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_direction_dropdown.columnconfigure(0, weight=1)
        self.frame_direction_dropdown.grid_propagate(False)
        self.frame_direction_dropdown.grid(row=2, column=1, padx=(25, 15), pady=(0, 15), sticky="ew")


        self.entry_selected_direction = CTkEntry(
            self.frame_direction_dropdown,
            height=35,
            width=200,
            fg_color="#F6F6F6",
            text_color="#828282",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            state="readonly"

        )
        self.entry_selected_direction.grid(row=0, column=0, sticky="nsew")
        self.set_entry_text(self.entry_selected_direction, data.get('direction', 'Select direction'),
                            "Select direction","disabled" )


        try:
            img_down_arrow = CTkImage(Image.open("./Resources/images/down_arrow_icon.png"), size=(22, 22))
        except:
            img_down_arrow = None

        self.button_select_direction = CTkButton(
            self.frame_direction_dropdown,
            image=img_down_arrow,
            height=30,
            width=33,
            text="▼" if img_down_arrow is None else "",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
            command=lambda: self.popup_dropdown(
                self.list_direction,
                self.entry_selected_direction,
                parent_window=self
            )
        )
        self.button_select_direction.grid(row=0, column=0, sticky="ne", padx=3, pady=1.5)


        self.camera_details_frame = CTkFrame(
            self.frame_form,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E5E7EB",
            corner_radius=8
        )
        self.camera_details_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")


        self.label_connection = CTkLabel(
            self.camera_details_frame,
            text="Connection Details",
            text_color="#2C2C2C",
            font=("", 14, "bold"),
            anchor="w"
        )
        self.label_connection.grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 5), sticky="w")

        self.label_connection_error = CTkLabel(
            self.camera_details_frame,
            text="",
            text_color="red",
            font=("", 14),
            anchor="w"
        )
        self.label_connection_error.grid(row=0, column=1, columnspan=2, padx=10, pady=(5, 5), sticky="w")


        self.label_rtsp_url = CTkLabel(
            self.camera_details_frame,
            text="RTSP URL",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_rtsp_url.grid(row=1, column=0, columnspan=2, padx=(15, 15), pady=(5, 5), sticky="w")

        self.entry_rtsp_url = CTkEntry(
            self.camera_details_frame,
            height=38,
            width=440,
            fg_color="#F6F6F6",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_rtsp_url.grid(row=1 + 1, column=0, columnspan=2, padx=(15, 15), pady=(0, 10), sticky="w")
        self.set_entry_text(self.entry_rtsp_url, data.get('url', ''), "rtsp://", )


        self.label_username = CTkLabel(
            self.camera_details_frame,
            text="Username",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_username.grid(row=3, column=0, columnspan=2, padx=(20, 15), pady=(5, 5), sticky="w")

        self.entry_username = CTkEntry(
            self.camera_details_frame,
            placeholder_text="Enter username",
            height=35,
            width=200,
            fg_color="#F6F6F6",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_username.grid(row=3 + 1, column=0, columnspan=2, padx=(15, 15), pady=(0, 10), sticky="w")

        self.label_IPAddress = CTkLabel(
            self.camera_details_frame,
            text="IP Address",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_IPAddress.grid(row=3, column=1, columnspan=2, padx=(20, 15), pady=(5, 5), sticky="w")

        self.entry_IPAddress = CTkEntry(
            self.camera_details_frame,
            placeholder_text="192.168.1.1",
            height=35,
            width=200,
            fg_color="#F6F6F6",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_IPAddress.grid(row=3 + 1, column=1, columnspan=2, padx=(20, 15), pady=(0, 10), sticky="w")


        self.label_password = CTkLabel(
            self.camera_details_frame,
            text="Password",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_password.grid(row=5, column=0, columnspan=2, padx=(20, 15), pady=(5, 5), sticky="w")

        self.entry_password = CTkEntry(
            self.camera_details_frame,
            placeholder_text="Enter Password",
            height=35,
            width=200,
            fg_color="#F6F6F6",
            show="*",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_password.grid(row=5 + 1, column=0, columnspan=2, padx=(15, 15), pady=(0, 10), sticky="w")

        self.label_port = CTkLabel(
            self.camera_details_frame,
            text="Port",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_port.grid(row=5, column=1, columnspan=2, padx=(20, 15), pady=(5, 5), sticky="w")

        self.entry_port = CTkEntry(
            self.camera_details_frame,
            placeholder_text="554",
            height=35,
            width=200,
            fg_color="#F6F6F6",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_port.grid(row=5 + 1, column=1, columnspan=2, padx=(20, 15), pady=(0, 10), sticky="w")


        self.label_substream = CTkLabel(
            self.camera_details_frame,
            text="Substream",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w"
        )
        self.label_substream.grid(row=7, column=0, columnspan=2, padx=(20, 15), pady=(5, 2), sticky="w")

        self.entry_substream = CTkEntry(
            self.camera_details_frame,
            placeholder_text="Enter substream",
            height=35,
            width=440,
            fg_color="#F6F6F6",
            placeholder_text_color="#828282",
            text_color="#414141",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14)
        )
        self.entry_substream.grid(row=7 + 1, column=0, columnspan=2, padx=(15, 15), pady=(0, 10), sticky="w")

        self.button_frame = CTkFrame(
            self.frame_form,
            fg_color="#FFFFFF",
            height=60
        )
        self.button_frame.grid(row=3, column=0, columnspan=2, padx=25, pady=(5, 10), sticky="ew")


        self.button_frame.columnconfigure(0, weight=1)  # Left Spacer
        self.button_frame.columnconfigure(1, weight=0)  # Save Button
        self.button_frame.columnconfigure(2, weight=0)  # Cancel Button
        self.button_frame.columnconfigure(3, weight=1)  # Right Spacer


        self.btn_save = CTkButton(
            self.button_frame,
            height=35,
            width=100,
            text=data['save_button'] if data['save_button'] else 'Save',
            text_color="#FFFFFF",
            fg_color="#444C57",
            border_color="#3A36F5",
            font=("", 14),
            state=data['state'] if data['state'] else 'normal',
            cursor="hand2",
            hover=False
        )
        self.btn_save.grid(row=0, column=1, padx=(0, 5), pady=(5, 10), sticky="nsew")


        self.btn_cancel = CTkButton(
            self.button_frame,
            height=35,
            width=100,
            text=data['cancel_button'] if data['cancel_button'] else 'Cancel',
            text_color="#FFFFFF",
            fg_color="#6C757D",
            border_color="#6C757D",
            font=("", 14),
            cursor="hand2",
            hover=False,
            command=self.cancel
        )
        self.btn_cancel.grid(row=0, column=2, padx=(5, 0), pady=(5, 10), sticky="nsew")

        self.bind("<Configure>",
                  lambda e: self.cancel)

        if hasattr(self, 'on_form_ready'):
            self.on_form_ready()
        self.bind_widgets(self)


    def cancel(self):
        if hasattr(self, 'popup'):
            if hasattr(self, 'frame_form'):
                self.close_dropdown()
                self.popup.destroy()

    def get_all_children(self, parent):
        children = parent.winfo_children()
        all_children = [] + children
        for child in children:
            all_children.extend(self.get_all_children(child))
        return all_children

    def bind_widgets(self, parent):
        self.list_widgets = self.get_all_children(parent)

        for widget in self.list_widgets:
            if (widget == self.button_select_direction):
                continue
            if isinstance(widget, (CTkLabel, CTkButton, CTkFrame, CTkEntry)):
                widget.bind("<Button-1>", self.close_dropdown)

    def popup_dropdown(self, list_data: list = [], entry_destination: CTkEntry = None, parent_window: CTkFrame = None,
                       event=None):

        if not self.bool_dropdown_opened:

            if not self.dropdown_window:
                self.dropdown_window = Toplevel(parent_window)
                self.dropdown_window.withdraw()
                self.dropdown_window.overrideredirect(True)
                self.dropdown_window.attributes("-topmost", True)



                # Create main frame in dropdown window
                self.frame_maindropdown_window = CTkFrame(
                    self.popup,
                    fg_color="#DEDEDE",
                    height=100,
                    corner_radius=5
                )
                self.frame_maindropdown_window.grid_propagate(False)
                self.frame_maindropdown_window.columnconfigure(0, weight=1)
                self.frame_maindropdown_window.rowconfigure(0, weight=1)
                self.frame_maindropdown_window.place(relx=0.52, rely=0.27)

                self.frame_popup_table = CTkScrollableFrame(
                    self.frame_maindropdown_window,
                    fg_color="#FFFFFF",
                    corner_radius=5
                )
                self.frame_popup_table.grid(column=0, row=0, sticky="nsew", padx=(1, 3), pady=(1, 3))


            # Clear existing buttons
            for widget in self.frame_popup_table.winfo_children():
                widget.destroy()

            # Create option buttons
            for index, row_data in enumerate(list_data):
                button_options = CTkButton(
                    self.frame_popup_table,
                    text=f"  {row_data}",
                    height=35,
                    fg_color="transparent",
                    text_color="#414141",
                    font=("", 14),
                    corner_radius=0,
                    hover_color="#F6F6F6",
                    anchor="w",
                    command=lambda selected_option=row_data: self.select_option(selected_option, entry_destination)
                )
                button_options.pack(fill="x", pady=1)

            self.unbind('<Button-1>')
            self.bind('<Button-1>', self.check_click_outside, add='+')
            self.dropdown_window.bind('<FocusOut>', self.close_dropdown)

            self.bool_dropdown_opened = True
        else:
            self.close_dropdown()

    def check_click_outside(self, event):
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            x, y = event.x_root, event.y_root
            wx = self.dropdown_window.winfo_x()
            wy = self.dropdown_window.winfo_y()
            ww = self.dropdown_window.winfo_width()
            wh = self.dropdown_window.winfo_height()

            # Close dropdown if the click is outside the dropdown window
            if not (wx <= x <= wx + ww and wy <= y <= wy + wh):
                self.close_dropdown()

    def close_dropdown(self, event=None):
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            self.frame_maindropdown_window.destroy()
            self.dropdown_window = None
            self.bool_dropdown_opened = False
            self.unbind('<Button-1>')

    def select_option(self, selected_option: str, entry_destination: CTkEntry):
        if entry_destination:
            entry_destination.configure(state="normal", text_color="#414141")
            entry_destination.delete(0, "end")
            entry_destination.insert(0, selected_option)
            entry_destination.configure(state="disabled")
            self.validate_direction()
        self.close_dropdown()

    def validate_direction(self, event=None):
        self.label_camera_error.configure(text="")
        direction = self.entry_selected_direction.get()
        if direction != "Select direction":
            self.entry_selected_direction.configure(border_color="green")
            self.check_direction = True
        else:
            self.entry_selected_direction.configure(border_color="red")
            self.check_direction = False


    def update_camera_data_list(self):
        datas = self.obj_Core.obj_Camera.fetch_all_Camera_data()
        self.dummy_camera_details.clear()
        slno = 0
        for data in datas:
            slno = slno + 1
            new_camera_details = {
                'sl_no': slno,
                'name': data['Camera_name'],
                'url': data['URL'],
                'direction': data['Camera_direction'],
                'height_start_percentage': data['ROIStartPercentageHeight'],
                'height_end_percentage': data['ROIEndPercentageHeight'],
                'width_start_percentage': data['ROIStartPercentageWidth'],
                'width_end_percentage': data['ROIEndPercentageWidth'],
                'start_percentage': data['ROIStartPercentageWidth'],
                'end_percentage': data['ROIEndPercentageWidth']
            }
            # Append the new data to the list
            self.dummy_camera_details.append(new_camera_details)





