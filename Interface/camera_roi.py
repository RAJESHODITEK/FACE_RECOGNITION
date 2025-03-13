import subprocess
import tkinter as tk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkOptionMenu, CTkEntry
import cv2
from PIL import Image, ImageTk
import threading
import time
import logging

#from FrameOperation.CameraManager import CameraStateManager


class CameraRoiInterface(CTkFrame):
    def __init__(self, master, root_width=None, root_height=None, **kwargs):
        if 'root_width' in kwargs:
            del kwargs['root_width']
        if 'root_height' in kwargs:
            del kwargs['root_height']

        super().__init__(master, **kwargs)

        # Set minimum dimensions
        self.min_width = 800
        self.min_height = 600

        # Initialize instance variables
        self._roi_state = {}
        self.camera_list = {}
        self.current_camera = None
        self.rtsp_url = None
        self.obj_Core = None

        self._initialized = False
        self.pending_roi_restore = False

        # Get screen dimensions
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        # Set height with extra room for buttons
        self.form_height = int(min(self.screen_height * 0.85, self.screen_height - 100))
        self.form_width = self.screen_width

        self.running = True
        self.roi_selected = False
        self.roi_coords = None
        self.frame = None
        self.drawing = False

        self.ROI_STYLE = {
            'outline_color': "#DAA520",  # Golden color
            'outline_width': 3,
            'fill_line_color': "black",
            'fill_line_spacing': 2
        }

        # Configure main frame
        self.configure(fg_color="#F1F5FA", corner_radius=0)

        # Main form frame
        self.frame_form = CTkFrame(
            self,
            fg_color="#F1F5FA",
            corner_radius=2
        )
        self.frame_form.pack(expand=True, fill="both", padx=5, pady=5)

        # Header frame
        self.header_frame = CTkFrame(
            self.frame_form,
            fg_color="#F1F5FA",
            corner_radius=0,
            height=40
        )
        self.header_frame.pack(fill="x", padx=10, pady=(5, 0))
        self.header_frame.pack_propagate(False)

        # Header elements
        self.label_heading = CTkLabel(
            self.header_frame,
            text="Camera ROI Selection",
            text_color="#000000",
            font=("Arial", 16, "bold")
        )
        self.label_heading.pack(side="left", pady=5)

        # Dropdown
        self.dropdown_values = []
        self.camera_dropdown = CTkLabel(
            self.header_frame,
            text='',
            fg_color="#FFFFFF",
            text_color="#000000",
            width=160,
            height=30,
            corner_radius=2
        )
        self.camera_dropdown.pack(side="left", padx=(20, 0), pady=5)


        self.status_label = CTkLabel(
            self.header_frame,
            text="Draw ROI on the image",
            text_color="#FFA500",
            font=("Arial", 12)
        )
        self.status_label.pack(side="right", pady=5, padx=5)

        # Canvas frame with fixed maximum height
        canvas_max_height = int(self.form_height * 0.65)  # 65% of form height
        self.canvas_frame = CTkFrame(
            self.frame_form,
            fg_color="#FFFFFF",
            corner_radius=0,
            height=canvas_max_height
        )
        self.canvas_frame.pack(expand=True, fill="both", padx=15, pady=5)

        # Canvas
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg="#FFFFFF",
            highlightthickness=1,
            highlightbackground="#DEDEDE",
            height=canvas_max_height - 10  # Account for padding
        )
        self.canvas.pack(expand=True, fill="both", padx=5, pady=5)

        # Control frame with fixed height
        self.control_frame = CTkFrame(
            self.frame_form,
            fg_color="#F1F5FA",
            corner_radius=0,
            height=90  # Increased height for better button visibility
        )
        self.control_frame.pack(fill="x", padx=10, pady=5)
        self.control_frame.pack_propagate(False)

        # Buttons with padding from the bottom
        self.button_frame = CTkFrame(
            self.control_frame,
            fg_color="#F1F5FA"
        )
        self.button_frame.pack(expand=True, pady=10)

        # Buttons
        self.save_button = CTkButton(
            self.button_frame,
            text="Save ROI",
            command=self.save_roi,
            fg_color="#5A616B",
            hover_color="#313A46",
            font=("Arial", 12, "bold"),
            corner_radius=4,
            state="disabled",
            height=35,
            width=100
        )
        self.save_button.pack(side="left", padx=5)

        self.cancel_button = CTkButton(
            self.button_frame,
            text="Cancel ROI",
            command=self.cancel_roi,
            fg_color="#6C757D",
            hover_color="#313A46",
            font=("Arial", 12, "bold"),
            corner_radius=4,
            height=35,
            width=100
        )
        self.cancel_button.pack(side="left", padx=5)


        # Initialize variables for ROI drawing
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.temp_rect_id = None
        self.can_draw = True
        self.roi_color = "#DAA520"

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        # Initialize frame and ROI
        self.initialize_frame_and_roi()

        #self.camera_manager = CameraStateManager()

    def update_camera_list(self, new_camera_list):
        """Update the camera list and dropdown with new values from database"""
        try:
            self.camera_list = new_camera_list
            print("Updating camera list with:", new_camera_list)

            # Update dropdown values with checkbox symbols
            self.dropdown_values = [f"☐ {camera}" for camera in self.camera_list.keys()]

            # Only automatically select a camera if none is currently selected
            if not self.current_camera and self.camera_list:
                first_camera = list(self.camera_list.keys())[0]
                self.change_camera(first_camera)

            if not self.dropdown_values:
                self.status_label.configure(text="No cameras available", text_color="#FF0000")

        except Exception as e:
            print(f"Error updating camera list: {e}")
            self.status_label.configure(text="Error updating camera list", text_color="#FF0000")

    def initialize_frame_and_roi(self):
        """Initialize the frame and restore ROI if available"""
        # Clear any existing ROI
        if hasattr(self, 'canvas'):
            self.canvas.delete("all")

        # If we have a current camera, try to restore its ROI
        if self.current_camera:
            # Try to get ROI data from the database
            try:
                roi_data = self.obj_Core.obj_Camera.get_roi_coordinates(self.current_camera)
                if roi_data and not roi_data.get("str_error_msg"):
                    coordinates = roi_data.get("coordinates", {})
                    if coordinates:
                        # Extract coordinates
                        x1, y1 = coordinates["point1"]
                        x2, y2 = coordinates["point4"]
                        self.roi_coords = (int(x1), int(y1), int(x2), int(y2))
                        self.roi_selected = True
                        self._roi_state[self.current_camera] = {
                            "coords": self.roi_coords,
                            "selected": True
                        }
                        self.pending_roi_restore = True
            except Exception as e:
                print(f"Error restoring ROI from database: {e}")

        if not self._initialized:
            # Create a message on the canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            self.canvas.create_text(
                canvas_width / 2,
                canvas_height / 2,
                font=("Arial", 14),
                fill="#666666"
            )
            self._initialized = True

    def is_camera_online(self, rtsp_url, timeout=3):
        try:
            command = [
                r"F:\ALPR_SOURCE_CODE\ffmpeg-7.1-full_build\ffmpeg-7.1-full_build\bin\ffmpeg.exe",
                "-rtsp_transport", "tcp", "-i", rtsp_url,
                "-t", str(timeout), "-loglevel", "error", "-frames:v", "1", "-f", "image2pipe", "-"
            ]

            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)

            if result.returncode == 0:
                print(f"Camera Online: {rtsp_url}")
                return True
            else:
                print(f"Camera Offline: {rtsp_url}\nError: {result.stderr.decode()}")
                return False
        except subprocess.TimeoutExpired:
            print(f"Timeout Expired: {rtsp_url}")
            return False

    def capture_frame(self):
        """Capture a single frame from the RTSP stream with robust error handling."""
        if not self.rtsp_url:
            self.handle_camera_error("No camera selected")
            return

        try:
            print(f"Attempting to open RTSP URL: {self.rtsp_url}-----------------------------------------")

            # Check if the RTSP connection is valid
            if not self.is_camera_online(self.rtsp_url):
                self.handle_camera_error("Failed to connect to camera. Invalid RTSP URL or Network issues.")
                return

            cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                cap.release()
                self.handle_camera_error("Could not open RTSP stream. Check your network or camera settings.")
                return

            print("Successfully opened RTSP URL")

            ret, frame = False, None
            max_retries = 3  # Try multiple times before giving up
            for attempt in range(max_retries):
                print(f"Attempt {attempt + 1}: Trying to read a frame...")
                ret, frame = cap.read()
                if ret and frame is not None:
                    print("Frame read successfully!")
                    break
                time.sleep(0.6)  # Delay between retries

            cap.release()

            # Check if frame retrieval was successful
            if not ret or frame is None:
                self.handle_camera_error("Could not read frame from camera. Please try again.")
                return

            print("Successfully read a frame")

            # Resize frame to fit the canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            self.frame = cv2.resize(frame, (canvas_width, canvas_height), interpolation=cv2.INTER_LANCZOS4)

            self._last_frame = self.frame
            self._last_camera = self.current_camera
            self.display_frame()
            self.status_label.configure(text="Frame captured", text_color="#00FF00")

        except cv2.error as e:
            logging.error(f"OpenCV error: {e}", exc_info=True)
            self.handle_camera_error(f"OpenCV error occurred: {str(e)}")

        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
            self.handle_camera_error("An unexpected error occurred. Please try again.")

    def handle_camera_error(self, error_msg):
        """Centralized error handling for camera-related issues"""
        print(f"Camera capture error: {error_msg}")

        # Set error message and update UI
        self.status_label.configure(text=f"Camera error: {error_msg}", text_color="#FF0000")

        # Clear the frame and display error message on canvas
        self.frame = None
        self.canvas.delete("all")

        # Create error message on canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.canvas.create_text(
            canvas_width / 2,
            canvas_height / 2,
            text=f"Camera Error:\n{error_msg}\n\nPlease select a different camera",
            font=("Arial", 14),
            fill="#FF0000",
            justify="center"
        )
        # Reset ROI state
        self.roi_coords = None
        self.roi_selected = False
        self.save_button.configure(state="disabled")

    def display_frame(self):
        """Display the current frame on the canvas"""
        if self.frame is not None:
            # Get current canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Ensure frame matches canvas size
            if self.frame.shape[1] != canvas_width or self.frame.shape[0] != canvas_height:
                self.frame = cv2.resize(self.frame, (canvas_width, canvas_height),
                                        interpolation=cv2.INTER_LANCZOS4)

            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=image)
            self.canvas.delete("all")  # Clear canvas before creating new image
            self.canvas.create_image(0, 0, image=photo, anchor="nw")
            self.canvas.image = photo

            # If there's a pending ROI restore, do it now
            if self.pending_roi_restore and self.roi_selected and self.roi_coords:
                self.restore_roi()
                self.pending_roi_restore = False
    def change_camera(self, camera_name):
        """Handle camera change from dropdown"""
        try:

            print("chnage camera name : ",camera_name)
            # Remove checkbox symbol to get actual camera name
            # actual_camera = camera_name.split(" ", 1)[1]
            actual_camera=camera_name
            # Save current ROI state before switching
            if self.current_camera:
                self._roi_state[self.current_camera] = {
                    "coords": self.roi_coords,
                    "selected": self.roi_selected
                }
                print(f"Saved state for {self.current_camera}: {self._roi_state[self.current_camera]}")

            # Update UI to show loading state
            self.status_label.configure(text="Switching camera...", text_color="#FFA500")
            self.update()

            # Switch camera
            self.current_camera = actual_camera
            self.rtsp_url = self.camera_list[actual_camera]

            # Clear canvas and reset drawing state
            self.canvas.delete("all")
            self.drawing = False

            # Capture new frame first
            self.capture_frame()

            # After frame is captured, restore ROI state if it exists
            camera_state = self._roi_state.get(actual_camera, {})
            print(f"Loading state for {actual_camera}: {camera_state}")

            self.roi_coords = camera_state.get("coords")
            self.roi_selected = camera_state.get("selected", False)

            # Update dropdown values
            self.dropdown_values = [
                f"☑ {cam}" if cam == actual_camera else f"☐ {cam}"
                for cam in self.camera_list.keys()
            ]
            self.camera_dropdown.configure(text=actual_camera)
            #self.camera_dropdown.set(f"☑ {actual_camera}")

            # Update save button state based on ROI
            if self.roi_selected and self.roi_coords:
                self.save_button.configure(state="normal")
                self.restore_roi()
            else:
                self.save_button.configure(state="disabled")
                # self.roi_coords_label.configure(text="ROI: None")
                self.status_label.configure(text="Draw ROI on the image", text_color="#FFA500")

        except Exception as e:
            error_msg = f"Camera switch error: {str(e)}"
            print(error_msg)
            self.status_label.configure(text=error_msg, text_color="#FF0000")

    def restore_roi(self):
        """Restore previously drawn ROI"""
        if self.roi_coords:
            # Use the helper method to draw the ROI
            self.rect_id = self._draw_roi_rectangle(*self.roi_coords)

            if self.roi_selected:
                self.save_button.configure(state="normal")



    def _draw_roi_rectangle(self, x1, y1, x2, y2, tags="roi"):
        """Helper method to consistently draw ROI rectangles with fill lines and border"""
        # Clear any existing ROI with the same tags
        self.canvas.delete(tags)

        # Draw horizontal fill lines
        for y in range(min(y1, y2), max(y1, y2), self.ROI_STYLE['fill_line_spacing']):
            self.canvas.create_line(
                min(x1, x2), y,
                max(x1, x2), y,
                fill=self.ROI_STYLE['fill_line_color'],
                tags=tags
            )

        # Draw vertical fill lines
        for x in range(min(x1, x2), max(x1, x2), self.ROI_STYLE['fill_line_spacing']):
            self.canvas.create_line(
                x, min(y1, y2),
                x, max(y1, y2),
                fill=self.ROI_STYLE['fill_line_color'],
                tags=tags
            )

        # Draw border rectangle
        return self.canvas.create_rectangle(
            min(x1, x2), min(y1, y2),
            max(x1, x2), max(y1, y2),
            outline=self.ROI_STYLE['outline_color'],
            width=self.ROI_STYLE['outline_width'],
            tags=tags
        )


    def start_draw(self, event):
        """Start drawing the rectangle"""
        # First check if a camera is selected
        if not self.current_camera:
            self.status_label.configure(
                text="Please select a camera before drawing ROI",
                text_color="#FF0000"
            )
            return

        # Clear all existing ROIs and temporary shapes
        self.canvas.delete("roi")
        self.canvas.delete("temp_roi")

        # Reset ROI state
        self.roi_coords = None
        self.roi_selected = False
        self.save_button.configure(state="disabled")

        # Start new drawing
        self.drawing = True
        self.start_x = event.x
        self.start_y = event.y
        self.temp_rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline=self.roi_color, width=4, tags="temp_roi"
        )

    def draw_rectangle(self, event):
        """Update the rectangle as the mouse moves"""
        if self.drawing and self.temp_rect_id and self.can_draw:
            # Constrain cursor position within canvas bounds
            cur_x = min(max(event.x, 0), self.canvas.winfo_width())
            cur_y = min(max(event.y, 0), self.canvas.winfo_height())

            # Update rectangle coordinates
            self.canvas.coords(self.temp_rect_id, self.start_x, self.start_y, cur_x, cur_y)

    def end_draw(self, event):
        """End drawing the rectangle"""
        if self.drawing:
            self.drawing = False

            # Clear any existing ROIs first
            self.canvas.delete("roi")

            x1, y1, x2, y2 = self.canvas.coords(self.temp_rect_id)
            self.canvas.delete("temp_roi")  # Remove the temporary rectangle

            self.roi_coords = (
                int(min(x1, x2)),
                int(min(y1, y2)),
                int(max(x1, x2)),
                int(max(y1, y2))
            )
            self.roi_selected = True

            # Use the helper method to draw the final ROI
            self.rect_id = self._draw_roi_rectangle(*self.roi_coords)

            self.save_button.configure(state="normal")
            self.status_label.configure(text="ROI selected", text_color="#00FF00")
    def save_roi(self):
        """Save the ROI coordinates and calculate percentages based on frame dimensions"""
        if self.roi_selected and self.frame is not None:
            try:
                # Update ROI state
                self._roi_state[self.current_camera] = {
                    "coords": self.roi_coords,
                    "selected": True
                }

                # Get frame dimensions
                frame_height = self.frame.shape[0]
                frame_width = self.frame.shape[1]

                # Get ROI coordinates
                x1, y1, x2, y2 = self.roi_coords

                # Calculate percentages based on frame dimensions
                ROIStartPercentageWidth = (x1 / frame_width) * 100
                ROIEndPercentageWidth = (x2 / frame_width) * 100
                ROIStartPercentageHeight = (y1 / frame_height) * 100
                ROIEndPercentageHeight = (y2 / frame_height) * 100

                # Prepare coordinates dictionary
                ROICoordinates = {
                    "point1": [x1, y1],
                    "point2": [x2, y1],
                    "point3": [x1, y2],
                    "point4": [x2, y2],
                    "frame_height": frame_height,
                    "frame_width": frame_width
                }

                # Save to database through Core object
                result = self.obj_Core.obj_Camera.add_roi_coordinates(
                    self.current_camera,
                    ROIStartPercentageHeight,
                    ROIEndPercentageHeight,

                    ROIStartPercentageWidth,
                    ROIEndPercentageWidth,
                    ROICoordinates,
                )

                if result["str_error_msg"]:
                    raise Exception(result["str_error_msg"])

                # Log the saved data
                print(f"\nSaved ROI coordinates and percentages:")
                print(f"Frame dimensions: {frame_width}x{frame_height}")
                print(f"ROI coordinates: ({x1},{y1}),({x2},{y1}),({x1},{y2}),({x2},{y2})")
                print(f"X-axis percentages: {ROIStartPercentageWidth:.2f}% - {ROIEndPercentageWidth:.2f}%")
                print(f"Y-axis percentages: {ROIStartPercentageHeight:.2f}% - {ROIEndPercentageHeight:.2f}%")

                # Redraw frame to ensure it's displayed
                self.display_frame()
                self.rect_id = self._draw_roi_rectangle(*self.roi_coords)

                self.save_button.configure(state="disabled")
                self.status_label.configure(text="ROI saved successfully", text_color="#00FF00")

            except Exception as e:
                self.status_label.configure(text=f"Save error: {str(e)}", text_color="#FF0000")
                print(f"Error saving ROI: {str(e)}")

    def cancel_roi(self):
        """Restore the previously saved ROI"""

        if self.current_camera:
            saved_roi = self._roi_state.get(self.current_camera)

            if saved_roi and saved_roi.get('coords') and saved_roi.get('selected'):
                # Clear existing drawings and redisplay frame
                self.canvas.delete("all")
                self.display_frame()

                # Restore saved coordinates using helper method
                self.rect_id = self._draw_roi_rectangle(*saved_roi['coords'])

                # Update current state
                self.roi_coords = saved_roi['coords']
                self.roi_selected = True
                self.save_button.configure(state="normal")
                self.status_label.configure(text="Saved ROI restored", text_color="#00FF00")
            else:
                # No saved ROI exists
                self.canvas.delete("all")
                self.display_frame()
                self.roi_coords = None
                self.roi_selected = False
                self.save_button.configure(state="disabled")
                self.status_label.configure(text="Draw ROI on the image", text_color="#FFA500")