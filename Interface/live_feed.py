import base64
import io
from tkinter import messagebox
import numpy as np
import pyodbc
from customtkinter import (
    CTk, CTkFrame, CTkLabel, CTkImage
)
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import cv2
import threading
import queue
import time
from datetime import datetime
from Core.audio import AudioController
from Core.Recognistion_process.ConfigLoader import ConfigLoader
from shared_queue import shared_queue


class LiveEventInterface(CTkFrame):
    def __init__(self, root, root_width: int = 1920, root_height: int = 1080):
        super().__init__(root)
        self.start_time = datetime.now()

        # Initialize basic properties
        self.root = root
        self.root_width = root_width
        self.root_height = root_height
        self.main_width = int(root_width * 0.95)
        self.main_height = int(root_height * 0.95)
        self.alert_flag = threading.Event()
        self.config = ConfigLoader()
        self.restricted_vehicle_caught_signal = False

        # Video processing properties
        self.running = True
        self.frame_count = 0
        self.details_frames = []
        self.audio_manager = AudioController()
        self.target_fps = 30  # Target frame rate for display
        self.frame_interval = 1.0 / self.target_fps
        self.display_queue = queue.Queue(maxsize=10)  # Queue for processed frames
        self.detection_queue = queue.Queue(maxsize=10)  # Queue for detection updates

        # Database connection
        self.dict_db_details = {
            "str_server": "ITDT23",
            "str_username": "sa",
            "str_password": "root1234",
            "str_db_name": "ZONE_INTRUSION_DB",
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

        # Create UI elements
        self.create_layout()

        # Initialize database connection
        self.db_connection = None
        self.db_cursor = None
        self.db_lock = threading.Lock()  # Lock for thread-safe database access
        self.connect_to_database()

        # Start processing threads
        self.start_processing_threads()

        # Schedule updates
        self.root.after(int(self.frame_interval * 1000), self.update_video_display)
        self.root.after(500, self.update_details_display)

    def enhance_image(self, image):
        """
        Apply slight image enhancement to improve visual quality
        """
        try:
            # Convert PIL image to numpy array for OpenCV processing
            img_array = np.array(image)

            # Apply slight sharpening using unsharp mask
            gaussian = cv2.GaussianBlur(img_array, (0, 0), 2.0)
            sharpened = cv2.addWeighted(img_array, 1.5, gaussian, -0.5, 0)

            # Convert back to PIL Image
            enhanced_image = Image.fromarray(sharpened)

            # Apply PIL enhancements
            # Slight brightness enhancement
            brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
            enhanced_image = brightness_enhancer.enhance(1.1)  # 10% brighter

            # Slight contrast enhancement
            contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = contrast_enhancer.enhance(1.15)  # 15% more contrast

            # Slight color saturation enhancement
            color_enhancer = ImageEnhance.Color(enhanced_image)
            enhanced_image = color_enhancer.enhance(1.1)  # 10% more saturated

            # Apply a very mild sharpening filter
            enhanced_image = enhanced_image.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))

            return enhanced_image

        except Exception as e:
            print(f"Image enhancement error: {e}")
            # Return original image if enhancement fails
            return image

    def connect_to_database(self):
        """Establish a persistent database connection"""
        try:
            self.db_connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.config.get('database.server')};"
                f"UID={self.config.get('database.user')};PWD={self.config.get('database.password')};"
                f"DATABASE={self.dict_db_details['str_db_name']}",
                autocommit=True
            )
            self.db_cursor = self.db_connection.cursor()
        except Exception as e:
            print(f"Database connection error: {e}")

    def create_layout(self):
        # Main Content Frame
        self.main_content = CTkFrame(self, fg_color="#F1F5FA")
        self.main_content.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        self.main_content.grid_columnconfigure(1, weight=1)

        # Create a frame for counters
        counter_frame = CTkFrame(self.main_content, fg_color="#F1F5FA")
        counter_frame.grid(row=0, column=0, padx=(0, 15), sticky="ns")

        # Entry Count Frame and Labels
        entry_frame = CTkFrame(counter_frame, fg_color="#E8F5E9")
        entry_frame.grid(row=0, column=0, padx=(0, 10))

        entry_label = CTkLabel(
            entry_frame,
            text="Entry",
            font=("", 16),
            text_color="#2E7D32"
        )
        entry_label.grid(row=0, column=0, padx=10, pady=5)

        self.entry_count = CTkLabel(
            entry_frame,
            text="0",
            font=("", 18, "bold"),
            text_color="#2E7D32",
            width=50,
            height=30,
            fg_color="#C8E6C9",
            corner_radius=6
        )
        self.entry_count.grid(row=0, column=1, padx=10, pady=5)

        # Exit Count Frame and Labels
        exit_frame = CTkFrame(counter_frame, fg_color="#FBE9E7")
        exit_frame.grid(row=0, column=1)

        exit_label = CTkLabel(
            exit_frame,
            text="Exit",
            font=("", 16),
            text_color="#C62828"
        )
        exit_label.grid(row=0, column=0, padx=10, pady=5)

        self.exit_count = CTkLabel(
            exit_frame,
            text="0",
            font=("", 18, "bold"),
            text_color="#C62828",
            width=50,
            height=30,
            fg_color="#FFCDD2",
            corner_radius=6
        )
        self.exit_count.grid(row=0, column=1, padx=10, pady=5)

        # Title Label
        title = CTkLabel(
            self.main_content,
            text="Live Event",
            font=("", 23, "bold"),
            text_color="#000000",
        )
        title.grid(row=0, column=1, pady=(0, 10), padx=(300, 0), sticky="w")

        # Content Holder Frame
        self.content = CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=6)
        self.content.grid_columnconfigure(1, weight=4)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_propagate(False)

        # Live Feed Frame
        self.create_video_frame()

        # Detection Sidebar
        self.create_detection_sidebar()

    def create_video_frame(self):
        self.live_feed_width = int(self.main_width * 0.65)
        self.live_feed_height = self.main_height

        video_container = CTkFrame(
            self.content,
            fg_color="white",
            corner_radius=0,
            border_width=4,
            border_color="white",
            width=self.live_feed_width,
            height=self.live_feed_height
        )
        video_container.grid(row=0, column=0, padx=(0, 0), sticky="nsew")
        video_container.grid_columnconfigure(0, weight=2)
        video_container.grid_rowconfigure(0, weight=1)
        video_container.grid_propagate(False)

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

        for i in range(5):
            self.sidebar.grid_rowconfigure(i, weight=1)
            self.create_detection_entry(self.sidebar, i)

    def create_detection_entry(self, parent, row_index):
        boundary_colors = "green"
        frame_height = int(self.live_feed_height / 5) - 10
        img_frame_width = int(self.main_width * 0.3 * 0.43)  # Consistent with target_size
        img_frame_height = frame_height - 10

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

        main_frame.grid_columnconfigure(0, weight=35)
        main_frame.grid_columnconfigure(1, weight=65)
        main_frame.grid_rowconfigure(0, weight=1)

        img_frame = CTkFrame(
            main_frame,
            fg_color="#f0f0f0",
            corner_radius=0,
            height=img_frame_height,
            width=img_frame_width
        )
        img_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        img_frame.grid_propagate(False)

        img_label = CTkLabel(
            img_frame,
            text="",
            fg_color="white"
        )
        img_label.grid(row=0, column=0, sticky="nsew")
        img_frame.grid_columnconfigure(0, weight=1)
        img_frame.grid_rowconfigure(0, weight=1)

        info_frame = CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=0,
            height=frame_height - 10,
            width=int((self.main_width * 0.3) * 0.57)
        )
        info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        info_frame.grid_propagate(False)

        for i in range(6):
            info_frame.grid_rowconfigure(i, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)

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

    def start_processing_threads(self):
        """Start the video processing threads"""
        self.video_thread = threading.Thread(target=self.video_processing)
        self.video_thread.daemon = True
        self.video_thread.start()

        self.background_thread = threading.Thread(target=self.video_processing_for_background)
        self.background_thread.daemon = True
        self.background_thread.start()

    def video_processing(self):
        """Process video frames for the main display"""
        last_frame_time = time.time()
        while self.running:
            try:
                frame = shared_queue.get_nowait()
                if isinstance(frame, np.ndarray):
                    if len(frame.shape) == 2:  # If frame is grayscale
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                    # Resize frame in background thread
                    content_width = max(self.live_feed.winfo_width(), 1)
                    content_height = max(self.live_feed.winfo_height(), 1)
                    frame = cv2.resize(frame, (content_width, content_height), interpolation=cv2.INTER_AREA)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    # Convert to PIL Image for display
                    image = Image.fromarray(frame)
                    photo = ImageTk.PhotoImage(image=image)
                    try:
                        self.display_queue.put_nowait((photo, self.frame_count))
                    except queue.Full:
                        try:
                            self.display_queue.get_nowait()
                            self.display_queue.put_nowait((photo, self.frame_count))
                        except queue.Empty:
                            pass
                    self.frame_count += 1
                # Control frame rate
                elapsed = time.time() - last_frame_time
                sleep_time = max(0, self.frame_interval - elapsed)
                time.sleep(sleep_time)
                last_frame_time = time.time()
            except queue.Empty:
                time.sleep(self.frame_interval / 2)
            except Exception as e:
                print(f"Video processing error: {e}")

    def video_processing_for_background(self):
        """Process video frames for detections"""
        last_event_no = 0
        while self.running:
            try:
                with self.db_lock:
                    if self.db_cursor and self.db_connection:
                        select_all_query = f"""SELECT TOP 1 event_id 
                                            FROM [ZONE_INTRUSION_DB].[dbo].[{self.dict_db_details['str_historical_event_table']}]
                                            ORDER BY event_id DESC"""
                        try:
                            self.db_cursor.execute(select_all_query)
                            latest_event = self.db_cursor.fetchone()
                        except pyodbc.Error as e:
                            print(f"Database query error: {e}")
                            self.connect_to_database()
                            continue

                        if latest_event and latest_event[0] > last_event_no:
                            select_all_query = f"""SELECT TOP 5 *
                                                FROM [ZONE_INTRUSION_DB].[dbo].[{self.dict_db_details['str_historical_event_table']}]
                                                ORDER BY event_id DESC"""
                            self.db_cursor.execute(select_all_query)
                            rows = self.db_cursor.fetchall()
                            last_event_no = latest_event[0]

                            new_detections = []
                            for row in rows:
                                decoded_image = base64.b64decode(row.vehicle_img)
                                image = Image.open(io.BytesIO(decoded_image))

                                # Resize image to fit img_frame, preserving aspect ratio
                                img_frame_width = int(self.main_width * 0.3 * 0.43)
                                img_frame_height = int(self.live_feed_height / 5) - 20
                                orig_width, orig_height = image.size
                                aspect_ratio = orig_width / orig_height
                                target_aspect = img_frame_width / img_frame_height

                                if aspect_ratio > target_aspect:
                                    new_height = img_frame_height
                                    new_width = int(new_height * aspect_ratio)
                                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                    left = (new_width - img_frame_width) // 2
                                    image = image.crop((left, 0, left + img_frame_width, new_height))
                                else:
                                    new_width = img_frame_width
                                    new_height = int(new_width / aspect_ratio)
                                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                    top = (new_height - img_frame_height) // 2
                                    image = image.crop((0, top, new_width, top + img_frame_height))

                                # Apply image enhancement
                                enhanced_image = image
                                detection_info = {
                                    'frame': enhanced_image,
                                    'plate_number': row.vehicle_number,
                                    'camera': row.camera_name,
                                    'plate_color': row.number_plate_color,
                                    'object_type': row.object_type,  # Add this line
                                    'timestamp': time.time(),
                                    'v_id': row.vehicle_id,
                                    'status': row.status,
                                    'captured_time': row.time,
                                    'event_no': row.event_id,
                                    'alarm': row.alarm

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
            except Exception as e:
                print(f"Background processing error: {e}")
            time.sleep(1.0)  # Check database every 2 seconds

    def update_video_display(self):
        """Update the video display with the latest frame"""
        try:
            photo, frame_count = self.display_queue.get_nowait()
            if not hasattr(self, 'video_label'):
                self.video_label = CTkLabel(self.live_feed, text="")
                self.video_label.grid(row=0, column=0, sticky="nsew")
            self.video_label.configure(image=photo)
            self.video_label.image = photo
            self.display_queue.task_done()
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Video display error: {e}")
        if self.running:
            self.root.after(int(self.frame_interval * 1000), self.update_video_display)

    def update_details_display(self):
        """Update the detection sidebar with the latest detections"""
        try:
            current_detections = []
            while not self.detection_queue.empty():
                try:
                    detection = self.detection_queue.get_nowait()
                    current_detections.append(detection)
                    self.detection_queue.task_done()
                except queue.Empty:
                    break

            current_detections.sort(key=lambda x: x['event_no'], reverse=True)
            if current_detections:
                if current_detections[0]['alarm'] == 2:
                    self.restricted_vehicle_caught_signal = True
                if current_detections[0]['status'] == 'Entry':
                    entry_counter = int(self.entry_count.cget('text'))
                    self.entry_count.configure(text=entry_counter + 1)
                else:
                    exit_counter = int(self.exit_count.cget('text'))
                    self.exit_count.configure(text=exit_counter + 1)

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
                    if (current_detections[0]['captured_time'] >= self.start_time and
                            current_detections[0]['alarm'] == 2 and
                            not self.audio_manager.is_muted and
                            current_detections[0]['v_id'] == detection_info['v_id']):
                        self.audio_manager.play()
                        confirmation = messagebox.askyesno(
                            "Attention Required",
                            "You want to stop the alarm now!",
                            icon='warning'
                        )
                        if confirmation:
                            self.audio_manager.stop()

                frame['frame'].configure(border_color=border_color)
                for widget in frame['info_frame'].winfo_children():
                    widget.destroy()

                tk_image = ImageTk.PhotoImage(detection_info['frame'])

                frame['img_label'].configure(image=tk_image)
                frame['img_label'].image = tk_image

                info_items = [
                    ("Event Id       ", detection_info['v_id']),
                    ("Camera Name    ", detection_info['camera']),
                    ("Object Type    ", detection_info['object_type']),  # Changed from Vehicle Colour
                    ("Status         ", detection_info['status']),
                    ("Time           ", detection_info['captured_time'])
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
        if self.running:
            self.root.after(500, self.update_details_display)

    def destroy(self):
        """Clean up resources on destroy"""
        self.running = False
        # Clear queues
        while not self.display_queue.empty():
            try:
                self.display_queue.get_nowait()
            except queue.Empty:
                break
        while not self.detection_queue.empty():
            try:
                self.detection_queue.get_nowait()
            except queue.Empty:
                break
        # Close database connection safely
        with self.db_lock:
            if self.db_cursor and not self.db_cursor.close:
                try:
                    self.db_cursor.close()
                except pyodbc.Error as e:
                    print(f"Error closing cursor: {e}")
            if self.db_connection:
                try:
                    self.db_connection.close()
                except pyodbc.Error as e:
                    print(f"Error closing connection: {e}")
        super().destroy()