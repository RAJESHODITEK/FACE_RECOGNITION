import base64
import os
from io import BytesIO
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage, CTkCanvas, CTkScrollableFrame, CTkEntry, CTkTextbox, \
    CTkToplevel
from PIL import Image, ImageDraw, ImageTk
import random
from datetime import datetime


class NotificationInterface(CTkFrame):
    def __init__(self, *args, root_width: int = 1920, root_height: int = 1080, **kwargs):
        super().__init__(*args, **kwargs)

        self.selected_vehicle = None  # Track selected card
        self.ack_frame = None  # Store reference to acknowledgment frame
        self.configure(fg_color="#F1F5FA", corner_radius=0)
        self.vehicle_data = []
        self.ack_window = None
        self.i_start_index = 0
        self.i_end_index = 0
        self.i_total_data = 0
        self.items_per_page = 5

        def create_arrow_image(direction, color):
            # Create a new image with transparent background
            img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            border_color = "#000000"
            border_width = 3  # Set the thickness of the border

            if direction == "left":
                # Draw a filled left arrow with a thicker border
                points = [(16, 4), (8, 12), (16, 20), (12, 12)]
            else:
                # Draw a filled right arrow with a thicker border
                points = [(8, 4), (16, 12), (8, 20), (12, 12)]

            # Draw the border (outline) first
            draw.polygon(points, outline=border_color, width=border_width)
            # Fill the arrow with the main color
            draw.polygon(points, fill=color)

            return img

        # Create images for both states
        self.left_arrow_image = CTkImage(
            light_image=create_arrow_image("left", "#2C2C2C"),
            dark_image=create_arrow_image("left", "#2C2C2C"),
            size=(30, 30)
        )

        self.left_arrow_disabled = CTkImage(
            light_image=create_arrow_image("left", "#9CA3AF"),
            dark_image=create_arrow_image("left", "#9CA3AF"),
            size=(30, 30)
        )

        self.right_arrow_image = CTkImage(
            light_image=create_arrow_image("right", "#2C2C2C"),
            dark_image=create_arrow_image("right", "#2C2C2C"),
            size=(30, 30)
        )

        self.right_arrow_disabled = CTkImage(
            light_image=create_arrow_image("right", "#9CA3AF"),
            dark_image=create_arrow_image("right", "#9CA3AF"),
            size=(30, 30)
        )

        # Main form frame
        i_form_width = int((int(root_width * 0.89)) * 0.885)
        i_form_height = int((int(root_height * 0.88)) * 0.9)

        self.frame_form = CTkFrame(
            self,
            width=i_form_width,
            height=i_form_height + 50,
            fg_color="white",
            corner_radius=10
        )
        self.frame_form.columnconfigure(0, weight=1)
        self.frame_form.rowconfigure(2, weight=1)
        self.frame_form.grid_propagate(False)
        self.frame_form.pack(side="top", expand=False, padx=10, pady=30)

        # Header frame
        self.frame_header = CTkFrame(
            self.frame_form,
            height=int(i_form_height * 0.10),
            fg_color="transparent",
            corner_radius=0
        )
        self.frame_header.columnconfigure((0, 1), weight=1)
        self.frame_header.grid(column=0, row=0, sticky="we", padx=5, pady=(5, 15))

        # Heading
        self.label_heading = CTkLabel(
            self.frame_header,
            text="Alarm List",
            text_color="#2C2C2C",
            font=("", 18, "bold"),
            corner_radius=10,
            anchor="w",
            fg_color="transparent"
        )
        self.label_heading.grid(row=0, column=0, padx=10, pady=(15, 0), sticky="w")

        # Underline
        self.canvas_underline = CTkCanvas(
            self.frame_form,
            height=2,
            bg="#D2D2D2",
            bd=0,
            highlightthickness=0,
        )
        self.canvas_underline.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))

        # CTkScrollableFrame for content
        self.frame_content = CTkScrollableFrame(
            self.frame_form,
            fg_color="transparent",
            height=int(i_form_height * 0.99),
        )
        self.frame_content.grid(row=2, column=0, sticky="nsew", padx=10, pady=15)

        # Bottom buttons frame
        self.frame_buttons = CTkFrame(
            self.frame_form,
            fg_color="transparent",
            height=10,
        )
        self.frame_buttons.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        self.frame_buttons.grid_rowconfigure(0, weight=1)
        self.frame_buttons.grid_columnconfigure((0, 2), weight=1)



        # Modified acknowledge button with command
        self.button_acknowledge = CTkButton(
            self.frame_buttons,
            text="Acknowledge",
            fg_color="#444C57",
            hover_color="#313A46",
            height=35,
            state="disabled"
        )
        self.button_acknowledge.grid(row=0, column=1, padx=5, pady=10, sticky="e")

        self.button_cancel = CTkButton(
            self.frame_buttons,
            text="Cancel",
            fg_color="#6C757D",
            hover_color="#5A6268",
            height=35,
            command=self.handle_cancel
        )
        self.button_cancel.grid(row=0, column=2, padx=5, pady=10, sticky="w")

        self.label_data_count = CTkLabel(
            self.frame_buttons,
            text="No Records Found!",
            text_color="#FF0000",
            font=("", 14),
        )
        self.label_data_count.grid(row=0, column=0, padx=15, pady=(0, 10), sticky="w")


        self.button_next = CTkButton(
            self.frame_form,
            height=38,
            width=100,
            text="Next",
            text_color="white",
            fg_color="#5A616B",
            border_color="#5A616B",
            font=("", 14),
            cursor="hand2",
            anchor="center",
            hover=False,
        )
        self.button_next.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="e")

        self.button_previous = CTkButton(
            self.frame_form,
            height=38,
            width=100,
            text="Previous",
            text_color="white",
            fg_color="#5A616B",
            border_color="#5A616B",
            font=("", 14),
            cursor="hand2",
            anchor="center",
            hover=False,
        )
        self.button_previous.grid(row=3, column=0, padx=(15, 120), pady=(0, 10), sticky="e")

        self.update_alarm_list()

    def handle_next(self):
        if self.i_end_index < self.i_total_data:
            self.i_start_index += self.items_per_page
            self.update_alarm_list()

    def handle_previous(self):
        if self.i_start_index > 0:
            self.i_start_index = max(0, self.i_start_index - self.items_per_page)
            self.update_alarm_list()

    def on_page_change(self):
        if self.i_total_data == 0:
            self.label_data_count.configure(
                text="No Records Found!",
                text_color="#FF0000"
            )
        else:
            self.label_data_count.configure(
                text=f"Showing {self.i_start_index + 1} - {self.i_end_index} of {self.i_total_data} entries",
                text_color="#2c2c2c"
            )

        enabled_color = "#444C57"  # Dark blue when enabled
        enabled_hover = "#1A233C"  # Slightly darker blue on hover
        enabled_text = "#FFFFFF"  # White text

        disabled_color = "#e6e6ff"  # Light blue when disabled
        disabled_hover = "#A5B1CD"  # Keep the same for consistency
        disabled_text = "#9CA3AF"  # Gray text when disabled

        self.update_button_state(
            button=self.button_previous,
            state="disabled" if self.i_start_index <= 0 else "normal",
            cursor="X_cursor" if self.i_start_index <= 0 else "hand2",
            fg_color=disabled_color if self.i_start_index <= 0 else enabled_color,
            hover_color=disabled_hover if self.i_start_index <= 0 else enabled_hover,
            #text_color=disabled_text if self.i_start_index <= 0 else enabled_text
        )

        self.update_button_state(
            button=self.button_next,
            state="disabled" if self.i_end_index >= self.i_total_data else "normal",
            cursor="X_cursor" if self.i_end_index >= self.i_total_data else "hand2",
            fg_color=disabled_color if self.i_end_index >= self.i_total_data else enabled_color,
            hover_color=disabled_hover if self.i_end_index >= self.i_total_data else enabled_hover,
            #text_color=disabled_text if self.i_end_index >= self.i_total_data else enabled_text
        )


    def update_button_state(self, button, state, cursor, fg_color, hover_color):
        """Updated button state handler for text buttons"""
        button.configure(
            state=state,
            text_color="#9CA3AF" if state == "disabled" else "#FFFFFF",
            fg_color="#e6e6ff" if state == "disabled" else "#444C57",
            hover_color="#F3F4F6" if state == "disabled" else "#232E48",
            cursor="arrow" if state == "disabled" else "hand2"
        )


    def reset_interface(self):
        # Add to existing reset_interface method
        self.i_start_index = 0
        self.i_end_index = 0
        self.i_total_data = 0
        self.frame_content._parent_canvas.yview_moveto(0)

        for widget in self.frame_content.winfo_children():
            widget.destroy()



    def show_acknowledge_dialog(self):
        """Modified to ensure cleanup of any existing windows"""
        # Check if window already exists and is showing
        if self.ack_window is not None and self.ack_window.winfo_exists():
            self.ack_window.focus_force()
            return

        # Clean up any existing windows first
        if self.ack_window is not None:
            try:
                self.ack_window.destroy()
            except:
                pass
            self.ack_window = None

        if self.ack_frame is not None:
            try:
                self.ack_frame.destroy()
            except:
                pass
            self.ack_frame = None

        self.create_acknowledgment_frame()

    def handle_acknowledgment_submit(self):
        self.handle_acknowledgment(self.selected_vehicle, '')
        self.close_acknowledgment_frame()

    def close_acknowledgment_frame(self):
        if self.ack_window:
            self.ack_window.destroy()
            self.ack_window = None
        if self.ack_frame:
            self.ack_frame.destroy()
            self.ack_frame = None


    def handle_acknowledgment(self, vehicle_number, note):
        # Find the specific vehicle in vehicle_data
        acknowledged_vehicle = next(
            (data for data in self.vehicle_data if data["vehicle_event_id"] == vehicle_number),
            None
        )

        if acknowledged_vehicle:
            # Update the vehicle's status and acknowledgment details
            acknowledged_vehicle['status'] = 'Resolved'
            acknowledged_vehicle['acknowledgment_note'] = note
            acknowledged_vehicle['acknowledgment_time'] = datetime.now()

            # Remove the card from the UI
            for container in self.frame_content.winfo_children():
                for widget in container.winfo_children():
                    if isinstance(widget, CTkFrame):
                        for child in widget.winfo_children():
                            if isinstance(child, CTkFrame):
                                for label in child.winfo_children():
                                    if isinstance(label, CTkLabel) and hasattr(label, 'cget'):
                                        if label.cget('text') == vehicle_number:
                                            container.destroy()
                                            break

            # Remove the acknowledged vehicle from vehicle_data
            self.vehicle_data = [data for data in self.vehicle_data if data["vehicle_event_id"] != vehicle_number]


            # Reset selection and disable acknowledge button
            self.selected_vehicle = None
            self.button_acknowledge.configure(state="disabled")

            # Refresh UI styling
            self.refresh_ui_styling()

            # Return the updated vehicle data for potential further processing
            return acknowledged_vehicle

        return None
    def refresh_ui_styling(self):
        # Update zebra striping and separators for remaining cards
        for i, container in enumerate(self.frame_content.winfo_children()):
            for widget in container.winfo_children():
                if isinstance(widget, CTkFrame) and widget.winfo_class() == 'CTkFrame':
                    widget.configure(fg_color="#FFFFFF" if i % 2 == 0 else "#F7F9FB")

    def handle_cancel(self):
        # Reset selection
        self.selected_vehicle = None
        self.button_acknowledge.configure(state="disabled")

        # Update visual selection without full refresh
        self.clear_selection()

    def clear_selection(self):
        for container in self.frame_content.winfo_children():
            for widget in container.winfo_children():
                if isinstance(widget, CTkFrame):
                    index = self.frame_content.winfo_children().index(container)
                    widget.configure(fg_color="#FFFFFF" if index % 2 == 0 else "#F7F9FB")

    def update_single_card(self, vehicle_number):
        # Find the frame containing the card to update
        for container in self.frame_content.winfo_children():
            for widget in container.winfo_children():
                if isinstance(widget, CTkFrame):
                    # Find vehicle number label in the frame
                    for child in widget.winfo_children():
                        if isinstance(child, CTkFrame):
                            for label in child.winfo_children():
                                if isinstance(label, CTkLabel) and hasattr(label, 'cget'):
                                    if label.cget('text') == vehicle_number:
                                        # Found the card to update
                                        container.destroy()
                                        # Get updated data
                                        updated_data = next(
                                            (data for data in self.vehicle_data if data["vehicle_event_id"] == vehicle_number),
                                            None
                                        )
                                        if updated_data:
                                            # Call update_alarm_list with only the updated data
                                            self.update_alarm_list([updated_data], append=True)
                                        return

    def on_card_click(self, vehicle_number):
        if self.selected_vehicle == vehicle_number:
            return
        # Clear previous selection
        self.clear_selection()
        self.selected_vehicle = vehicle_number
        self.button_acknowledge.configure(state="normal")

        # Update only the selected card's appearance
        for container in self.frame_content.winfo_children():
            for widget in container.winfo_children():
                if isinstance(widget, CTkFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, CTkFrame):
                            for label in child.winfo_children():
                                if isinstance(label, CTkLabel) and hasattr(label, 'cget'):
                                    if label.cget('text') == vehicle_number:
                                        widget.configure(fg_color="#E8E8E8")

    def convert_rgb_to_bgr(self, image_param, target_size=(230, 200)):
        try:
            if isinstance(image_param, Image.Image):
                image = image_param
            elif isinstance(image_param, CTkImage):
                image = image_param._light_image
            elif isinstance(image_param, str):
                if image_param.startswith(('data:image', 'iVBOR', '/9j/')):
                    try:
                        image_data = base64.b64decode(image_param)
                        image = Image.open(BytesIO(image_data))
                    except Exception as e:
                        print(f"Error decoding base64 image: {e}")
                        return Image.new('RGB', target_size, color=(200, 200, 200))
                elif os.path.exists(image_param):
                    image = Image.open(image_param)
                else:
                    print(f"Image file not found: {image_param}")
                    return Image.new('RGB', target_size, color=(200, 200, 200))
            else:
                print(f"Unsupported image type: {type(image_param)}")
                return Image.new('RGB', target_size, color=(200, 200, 200))

            if image.mode != "RGB":
                image = image.convert("RGB")

            # Resize to target size while preserving aspect ratio
            width, height = image.size
            aspect_ratio = width / height
            target_aspect = target_size[0] / target_size[1]

            if aspect_ratio > target_aspect:
                # Image is wider than target
                new_width = target_size[0]
                new_height = int(new_width / aspect_ratio)
            else:
                # Image is taller than target
                new_height = target_size[1]
                new_width = int(new_height * aspect_ratio)

            resized_image = image.resize((new_width, new_height), Image.LANCZOS)

            # Create a blank image with the target size
            new_image = Image.new('RGB', target_size, color=(255, 255, 255))

            # Paste the resized image centered on the blank image
            paste_position = ((target_size[0] - new_width) // 2,
                              (target_size[1] - new_height) // 2)
            new_image.paste(resized_image, paste_position)

            # For actual RGB to BGR conversion (if needed):
            # b, g, r = new_image.split()
            # new_image = Image.merge("RGB", (b, g, r))

            return new_image

        except Exception as e:
            print(f"Error processing image: {e}")
            return Image.new('RGB', target_size, color=(200, 200, 200))

    def create_acknowledgment_frame(self):
        if not self.selected_vehicle:
            return

        # Find the selected data
        selected_data = next(
            (data for data in self.vehicle_data if data.get("event_id") == self.selected_vehicle),
            None
        )

        if not selected_data:
            return

        self.ack_window = CTkToplevel()
        self.ack_window.geometry("800x575")
        self.ack_window.title("Acknowledgment Panel")
        self.ack_window.configure(bg="#1E2749")
        self.ack_window.resizable(False, False)
        self.ack_window.attributes("-topmost", True)

        # Center window
        screen_width = self.ack_window.winfo_screenwidth()
        screen_height = self.ack_window.winfo_screenheight()
        x_position = (screen_width - 800) // 2 + 200
        y_position = (screen_height - 575) // 2
        self.ack_window.geometry(f"800x575+{x_position}+{y_position}")
        self.ack_window.focus_force()

        # Main frame
        self.ack_frame = CTkFrame(
            self.ack_window,
            width=800,
            height=575,
            fg_color="#1E2749",
            corner_radius=0,
            border_width=1,
            border_color="#4A5567"
        )
        self.ack_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.ack_frame.grid_propagate(False)

        # Header
        ack_label = CTkLabel(
            self.ack_frame,
            text="Acknowledgment Panel",
            font=("Inter", 28, "bold"),
            text_color="#FFFFFF",
            bg_color="transparent"
        )
        ack_label.pack(pady=(20, 10))

        # Information boxes frame
        info_boxes_frame = CTkFrame(
            self.ack_frame,
            fg_color="transparent"
        )
        info_boxes_frame.pack(pady=(10, 15), padx=20, fill="x")

        # Event Info Box (First Box)
        event_box = CTkFrame(
            info_boxes_frame,
            fg_color="#2C3656",
            border_width=1,
            border_color="#4A5567",
            corner_radius=12,
            width=240,
            height=265
        )
        event_box.pack(side="left", padx=10, fill="both", expand=True)
        event_box.pack_propagate(False)

        event_title_frame = CTkFrame(
            event_box,
            fg_color="#3A4766",
            corner_radius=8,
            height=40
        )
        event_title_frame.pack(pady=(15, 10), padx=15, fill="x")

        CTkLabel(
            event_title_frame,
            text="Event Details",
            font=("Inter", 18, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=5)

        # Event Info Content
        event_info_frame = CTkFrame(event_box, fg_color="transparent")
        event_info_frame.pack(pady=10, padx=20, fill="both", expand=True)

        event_details = [
            ("Event No:", str(selected_data.get("event_id", "N/A"))),
            ("Status:", "UNRECOGNIZED PERSON"),
            ("Start Time:", selected_data.get("start_time", "N/A")),
            ("End Time:", selected_data.get("end_time", "N/A")),
            ("Event Type:", "Alert")
        ]

        for label, value in event_details:
            row_frame = CTkFrame(event_info_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)

            CTkLabel(
                row_frame,
                text=label,
                font=("Inter", 14, "bold"),
                text_color="#B0B8C4",
                anchor="w"
            ).pack(side="left", padx=(0, 10))

            if label == "Event Type:" and value in ["Blacklisted", "Alert"]:
                CTkLabel(
                    row_frame,
                    text=value,
                    font=("Inter", 14, "bold"),
                    text_color="#FFFFFF",
                    fg_color="#FF4B4B",
                    corner_radius=4,
                ).pack(side="left")
            else:
                if label == "Start Time:" or label == "End Time:":
                    font_size = 11
                    value = str(value)
                else:
                    font_size = 14
                    value = value
                CTkLabel(
                    row_frame,
                    text=value,
                    font=("Inter", font_size),
                    text_color="#FFFFFF"
                ).pack(side="left")

        # Person Image Box (Second Box)
        person_box = CTkFrame(
            info_boxes_frame,
            fg_color="#2C3656",
            border_width=1,
            border_color="#4A5567",
            corner_radius=12,
            width=240,
            height=265
        )
        person_box.pack(side="left", padx=10, fill="both", expand=True)
        person_box.pack_propagate(False)

        # Person Image Section
        person_section = CTkFrame(
            person_box,
            fg_color="transparent",
            height=130
        )
        person_section.pack(fill="x")

        person_title_frame = CTkFrame(
            person_section,
            fg_color="#3A4766",
            corner_radius=8,
            height=40
        )
        person_title_frame.pack(pady=(15, 5), padx=15, fill="x")

        CTkLabel(
            person_title_frame,
            text="Person Image",
            font=("Inter", 18, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=5)

        bgr_image_of_person = self.convert_rgb_to_bgr(selected_data["captured_img"])
        bgr_image_of_face = self.convert_rgb_to_bgr(selected_data["person_img"])

        # Convert the image to a format suitable for CTkLabel
        person_img = ImageTk.PhotoImage(bgr_image_of_person)
        face_img = ImageTk.PhotoImage(bgr_image_of_face)

        # Person Image
        if selected_data.get("captured_img"):
            CTkLabel(
                person_section,
                image=person_img,
                text=""
            ).pack(pady=5, padx=5)

        # Face Image
        face_title_frame = CTkFrame(
            person_section,
            fg_color="#3A4766",
            corner_radius=8,
            height=40
        )
        face_title_frame.pack(pady=(15, 5), padx=15, fill="x")

        CTkLabel(
            face_title_frame,
            text="Face Image",
            font=("Inter", 18, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=5)

        if selected_data.get("person_img"):
            CTkLabel(
                person_section,
                image=face_img,
                text=""
            ).pack(pady=5, padx=5)

        # Person Details Box (Third Box)
        details_box = CTkFrame(
            info_boxes_frame,
            fg_color="#2C3656",
            border_width=1,
            border_color="#4A5567",
            corner_radius=12,
            width=240,
            height=265
        )
        details_box.pack(side="left", padx=10, fill="both", expand=True)
        details_box.pack_propagate(False)

        details_title_frame = CTkFrame(
            details_box,
            fg_color="#3A4766",
            corner_radius=8,
            height=40
        )
        details_title_frame.pack(pady=(15, 10), padx=15, fill="x")

        CTkLabel(
            details_title_frame,
            text="Person Details",
            font=("Inter", 18, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=5)

        # Person Details Content
        person_content_frame = CTkFrame(details_box, fg_color="transparent")
        person_content_frame.pack(pady=10, padx=20, fill="both", expand=True)

        person_details = [
            ("Person Name:", selected_data.get("person_name", "Unknown")),
            ("Age:", selected_data.get("age", "Unknown")),
            ("Gender:", selected_data.get("gender", "Unknown")),
            ("Location:", "Main Entrance"),
            ("Department:", "Security")
        ]

        for label, value in person_details:
            row_frame = CTkFrame(person_content_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)

            CTkLabel(
                row_frame,
                text=label,
                font=("Inter", 14, "bold"),
                text_color="#B0B8C4",
                anchor="w"
            ).pack(side="left", padx=(0, 10))

            CTkLabel(
                row_frame,
                text=value,
                font=("Inter", 14),
                text_color="#FFFFFF"
            ).pack(side="left")

        # Acknowledgment Message Frame
        message_frame = CTkFrame(
            self.ack_frame,
            fg_color="transparent"
        )
        message_frame.pack(pady=(20, 15), padx=20, fill="x")

        CTkLabel(
            message_frame,
            text="Acknowledgment Message",
            font=("", 18, "bold"),
            anchor="center",
            justify="center",
            text_color="#FFFFFF"
        ).pack(pady=(0, 5), anchor="center")

        self.text_note = CTkTextbox(
            message_frame,
            width=700,
            height=100,
            text_color="black",
            fg_color="#E0E0E0",
            font=("Helvetica", 18, "bold"),
            border_color="#000000",
            border_width=2,
            corner_radius=8
        )
        self.text_note.pack(fill="x")

        # Buttons Frame
        frame_buttons = CTkFrame(
            self.ack_frame,
            fg_color="transparent"
        )
        frame_buttons.pack(pady=(15, 20))

        # Submit Button
        self.button_submit = CTkButton(
            frame_buttons,
            text="Submit",
            fg_color="#313A46",
            hover_color="#5A616B",
            width=110,
            height=35,
            corner_radius=6,
            font=("", 12, "bold"),
            command=self.handle_acknowledgment_submit
        )
        self.button_submit.pack(side="left", padx=5)

        # Cancel Button
        button_cancel = CTkButton(
            frame_buttons,
            text="Cancel",
            fg_color="#6C757D",
            hover_color="#5A6268",
            width=110,
            height=35,
            corner_radius=6,
            font=("", 12, "bold"),
            command=self.close_acknowledgment_frame
        )
        button_cancel.pack(side="left", padx=5)
        self.text_note.focus_force()

        # Keep references to the images to prevent garbage collection
        self.ack_window.person_img = person_img
        self.ack_window.face_img = face_img

        if hasattr(self, 'on_form_ready'):
            self.on_form_ready()

    def update_alarm_list(self, alarm_data_list=None, append=False):

        if alarm_data_list is None:
            alarm_data_list = getattr(self, 'vehicle_data', [])

        self.i_total_data = len(alarm_data_list)

        if not append:
            for widget in self.frame_content.winfo_children():
                widget.destroy()

        # Calculate pagination
        start_idx = self.i_start_index
        end_idx = min(start_idx + self.items_per_page, self.i_total_data)
        current_page_data = alarm_data_list[start_idx:end_idx]
        self.i_end_index = end_idx

        colors = {
            'primary': '#D81E5B',  # Bold crimson - signifies alert/danger
            'primary_light': '#FFE8ED',  # Light red for hover states
            'primary_dark': '#B3143F',  # Darker red for buttons hover
            'accent': '#00224D',  # Deep navy for authority/security
            'text_dark': '#1A1A2E',  # Deep navy text for readability
            'text_medium': '#394867',  # Medium slate for secondary text
            'text_light': '#8D93AB',  # Soft slate for tertiary text
            'bg_white': '#FFFFFF',  # Pure white background
            'bg_light': '#F8FAFC',  # Soft background for frames
            'border_light': '#E2E8F0',  # Light border for subtle division
            'border_focus': '#FFB8C9',  # Alert pinkish border on focus
            'status_bg': '#FFEBEE',  # Alert light red background
            'status_accent': '#D50000',  # Vibrant red for alert indicators
            'highlight': '#FFC107',  # Warning yellow for highlights
        }

        # Create striking card layouts for each alarm
        for i, data in enumerate(current_page_data, start=start_idx):
            # Add increased spacing between cards for better separation
            if i > start_idx:
                spacing_frame = CTkFrame(
                    self.frame_content,
                    fg_color="transparent",
                    height=12
                )
                spacing_frame.pack(fill="x", expand=False)

            # Main card container with enhanced shadow effect and proper sizing
            container_frame = CTkFrame(
                self.frame_content,
                fg_color=colors['bg_white'],
                corner_radius=16,  # Reduced to ensure proper rendering
                border_width=2,
                border_color=colors['border_light']
            )
            container_frame.pack(fill="x", expand=True, padx=24, pady=(0, 2))

            # Main alarm content frame with matching corner radius
            frame_alarm = CTkFrame(
                container_frame,
                fg_color=colors['bg_white'],
                height=250,
                corner_radius=14,  # Slightly smaller than container for proper nesting
            )
            frame_alarm.pack(fill="x", expand=True, pady=(8, 8), padx=6)  # Added horizontal padding
            frame_alarm.grid_propagate(False)
            frame_alarm.columnconfigure(1, weight=1)

            self.selected_frame = None

            # Create refined event handlers
            def create_click_handler(vehicle_event_id, frame, index):
                def handler(event):
                    # Reset all frames to original state
                    for container in self.frame_content.winfo_children():
                        if isinstance(container, CTkFrame) and container.winfo_children():
                            for widget in container.winfo_children():
                                if isinstance(widget, CTkFrame) and widget.winfo_height() > 10:
                                    widget.configure(fg_color=colors['bg_white'])

                    # Apply selection styling
                    frame.configure(fg_color=colors['primary_light'])

                    # Update selected state and activate acknowledge button
                    self.selected_vehicle = vehicle_event_id
                    if hasattr(self, 'button_acknowledge'):
                        self.button_acknowledge.configure(
                            state="normal",
                            fg_color=colors['primary'],
                            hover_color=colors['primary_dark'],
                            text_color=colors['bg_white']
                        )

                return handler

            def create_hover_enter_handler(frame):
                def handler(event):
                    if self.selected_vehicle and frame == self.selected_vehicle:
                        return

                    # Apply hover effect
                    frame.configure(fg_color=colors['bg_light'])

                    # Border highlight effect
                    if frame.master:
                        frame.master.configure(border_color=colors['primary'], border_width=2)

                return handler

            def create_hover_leave_handler(frame, index):
                def handler(event):
                    if self.selected_vehicle and frame == self.selected_vehicle:
                        frame.configure(fg_color=colors['primary_light'])
                        return

                    # Reset to default state
                    frame.configure(fg_color=colors['bg_white'])

                    # Reset container styling
                    if frame.master:
                        frame.master.configure(border_color=colors['border_light'], border_width=1)

                return handler

            # Bind sophisticated event handlers
            click_handler = create_click_handler(data.get("event_id"), frame_alarm, i)
            hover_enter_handler = create_hover_enter_handler(frame_alarm)
            hover_leave_handler = create_hover_leave_handler(frame_alarm, i)

            frame_alarm.bind("<Button-1>", click_handler)
            frame_alarm.bind("<Enter>", hover_enter_handler)
            frame_alarm.bind("<Leave>", hover_leave_handler)

            # Prepare images
            bgr_image_of_vehicle = self.convert_rgb_to_bgr(data.get("captured_img"))
            bgr_image_of_person = self.convert_rgb_to_bgr(data.get("person_img"))

            # Convert to format suitable for CTkLabel
            photo_path = ImageTk.PhotoImage(bgr_image_of_vehicle)
            captured_img = ImageTk.PhotoImage(bgr_image_of_person)

            # SIMPLIFIED LEFT IMAGE (VEHICLE) DISPLAY
            # Single frame with border and proper padding
            vehicle_frame = CTkFrame(
                frame_alarm,
                fg_color=colors['bg_white'],
                #fg_color="red",
                corner_radius=14,
                border_width=2,
                border_color=colors['primary']
               # border_color="#000000",
            )
            vehicle_frame.grid(row=0, column=0, sticky="nw", padx=22, pady=50)

            # Vehicle image with proper padding to avoid border overlap
            label_vehicle = CTkLabel(
                vehicle_frame,
                image=photo_path,
                text="",
                fg_color=colors['bg_white'],
                corner_radius=10,
            )
            label_vehicle.pack(padx=6, pady=6)

            # Central information panel
            frame_details = CTkFrame(
                frame_alarm,
                fg_color="transparent",
            )
            frame_details.grid(row=0, column=1, sticky="nsew", padx=12, pady=16)

            # Status indicator with enhanced corner radius
            status_frame = CTkFrame(
                frame_details,
                fg_color=colors['status_bg'],
                corner_radius=5,  # Increased corner radius
                height=42,
                border_width=1,
                border_color=colors['primary']
            )
            status_frame.grid(row=0, column=0, columnspan=2, sticky="w",padx=2, pady=(0, 20))

            # Status indicator dot
            status_icon = CTkFrame(
                status_frame,
                fg_color=colors['status_accent'],
                width=12,
                height=12,
                corner_radius=6
            )
            status_icon.pack(side="left", padx=(3, 5), pady=2)

            # Status label
            CTkLabel(
                status_frame,
                text="STATUS:",
                font=("Helvetica", 12, "bold"),
                text_color=colors['text_medium']
            ).pack(side="left", padx=(0, 0.1), pady=2)

            # Status text with warning styling
            event_type_label = CTkLabel(
                status_frame,
                text="UNAUTHORIZED PERSON",
                font=("Helvetica", 12, "bold"),
                text_color=colors['status_accent']
            )
            event_type_label.pack(side="left", pady=2,padx=4)

            # Information grid with security styling
            info_grid = CTkFrame(
                frame_details,
                fg_color="transparent"
            )
            info_grid.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=6)
            info_grid.columnconfigure(1, weight=1)
            info_grid.columnconfigure(3, weight=1)

            # Information layout - keeping all labels and values the same
            labels_data = [
                (0, 0, "Event Number:", data.get("event_id", "Unknown")),
                (0, 2, "Person Name:", data.get("person_name", "Unknown")),
                (1, 0, "Person Age:", data.get("age", "Unknown")),
                (1, 2, "Person Gender:", data.get("gender", "Unknown")),
                (2, 0, "Start Time:", data.get("start_time", "Unknown")),
                (2, 2, "End Time:", data.get("end_time", "Unknown"))
            ]

            # Create information fields with enhanced styling
            for row, col, label_text, value in labels_data:
                # Label with security-focused typography
                label_name = CTkLabel(
                    info_grid,
                    text=label_text,
                    font=("Helvetica", 14),
                    text_color=colors['text_medium']
                )
                label_name.grid(row=row, column=col, sticky="w", pady=12, padx=(0 if col == 0 else 28, 6))

                # Format value with fallback
                display_value = value if value is not None else "Unknown"

                # Value display with more prominent styling
                label_value = CTkLabel(
                    info_grid,
                    text=display_value,
                    font=("Helvetica", 15, "bold"),
                    text_color=colors['text_dark']
                )
                label_value.grid(row=row, column=col + 1, sticky="w", pady=12)

            # SIMPLIFIED RIGHT IMAGE (PERSON) DISPLAY
            # Single frame with border and proper padding
            person_frame = CTkFrame(
                frame_alarm,
                fg_color=colors['bg_white'],
                corner_radius=14,
                border_width=2,
                border_color=colors['primary']
            )
            person_frame.grid(row=0, column=2, padx=22, pady=22, sticky="e")

            # Person image with proper padding to avoid border overlap
            label_plate = CTkLabel(
                person_frame,
                image=captured_img,
                text="",
                fg_color=colors['bg_white'],
                corner_radius=10,
            )
            label_plate.pack(padx=6, pady=6)

            # Bind interaction events to all child widgets
            widgets_to_bind = [
                label_vehicle, label_plate, frame_details,
                event_type_label, status_frame, info_grid,
                vehicle_frame, person_frame
            ]

            for widget in widgets_to_bind:
                widget.bind("<Button-1>", click_handler)
                widget.bind("<Enter>", hover_enter_handler)
                widget.bind("<Leave>", hover_leave_handler)

        self.on_page_change()
        self.update_idletasks()
    def reset_interface(self):
        for widget in self.frame_content.winfo_children():
            widget.destroy()

