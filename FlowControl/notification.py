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
        db_data_list = self.obj_core.obj_event.fetch_unrecognized_persons()
        self.obj_NotificationInterface.button_next.configure(command=self.obj_NotificationInterface.handle_next)
        self.obj_NotificationInterface.button_previous.configure(command=self.obj_NotificationInterface.handle_previous)

        self.add_person_data(db_data_list)

        self.bind_buttons()

    def bind_form_button(self):
        self.obj_NotificationInterface.button_submit.configure(command=self.onclick_acknowledge_submit)

    def bind_buttons(self) -> None:
        self.obj_NotificationInterface.button_acknowledge.configure(command=self.onclick_acknowledge)

        # self.obj_NotificationInterface.button_submit.configure(command=self.onclick_submit)
        # self.obj_NotificationInterface.button_acknowledge.configure(command=self.onclick_acknowledge)

    def add_person_data(self, db_data_list):
        """
        Adds unrecognized person data to the person_data list.
        """
        if not hasattr(self, 'person_data'):
            self.person_data = []

        for db_data in db_data_list:
            self.person_data.append({
                "event_id": db_data.get("event_id"),
                "captured_img": db_data.get("captured_img"),
                "person_img": db_data.get("person_img"),
                "person_name": db_data.get("person_name"),
                "person_age": db_data.get("person_age"),
                "person_gender": db_data.get("person_gender"),
                "start_time": db_data.get("start_time"),
                "end_time":db_data.get("end_time","1234"),
                "status": db_data.get("status"),
                "alert_type": "Unrecognized Person",
                "acknowledgment_note": db_data.get("acknowledgment_message", ""),
                "acknowledgment_time": db_data.get("acknowledgment_time")
            })

        self.obj_NotificationInterface.person_data = self.person_data
        self.obj_NotificationInterface.update_alarm_list()

    def onclick_acknowledge(self):
        self.obj_NotificationInterface.show_acknowledge_dialog()

    def onclick_acknowledge_submit(self):
        note = self.obj_NotificationInterface.text_note.get("1.0", "end").strip()

        if note != '':
            # Debug prints
            print("Selected person info:")
            print(f"Type: {type(self.obj_NotificationInterface.selected_person)}")
            print(f"Value: {self.obj_NotificationInterface.selected_person}")

            # # Get the actual person_name from selected_person
            # person_name = None
            # for person in self.person_data:
            #     if person["person_name"] == self.obj_NotificationInterface.selected_person:
            #         person_name = person["person_name"]
            #         break
            person_name = self.obj_NotificationInterface.selected_person
            if person_name:
                print(f"Found person_name: {person_name}")
                result = self.obj_event.insert_acknowledgment(
                    person_name,  # Pass person_name instead of event_id
                    note
                )

                print(f"Acknowledgment Result: {result}")

                if result:
                    # Close acknowledgment frame and update list
                    self.obj_NotificationInterface.close_acknowledgment_frame()
                    self.obj_NotificationInterface.handle_acknowledgment_submit()
                    self.obj_NotificationInterface.update_alarm_list()
                else:
                    print("Failed to insert acknowledgment")
            else:
                print("Could not find person_name for selected person")

    # def onclick_submit(self):
    #     acknowledgment_note = self.obj_NotificationInterface.text_note.get("1.0", "end").strip()
    #     acknowledgment_result = self.obj_core.obj_event.insert_acknowledgment(self.obj_NotificationInterface.selected_person, acknowledgment_note)
