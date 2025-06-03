import base64
import os
from functools import partial
from io import BytesIO

from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCanvas, CTkScrollableFrame, CTkImage, CTkTextbox, \
    CTkToplevel, CTkFont
from tkinter import StringVar, Spinbox
from tkcalendar import Calendar
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageDraw, ImageFont
import datetime


class HistoricalEventInterface(CTkFrame):

    def __init__(self, *args, root_width: int = 1920, root_height: int = 1080, **kwargs):

        super().__init__(*args, **kwargs)

        self.bool_filter_popup = False
        self.bool_sdate_dropdown_opened = False
        self.bool_edate_dropdown_opened = False
        self.bool_person_dropdown_opened = False
        self.bool_status_dropdown_opened = False




        self.current_person_id = self.current_person_number = ''
        self.current_person_image= self.current_captured_image= None
        self.label_imge=None
        self.event_starting_date = ""
        self.eventType = 0
        self.current_event_details= None
        self.add_person_button= None
        self.configure(fg_color="#F1F5FA", corner_radius=0)
        self.master.bind("<FocusOut>", self.on_focus_out)



        self.image_references = []

        self.i_start_index = 0
        self.i_end_index = 0
        self.i_total_data = 0
        self.dict_filter_criteria = {
            "str_start_timeperiod": "",
            "str_end_timeperiod": "",
            "str_person_name": "",
            "str_status": ""  # Add status to filter criteria
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
        self.frame_table.grid(row=2, column=0, padx=(15, 2), pady=(10, 10), sticky="nsew")

        # self.white_label = CTkLabel(
        #     self.frame_form,
        #     text="",
        #     fg_color="red",
        #     font=("", 14),
        #     height=40
        # )
        # self.white_label.grid(row=3, column=0, columnspan=2, padx=15, pady=(0, 0), sticky="ew")
        #

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



        self.lable_person_number = CTkLabel(
            self.frame_filter_form_lcol,
            text="Person Name",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w",
            fg_color="transparent",
        )
        self.lable_person_number.grid(row=4, column=0, padx=15, pady=(15, 0), sticky="ew")

        self.frame_person_number_dropdown = CTkFrame(
            self.frame_filter_form_lcol,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_person_number_dropdown.columnconfigure(0, weight=1)
        self.frame_person_number_dropdown.rowconfigure(0, weight=1)
        self.frame_person_number_dropdown.grid(row=5, column=0, padx=(15, 0), pady=(2, 0), sticky="ew")

        self.entry_selected_person = CTkEntry(
            self.frame_person_number_dropdown,
            height=40,
            fg_color="#F6F6F6",
            textvariable=StringVar(value="Select person"),
            text_color="#828282",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
            #state="disabled"
        )
        self.entry_selected_person.grid(row=0, column=0, sticky="nsew")

        img_down_arraow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(20, 20))
        self.button_select_person = CTkButton(
            self.frame_person_number_dropdown,
            image=img_down_arraow,
            height=25,
            width=20,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_person.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)

        # Add Status Label
        self.lable_status = CTkLabel(
            self.frame_filter_form_rcol,
            text="Status",
            text_color="#2C2C2C",
            font=("", 14),
            anchor="w",
            fg_color="transparent",
        )
        self.lable_status.grid(row=4, column=0, padx=15, pady=(15, 0), sticky="ew")

        # Add Status Entry Field
        self.frame_status_dropdown = CTkFrame(
            self.frame_filter_form_rcol,
            height=40,
            fg_color="#F6F6F6",
            corner_radius=5,
        )
        self.frame_status_dropdown.columnconfigure(0, weight=1)
        self.frame_status_dropdown.rowconfigure(0, weight=1)
        self.frame_status_dropdown.grid(row=5, column=0, padx=(15, 0), pady=(2, 0), sticky="ew")

        self.entry_selected_status = CTkEntry(
            self.frame_status_dropdown,
            height=40,
            fg_color="#F6F6F6",
            textvariable=StringVar(value="Select status"),
            text_color="#828282",
            border_color="#DEDEDE",
            border_width=2,
            corner_radius=5,
            font=("", 14),
        )
        self.entry_selected_status.grid(row=0, column=0, sticky="nsew")

        img_down_arrow = CTkImage(Image.open(".\\Resources\\images\\down_arrow_icon.png"), size=(20, 20))
        self.button_select_status = CTkButton(
            self.frame_status_dropdown,
            image=img_down_arrow,
            height=25,
            width=20,
            text="",
            fg_color="transparent",
            cursor="hand2",
            border_width=0,
            hover=False,
        )
        self.button_select_status.grid(row=0, column=0, sticky="e", padx=3, pady=1.5)

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

        self.frame_maindropdown_lwindow = CTkFrame(
            self.frame_filter_form_lcol,
            fg_color="#DEDEDE",
            height=40,
            corner_radius=5
        )
        self.frame_maindropdown_lwindow.columnconfigure(0, weight=1)
        self.frame_maindropdown_lwindow.rowconfigure(0, weight=1)
        self.frame_maindropdown_lwindow.grid_propagate(False)

        self.frame_maindropdown_rwindow = CTkFrame(
            self.frame_filter_form_rcol,
            fg_color="#DEDEDE",
            height=40,
            corner_radius=5
        )
        self.frame_maindropdown_rwindow.columnconfigure(0, weight=1)
        self.frame_maindropdown_rwindow.rowconfigure(0, weight=1)
        self.frame_maindropdown_rwindow.grid_propagate(False)

    def on_focus_out(self, event):
        """Destroy ack_window when main window loses focus"""
        if hasattr(self, 'ack_window') and self.ack_window.winfo_exists():
            self.ack_window.destroy()



    def convert_rgb_to_bgr(self, image_param):
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
                        return Image.new('RGB', (230, 185), color=(200, 200, 200))
                elif os.path.exists(image_param):
                    image = Image.open(image_param)
                else:
                    print(f"Image file not found: {image_param}")
                    return Image.new('RGB', (230, 185), color=(200, 200, 200))
            else:
                print(f"Unsupported image type: {type(image_param)}")
                return Image.new('RGB', (230, 185), color=(200, 200, 200))

            if image.mode != "RGB":
                image = image.convert("RGB")

            return image

        except Exception as e:
            print(f"Error processing image: {e}")
            return Image.new('RGB', (230, 185), color=(200, 200, 200))

    def on_page_change(self):



        if int(self.i_total_data) == 0:
            self.label_data_count.configure(text="No Records Found!", text_color="#FF0000")
        else:
            # Use the i_end_index set by update_table, but cap it by total data
            actual_displayed = min(5, self.i_total_data - self.i_start_index)
            self.i_end_index = min(self.i_end_index, self.i_start_index + actual_displayed)
            print(f"on_page_change: i_start_index={self.i_start_index}, i_end_index={self.i_end_index}, "
                  f"i_total_data={self.i_total_data}, actual_displayed={actual_displayed}")
            self.label_data_count.configure(
                text=f"Showing {self.i_start_index + 1} - {self.i_end_index} of {self.i_total_data} entries",
                text_color="#2c2c2c"
            )

        enabled_color = "#374151"
        enabled_hover = "#1F2937"
        disabled_color = "#e6e6ff"

        self.update_button_state(
            button=self.button_previous,
            state="disabled" if self.i_start_index <= 0 else "normal",
            cursor="X_cursor" if self.i_start_index <= 0 else "hand2",
            fg_color=disabled_color if self.i_start_index <= 0 else enabled_color,
            hover_color=disabled_color if self.i_start_index <= 0 else enabled_hover,
        )

        self.update_button_state(
            button=self.button_next,
            state="disabled" if self.i_end_index >= self.i_total_data else "normal",
            cursor="X_cursor" if self.i_end_index >= self.i_total_data else "hand2",
            fg_color=disabled_color if self.i_end_index >= self.i_total_data else enabled_color,
            hover_color=disabled_color if self.i_end_index >= self.i_total_data else enabled_hover,
        )

    def update_table(self, list_historical_events: list):
        event_details = None
        for child in self.frame_table.winfo_children():
            child.destroy()

        # Define color scheme with consistent row color
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
        header_frame = CTkFrame(
            self.frame_table,
            fg_color="#232E51",
            corner_radius=7,
            height=60
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))
        header_frame.grid_propagate(False)

        header_1 = CTkLabel(
            header_frame,
            # text="📸 Captured Image",
            text="Captured Image",
            font=CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="white",
            anchor="center",
        )

        header_2 = CTkLabel(
            header_frame,
            # text="🪪 Identity Details",
            text="Identity Details",
            font=CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="white",
            anchor="center",
        )

        header_3 = CTkLabel(
            header_frame,
            # text="📊 Activity Timeline",
            text="Activity Timeline",
            font=CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="white",
            anchor="center",
        )

        header_4 = CTkLabel(
            header_frame,
            # text="👤 Actual Image",
            text="Actual Image",
            font=CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="white",
            anchor="center",
        )

        # Now you can place these headers manually using place() instead of grid or pack
        # These are example placements - adjust x and y coordinates as needed
        header_1.place(relx=0.08, rely=0.5, anchor="center")
        header_2.place(relx=0.27, rely=0.5, anchor="center")
        header_3.place(relx=0.56, rely=0.5, anchor="center")
        header_4.place(relx=0.871, rely=0.5, anchor="center")

        # Add elegant spacing
        spacer = CTkFrame(self.frame_table, height=3, fg_color="transparent")
        spacer.grid(row=1, column=0)

        try:
            logo_img = Image.open("Resources\\images\\prop.jpg")
        except (FileNotFoundError, IOError):
            logo_img = Image.new("RGB", (500, 500), color="#F0F0F0")
            draw = ImageDraw.Draw(logo_img)
            draw.rectangle([50, 40, 300, 300], fill="#2563EB")  # Draw a blue rectangle as a simple logo
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except IOError:
                font = ImageFont.load_default()
            draw.text((100, 75), "LOGO", fill="white", font=font, anchor="mm")

        logo_img = logo_img.resize((300, 300), Image.Resampling.LANCZOS)
        self.i_row_index = self.i_start_index + 1
        for row_index, row_data in enumerate(list_historical_events):
            row_bg_color = COLORS["card"]

            event_details = row_data

            image_width, image_height = 230, 185

            bgr_image_of_person = Image.new("RGB", (image_width, image_height),
                                            color="#F0F0F0")  # Light gray background
            if row_data.get("photo_path"):
                bgr_image_of_person = self.convert_rgb_to_bgr(row_data["photo_path"])
            else:
                # Create placeholder with logo instead of text
                bgr_image_of_person = Image.new("RGB", (image_width, image_height), color="#F0F0F0")
                # Calculate position to center the logo
                paste_x = (image_width - logo_img.width) // 2
                paste_y = (image_height - logo_img.height) // 2
                bgr_image_of_person.paste(logo_img, (paste_x, paste_y))

            # Handle captured image
            bgr_image_of_captured = Image.new("RGB", (image_width, image_height),
                                              color="#F0F0F0")  # Light gray background
            if row_data.get("captured_img"):
                bgr_image_of_captured = self.convert_rgb_to_bgr(row_data["captured_img"])
            else:
                bgr_image_of_captured = Image.new("RGB", (image_width, image_height), color="#F0F0F0")
                paste_x = (image_width - logo_img.width) // 2
                paste_y = (image_height - logo_img.height) // 2
                bgr_image_of_captured.paste(logo_img, (paste_x, paste_y))

            # Resize images without enhancement effects
            person_img_pil = bgr_image_of_person.resize(
                (image_width, image_height),
                Image.Resampling.LANCZOS
            )

            captured_img_pil = bgr_image_of_captured.resize(
                (image_width, image_height),
                Image.Resampling.LANCZOS
            )

            # Convert to PhotoImage
            person_img = ImageTk.PhotoImage(person_img_pil)
            captured_img = ImageTk.PhotoImage(captured_img_pil)

            frame_row = CTkFrame(
                self.frame_table,
                height=220,
                fg_color=row_bg_color,
                corner_radius=20,
                border_width=2,
                border_color=COLORS["border"]
            )

            # Modified: Adjusted column weights to give more space to the details section
            frame_row.columnconfigure(0, weight=2)  # Image column
            frame_row.columnconfigure(1, weight=3)  # Details column - increased weight
            frame_row.columnconfigure(2, weight=2)  # Timeline column
            frame_row.columnconfigure(3, weight=2)  # Actual image column

            frame_row.rowconfigure(0, weight=1)
            frame_row.grid_propagate(False)
            frame_row.grid(row=row_index + 2, column=0, sticky="nsew", padx=20, pady=12)

            status = row_data.get("status", "0")
            alarm_value = 0
            if status == 'WhiteList' or status == 'white-list':
                alarm_value = 1  # Verified (green)
            elif status == 'BlackList':
                alarm_value = 2  # Restricted (red)
            # else stays 0 (Unknown - orange)

            print(f"Status from DB: '{row_data.get('status')}' for person: {row_data.get('person_name')}")

            img_frame = CTkFrame(
                frame_row,
                corner_radius=15,
                fg_color=COLORS["accent"],
                border_width=2,
                border_color=status_config[alarm_value]["border_color"]
            )
            img_frame.grid(row=0, column=0, sticky="w", padx=(20, 10), pady=15)

            label_imge = CTkLabel(
                img_frame,
                image=captured_img,
                text="",
                height=image_height,
                width=image_width,
                fg_color="transparent",
                corner_radius=12
            )
            label_imge.pack(padx=5, pady=5)

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

            # Modified: Increased the width of the details frame and adjusted layout
            frame_details = CTkFrame(
                frame_row,
                height=190,
                width=320,  # Increased width
                fg_color="transparent",
                corner_radius=12
            )
            frame_details.rowconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="row_height")
            frame_details.columnconfigure(0, weight=1)
            frame_details.grid(row=0, column=1, padx=(0, 5), pady=15, sticky="nsew")
            frame_details.grid_propagate(False)  # Prevent resizing based on content

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

            status_types = {
                0: "Unknown",
                1: "Verified",
                2: "Restricted"
            }
            person_type = status_types.get(alarm_value, "Unknown")

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

            field_mappings = {
                "person_name": {"title": "Person Name", "value": row_data.get("person_name", ""), "icon": "👤"},
                "age": {"title": "Age", "value": row_data.get("person_age", ""), "icon": "🔢"},
                "gender": {"title": "Gender", "value": row_data.get("person_gender", ""), "icon": "⚧️"},
                "person_type": {"title": "Status", "value": person_type, "icon": status_config[alarm_value]["icon"]},
                "Camera Name": {"title": "Camera Name", "value": "Entry Gate", "icon": "📸"}
            }

            # Modified: Adjusted the field layout for better text display
            for idx, (key, data) in enumerate(field_mappings.items()):
                frame_cell = CTkFrame(
                    frame_details,
                    fg_color="transparent",
                    corner_radius=8,
                    height=30,
                    width=320  # Increased width
                )
                frame_cell.grid(row=idx + 1, column=0, sticky="ew", pady=3)

                # Icon container with accent circle
                icon_container = CTkFrame(
                    frame_cell,
                    width=28,
                    height=28,
                    corner_radius=14,
                    fg_color=COLORS["accent"],
                )
                icon_container.pack(side="left", padx=(3, 8))
                icon_container.pack_propagate(False)

                # Center the icon in the circle
                CTkLabel(
                    icon_container,
                    text=data["icon"],
                    font=CTkFont(size=16),
                    width=20,
                    height=20,
                    text_color="black",
                    fg_color="transparent"
                ).place(relx=0.5, rely=0.5, anchor="center")

                # Modified: Reduced the fixed width of the label to allow for text wrapping
                CTkLabel(
                    frame_cell,
                    text=f"{data['title']}",
                    font=CTkFont(family="Helvetica", size=14, weight="bold"),
                    text_color=COLORS["primary_dark"],
                    width=90,  # Reduced width
                    anchor="w"
                ).pack(side="left")

                # Special styling for status field
                if key == "person_type":
                    CTkLabel(
                        frame_cell,
                        text=": ",
                        font=CTkFont(family="Helvetica", size=14, weight="bold"),
                        text_color=COLORS["primary_dark"],
                        anchor="w"
                    ).pack(side="left", padx=(0, 2))
                    status_label = CTkLabel(
                        frame_cell,
                        text=data["value"],
                        font=CTkFont(family="Helvetica", size=13, weight="bold"),
                        text_color="white",
                        fg_color=status_config[alarm_value]["border_color"],
                        corner_radius=4,
                        width=120,  # Allows the text to fit
                        height=26
                    )
                    status_label.pack(side="left", padx=(0, 0))
                elif key == "person_name":
                    # Modified: Special handling for names with dynamic font sizing
                    CTkLabel(
                        frame_cell,
                        text=": ",
                        font=CTkFont(family="Helvetica", size=14, weight="bold"),
                        text_color=COLORS["primary_dark"],
                        anchor="w"
                    ).pack(side="left", padx=(0, 2))

                    # Name value container with horizontal scrolling if needed
                    name_value_frame = CTkFrame(
                        frame_cell,
                        fg_color="transparent",
                        width=170  # Maximum width for the name
                    )
                    name_value_frame.pack(side="left", fill="x", expand=True)

                    # Calculate dynamic font size based on name length
                    name_text = str(data["value"])
                    if len(name_text) <= 17:
                        font_size = 13  # Default size for names up to 17 characters
                    elif len(name_text) <= 25:
                        font_size = 11  # Smaller size for names between 18-25 characters
                    elif len(name_text) <= 35:
                        font_size = 9  # Even smaller for names between 26-35 characters
                    else:
                        font_size = 8  # Minimum size for very long names (over 35 characters)

                    CTkLabel(
                        name_value_frame,
                        text=name_text,
                        font=CTkFont(family="Helvetica", size=font_size),  # Use dynamic font size
                        text_color=COLORS["text_secondary"],
                        anchor="w",
                        wraplength=165  # Still keep wrapping for extremely long names
                    ).pack(side="left", fill="x", expand=True)
                else:
                    CTkLabel(
                        frame_cell,
                        text=": ",
                        font=CTkFont(family="Helvetica", size=14, weight="bold"),
                        text_color=COLORS["primary_dark"],
                        anchor="w"
                    ).pack(side="left", padx=(0, 2))

                    CTkLabel(
                        frame_cell,
                        text=str(data["value"]),
                        font=CTkFont(family="Helvetica", size=13),
                        text_color=COLORS["text_secondary"],
                        anchor="w"
                    ).pack(side="left", padx=(0, 0))

            # Timeline frame
            frame_additional_details = CTkFrame(
                frame_row,
                height=190,
                width=290,  # Adjusted width
                fg_color="transparent",
                corner_radius=12
            )
            frame_additional_details.grid(row=0, column=2, sticky="nsew", padx=(0, 5), pady=15)
            frame_additional_details.grid_propagate(False)

            # Timeline container setup
            timeline_container = CTkFrame(
                frame_additional_details,
                fg_color=COLORS["accent"],
                corner_radius=15,
                border_width=2,
                border_color=COLORS["border"],
                height=190,
                width=280
            )
            timeline_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10))
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

            # Add connector line for Unknown and Verified status
            if alarm_value == 0 or alarm_value == 1:  # Unknown or Verified status
                connector_frame = CTkFrame(
                    timeline_container,
                    fg_color="transparent",
                    height=20
                )
                connector_frame.pack(fill="x", padx=15, pady=0)

                # Create a vertical line to connect dots
                connector_line = CTkFrame(
                    connector_frame,
                    width=2,
                    height=20,
                    fg_color=COLORS["border"]  # Use border color for the line
                )
                connector_line.pack(side="left", padx=(9, 0))  # Align with the dots

            # Last seen entry with small red dot
            last_seen_frame = CTkFrame(
                timeline_container,
                fg_color="transparent"
            )
            last_seen_frame.pack(fill="x", padx=15, pady=(5, 10))

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

            # Only show acknowledgment for Restricted (2) status
            if alarm_value == 2:  # Restricted status
                acknowledged_frame = CTkFrame(
                    timeline_container,
                    fg_color="transparent"
                )
                acknowledged_frame.pack(fill="x", padx=15, pady=(5, 10))

                # Determine acknowledgment status and color
                has_acknowledgment = "No"
                acknowledgment_color = COLORS["danger"]  # Default to red for "No"

                if row_data.get("acknowledgment_message") is not None:
                    has_acknowledgment = "Yes"
                    acknowledgment_color = COLORS["success"]  # Green for "Yes"

                CTkLabel(
                    acknowledged_frame,
                    text="●",  # Dot indicator
                    font=CTkFont(family="Helvetica", size=23, weight="bold"),
                    text_color=acknowledgment_color,  # Use dynamic color based on status
                    anchor="w"
                ).pack(side="left", padx=(5, 5))

                # Acknowledged label
                CTkLabel(
                    acknowledged_frame,
                    text="Is Acknowledged :",
                    font=CTkFont(family="Helvetica", size=13, weight="bold"),
                    text_color=COLORS["text_primary"],
                    anchor="w"
                ).pack(side="left", padx=(5, 0))

                CTkLabel(
                    acknowledged_frame,
                    text=has_acknowledgment,  # Display dynamic Yes/No value
                    font=CTkFont(family="Helvetica", size=12, weight="bold"),
                    text_color=acknowledgment_color,  # Use dynamic color for the status text
                    anchor="w"
                ).pack(side="left", padx=(5, 0))
            elif alarm_value == 0:  # Keep the existing behavior for Unknown status
                # For Unknown status, add a spacer to maintain proper layout spacing
                spacer_frame = CTkFrame(
                    timeline_container,
                    height=30,
                    fg_color="transparent"
                )
                spacer_frame.pack(fill="x", padx=15, pady=(5, 10))
            else:  # For Verified status (1), also add a spacer like Unknown
                # Add the same spacer as for Unknown status
                spacer_frame = CTkFrame(
                    timeline_container,
                    height=30,
                    fg_color="transparent"
                )
                spacer_frame.pack(fill="x", padx=15, pady=(5, 10))

            # Get current status configuration
            event_id_current = row_data.get("event_id", "")
            person_name_current = row_data.get("person_name", "")
            eventType = alarm_value

            plate_container = CTkFrame(
                frame_row,
                fg_color="white",
                width=image_width + 20,
                height=image_height + 20,
                corner_radius=18,
                border_width=2,
                border_color=COLORS["border"]
            )
            plate_container.grid(row=0, column=3, sticky="e", padx=(0, 20), pady=15)
            plate_container.grid_propagate(False)

            self.label_imge = CTkLabel(
                plate_container,
                image=person_img,
                text="",
                height=image_height,
                width=image_width,
                cursor='hand2',
                fg_color="transparent",
                corner_radius=12
            )
            self.label_imge.pack(padx=8, pady=8, expand=True)

            # view_button = CTkButton(
            #     plate_container,
            #     text="View Details",
            #     width=120,
            #     height=30,
            #     corner_radius=15,
            #     fg_color=COLORS["primary"],
            #     hover_color=COLORS["primary_dark"],
            #     text_color="white",
            #     font=CTkFont(family="Helvetica", size=12, weight="bold"),
            #     command=lambda event_id=event_id_current,
            #                    person=person_name_current,
            #                    pimg=person_img,
            #                    cimg=captured_img,
            #                    evdata=event_details,
            #                    evtype=eventType: self.on_row_click(None, event_id, person, pimg, cimg, evdata, evtype)
            # )
            # view_button.pack(pady=8)

            self.label_imge.bind("<Button-1>",
                                 partial(self.on_row_click,
                                         event_id_current=event_id_current,
                                         person_number=person_name_current,
                                         personimg=person_img,
                                         capturedimg=captured_img,
                                         eventdata=event_details,
                                         eventType=eventType))

            self.create_tooltip(self.label_imge, "Click To View Detailed Info")

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

    def create_acknowledgment_frame(self, event_data=None, person_data=None, person_image=None,
                                    captured_image=None, data=None, eventType: int = None):
        # First, properly cleanup any existing window
        self.cleanup_popup()

        # Determine event type and heading based on eventType
        event_type_map = {
            0: {"type": "Unknown", "heading": "Un-Registered Person Details", "color": "#FFC107", "icon": "⚠️"},
            1: {"type": "Verified", "heading": "Authorized Person Details", "color": "#4CAF50", "icon": "✅"},
            2: {"type": "Restricted", "heading": "Restricted Person Details", "color": "#F44336", "icon": "⛔"}
        }

        event_info = event_type_map.get(eventType, {"type": "Unknown", "heading": "Un-Registered Person Details",
                                                    "color": "#FFC107", "icon": "⚠️"})
        event_type = event_info["type"]
        heading = event_info["heading"]
        status_color = event_info["color"]
        status_icon = event_info["icon"]

        # Extract data from event_data or data
        person_name = ""
        event_id = ""
        gender = ""
        age = ""
        start_time = ""
        end_time = ""
        status = event_type
        camera_name = "Entry Gate"  # Default value as shown in update_table

        # Format timestamps with elegant styling
        def format_timestamp(timestamp_value):
            if not timestamp_value:
                return "N/A"
            try:
                timestamp = float(timestamp_value)
                if timestamp > 0:
                    return datetime.datetime.fromtimestamp(timestamp).strftime('%b %d, %Y • %H:%M:%S')
                return "N/A"
            except (ValueError, TypeError):
                return str(timestamp_value)

        # Process event data correctly
        if data:
            # When called directly with data array or dict
            person_name = data[0] if isinstance(data, (list, tuple)) else data.get("person_name", "N/A")
            event_id = "35098"  # Default if not present
            gender = data.get(2, "N/A") if isinstance(data, (list, tuple)) else data.get("person_gender", "N/A")
            age = data.get("person_age", "N/A") if isinstance(data, dict) else "N/A"
            start_time = format_timestamp(data.get("start_time")) if isinstance(data, dict) else "N/A"
            end_time = format_timestamp(data.get("end_time")) if isinstance(data, dict) else "N/A"
        elif event_data:
            # When called with event_data dictionary from update_table
            person_name = event_data.get("person_name", "N/A")
            event_id = event_data.get("event_id", "N/A")
            gender = event_data.get("person_gender", "N/A")
            age = event_data.get("person_age", "N/A")
            start_time = format_timestamp(event_data.get("start_time"))
            end_time = format_timestamp(event_data.get("end_time"))

        # Window setup with modern dark theme
        self.ack_window = CTkToplevel(self.master)  # Set master as the parent
        self.ack_window.geometry("950x550")
        self.ack_window.title("Face Recognition")
        self.ack_window.configure(bg="#121828")
        self.ack_window.resizable(False, False)

        # Make the ack_window transient to the main window (keeps it above main window only)
        self.ack_window.transient(self.master)

        # Bind close event to cleanup
        self.ack_window.protocol("WM_DELETE_WINDOW", self.cleanup_popup)

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

        # Left Box for Captured Image with enhanced styling
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
            text="CAPTURED IMAGE",
            font=("Inter", 14, "bold"),
            text_color="#FFFFFF",
            bg_color="transparent"
        ).pack(pady=5)

        # Captured Image Container with scanning animation and overlay effects
        person_image_container = CTkFrame(
            left_box,
            fg_color="transparent",
        )
        person_image_container.pack(expand=True, fill="both", padx=20, pady=(5, 20))

        # Image frame with border
        image_frame = CTkFrame(
            person_image_container,
            fg_color="#121828",
            corner_radius=8,
            border_width=1,
            border_color="#3B4B88"
        )
        image_frame.pack(expand=True, fill="both")

        # Calculate appropriate image size
        container_width = 380
        container_height = 280

        # Create elements for the scanning animation
        scanning_placeholder = CTkFrame(
            image_frame,
            fg_color="#121828",
            width=container_width,
            height=container_height,
        )
        scanning_placeholder.pack(expand=True, pady=10, padx=10)

        scanning_text = CTkLabel(
            scanning_placeholder,
            text="SCANNING...",
            font=("Inter", 16, "bold"),
            text_color="#4D79FF",
        )
        scanning_text.place(relx=0.5, rely=0.2, anchor="center")

        scan_line = CTkFrame(
            scanning_placeholder,
            width=container_width - 20,
            height=2,
            fg_color="#4D79FF"
        )
        scan_line.place(relx=0.5, rely=0.3, anchor="center")

        face_box = CTkFrame(
            scanning_placeholder,
            width=150,
            height=150,
            fg_color="transparent",
            border_width=2,
            border_color="#4D79FF",
            corner_radius=5
        )
        face_box.place(relx=0.5, rely=0.5, anchor="center")

        for x_pos, y_pos in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            point = CTkFrame(
                face_box,
                width=6,
                height=6,
                fg_color="#4D79FF",
                corner_radius=3
            )
            point.place(relx=x_pos, rely=y_pos, anchor="center")

        processing_status = CTkLabel(
            scanning_placeholder,
            text="Processing facial features...",
            font=("Inter", 12),
            text_color="#6D7A9E",
        )
        processing_status.place(relx=0.5, rely=0.8, anchor="center")

        # Function to animate the scan line
        def animate_scan_line(current_pos=0.3, direction=1):
            try:
                # Additional checks to ensure all required widgets exist and are valid
                if (not hasattr(self, 'ack_window') or
                        not self.ack_window.winfo_exists() or
                        not scan_line.winfo_exists()):
                    return

                new_pos = current_pos + 0.02 * direction

                # Constrain the position between 0.3 and 0.7
                if new_pos > 0.7:
                    direction = -1
                    new_pos = 0.7
                elif new_pos < 0.3:
                    direction = 1
                    new_pos = 0.3

                # Use a try-except block to catch any placement errors
                try:
                    scan_line.place(relx=0.5, rely=new_pos, anchor="center")
                except Exception as placement_error:
                    print(f"Placement error: {placement_error}")
                    return

                # Use a weak reference to avoid potential circular references
                import weakref
                weak_self = weakref.ref(self)

                # Modify the after call to include error handling
                def safe_animate():
                    self_ref = weak_self()
                    if self_ref and hasattr(self_ref, 'ack_window') and self_ref.ack_window.winfo_exists():
                        animate_scan_line(new_pos, direction)

                self.ack_window.after(30, safe_animate)

            except Exception as e:
                print(f"Error in animate_scan_line: {e}")
                # Optionally log the full traceback
                import traceback
                traceback.print_exc()
        # Start the scan line animation
        animate_scan_line()

        # Function to show the final captured image after animation
        def show_final_image():
            if not hasattr(self, 'ack_window') or not self.ack_window.winfo_exists():
                return
            scanning_text.destroy()
            scan_line.destroy()
            face_box.destroy()
            processing_status.destroy()
            complete_message = CTkLabel(
                scanning_placeholder,
                text="ANALYSIS COMPLETE",
                font=("Inter", 16, "bold"),
                text_color="#4CAF50",
            )
            complete_message.place(relx=0.5, rely=0.5, anchor="center")
            self.ack_window.after(500, lambda: display_captured_image(complete_message))

        # Function to display the final captured image
        def display_captured_image(message_label=None):
            if not hasattr(self, 'ack_window') or not self.ack_window.winfo_exists():
                return
            if message_label:
                message_label.destroy()
            scanning_placeholder.destroy()
            if captured_image:
                captured_imagen = self.resize_ctk_image(captured_image, (container_width, container_height))
                image_label = CTkLabel(
                    image_frame,
                    image=captured_imagen,
                    text="",
                )
                image_label.pack(expand=True, pady=10, padx=10)
            else:
                CTkLabel(
                    image_frame,
                    text="NO CAPTURED IMAGE",
                    font=("Inter", 14),
                    text_color="#6D7A9E",
                ).pack(expand=True)

        # Schedule the switch to the final image after 1 second
        self.ack_window.after(1000, show_final_image)

        # Right Box with enhanced styling
        right_box = CTkFrame(
            info_boxes_frame,
            fg_color="#1A2138",
            border_width=1,
            border_color="#3B4B88",
            corner_radius=10,
            width=440,
            height=380
        )
        right_box.pack(side="right", padx=(10, 0), fill="both", expand=True)
        right_box.pack_propagate(False)

        # Right box header with the person's name
        name_header = CTkFrame(
            right_box,
            fg_color="#232942",
            corner_radius=8,
            height=40
        )
        name_header.pack(fill="x", padx=10, pady=10)

        CTkLabel(
            name_header,
            text=person_name,
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

        # Image frame with enhanced border - Now showing person_image (Actual Image)
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

        if person_image:
            inner_frame = CTkFrame(
                capture_frame,
                fg_color="transparent",
            )
            inner_frame.pack(expand=True, fill="both", padx=8, pady=8)
            person_imagen = self.resize_ctk_image(person_image, (160, 160))
            CTkLabel(
                inner_frame,
                image=person_imagen,
                text="",
            ).pack(expand=True, fill="both")
        else:
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
                text="ACTUAL IMAGE",
                text_color="#6D7A9E",
                font=("Inter", 12)
            ).pack(expand=True)

        # Main data frame for standard fields
        data_frame = CTkFrame(
            right_content_frame,
            fg_color="transparent"
        )
        data_frame.pack(side="left", fill="both", expand=True, anchor="n")

        # Event ID
        row_frame = CTkFrame(
            data_frame,
            fg_color="#232942",
            corner_radius=6,
            height=28
        )
        row_frame.pack(fill="x", pady=4, anchor="w")
        CTkLabel(
            row_frame,
            text="👤",
            font=("Inter", 12),
            width=25,
            text_color="#FFFFFF",
            anchor="w"
        ).pack(side="left", padx=(8, 0))
        CTkLabel(
            row_frame,
            text="Event ID         :",
            font=("Inter", 12, "bold"),
            text_color="#A0AEC0",
            anchor="w",
            width=100
        ).pack(side="left", padx=(5, 0))
        CTkLabel(
            row_frame,
            text=event_id,
            font=("Inter", 12),
            text_color="#FFFFFF",
            anchor="w"
        ).pack(side="left", padx=(5, 0))

        # Age
        row_frame = CTkFrame(
            data_frame,
            fg_color="#232942",
            corner_radius=6,
            height=28
        )
        row_frame.pack(fill="x", pady=4, anchor="w")
        CTkLabel(
            row_frame,
            text="🔢",
            font=("Inter", 12),
            width=25,
            text_color="#FFFFFF",
            anchor="w"
        ).pack(side="left", padx=(8, 0))
        CTkLabel(
            row_frame,
            text="Age                  :",
            font=("Inter", 12, "bold"),
            text_color="#A0AEC0",
            anchor="w",
            width=100
        ).pack(side="left", padx=(5, 0))
        CTkLabel(
            row_frame,
            text=age,
            font=("Inter", 12),
            text_color="#FFFFFF",
            anchor="w"
        ).pack(side="left", padx=(5, 0))

        # Gender
        row_frame = CTkFrame(
            data_frame,
            fg_color="#232942",
            corner_radius=6,
            height=28
        )
        row_frame.pack(fill="x", pady=4, anchor="w")
        CTkLabel(
            row_frame,
            text="⚧️",
            font=("Inter", 12),
            width=25,
            text_color="#FFFFFF",
            anchor="w"
        ).pack(side="left", padx=(8, 0))
        CTkLabel(
            row_frame,
            text="Gender           :",
            font=("Inter", 12, "bold"),
            text_color="#A0AEC0",
            anchor="w",
            width=100
        ).pack(side="left", padx=(5, 0))
        CTkLabel(
            row_frame,
            text=gender,
            font=("Inter", 12),
            text_color="#FFFFFF",
            anchor="w"
        ).pack(side="left", padx=(5, 0))

        # Status
        row_frame = CTkFrame(
            data_frame,
            fg_color="#232942",
            corner_radius=6,
            height=28
        )
        row_frame.pack(fill="x", pady=4, anchor="w")
        CTkLabel(
            row_frame,
            text=status_icon,
            font=("Inter", 12),
            width=25,
            text_color="#FFFFFF",
            anchor="w"
        ).pack(side="left", padx=(8, 0))
        CTkLabel(
            row_frame,
            text="Status              :",
            font=("Inter", 12, "bold"),
            text_color="#A0AEC0",
            anchor="w",
            width=100
        ).pack(side="left", padx=(5, 0))
        status_value_label = CTkLabel(
            row_frame,
            text=status,
            font=("Inter", 12, "bold"),
            text_color="white",
            fg_color=status_color,
            corner_radius=4,
            width=80,
            height=22
        )
        status_value_label.pack(side="left", padx=(5, 0))

        # Camera Name
        row_frame = CTkFrame(
            data_frame,
            fg_color="#232942",
            corner_radius=6,
            height=28
        )
        row_frame.pack(fill="x", pady=4, anchor="w")
        CTkLabel(
            row_frame,
            text="📸",
            font=("Inter", 12),
            width=25,
            text_color="#FFFFFF",
            anchor="w"
        ).pack(side="left", padx=(8, 0))
        CTkLabel(
            row_frame,
            text="Camera Name :",
            font=("Inter", 12, "bold"),
            text_color="#A0AEC0",
            anchor="w",
            width=100
        ).pack(side="left", padx=(5, 0))
        CTkLabel(
            row_frame,
            text=camera_name,
            font=("Inter", 12),
            text_color="#FFFFFF",
            anchor="w"
        ).pack(side="left", padx=(5, 0))

        # Create a container for timeline data (first seen & last seen)
        timeline_container = CTkFrame(
            right_box,
            fg_color="#232942",
            corner_radius=8,
            border_width=1,
            border_color="#3B4B88"
        )
        timeline_container.pack(fill="x", padx=15, pady=(10, 20), side="bottom")

        # Timeline entries container
        timeline_entries = CTkFrame(
            timeline_container,
            fg_color="transparent"
        )
        timeline_entries.pack(fill="x", padx=15, pady=10)

        # First seen entry with small green dot
        first_seen_frame = CTkFrame(
            timeline_entries,
            fg_color="transparent"
        )
        first_seen_frame.pack(fill="x", pady=(0, 5))

        first_seen_dot = CTkFrame(
            first_seen_frame,
            width=10,
            height=10,
            corner_radius=5,
            fg_color="#4CAF50"  # Green
        )
        first_seen_dot.pack(side="left", padx=(5, 10))

        first_seen_content = CTkFrame(
            first_seen_frame,
            fg_color="transparent"
        )
        first_seen_content.pack(side="left", fill="x", expand=True)

        CTkLabel(
            first_seen_content,
            text="First Seen:",
            font=("Inter", 13, "bold"),
            text_color="#A0AEC0",
            anchor="w",
            width=80
        ).pack(side="left", padx=(0, 5))
        CTkLabel(
            first_seen_content,
            text=start_time if start_time else "N/A",
            font=("Inter", 12),
            text_color="#FFFFFF",
            anchor="w"
        ).pack(side="left")

        # Add connector line
        line_frame = CTkFrame(
            timeline_entries,
            width=2,
            height=20,
            fg_color="#3B4B88"
        )
        line_frame.pack(padx=(9, 0), anchor="w")

        # Last seen entry with small red dot
        last_seen_frame = CTkFrame(
            timeline_entries,
            fg_color="transparent"
        )
        last_seen_frame.pack(fill="x", pady=(5, 0))

        last_seen_dot = CTkFrame(
            last_seen_frame,
            width=10,
            height=10,
            corner_radius=5,
            fg_color="#F44336"  # Red
        )
        last_seen_dot.pack(side="left", padx=(5, 10))

        last_seen_content = CTkFrame(
            last_seen_frame,
            fg_color="transparent"
        )
        last_seen_content.pack(side="left", fill="x", expand=True)

        CTkLabel(
            last_seen_content,
            text="Last Seen:",
            font=("Inter", 13, "bold"),
            text_color="#A0AEC0",
            anchor="w",
            width=80
        ).pack(side="left", padx=(0, 5))
        CTkLabel(
            last_seen_content,
            text=end_time if end_time else "N/A",
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

        # After info_boxes_frame.pack(...) and before any subsequent frame packing
        if event_data and event_data.get("acknowledgment_message"):
            ack_message_frame = CTkFrame(
                self.ack_frame,  # Use the main ack_frame as the parent
                fg_color="transparent",
                corner_radius=0,
                width=930


            )
            ack_message_frame.pack(fill="x", padx=0, pady=(10, 20), after=info_boxes_frame)

            ack_content_frame = CTkFrame(
                ack_message_frame,
                fg_color="transparent"
            )
            ack_content_frame.pack(padx=15, pady=0, fill="x")

            star_label = CTkLabel(
                ack_content_frame,
                text="Acknowledge Message : ",
                font=("Inter", 15, "bold"),
                text_color="#00ADB5",
                bg_color="transparent"
            )
            star_label.pack(side="left", padx=(0, 5))

            message_label = CTkLabel(
                ack_content_frame,
                text=event_data["acknowledgment_message"],
                font=("Inter", 13, "bold"),
                text_color="#FFFFFF",
                bg_color="transparent"
            )
            message_label.pack(side="left")

        # # Close button with premium styling
        # close_button = CTkButton(
        #     footer_frame,
        #     text="CLOSE",
        #     font=("Inter", 12, "bold"),
        #     fg_color="#2D3250",
        #     hover_color="#3B4272",
        #     corner_radius=8,
        #     width=120,
        #     height=36,
        #     command=self.ack_window.destroy
        # )
        # close_button.pack(side="right")
        #
        # # Additional action button based on event type
        # action_text = "VERIFY" if event_type == "Unknown" else "VIEW DETAILS"
        # action_color = "#4D79FF" if event_type == "Unknown" else "#2D3250"
        #
        # action_button = CTkButton(
        #     footer_frame,
        #     text=action_text,
        #     font=("Inter", 12, "bold"),
        #     fg_color=action_color,
        #     hover_color="#3B59B3",
        #     corner_radius=8,
        #     width=120,
        #     height=36
        # )
        # action_button.pack(side="right", padx=10)

        if hasattr(self, 'on_form_ready'):
            self.on_form_ready()

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

    def hide_popup(self):

        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()


    def cleanup_popup(self):
        """Ensure popup is destroyed when the main widget is destroyed"""
        if hasattr(self, 'popup'):
            self.popup.destroy()
        if hasattr(self, 'ack_window'):
            self.ack_window.destroy()

    def on_row_click(self, event, event_id_current, person_number, personimg=None, capturedimg=None, eventdata=None,
                     eventType=None):
        print(f"Row {event_id_current} clicked! person: {person_number} with {eventType}")
        self.current_person_number = person_number
        self.current_person_id = event_id_current
        self.current_person_image = personimg
        self.current_captured_image = capturedimg
        self.current_event_details = eventdata
        self.eventType = eventType

    def format_label(self, label, max_length=12):
        return f"{label.ljust(max_length)} : "

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
                x = widget.winfo_rootx() + widget.winfo_width() - 220
                y = widget.winfo_rooty() + (widget.winfo_height() // 2) + 95
                screen_height = widget.winfo_screenheight()
                if y < int(screen_height+40):
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
        else:
            self.frame_filter.grid_forget()

        self.bool_filter_popup = not self.bool_filter_popup

    def popup_dropdown(self, list_data: list = [], entry_destination: CTkEntry = None, i_row: int = None,i_col: int = 0,
                       i_rowspan: int = 2, side=None):
        if side is None:
            dropframe= self.frame_maindropdown_lwindow
        else:
            dropframe= self.frame_maindropdown_rwindow
        frame_dropdown_table = CTkScrollableFrame(
            dropframe,
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

        dropframe.grid_propagate(False)
        dropframe.grid(row=i_row, column=i_col, rowspan=i_rowspan, columnspan=2, sticky="nsew",
                                            padx=(15, 0), pady=(5, 2))

        dropframe.tkraise()

    def open_calendar(self, entry_destination=None, i_row=None, i_rowspan=2):
        # Create a simple calendar
        calendar = Calendar(
            self.frame_maindropdown_lwindow,
            selectmode="day",
            date_pattern="dd-mm-yyyy",  # Will display as 01-02-2025
            background="#1E1E2E",
            foreground="#FFFFFF",
            height=10,  # Increased height
        )

        # Position the calendar with more vertical space
        calendar.grid(row=0, column=0, padx=8, pady=8, sticky="ew", ipady=20)  # Added ipady for more height

        # Add event binding
        calendar.bind("<<CalendarSelected>>", lambda event: self.select_date(event, calendar, entry_destination))

        # Position the window with increased rowspan for more height
        self.frame_maindropdown_lwindow.grid_propagate(False)
        self.frame_maindropdown_lwindow.grid(
            row=i_row,
            column=0,
            rowspan=i_rowspan + 1,  # Increased rowspan for more height
            columnspan=2,
            sticky="nsew",
            padx=(15, 0),
            pady=10
        )
        self.frame_maindropdown_lwindow.tkraise()
    def close_dropdown(self, event):
        self.frame_maindropdown_lwindow.grid_forget()
        self.frame_maindropdown_rwindow.grid_forget()

        for child in self.frame_maindropdown_lwindow.winfo_children():
            child.destroy()
        for child in self.frame_maindropdown_rwindow.winfo_children():
            child.destroy()

    def reset_filter_form(self):
        today_date = (datetime.date.today()).strftime("%d-%m-%Y")
        today_date = datetime.datetime.strptime(today_date, "%d-%m-%Y")
        today_date = f"{today_date.day:02d}-{today_date.month:02d}-{today_date.year}"

        current_time = datetime.datetime.now()

        self.entry_selected_sdate.configure(state="normal", text_color="#414141", border_color="#DEDEDE")
        self.entry_selected_sdate.delete(0, "end")
        self.entry_selected_sdate.insert(0, today_date)
        self.entry_selected_sdate.configure(state="disabled")

        self.entry_selected_edate.configure(state="normal", text_color="#414141", border_color="#DEDEDE")
        self.entry_selected_edate.delete(0, "end")
        self.entry_selected_edate.insert(0, today_date)
        self.entry_selected_edate.configure(state="disabled")

        self.entry_selected_person.configure(state="normal", text_color="#414141", border_color="#DEDEDE")
        self.entry_selected_person.delete(0, "end")
        self.entry_selected_person.insert(0, "All")
        self.entry_selected_person.configure(state="normal")

        self.entry_selected_status.configure(state="normal", text_color="#414141", border_color="#DEDEDE")
        self.entry_selected_status.delete(0, "end")
        self.entry_selected_status.insert(0, "All")
        self.entry_selected_status.configure(state="normal")

        self.var_spinbox_shour.set("00")
        self.var_spinbox_sminute.set("00")
        self.var_spinbox_ehour.set(f"{current_time.hour:02d}")
        self.var_spinbox_eminute.set(f"{current_time.minute:02d}")

    def select_option(self, selected_option: str, entry_destination: CTkEntry):
        entry_destination.configure(state="normal", text_color="#414141")
        entry_destination.delete(0, "end")
        entry_destination.insert(0, selected_option)
        entry_destination.configure(state="disabled")

        if (entry_destination == self.entry_selected_person):
            self.bool_person_dropdown_opened = False

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
        self.dict_filter_criteria["str_person_number"] = ""

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


