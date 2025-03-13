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

    def bind_form_button(self):
        self.obj_NotificationInterface.button_submit.configure(command=self.onclick_acknowledge_submit)

    def bind_buttons(self) -> None:
        self.obj_NotificationInterface.button_acknowledge.configure(command=self.onclick_acknowledge)

        # self.obj_NotificationInterface.button_submit.configure(command=self.onclick_submit)
        # self.obj_NotificationInterface.button_acknowledge.configure(command=self.onclick_acknowledge)

    def add_vehicle_data(self, db_data_list):
        """
        Adds unrecognized person data to the vehicle_data list.
        """
        if not hasattr(self, 'vehicle_data'):
            self.vehicle_data = []

        for db_data in db_data_list:
            self.vehicle_data.append({
                "event_id": db_data.get("event_id"),
                "captured_img": db_data.get("captured_img"),
                "person_img": db_data.get("person_img"),
                "person_name": db_data.get("person_name"),
                "person_age": db_data.get("person_age"),
                "person_gender": db_data.get("person_gender"),
                "start_time": db_data.get("start_time"),
                "end_time":db_data.get("end_time"),
                "status": db_data.get("status"),
                "alert_type": "Unrecognized Person",
                "acknowledgment_note": db_data.get("acknowledgment_message", ""),
                "acknowledgment_time": db_data.get("acknowledgment_time")
            })

        self.obj_NotificationInterface.vehicle_data = self.vehicle_data
        self.obj_NotificationInterface.update_alarm_list()

    def onclick_acknowledge(self):
        self.obj_NotificationInterface.show_acknowledge_dialog()

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
