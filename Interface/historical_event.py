import os
from functools import partial

import cv2
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCanvas, CTkScrollableFrame, CTkImage, CTkTextbox, \
    CTkToplevel
from tkinter import StringVar, Spinbox, messagebox
from tkcalendar import Calendar
from PIL import Image, ImageTk
import datetime


class HistoricalEventInterface(CTkFrame):

    def __init__(self, *args, root_width: int = 1920, root_height: int = 1080, **kwargs):

        super().__init__(*args, **kwargs)

        self.bool_filter_popup = False
        self.bool_sdate_dropdown_opened = False
        self.bool_edate_dropdown_opened = False
        self.bool_vehicle_dropdown_opened = False
        self.current_vehicle_id = self.current_vehicle_number = ''
        self.current_vehicle_image= self.current_plate_image= None
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
            text="Vehicle Number",
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
        if isinstance(image_param, Image.Image):
            image = image_param
        elif isinstance(image_param, CTkImage):
            # Access the _light_image attribute to get the underlying PIL image
            image = image_param._light_image
        else:
            image = Image.open(image_param)

        # Convert the image from RGB to BGR by reordering channels
        bgr_image = Image.merge("RGB", image.split()[::-1])
        return bgr_image

    def show_ack_popup(self, message):

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


    def hide_popup(self):

        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()


    def cleanup_popup(self):
        """Ensure popup is destroyed when the main widget is destroyed"""
        if hasattr(self, 'popup'):
            self.popup.destroy()
        if hasattr(self, 'ack_window'):
            self.ack_window.destroy()

    def on_row_click(self, event, event_id_current, vehicle_number, vehicleimg=None, plateimg=None, eventdata=None,
                     eventType=None):
        print(f"Row {event_id_current} clicked! Vehicle: {vehicle_number} with {eventType}")
        self.current_vehicle_number = vehicle_number
        self.current_vehicle_id = event_id_current
        self.current_vehicle_image = vehicleimg
        self.current_plate_image = plateimg
        self.current_event_details = eventdata
        self.eventType = eventType

    def format_label(self, label, max_length=12):
        return f"{label.ljust(max_length)} : "

    def update_table(self, list_historical_events: list):
        event_details = None

        for child in self.frame_table.winfo_children():
            child.destroy()

        for row_index, row_data in enumerate(list_historical_events):
            # Enhanced row styling with gradient-like effect
            row_bg_color = "#FAFBFC" if row_index % 2 == 0 else "#F1F5F9"
            event_details = row_data

            # Convert the vehicle image from RGB to BGR
            bgr_image_of_vehicle = self.convert_rgb_to_bgr(row_data["vehicle_img"])
            vehicle_img = ImageTk.PhotoImage(bgr_image_of_vehicle)

            # Create main row frame with enhanced modern styling - INCREASED HEIGHT
            frame_row = CTkFrame(
                self.frame_table,
                height=220,  # Increased from 160 to 220
                fg_color=row_bg_color,
                corner_radius=16,  # More rounded corners
                border_width=2,
                border_color="#E2E8F0"
            )
            frame_row.columnconfigure((2, 3), weight=1)
            frame_row.rowconfigure(0, weight=1)
            frame_row.grid_propagate(False)
            frame_row.grid(row=row_index * 2, column=0, sticky="nsew", pady=8, padx=12)

            # Enhanced vehicle image with modern styling - INCREASED SIZE
            vehicle_frame = CTkFrame(
                frame_row,
                fg_color="#FFFFFF",
                corner_radius=12,
                border_width=2,
                border_color="#E2E8F0"
            )
            vehicle_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)

            label_image = CTkLabel(
                vehicle_frame,
                image=vehicle_img,
                text="",
                height=190,  # Increased from 140 to 190
                width=260,  # Increased from 200 to 260
                fg_color="#F8FAFC",
                corner_radius=10
            )
            label_image.pack(padx=8, pady=8)

            # Enhanced details frame with modern styling
            frame_details = CTkFrame(
                frame_row,
                height=180,  # Increased height
                fg_color="transparent",
            )
            frame_details.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="row_height")
            frame_details.columnconfigure(0, weight=1)
            frame_details.grid(row=0, column=1, sticky="nsew", padx=15)

            # Enhanced Serial Number with modern styling
            frame_cell = CTkFrame(
                frame_details,
                fg_color="#FFFFFF",
                corner_radius=8,
                border_width=1,
                border_color="#E2E8F0"
            )
            frame_cell.grid(row=0, column=0, sticky="nsew", pady=3)

            CTkLabel(
                frame_cell,
                text="Serial Number:",
                font=("Inter", 14, "bold"),
                text_color="#1E293B"
            ).pack(side="left", padx=12, pady=5)

            CTkLabel(
                frame_cell,
                text=str(self.i_row_index),
                font=("Inter", 14),
                text_color="#3B82F6",
                fg_color="#EFF6FF",
                corner_radius=6
            ).pack(side="left", padx=(15, 12), pady=5)

            # Enhanced dynamic fields with modern card styling
            index = 0
            for key, value in row_data.items():
                if key in ["vehicle_id", "object_type", "time", "camera_name"]:
                    str_title = {
                        "vehicle_id": "Event ID:",
                        "object_type": "Object Type:",
                        "time": "Capture Time:",
                        "camera_name": "Camera Name:"
                    }.get(key, "")

                    frame_cell = CTkFrame(
                        frame_details,
                        fg_color="#FFFFFF",
                        corner_radius=8,
                        border_width=1,
                        border_color="#E2E8F0"
                    )
                    frame_cell.grid(row=index + 1, column=0, sticky="nsew", pady=3)

                    CTkLabel(
                        frame_cell,
                        text=str_title,
                        font=("Inter", 14, "bold"),
                        text_color="#1E293B"
                    ).pack(side="left", padx=12, pady=5)

                    CTkLabel(
                        frame_cell,
                        text=str(value),
                        font=("Inter", 14),
                        text_color="#64748B"
                    ).pack(side="left", padx=(15, 12), pady=5)

                    index += 1

            # Enhanced additional details frame
            frame_additional_details = CTkFrame(
                frame_row,
                height=180,
                width=420,  # Increased width
                fg_color="transparent",
            )
            frame_additional_details.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="row_height")
            frame_additional_details.columnconfigure(0, weight=1)
            frame_additional_details.grid(row=0, column=2, sticky="ns", padx=(15, 20))
            frame_additional_details.grid_propagate(False)

            # Enhanced Event ID
            frame_event_id = CTkFrame(
                frame_additional_details,
                fg_color="#FFFFFF",
                corner_radius=8,
                border_width=1,
                border_color="#E2E8F0"
            )
            frame_event_id.grid(row=0, column=0, sticky="nsew", pady=3)

            CTkLabel(
                frame_event_id,
                text="Event ID:",
                font=("Inter", 14, "bold"),
                text_color="#1E293B"
            ).pack(side="left", padx=12, pady=5)

            CTkLabel(
                frame_event_id,
                text=row_data.get("event_id", "N/A"),
                font=("Inter", 14),
                text_color="#7C3AED",
                fg_color="#F3E8FF",
                corner_radius=6
            ).pack(side="left", padx=(15, 12), pady=5)

            # Enhanced ACK Time
            frame_ack_time = CTkFrame(
                frame_additional_details,
                fg_color="#FFFFFF",
                corner_radius=8,
                border_width=1,
                border_color="#E2E8F0"
            )
            frame_ack_time.grid(row=1, column=0, sticky="nsew", pady=3)

            CTkLabel(
                frame_ack_time,
                text="ACK Time:",
                font=("Inter", 14, "bold"),
                text_color="#1E293B"
            ).pack(side="left", padx=12, pady=5)

            msg = row_data.get("acknowledgment_time", "N/A")
            if msg is not None and len(str(msg)) > 8:
                msg = str(msg)[:-7]
            else:
                msg = "N/A" if msg is None else msg

            CTkLabel(
                frame_ack_time,
                text=msg,
                font=("Inter", 14),
                text_color="#059669",
                fg_color="#ECFDF5",
                corner_radius=6
            ).pack(side="left", padx=(15, 12), pady=5)

            # Enhanced ACK Message section
            frame_ack = CTkFrame(
                frame_additional_details,
                fg_color="#FFFFFF",
                corner_radius=8,
                border_width=1,
                border_color="#E2E8F0"
            )
            frame_ack.grid(row=2, column=0, sticky="nsew", pady=3)

            CTkLabel(
                frame_ack,
                text="ACK Message:",
                font=("Inter", 14, "bold"),
                text_color="#1E293B"
            ).pack(side="left", padx=12, pady=5)

            ack_msg = row_data.get("acknowledgment_message", "N/A")
            if ack_msg is None:
                ack_msg = 'N/A'

            display_msg = ack_msg if len(ack_msg) <= 25 else ack_msg[:22] + "..."

            msg_container = CTkFrame(frame_ack, fg_color="transparent")
            msg_container.pack(side="left", padx=(15, 12), pady=5)

            msg_label = CTkLabel(
                msg_container,
                text=display_msg,
                font=("Inter", 14),
                text_color="#64748B"
            )
            msg_label.pack(side="left")

            if len(ack_msg) > 25:
                info_button = CTkButton(
                    msg_container,
                    text="ⓘ",
                    width=24,
                    height=24,
                    corner_radius=12,
                    fg_color="#3B82F6",
                    hover_color="#2563EB",
                    font=("Inter", 12, "bold"),
                    command=lambda m=ack_msg: self.show_ack_popup(m)
                )
                info_button.pack(side="left", padx=(8, 0))

            # Enhanced status styling - REMOVED UNKNOWN STATUS
            alarm_value = int(row_data.get("alarm", "0"))
            if alarm_value == 1:
                status_color = "#10B981"
                status_text = "✓ Verified"
                hover_color = "#34D399"
                button_fg_color = "#D1FAE5"
                button_text_color = "#065F46"
                gradient_start = "#10B981"
                gradient_end = "#059669"
            else:  # alarm_value == 0 or other values become "Restricted"
                status_color = "#EF4444"
                status_text = "⚠ Restricted"
                hover_color = "#F87171"
                button_fg_color = "#FEE2E2"
                button_text_color = "#991B1B"
                gradient_start = "#EF4444"
                gradient_end = "#DC2626"

            event_id_current = row_data.get("event_id", "")
            vehicle_number_current = row_data.get("vehicle_id", "")
            eventType = alarm_value

            # Create ultra-modern video button container with gradient effect
            video_container = CTkFrame(
                frame_row,
                fg_color=gradient_start,
                width=200,  # Increased width
                height=190,  # Increased height
                corner_radius=16,
                border_width=3,
                border_color=gradient_end
            )
            video_container.grid(row=0, column=3, sticky="e", padx=20, pady=15)
            video_container.grid_propagate(False)

            # Check if video exists and is valid (>=2 seconds)
            video_path = f"E:\\SUBRAT_FOLDER\\Zone_Intrusion\\track_videos\\track_{row_data.get('vehicle_id', 'N/A')}.mp4"
            video_exists = os.path.exists(video_path)
            if video_exists:
                cap = cv2.VideoCapture(video_path)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                fps = cap.get(cv2.CAP_PROP_FPS)
                duration = frame_count / fps if fps > 0 else 0
                cap.release()
                is_valid_video = duration >= 1.0
            else:
                is_valid_video = False

            # EXTREMELY STYLISH green check mark - positioned ABOVE the button
            if is_valid_video:
                # Create a stylish container for the check mark
                check_container = CTkFrame(
                    video_container,
                    fg_color="#FFFFFF",
                    corner_radius=20,
                    width=40,
                    height=40,
                    border_width=3,
                    border_color="#10B981"
                )
                check_container.place(relx=0.5, rely=0.15, anchor="center")

                # Animated-style check mark with shadow effect
                check_mark = CTkLabel(
                    check_container,
                    text="✓",
                    font=("Inter", 20, "bold"),
                    text_color="#10B981",
                    fg_color="transparent"
                )
                check_mark.place(relx=0.5, rely=0.5, anchor="center")

                # Add a subtle glow effect with multiple layers
                glow_outer = CTkFrame(
                    video_container,
                    fg_color="#10B981",
                    corner_radius=25,
                    width=50,
                    height=50
                )
                glow_outer.place(relx=0.5, rely=0.15, anchor="center")
                glow_outer.lower()  # Send to back

                # Status indicator text
                status_indicator = CTkLabel(
                    video_container,
                    text="• VIDEO READY •",
                    font=("Inter", 10, "bold"),
                    text_color="#FFFFFF",
                    fg_color="transparent"
                )
                status_indicator.place(relx=0.5, rely=0.35, anchor="center")

            # Enhanced status badge with modern design
            status_badge = CTkFrame(
                video_container,
                fg_color="#FFFFFF",
                corner_radius=25,
                height=36,
                border_width=2,
                border_color="#E5E7EB"
            )
            status_badge.pack(pady=(50 if is_valid_video else 20, 10))

            status_label = CTkLabel(
                status_badge,
                text=status_text,
                text_color=status_color,
                font=("Inter", 13, "bold"),
                fg_color="transparent"
            )
            status_label.pack(padx=20, pady=8)

            # Ultra-modern "Click to View" button with enhanced styling
            view_button = CTkButton(
                video_container,
                text="🎬 VIEW VIDEO",
                font=("Inter", 13, "bold"),
                fg_color="#FFFFFF",
                text_color=status_color,
                hover_color="#F8FAFC",
                corner_radius=12,
                height=45,  # Increased height
                width=170,  # Increased width
                border_width=2,
                border_color=status_color,
                command=lambda path=video_path, data=row_data: self.show_video_popup(path, data)
            )
            view_button.pack(pady=(10, 15))

            # Add subtle animation effect on hover (simulation with colors)
            def on_enter(event):
                view_button.configure(
                    fg_color=status_color,
                    text_color="#FFFFFF",
                    border_color="#FFFFFF"
                )

            def on_leave(event):
                view_button.configure(
                    fg_color="#FFFFFF",
                    text_color=status_color,
                    border_color=status_color
                )

            view_button.bind("<Enter>", on_enter)
            view_button.bind("<Leave>", on_leave)

            # Add click event for row details
            view_button.bind("<Button-1>",
                             partial(self.on_row_click,
                                     event_id_current=event_id_current,
                                     vehicle_number=vehicle_number_current,
                                     vehicleimg=vehicle_img,
                                     plateimg=None,
                                     eventdata=event_details,
                                     eventType=eventType))

            # Ultra-modern separator line with gradient effect
            separator_container = CTkFrame(
                self.frame_table,
                height=8,
                fg_color="transparent"
            )
            separator_container.grid(row=row_index * 2 + 1, column=0, sticky="ew", padx=25, pady=8)

            separator = CTkFrame(
                separator_container,
                height=2,
                fg_color="#E2E8F0",
                corner_radius=1
            )
            separator.pack(fill="x")

            self.i_row_index += 1

        self.on_page_change()

    def show_video_popup(self, video_path, event_data):
        """Show video in a modern styled popup window with auto-play"""
        try:
            # Create modern video popup window
            video_window = CTkToplevel(self)
            video_window.title("Objects Video Player")
            video_window.geometry("900x650")
            video_window.configure(fg_color="#0F172A")

            # Make window modal
            video_window.transient(self)
            video_window.grab_set()

            # Center the window
            video_window.update_idletasks()
            x = (video_window.winfo_screenwidth() // 2) - (900 // 2)
            y = (video_window.winfo_screenheight() // 2) - (650 // 2)
            video_window.geometry(f"900x650+{x}+{y}")

            # Header frame
            header_frame = CTkFrame(
                video_window,
                height=60,
                fg_color="#1E293B",
                corner_radius=0
            )
            header_frame.pack(fill="x", padx=0, pady=0)
            header_frame.pack_propagate(False)

            # Title
            title_label = CTkLabel(
                header_frame,
                text=f"🎥 Event Video - Event ID: {event_data.get('event_id', 'N/A')}",
                font=("Inter", 18, "bold"),
                text_color="white"
            )
            title_label.pack(side="left", padx=20, pady=15)

            # Close button
            close_button = CTkButton(
                header_frame,
                text="✕",
                width=40,
                height=30,
                corner_radius=15,
                fg_color="#EF4444",
                hover_color="#DC2626",
                command=video_window.destroy
            )
            close_button.pack(side="right", padx=20, pady=15)

            # Main video container
            main_container = CTkFrame(
                video_window,
                fg_color="#1E293B",
                corner_radius=15,
                border_width=2,
                border_color="#334155"
            )
            main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

            # Video frame
            video_frame = CTkFrame(
                main_container,
                fg_color="#000000",
                corner_radius=10
            )
            video_frame.pack(fill="both", expand=True, padx=15, pady=15)

            # Video label
            video_label = CTkLabel(
                video_frame,
                text="Loading video...",
                font=("Inter", 16),
                text_color="white",
                fg_color="transparent"
            )
            video_label.pack(expand=True)

            # Controls frame
            controls_frame = CTkFrame(
                main_container,
                height=50,
                fg_color="#334155",
                corner_radius=10
            )
            controls_frame.pack(fill="x", padx=15, pady=(0, 15))
            controls_frame.pack_propagate(False)

            # Control variables
            video_playing = False
            cap = None
            after_id = None

            def update_frame():
                nonlocal video_playing, cap, after_id

                if not video_playing:
                    return

                try:
                    if cap is None or not cap.isOpened():
                        return

                    ret, frame = cap.read()
                    if not ret:
                        # Loop video
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = cap.read()
                        if not ret:
                            stop_video()
                            return

                    # Resize frame to fit the display
                    frame = cv2.resize(frame, (800, 450))
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Convert to PhotoImage
                    img = Image.fromarray(frame_rgb)
                    photo = ImageTk.PhotoImage(img)

                    # Update video label safely
                    if video_window.winfo_exists():
                        video_label.configure(image=photo, text="")
                        video_label.image = photo  # Keep a reference

                        # Schedule next frame update
                        after_id = video_window.after(33, update_frame)  # ~30 FPS

                except Exception as e:
                    print(f"Error in video playback: {e}")
                    stop_video()

            def start_video():
                """Auto-start the video when popup opens"""
                nonlocal video_playing, cap

                try:
                    cap = cv2.VideoCapture(video_path)

                    if not cap.isOpened():
                        video_label.configure(text="Error: Could not open video file")
                        messagebox.showerror("Video Error", "Could not open video file")
                        return

                    video_playing = True
                    update_frame()  # Start the video loop

                except Exception as e:
                    video_label.configure(text=f"Error: {str(e)}")
                    messagebox.showerror("Video Error", f"Could not play video: {str(e)}")

            def stop_video():
                nonlocal video_playing, cap, after_id

                video_playing = False

                if after_id:
                    video_window.after_cancel(after_id)
                    after_id = None

                # Keep the last frame visible - don't clear the image
                # The current frame in video_label will remain displayed

                # Release the video capture to free resources
                if cap:
                    cap.release()
                    cap = None

                # Change button to Play
                control_button.configure(
                    text="▶ Play Video",
                    fg_color="#10B981",
                    hover_color="#059669",
                    command=play_video
                )

            def play_video():
                """Play the video and change button back to Stop"""
                nonlocal video_playing, cap

                try:
                    # Release previous cap if exists
                    if cap:
                        cap.release()

                    cap = cv2.VideoCapture(video_path)

                    if not cap.isOpened():
                        video_label.configure(text="Error: Could not open video file")
                        messagebox.showerror("Video Error", "Could not open video file")
                        return

                    video_playing = True
                    update_frame()  # Start the video loop

                    # Change button back to Stop
                    control_button.configure(
                        text="⏹ Stop Video",
                        fg_color="#EF4444",
                        hover_color="#DC2626",
                        command=stop_video
                    )

                except Exception as e:
                    video_label.configure(text=f"Error: {str(e)}")
                    messagebox.showerror("Video Error", f"Could not play video: {str(e)}")
            def play_video():
                """Play the video and change button back to Stop"""
                nonlocal video_playing, cap

                try:
                    cap = cv2.VideoCapture(video_path)

                    if not cap.isOpened():
                        video_label.configure(text="Error: Could not open video file")
                        messagebox.showerror("Video Error", "Could not open video file")
                        return

                    video_playing = True
                    update_frame()  # Start the video loop

                    # Change button back to Stop
                    control_button.configure(
                        text="⏹ Stop Video",
                        fg_color="#EF4444",
                        hover_color="#DC2626",
                        command=stop_video
                    )

                except Exception as e:
                    video_label.configure(text=f"Error: {str(e)}")
                    messagebox.showerror("Video Error", f"Could not play video: {str(e)}")

            # Control button (starts as Stop since video auto-plays)
            control_button = CTkButton(
                controls_frame,
                text="⏹ Stop Video",
                width=120,
                height=35,
                corner_radius=8,
                fg_color="#EF4444",
                hover_color="#DC2626",
                command=stop_video
            )
            control_button.pack(side="left", padx=15, pady=7)

            # Info label
            info_label = CTkLabel(
                controls_frame,
                text="Video playing automatically • Auto-loop enabled • Click Stop/Play to control",
                font=("Inter", 12),
                text_color="#94A3B8"
            )
            info_label.pack(side="right", padx=15, pady=7)

            # Auto-start video after window is fully loaded
            video_window.after(100, start_video)

            # Cleanup when window is closed
            def on_closing():
                nonlocal video_playing, cap, after_id

                video_playing = False

                if after_id:
                    video_window.after_cancel(after_id)

                if cap:
                    cap.release()

                video_window.destroy()

            video_window.protocol("WM_DELETE_WINDOW", on_closing)

        except Exception as e:
            messagebox.showerror("Error", f"Could not open video player: {str(e)}")
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

    def create_acknowledgment_frame(self, event_data=None, vehicle_data=None, vehicle_image=None,
                                    plate_image=None, data=None, eventType: int = 0):
        # First, properly cleanup any existing window
        self.cleanup_popup()

        # Determine event type and heading based on data[8]
        event_type = 'Unknown'
        heading = 'Un-Registered Vehicle Details'


        if eventType == 1:
            event_type = 'Verified'
            heading = 'Authorized Vehicle Details'
        elif eventType == 2:
            event_type = 'Blacklisted'
            heading = 'Restricted Vehicle Details'
        elif eventType == 0:
            event_type = 'Unknown'
            heading = 'Un-Registered Vehicle Details'

        if event_data is None and data:
            event_data = [
                {"label": "Vehicle No", "value": data[0]},
                {"label": "Event No", "value": "N/A"},
                {"label": "Direction", "value": "N/A"},
                {"label": "Event Time", "value": "N/A"},
                {"label": "Event Type", "value": event_type}
            ]
        else:
            print("event data ", event_data)
            event_data = [
                {"label": "Vehicle No", "value": event_data.get("vehicle_number", "N/A")},
                {"label": "Event No", "value": event_data.get("event_id", "N/A")},
                {"label": "Direction", "value": event_data.get("status", "N/A")},
                {"label": "Event Time", "value": event_data.get("time", "N/A")},
                {"label": "Event Type", "value": event_type}
            ]

        if vehicle_data is None and data:
            vehicle_data = [
                {"label": "Model Name", "value": data[3]},
                {"label": "Color", "value": data[5]},
                {"label": "Vehicle Type", "value": data[4]},
                {"label": "Mfg Year", "value": data[7]},
                {"label": "Owner Name", "value": data[6]}
            ]



        # Window setup
        self.ack_window = CTkToplevel()
        self.ack_window.geometry("900x500")
        self.ack_window.title("Acknowledgment Panel")
        self.ack_window.configure(bg="#1E2749")
        self.ack_window.resizable(False, False)
        self.ack_window.attributes("-topmost", True)

        # Centering the window
        self.ack_window.update_idletasks()
        screen_width = self.ack_window.winfo_screenwidth()
        screen_height = self.ack_window.winfo_screenheight()
        x_position = (screen_width - 900) // 2
        y_position = (screen_height - 500) // 2
        self.ack_window.geometry(f"900x480+{x_position}+{y_position}")

        # Main frame
        self.ack_frame = CTkFrame(
            self.ack_window,
            width=900,
            height=500,
            fg_color="#1E2749",
            corner_radius=0,
            border_width=1,
            border_color="#4A5567"
        )
        self.ack_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.ack_frame.grid_propagate(False)

        # Heading
        ack_label = CTkLabel(
            self.ack_frame,
            text=heading,
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
        info_boxes_frame.pack(pady=10, padx=30, fill="x")

        # Event Details Box
        event_box = CTkFrame(
            info_boxes_frame,
            fg_color="#2C3656",
            border_width=1,
            border_color="#4A5567",
            corner_radius=12,
            width=260,
            height=300
        )
        event_box.pack(side="left", padx=10, fill="both", expand=True)
        event_box.pack_propagate(False)

        # Event Details Title and Content
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

        # Event Details Content
        event_content_frame = CTkFrame(event_box, fg_color="transparent")
        event_content_frame.pack(pady=10, padx=20, fill="both", expand=True)
        if event_data:
            for item in event_data:
                row_frame = CTkFrame(event_content_frame, fg_color="transparent")
                row_frame.grid(sticky="w", pady=5)
                padded_label = item["label"].ljust(12)
                label = CTkLabel(
                    row_frame,
                    text=padded_label + ':',
                    font=("Inter", 14, "bold"),
                    text_color="#B0B8C4",
                    anchor="w"
                )
                label.grid(row=0, column=0, sticky="w", padx=(0, 5))

                # Modified value_label styling based on Event Type
                if item["label"] == "Event Type":
                    if item["value"] == "Blacklisted":
                        bg_color = "#FF4B4B"  # Red for blacklisted
                        txt_color= '#FFFFFF'
                    elif item["value"] == "Verified":
                        bg_color = "#28A745"  # Green for verified
                        txt_color = '#FFFFFF'
                    else:
                        bg_color = "#FFA500"  # Orange for unknown
                        txt_color = '#2C2C2C'

                    value_label = CTkLabel(
                        row_frame,
                        text=item["value"],
                        font=("Inter", 14, "bold"),
                        text_color=txt_color,
                        fg_color=bg_color,
                        corner_radius=6
                    )
                else:
                    if item["label"] == "Event Time":
                        font_size=12
                    else:
                        font_size = 14
                    value_label = CTkLabel(
                        row_frame,
                        text=item["value"],
                        font=("Inter", font_size),
                        text_color="#FFFFFF",
                        anchor="w"
                    )

                value_label.grid(row=0, column=1, sticky="w", padx=(0, 10), ipadx=5, ipady=2)

        # Ensure uniform column alignment
        event_content_frame.grid_columnconfigure(0, minsize=150)
        event_content_frame.grid_columnconfigure(1, weight=1)

        # Images Box
        image_box = CTkFrame(
            info_boxes_frame,
            fg_color="#2C3656",
            border_width=1,
            border_color="#4A5567",
            corner_radius=12,
            width=260,
            height=300
        )
        image_box.pack(side="left", padx=10, fill="both", expand=True)
        image_box.pack_propagate(False)

        # Images Title
        image_title_frame = CTkFrame(
            image_box,
            fg_color="#3A4766",
            corner_radius=8,
            height=40
        )
        image_title_frame.pack(pady=(15, 10), padx=15, fill="x")

        CTkLabel(
            image_title_frame,
            text="Vehicle Images",
            font=("Inter", 18, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=5)

        # Vehicle Image Container
        vehicle_image_container = CTkFrame(image_box, fg_color="transparent")
        vehicle_image_container.pack(expand=True, fill="both", padx=10, pady=5)

        vehicle_imagen = self.resize_ctk_image(vehicle_image, (220, 160))
        CTkLabel(vehicle_image_container, image=vehicle_imagen, text="").pack(pady=(0, 5))

        plate_imagen = self.resize_ctk_image(plate_image, (220, 40))
        CTkLabel(vehicle_image_container, image=plate_imagen, text="").pack(pady=(5, 0))

        vehicle_box = CTkFrame(
            info_boxes_frame,
            fg_color="#2C3656",
            border_width=1,
            border_color="#4A5567",
            corner_radius=12,
            width=260,
            height=300
        )
        vehicle_box.pack(side="left", padx=10, fill="both", expand=True)
        vehicle_box.pack_propagate(False)

        # Vehicle Details Title
        vehicle_title_frame = CTkFrame(
            vehicle_box,
            fg_color="#3A4766",
            corner_radius=8,
            height=40
        )
        vehicle_title_frame.pack(pady=(15, 10), padx=15, fill="x")

        CTkLabel(
            vehicle_title_frame,
            text="Vehicle Details",
            font=("Inter", 18, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=5)

       
        vehicle_content_frame = CTkFrame(
            vehicle_box,
            fg_color="transparent"
        )
        vehicle_content_frame.pack(pady=10, padx=20, fill="both", expand=True)

        if event_type == "Unknown":

            message_frame = CTkFrame(
                vehicle_content_frame,
                fg_color="transparent"
            )
            message_frame.pack(pady=(30, 20))


            CTkLabel(
                message_frame,
                text="Vehicle details not available\nFor Un-Registered vehicle.",
                font=("Inter", 14),
                text_color="#B0B8C4",
                justify="center"
            ).pack(pady=10)


            spacer_frame = CTkFrame(
                vehicle_content_frame,
                fg_color="transparent",
                height=40
            )
            spacer_frame.pack(pady=10)
            spacer_frame.pack_propagate(False)


            button_frame = CTkFrame(
                vehicle_content_frame,
                fg_color="transparent"
            )
            button_frame.pack(pady=5, fill="x")

            self.add_vehicle_button = CTkButton(
                button_frame,
                text="Add this vehicle",
                font=("Inter", 15, "bold"),
                fg_color="orange",
                text_color="#000000",
               # hover_color="#218838",
                height=38,
                corner_radius=6,
                width=180,
                border_width=2,
                command=lambda: print("add vehicle button clicked")
            )
            self.add_vehicle_button.pack(pady=5)

        else:

            for item in vehicle_data:
                row_frame = CTkFrame(vehicle_content_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=5)
                padded_label = item["label"].ljust(15)
                CTkLabel(
                    row_frame,
                    text=padded_label + ":",
                    font=("Inter", 14, "bold"),
                    text_color="#B0B8C4",
                    anchor="w"
                ).pack(side="left", padx=(0, 10))

                CTkLabel(
                    row_frame,
                    text=item["value"],
                    font=("Inter", 14),
                    text_color="#FFFFFF"
                ).pack(side="left")

        if hasattr(self, 'on_form_ready'):
            self.on_form_ready()

    def show_acknowledge_dialog(self, data=None, vehicleimg=None, plateimg=None, event_data=None, eventType=None):
        pass

        # self.create_acknowledgment_frame(data=data, vehicle_image=vehicleimg,
        #                                  plate_image=plateimg, event_data=event_data, eventType=eventType)

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


