import base64
import io

import numpy as np
import pyodbc
import pygame
import tkinter as tk
from customtkinter import (
    CTk, CTkFrame, CTkLabel, CTkImage
)
from PIL import Image, ImageTk
import cv2
import threading
import queue
import time

from Core.audio import AudioController, AudioThreadManager
from Core.main import Core
from Core.Recognistion_process.ConfigLoader import ConfigLoader
from sympy import false

from shared_queue import shared_queue


class LiveEventInterface(CTkFrame):
    def __init__(self, root, root_width: int = 1920, root_height: int = 1080):
        super().__init__(root)
        imo_height=0

        # Initialize basic properties
        self.root = root
        self.root_width = root_width
        self.root_height = root_height
        self.main_width = int(root_width * 0.95)
        self.main_height = int(root_height * 0.95)
        print("  self.main_height = int(root_height * 0.95)",  self.main_height)
        self.alert_flag = threading.Event()
        self.config=ConfigLoader()
        # Video processing properties
        self.video_queue = queue.Queue(maxsize=10)
        self.detection_queue = queue.Queue(maxsize=10)
        self.running = True
        self.frame_count = 0
        self.details_frames = []
        # self.audio_manager = AudioThreadManager()
        # Start processing threads
        self.start_processing_threads()
        self.dict_db_details = {
            "str_server": "ITDT14",
            "str_username": "sa",
            "str_password": "root1234",
            "str_db_name": "ALPR_DB_NEW",
            "str_user_table": "user_details",
            "str_vehicle_table": "vehicle_details",
            "str_historical_event_table": "event_details"
        }
        # Configure main frame
        self.configure(fg_color="#F1F5FA", corner_radius=0)
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_propagate(False)

        time.sleep(1)
        # Create UI elements
        self.create_layout()

        # Schedule updates
        self.root.after(50, self.update_video_display)
        self.root.after(100, self.update_details_display)

    def create_layout(self):
        # Main Content Frame
        self.main_content = CTkFrame(self, fg_color="#F1F5FA")
        self.main_content.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        self.main_content.grid_columnconfigure(0, weight=1)

        # Title Label
        title = CTkLabel(
            self.main_content,
            text="Live Event",
            font=("", 23, "bold"),
            text_color="#000000",
        )
        title.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        # Content Holder Frame (contains video and detection frames)
        self.content = CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=6)
        self.content.grid_columnconfigure(1, weight=4)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_propagate(False)

        # Live Feed Frame (Left Side - 70%)
        self.create_video_frame()

        # Detection Sidebar (Right Side - 30%)
        self.create_detection_sidebar()

    def create_video_frame(self):
        # Define dimensions for live feed
        self.live_feed_width = int(self.main_width * 0.65)  # 70% of the main width
        self.live_feed_height = self.main_height  # Full height of the main content

        # Container for video feed with shadow effect
        video_container = CTkFrame(
            self.content,
            fg_color="white",
            corner_radius=0,
            border_width=4,
            border_color="white",
            width=self.live_feed_width,
            height= self.live_feed_height
        )
        video_container.grid(row=0, column=0, padx=(0, 0), sticky="nsew")
        video_container.grid_columnconfigure(0, weight=2)
        video_container.grid_rowconfigure(0, weight=1)
        video_container.grid_propagate(False)

        # Inner frame for video
        self.live_feed = CTkFrame(
            video_container,
            fg_color="white",
            corner_radius=0,
            width=self.live_feed_width

        )
        self.live_feed.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.live_feed.grid_columnconfigure(0, weight=1)
        self.live_feed.grid_rowconfigure(0, weight=1)
        self.live_feed.grid_propagate(False)

    def create_detection_sidebar(self):
        # Container for detection entries
        self.sidebar = CTkFrame(
            self.content,
            fg_color="white",
            corner_radius=0,
            border_width=0,
            border_color="white",
            height=self.live_feed_height,
            width=int(self.main_width * 0.35)
        )
        self.sidebar.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 0))
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_propagate(False)

        # Configure 5 equal rows in the sidebar
        for i in range(5):
            self.sidebar.grid_rowconfigure(i, weight=1)

        # Create detection entries
        for i in range(5):
            self.create_detection_entry(self.sidebar, i)

    def create_detection_entry(self, parent, row_index):
        # Define boundary colors in a cyclic pattern
        boundary_colors = "green"
        # border_color = boundary_colors[row_index % len(boundary_colors)]

        # Calculate dimensions for each frame
        frame_height = int(self.live_feed_height / 5) - 10  # Subtract padding

        # Main container frame
        main_frame = CTkFrame(
            parent,
            fg_color="white",
            corner_radius=5,
            border_width=4,
            border_color=boundary_colors,
            height=frame_height,
            width=int(self.main_width * 0.3)
        )
        main_frame.grid(row=row_index, column=0, pady=5, padx=5, sticky="nsew")
        main_frame.grid_propagate(False)

        # Configure two columns: 45% for image, 55% for info
        main_frame.grid_columnconfigure(0, weight=35)  # Image section
        main_frame.grid_columnconfigure(1, weight=65)  # Info section
        main_frame.grid_rowconfigure(0, weight=1)

        # Image section frame
        img_frame = CTkFrame(
            main_frame,
            fg_color="#f0f0f0",  # Light gray background
            corner_radius=0,
            height=frame_height - 0,  # Account for padding
            width=int((self.main_width * 0.3) * 0.43)  # 43% of main frame width
        )
        img_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        img_frame.grid_propagate(False)

        # Image label
        img_label = CTkLabel(
            img_frame,
            text="",
            fg_color="white"
        )
        img_label.grid(row=0, column=0, sticky="nsew")
        img_frame.grid_columnconfigure(0, weight=1)
        img_frame.grid_rowconfigure(0, weight=1)

        # Info section frame
        info_frame = CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=0,
            height=frame_height - 0,
            width=int((self.main_width * 0.3) * 0.82)  # 52% of main frame width
        )
        info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        info_frame.grid_propagate(False)

        # Configure info frame rows
        for i in range(6):  # For 6 info items
            info_frame.grid_rowconfigure(i, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)

        # Store frame references
        self.details_frames.append({
            'frame': main_frame,
            'img_label': img_label,
            'img_frame': img_frame,
            'info_frame': info_frame,
            'plate_value': None,
            'country_value': None,
            'active': False,
            'timestamp': None
        })


    # def alarm_sound(self,play_alert_flag, sound_path='F:/ALPR_SOURCE_CODE/Resources/alertmini.mp3'):
    #     """
    #     Continuously checks the flag and plays the alarm sound if triggered.
    #     :param play_alert_flag: A threading.Event instance used to signal when to play the alarm.
    #     :param sound_path: Path to the sound file to play.
    #     """
    #
    #     def sound_worker():
    #         pygame.mixer.init()  # Initialize the mixer
    #         while True:
    #             play_alert_flag=self.alert_flag
    #             if play_alert_flag.is_set():  # Check if the flag is set
    #                 play_alert_flag.clear()  # Reset the flag
    #                 time.sleep(5)
    #                 try:
    #                     pygame.mixer.music.load(sound_path)  # Load the sound
    #                     pygame.mixer.music.play()  # Play the sound
    #                     while pygame.mixer.music.get_busy():
    #                         time.sleep(0.1)  # Wait for the sound to finish
    #                 except Exception as e:
    #                     print(f"Error playing sound: {e}")
    #                 print("Alert sound stopped!")
    #             time.sleep(0.1)  # Small delay to avoid busy-waiting
    #
    #     # Start the worker thread
    #     threading.Thread(target=sound_worker, daemon=True).start()
    def start_processing_threads(self):
        """Start the video processing threads"""
        self.video_thread = threading.Thread(target=self.video_processing)
        self.video_thread.daemon = True
        self.video_thread.start()

        self.background_thread = threading.Thread(target=self.video_processing_for_background)
        self.background_thread.daemon = True
        self.background_thread.start()

    def video_processing(self):
        """Process video frames for the main display."""
        while self.running:
          #  print("length of shared queue: ", shared_queue.qsize())
            time.sleep(0.1)
            if shared_queue.qsize() > 0:
                if self.video_queue.full():
                    # Clear the video queue if it's full to prevent blocking
                    self.video_queue.get_nowait()

                # Retrieve the next frame from the shared queue
                frame = shared_queue.get_nowait()

                # Ensure frame is a valid numpy array
                if isinstance(frame, np.ndarray):

                    if len(frame.shape) == 2:  # If frame is grayscale (single channel)
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                    # Add frame to video queue for further processing
                    self.video_queue.put_nowait(frame)
                else:
                    print("Received an invalid frame")

            # Sleep to prevent excessive CPU usage
            # time.sleep(0.07)

    def video_processing_for_background(self):
        """Process video frames for detections."""
        last_event_no = 0
        while self.running:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=ITDT14;UID=sa;PWD=root1234",
                autocommit=True)
            cursor = connection.cursor()
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)
            select_all_query = (f"""SELECT TOP 1 event_id 
                  FROM [ALPR_DB_NEW].[dbo].[{self.dict_db_details['str_historical_event_table']}]
                  ORDER BY event_id DESC""")
            cursor.execute(select_all_query)
            latest_event = cursor.fetchone()
            if latest_event and latest_event[0] > last_event_no:
                # New events detected, fetch top 5 most recent records
                select_all_query = f"""SELECT TOP 5 *
                                                   FROM [ALPR_DB_NEW].[dbo].[{self.dict_db_details['str_historical_event_table']}]
                  ORDER BY event_id DESC"""
                cursor.execute(select_all_query)
                rows = cursor.fetchall()

                # Update our tracking of the most recent event
                last_event_no = latest_event[0]

                new_detections = []
                for row in rows:
                    decoded_image = base64.b64decode(row.vehicle_img)
                    image = Image.open(io.BytesIO(decoded_image))
                    resized_image = image.resize((int(self.main_width * 0.45*0.55), int(self.main_width * 0.45*0.55)), Image.Resampling.LANCZOS)
                    detection_info = {
                        'frame': resized_image,
                        'plate_number': row.vehicle_number,
                        'country': row.country,
                        'plate_color': row.number_plate_color,
                        'timestamp': time.time(),
                        'v_id':row.vehicle_id,
                        'status':row.status,
                        'captured_time': row.time,
                        'event_no': row.event_id ,
                        'alarm':row.alarm
                    }
                    new_detections.append(detection_info)
                # Clear existing queue
                while not self.detection_queue.empty():
                    try:
                        self.detection_queue.get_nowait()
                    except queue.Empty:
                        break
                # Add new detections to queue
                for detection in new_detections:
                    try:
                        self.detection_queue.put_nowait(detection)
                    except queue.Full:
                        break
            cursor.close()
            connection.close()

    time.sleep(1)  # Check for updates every second


    def update_video_display(self):
        try:
            frame = self.video_queue.get_nowait()

            # Get the container dimensions
            content_width = self.live_feed.winfo_width()
            content_height = self.live_feed.winfo_height()


            if content_width > 1 and content_height > 1:
                # Resize the frame directly to the container dimensions
                resized_frame = cv2.resize(frame, (content_width, content_height), interpolation=cv2.INTER_AREA)
                resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_RGB2BGR)

                # Convert to PhotoImage
                image = Image.fromarray(resized_frame)
                photo = ImageTk.PhotoImage(image=image)

                # Update the video label
                if not hasattr(self, 'video_label'):
                    self.video_label = CTkLabel(self.live_feed, text="")
                    self.video_label.grid(row=0, column=0, sticky="nsew")

                self.video_label.configure(image=photo)
                self.video_label.image = photo

        except queue.Empty:
          pass
        self.root.after(20, self.update_video_display)

    def update_details_display(self):
        try:
            # Collect current detections
            current_detections = []
            while not self.detection_queue.empty():
                try:
                    detection = self.detection_queue.get_nowait()
                    current_detections.append(detection)
                except queue.Empty:
                    break

            current_detections.sort(key=lambda x: x['event_no'], reverse=True)

            for i, detection_info in enumerate(current_detections[:5]):
                if i >= len(self.details_frames):
                    break

                frame = self.details_frames[i]

                border_color = 'green'

                if detection_info['alarm'] == 0:
                    border_color = 'orange'
                elif detection_info['alarm'] == 1:
                    border_color = 'green'
                elif detection_info['alarm'] == 2:
                    border_color = 'red'
                    # self.audio_manager.send_command("play_with_duration:5")


                frame['frame'].configure(border_color=border_color)
                frame['frame'].configure(border_color=border_color)
                for widget in frame['info_frame'].winfo_children():
                    widget.destroy()

                img_frame_width = frame['img_frame'].winfo_width() - 0  # Account for padding
                img_frame_height = frame['img_frame'].winfo_height() - 0

                original_img = detection_info['frame']
                orig_width, orig_height = original_img.size
                aspect_ratio = orig_width / orig_height

                if img_frame_width / img_frame_height > aspect_ratio:
                    new_height = img_frame_height
                    new_width = int(new_height * aspect_ratio)
                else:
                    new_width = img_frame_width
                    new_height = int(new_width / aspect_ratio)

                new_width = max(new_width, 160)
                new_height = max(new_height, 160)

                resized_frame = original_img.resize((new_width+15, new_height), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(resized_frame)
                frame['img_label'].configure(image=tk_image)
                frame['img_label'].image = tk_image

                info_items = [
                    ("Vechile Number ", detection_info['plate_number']),
                    ("Event Id               ", detection_info['v_id']),
                    ("Country               ", detection_info['country']),
                    ("Vechile Colour   ", detection_info['plate_color']),
                    ("Status                  ", detection_info['status']),
                    ("Time                     ", detection_info['captured_time'])
                ]

                for idx, (label, value) in enumerate(info_items):
                    CTkLabel(
                        frame['info_frame'],
                        text=f"{label}: {value}",
                        font=("", 11, "bold"),
                        text_color="black",
                        anchor="w",
                        justify="left"
                    ).grid(row=idx, column=0, sticky="w", padx=0, pady=1)

        except Exception as e:
            print(f"Error updating display: {e}")
        self.root.after(100, self.update_details_display)