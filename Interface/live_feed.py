import base64
from datetime import datetime
import io
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np
import pyodbc
import time

from customtkinter import (
    CTk, CTkFrame, CTkLabel, CTkImage
)
from PIL import Image, ImageTk, ImageDraw
import cv2
import threading
import queue

from Core.Recognistion_process.ConfigLoader import ConfigLoader
from FR_Detection.ptz_controller import PTZController
from shared_queue import  live_feed_queue, current_camera_details, locked_ID


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
        self.current_boxes = []
        self.clicked_id = None
        self.alert_flag = threading.Event()
        self.config=ConfigLoader()
        self.obj_PTZController= PTZController()
        # Video processing properties
        self.video_queue = queue.Queue(maxsize=10)
        self.detection_queue = queue.Queue(maxsize=10)
        self.running = True
        self.restricted_person_caught_signal=False
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
            "str_person_table": "person_details",
            "str_historical_event_table": "event_details"
        }
        # Configure main frame
        self.configure(fg_color="#F1F5FA", corner_radius=0)
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_propagate(False)
        self.make_clickable=False
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



    def start_processing_threads(self):
        """Start the video processing threads"""
        self.video_thread = threading.Thread(target=self.video_processing_new)
        self.video_thread.daemon = True
        self.video_thread.start()

        self.background_thread = threading.Thread(target=self.video_processing_for_background)
        self.background_thread.daemon = True
        self.background_thread.start()





    # def video_processing(self):
    #     """Process video frames for the main display."""
    #     while self.running:
    #         #  print("length of shared queue: ", shared_queue.qsize())
    #         time.sleep(0.1)
    #         if shared_queue.qsize() > 0:
    #             if self.video_queue.full():
    #                 # Clear the video queue if it's full to prevent blocking
    #                 self.video_queue.get_nowait()
    #
    #             # Retrieve the next frame from the shared queue
    #             frame = shared_queue.get_nowait()
    #
    #             # Ensure frame is a valid numpy array
    #             if isinstance(frame, np.ndarray):
    #
    #                 if len(frame.shape) == 2:  # If frame is grayscale (single channel)
    #                     frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    #                 # Add frame to video queue for further processing
    #                 self.video_queue.put_nowait(frame)
    #             else:
    #                 print("Received an invalid frame")

    # def resize_frame_and_detections(self, frame, detections, target_width=1041, target_height=908):
    #     start=time.time()
    #
    #     """Resize frame and scale detections to match new frame size."""
    #     original_height, original_width = frame.shape[:2]
    #
    #     # Calculate scaling factors
    #     scale_x = target_width / original_width
    #     scale_y = target_height / original_height
    #
    #     # Resize the frame
    #     resized_frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)
    #
    #     # Scale the detection boxes
    #     resized_detections = []
    #     for det in detections:
    #         x1, y1, x2, y2 = det["bbox"]
    #         new_x1 = int(x1 * scale_x)
    #         new_y1 = int(y1 * scale_y)
    #         new_x2 = int(x2 * scale_x)
    #         new_y2 = int(y2 * scale_y)
    #
    #         # Copy and update detection box
    #         updated_det = det.copy()
    #         updated_det["bbox"] = (new_x1, new_y1, new_x2, new_y2)
    #         resized_detections.append(updated_det)
    #
    #     end=time.time()
    #     total=start-end
    #     print(f"Total processing time: {total:.6f} seconds")
    #
    #
    #     return resized_detections, resized_frame

    def resize_frame_and_detections(self, frame, detections, target_width=1041, target_height=908):

        t0 = time.time()

        original_height, original_width = frame.shape[:2]
        scale_x = target_width / original_width
        scale_y = target_height / original_height


        frame_gpu = cv2.UMat(frame)
        resized_gpu = cv2.resize(frame_gpu, (target_width, target_height), interpolation=cv2.INTER_LINEAR)


        resized_frame = resized_gpu.get()
        resized_detections = []
        if detections:
            boxes = np.array([det["bbox"] for det in detections])
            boxes[:, [0, 2]] = (boxes[:, [0, 2]] * scale_x).astype(int)
            boxes[:, [1, 3]] = (boxes[:, [1, 3]] * scale_y).astype(int)

            for i, det in enumerate(detections):
                updated_det = det.copy()
                updated_det["bbox"] = tuple(boxes[i])
                resized_detections.append(updated_det)

        t1 = time.time()
        print(f"Total time with GPU (UMat): {t1 - t0:.6f} seconds")

        return resized_detections, resized_frame




    def video_processing_new(self, new_width=1041, new_height=908):
        """Process video frames for the main display with resized frames and adjusted detection boxes."""
        while self.running:
            time.sleep(0.01)
            if not live_feed_queue.empty():
                frame, boxes_data = live_feed_queue.get(timeout=1)
                resize_detections, resized_frame= self.resize_frame_and_detections(frame,boxes_data)
                if not  self.video_queue.full():
                    self.video_queue.put((resized_frame,resize_detections),timeout=1)




    # def video_processing(self):
    #     """Process video frames for the main display."""
    #     # content_width = self.live_feed.winfo_width()
    #     # content_height = self.live_feed.winfo_height()
    #     # print(content_width," WIDTHHH ",content_height)
    #     while self.running:
    #         #  print("length of shared queue: ", shared_queue.qsize())
    #         time.sleep(0.1)
    #         if not live_feed_queue.empty():
    #             frame,boxes_data=live_feed_queue.get(timeout=1)
    #             for track in boxes_data:
    #                 track_id = track["track_id"]
    #                 x1_draw, y1_draw, x2_draw, y2_draw = track["bbox"]
    #
    #                 cv2.rectangle(frame, (x1_draw, y1_draw), (x2_draw, y2_draw), (0, 255, 0), 2)
    #                 cv2.putText(frame, f"ID: {track_id}", (x1_draw, y1_draw - 10),
    #                             cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    #             cv2.imshow("live_feed",frame)
    #
    #             cv2.waitKey(1)
    #
    #         if shared_queue.qsize() > 0:
    #             if self.video_queue.full():
    #                 # Clear the video queue if it's full to prevent blocking
    #                 self.video_queue.get_nowait()
    #
    #             # Retrieve the next frame from the shared queue
    #             frame = shared_queue.get_nowait()
    #
    #             # Ensure frame is a valid numpy array
    #             if isinstance(frame, np.ndarray):
    #
    #                 if len(frame.shape) == 2:  # If frame is grayscale (single channel)
    #                     frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    #                 # Add frame to video queue for further processing
    #                 self.video_queue.put_nowait(frame)
    #             else:
    #                 print("Received an invalid frame")

    def video_processing_for_background(self):
        """Process video frames for detections."""
        last_event_no = 0
        while self.running:
            # Connect to the database
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=ITDT14;UID=sa;PWD=root1234;DATABASE=FR_DB_NEW",
                autocommit=True)
            cursor = connection.cursor()

            # Get the latest event_id
            select_latest_query = """
                SELECT TOP 1 event_id 
                FROM [FR_DB_NEW].[dbo].[event_details]
                ORDER BY event_id DESC
            """
            cursor.execute(select_latest_query)
            latest_event = cursor.fetchone()

            # if latest_event and latest_event[0] > last_event_no:
            if True:
                # New events detected, fetch top 5 most recent records
                select_all_query = """
                    SELECT TOP 5 
                        [event_id],
                        [person_name],
                        [captured_img],
                        [start_time],
                        [end_time],
                        [acknowledgment_time],
                        [acknowledgment_message]
                    FROM [FR_DB_NEW].[dbo].[event_details]
                    ORDER BY event_id DESC
                """
                cursor.execute(select_all_query)
                rows = cursor.fetchall()

                # Update the tracking of the most recent event
                if latest_event:
                    last_event_no = latest_event[0]


                new_detections = []
                for row in rows:
                    # Decode the captured_img (assuming it's base64 encoded like person_img in your original code)
                    decoded_image = base64.b64decode(row.captured_img)
                    image = Image.open(io.BytesIO(decoded_image))
                    resized_image = image.resize(
                        (int(self.main_width * 0.45 * 0.55), int(self.main_width * 0.45 * 0.55)),
                        Image.Resampling.LANCZOS)

                    # Create detection info dictionary with the new fields
                    detection_info = {
                        'frame': resized_image,
                        'event_id': row.event_id,
                        'person_name': row.person_name,
                        'start_time': row.start_time,
                        'end_time': row.end_time,
                        'acknowledgment_time': row.acknowledgment_time,
                        'acknowledgment_message': row.acknowledgment_message,
                        'timestamp': time.time()
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
            time.sleep(1)

    #
    # def update_video_display(self):
    #
    #     content_widthi = self.live_feed.winfo_rootx()
    #     content_heighti = self.live_feed.winfo_rooty()
    #     print(content_widthi, " position -------------------------------------------------------------", content_heighti)
    #     try:
    #         frame = self.video_queue.get_nowait()
    #
    #
    #         content_width = self.live_feed.winfo_width()
    #         content_height = self.live_feed.winfo_height()
    #         print(content_width, " Width -------------------------------------------------------------", content_height)
    #
    #         if content_width > 1 and content_height > 1:
    #             # Resize the frame directly to the container dimensions
    #             resized_frame = cv2.resize(frame, (content_width, content_height), interpolation=cv2.INTER_AREA)
    #             resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_RGB2BGR)
    #
    #             # Convert to PhotoImage
    #             image = Image.fromarray(resized_frame)
    #             photo = ImageTk.PhotoImage(image=image)
    #
    #
    #             if not hasattr(self, 'video_label'):
    #                 self.video_label = CTkLabel(self.live_feed, text="")
    #                 self.video_label.grid(row=0, column=0, sticky="nsew")
    #
    #             self.video_label.configure(image=photo)
    #             self.video_label.image = photo
    #
    #     except queue.Empty:
    #       pass
    #     self.root.after(20, self.update_video_display)



    # def update_video_display(self):
    #     # content_widthi = self.live_feed.winfo_rootx()
    #     # content_heighti = self.live_feed.winfo_rooty()
    #     # print(content_widthi, " position -------------------------------------------------------------",
    #     #       content_heighti)
    #
    #     try:
    #         # Retrieve frame and detection boxes
    #         frame, boxes_data = self.video_queue.get_nowait()
    #
    #         content_width = self.live_feed.winfo_width()
    #         content_height = self.live_feed.winfo_height()
    #         # print(content_width, " Width -------------------------------------------------------------", content_height)
    #
    #         if content_width > 1 and content_height > 1:
    #             # Resize frame
    #             resized_frame = cv2.resize(frame, (content_width, content_height), interpolation=cv2.INTER_AREA)
    #             resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    #
    #             # Convert to PIL for drawing transparent overlays
    #             image = Image.fromarray(resized_frame).convert("RGBA")
    #             overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    #             draw = ImageDraw.Draw(overlay)
    #             self.current_boxes = []
    #             for box in boxes_data:
    #                 track_id = box['track_id']
    #                 x1, y1, x2, y2 = box['bbox']
    #
    #                 # Scale coordinates based on new frame size
    #                 original_h, original_w = frame.shape[:2]
    #                 x_scale = content_width / original_w
    #                 y_scale = content_height / original_h
    #
    #                 x1 = int(x1 * x_scale)
    #                 y1 = int(y1 * y_scale)
    #                 x2 = int(x2 * x_scale)
    #                 y2 = int(y2 * y_scale)
    #
    #                 # Store scaled box for click detection
    #                 self.current_boxes.append({
    #                     "track_id": track_id,
    #                     "coords": (x1, y1, x2, y2)
    #                 })
    #
    #                 if self.clicked_id == track_id:
    #                     # Draw semi-transparent red box
    #                     draw.rectangle([(x1, y1), (x2, y2)], outline=(255, 0, 0, 255), width=5)
    #                     draw.rectangle([(x1, y1 - 25), (x1 + 50, y1)], fill=(255, 0, 0, 160))  # Red label background
    #                     draw.text((x1 + 5, y1 - 23), f"Locked", fill=(255, 255, 255, 255))  # White text
    #                 else:
    #                     # Draw semi-transparent box
    #                     draw.rectangle([(x1, y1), (x2, y2)], outline=(0, 255, 0, 255), width=3)
    #                     draw.rectangle([(x1, y1 - 25), (x1 , y1)], fill=(0, 0, 0, 160))  # Label background
    #                     font = ImageFont.truetype("arial.ttf", 20)
    #                     draw.text((x1 + 5, y1 - 23), f"ID: {track_id}", fill=(255, 0, 0, 255),font=font)
    #
    #             # Composite image and overlay
    #             combined = Image.alpha_composite(image, overlay).convert("RGB")
    #             photo = ImageTk.PhotoImage(image=combined)
    #
    #             # Display on CTkLabel
    #             if not hasattr(self, 'video_label'):
    #                 self.video_label = CTkLabel(self.live_feed, text="")
    #                 self.video_label.grid(row=0, column=0, sticky="nsew")
    #
    #             self.video_label.configure(image=photo)
    #             self.video_label.image = photo
    #
    #             if hasattr(self, 'on_form_ready') and self.make_clickable == False :
    #                 self.on_form_ready()
    #                 self.make_clickable=True
    #
    #     except queue.Empty:
    #         pass
    #
    #     self.root.after(2, self.update_video_display)

    def update_video_display(self):
        try:
            # Try to get a frame from the queue
            frame, boxes_data = self.video_queue.get_nowait()
        except queue.Empty:
            self.root.after(30, self.update_video_display)  # Wait for next frame
            return

        content_width = self.live_feed.winfo_width()
        content_height = self.live_feed.winfo_height()

        # Validate target size
        if content_width <= 1 or content_height <= 1:
            self.root.after(30, self.update_video_display)
            return

        # Resize and convert color
        resized_frame = cv2.resize(frame, (content_width, content_height), interpolation=cv2.INTER_AREA)
        resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        # Convert to PIL
        image = Image.fromarray(resized_frame).convert("RGBA")
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        self.current_boxes = []

        # Precompute scale
        original_h, original_w = frame.shape[:2]
        x_scale = content_width / original_w
        y_scale = content_height / original_h

        # Cache font only once
        if not hasattr(self, 'font_cache'):
            try:
                self.font_cache = ImageFont.truetype("arial.ttf", 20)
            except:
                self.font_cache = ImageFont.load_default()

        for box in boxes_data:
            track_id = box['track_id']
            x1, y1, x2, y2 = box['bbox']
            x1 = int(x1 * x_scale)
            y1 = int(y1 * y_scale)
            x2 = int(x2 * x_scale)
            y2 = int(y2 * y_scale)

            self.current_boxes.append({
                "track_id": track_id,
                "coords": (x1, y1, x2, y2)
            })
            # val= str(current_camera_details.get("ptz_feature", "False"))
            if self.clicked_id == track_id and self.obj_PTZController.ptz_eligibility:
                draw.rectangle([(x1, y1), (x2, y2)], outline=(255, 0, 0, 255), width=5)
                draw.rectangle([(x1, y1 - 25), (x1 + 50, y1)], fill=(255, 0, 0, 160))  # Red label background
                draw.text((x1 + 5, y1 - 23), f"Locked", fill=(255, 255, 255, 255))  # White text
            elif  self.clicked_id == track_id and not self.obj_PTZController.ptz_eligibility:
                print("No PTZ camera")
                # draw.rectangle([(x1, y1), (x2, y2)], outline=(0, 0, 255, 255), width=5)
                # draw.rectangle([(x1, y1 - 25), (x1 + 50, y1)], fill=(255, 0, 0, 160))  # Red label background
                # draw.text((x1 + 5, y1 - 23), f"PTZ not found", fill=(255, 255, 255, 255))  # White text
                # # self.clicked_id=None
            else:
                # Draw semi-transparent box
                draw.rectangle([(x1, y1), (x2, y2)], outline=(0, 255, 0, 255), width=3)
                draw.rectangle([(x1, y1 - 25), (x1 , y1)], fill=(0, 0, 0, 160))  # Label background
                font = ImageFont.truetype("arial.ttf", 20)
                draw.text((x1 + 5, y1 - 23), f"ID: {track_id}", fill=(255, 0, 0, 255),font=font)


        # Combine and show
        combined = Image.alpha_composite(image, overlay).convert("RGB")
        photo = ImageTk.PhotoImage(image=combined)

        if not hasattr(self, 'video_label'):
            self.video_label = CTkLabel(self.live_feed, text="")
            self.video_label.grid(row=0, column=0, sticky="nsew")

        self.video_label.configure(image=photo)
        self.video_label.image = photo

        # Callback once when UI is ready
        if hasattr(self, 'on_form_ready') and not self.make_clickable:
            # if True in settings:
                self.on_form_ready()

                self.make_clickable = True

        self.root.after(2, self.update_video_display)  # Target ~33 FPS

    def on_box_click(self, event):
        # if True in settings:
        #     print("PTZ is enabled.")

        x, y = event.x, event.y
        for box in self.current_boxes:
            x1, y1, x2, y2 = box['coords']
            if x1 <= x <= x2 and y1 <= y <= y2:
                print(f"Clicked on box ID: {box['track_id']}")
                if self.clicked_id != box['track_id']:
                     self.clicked_id= box['track_id']
                else:
                    self.clicked_id=None
                locked_ID["locked_id"]=self.clicked_id
                break

    def format_timestamp(self, timestamp_value):
        if not timestamp_value:
            return "N/A"
        try:
            timestamp = float(timestamp_value)
            if timestamp > 0:
                return datetime.fromtimestamp(timestamp).strftime('%b %d, %Y • %H:%M:%S')
            return "N/A"
        except (ValueError, TypeError):
            return str(timestamp_value)

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

            # Sort by event_id in descending order
            current_detections.sort(key=lambda x: x['event_id'], reverse=True)

            for i, detection_info in enumerate(current_detections[:5]):
                if i >= len(self.details_frames):
                    break

                frame = self.details_frames[i]

                # Set a default border color (customize as needed)
                border_color = 'green'
                frame['frame'].configure(border_color=border_color)

                # Clear previous info
                for widget in frame['info_frame'].winfo_children():
                    widget.destroy()

                # Update image
                img_frame_width = frame['img_frame'].winfo_width() - 0
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

                resized_frame = original_img.resize((new_width + 15, new_height), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(resized_frame)
                frame['img_label'].configure(image=tk_image)
                frame['img_label'].image = tk_image



                # Display the new fields
                info_items = [
                    ("Event ID            ", detection_info['event_id']),
                    ("Person Name   ", detection_info['person_name']),
                    ("Start Time        ", self.format_timestamp(detection_info['start_time'])),
                    ("End Time          ", self.format_timestamp(detection_info['end_time'])),

                ]

                for idx, (label, value) in enumerate(info_items):
                    CTkLabel(
                        frame['info_frame'],
                        text=f"{label}:",  # Removed extra space after colon
                        font=("", 16, "bold"),
                        text_color="black",
                        anchor="w",
                        justify="left",
                        width=120  # Added fixed width for consistent alignment
                    ).grid(row=idx, column=0, sticky="w", padx=(0, 5), pady=2)  # Added padding between columns

                    # Ensure value is a string before checking length
                    value_str = str(value)

                    if len(value_str) > 0 and len(value_str) <= 15:
                        font_size = 18
                    elif len(value_str) > 15 and len(value_str) < 25:
                        font_size = 14
                    else:
                        font_size = 9

                    CTkLabel(
                        frame['info_frame'],
                        text=value_str,  # Use the converted string
                        font=("", font_size),
                        text_color="black",
                        anchor="w",
                        justify="left",
                        width=200  # Added width for value field
                    ).grid(row=idx, column=1, sticky="w", padx=0, pady=2)  # Consistent padding

        except Exception as e:
            print(f"Error updating display: {e}")
        self.root.after(100, self.update_details_display)