import base64
from datetime import datetime
import cv2
import numpy as np
import pyodbc
import torch
from ultralytics import YOLO
import argparse
from collections import defaultdict
import time
import threading
import queue
import os

from Core.db_connection import Camera_db
from shared_queue import shared_queue, current_camera_details,all_camera_data


class YOLOTracker:
    def __init__(self, model_path='yolo11l.pt', conf_threshold=0.2, iou_threshold=0.7, target_classes=None):
        print("Loading YOLO model...")
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.obj_Camera= Camera_db()
        self.points=(1,100,1,100)
        # Track history for smoothing
        self.track_history = defaultdict(list)
        self.max_history_length = 10
        self.frame_stock_for_record_queue= queue.Queue(maxsize=self.max_history_length)
        self.stock_image_processor_thread= threading.Thread(target=self.stock_image_processing,daemon=True)
        self.stock_image_processor_thread.start()


        # Performance optimization
        self.model.overrides['verbose'] = False
        self.saved_object_images = set()

        # Sequential track ID management
        self.yolo_to_sequential_id = {}
        self.next_sequential_id = 1
        self.used_track_ids = set()
        self.sequential_track_history = defaultdict(list)
        self.copy_frame = None
        self.active_tracks = set()
        self.last_seen = defaultdict(float)
        self.track_timeout = 4.0
        self.track_hits_list = []

        self.last_valid_detections = []  # Store last valid detections for visualization
        self.detection_frame_count = 0  # Track when detections were last updated
        self.max_detection_age = 5  # Maximum frames to show old detections

        # Class filtering
        self.target_classes = target_classes
        self.setup_class_filter()
        self.copy_frame=None

        # Initialize track IDs from database
        self.initialize_track_ids_from_db()

        # Database queue for async writes
        self.db_queue = queue.Queue(maxsize=100)  # Limit queue size
        self.db_thread = threading.Thread(target=self._process_db_queue, daemon=True)
        self.db_thread.start()

        # IMPROVED BUFFER MANAGEMENT
        self.buffer_size = 1  # Reduced buffer size for RTSP
        self.frame_count = 0
        self.skip_frames = 1  # Skip frames to reduce processing load
        self.frame_skip_counter = 0

        # Video recording optimizations
        self.video_output_dir = "E:\\track_videos"
        self.create_video_directory()
        self.track_video_writers = {}
        self.track_frame_buffers = defaultdict(list)
        self.track_recording_started = {}
        self.video_fps = 10
        self.video_duration = 10
        self.max_frames_per_track = self.video_fps * self.video_duration
        self.valid_videos = set()

        # BUFFER OVERFLOW PREVENTION
        self.max_buffer_frames = 50  # Maximum frames to keep in any buffer
        self.cleanup_interval = 30  # Cleanup every 30 frames
        self.last_cleanup = time.time()

        # Connection health monitoring
        self.connection_health = {
            'consecutive_failures': 0,
            'max_failures': 5,
            'last_successful_read': time.time(),
            'reconnect_count': 0,
            'frame_rate_drop_threshold': 5.0  # FPS below this triggers reconnection
        }

        # Frame rate monitoring
        self.fps_monitor = {
            'frame_times': [],
            'max_samples': 10,
            'target_fps': 30.0,
            'low_fps_count': 0,
            'low_fps_threshold': 3
        }

        self.roi_x1 = 1
        self.roi_x2 = 100
        self.roi_y1 = 1
        self.roi_y2 = 100

        # Log device usage
        print(f"Using device: {'GPU' if torch.cuda.is_available() else 'CPU'}")

    def create_video_directory(self):
        """Create directory for storing track videos"""
        if not os.path.exists(self.video_output_dir):
            os.makedirs(self.video_output_dir)
            print(f"Created video output directory: {self.video_output_dir}")

    def cleanup_buffers(self):
        """Enhanced buffer cleanup to prevent overflow"""
        current_time = time.time()

        # Clean up frame buffers that are too large
        for track_id in list(self.track_frame_buffers.keys()):
            buffer = self.track_frame_buffers[track_id]
            if len(buffer) > self.max_buffer_frames:
                # Keep only the most recent frames
                self.track_frame_buffers[track_id] = buffer[-self.max_buffer_frames // 2:]
                print(
                    f"Trimmed buffer for track {track_id} from {len(buffer)} to {len(self.track_frame_buffers[track_id])} frames")

        # Clean up old track histories
        for track_id in list(self.sequential_track_history.keys()):
            if len(self.sequential_track_history[track_id]) > self.max_history_length:
                self.sequential_track_history[track_id] = self.sequential_track_history[track_id][
                                                          -self.max_history_length:]

        # Clean up stale video writers
        for track_id in list(self.track_video_writers.keys()):
            if track_id in self.track_recording_started:
                recording_duration = current_time - self.track_recording_started[track_id]
                if recording_duration > self.video_duration + 5:  # 5 second grace period
                    print(f"Force finalizing stale video for track {track_id}")
                    self.finalize_track_video(track_id)

        self.last_cleanup = current_time

    def monitor_frame_rate(self, frame_time):
        """Monitor frame rate and detect performance issues"""
        self.fps_monitor['frame_times'].append(frame_time)

        # Keep only recent samples
        if len(self.fps_monitor['frame_times']) > self.fps_monitor['max_samples']:
            self.fps_monitor['frame_times'].pop(0)

        # Calculate current FPS
        if len(self.fps_monitor['frame_times']) >= 3:
            avg_frame_time = sum(self.fps_monitor['frame_times']) / len(self.fps_monitor['frame_times'])
            current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0

            # Check for low FPS
            if current_fps < self.fps_monitor['target_fps'] / 3:  # Less than 1/3 of target FPS
                self.fps_monitor['low_fps_count'] += 1
                if self.fps_monitor['low_fps_count'] >= self.fps_monitor['low_fps_threshold']:
                    print(f"Warning: Low FPS detected ({current_fps:.1f}), may need reconnection")
                    return True
            else:
                self.fps_monitor['low_fps_count'] = 0

        return False

    def setup_rtsp_stream(self, video_path):
        """Enhanced RTSP stream setup with better buffer management"""
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return None

        # CRITICAL: Aggressive RTSP optimizations
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer
        cap.set(cv2.CAP_PROP_FPS, 30)

        # Set codec preferences
        try:
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
        except:
            try:
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            except:
                print("Warning: Could not set preferred codec")

        # Additional RTSP optimizations
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Clear initial buffer by reading and discarding frames
        print("Clearing initial RTSP buffer...")
        for i in range(10):
            ret, _ = cap.read()
            if not ret:
                print(f"Warning: Could not clear buffer frame {i + 1}")
                break

        print("RTSP stream setup completed with optimized settings")
        return cap

    def handle_connection_failure(self, cap, video_path):
        """Enhanced connection failure handling"""
        self.connection_health['consecutive_failures'] += 1

        if self.connection_health['consecutive_failures'] >= self.connection_health['max_failures']:
            print(
                f"Connection failed {self.connection_health['consecutive_failures']} times, attempting reconnection...")

            # Release current connection
            if cap:
                cap.release()

            # Wait before reconnecting
            time.sleep(2)

            # Attempt reconnection
            new_cap = self.setup_rtsp_stream(video_path)
            if new_cap:
                self.connection_health['consecutive_failures'] = 0
                self.connection_health['reconnect_count'] += 1
                self.connection_health['last_successful_read'] = time.time()
                print(f"Successfully reconnected (reconnection #{self.connection_health['reconnect_count']})")
                return new_cap
            else:
                print("Reconnection failed")
                return None

        return cap

    def initialize_track_ids_from_db(self):
        try:
            print("Checking existing track IDs in database...")
            conn = pyodbc.connect(
                r'DRIVER={ODBC Driver 17 for SQL Server};'
                r'SERVER=ITDT23;'
                r'DATABASE=ZONE_INTRUSION_DB;'
                r'UID=sa;'
                r'PWD=root1234;'
            )
            cursor = conn.cursor()
            query = "SELECT DISTINCT vehicle_id FROM [ZONE_INTRUSION_DB].[dbo].[event_details] WHERE vehicle_id IS NOT NULL"
            cursor.execute(query)
            existing_ids = cursor.fetchall()
            for row in existing_ids:
                if row[0] is not None:
                    self.used_track_ids.add(int(row[0]))
            if self.used_track_ids:
                self.next_sequential_id = max(self.used_track_ids) + 1
                print(f"Found {len(self.used_track_ids)} existing track IDs in database")
                print(f"Next available track ID will start from: {self.next_sequential_id}")
            else:
                self.next_sequential_id = 1
                print("No existing track IDs found in database. Starting from ID 1")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error initializing track IDs from database: {e}")
            self.next_sequential_id = 1

    def get_next_available_track_id(self):
        while self.next_sequential_id in self.used_track_ids:
            self.next_sequential_id += 1
        current_id = self.next_sequential_id
        self.used_track_ids.add(current_id)
        self.next_sequential_id += 1
        return current_id

    def get_sequential_track_id(self, yolo_track_id):
        current_time = time.time()
        if yolo_track_id not in self.yolo_to_sequential_id:
            new_id = self.get_next_available_track_id()
            self.yolo_to_sequential_id[yolo_track_id] = new_id
            self.active_tracks.add(yolo_track_id)
            print(f"Assigned new track ID {new_id} to YOLO track {yolo_track_id}")
        self.last_seen[yolo_track_id] = current_time
        return self.yolo_to_sequential_id[yolo_track_id]

    def cleanup_stale_tracks(self):
        current_time = time.time()
        stale_tracks = [
            track_id for track_id in self.active_tracks
            if current_time - self.last_seen[track_id] > self.track_timeout
        ]
        for track_id in stale_tracks:
            self.active_tracks.remove(track_id)
            sequential_id = self.yolo_to_sequential_id.pop(track_id, None)
            if sequential_id:
                # Finalize and save video for this track
                self.finalize_track_video(sequential_id)
                self.sequential_track_history.pop(sequential_id, None)
                self.track_history.pop(sequential_id, None)
            self.last_seen.pop(track_id, None)
            print(f"Cleaned up stale track ID {track_id}")

    def check_track_id_in_db(self, track_id):
        try:
            conn = pyodbc.connect(
                r'DRIVER={ODBC Driver 17 for SQL Server};'
                r'SERVER=ITDT23;'
                r'DATABASE=ZONE_INTRUSION_DB;'
                r'UID=sa;'
                r'PWD=root1234;'
            )
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM [ZONE_INTRUSION_DB].[dbo].[event_details] WHERE vehicle_id = ?"
            cursor.execute(query, track_id)
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count > 0
        except Exception as e:
            print(f"Error checking track ID in database: {e}")
            return False

    def _process_db_queue(self):
        """Enhanced database queue processing with overflow protection"""
        while True:
            try:
                # Use timeout to prevent hanging
                item = self.db_queue.get(timeout=1.0)
                self._save_to_db(item)
                self.db_queue.task_done()

                # Check if queue is getting too full
                if self.db_queue.qsize() > 80:  # 80% of max capacity
                    print(f"Warning: Database queue is {self.db_queue.qsize()}/100 full")

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in database queue processing: {e}")

    def create_individual_track_frame(self, frame, target_track_id, boxes, confidences, class_ids, track_ids):
        """Create a frame showing only the specified track ID with its bounding box"""
        frame_copy = frame.copy()

        category_colors = {
            'person': (255, 0, 0),
            'animal': (0, 255, 0),
            'vehicle': (0, 0, 255),
            'default': (255, 255, 0)
        }

        # Find the target track in current detections
        for i, (box, conf, class_id) in enumerate(zip(boxes, confidences, class_ids)):
            if conf < self.conf_threshold or not self.is_allowed_class(class_id):
                continue

            yolo_track_id = track_ids[i] if track_ids is not None else i
            sequential_track_id = self.get_sequential_track_id(yolo_track_id)

            # Only draw this track if it matches our target
            if sequential_track_id == target_track_id:
                smoothed_box = self.smooth_bbox(sequential_track_id, box.tolist())
                x1, y1, x2, y2 = map(int, smoothed_box)
                center_x = x1 + ((x2 - x1) / 2)
                center_y = y1 + ((y2 - y1) / 2)

                generic_class_name = self.get_generic_class_name(class_id)
                color = category_colors.get(generic_class_name, category_colors['default'])

                # Draw bounding box
                cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)

                # Draw label
                label = f"ID:{sequential_track_id} {generic_class_name} {conf:.2f}"
                (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                label_y = max(y1, label_height + 10)
                cv2.rectangle(frame_copy, (x1, label_y - label_height - 10), (x1 + label_width, label_y), color, -1)
                cv2.putText(frame_copy, label, (x1, label_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                break

        return frame_copy

    def start_track_video_recording(self, track_id, frame_shape):
        """Initialize video writer for a specific track"""
        if track_id not in self.track_video_writers:
            height, width = frame_shape[:2]
            video_filename = os.path.join(self.video_output_dir, f"track_{track_id}.mp4")

            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.track_video_writers[track_id] = cv2.VideoWriter(
                video_filename, fourcc, self.video_fps, (width, height)
            )
            self.track_recording_started[track_id] = time.time()  # Store start time
            print(f"Started video recording for track ID {track_id}: {video_filename}")

    def add_frame_to_track_video(self, track_id, frame, boxes, confidences, class_ids, track_ids):
        """Add frame to track's video buffer with overflow protection"""
        if track_id not in self.track_frame_buffers:
            self.track_frame_buffers[track_id] = []

        # Buffer overflow protection
        current_buffer = self.track_frame_buffers[track_id]
        if len(current_buffer) >= self.max_frames_per_track:
            print(f"Track {track_id} buffer full, finalizing video")
            self.finalize_track_video(track_id)
            return

        # Only add frame if we haven't reached the maximum
        elif len(current_buffer) < self.max_frames_per_track:
            # Create individual track frame
            track_frame = self.create_individual_track_frame(frame, track_id, boxes, confidences, class_ids, track_ids)
            current_buffer.append(track_frame)

            # If this is the first frame, start video recording
            if track_id not in self.track_recording_started:
                self.start_track_video_recording(track_id, frame.shape)

        # # If buffer is full, write all frames and finalize
        # if len(current_buffer) >= self.max_frames_per_track:
        #     self.finalize_track_video(track_id)

    def finalize_track_video(self, track_id):
        """Write all buffered frames to video file and close writer"""
        if track_id in self.track_frame_buffers and self.track_frame_buffers[track_id]:
            # Write all frames to video
            if track_id in self.track_video_writers:
                try:
                    for frame in self.track_frame_buffers[track_id]:
                        self.track_video_writers[track_id].write(frame)

                    # Close video writer
                    self.track_video_writers[track_id].release()
                    del self.track_video_writers[track_id]

                    frame_count = len(self.track_frame_buffers[track_id])
                    duration = frame_count / self.video_fps
                    print(f"Finalized video for track ID {track_id}: {frame_count} frames, {duration:.1f}s duration")

                    # Mark video as valid if duration is at least 2 seconds
                    if duration >= 2.0:
                        self.valid_videos.add(track_id)

                except Exception as e:
                    print(f"Error finalizing video for track {track_id}: {e}")

            # Clear buffer
            del self.track_frame_buffers[track_id]

        # Clean up recording flag
        if track_id in self.track_recording_started:
            del self.track_recording_started[track_id]

    def _process_frame(self, frame, frame_count):
        """Enhanced frame processing with persistent visualization during frame skipping"""
        # Skip frames to reduce processing load
        self.frame_skip_counter += 1
        self.copy_frame = frame.copy()
        should_process = (self.frame_skip_counter % (self.skip_frames + 1) == 0)

        if should_process:
            # Process YOLO detection and tracking
            results = self.model.track(
                frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                persist=True,
                tracker="bytetrack.yaml",
                verbose=False,
                imgsz=640,
                half=True,
                device='0' if torch.cuda.is_available() else 'cpu'
            )

            # Cleanup stale tracks
            self.cleanup_stale_tracks()

            # Periodic buffer cleanup
            if frame_count % self.cleanup_interval == 0:
                self.cleanup_buffers()

            # Update last valid detections for visualization
            if results[0].boxes is not None:
                self.update_last_valid_detections(results[0])
                self.detection_frame_count = frame_count

            # Process video recording (reduced frequency)
            should_record_frame = frame_count % 2
            if should_record_frame and results[0].boxes is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                confidences = results[0].boxes.conf.cpu().numpy()
                class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
                track_ids = results[0].boxes.id.cpu().numpy().astype(int) if hasattr(results[0].boxes, 'id') and \
                                                                             results[0].boxes.id is not None else None

                # Process each detected track for video recording
                for i, (box, conf, class_id) in enumerate(zip(boxes, confidences, class_ids)):
                    if conf < self.conf_threshold or not self.is_allowed_class(class_id):
                        continue

                    yolo_track_id = track_ids[i] if track_ids is not None else i
                    sequential_track_id = self.get_sequential_track_id(yolo_track_id)


                    # Add frame to this track's video
                    if not self.frame_stock_for_record_queue.full():
                        self.frame_stock_for_record_queue.put((sequential_track_id, self.copy_frame, boxes, confidences, class_ids, track_ids),block=False)
                    # self.add_frame_to_track_video(sequential_track_id, frame, boxes, confidences, class_ids, track_ids)

            # Draw tracks using current or last valid detections
            return self.draw_tracks_with_persistence(frame, results if should_process else None, frame_count)
        else:
            # For skipped frames, use last valid detections for visualization
            return self.draw_tracks_with_persistence(frame, None, frame_count)

    def stock_image_processing(self):
        while True:
            if not self.frame_stock_for_record_queue.empty():
                params = self.frame_stock_for_record_queue.get()
                self.add_frame_to_track_video(params[0], params[1], params[2], params[3], params[4], params[5])
            else:
                time.sleep(1)

    def update_last_valid_detections(self, yolo_results):
        """Store the last valid detections for visualization during frame skipping"""
        if yolo_results.boxes is None:
            return

        boxes = yolo_results.boxes.xyxy.cpu().numpy()
        confidences = yolo_results.boxes.conf.cpu().numpy()
        class_ids = yolo_results.boxes.cls.cpu().numpy().astype(int)
        track_ids = yolo_results.boxes.id.cpu().numpy().astype(int) if hasattr(yolo_results.boxes,
                                                                               'id') and yolo_results.boxes.id is not None else None

        self.last_valid_detections = []

        for i, (box, conf, class_id) in enumerate(zip(boxes, confidences, class_ids)):
            if conf < self.conf_threshold or not self.is_allowed_class(class_id):
                continue

            yolo_track_id = track_ids[i] if track_ids is not None else i
            sequential_track_id = self.get_sequential_track_id(yolo_track_id)

            # Store detection with smoothed bbox
            smoothed_box = self.smooth_bbox(sequential_track_id, box.tolist())

            detection_data = {
                'box': smoothed_box,
                'confidence': conf,
                'class_id': class_id,
                'sequential_track_id': sequential_track_id,
                'yolo_track_id': yolo_track_id
            }

            self.last_valid_detections.append(detection_data)

    def draw_tracks_with_persistence(self, frame, results, frame_count):
        """Draw tracks with persistence to avoid blinking during frame skipping"""
        # Check if we should use current detections or last valid ones
        detection_age = frame_count - self.detection_frame_count
        use_last_detections = (results is None or results[0].boxes is None) and detection_age <= self.max_detection_age

        if use_last_detections and self.last_valid_detections:
            # Use stored detections for visualization
            return self.draw_stored_detections(frame)
        elif results is not None and results[0].boxes is not None:
            # Use current detections and update stored ones
            self.update_last_valid_detections(results[0])
            self.detection_frame_count = frame_count
            return self.draw_current_detections(frame, results[0])
        else:
            # No valid detections available
            return frame

    def draw_stored_detections(self, frame):
        """Draw bounding boxes using stored detection data with stylish red design"""
        red_color = (0, 0, 255)  # Bright red in BGR format
        red_dark = (0, 0, 180)  # Darker red for accents

        for detection in self.last_valid_detections:
            box = detection['box']
            conf = detection['confidence']
            class_id = detection['class_id']
            sequential_track_id = detection['sequential_track_id']
            x1, y1, x2, y2 = map(int, box)
            center_x = x1 + (x2 - x1) / 2
            center_y = y1 + (y2 - y1) / 2

            # Check ROI
            if self.roi_x1 < center_x < self.roi_x2 and self.roi_y1 < center_y < self.roi_y2:
                generic_class_name = self.get_generic_class_name(class_id)

                # Draw stylish red bounding box with corner accents
                # Main bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), red_color, 3)

                # Corner accents for style
                corner_length = 20
                corner_thickness = 5
                # Top-left corner
                cv2.line(frame, (x1, y1), (x1 + corner_length, y1), red_dark, corner_thickness)
                cv2.line(frame, (x1, y1), (x1, y1 + corner_length), red_dark, corner_thickness)
                # Top-right corner
                cv2.line(frame, (x2, y1), (x2 - corner_length, y1), red_dark, corner_thickness)
                cv2.line(frame, (x2, y1), (x2, y1 + corner_length), red_dark, corner_thickness)
                # Bottom-left corner
                cv2.line(frame, (x1, y2), (x1 + corner_length, y2), red_dark, corner_thickness)
                cv2.line(frame, (x1, y2), (x1, y2 - corner_length), red_dark, corner_thickness)
                # Bottom-right corner
                cv2.line(frame, (x2, y2), (x2 - corner_length, y2), red_dark, corner_thickness)
                cv2.line(frame, (x2, y2), (x2, y2 - corner_length), red_dark, corner_thickness)

                # Stylish label with gradient-like effect
                label = f"ID:{sequential_track_id} {generic_class_name} {conf:.2f}"
                (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.7, 2)
                label_y = max(y1, label_height + 15)

                # Background with rounded effect (multiple rectangles for gradient-like appearance)
                cv2.rectangle(frame, (x1, label_y - label_height - 15), (x1 + label_width + 10, label_y), red_dark, -1)
                cv2.rectangle(frame, (x1 + 2, label_y - label_height - 13), (x1 + label_width + 8, label_y - 2),
                              red_color, -1)

                # Text with shadow effect
                cv2.putText(frame, label, (x1 + 4, label_y - 7), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 3)  # Shadow
                cv2.putText(frame, label, (x1 + 3, label_y - 8), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255),
                            2)  # Main text

        return frame

    def draw_current_detections(self, frame, yolo_results):
        """Draw bounding boxes using current YOLO detection results with stylish red design"""
        boxes = yolo_results.boxes.xyxy.cpu().numpy()
        confidences = yolo_results.boxes.conf.cpu().numpy()
        class_ids = yolo_results.boxes.cls.cpu().numpy().astype(int)
        track_ids = yolo_results.boxes.id.cpu().numpy().astype(int) if hasattr(yolo_results.boxes,
                                                                               'id') and yolo_results.boxes.id is not None else None

        red_color = (0, 0, 255)  # Bright red in BGR format
        red_dark = (0, 0, 180)  # Darker red for accents

        for i, (box, conf, class_id) in enumerate(zip(boxes, confidences, class_ids)):
            if conf < self.conf_threshold or not self.is_allowed_class(class_id):
                continue

            yolo_track_id = track_ids[i] if track_ids is not None else i
            sequential_track_id = self.get_sequential_track_id(yolo_track_id)
            smoothed_box = self.smooth_bbox(sequential_track_id, box.tolist())
            x1, y1, x2, y2 = map(int, smoothed_box)
            center_x = x1 + (x2 - x1) / 2
            center_y = y1 + (y2 - y1) / 2

            if self.roi_x1 < center_x < self.roi_x2 and self.roi_y1 < center_y < self.roi_y2:
                self.save_cropped_object(frame, sequential_track_id, class_id, box, conf)
                generic_class_name = self.get_generic_class_name(class_id)

                # Draw stylish red bounding box with corner accents
                # Main bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), red_color, 3)

                # Corner accents for style
                corner_length = 20
                corner_thickness = 5
                # Top-left corner
                cv2.line(frame, (x1, y1), (x1 + corner_length, y1), red_dark, corner_thickness)
                cv2.line(frame, (x1, y1), (x1, y1 + corner_length), red_dark, corner_thickness)
                # Top-right corner
                cv2.line(frame, (x2, y1), (x2 - corner_length, y1), red_dark, corner_thickness)
                cv2.line(frame, (x2, y1), (x2, y1 + corner_length), red_dark, corner_thickness)
                # Bottom-left corner
                cv2.line(frame, (x1, y2), (x1 + corner_length, y2), red_dark, corner_thickness)
                cv2.line(frame, (x1, y2), (x1, y2 - corner_length), red_dark, corner_thickness)
                # Bottom-right corner
                cv2.line(frame, (x2, y2), (x2 - corner_length, y2), red_dark, corner_thickness)
                cv2.line(frame, (x2, y2), (x2, y2 - corner_length), red_dark, corner_thickness)

                # Stylish label with gradient-like effect
                label = f"ID:{sequential_track_id} {generic_class_name} {conf:.2f}"
                (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.7, 2)
                label_y = max(y1, label_height + 15)

                # Background with rounded effect (multiple rectangles for gradient-like appearance)
                cv2.rectangle(frame, (x1, label_y - label_height - 15), (x1 + label_width + 10, label_y), red_dark, -1)
                cv2.rectangle(frame, (x1 + 2, label_y - label_height - 13), (x1 + label_width + 8, label_y - 2),
                              red_color, -1)

                # Text with shadow effect
                cv2.putText(frame, label, (x1 + 4, label_y - 7), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 3)  # Shadow
                cv2.putText(frame, label, (x1 + 3, label_y - 8), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255),
                            2)  # Main text

        return frame

    def _save_to_db(self, item):
        try:
            (object_id, vehicle_number, number_plate_color, country, image_base64,
             is_recognized, timestamp, status, alarm, acknowledgment_message,
             acknowledgment_time, object_type) = item

            conn = pyodbc.connect(
                r'DRIVER={ODBC Driver 17 for SQL Server};'
                r'SERVER=ITDT23;'
                r'DATABASE=ZONE_INTRUSION_DB;'
                r'UID=sa;'
                r'PWD=root1234;',
                autocommit=True
            )
            cursor = conn.cursor()
            insert_query = """
                           INSERT INTO [ZONE_INTRUSION_DB].[dbo].[event_details]
                           ([vehicle_id], [vehicle_number], [number_plate_color], [country],
                               [vehicle_img], [number_plate_img], [is_recognized], [time],
                               [status], [alarm], [acknowledgment_message], [acknowledgment_time], [object_type], [camera_name])
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                           """
            cursor.execute(insert_query,
                           int(object_id),
                           vehicle_number,
                           number_plate_color,
                           country,
                           image_base64,
                           image_base64,
                           is_recognized,
                           timestamp,
                           status,
                           alarm,
                           acknowledgment_message,
                           acknowledgment_time,
                           object_type,
                           current_camera_details.get("camera_name", "N/A")
                           )
            cursor.close()
            conn.close()
            print(f"Successfully saved track ID {object_id} ({object_type}) to database")
        except Exception as e:
            print(f"Database write error: {e}")

    def update_hits(self, track_id):
        found = False
        for track in self.track_hits_list:
            if track["track_id"] == track_id:
                found = True
                new_hits = int(track["hits"]) + 1
                track["hits"] = new_hits
                return True
        if not found:
            self.add_track(track_id)
        return False

    def delete_track(self, track_id):
        for i, track in enumerate(self.track_hits_list):
            if track["track_id"] == track_id:
                del self.track_hits_list[i]
                return True
        return False

    def add_track(self, track_id, hits=1):
        self.track_hits_list.append({"track_id": track_id, "hits": hits})

    def get_track(self, track_id):
        for track in self.track_hits_list:
            if track["track_id"] == track_id:
                return track
        return None

    def setup_class_filter(self):
        coco_classes = {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus',
            6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant',
            11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat',
            16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear',
            22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag',
            27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard',
            32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove',
            36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle',
            40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl',
            46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli',
            51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair',
            57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet',
            62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone',
            68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator',
            73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear',
            78: 'hair drier', 79: 'toothbrush'
        }

        self.category_mappings = {
            'person': [0],
            'animal': [14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
            'vehicle': [1, 2, 3, 5, 6, 7, 8]
        }

        self.class_id_to_category = {}
        for category, class_ids in self.category_mappings.items():
            for class_id in class_ids:
                self.class_id_to_category[class_id] = category

        if self.target_classes:
            self.allowed_class_ids = set()
            for target_class in self.target_classes:
                if target_class.lower() in self.category_mappings:
                    self.allowed_class_ids.update(self.category_mappings[target_class.lower()])
            print(f"Filtering for classes: {self.target_classes}")
            print(f"Allowed class IDs: {sorted(self.allowed_class_ids)}")
            detected_classes = [coco_classes[class_id] for class_id in sorted(self.allowed_class_ids) if
                                class_id in coco_classes]
            print(f"Will detect: {detected_classes}")
        else:
            self.allowed_class_ids = None
            print("No class filtering - detecting all objects")

    def is_allowed_class(self, class_id):
        if self.allowed_class_ids is None:
            return True
        return class_id in self.allowed_class_ids

    def get_generic_class_name(self, class_id):
        return self.class_id_to_category.get(class_id, self.model.names[class_id])

    def smooth_bbox(self, track_id, bbox, alpha=0.7):
        if track_id not in self.sequential_track_history:
            self.sequential_track_history[track_id] = [bbox]
            return bbox

        prev_bbox = self.sequential_track_history[track_id][-1]
        smoothed_bbox = [alpha * bbox[i] + (1 - alpha) * prev_bbox[i] for i in range(4)]
        self.sequential_track_history[track_id].append(smoothed_bbox)

        if len(self.sequential_track_history[track_id]) > self.max_history_length:
            self.sequential_track_history[track_id].pop(0)

        return smoothed_bbox

    def draw_tracks(self, frame, results, frame_count):
        if results[0].boxes is None:
            return frame

        boxes = results[0].boxes.xyxy.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()
        class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
        track_ids = results[0].boxes.id.cpu().numpy().astype(int) if hasattr(results[0].boxes, 'id') and results[
            0].boxes.id is not None else None

        category_colors = {
            'person': (255, 0, 0),
            'animal': (0, 255, 0),
            'vehicle': (0, 0, 255),
            'default': (255, 255, 0)
        }

        for i, (box, conf, class_id) in enumerate(zip(boxes, confidences, class_ids)):
            if conf < self.conf_threshold or not self.is_allowed_class(class_id):
                continue

            yolo_track_id = track_ids[i] if track_ids is not None else i
            sequential_track_id = self.get_sequential_track_id(yolo_track_id)
            smoothed_box = self.smooth_bbox(sequential_track_id, box.tolist())
            x1, y1, x2, y2 = map(int, smoothed_box)
            center_x = x1 + (x2 - x1) / 2
            center_y = y1 + (y2 - y1) / 2
            if self.roi_x1 < center_x < self.roi_x2 and self.roi_y1 < center_y < self.roi_y2:
                self.save_cropped_object(frame, sequential_track_id, class_id, box, conf)

                generic_class_name = self.get_generic_class_name(class_id)
                color = category_colors.get(generic_class_name, category_colors['default'])
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                label = f"ID:{sequential_track_id} {generic_class_name} {conf:.2f}"
                (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                label_y = max(y1, label_height + 10)
                cv2.rectangle(frame, (x1, label_y - label_height - 10), (x1 + label_width, label_y), color, -1)
                cv2.putText(frame, label, (x1, label_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        return frame

    def save_cropped_object(self, frame, object_id, class_name, bbox, confidence):
        self.update_hits(object_id)
        hits = self.get_track(object_id)
        if hits["hits"] < 25:
            return
        else:
            self.delete_track(object_id)
            if object_id in self.saved_object_images:
                return

            x1, y1, x2, y2 = [int(max(0, x)) for x in bbox]
            frame_height, frame_width = frame.shape[:2]
            x1 = min(x1, frame_width - 1)
            x2 = min(x2, frame_width)
            y1 = min(y1, frame_height - 1)
            y2 = min(y2, frame_height)

            min_size = 30
            if x2 <= x1 or y2 <= y1 or (x2 - x1) < min_size or (y2 - y1) < min_size:
                print(f"Invalid crop dimensions for object {object_id}: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
                return

            cropped_image = self.copy_frame[y1:y2, x1:x2]
            if cropped_image.size == 0:
                print(f"Empty cropped image for object {object_id}")
                return

            current_height, current_width = cropped_image.shape[:2]
            target_width = 235
            target_height = 185

            resized_image = cv2.resize(cropped_image, (target_width, target_height), interpolation=cv2.INTER_CUBIC)
            _, img_encoded = cv2.imencode('.jpg', resized_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            image_base64 = base64.b64encode(img_encoded).decode('utf-8')

            # Get the generic object type using the existing method
            object_type = self.get_generic_class_name(class_name)

            vehicle_number = "N/A"
            number_plate_color = "white"
            country = "IN"
            is_recognized = 1
            status = "Alarm"
            alarm = 0
            acknowledgment_message = "None"
            acknowledgment_time = datetime.now()
            timestamp = acknowledgment_time

            self.db_queue.put((
                object_id, vehicle_number, number_plate_color, country, image_base64,
                is_recognized, timestamp, status, alarm, acknowledgment_message, acknowledgment_time, object_type
            ))

            self.saved_object_images.add(object_id)
            print(
                f"Saved resized cropped object {object_id} ({object_type}) - Original: {current_width}x{current_height}, Resized: {target_width}x{target_height}")

    def reconnect_video_source(self, video_path, max_retries=5, retry_delay=2):
        for attempt in range(max_retries):
            print(f"Reconnecting to {video_path} (Attempt {attempt + 1}/{max_retries})...")
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                print("Successfully reconnected to video source")
                if video_path.lower().startswith(('rtsp://', 'rtmp://', 'http://')):
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    for _ in range(5):
                        cap.read()
                return cap
            else:
                print(f"Failed to connect. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        print(f"Error: Could not reconnect to {video_path} after {max_retries} attempts")
        return None

    def cleanup_all_track_videos(self):
        """Finalize all remaining track videos on shutdown"""
        print("Finalizing all remaining track videos...")
        for track_id in list(self.track_video_writers.keys()):
            self.finalize_track_video(track_id)
        print("All track videos finalized.")

    def check_roi_change(self,new):
        for a, b in zip(self.points, new):
            if a != b:
                print("Mismatch:", a, b)
                return True
        return False

    def process_video(self, video_path, output_path=None, display=True):
        is_rtsp = video_path.lower().startswith(('rtsp://', 'rtmp://', 'http://'))
        max_retries = 5
        retry_delay = 2

        for attempt in range(max_retries):
            print(f"Attempting to connect to {video_path} (Attempt {attempt + 1}/{max_retries})...")
            cap = cv2.VideoCapture(video_path)

            if cap.isOpened():
                print("Successfully connected to video source")
                break
            else:
                print(f"Failed to open video source: {video_path}")
                cap.release()
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                continue
        else:
            print(f"Error: Could not open video source {video_path} after {max_retries} attempts")
            return

        if is_rtsp:
            print("RTSP stream detected - applying optimizations...")
            cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
            cap.set(cv2.CAP_PROP_FPS, 30)
            try:
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            except:
                print("Warning: Could not set MJPG codec")
            for _ in range(5):
                cap.read()

        fps = int(cap.get(cv2.CAP_PROP_FPS)) if not is_rtsp else 30
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        height, width = (original_height, original_width)

        self.roi_x1 = int((current_camera_details["roi_start_width"] / 100) * width)
        self.roi_x2 = int((current_camera_details["roi_end_width"] / 100) * width)
        self.roi_y1 = int((current_camera_details["roi_start"] / 100) * height)
        self.roi_y2 = int((current_camera_details["roi_end"] / 100) * height)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if not is_rtsp else -1

        print(f"Video Properties:")
        print(f"  Source type: {'RTSP Stream' if is_rtsp else 'Video File'}")
        print(f"  Original Resolution: {original_width}x{original_height}")
        print(f"  FPS: {fps}")
        if not is_rtsp:
            print(f"  Total Frames: {total_frames}")

        if output_path and not is_rtsp:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps)
        else:
            out = None

        self.frame_count = 0
        start_time = time.time()
        processing_times = []
        last_frame_time = time.time()
        consecutive_failures = 0
        max_failures = 3

        print(f"\nStarting video processing...")
        print("Press 'q' to quit, 'p' to pause/resume")

        paused = False
        while True:
            if not paused:
                if video_path != current_camera_details.get("rtsp_url", "N/A") or self.check_roi_change(
                        (self.roi_x1, self.roi_y1, self.roi_x2, self.roi_y2)):
                    print("Video source changed, reconnecting...")
                    cap.release()
                    new_url = current_camera_details.get("rtsp_url", "N/A")
                    new_cap = self.reconnect_video_source(new_url)

                    if new_cap:
                        cap = new_cap
                        video_path = new_url  # Update current path
                        ret, frame = cap.read()
                        height, width, _ = frame.shape
                        self.roi_x1 = int((current_camera_details["roi_start_width"] / 100) * width)
                        self.roi_x2 = int((current_camera_details["roi_end_width"] / 100) * width)
                        self.roi_y1 = int((current_camera_details["roi_start"] / 100) * height)
                        self.roi_y2 = int((current_camera_details["roi_end"] / 100) * height)
                        self.points = (self.roi_x1, self.roi_y1, self.roi_x2, self.roi_y2)
                        continue
                    else:
                        print("Failed to switch video source. Exiting processing loop.")
                        break

                ret, frame = cap.read()
                if not ret:
                    consecutive_failures += 1
                    if is_rtsp:
                        print(f"Frame read failure {consecutive_failures}/{max_failures}")
                        if consecutive_failures >= max_failures:
                            print("Too many consecutive failures, attempting to reconnect...")
                            cap.release()
                            time.sleep(1)
                            cap = cv2.VideoCapture(video_path)
                            if is_rtsp:
                                cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
                                cap.set(cv2.CAP_PROP_FPS, 30)
                                for _ in range(5):
                                    cap.read()
                            consecutive_failures = 0
                            continue
                        time.sleep(0.05)
                        continue
                    else:
                        break
                else:
                    consecutive_failures = 0

                self.roi_x1 = int((current_camera_details["roi_start_width"] / 100) * width)
                self.roi_x2 = int((current_camera_details["roi_end_width"] / 100) * width)
                self.roi_y1 = int((current_camera_details["roi_start"] / 100) * height)
                self.roi_y2 = int((current_camera_details["roi_end"] / 100) * height)

                # SOLUTION: Store the original frame BEFORE drawing ROI rectangle
                # This ensures cropped objects don't include the ROI line
                self.copy_frame = frame.copy()  # Clean frame for cropping

                # Draw ROI rectangle on the display frame (not the copy used for cropping)
                cv2.rectangle(frame, (self.roi_x1, self.roi_y1), (self.roi_x2, self.roi_y2), (0, 255, 0), 2)

                # Process frame directly (removed separate thread/queue)
                annotated_frame = self._process_frame(frame, self.frame_count)

                frame_time = time.time() - last_frame_time
                last_frame_time = time.time()
                processing_times.append(frame_time)
                if len(processing_times) > 20:
                    processing_times.pop(0)

                frame_info = f"RTSP Stream | Frame: {self.frame_count}" if is_rtsp else f"Frame: {self.frame_count + 1}/{total_frames}"
                cv2.putText(annotated_frame, frame_info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                current_fps = 1.0 / frame_time if frame_time > 0 else 0
                avg_fps = len(processing_times) / sum(processing_times) if processing_times else 0
                fps_text = f"FPS: {current_fps:.1f} | Avg: {avg_fps:.1f}"
                cv2.putText(annotated_frame, fps_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                if is_rtsp:
                    latency = (time.time() - last_frame_time) * 1000
                    latency_text = f"Latency: {latency:.1f}ms"
                    cv2.putText(annotated_frame, latency_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (0, 255, 255), 2)
                    status_color = (0, 255, 0) if consecutive_failures == 0 else (0, 165, 255)
                    status_text = "Connected" if consecutive_failures == 0 else "Retrying..."
                    cv2.putText(annotated_frame, f"Status: {status_text}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                status_color, 2)

                if out and not is_rtsp:
                    out.write(annotated_frame)

                try:
                    shared_queue.put(annotated_frame, timeout=0.01)
                except:
                    pass

                self.frame_count += 1
                if self.frame_count % 150 == 0:
                    if is_rtsp:
                        print(
                            f"RTSP Stream | Frames: {self.frame_count} | Avg FPS: {avg_fps:.1f} | Latency: {latency:.1f}ms")
                    else:
                        progress = (self.frame_count / total_frames) * 100
                        print(f"Progress: {progress:.1f}% | Avg FPS: {avg_fps:.1f}")

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                paused = not paused
                print(f"{'Paused' if paused else 'Resumed'}")

        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()

        total_time = time.time() - start_time
        if is_rtsp:
            print(f"\nRTSP Stream Processing Complete!")
            print(f"Total time: {total_time:.2f}s")
            print(f"Total frames processed: {self.frame_count}")
            print(f"Average FPS: {self.frame_count / total_time:.2f}" if total_time > 0 else "Average FPS: N/A")
        else:
            print(f"\nProcessing Complete!")
            print(f"Total time: {total_time:.2f}s")
            print(f"Total frames processed: {self.frame_count}")
            print(f"Average FPS: {self.frame_count / total_time:.2f}" if total_time > 0 else "Average FPS: N/A")
            if output_path:
                print(f"Output saved to: {output_path}")



def main():
    video_path = current_camera_details.get("rtsp_url","N/A")
    output_path = None
    tracker = YOLOTracker(
        model_path='yolo11l.pt',
        conf_threshold=0.4,
        iou_threshold=0.7,
        target_classes=['person', 'animal', 'vehicle']
    )
    try:
        tracker.process_video(
            video_path=video_path,
            output_path=output_path,
            display=True
        )
    except Exception as e:
        print(f"Error processing video: {e}")