import base64
import os
from functools import partial
from io import BytesIO

from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCanvas, CTkScrollableFrame, CTkImage, CTkTextbox, \
    CTkToplevel, CTkFont
from tkinter import StringVar, Spinbox
from tkcalendar import Calendar
from PIL import Image, ImageTk, ImageOps, ImageEnhance
import datetime


class HistoricalEventInterface(CTkFrame):

    def __init__(self, *args, root_width: int = 1920, root_height: int = 1080, **kwargs):

        super().__init__(*args, **kwargs)

        self.bool_filter_popup = False
        self.bool_sdate_dropdown_opened = False
        self.bool_edate_dropdown_opened = False
        self.bool_vehicle_dropdown_opened = False
        self.current_vehicle_id = self.current_vehicle_number = ''
        self.current_person_image= self.current_captured_image= None
        self.label_imge=None
        self.event_starting_date = ""
        self.eventType = 0
        self.current_event_details= None
        self.add_vehicle_button= None
        self.configure(fg_color="#F1F5FA", corner_radius=0)

        self.i_start_index = 0
        self.i_end_index = 0
        self.i_total_data = 0
        self.dict_filter_criteria = {
            "str_start_timeperiod": "",
            "str_end_timeperiod": "",
            "str_vehicle_number": "%"
        }
        self.i_row_index = 1

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
        self.frame_form.rowconfigure(2, weight=1)
        self.frame_form.grid_propagate(False)
        self.frame_form.pack(side="top", expand=False, padx=10, pady=30)

        self.frame_header = CTkFrame(
            self.frame_form,
            height=int(i_form_height * 0.12),
            fg_color="transparent",
            corner_radius=10
        )
        self.frame_header.columnconfigure(0, weight=1)
        self.frame_header.columnconfigure(1, weight=1)
        self.frame_header.grid(column=0, row=0, sticky="we", padx=5, pady=(5, 15))

        self.label_heading = CTkLabel(
            self.frame_header,
            text="Historical Event",
            text_color="#2C2C2C",
            font=("", 18, "bold"),
            corner_radius=10,
            anchor="w",
            fg_color="transparent"
        )
        self.label_heading.grid(row=0, column=0, padx=10, pady=(15, 0), sticky="ew")

        self.label_Balance_count = CTkLabel(
            self.frame_header,
            text="Parked:",
            text_color="#2C2C2C",
            font=("", 16, "bold"),
            corner_radius=5,
            anchor="w",
            fg_color="transparent"
        )
        self.label_Balance_count.grid(row=0, column=2, padx=10, pady=(15, 0), sticky="ew")

        self.label_Balance_count_value = CTkLabel(
            self.label_Balance_count,
            text="0",
            text_color="White",
            font=("", 16, "bold"),
            corner_radius=5,
            anchor="w",
            fg_color="orange"
        )
        self.label_Balance_count_value.grid(row=0, column=2, padx=0, pady=(0, 0), sticky="nsew")

        self.label_Entry_count = CTkLabel(
            self.frame_header,
            text="Entry:",
            text_color="#2C2C2C",
            font=("", 16, "bold"),
            corner_radius=5,
            anchor="w",
            fg_color="transparent"
        )
        self.label_Entry_count.grid(row=0, column=3, padx=10, pady=(15, 0), sticky="ew")

        self.label_Entry_count_value = CTkLabel(
            self.label_Entry_count,
            text="0",
            text_color="White",
            font=("", 16, "bold"),
            corner_radius=5,
            anchor="w",
            fg_color="green"
        )
        self.label_Entry_count_value.grid(row=0, column=2, padx=0, pady=(0, 0), sticky="nsew")

        self.label_Exit_count = CTkLabel(
            self.frame_header,
            text="Exit:",
            text_color="#2C2C2C",
            font=("", 16, "bold"),
            corner_radius=5,
            anchor="w",
            fg_color="transparent"
        )
        self.label_Exit_count.grid(row=0, column=4, padx=10, pady=(15, 0), sticky="ew")

        self.label_Exit_count_value = CTkLabel(
            self.label_Exit_count,
            text="0",
            text_color="White",
            font=("", 16, "bold"),
            corner_radius=5,
            anchor="w",
            fg_color="red"
        )
        self.label_Exit_count_value.grid(row=0, column=2, padx=0, pady=(0, 0), sticky="nsew")

        self.button_filter = CTkButton(
            self.frame_header,
            height=38,
            width=100,
            text="Filter",
            text_color="#FFFFFF",
            fg_color="#5A616B",
            border_width=2,
            border_color="#313A46",
            font=("", 14),
            cursor="hand2",
            anchor="center",
            #hover=False,
            hover_color="#313A46"

        )
        self.button_filter.grid(row=0, column=5, padx=20, pady=(15, 0), sticky="e")

        self.canvas_underline = CTkCanvas(
            self.frame_form,
            height=1,
            bg="#D2D2D2",
            bd=0,
            highlightthickness=0
        )
        self.canvas_underline.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.frame_table = CTkScrollableFrame(
            self.frame_form,
            fg_color="transparent",
            corner_radius=0
        )
        self.frame_form.grid_propagate(False)
        self.frame_table.columnconfigure(0, weight=1)
        self.frame_table.grid(row=2, column=0, padx=(15, 2), pady=(10, 20), sticky="nsew")

        self.label_data_count = CTkLabel(
            self.frame_form,
            text="No Records Found!",
            text_color="#FF0000",
            font=("", 14),
        )
        self.label_data_count.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="w")

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

        self.frame_filter = CTkFrame(
            self.frame_form,
            width=500,
            height=450,
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
        self.frame_filter_form.columnconfigure((0, 1), weight=1, uniform='a')
        self.frame_filter_form.rowconfigure(2, weight=1)
        self.frame_filter_form.grid(row=0, column=0, padx=(2, 6), pady=(2, 5), sticky="nsew")

        self.label_filter_heading = CTkLabel(
            self.frame_filter_form,
            text="Filter Historical Event",
            text_color="#2C2C2C",
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
        self.canvas_filter_underline.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.frame_filter_form_lcol = CTkFrame(
            self.frame_filter_form,
            fg_color="transparent",
        )
        self.frame_filter_form_lcol.columnconfigure(0, weight=1)
        self.frame_filter_form_lcol.rowconfigure(7, weight=1)
        self.frame_filter_form_lcol.grid(row=2, column=0, sticky="nsew")

        self.frame_filter_form_rcol = CTkFrame(
            self.frame_filter_form,
            fg_color="transparent",
        )
        self.frame_filter_form_rcol.columnconfigure(0, weight=1)
        self.frame_filter_form_rcol.grid(row=2, column=1, sticky="nsew")

        self.lable_syear = CTkLabel(
            self.frame_filter_form_lcol,
            text="Start Date",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w",
            fg_color="transparent"
        )
        self.lable_syear.grid(row=0, column=0, padx=15, pady=(15, 0), sticky="ew")

        self.frame_syear_dropdown = CTkFrame(
            self.frame_filter_form_lcol,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_syear_dropdown.columnconfigure(0, weight=1)
        self.frame_syear_dropdown.rowconfigure(0, weight=1)
        self.frame_syear_dropdown.grid(row=1, column=0, padx=(15, 0), pady=(2, 0), sticky="ew")

        self.entry_selected_sdate = CTkEntry(
            self.frame_syear_dropdown,
            height=40,
            fg_color="#F6F6F6",
            textvariable=StringVar(value="DD-MM-YYYY"),
            text_color="#828282",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
            state="disabled"
        )
        self.entry_selected_sdate.grid(row=0, column=0, sticky="nsew")

        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\calendar_icon.png"), size=(20, 20))
        self.button_select_sdate = CTkButton(
            self.frame_syear_dropdown,
            image=img_down_arraow,
            height=25,
            width=20,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_sdate.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)

        self.lable_stime = CTkLabel(
            self.frame_filter_form_rcol,
            text="Start Time",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w",
            fg_color="transparent"
        )
        self.lable_stime.grid(row=0, column=0, padx=15, pady=(15, 0), sticky="ew")

        self.frame_main_stime = CTkFrame(
            self.frame_filter_form_rcol,
            height=40,
            fg_color="#F6F6F6",
            border_width=2,
            border_color="#DEDEDE",
            corner_radius=5,
        )
        self.frame_main_stime.grid_propagate(False)
        self.frame_main_stime.columnconfigure(0, weight=1)
        self.frame_main_stime.rowconfigure(0, weight=1)
        self.frame_main_stime.grid(row=1, column=0, padx=15, pady=(2, 0), sticky="ew")

        self.frame_sub_stime = CTkFrame(
            self.frame_main_stime,
            fg_color="#F6F6F6",
            height=40,
            border_width=0,
            corner_radius=5,
        )
        self.frame_sub_stime.grid(row=0, column=0, padx=30, pady=5, sticky="nsew")

        self.var_spinbox_shour = StringVar(value="00")
        self.spinbox_shour = Spinbox(
            self.frame_sub_stime,
            values=[f"{i:02}" for i in range(24)],
            textvariable=self.var_spinbox_shour,
            width=3,
            wrap=True,
            font=("", 14),
            justify="center",
            borderwidth=0,
            background="#F6F6F6",
            foreground="#414141"
        )
        self.spinbox_shour.pack(side="left")

        CTkLabel(
            self.frame_sub_stime,
            text=":",
            font=("", 14, "bold"),
            text_color="#414141"
        ).pack(side="left", padx=(10, 5))

        self.var_spinbox_sminute = StringVar(value="00")
        self.spinbox_sminute = Spinbox(
            self.frame_sub_stime,
            values=[f"{i:02}" for i in range(60)],
            textvariable=self.var_spinbox_sminute,
            width=3,
            wrap=True,
            font=("", 14),
            justify="center",
            borderwidth=0,
            background="#F6F6F6",
            foreground="#414141"
        )
        self.spinbox_sminute.pack(side="left")

        self.lable_eyear = CTkLabel(
            self.frame_filter_form_lcol,
            text="End Date",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w",
            fg_color="transparent"
        )
        self.lable_eyear.grid(row=2, column=0, padx=15, pady=(15, 0), sticky="ew")

        self.frame_syear_dropdown = CTkFrame(
            self.frame_filter_form_lcol,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_syear_dropdown.columnconfigure(0, weight=1)
        self.frame_syear_dropdown.rowconfigure(0, weight=1)
        self.frame_syear_dropdown.grid(row=3, column=0, padx=(15, 0), pady=(2, 0), sticky="ew")

        self.entry_selected_edate = CTkEntry(
            self.frame_syear_dropdown,
            height=40,
            fg_color="#F6F6F6",
            textvariable=StringVar(value="DD-MM-YYYY"),
            text_color="#828282",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
            state="disabled"
        )
        self.entry_selected_edate.grid(row=0, column=0, sticky="nsew")

        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\calendar_icon.png"), size=(20, 20))
        self.button_select_edate = CTkButton(
            self.frame_syear_dropdown,
            image=img_down_arraow,
            height=25,
            width=20,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_edate.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)

        self.lable_etime = CTkLabel(
            self.frame_filter_form_rcol,
            text="End Time",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w",
            fg_color="transparent"
        )
        self.lable_etime.grid(row=2, column=0, padx=15, pady=(15, 0), sticky="ew")

        self.frame_main_etime = CTkFrame(
            self.frame_filter_form_rcol,
            height=40,
            fg_color="#F6F6F6",
            border_width=2,
            border_color="#DEDEDE",
            corner_radius=5,
        )
        self.frame_main_etime.grid_propagate(False)
        self.frame_main_etime.columnconfigure(0, weight=1)
        self.frame_main_etime.rowconfigure(0, weight=1)
        self.frame_main_etime.grid(row=3, column=0, padx=15, pady=(2, 0), sticky="ew")

        self.frame_sub_etime = CTkFrame(
            self.frame_main_etime,
            fg_color="#F6F6F6",
            height=40,
            border_width=0,
            corner_radius=5,
        )
        self.frame_sub_etime.grid(row=0, column=0, padx=30, pady=5, sticky="nsew")

        self.var_spinbox_ehour = StringVar(value="00")
        self.spinbox_ehour = Spinbox(
            self.frame_sub_etime,
            values=[f"{i:02}" for i in range(24)],
            textvariable=self.var_spinbox_ehour,
            width=3,
            wrap=True,
            font=("", 14),
            justify="center",
            borderwidth=0,
            background="#F6F6F6",
            foreground="#414141"
        )
        self.spinbox_ehour.pack(side="left")

        CTkLabel(
            self.frame_sub_etime,
            text=":",
            font=("", 14, "bold"),
            text_color="#414141"
        ).pack(side="left", padx=(10, 5))

        self.var_spinbox_eminute = StringVar(value="00")
        self.spinbox_eminute = Spinbox(
            self.frame_sub_etime,
            values=[f"{i:02}" for i in range(60)],
            textvariable=self.var_spinbox_eminute,
            width=3,
            wrap=True,
            font=("", 14),
            justify="center",
            borderwidth=0,
            background="#F6F6F6",
            foreground="#414141"
        )
        self.spinbox_eminute.pack(side="left")

        self.lable_vehicle_number = CTkLabel(
            self.frame_filter_form_lcol,
            text="Person Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w",
            fg_color="transparent"
        )
        self.lable_vehicle_number.grid(row=4, column=0, padx=15, pady=(15, 0), sticky="ew")

        self.frame_vehicle_number_dropdown = CTkFrame(
            self.frame_filter_form_lcol,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_vehicle_number_dropdown.columnconfigure(0, weight=1)
        self.frame_vehicle_number_dropdown.rowconfigure(0, weight=1)
        self.frame_vehicle_number_dropdown.grid(row=5, column=0, padx=(15, 0), pady=(2, 0), sticky="ew")

        self.entry_selected_vehicle = CTkEntry(
            self.frame_vehicle_number_dropdown,
            height=40,
            fg_color="#F6F6F6",
            textvariable=StringVar(value="Select Vehicle"),
            text_color="#828282",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
            state="disabled"
        )
        self.entry_selected_vehicle.grid(row=0, column=0, sticky="nsew")

        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(20, 20))
        self.button_select_vehicle = CTkButton(
            self.frame_vehicle_number_dropdown,
            image=img_down_arraow,
            height=25,
            width=20,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_vehicle.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)

        CTkLabel(
            self.frame_filter_form_rcol,
            text="",
            font=("", 14),
        ).grid(row=4, column=0, padx=15, pady=(15, 0), sticky="ew")

        CTkFrame(
            self.frame_filter_form_rcol,
            height=40,
            fg_color="transparent",
        ).grid(row=5, column=0, padx=(15, 0), pady=(2, 0), sticky="ew")

        self.button_ok = CTkButton(
            self.frame_filter_form_lcol,
            height=38,
            width=100,
            text="Ok",
            text_color="#FFFFFF",
            hover_color="#313A46",
            fg_color="#5A616B",
            font=("", 14),
            cursor="hand2",
            hover=True
        )
        self.button_ok.grid(row=6, column=0, padx=(0, 3.75), pady=(25, 0), sticky="e")

        self.button_cancel = CTkButton(
            self.frame_filter_form_rcol,
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
        self.button_cancel.grid(row=6, column=0, padx=(3.75, 0), pady=(25, 0), sticky="w")

        self.frame_maindropdown_window = CTkFrame(
            self.frame_filter_form_lcol,
            fg_color="#DEDEDE",
            height=40,
            corner_radius=5
        )
        self.frame_maindropdown_window.columnconfigure(0, weight=1)
        self.frame_maindropdown_window.rowconfigure(0, weight=1)
        self.frame_maindropdown_window.grid_propagate(False)

    def convert_rgb_to_bgr(self, image_param):
        try:
            # Handle different types of image inputs
            if isinstance(image_param, Image.Image):
                image = image_param
            elif isinstance(image_param, CTkImage):
                # Access the _light_image attribute to get the underlying PIL image
                image = image_param._light_image
            elif isinstance(image_param, str):
                # Check if it's base64 encoded
                if image_param.startswith(('data:image', 'iVBOR', '/9j/')):
                    # Likely a base64 string
                    try:
                        image_data = base64.b64decode(image_param)
                        image = Image.open(BytesIO(image_data))
                    except Exception as e:
                        print(f"Error decoding base64 image: {e}")
                        return Image.new('RGB', (230, 185), color=(200, 200, 200))
                # Check if it's a file path
                elif os.path.exists(image_param):
                    image = Image.open(image_param)
                else:
                    print(f"Image file not found: {image_param}")
                    return Image.new('RGB', (230, 185), color=(200, 200, 200))
            else:
                print(f"Unsupported image type: {type(image_param)}")
                return Image.new('RGB', (230, 185), color=(200, 200, 200))

            # Ensure the image is in RGB mode
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Convert the image from RGB to BGR by reordering channels
            r, g, b = image.split()
            bgr_image = Image.merge("RGB", (b, g, r))
            return bgr_image
        except Exception as e:
            print(f"Error processing image: {e}")
            # Return a placeholder image when errors occur
            return Image.new('RGB', (230, 185), color=(200, 200, 200))
    def show_ack_popup(self, message):
        # Destroy any existing popup before creating a new one
        # if self.popup.winfo_exists():
        #     self.popup.lift()
        #     return


        self.popup = CTkToplevel(self)
        self.popup.title("")
        self.popup.configure(fg_color="#FFFFFF")

        # Remove window decorations
        self.popup.overrideredirect(True)
        self.popup.protocol("WM_DELETE_WINDOW", self.cleanup_popup)
        # Get the cursor position for popup placement
        cursor_x = self.popup.winfo_pointerx()
        cursor_y = self.popup.winfo_pointery()

        # Set popup dimensions
        self.popup_width = 300
        self.popup_height = 170

        # Position popup near cursor
        pos_x = cursor_x - (self.popup_width // 2)
        pos_y = cursor_y - self.popup_height - 10

        # Set the new position and size
        self.popup.geometry(f"{self.popup_width}x{self.popup_height}+{pos_x}+{pos_y}")

        # Create main content frame with premium styling
        content_frame = CTkFrame(self.popup, fg_color="#1E293B", corner_radius=12)
        content_frame.pack(fill="both", expand=True, padx=2, pady=3)

        # Add a decorative header with premium color
        header_frame = CTkFrame(content_frame, height=40, fg_color="#0F172A", corner_radius=10)
        header_frame.pack(fill="x", padx=2, pady=(2, 5))

        # Add logo/icon in header
        logo_label = CTkLabel(
            header_frame,
            text="",
            font=("", 20),
            text_color="#60A5FA",
        )
        logo_label.pack(side="left", padx=10, pady=5)

        # Add header text with premium styling
        header_label = CTkLabel(
            header_frame,
            text="Acknowledgment Message",
            font=("Inter", 14, "bold"),
            text_color="#F1F5F9",
        )
        header_label.pack(side="left", padx=25, pady=5)

        self.text_area = CTkTextbox(
            content_frame,
            width=280,
            height=70,
            font=("Inter", 12),
            fg_color="#334155",
            text_color="#F8FAFC",
            border_color="#475569",
            border_width=1,
            corner_radius=8
        )
        self.text_area.pack(padx=10, pady=(5, 10))
        self.text_area.insert("1.0", message)
        self.text_area.configure(state="disabled")

        close_button = CTkButton(
            content_frame,
            text="Close",
            width=60,
            height=35,
            fg_color="#0066FF",
            hover_color="#0052CC",
            text_color="#FFFFFF",
            corner_radius=4,
            font=("", 12),
            command=self.hide_popup
        )
        close_button.pack(pady=(0, 12))

        # Add premium shadow effect
        self.popup.configure(border_width=1, border_color="#1E293B")

        # Make popup stay on top
        self.popup.attributes('-topmost', True)

        # Add binding to close popup when clicking outside
        def check_mouse_position(event):
            if not (0 <= event.x <= self.popup.winfo_width() and 0 <= event.y <= self.popup.winfo_height()):
                self.hide_popup()

        self.popup.bind('<Button-1>', check_mouse_position)

        # Function to handle popup movement
        # def move_popup(e):
        #     self.popup.geometry(f'+{e.x_root - self.popup_width // 2}+{e.y_root - self.popup_height // 2}')
        #
        # #Allow dragging the popup by the header
        # header_frame.bind('<B1-Motion>', move_popup)
        #
        # #Bind the popup destruction to the widget destruction
        # self.bind('<Destroy>', lambda e: self.cleanup_popup())

    def hide_popup(self):

        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()


    def cleanup_popup(self):
        """Ensure popup is destroyed when the main widget is destroyed"""
        if hasattr(self, 'popup'):
            self.popup.destroy()
        if hasattr(self, 'ack_window'):
            self.ack_window.destroy()

    def on_row_click(self, event, event_id_current, vehicle_number, personimg=None, capturedimg=None, eventdata=None,
                     eventType=None):
        print(f"Row {event_id_current} clicked! Vehicle: {vehicle_number} with {eventType}")
        self.current_vehicle_number = vehicle_number
        self.current_vehicle_id = event_id_current
        self.current_person_image = personimg
        self.current_captured_image = capturedimg
        self.current_event_details = eventdata
        self.eventType = eventType

    def format_label(self, label, max_length=12):
        return f"{label.ljust(max_length)} : "

    def update_table(self, list_historical_events: list):
        event_details = None
        # Clear existing table content
        for child in self.frame_table.winfo_children():
            child.destroy()


        # Define premium color scheme with consistent row color
        COLORS = {
            "primary": "#2563EB",  # Royal blue
            "primary_dark": "#1E40AF",  # Deep blue
            "secondary": "#7C3AED",  # Purple
            "accent": "#EFF6FF",  # Lightest blue
            "success": "#10B981",  # Emerald green
            "warning": "#F59E0B",  # Amber
            "danger": "#EF4444",  # Red
            "text_primary": "#1E293B",  # Dark slate
            "text_secondary": "#64748B",  # Medium slate
            "background": "#FFFFFF",  # White
            "card": "#F8FAFC",  # Light gray (consistent card color)
            "border": "#E2E8F0"  # Light border color
        }

        # Status configuration with premium styling
        status_config = {
            0: {
                "border_color": COLORS["warning"],
                "status": "Unknown",
                "bg_color": "#FFF7ED",
                "icon": "⚠️"
            },
            1: {
                "border_color": COLORS["success"],
                "status": "Verified",
                "bg_color": "#ECFDF5",
                "icon": "✓"
            },
            2: {
                "border_color": COLORS["danger"],
                "status": "Restricted",
                "bg_color": "#FEF2F2",
                "icon": "⛔"
            }
        }

        # Create stylish glass-morphism header
        header_frame = CTkFrame(
            self.frame_table,
            fg_color="#232E51",
            corner_radius=7,
            height=60
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))
        header_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        header_frame.grid_propagate(False)

        # Stylish header columns with icons
        header_data = [
            {"text": "Captured Image", "icon": "📸"},
            {"text": "Identity Details", "icon": "🪪"},
            {"text": "Activity Timeline", "icon": "📊"},
            {"text": "Actual Image", "icon": "👤"}
        ]

        for idx, header in enumerate(header_data):
            header_container = CTkFrame(
                header_frame,
                fg_color="transparent"
            )
            header_container.grid(row=0, column=idx, padx=10, pady=15, sticky="ew")

            CTkLabel(
                header_container,
                text=f"{header['icon']} {header['text']}",
                font=CTkFont(family="Helvetica", size=16, weight="bold"),
                text_color="white",
                anchor="center",
            ).pack(expand=True)

        # Add elegant spacing
        spacer = CTkFrame(self.frame_table, height=5, fg_color="transparent")
        spacer.grid(row=1, column=0)

        for row_index, row_data in enumerate(list_historical_events):
            # Use consistent color for all rows
            row_bg_color = COLORS["card"]

            event_details = row_data

            # Convert and process images
            bgr_image_of_person = self.convert_rgb_to_bgr(row_data["photo_path"])
            bgr_image_of_captured = self.convert_rgb_to_bgr(row_data["captured_img"])

            # Set identical image dimensions for both images
            image_width, image_height = 230, 185

            # Resize with high-quality resampling


            # Apply image enhancements for person image
            person_img_pil = bgr_image_of_person.resize(
                (image_width, image_height),
                Image.Resampling.LANCZOS
            )
            # Add premium image enhancements
            person_img_pil = ImageOps.autocontrast(person_img_pil, cutoff=0.5)
            person_img_pil = ImageEnhance.Sharpness(person_img_pil).enhance(1.5)
            person_img_pil = ImageEnhance.Contrast(person_img_pil).enhance(1.2)

            # Apply image enhancements for captured image
            captured_img_pil = bgr_image_of_captured.resize(
                (image_width, image_height),
                Image.Resampling.LANCZOS
            )
            captured_img_pil = ImageOps.autocontrast(captured_img_pil, cutoff=0.5)
            captured_img_pil = ImageEnhance.Sharpness(captured_img_pil).enhance(1.5)
            captured_img_pil = ImageEnhance.Contrast(captured_img_pil).enhance(1.2)

            # Convert to PhotoImage
            person_img = ImageTk.PhotoImage(person_img_pil)
            captured_img = ImageTk.PhotoImage(captured_img_pil)

            # Apply premium card-like frame with subtle shadow and border
            frame_row = CTkFrame(
                self.frame_table,
                height=220,
                fg_color=row_bg_color,
                corner_radius=20,
                border_width=2,
                border_color=COLORS["border"]
            )

            frame_row.columnconfigure((0, 1, 2, 3), weight=1)
            frame_row.rowconfigure(0, weight=1)
            frame_row.grid_propagate(False)
            frame_row.grid(row=row_index + 2, column=0, sticky="nsew", padx=20, pady=12)

            # Get current status
            alarm_value = int(row_data.get("alarm", "0"))

            # SWAPPED: Now showing captured image in first column
            # Apply status-specific border color to captured image container
            img_frame = CTkFrame(
                frame_row,
                corner_radius=15,
                fg_color=COLORS["accent"],
                border_width=1,
                border_color=status_config[alarm_value]["border_color"]  # Status-specific border color
            )
            img_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)

            # Create stylish label for captured image (previously for person image)
            label_imge = CTkLabel(
                img_frame,
                image=captured_img,  # SWAPPED: Using captured_img instead of person_img
                text="",
                height=image_height,
                width=image_width,
                fg_color="transparent",
                corner_radius=12
            )
            label_imge.pack(padx=5, pady=5)

            # Add stylish floating badge with serial number
            serial_badge = CTkFrame(
                img_frame,
                fg_color="#232E51",
                corner_radius=12,
                height=28,
                width=50
            )
            serial_badge.place(x=10, y=10)

            CTkLabel(
                serial_badge,
                fg_color="#232E51",
                text=f"#{self.i_row_index}",
                font=CTkFont(family="Helvetica", size=14, weight="bold"),
                text_color="white"
            ).pack(padx=8, pady=3)

            # Details frame with modern styling
            frame_details = CTkFrame(
                frame_row,
                height=190,
                fg_color="transparent",
                corner_radius=12
            )
            frame_details.rowconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="row_height")
            frame_details.columnconfigure(0, weight=1)
            frame_details.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

            # Section title with modern styling
            section_title = CTkFrame(
                frame_details,
                fg_color="#232E51",
                corner_radius=5,
                height=32
            )
            section_title.grid(row=0, column=0, sticky="w", pady=(0, 10))

            CTkLabel(
                section_title,
                text="  Identity Information  ",
                font=CTkFont(family="Helvetica", size=14, weight="bold"),
                text_color="white"
            ).pack(padx=10, pady=4)

            # Map status values to Person Type
            status_types = {
                0: "Unknown",
                1: "Verified",
                2: "Restricted"
            }
            alarm_value = int(row_data.get("alarm", "0"))
            person_type = status_types.get(alarm_value, "Unknown")

            # Format timestamps with elegant styling
            from datetime import datetime

            def format_timestamp(timestamp_value):
                if not timestamp_value:
                    return "N/A"
                try:
                    timestamp = float(timestamp_value)
                    if timestamp > 0:
                        return datetime.fromtimestamp(timestamp).strftime('%b %d, %Y • %H:%M:%S')
                    return "N/A"
                except (ValueError, TypeError):
                    return str(timestamp_value)

            start_time_formatted = format_timestamp(row_data.get("start_time"))
            end_time_formatted = format_timestamp(row_data.get("end_time"))

            # Modern field mappings with icons
            field_mappings = {
                "person_name": {"title": "Person Name", "value": row_data.get("person_name", ""), "icon": "👤"},
                "age": {"title": "Age", "value": row_data.get("person_age", ""), "icon": "🔢"},
                "gender": {"title": "Gender", "value": row_data.get("person_gender", ""), "icon": "⚧️"},
                "person_type": {"title": "Status", "value": person_type, "icon": status_config[alarm_value]["icon"]},
                "Camera Name": {"title": "Camera Name", "value": "Entry Gate", "icon": "📸"}
            }

            # Create elegant info fields with modern styling
            for idx, (key, data) in enumerate(field_mappings.items()):
                frame_cell = CTkFrame(
                    frame_details,
                    fg_color="transparent",
                    corner_radius=8,
                    height=30
                )
                frame_cell.grid(row=idx + 1, column=0, sticky="ew", pady=3)

                # Icon container with accent circle
                icon_container = CTkFrame(
                    frame_cell,
                    width=30,
                    height=30,
                    corner_radius=15,
                    fg_color=COLORS["accent"],
                )
                icon_container.pack(side="left", padx=(5, 10))
                icon_container.pack_propagate(False)

                # Center the icon in the circle
                CTkLabel(
                    icon_container,
                    text=data["icon"],
                    font=CTkFont(size=16),
                    width=20,
                    height=20,
                    fg_color="transparent"
                ).place(relx=0.5, rely=0.5, anchor="center")

                # Label with premium styling
                CTkLabel(
                    frame_cell,
                    text=f"{data['title']}:",
                    font=CTkFont(family="Helvetica", size=14, weight="bold"),
                    text_color=COLORS["primary_dark"],
                    width=110,
                    anchor="w"
                ).pack(side="left")

                # Special styling for status field
                if key == "person_type":
                    status_label = CTkLabel(
                        frame_cell,
                        text=data["value"],
                        font=CTkFont(family="Helvetica", size=13, weight="bold"),
                        text_color="white",
                        fg_color=status_config[alarm_value]["border_color"],
                        #fg_color="red",
                        corner_radius=4,
                        width=130,
                        height=26
                    )
                    status_label.pack(side="left", padx=1)
                else:
                    CTkLabel(
                        frame_cell,
                        text=data["value"],
                        font=CTkFont(family="Helvetica", size=13),
                        text_color=COLORS["text_secondary"],
                        anchor="w"
                    ).pack(side="left", padx=5)

            # Timeline frame with elegant styling
            frame_additional_details = CTkFrame(
                frame_row,
                height=190,
                width=400,
                fg_color="transparent",
                corner_radius=12
            )
            frame_additional_details.grid(row=0, column=2, sticky="nsew", padx=15, pady=15)
            frame_additional_details.grid_propagate(False)

            # Create stylish timeline container
            timeline_container = CTkFrame(
                frame_additional_details,
                fg_color=COLORS["accent"],
                corner_radius=15,
                border_width=2,
                border_color=COLORS["border"],
                height=190,
                width=300
            )
            timeline_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
            timeline_container.pack_propagate(False)

            # First seen entry with small green dot
            first_seen_frame = CTkFrame(
                timeline_container,
                fg_color="transparent"
            )
            first_seen_frame.pack(fill="x", padx=15, pady=(15, 5))

            # Small green dot (10x10 pixels)
            first_seen_dot = CTkFrame(
                first_seen_frame,
                width=10,
                height=10,
                corner_radius=5,
                fg_color=COLORS["success"]
            )
            first_seen_dot.pack(side="left", padx=(5, 10))

            # First seen content
            first_seen_content = CTkFrame(
                first_seen_frame,
                fg_color="transparent"
            )
            first_seen_content.pack(side="left", fill="x", expand=True)

            CTkLabel(
                first_seen_content,
                text="First Seen",
                font=CTkFont(family="Helvetica", size=13, weight="bold"),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).pack(side="top", anchor="w")

            CTkLabel(
                first_seen_content,
                text=start_time_formatted,
                font=CTkFont(family="Helvetica", size=12),
                text_color=COLORS["text_secondary"],
                anchor="w"
            ).pack(side="top", anchor="w")

            # Add connector line
            line_frame = CTkFrame(
                timeline_container,
                width=2,
                height=30,
                fg_color=COLORS["border"]
            )
            line_frame.pack(padx=(9, 0), anchor="w")

            # Last seen entry with small red dot
            last_seen_frame = CTkFrame(
                timeline_container,
                fg_color="transparent"
            )
            last_seen_frame.pack(fill="x", padx=15, pady=(5, 15))

            # Small red dot (10x10 pixels)
            last_seen_dot = CTkFrame(
                last_seen_frame,
                width=10,
                height=10,
                corner_radius=5,
                fg_color=COLORS["danger"]
            )
            last_seen_dot.pack(side="left", padx=(5, 10))

            # Last seen content
            last_seen_content = CTkFrame(
                last_seen_frame,
                fg_color="transparent"
            )
            last_seen_content.pack(side="left", fill="x", expand=True)

            CTkLabel(
                last_seen_content,
                text="Last Seen",
                font=CTkFont(family="Helvetica", size=13, weight="bold"),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).pack(side="top", anchor="w")

            CTkLabel(
                last_seen_content,
                text=end_time_formatted,
                font=CTkFont(family="Helvetica", size=12),
                text_color=COLORS["text_secondary"],
                anchor="w"
            ).pack(side="top", anchor="w")

            # Get current status configuration
            alarm_value = int(row_data.get("alarm", "0"))
            current_status = status_config.get(alarm_value)

            event_id_current = row_data.get("event_id", "")
            person_name_current = row_data.get("person_name", "")
            eventType = alarm_value

            # SWAPPED: Now showing person image in the final column with a simple border
            plate_container = CTkFrame(
                frame_row,
                fg_color="white",
                width=image_width + 20,
                height=image_height + 20,
                corner_radius=18,
                border_width=2,
                border_color=COLORS["border"]  # Using standard border color for person image
            )
            plate_container.grid(row=0, column=3, sticky="e", padx=20, pady=15)
            plate_container.grid_propagate(False)

            # Create enhanced image label - SWAPPED to show person_img
            self.label_imge = CTkLabel(
                plate_container,
                image=person_img,  # SWAPPED: Using person_img instead of captured_img
                text="",
                height=image_height,
                width=image_width,
                cursor='hand2',
                fg_color="transparent",
                corner_radius=12
            )
            self.label_imge.pack(padx=8, pady=8, expand=True)

            # Add modern view button
            view_button = CTkButton(
                plate_container,
                text="View Details",
                width=120,
                height=30,
                corner_radius=15,
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_dark"],
                text_color="white",
                font=CTkFont(family="Helvetica", size=12, weight="bold"),
                command=lambda event_id=event_id_current,
                               vehicle=person_name_current,
                               pimg=person_img,
                               cimg=captured_img,
                               evdata=event_details,
                               evtype=eventType: self.on_row_click(None, event_id, vehicle, pimg, cimg, evdata, evtype)
            )
            view_button.pack(pady=8)

            # Add click event
            self.label_imge.bind("<Button-1>",
                                 partial(self.on_row_click,
                                         event_id_current=event_id_current,
                                         vehicle_number=person_name_current,
                                         personimg=person_img,
                                         capturedimg=captured_img,
                                         eventdata=event_details,
                                         eventType=eventType))

            # Create tooltip without hover effects
            self.create_tooltip(self.label_imge, "Click to view detailed information")

            # Increment row index counters
            self.i_row_index += 1

        # Add pagination controls
        self.on_page_change()

        # Add stylish empty state if no rows
        if len(list_historical_events) == 0:
            empty_frame = CTkFrame(
                self.frame_table,
                fg_color=COLORS["accent"],
                corner_radius=20,
                height=300
            )
            empty_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)

            CTkLabel(
                empty_frame,
                text="No Records Found",
                font=CTkFont(family="Helvetica", size=22, weight="bold"),
                text_color=COLORS["primary_dark"]
            ).pack(pady=(100, 10))

            CTkLabel(
                empty_frame,
                text="There are no historical events to display at this time",
                font=CTkFont(family="Helvetica", size=14),
                text_color=COLORS["text_secondary"]
            ).pack()
    def create_acknowledgment_frame(self, event_data=None, vehicle_data=None, person_image=None,
                                    captured_image=None, data=None, eventType: int = None):
        # First, properly cleanup any existing window
        self.cleanup_popup()

        # Determine event type and heading based on eventType
        event_type_map = {
            0: {"type": "Unknown", "heading": "Un-Registered Person Details", "color": "#FFC107"},  # Amber for unknown
            1: {"type": "Verified", "heading": "Authorized Person Details", "color": "#4CAF50"},  # Green for authorized
            2: {"type": "Blacklisted", "heading": "Restricted Person Details", "color": "#F44336"}  # Red for restricted
        }

        event_info = event_type_map.get(eventType, {"type": "Unknown", "heading": "Un-Registered Person Details",
                                                    "color": "#FFC107"})
        event_type = event_info["type"]
        heading = event_info["heading"]
        status_color = event_info["color"]

        # Process event data
        if event_data is None and data:
            event_data = [
                {"label": "Person Name", "value": data[0]},
                {"label": "Event No", "value": "35098"},
                {"label": "Gender", "value": "Leaving"},
                {"label": "Starting Time", "value": "05.17:35"},
                {"label": "Status", "value": event_type}
            ]
        else:
            event_data = [
                {"label": "Person Name", "value": event_data.get("vehicle_number", "N/A")},
                {"label": "Event No", "value": event_data.get("event_id", "N/A")},
                {"label": "Gender", "value": event_data.get("status", "N/A")},
                {"label": "Starting Time", "value": event_data.get("time", "N/A")},
                {"label": "Status", "value": event_type}
            ]

        if vehicle_data is None and data:
            vehicle_data = [
                {"label": "Model Name", "value": data[3]},
                {"label": "Color", "value": data[5]},
                {"label": "Vehicle Type", "value": data[4]},
                {"label": "Mfg Year", "value": data[7]},
                {"label": "Owner Name", "value": data[6]}
            ]

        # Window setup with modern dark theme
        self.ack_window = CTkToplevel()
        self.ack_window.geometry("950x550")
        self.ack_window.title("Face Recognition")
        self.ack_window.configure(bg="#121828")  # Darker background for premium look
        self.ack_window.resizable(False, False)
        self.ack_window.attributes("-topmost", True)

        # Centering the window
        self.ack_window.update_idletasks()
        screen_width = self.ack_window.winfo_screenwidth()
        screen_height = self.ack_window.winfo_screenheight()
        x_position = (screen_width - 950) // 2
        y_position = (screen_height - 550) // 2
        self.ack_window.geometry(f"950x550+{x_position}+{y_position}")

        # Main frame with gradient effect
        self.ack_frame = CTkFrame(
            self.ack_window,
            width=950,
            height=550,
            fg_color="#121828",  # Dark blue-black background
            corner_radius=7,  # Rounded corners
            border_width=1,
            border_color="#3B4B88"  # Subtle border
        )
        self.ack_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.ack_frame.grid_propagate(False)

        # Add header with premium styling
        header_frame = CTkFrame(
            self.ack_frame,
            fg_color="#1A2138",  # Slightly lighter than background
            height=60,
            width=930,
            corner_radius=10
        )
        header_frame.pack(fill="x", pady=(15, 20), padx=15)

        # Add logo or icon (placeholder)
        logo_label = CTkLabel(
            header_frame,
            text="🔒",
            font=("Inter", 24),
            text_color="#4D79FF",
            bg_color="transparent"
        )
        logo_label.pack(side="left", padx=(15, 5))

        # Title with gradient-like effect
        title_label = CTkLabel(
            header_frame,
            text="FACE RECOGNITION ",
            font=("Inter", 18, "bold"),
            text_color="#4D79FF",  # Blue accent color
            bg_color="transparent"
        )
        title_label.pack(side="left", padx=5)

        # Status indicator
        status_frame = CTkFrame(
            header_frame,
            fg_color="transparent",
            height=40
        )
        status_frame.pack(side="right", padx=15)

        status_indicator = CTkFrame(
            status_frame,
            width=12,
            height=12,
            corner_radius=6,
            fg_color=status_color  # Dynamic color based on event type
        )
        status_indicator.pack(side="left", padx=(0, 8))

        status_text = CTkLabel(
            status_frame,
            text=event_type.upper(),
            font=("Inter", 14, "bold"),
            text_color=status_color,  # Dynamic color based on event type
            bg_color="transparent"
        )
        status_text.pack(side="left")

        # Subtitle showing the category
        subtitle_frame = CTkFrame(
            self.ack_frame,
            fg_color="transparent"
        )
        subtitle_frame.pack(fill="x", pady=(0, 15), padx=20)

        CTkLabel(
            subtitle_frame,
            text=heading,
            font=("Inter", 16, "bold"),
            text_color="#FFFFFF",
            bg_color="transparent"
        ).pack(side="left")

        # Information boxes frame with better spacing
        info_boxes_frame = CTkFrame(
            self.ack_frame,
            fg_color="transparent"
        )
        info_boxes_frame.pack(pady=5, padx=20, fill="both", expand=True)

        # Left Box for Person Image with enhanced styling
        left_box = CTkFrame(
            info_boxes_frame,
            fg_color="#1A2138",
            border_width=1,
            border_color="#3B4B88",  # Subtle border
            corner_radius=10,
            width=440,
            height=380
        )
        left_box.pack(side="left", padx=(0, 10), fill="both", expand=True)
        left_box.pack_propagate(False)

        # Left box header
        left_header = CTkFrame(
            left_box,
            fg_color="#232942",  # Slightly darker than the box
            corner_radius=8,
            height=40
        )
        left_header.pack(fill="x", padx=10, pady=10)

        CTkLabel(
            left_header,
            text="FACIAL IDENTIFICATION",
            font=("Inter", 14, "bold"),
            text_color="#FFFFFF",
            bg_color="transparent"
        ).pack(pady=5)

        # Person Image Container with overlay effects
        if person_image:
            person_image_container = CTkFrame(
                left_box,
                fg_color="transparent",
            )
            person_image_container.pack(expand=True, fill="both", padx=20, pady=(5, 20))

            # Calculate appropriate image size
            container_width = 380
            container_height = 280
            person_imagen = self.resize_ctk_image(person_image, (container_width, container_height))

            # Image with facial recognition overlay hint
            image_frame = CTkFrame(
                person_image_container,
                fg_color="#121828",
                corner_radius=8,
                border_width=1,
                border_color="#3B4B88"
            )
            image_frame.pack(expand=True, fill="both")

            CTkLabel(
                image_frame,
                image=person_imagen,
                text="",
            ).pack(expand=True, pady=10, padx=10)
        else:
            # Placeholder for when no image is available
            placeholder_frame = CTkFrame(
                left_box,
                fg_color="#121828",
                corner_radius=8,
                border_width=1,
                border_color="#3B4B88",
                width=380,
                height=280
            )
            placeholder_frame.pack(expand=True, fill="both", padx=20, pady=(5, 20))

            CTkLabel(
                placeholder_frame,
                text="NO FACIAL DATA",
                font=("Inter", 14),
                text_color="#6D7A9E",
            ).pack(expand=True)

        # Right Box with enhanced styling
        right_box = CTkFrame(
            info_boxes_frame,
            fg_color="#1A2138",  # Slightly lighter than main background
            border_width=1,
            border_color="#3B4B88",  # Subtle border
            corner_radius=10,
            width=440,
            height=380
        )
        right_box.pack(side="right", padx=(10, 0), fill="both", expand=True)
        right_box.pack_propagate(False)

        # Right box header
        person_name = data[0] if data else event_data[0]["value"]
        name_header = CTkFrame(
            right_box,
            fg_color="#232942",  # Slightly darker than the box
            corner_radius=8,
            height=40
        )
        name_header.pack(fill="x", padx=10, pady=10)

        CTkLabel(
            name_header,
            text="Anupriya Shahdeo",
            font=("Inter", 18, "bold"),
            text_color="#FFFFFF",
            bg_color="transparent"
        ).pack(pady=5)

        # Right box content frame
        right_content_frame = CTkFrame(
            right_box,
            fg_color="transparent"
        )
        right_content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Image frame with enhanced border for captured image
        capture_frame = CTkFrame(
            right_content_frame,
            fg_color="#121828",
            border_width=1,
            border_color="#3B4B88",
            corner_radius=8,
            width=180,
            height=180
        )
        capture_frame.pack(side="left", padx=(0, 15), anchor="nw")
        capture_frame.pack_propagate(False)


        if captured_image:
            inner_frame = CTkFrame(
                capture_frame,
                fg_color="transparent",
            )
            inner_frame.pack(expand=True, fill="both", padx=8, pady=8)

            captured_imagen = self.resize_ctk_image(captured_image, (160, 160))
            CTkLabel(
                inner_frame,
                image=captured_imagen,
                text="",
            ).pack(expand=True, fill="both")
        else:
            # Styled placeholder if no image provided
            dummy_frame = CTkFrame(
                capture_frame,
                fg_color="#161C30",
                width=160,
                height=160,
                corner_radius=8
            )
            dummy_frame.pack(expand=True, fill="both", padx=8, pady=8)

            CTkLabel(
                dummy_frame,
                text="Live Capture",
                text_color="#6D7A9E",
                font=("Inter", 12)
            ).pack(expand=True)

        # Split data fields into two sections - main data and the two fields that need to start from bottom of image
        main_data = [
            {"label": "Age", "value": "35", "icon": "👤"},
            {"label": "Gender", "value": "Male", "icon": "📏"},
            {"label": "Person Type", "value": "185 lbs", "icon": "⚖️"},
            {"label": "Hair Color", "value": "Black", "icon": "💈"},
            {"label": "Eye Color", "value": "Brown", "icon": "👁️"}
        ]

        bottom_data = [
            {"label": "Starting Time", "value": "2025-12-1 20:35", "icon": "⌚"},
            {"label": "Ending Time", "value": "2025-12-1 20:35", "icon": "⌚"}
        ]

        # Main data frame for standard fields
        data_frame = CTkFrame(
            right_content_frame,
            fg_color="transparent"
        )
        data_frame.pack(side="left", fill="both", expand=True, anchor="n")

        # Add main information with premium styling
        for item in main_data:
            row_frame = CTkFrame(
                data_frame,
                fg_color="#232942",
                corner_radius=6,
                height=28
            )
            row_frame.pack(fill="x", pady=4, anchor="w")

            # Optional icon for visual enhancement
            if "icon" in item:
                CTkLabel(
                    row_frame,
                    text=item["icon"],
                    font=("Inter", 12),
                    width=25,
                    anchor="w"
                ).pack(side="left", padx=(8, 0))

            CTkLabel(
                row_frame,
                text=item["label"] + ":",
                font=("Inter", 12, "bold"),
                text_color="#A0AEC0",  # Lighter gray for label
                anchor="w",
                width=100  # Fixed width for alignment
            ).pack(side="left", padx=(5, 0))

            CTkLabel(
                row_frame,
                text=item["value"],
                font=("Inter", 12),
                text_color="#FFFFFF",
                anchor="w"
            ).pack(side="left")

        # Create a container for the address and marital status that will be positioned below the image
        bottom_container = CTkFrame(
            right_box,
            fg_color="transparent"
        )
        bottom_container.pack(fill="x", padx=15, pady=(0, 50), side="bottom")

        # Add address and marital status fields
        for item in bottom_data:
            row_frame = CTkFrame(
                bottom_container,
                fg_color="#232942",
                corner_radius=6,
                height=28
            )
            row_frame.pack(fill="x", pady=4, anchor="w")

            # Optional icon for visual enhancement
            if "icon" in item:
                CTkLabel(
                    row_frame,
                    text=item["icon"],
                    font=("Inter", 12),
                    width=25,
                    anchor="w"
                ).pack(side="left", padx=(8, 0))

            CTkLabel(
                row_frame,
                text=item["label"] + ":",
                font=("Inter", 12, "bold"),
                text_color="#A0AEC0",  # Lighter gray for label
                anchor="w",
                width=100  # Fixed width for alignment
            ).pack(side="left", padx=(5, 0))

            CTkLabel(
                row_frame,
                text=item["value"],
                font=("Inter", 12),
                text_color="#FFFFFF",
                anchor="w"
            ).pack(side="left")

        # Footer with action buttons
        footer_frame = CTkFrame(
            self.ack_frame,
            fg_color="transparent",
            height=50
        )
        footer_frame.pack(fill="x", pady=(15, 15), padx=20)

        # Close button with premium styling
        close_button = CTkButton(
            footer_frame,
            text="CLOSE",
            font=("Inter", 12, "bold"),
            fg_color="#2D3250",
            hover_color="#3B4272",
            corner_radius=8,
            width=120,
            height=36,
            command=self.ack_window.destroy
        )
        close_button.pack(side="right")

        # Additional action button based on event type
        action_text = "VERIFY" if event_type == "Unknown" else "VIEW DETAILS"
        action_color = "#4D79FF" if event_type == "Unknown" else "#2D3250"

        action_button = CTkButton(
            footer_frame,
            text=action_text,
            font=("Inter", 12, "bold"),
            fg_color=action_color,
            hover_color="#3B59B3",
            corner_radius=8,
            width=120,
            height=36
        )
        action_button.pack(side="right", padx=10)

        if hasattr(self, 'on_form_ready'):
            self.on_form_ready()
    def create_tooltip(self, widget, text):
        # Create a toplevel window for the tooltip
        tooltip = CTkToplevel()
        tooltip.withdraw()  # Initially hide the tooltip
        tooltip.overrideredirect(True)  # Remove window decorations

        # Style and position the tooltip
        label = CTkLabel(
            tooltip,
            text=text,
            fg_color="#232E51",
            text_color="#FFFFFF",
            corner_radius=1,
            padx=12,
            pady=8,
            font=("Arial", 12, "bold")
        )
        label.pack(padx=1, pady=1)
        tooltip.configure(bg="#555555")

        def show_tooltip(event):
            x = widget.winfo_rootx() + widget.winfo_width() - 180
            y = widget.winfo_rooty() + (widget.winfo_height() // 2) + 20

            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()

            tooltip.lift()

        def hide_tooltip(event):
            tooltip.withdraw()

        # Bind show/hide events to the widget
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

        return tooltip

    def toggle_filter_popup(self):
        if (self.bool_filter_popup is False):
            self.frame_filter.grid_propagate(False)
            self.frame_filter.grid(row=2, column=0, rowspan=2, sticky="ne", padx=19, pady=(2, 80))
            self.frame_filter.tkraise()
        else:  # Popup is opened, need to closed it
            self.frame_filter.grid_forget()

        self.bool_filter_popup = not self.bool_filter_popup

    def popup_dropdown(self, list_data: list = [], entry_destination: CTkEntry = None, i_row: int = None,
                       i_rowspan: int = 2):

        frame_dropdown_table = CTkScrollableFrame(
            self.frame_maindropdown_window,
            fg_color="#FFFFFF",
            height=40,
            corner_radius=5
        )
        frame_dropdown_table.columnconfigure(0, weight=1)
        frame_dropdown_table.grid(row=0, column=0, padx=(1, 5), pady=(1, 3), sticky="nsew")

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
                command=lambda selected_option=row_data: self.select_option(selected_option, entry_destination)
            )
            button_options.grid(row=index, column=0, sticky="nsew")

        self.frame_maindropdown_window.grid_propagate(False)
        self.frame_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, columnspan=2, sticky="nsew",
                                            padx=(15, 0), pady=(5, 2))

        self.frame_maindropdown_window.tkraise()

    def open_calendar(self, entry_destination: CTkEntry = None, i_row: int = None, i_rowspan: int = 2):
        calendar = Calendar(
            self.frame_maindropdown_window,
            selectmode="day",
            date_pattern="dd-mm-yyyy"
        )
        calendar.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        calendar.bind("<<CalendarSelected>>", lambda event: self.select_date(event, calendar, entry_destination))

        self.frame_maindropdown_window.grid_propagate(False)
        self.frame_maindropdown_window.grid(row=i_row, column=0, rowspan=i_rowspan, columnspan=2, sticky="nsew",
                                            padx=(15, 0), pady=1)
        self.frame_maindropdown_window.tkraise()

    def close_dropdown(self, event):
        self.frame_maindropdown_window.grid_forget()
        for child in self.frame_maindropdown_window.winfo_children():
            child.destroy()

    def reset_filter_form(self):
        today_date = (datetime.date.today()).strftime("%d-%m-%Y")
        today_date = datetime.datetime.strptime(today_date, "%d-%m-%Y")
        today_date = f"{today_date.day}-{today_date.month}-{today_date.year}"

        current_time = datetime.datetime.now()

        self.entry_selected_sdate.configure(state="normal", text_color="#414141", border_color="#DEDEDE")
        self.entry_selected_sdate.delete(0, "end")
        self.entry_selected_sdate.insert(0, today_date)
        self.entry_selected_sdate.configure(state="disabled")

        self.entry_selected_edate.configure(state="normal", text_color="#414141", border_color="#DEDEDE")
        self.entry_selected_edate.delete(0, "end")
        self.entry_selected_edate.insert(0, today_date)
        self.entry_selected_edate.configure(state="disabled")

        self.entry_selected_vehicle.configure(state="normal", text_color="#414141", border_color="#DEDEDE")
        self.entry_selected_vehicle.delete(0, "end")
        self.entry_selected_vehicle.insert(0, "All")
        self.entry_selected_vehicle.configure(state="disabled")

        self.var_spinbox_shour.set("00")
        self.var_spinbox_sminute.set("00")
        self.var_spinbox_ehour.set(f"{current_time.hour}")
        self.var_spinbox_eminute.set(f"{current_time.minute}")

    def select_option(self, selected_option: str, entry_destination: CTkEntry):
        entry_destination.configure(state="normal", text_color="#414141")
        entry_destination.delete(0, "end")
        entry_destination.insert(0, selected_option)
        entry_destination.configure(state="disabled")

        if (entry_destination == self.entry_selected_vehicle):
            self.bool_vehicle_dropdown_opened = False

        self.close_dropdown(None)

    def select_date(self, event, calendar, entry_destination):

        selected_date = calendar.get_date()

        entry_destination.configure(state="normal", text_color="#414141")
        entry_destination.delete(0, "end")
        entry_destination.insert(0, selected_date)
        entry_destination.configure(state="disabled")

        if (entry_destination == self.entry_selected_sdate):
            self.bool_sdate_dropdown_opened = False
        elif (entry_destination == self.entry_selected_edate):
            self.bool_edate_dropdown_opened = False

        self.close_dropdown(None)

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

        enabled_color = "#374151"
        enabled_hover = "#1F2937"
        enabled_text = "#FFFFFF"

        disabled_color = "#e6e6ff"
        disabled_border = "#000000"
        disabled_text = "#9CA3AF"

        self.update_button_state(
            button=self.button_previous,
            state="disabled" if self.i_start_index <= 1 else "normal",
            cursor="X_cursor" if self.i_start_index <= 1 else "hand2",
            fg_color=disabled_color if self.i_start_index <= 1 else enabled_color,
            hover_color=disabled_color if self.i_start_index <= 1 else enabled_hover,
            # text_color=disabled_text if self.i_start_index <= 1 else enabled_text
        )

        self.update_button_state(
            button=self.button_next,
            state="disabled" if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else "normal",
            cursor="X_cursor" if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else "hand2",
            fg_color=disabled_color if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else enabled_color,
            hover_color=disabled_color if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else enabled_hover,
            # text_color=disabled_text if self.i_end_index >= self.i_total_data or self.i_end_index == 0 else enabled_text
        )

    def update_button_state(self, button, state, cursor, fg_color, hover_color):
        button.configure(state=state, cursor=cursor, fg_color=fg_color)
        button.unbind("<Enter>")
        button.unbind("<Leave>")
        if state == "normal":
            button.bind("<Enter>", lambda e: button.configure(fg_color=hover_color))
            button.bind("<Leave>", lambda e: button.configure(fg_color=fg_color))

    def reset_filter_criteria(self):
        self.dict_filter_criteria["str_start_timeperiod"] = ""
        self.dict_filter_criteria["str_end_timeperiod"] = ""
        self.dict_filter_criteria["str_vehicle_number"] = ""

    def resize_ctk_image(self, tk_photo, size):
        """ Convert a Tkinter PhotoImage to PIL Image, resize it, and return a CTkImage """
        # Convert PhotoImage to PIL Image
        pil_image = ImageTk.getimage(tk_photo)  # Converts PhotoImage to a PIL image
        pil_image = pil_image.resize(size, Image.LANCZOS)  # Resize the image

        # Convert back to CTkImage
        return CTkImage(light_image=pil_image, size=size)


    def show_acknowledge_dialog(self, data=None, personimg=None, capturedimg=None, event_data=None, eventType=None):
        """Show the acknowledgment dialog with the given data"""
        self.create_acknowledgment_frame(data=data, person_image=personimg,
                                         captured_image=capturedimg, event_data=event_data, eventType=eventType)

    def reset_interface(self):

        self.cleanup_popup()

        self.close_dropdown(None)
        self.reset_filter_form()

        if self.bool_filter_popup is True:
            self.toggle_filter_popup()

        self.frame_table._parent_canvas.yview_moveto(0)

        for child in self.frame_table.winfo_children():
            child.destroy()

        self.i_start_index = 0
        self.i_end_index = 0
        self.i_row_index = 1


