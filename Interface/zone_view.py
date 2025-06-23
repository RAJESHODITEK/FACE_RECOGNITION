import subprocess
import tkinter as tk
from customtkinter import CTkFrame, CTkLabel, CTkOptionMenu
import cv2
from PIL import Image, ImageTk
import threading
import time
import logging
import os
import numpy as np
from datetime import datetime
from Config.configloader import ConfigLoader

class ZoneViewInterface(CTkFrame):
    def __init__(self, root, root_width: int = 1920, root_height: int = 1080):
        super().__init__(root)
        self.config = ConfigLoader()

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("ZoneViewInterface")

        # Set dimensions
        self.main_width = int(root_width * 0.95)
        self.main_height = int(root_height * 0.95)
        self.min_width = 800

        # Initialize instance variables
        self._roi_state = {}
        self.camera_list = {}
        self.current_camera = None
        self.rtsp_url = None
        self.obj_Core = None
        self._initialized = False
        self.pending_roi_restore = False
        self.stream_thread = None
        self.stop_stream = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2
        self.running = True
        self.roi_selected = False
        self.roi_coords = None
        self.frame = None
        self.drawing = False
        self._last_frame = None
        self._frames_since_last_good = 0

        self.ROI_STYLE = {
            'outline_color': "#DAA520",
            'outline_width': 3,
            'fill_line_color': "black",
            'fill_line_spacing': 2
        }

        # Configure main frame
        self.configure(fg_color="#F1F5FA", corner_radius=0)
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_propagate(False)

        # Create UI elements
        self.create_layout()

        # Initialize variables for ROI drawing
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.temp_rect_id = None
        self.can_draw = True
        self.roi_color = "#DAA520"

        # Bind mouse events
        # self.canvas.bind("<ButtonPress-1>", self.start_draw)
        # self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        # self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        # Initialize frame and ROI
        self.initialize_frame_and_roi()

    def create_layout(self):
        # Main Content Frame
        self.main_content = CTkFrame(self, fg_color="#F1F5FA")
        self.main_content.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        self.main_content.grid_columnconfigure(1, weight=1)

        # Camera Dropdown
        self.dropdown_values = []
        self.camera_dropdown = CTkOptionMenu(
            self.main_content,
            values=[],
            command=self.on_camera_select,
            fg_color="#FFFFFF",
            text_color="#000000",
            button_color="#5A616B",
            button_hover_color="#313A46",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#F1F5FA",
            dropdown_text_color="#000000",
            width=160,
            height=30,
            corner_radius=2
        )
        self.camera_dropdown.grid(row=0, column=0, padx=(0, 15), pady=5, sticky="w")

        # Title Label
        title = CTkLabel(
            self.main_content,
            text="Zone View",
            font=("", 23, "bold"),
            text_color="#000000"
        )
        title.grid(row=0, column=1, pady=(0, 10), padx=(300, 0), sticky="w")

        # Content Holder Frame
        self.content = CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=6)
        self.content.grid_columnconfigure(1, weight=4)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_propagate(False)

        # Live Feed Frame (Left Side - 65%)
        self.create_video_frame()

        # Sidebar for Dummy Images (Right Side - 35%)
        self.create_control_sidebar()

    def create_video_frame(self):
        # Define dimensions for live feed
        self.live_feed_width = int(self.main_width * 0.65)
        self.live_feed_height = self.main_height

        # Container for video feed
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

        # Inner frame for canvas
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

        # Canvas
        self.canvas = tk.Canvas(
            self.live_feed,
            bg="#FFFFFF",
            highlightthickness=1,
            highlightbackground="#DEDEDE"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

    def create_control_sidebar(self):
        # Sidebar with Scrollable Frame
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
        self.sidebar.grid_rowconfigure(0, weight=1)
        self.sidebar.grid_propagate(False)

        # Scrollable frame for dummy entries
        self.scrollable_frame = CTkFrame(self.sidebar, fg_color="white")
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_rowconfigure(0, weight=1)

        # Canvas for scrolling
        self.scroll_canvas = tk.Canvas(
            self.scrollable_frame,
            bg="white",
            highlightthickness=0
        )
        self.scroll_canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        self.scrollbar = tk.Scrollbar(
            self.scrollable_frame,
            orient="vertical",
            command=self.scroll_canvas.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Inner frame for content
        self.scroll_content = CTkFrame(self.scroll_canvas, fg_color="white")
        self.scroll_content_id = self.scroll_canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.scroll_content.grid_columnconfigure(0, weight=1)

        # Configure scrollable region and bindings
        self.scroll_content.bind("<Configure>", self._update_scroll_region)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Enable mouse wheel scrolling
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Create dummy image entries
        self.dummy_frames = []
        for i in range(5):
            self.create_dummy_entry(self.scroll_content, i)

    def _update_scroll_region(self, event=None):
        """Update the scroll region based on the content size"""
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        # Update canvas window width to match scrollable frame
        canvas_width = self.scroll_canvas.winfo_width()
        if canvas_width > 0:
            self.scroll_canvas.itemconfig(self.scroll_content_id, width=canvas_width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if self.scroll_canvas.winfo_exists():
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_dummy_entry(self, parent, row_index):
        # Main container frame
        frame_height = int(self.live_feed_height / 5.5)  # Increased height
        main_frame = CTkFrame(
            parent,
            fg_color="white",
            corner_radius=5,
            border_width=4,
            border_color="red",
            height=frame_height,
            width=int(self.main_width * 0.3)
        )
        main_frame.grid(row=row_index, column=0, pady=5, padx=5, sticky="nsew")
        main_frame.grid_propagate(False)

        # Configure two columns
        main_frame.grid_columnconfigure(0, weight=35)
        main_frame.grid_columnconfigure(1, weight=65)
        main_frame.grid_rowconfigure(0, weight=1)

        # Image section frame
        img_frame = CTkFrame(
            main_frame,
            fg_color="#f0f0f0",
            corner_radius=0,
            height=frame_height - 10,
            width=int((self.main_width * 0.3) * 0.43)
        )
        img_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        img_frame.grid_propagate(False)
        img_frame.grid_columnconfigure(0, weight=1)
        img_frame.grid_rowconfigure(0, weight=1)

        # Image label
        img_label = CTkLabel(
            img_frame,
            text=""
        )
        img_label.grid(row=0, column=0, sticky="nsew")

        # Load and display dummy image
        try:
            dummy_image = Image.open("C:\\Users\\ITLP 93\\Downloads\\OIP (38).jpg")  # Replace with actual path
            img_frame_width = img_frame.winfo_width() - 10
            img_frame_height = img_frame.winfo_height() - 10
            if img_frame_width <= 1 or img_frame_height <= 1:
                img_frame_width = int((self.main_width * 0.3) * 0.43)
                img_frame_height = frame_height - 10
            orig_width, orig_height = dummy_image.size
            aspect_ratio = orig_width / orig_height
            if img_frame_width / img_frame_height > aspect_ratio:
                new_height = img_frame_height
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = img_frame_width
                new_height = int(new_width / aspect_ratio)
            new_width = max(new_width, 160)
            new_height = max(new_height, 160)
            resized_image = dummy_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            tk_image = ImageTk.PhotoImage(resized_image)
            img_label.configure(image=tk_image)
            img_label.image = tk_image
        except Exception as e:
            self.logger.error(f"Error loading dummy image: {e}")
            img_label.configure(text="No Image")

        # Info section frame
        info_frame = CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=0,
            height=frame_height - 10,
            width=int((self.main_width * 0.3) * 0.82)
        )
        info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        info_frame.grid_propagate(False)
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(0, weight=1)

        # Date-time label
        current_time = datetime.now().strftime("%d-%b-%Y %I:%M %p")
        CTkLabel(
            info_frame,
            text=f"Time: {current_time}",
            font=("", 11, "bold"),
            text_color="black",
            anchor="w",
            justify="left"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Store frame references
        self.dummy_frames.append({
            'frame': main_frame,
            'img_label': img_label,
            'img_frame': img_frame,
            'info_frame': info_frame
        })

    def on_camera_select(self, selected_value):
        """Handle selection from dropdown menu"""
        if selected_value and selected_value in self.camera_list:
            self.stop_stream = True
            if self.stream_thread and self.stream_thread.is_alive():
                self.stream_thread.join(timeout=1.0)
            self.change_camera(selected_value)

    def update_camera_list(self, new_camera_list):
        """Update the camera list and dropdown"""
        try:
            self.camera_list = new_camera_list
            self.logger.info(f"Updating camera list with: {list(new_camera_list.keys())}")
            self.dropdown_values = list(self.camera_list.keys())
            self.camera_dropdown.configure(values=self.dropdown_values)
            if not self.current_camera and self.camera_list:
                first_camera = list(self.camera_list.keys())[0]
                self.camera_dropdown.set(first_camera)
                self.initialize_frame_and_roi()
                self.change_camera(first_camera)
            if not self.dropdown_values:
                self.camera_dropdown.configure(values=["No cameras"])
        except Exception as e:
            self.logger.error(f"Error updating camera list: {e}", exc_info=True)

    def initialize_frame_and_roi(self):
        """Initialize the frame and restore ROI if available"""
        self.canvas.delete("all")
        if self.current_camera:
            try:
                roi_data = self.obj_Core.obj_Camera.get_roi_coordinates(self.current_camera)
                if roi_data and not roi_data.get("str_error_msg"):
                    coordinates = roi_data.get("coordinates", {})
                    if coordinates:
                        x1, y1 = coordinates["point1"]
                        x2, y2 = coordinates["point4"]
                        self.roi_coords = (int(x1), int(y1), int(x2), int(y2))
                        self.roi_selected = True
                        self._roi_state[self.current_camera] = {
                            "coords": self.roi_coords,
                            "selected": True
                        }
                        self.pending_roi_restore = True
                        self.logger.info(f"Restored ROI for camera {self.current_camera}: {self.roi_coords}")
            except Exception as e:
                self.logger.error(f"Error restoring ROI from database: {e}", exc_info=True)
        if not self._initialized:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            self.canvas.create_text(
                canvas_width / 2,
                canvas_height / 2,
                font=("", 14),
                fill="#666666"
            )
            self._initialized = True

    def is_camera_online(self, rtsp_url, timeout=3):
        """Check if camera is online using FFmpeg"""
        try:
            ffmpeg_path = self.config.get('ffmpeg_lib_path', 'ffmpeg')
            if not os.path.exists(ffmpeg_path) and not os.path.exists(ffmpeg_path + '.exe'):
                self.logger.warning(f"FFmpeg not found at {ffmpeg_path}, using system path")
                ffmpeg_path = 'ffmpeg'
            command = [
                ffmpeg_path,
                "-rtsp_transport", "tcp",
                "-i", rtsp_url,
                "-t", str(timeout),
                "-loglevel", "error",
                "-frames:v", "1",
                "-f", "null", "-"
            ]
            self.logger.info(f"Testing camera connection: {rtsp_url}")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            if result.returncode == 0:
                self.logger.info(f"Camera Online: {rtsp_url}")
                return True
            else:
                stderr = result.stderr.decode() if result.stderr else "Unknown error"
                self.logger.warning(f"Camera Offline: {rtsp_url}\nError: {stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.logger.warning(f"FFmpeg Timeout Expired: {rtsp_url}")
            return False
        except Exception as e:
            self.logger.error(f"Error checking camera: {e}", exc_info=True)
            return False

    def start_stream(self):
        """Start a separate thread for continuous streaming"""
        # Make sure any existing stream is stopped
        self.stop_stream = True
        if self.stream_thread and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=1.0)

        # Reset critical variables
        self.stop_stream = False
        self.reconnect_attempts = 0
        self._frames_since_last_good = 0

        # Clear frame buffers
        if hasattr(self, '_last_displayed_frame'):
            self._last_displayed_frame = None
        self._last_frame = None

        # Start streaming thread
        self.stream_thread = threading.Thread(target=self.stream_frames)
        self.stream_thread.daemon = True
        self.stream_thread.start()

    def stream_frames(self):
        """Continuously stream frames from the selected camera"""
        if not self.rtsp_url:
            self.handle_camera_error("No camera selected")
            return

        try:
            self.logger.info(f"Starting stream from: {self.rtsp_url}")
            self.update_status_on_canvas("Connecting to camera...")

            # Set RTSP over TCP for more reliable streaming
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|timeout;15000000"

            cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 10)  # Reduced buffer size

            if not cap.isOpened():
                self.handle_camera_error("Could not open RTSP stream. Check your network or camera settings.")
                return

            self.logger.info("Successfully opened RTSP stream")
            consecutive_errors = 0
            frame_buffer = []  # Add a small frame buffer
            last_update_time = time.time()
            update_interval = 0.033  # ~30 FPS rate limiting

            while not self.stop_stream:
                try:
                    ret, frame = cap.read()

                    if not ret:
                        consecutive_errors += 1
                        self._frames_since_last_good += 1
                        self.logger.warning(f"Failed to read frame ({consecutive_errors} consecutive errors)")

                        # Use last good frame from buffer if available
                        if frame_buffer and self._frames_since_last_good < 30:
                            frame = frame_buffer[-1].copy()
                        elif self._last_frame is not None and self._frames_since_last_good < 30:
                            frame = self._last_frame.copy()
                        else:
                            time.sleep(0.1)
                            continue

                        # Handle reconnection
                        if consecutive_errors >= 5:
                            if self.reconnect_attempts < self.max_reconnect_attempts:
                                self.reconnect_attempts += 1
                                self.logger.info(f"Attempting reconnection #{self.reconnect_attempts}")
                                cap.release()
                                time.sleep(self.reconnect_delay)
                                cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
                                cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Reduced buffer size
                                if not cap.isOpened():
                                    self.logger.error("Reconnection failed")
                                    continue
                                consecutive_errors = 0
                            else:
                                self.logger.error("Max reconnection attempts reached")
                                self.handle_camera_error("Max reconnection attempts reached. Please check camera.")
                                break
                    else:
                        consecutive_errors = 0
                        self._frames_since_last_good = 0
                        self._last_frame = frame.copy()

                        # Maintain a small buffer of recent frames
                        frame_buffer.append(frame.copy())
                        if len(frame_buffer) > 3:  # Keep last 3 frames only
                            frame_buffer.pop(0)

                    # Rate-limit frame updates to reduce UI pressure
                    current_time = time.time()
                    if current_time - last_update_time >= update_interval:
                        # Process and display the frame
                        canvas_width = self.canvas.winfo_width()
                        canvas_height = self.canvas.winfo_height()

                        if canvas_width > 1 and canvas_height > 1 and frame is not None:
                            # Resize with consistent method and cache dimensions
                            if not hasattr(self, '_last_dimensions') or self._last_dimensions != (
                            canvas_width, canvas_height):
                                self._last_dimensions = (canvas_width, canvas_height)

                            resized_frame = cv2.resize(frame, (canvas_width, canvas_height),
                                                       interpolation=cv2.INTER_LINEAR)
                            self.frame = resized_frame
                            self.after(1, self.update_frame_display)
                            last_update_time = current_time

                    # Precise frame rate control
                    time.sleep(0.01)

                except Exception as e:
                    self.logger.error(f"Frame processing error: {e}", exc_info=True)
                    time.sleep(0.1)
                    continue

            cap.release()
            self.logger.info(f"Stopped stream for camera: {self.current_camera}")

        except Exception as e:
            self.logger.error(f"Stream error: {e}", exc_info=True)
            self.handle_camera_error(f"Stream error: {str(e)}")

    def update_status_on_canvas(self, message, color="#666666"):
        """Update status message on canvas"""
        try:
            self.canvas.delete("status_text")
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 400
                canvas_height = 300
            self.canvas.create_text(
                canvas_width / 2,
                canvas_height / 2,
                text=message,
                font=("", 14),
                fill=color,
                tags="status_text"
            )
        except Exception as e:
            self.logger.error(f"Error updating canvas status: {e}")

    def update_frame_display(self):
        """Update the UI with the current frame"""
        if self.frame is None:
            return

        try:
            # Skip redisplay if frame hasn't changed
            if hasattr(self, '_last_displayed_frame') and self._last_displayed_frame is not None:
                if np.array_equal(self.frame, self._last_displayed_frame):
                    return

            # Maintain frame copy to detect changes
            self._last_displayed_frame = self.frame.copy()

            # Convert to RGB efficiently
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            # Create and display image
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=image)

            # Only update canvas when not drawing ROI
            if not self.drawing:
                # Clear canvas just once
                self.canvas.delete("all")

                # Draw new image
                self.canvas.create_image(0, 0, image=photo, anchor="nw")

                # Keep reference to prevent GC
                self.canvas.image = photo

                # Restore ROI if needed
                if (self.pending_roi_restore or self.roi_selected) and self.roi_coords:
                    self.rect_id = self._draw_roi_rectangle(*self.roi_coords)
                    self.pending_roi_restore = False

        except Exception as e:
            self.logger.error(f"Error updating frame display: {e}", exc_info=True)
    def handle_camera_error(self, error_msg):
        """Handle camera-related errors"""
        self.logger.error(f"Camera capture error: {error_msg}")
        self.frame = None
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 400
            canvas_height = 300
        self.canvas.create_text(
            canvas_width / 2,
            canvas_height / 2,
            text=f"Camera Error:\n{error_msg}\n\nPlease select a different camera",
            font=("", 14),
            fill="#FF0000",
            justify="center"
        )

    def change_camera(self, camera_name):
        """Handle camera change from dropdown"""
        try:
            self.logger.info(f"Changing camera to: {camera_name}")
            actual_camera = camera_name

            # Save current ROI state first
            if self.current_camera:
                self._roi_state[self.current_camera] = {
                    "coords": self.roi_coords,
                    "selected": self.roi_selected
                }
                self.logger.debug(f"Saved state for {self.current_camera}: {self._roi_state[self.current_camera]}")

            # Stop current stream cleanly before starting new one
            self.stop_stream = True
            if self.stream_thread and self.stream_thread.is_alive():
                self.stream_thread.join(timeout=2.0)  # Increased timeout

            # Clear all frame buffers and references
            self._frames_since_last_good = 0
            self._last_frame = None
            if hasattr(self, '_last_displayed_frame'):
                self._last_displayed_frame = None
            self.frame = None

            # Update UI and camera settings
            self.current_camera = actual_camera
            self.rtsp_url = self.camera_list[actual_camera]
            self.canvas.delete("all")
            self.drawing = False
            self.reconnect_attempts = 0
            self.update_status_on_canvas("Connecting to camera...")

            # Apply any saved ROI state for this camera
            camera_state = self._roi_state.get(actual_camera, {})
            self.roi_coords = camera_state.get("coords")
            self.roi_selected = camera_state.get("selected", False)
            self.camera_dropdown.set(actual_camera)

            # Start new stream after a short delay
            self.after(100, self.start_stream)

        except Exception as e:
            error_msg = f"Camera switch error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

    def restore_roi(self):
        """Restore previously drawn ROI"""
        if self.roi_coords:
            self.rect_id = self._draw_roi_rectangle(*self.roi_coords)

    def _draw_roi_rectangle(self, x1, y1, x2, y2, tags="roi"):
        """Draw ROI rectangle with fill lines and border"""
        self.canvas.delete(tags)
        for y in range(min(y1, y2), max(y1, y2), self.ROI_STYLE['fill_line_spacing']):
            self.canvas.create_line(
                min(x1, x2), y,
                max(x1, x2), y,
                fill=self.ROI_STYLE['fill_line_color'],
                tags=tags
            )
        for x in range(min(x1, x2), max(x1, x2), self.ROI_STYLE['fill_line_spacing']):
            self.canvas.create_line(
                x, min(y1, y2),
                x, max(y1, y2),
                fill=self.ROI_STYLE['fill_line_color'],
                tags=tags
            )
        return self.canvas.create_rectangle(
            min(x1, x2), min(y1, y2),
            max(x1, x2), max(y1, y2),
            outline=self.ROI_STYLE['outline_color'],
            width=self.ROI_STYLE['outline_width'],
            tags=tags
        )

    # def start_draw(self, event):
    #     """Start drawing the rectangle"""
    #     if not self.current_camera:
    #         return
    #     self.canvas.delete("roi")
    #     self.canvas.delete("temp_roi")
    #     self.roi_coords = None
    #     self.roi_selected = False
    #     self.drawing = True
    #     self.start_x = event.x
    #     self.start_y = event.y
    #     self.temp_rect_id = self.canvas.create_rectangle(
    #         self.start_x, self.start_y, self.start_x, self.start_y,
    #         outline=self.roi_color, width=4, tags="temp_roi"
    #     )
    #
    # def draw_rectangle(self, event):
    #     """Update the rectangle as the mouse moves"""
    #     if self.drawing and self.temp_rect_id and self.can_draw:
    #         cur_x = min(max(event.x, 0), self.canvas.winfo_width())
    #         cur_y = min(max(event.y, 0), self.canvas.winfo_height())
    #         self.canvas.coords(self.temp_rect_id, self.start_x, self.start_y, cur_x, cur_y)
    #
    # def end_draw(self, event):
    #     """End drawing the rectangle"""
    #     if self.drawing:
    #         self.drawing = False
    #         self.canvas.delete("roi")
    #         try:
    #             x1, y1, x2, y2 = self.canvas.coords(self.temp_rect_id)
    #             self.canvas.delete("temp_roi")
    #             if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
    #                 return
    #             self.roi_coords = (
    #                 int(min(x1, x2)),
    #                 int(min(y1, y2)),
    #                 int(max(x1, x2)),
    #                 int(max(y1, y2))
    #             )
    #             self.roi_selected = True
    #             self.rect_id = self._draw_roi_rectangle(*self.roi_coords)
    #         except Exception as e:
    #             self.logger.error(f"Error finalizing ROI drawing: {e}", exc_info=True)

    def __del__(self):
        """Clean up resources"""
        self.stop_stream = True
        if hasattr(self, 'stream_thread') and self.stream_thread and self.stream_thread.is_alive():
            try:
                self.stream_thread.join(timeout=1.0)
            except:
                pass