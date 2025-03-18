from functools import partial

from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCanvas, CTkScrollableFrame, CTkImage, CTkTextbox, \
    CTkToplevel
from tkinter import StringVar, Spinbox
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
        self.popup = None
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
            text_color="#313A46",
            fg_color="transparent",
            border_width=2,
            border_color="#313A46",
            font=("", 14),
            cursor="hand2",
            anchor="center",
            #hover=False,
            hover_color="#ADD8E6"

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
            fg_color="#3A36F5",
            border_color="#3A36F5",
            font=("", 14),
            cursor="hand2",
            hover=False
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
        # Destroy any existing popup before creating a new one
        if self.popup is not None:
            self.popup.destroy()
            self.popup = None

        self.popup = CTkToplevel(self)
        self.popup.title("")
        self.popup.configure(fg_color="#FFFFFF")

        # Remove window decorations
        self.popup.overrideredirect(True)

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
        if self.popup is not None:
            self.popup.destroy()
            self.popup = None

    def cleanup_popup(self):
        """Ensure popup is destroyed when the main widget is destroyed"""
        if self.popup is not None and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None



    def on_row_click(self,event, event_id_current, vehicle_number,vehicleimg=None,plateimg=None, eventdata=None):
        print(f"Row {event_id_current} clicked! Vehicle: {vehicle_number}")
        self.current_vehicle_number = vehicle_number
        self.current_vehicle_id=event_id_current
        self.current_vehicle_image= vehicleimg
        self.current_plate_image= plateimg
        self.current_event_details= eventdata

    def format_label(self, label, max_length=12):
        return f"{label.ljust(max_length)} : "

    def update_table(self, list_historical_events: list):
        event_details=None
        for child in self.frame_table.winfo_children():
            child.destroy()

        for row_index, row_data in enumerate(list_historical_events):
            row_bg_color = "white" if row_index % 2 == 0 else "#F7F9FB"
            event_details = row_data

            # Convert the image from RGB to BGR
            bgr_image_of_vehicle = self.convert_rgb_to_bgr(row_data["vehicle_img"])
            bgr_image_of_plate = self.convert_rgb_to_bgr(row_data["number_plate_img"])

            # Convert the image to a format suitable for CTkLabel
            vehicle_img = ImageTk.PhotoImage(bgr_image_of_vehicle)
            plate_img = ImageTk.PhotoImage(bgr_image_of_plate)

            frame_row = CTkFrame(
                self.frame_table,
                height=150,
                fg_color=row_bg_color
            )
            frame_row.columnconfigure((2, 3), weight=1)
            frame_row.rowconfigure(0, weight=1)
            frame_row.grid_propagate(False)
            frame_row.grid(row=row_index * 2, column=0, sticky="nsew")

            label_imge = CTkLabel(
                frame_row,
                image=vehicle_img,
                text="",
                height=160,
                fg_color="transparent",
                padx=20
            )
            label_imge.grid(row=0, column=0, sticky="w", padx=10)

            frame_details = CTkFrame(
                frame_row,
                height=110,
                fg_color="transparent",
            )
            frame_details.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="row_height")
            frame_details.columnconfigure(0, weight=1)
            frame_details.grid(row=0, column=1)

            frame_cell = CTkFrame(
                frame_details,
                fg_color="transparent",
            )
            frame_cell.grid(row=0, column=0, sticky="nsew", pady=1)

            CTkLabel(
                frame_cell,
                text="Serial Number : ",
                font=("", 14, "bold"),
                text_color="#011D76"
            ).pack(side="left")

            CTkLabel(
                frame_cell,
                text=self.i_row_index,
                font=("", 13),
                text_color="#2C2C2C"
            ).pack(side="left")

            index = 0
            for key, value in row_data.items():
                if key in ["vehicle_number", "number_plate_color", "time", "status"]:
                    str_title = {
                        "vehicle_number": "Vehicle Number : ",
                        "number_plate_color": "Plate Color : ",
                        "time": "Capture Time : ",
                        "status": "Status : "
                    }.get(key, "")

                    frame_cell = CTkFrame(
                        frame_details,
                        fg_color="transparent",
                    )
                    frame_cell.grid(row=index + 1, column=0, sticky="nsew", pady=1)

                    CTkLabel(
                        frame_cell,
                        text=str_title,
                        font=("", 14, "bold"),
                        text_color="#011D76"
                    ).pack(side="left")

                    CTkLabel(
                        frame_cell,
                        text=value,
                        font=("", 13),
                        text_color="#2C2C2C"
                    ).pack(side="left")

                    index += 1

            # Additional details frame
            frame_additional_details = CTkFrame(
                frame_row,
                height=110,
                width=400,
                fg_color="transparent",
            )
            frame_additional_details.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="row_height")
            frame_additional_details.columnconfigure(0, weight=1)
            frame_additional_details.grid(row=0, column=2, sticky="ns", padx=(10, 20))
            frame_additional_details.grid_propagate(False)

            # Event ID
            frame_event_id = CTkFrame(
                frame_additional_details,
                fg_color="transparent",
            )
            frame_event_id.grid(row=0, column=0, sticky="nsew", pady=1)

            CTkLabel(
                frame_event_id,
                text="Event ID : ",
                font=("", 14, "bold"),
                text_color="#011D76"
            ).pack(side="left")

            CTkLabel(
                frame_event_id,
                text=row_data.get("event_id", "N/A"),
                font=("", 13),
                text_color="#2C2C2C"
            ).pack(side="left")

            # ACK Time
            frame_ack_time = CTkFrame(
                frame_additional_details,
                fg_color="transparent",
            )
            frame_ack_time.grid(row=1, column=0, sticky="nsew", pady=1)

            CTkLabel(
                frame_ack_time,
                text="ACK Time : ",
                font=("", 14, "bold"),
                text_color="#011D76"
            ).pack(side="left")

            msg = row_data.get("acknowledgment_time", "N/A")
            if msg is not None:
                if len(str(msg)) > 8:
                    msg = str(msg)[:-7]
            else:
                msg = "N/A"

            CTkLabel(
                frame_ack_time,
                text=msg,
                font=("", 13),
                text_color="#2C2C2C"
            ).pack(side="left")

            # ACK Message section
            frame_ack = CTkFrame(
                frame_additional_details,
                fg_color="transparent",
            )
            frame_ack.grid(row=2, column=0, sticky="nsew", pady=1)

            CTkLabel(
                frame_ack,
                text="ACK Message : ",
                font=("", 14, "bold"),
                text_color="#011D76"
            ).pack(side="left")

            ack_msg = row_data.get("acknowledgment_message", "N/A")
            if ack_msg is None:
                ack_msg = 'N/A'

            # Create truncated message for display
            display_msg = ack_msg if len(ack_msg) <= 30 else ack_msg[:27] + "..."

            # Create message label and info icon container
            msg_container = CTkFrame(frame_ack, fg_color="transparent")
            msg_container.pack(side="left")

            msg_label = CTkLabel(
                msg_container,
                text=display_msg,
                font=("", 13),
                text_color="#2C2C2C",
            )
            msg_label.pack(side="left")

            if len(ack_msg) > 30:
                info_button = CTkButton(
                    msg_container,
                    text="ⓘ",
                    width=20,
                    height=20,
                    corner_radius=10,
                    fg_color="transparent",
                    text_color="#011D76",
                    hover_color="#F0F0F0",
                    command=lambda m=ack_msg: self.show_ack_popup(m)
                )
                info_button.pack(side="left", padx=(5, 0))

            if int(row_data.get("alarm", "0")) == 0:
                color = "orange"
                status_text = "Unknown"
                hover_color = "#FFB74D"
                tooltip_text = "Click to see vehicle details"
            elif int(row_data.get("alarm", "0")) == 1:
                color = "green"
                status_text = "Verified"
                hover_color = "#66BB6A"
                tooltip_text = "Click to see vehicle details"
            else:
                color = "red"
                status_text = "Restricted"
                hover_color = "#EF5350"
                tooltip_text = "Click to see vehicle details"

            event_id_current = row_data.get("event_id", "")
            vehicle_number_current = row_data.get("vehicle_number", "")

            # Create a container frame for the entire plate section
            plate_container = CTkFrame(
                frame_row,
                fg_color=color,
                width=plate_img.width() + 228,
                height=plate_img.height() + 228,
                corner_radius=5
            )
            plate_container.grid(row=0, column=3, sticky="e", padx=10)


            # Add status label
            status_label = CTkLabel(
                plate_container,
                text=status_text,
                text_color="white",
                font=("", 14, "bold"),
                fg_color="transparent",
            )
            status_label.pack(pady=(2, 0))

            # Create plate image label
            self.label_imge = CTkLabel(
                plate_container,
                image=plate_img,
                text="",
                height=55,
                cursor='hand2',
                width=160,
                fg_color=row_bg_color,
                padx=20
            )
            self.label_imge.pack(padx=2, pady=2)

            # Add click event and tooltip to image label
            # if int(row_data.get("alarm", "0")) in [1, 2,0]:
            self.label_imge.bind("<Button-1>",
                                 partial(self.on_row_click, event_id_current=event_id_current,
                                         vehicle_number=vehicle_number_current,
                                         vehicleimg=vehicle_img, plateimg=plate_img, eventdata=event_details))
            # Create tooltip for the image label
            self.create_tooltip(self.label_imge, tooltip_text)

            canvas_underline = CTkCanvas(
                self.frame_table,
                height=1,
                bg="#D7DDE5",
                bd=0,
                highlightthickness=0
            )
            canvas_underline.grid(row=row_index * 2 + 1, column=0, columnspan=len(row_data),
                                  padx=0, pady=0, sticky="ew")

            row_index += 1
            self.i_row_index += 1

        self.on_page_change()

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
            x = widget.winfo_rootx() + widget.winfo_width() - 160
            y = widget.winfo_rooty() + (widget.winfo_height() // 2) + 10

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
                                    plate_image=None, data=None):
        # Destroy existing window if it exists
        if hasattr(self, 'ack_window'):
            self.ack_window.destroy()

        # Determine event type and heading based on data[8]
        event_type = 'Unknown'
        heading = 'Un-Registered Vehicle Details'

        if data:
            if data[8] == 0:
                event_type = 'Verified'
                heading = 'Authorized Vehicle Details'
            elif data[8] == 1:
                event_type = 'Blacklisted'
                heading = 'Restricted Vehicle Details'
            elif data[8] == 2:
                event_type = 'Unknown'
                heading = 'Un-Registered Vehicle Details'

        if event_data is None and data:
            event_data = [
                {"label": "Vehicle No", "value": data[0]},
                {"label": "Event No", "value": "35098"},
                {"label": "Direction", "value": "Leaving"},
                {"label": "Event Time", "value": "05.17:35"},
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

        print("vehicle data------>", data)

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
                row_frame.grid(sticky="ew", pady=5)

                label = CTkLabel(
                    row_frame,
                    text=item["label"] + ':',
                    font=("Inter", 14, "bold"),
                    text_color="#B0B8C4",
                    anchor="w"
                )
                label.grid(row=0, column=0, sticky="w", padx=(10, 5))

                # Modified value_label styling based on Event Type
                if item["label"] == "Event Type":
                    if item["value"] == "Blacklisted":
                        bg_color = "#FF4B4B"  # Red for blacklisted
                    elif item["value"] == "Verified":
                        bg_color = "#28A745"  # Green for verified
                    else:
                        bg_color = "#FFA500"  # Orange for unknown

                    value_label = CTkLabel(
                        row_frame,
                        text=item["value"],
                        font=("Inter", 14, "bold"),
                        text_color="#FFFFFF",
                        fg_color=bg_color,
                        corner_radius=6
                    )
                else:
                    value_label = CTkLabel(
                        row_frame,
                        text=item["value"],
                        font=("Inter", 14),
                        text_color="#FFFFFF",
                        anchor="w"
                    )

                value_label.grid(row=0, column=1, sticky="w", padx=(5, 10), ipadx=5, ipady=2)

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

        # Content frame
        vehicle_content_frame = CTkFrame(
            vehicle_box,
            fg_color="transparent"
        )
        vehicle_content_frame.pack(pady=10, padx=20, fill="both", expand=True)

        if event_type == "Unknown":
            # Message frame with icon and text
            message_frame = CTkFrame(
                vehicle_content_frame,
                fg_color="transparent"
            )
            message_frame.pack(pady=(30, 20))

            # Info/warning message
            CTkLabel(
                message_frame,
                text="Vehicle details not available\nFor Un-Registered vehicle.",
                font=("Inter", 14),
                text_color="#B0B8C4",
                justify="center"
            ).pack(pady=10)

            # Styled button frame
            button_frame = CTkFrame(
                vehicle_content_frame,
                fg_color="transparent"
            )
            button_frame.pack(pady=20)

            self.add_vehicle_button = CTkButton(
                button_frame,
                text="Add this vehicle",
                font=("Inter", 15, "bold"),
                fg_color="#28A745",
                hover_color="#218838",
                height=38,
                corner_radius=6,
                width=180,
                border_width=2,
                command=lambda: print("add vehicle button clicked")
            )
            self.add_vehicle_button.pack(pady=10)

        else:
            # Normal vehicle details display for known vehicles
            for item in vehicle_data:
                row_frame = CTkFrame(vehicle_content_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=5)

                CTkLabel(
                    row_frame,
                    text=item["label"] + ":",
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
    def show_acknowledge_dialog(self,data=None,vehicleimg=None, plateimg=None,event_data= None):
        self.create_acknowledgment_frame(data=data,vehicle_image=vehicleimg,plate_image=plateimg , event_data= event_data)



    def reset_interface(self):
        # Clean up popup before resetting interface
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


