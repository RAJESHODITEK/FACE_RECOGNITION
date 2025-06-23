from click import command
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage, CTkCanvas, CTkScrollableFrame, CTkEntry, CTkTextbox
from PIL import Image
import random
from datetime import datetime, timedelta

from Core.event import Event
from Core.main import Core

from Interface.main import Interface
from Interface.notification import NotificationInterface


class NotificationController:
    def __init__(self, Core: Core, Interface: Interface):
        self.obj_core = Core
        self.obj_event = Event(self.obj_core.dict_db_details, self.obj_core.dict_user_data)
        self.obj_Interface = Interface
        self.obj_NotificationInterface = self.obj_Interface.dict_frames["notification"]
        self.obj_NotificationInterface.on_form_ready = self.bind_form_button
        self.obj_NotificationInterface.label_heading_for_miss.bind("<Button-1>", self.onclick_missed_event)
        self.obj_NotificationInterface.button_next.configure(command=self.obj_NotificationInterface.handle_next)
        self.obj_NotificationInterface.button_previous.configure(command=self.obj_NotificationInterface.handle_previous)
        db_data_list = self.obj_core.obj_event.fetch_unrecognized_vehicles()

        self.add_vehicle_data(db_data_list)

        self.bind_buttons()

    def onclick_missed_event(self,event=None):
        db_data_list = self.obj_core.obj_event.fetch_missed_vehicles()
        # Update vehicle data in interface
        if db_data_list:
            temp_notification_data=[]
            for db_data in db_data_list:
                temp_notification_data.append({
                    "vehicle_event_id": db_data.get("event_id"),
                    "vehicle_img": db_data.get("vehicle_img"),
                    "number_plate_img": db_data.get("number_plate_img"),
                    "vehicle_number": db_data.get("vehicle_number"),
                    "number_plate_color": db_data.get("number_plate_color"),
                    "country": db_data.get("country"),
                    "capture_time": db_data.get("time"),
                    "status": db_data.get("status"),
                    "alert_type": "Blacklisted",
                    "acknowledgment_note": db_data.get("acknowledgment_message", ""),
                    "acknowledgment_time": db_data.get("acknowledgment_time")
                })
            self.obj_Interface.dict_frames['notification'].vehicle_data= temp_notification_data
            self.obj_Interface.dict_frames['notification'].update_alarm_list()

        self.obj_Interface.switch_frames("notification")


    def refresh_vehicle_data(self):
        # Fetch latest unacknowledged vehicles
        db_data_list = self.obj_core.obj_event.fetch_unrecognized_vehicles()
        # Update vehicle data in interface
        if db_data_list:
            self.add_vehicle_data(db_data_list)

        # Schedule next refresh
        #self.obj_Interface.dict_frames["notification"].after(3000, self.refresh_vehicle_data)

    def bind_form_button(self):
        self.obj_NotificationInterface.button_submit.configure(command=self.onclick_acknowledge_submit)

    def bind_buttons(self) -> None:
        self.obj_NotificationInterface.button_acknowledge.configure(command=self.onclick_acknowledge)


    def add_vehicle_data(self, db_data_list):

        if not hasattr(self, 'vehicle_data'):
            self.vehicle_data = []

        for db_data in db_data_list:
            self.vehicle_data.append({
                "vehicle_event_id": db_data.get("event_id"),
                "vehicle_img": db_data.get("vehicle_img"),
                "number_plate_img": db_data.get("number_plate_img"),
                "vehicle_number": db_data.get("vehicle_number"),
                "number_plate_color": db_data.get("number_plate_color"),
                "country": db_data.get("country"),
                "capture_time": db_data.get("time"),
                "status": db_data.get("status"),
                "alert_type": "Blacklisted" ,
                "acknowledgment_note": db_data.get("acknowledgment_message", ""),
                "acknowledgment_time": db_data.get("acknowledgment_time")
            })

        self.obj_NotificationInterface.vehicle_data = self.vehicle_data
        self.obj_NotificationInterface.update_alarm_list()

    def onclick_acknowledge(self):
        self.obj_NotificationInterface.show_acknowledge_dialog( self.obj_core.obj_Vehicle.fetch_single_vehicle_data(self.obj_NotificationInterface.selected_vehicle_number)['vehicle_data'])

    def onclick_acknowledge_submit(self):
        if self.obj_NotificationInterface.text_note.get("1.0", "end").strip() != '':
            event_id =self.obj_NotificationInterface.selected_vehicle
            if event_id:
                result = self.obj_event.insert_acknowledgment(
                    event_id,
                    self.obj_NotificationInterface.text_note.get("1.0", "end").strip()
                )

                if result:
                    self.obj_NotificationInterface.close_acknowledgment_frame()
                    self.obj_NotificationInterface.handle_acknowledgment_submit()
                    self.obj_NotificationInterface.update_alarm_list()
                    self.obj_Interface.on_error(
                        "home",
                        "Acknowledged Successfully !",
                        "The selected vehicle is now acknowledged.",
                        "#63CA6D"
                    )
                else:

                    self.obj_Interface.on_error(
                        "home",
                        "Acknowledge failed !",
                        "Some internal error occurred .",
                        "#FF4B4B"
                    )
            else:
                self.obj_Interface.on_error(
                    "home",
                    "Acknowledge failed !",
                    "Event ID not found for this selected event.",
                    "#FF4B4B"
                )
