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
        db_data_list = self.obj_core.obj_event.fetch_unrecognized_vehicles()

        self.add_vehicle_data(db_data_list)

        self.bind_buttons()
        # self.start_periodic_updates()

    def start_periodic_updates(self):
        # Schedule vehicle data refresh every 30 seconds
        self.obj_core.obj_event.fetch_unrecognized_vehicles()

    def refresh_vehicle_data(self):
        # Fetch latest unacknowledged vehicles
        db_data_list = self.obj_core.obj_event.fetch_unrecognized_vehicles()

        # Update vehicle data in interface
        if db_data_list:
            self.add_vehicle_data(db_data_list)

        # Schedule next refresh
        self.obj_Interface.dict_frames["notification"].after(30000, self.refresh_vehicle_data)
    def bind_form_button(self):
        self.obj_NotificationInterface.button_submit.configure(command=self.onclick_acknowledge_submit)

    def bind_buttons(self) -> None:
        self.obj_NotificationInterface.button_acknowledge.configure(command=self.onclick_acknowledge)

        # self.obj_NotificationInterface.button_submit.configure(command=self.onclick_submit)
        # self.obj_NotificationInterface.button_acknowledge.configure(command=self.onclick_acknowledge)

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
                "alert_type": "Alarm" if db_data.get("alarm") else "Alert",
                "acknowledgment_note": db_data.get("acknowledgment_message", ""),
                "acknowledgment_time": db_data.get("acknowledgment_time")
            })

        self.obj_NotificationInterface.vehicle_data = self.vehicle_data
        self.obj_NotificationInterface.update_alarm_list()

    def onclick_acknowledge(self):
        print("seelected vehicle is ", self.obj_NotificationInterface.selected_vehicle_number)
        self.obj_NotificationInterface.show_acknowledge_dialog(data= self.obj_core.obj_Vehicle.fetch_single_vehicle_data(self.obj_NotificationInterface.selected_vehicle_number))

    def onclick_acknowledge_submit(self):
        if self.obj_NotificationInterface.text_note.get("1.0", "end").strip() != '':
            # Debug prints
            print("Selected vehicle info:")
            print(f"Type: {type(self.obj_NotificationInterface.selected_vehicle)}")
            print(f"Value: {self.obj_NotificationInterface.selected_vehicle}")

            # Get the actual event_id
            event_id = None
            for vehicle in self.vehicle_data:
                if vehicle["vehicle_event_id"] == self.obj_NotificationInterface.selected_vehicle:
                    event_id = vehicle["vehicle_event_id"]
                    break

            if event_id:
                print(f"Found event_id: {event_id}")
                result = self.obj_event.insert_acknowledgment(
                    event_id,
                    self.obj_NotificationInterface.text_note.get("1.0", "end").strip()
                )

                print(f"Acknowledgment Result: {result}")

                if result:
                    self.obj_NotificationInterface.close_acknowledgment_frame()
                    self.obj_NotificationInterface.handle_acknowledgment_submit()
                    self.obj_NotificationInterface.update_alarm_list()
                else:
                    print("Failed to insert acknowledgment")
            else:
                print("Could not find event_id for selected vehicle")
    # def onclick_submit(self):
    #     acknowledgment_note = self.obj_NotificationInterface.text_note.get("1.0", "end").strip()
    #     acknowledgment_result = self.obj_core.obj_event.insert_acknowledgment(self.obj_NotificationInterface.selected_vehicle, acknowledgment_note)
