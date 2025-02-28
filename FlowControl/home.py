import logging
from tkinter import StringVar


from shared_queue import all_camera_data , current_camera_details
from Core.main import Core
from Interface.main import Interface


class HomeController:

    def __init__(self, Core: Core, Interface: Interface):
        self.obj_Core = Core
        self.obj_Interface = Interface
        self.obj_HomeInterface = self.obj_Interface.dict_frames["home"]
        self.bind_buttons()
        self.bind_settings_buttons()
        self.restore_all_camera_name()
        self.set_camera_name()
        self.obj_HomeInterface.bind("<Unmap>", lambda event: self.on_minimize(event))
        self.obj_HomeInterface.bind("<Map>", lambda event: self.on_window_restored(event))

    def set_camera_name(self):
        """
        Set the camera name in the home interface based on available camera data.
        Prioritize a camera named 'rtsp' if available; otherwise, use the first camera in the data.
        """
        try :
            # Get the count of cameras and fetch all camera data
            count = self.obj_Core.obj_Camera.get_camera_count()
            camera_data = self.obj_Core.obj_Camera.fetch_all_Camera_data()
            for camera in camera_data:
                camera_info = {
                    "camera_name": camera.get('Camera_name','N/A'),
                    "roi_start": camera.get('ROIStartPercentageHeight','15'),
                    'roi_end':camera.get('ROIEndPercentageHeight','90'),
                    "status": camera.get('Camera_direction','N/A'),
                    "rtsp_url": camera.get('URL','N/A')
                }
                all_camera_data.append(camera_info)


            # Check if there are cameras available and the data is valid
            if count > 0 and camera_data:
                # Try to find a camera named 'rtsp'
                rtsp_camera = next((camera for camera in camera_data if camera.get('Camera_name') == 'rtsp'), None)

                # Use the 'rtsp' camera if found; otherwise, use the first camera
                selected_camera_name = rtsp_camera.get('Camera_name') if rtsp_camera else camera_data[0].get('Camera_name',
                                                                                                             'N/A')
                self.obj_HomeInterface.selected_camera = selected_camera_name

                current_camera_details = next((cam for cam in all_camera_data if cam["camera_name"] == selected_camera_name), None)
                # Configure the entry with the selected camera name
                self.obj_HomeInterface.entry_selected_camera.configure(
                    textvariable=StringVar(value=selected_camera_name)
                )
            else:
                # Handle cases where no cameras are available
                self.obj_HomeInterface.selected_camera = ''
                self.obj_HomeInterface.entry_selected_camera.configure(
                    textvariable=StringVar(value='N/A')
                )
        except Exception as e:
            print(e)


    def on_minimize(self, event=None):
        try:
            # Check if 'camera_manager' exists in the dictionary and has a 'popup' attribute
            if 'camera_manager' in self.obj_Interface.dict_frames and hasattr(
                    self.obj_Interface.dict_frames['camera_manager'], 'popup'):
                self.obj_Interface.dict_frames['camera_manager'].popup.iconify()
            else:
                logging.warning("'camera_manager' or 'popup' attribute not found during minimize operation.")
        except Exception as e:
            logging.error(f"An error occurred during minimize: {e}")
        try:
           
            if 'vehicle_list' in self.obj_Interface.dict_frames and hasattr(
                    self.obj_Interface.dict_frames['vehicle_list'], 'popup'):
                self.obj_Interface.dict_frames['vehicle_list'].popup.iconify()
            else:
                logging.warning("'vehicle_list' or 'popup' attribute not found during minimize operation.")
        except Exception as e:
            logging.error(f"An error occurred during minimize: {e}")

        try:

            if  hasattr(self.obj_Interface.dict_frames['historical_event'], 'ack_window'):
                print("type ",type(self.obj_Interface.dict_frames['historical_event'].ack_window))
                self.obj_Interface.dict_frames['historical_event'].ack_window.iconify()
            else:
                print("'historical_event' or 'popup' attribute not found during minimize operation.")
        except Exception as e:
            logging.error(f"An error occurred during minimize: {e}")

        try:

            if hasattr(self.obj_Interface.dict_frames['notification'], 'ack_window'):
                print("type ", type(self.obj_Interface.dict_frames['historical_event'].ack_window))
                self.obj_Interface.dict_frames['notification'].ack_window.iconify()
            else:
                print("'historical_event' or 'popup' attribute not found during minimize operation.")
        except Exception as e:
            logging.error(f"An error occurred during minimize: {e}")
        


    def on_window_restored(self, event=None):
        try:
            # Check if 'camera_manager' exists in the dictionary and has a 'popup' attribute
            if 'camera_manager' in self.obj_Interface.dict_frames and hasattr(
                    self.obj_Interface.dict_frames['camera_manager'], 'popup'):
                self.obj_Interface.dict_frames['camera_manager'].popup.deiconify()
            else:
                logging.warning("'camera_manager' or 'popup' attribute not found during restore operation.")
        except Exception as e:
            logging.error(f"An error occurred during restore: {e}")
        try:
            # Check if 'vehicle_list' exists in the dictionary and has a 'popup' attribute
            if 'vehicle_list' in self.obj_Interface.dict_frames and hasattr(
                    self.obj_Interface.dict_frames['vehicle_list'], 'popup'):
                self.obj_Interface.dict_frames['vehicle_list'].popup.deiconify()
            else:
                logging.warning("'vehicle_list' or 'popup' attribute not found during restore operation.")
        except Exception as e:
            logging.error(f"An error occurred during restore: {e}")

        try:

            if  hasattr(self.obj_Interface.dict_frames['historical_event'], 'ack_window'):
                print("type ",type(self.obj_Interface.dict_frames['historical_event'].ack_window))
                self.obj_Interface.dict_frames['historical_event'].ack_window.deiconify()
            else:
                print("'historical_event' or 'popup' attribute not found during minimize operation.")
        except Exception as e:
            logging.error(f"An error occurred during minimize: {e}")

        try:

            if hasattr(self.obj_Interface.dict_frames['notification'], 'ack_window'):
                print("type ", type(self.obj_Interface.dict_frames['historical_event'].ack_window))
                self.obj_Interface.dict_frames['notification'].ack_window.deiconify()
            else:
                print("'historical_event' or 'popup' attribute not found during minimize operation.")
        except Exception as e:
            logging.error(f"An error occurred during minimize: {e}")


    def restore_all_camera_name(self):
        all_camera = self.obj_Core.obj_Camera.fetch_all_Camera_data()
        camera_names = [camera['Camera_name'] for camera in all_camera]
        self.obj_HomeInterface.list_camera = camera_names

    def bind_buttons(self) -> None:
        self.obj_HomeInterface.button_live_event.configure(
            command=lambda: self.onclick_menu_buttons(self.obj_HomeInterface.button_live_event))
        self.obj_HomeInterface.button_add_vehicle.configure(
            command=lambda: self.onclick_menu_buttons(self.obj_HomeInterface.button_add_vehicle))
        # self.obj_HomeInterface.button_vehicle_list.configure(
        #     command=lambda: self.onclick_menu_buttons(self.obj_HomeInterface.button_vehicle_list))
        self.obj_HomeInterface.button_delete_vehicle.configure(
            command=lambda: self.onclick_menu_buttons(self.obj_HomeInterface.button_delete_vehicle))
        self.obj_HomeInterface.button_historical_event.configure(
            command=lambda: self.onclick_menu_buttons(self.obj_HomeInterface.button_historical_event))
       # self.obj_HomeInterface.button_menu.configure(command=self.onclick_menu)
        self.obj_HomeInterface.button_user.configure(command=self.onclick_user_button)
        self.obj_HomeInterface.button_edit.configure(
            command=lambda: self.onclick_menu_buttons(self.obj_HomeInterface.button_edit))
        self.obj_HomeInterface.button_create_user.configure(
            command=lambda: self.onclick_menu_buttons(self.obj_HomeInterface.button_create_user))
        self.obj_HomeInterface.button_signout_1.configure(command=self.onclick_signout)
        self.obj_HomeInterface.button_signout_2.configure(command=self.onclick_signout)
        self.obj_HomeInterface.button_notification.configure(
            command=self.onclick_notification_button)
        self.obj_HomeInterface.button_settings.configure(
            command=self.onclick_settings_button
        )


    def onclick_camera_manager(self):
        self.obj_HomeInterface.update_menu_buttons_state(self.obj_HomeInterface.button_camera_settings)
        self.obj_Interface.switch_frames('camera_manager')

    def onclick_audio_manager(self) -> None:
        self.obj_Interface.dict_frames['camera_manager'].reset_interface()
        self.obj_HomeInterface.update_menu_buttons_state(self.obj_HomeInterface.button_audio_settings)
        self.obj_Interface.switch_frames('audio_manager')

    def bind_settings_buttons(self) -> None:
        """Bind the settings submenu buttons after they are created"""
        if hasattr(self.obj_HomeInterface, 'button_camera_settings'):
            self.obj_HomeInterface.button_camera_settings.configure(
                command=lambda: self.onclick_submenu_button("camera")
            )
        if hasattr(self.obj_HomeInterface, 'btn_vehicle_manager'):
            self.obj_HomeInterface.btn_vehicle_manager.configure(
                command=lambda: self.onclick_submenu_button("vehicle_list")
            )
        if hasattr(self.obj_HomeInterface, 'button_audio_settings'):
            self.obj_HomeInterface.button_audio_settings.configure(
                command=lambda: self.onclick_audio_manager()
            )

    def onclick_settings_button(self) -> None:
        """Handle settings button click and bind submenu buttons"""
        # Update the settings button state first
        self.obj_HomeInterface.update_menu_buttons_state(self.obj_HomeInterface.button_settings)
        # Then toggle the popup
        self.obj_HomeInterface.toggle_settings_popup()
        # Bind the submenu buttons
        self.bind_settings_buttons()
    def onclick_submenu_button(self, option: str) -> None:

        self.obj_Interface.dict_frames["add_vehicle"].reset_interface()
        self.obj_Interface.dict_frames["delete_vehicle"].reset_interface()
        self.obj_Interface.dict_frames["vehicle_list"].reset_interface()
        self.obj_Interface.dict_frames["historical_event"].reset_interface()
        self.obj_Interface.dict_frames['camera_manager'].reset_interface()
        self.obj_Interface.dict_frames['vehicle_list'].reset_checkbox()

        if option == "camera":
            # Update button state for camera manager
            self.obj_HomeInterface.update_menu_buttons_state(self.obj_HomeInterface.button_camera_settings)
            self.obj_Interface.dict_frames['camera_manager'].update_camera_data_list()
            self.obj_Interface.dict_frames['camera_manager'].update_table(self.obj_Interface.dict_frames['camera_manager'].dummy_camera_details)
            self.obj_HomeInterface.hide_frame_camera()
            self.obj_Interface.switch_frames('camera_manager')


        elif option == 'vehicle_list':
            self.obj_Interface.dict_frames['camera_manager'].reset_interface()
            self.obj_HomeInterface.hide_frame_camera()
            # Update button state for ROI
            self.obj_HomeInterface.update_menu_buttons_state(self.obj_HomeInterface.btn_vehicle_manager)

            # self.obj_Interface.dict_frames["vehicle_list"].reset_filter_criteria()
            # self.obj_Interface.dict_frames[
            #     "vehicle_list"].vehicle_data = self.obj_Core.obj_Vehicle.fetch_vehicle_details(
            #     self.obj_Interface.dict_frames["vehicle_list"].i_end_index,
            #     self.obj_Interface.dict_frames["vehicle_list"].dict_filter_criteria)
            # self.obj_Interface.dict_frames["vehicle_list"].i_total_data = self.obj_Core.obj_Vehicle.get_data_count(
            #     self.obj_Interface.dict_frames["vehicle_list"].dict_filter_criteria)
            # i_total_data_fetched = len(self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)
            # if (i_total_data_fetched > 0):
            #     self.obj_Interface.dict_frames["vehicle_list"].i_start_index = 1
            #     self.obj_Interface.dict_frames["vehicle_list"].i_end_index += i_total_data_fetched
            # self.obj_Interface.dict_frames["vehicle_list"].update_table(
            #     self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)
            # self.obj_Interface.switch_frames("vehicle_list")

            self.obj_Interface.dict_frames["vehicle_list"].reset_filter_criteria()
            self.obj_Interface.dict_frames["vehicle_list"].vehicle_data = self.obj_Core.obj_Vehicle.fetch_vehicle_details(self.obj_Interface.dict_frames["vehicle_list"].dict_filter_criteria)
            self.obj_Interface.dict_frames["vehicle_list"].i_total_data = len(self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)
            if (self.obj_Interface.dict_frames["vehicle_list"].i_total_data > 0):
                self.obj_Interface.dict_frames["vehicle_list"].i_start_index = 1
                self.obj_Interface.dict_frames["vehicle_list"].i_end_index = 5 if self.obj_Interface.dict_frames["vehicle_list"].i_total_data >= 5 else self.obj_Interface.dict_frames["vehicle_list"].i_total_data
            self.obj_Interface.dict_frames["vehicle_list"].update_table((self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)[0:5])
            self.obj_Interface.switch_frames("vehicle_list")

        elif option == 'audio':
            self.obj_Interface.dict_frames['camera_manager'].reset_interface()
            # Update button state for audio manager
            self.obj_HomeInterface.update_menu_buttons_state(self.obj_HomeInterface.button_audio_settings)
            self.obj_HomeInterface.hide_frame_camera()
            self.obj_Interface.switch_frames('audio_manager')

    def onclick_camera_button(self, frame_name: str, button) -> None:
        """Handle camera-related button clicks without destroying the camera menu"""
        self.obj_HomeInterface.update_menu_buttons_state(button)  # Update the state of the clicked button
        self.obj_Interface.switch_frames(frame_name)

    def onclick_menu_buttons(self, button_menu) -> None:
        # Reset interfaces
        self.obj_Interface.dict_frames["add_vehicle"].reset_interface()
        self.obj_Interface.dict_frames["delete_vehicle"].reset_interface()
        self.obj_Interface.dict_frames["vehicle_list"].reset_interface()
        self.obj_Interface.dict_frames["historical_event"].reset_interface()
        self.obj_Interface.dict_frames['camera_manager'].reset_interface()
        self.obj_Interface.dict_frames['vehicle_list'].reset_checkbox()
        self.obj_HomeInterface.update_profile_icon_menu_button_state('reset')
        self.obj_HomeInterface.hide_frame_camera()

        if (self.obj_HomeInterface.bool_user_popup is True):
            self.obj_HomeInterface.toggle_user_popup()

        self.obj_HomeInterface.update_menu_buttons_state(button_menu)

        # Handle button clicks
        if (button_menu == self.obj_HomeInterface.button_add_vehicle):
            self.obj_Interface.switch_frames("add_vehicle")
        elif (button_menu == self.obj_HomeInterface.button_delete_vehicle):
            self.obj_Interface.switch_frames("delete_vehicle")
        elif (button_menu == self.obj_HomeInterface.button_edit):

            self.obj_Interface.dict_frames["edit_user"].user_details_update(
                self.obj_Core.dict_user_data["str_user_name"],
                self.obj_Core.dict_user_data["str_password"]
            )
            self.obj_Interface.switch_frames("edit_user")
            self.obj_HomeInterface.update_profile_icon_menu_button_state('edit_user')
        elif (button_menu == self.obj_HomeInterface.button_create_user):
            self.obj_Interface.switch_frames("create_user")
            self.obj_HomeInterface.update_profile_icon_menu_button_state('new_user')
        elif (button_menu == self.obj_HomeInterface.button_live_event):
            self.restore_all_camera_name()
            self.obj_Interface.switch_frames("live_feed")
            self.obj_HomeInterface.show_frame_camera()

        elif (button_menu == self.obj_HomeInterface.button_historical_event):
            self.obj_Interface.dict_frames["historical_event"].reset_filter_criteria()
            list_historical_events, self.obj_Interface.dict_frames[
                "historical_event"].event_starting_date = self.obj_Core.obj_event.fetch_event_combo_details(
                self.obj_Interface.dict_frames["historical_event"].i_end_index,
                self.obj_Interface.dict_frames["historical_event"].dict_filter_criteria)
            self.obj_Interface.dict_frames["historical_event"].i_total_data = self.obj_Core.obj_event.get_data_count(
                self.obj_Interface.dict_frames["historical_event"].dict_filter_criteria)
            i_total_data_fetched = len(list_historical_events)
            if (i_total_data_fetched > 0):
                self.obj_Interface.dict_frames["historical_event"].i_start_index = 1
                self.obj_Interface.dict_frames["historical_event"].i_end_index += i_total_data_fetched
            self.obj_Interface.dict_frames["historical_event"].update_table(list_historical_events)
            self.obj_Interface.switch_frames("historical_event")
        elif (button_menu == self.obj_HomeInterface.button_settings):
            self.obj_Interface.switch_frames("settings")



    def onclick_notification_button(self):
        self.obj_Interface.dict_frames['home'].dot_label.configure(text='')
        self.obj_HomeInterface.reset_menu_highlight()

        db_data_list = self.obj_Core.obj_event.fetch_unrecognized_vehicles()
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

    def onclick_menu(self) -> None:
        self.obj_HomeInterface.toggle_menu_bar()

    def onclick_user_button(self) -> None:
        self.obj_HomeInterface.toggle_user_popup()

    def onclick_signout(self) -> None:
        if (self.obj_HomeInterface.bool_user_popup is True):
            self.obj_HomeInterface.toggle_user_popup()

        self.obj_Interface.dict_frames["home"].starting_home_screen()
        self.obj_Interface.switch_frames("signin")