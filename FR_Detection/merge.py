#
# import ast
# import logging
# import re
#
# import cv2
# import torch
# import numpy as np
# import time
# import threading
# import queue
# import base64
# from io import BytesIO
# from PIL import Image,ImageEnhance
# import pyodbc
# from facenet_pytorch import MTCNN, InceptionResnetV1
# from ultralytics import YOLO
# from onvif import ONVIFCamera
# from collections import OrderedDict
# from sklearn.metrics.pairwise import cosine_similarity
# from Core.face_image import fetch_first_camera
# from shared_queue import shared_queue, update_camera_details, current_camera_details,live_feed_queue,locked_ID
#
#
# tracking_dict = OrderedDict()
# MAX_RECENT = 50  # only keep last 50 unique entries
#
# DATABASE_HOST = 'ITDT14'
# DATABASE_NAME = 'FR_DB_NEW'
# DEVICE = 'cuda' #if torch.cuda.is_available() else 'cpu'
# lock = threading.Lock()
# MODEL_PATH = "Resources/headtrackeryolo11.pt"
# RTSP_LINK = ""
# cap = None
# CONF_THRESHOLD = 0.45
# IOU_THRESHOLD = 0.3
# TARGET_CLASS = 0
# TARGET_FPS = 10
# FRAME_DELAY = 1 / TARGET_FPS
# ROI = (0, 0, 1200, 1000)
#
# # === Load Model ===
# model = YOLO(MODEL_PATH)
# model.fuse()
#
# # === Globals ===
# frame_queue = queue.Queue(maxsize=5)
# stop_thread = False
# hidden_tracks = {}
# cropped_faces = []
# known_face_embeddings = []
# known_face_names = []
# custom_id_map = {}
# next_custom_id = 1
# event_log = {}
# flag = False
# db_connection = None
#
# EXIT_TIMEOUT = 3
# track_last_seen = {}
#
# active_tracks = set()
#
# dict_db_details = {
#     "str_server": "ITDT14",
#     "str_username": "sa",
#     "str_password": "root1234",
#     "str_db_name": "FR_DB_NEW",
#     "str_user_table": "user_details",
#     "str_person_table": "person_details",
#     "str_person_tracking_table": "person_tracking_details",
#     "str_event_details_table": "event_details",
#     "str_camera_details": "Camera_Details",
#     "str_persion_tabel": "personregister"
# }
#
#
# # Models
# mtcnn = MTCNN(keep_all=True,min_face_size=80,thresholds=[0.7,0.8,0.9] ,factor=0.9,device= 'cuda' )
# resnet = InceptionResnetV1(pretrained='vggface2').eval().to(DEVICE)
#
# ptz_enabled = True
# # ptz_camera_ip = '10.30.30.49'
# # ptz_camera_port = 80
# # ptz_camera_user = 'admin'
# # ptz_camera_pass = 'Admin@123'
# onvif_cam = None
# media_service = None
# ptz_service = None
# profile_token = None
#
#
# # PTZ Initialization
# def initialize_ptz(ptz_camera_ip, ptz_camera_port, ptz_camera_user, ptz_camera_pass):
#     global onvif_cam, media_service, ptz_service, profile_token
#     try:
#         onvif_cam = ONVIFCamera(ptz_camera_ip, ptz_camera_port, ptz_camera_user, ptz_camera_pass)
#         media_service = onvif_cam.create_media_service()
#         ptz_service = onvif_cam.create_ptz_service()
#         profiles = media_service.GetProfiles()
#         profile_token = profiles[0].token
#
#     except Exception as e:
#         print(f"[ERROR] PTZ initialization failed: {e}")
#
#
# def move_camera(dx, dy):
#     global ptz_service, profile_token
#     try:
#         request = ptz_service.create_type('ContinuousMove')
#         request.ProfileToken = profile_token
#         request.Velocity = ptz_service.GetStatus({'ProfileToken': profile_token}).Position
#         request.Velocity.PanTilt.x = dx
#         request.Velocity.PanTilt.y = dy
#         ptz_service.ContinuousMove(request)
#         time.sleep(0.2)
#         ptz_service.Stop({'ProfileToken': profile_token})
#     except Exception as e:
#         print(f"[ERROR] PTZ move failed: {e}")
#
#
# def ptz_follow_target(box, frame_shape, ptz_service, profile_token):
#     frame_height, frame_width = frame_shape
#     x1, y1, x2, y2 = box
#     box_center_x = (x1 + x2) / 2
#     box_center_y = (y1 + y2) / 2
#
#     offset_x = (box_center_x - frame_width / 2) / frame_width
#     offset_y = (box_center_y - frame_height / 2) / frame_height
#
#     pan_speed = 0.4
#     tilt_speed = 0.4
#     threshold = 0.05
#
#     pan = tilt = 0
#     if abs(offset_x) > threshold:
#         pan = pan_speed if offset_x > 0 else -pan_speed
#     if abs(offset_y) > threshold:
#         tilt = -tilt_speed if offset_y > 0 else tilt_speed
#
#     if pan != 0 or tilt != 0:
#         request = ptz_service.create_type('ContinuousMove')
#         request.ProfileToken = profile_token
#         request.Velocity = request.Velocity or {}
#         request.Velocity.PanTilt = {'x': pan, 'y': tilt}
#         request.Velocity.Zoom = {'x': 0}
#         ptz_service.ContinuousMove(request)
#         time.sleep(0.3)
#         ptz_service.Stop({'ProfileToken': profile_token})
#
# def update_tracking_dict(track_id, name):
#     global tracking_dict
#
#     if track_id in tracking_dict:
#         existing_name = tracking_dict[track_id]
#
#         if existing_name == "Unknown" and name != "Unknown":
#             tracking_dict[track_id] = name
#             return "updated"
#         elif existing_name == "Unknown" and name == "Unknown":
#             tracking_dict[track_id] = name
#             return "updated"
#         elif existing_name == name or (existing_name != "Unknown" and name != "Unknown"):
#             return "skip"
#         elif existing_name != "Unknown" and name == "Unknown":
#             return "skip"
#     else:
#         # Add new entry
#         tracking_dict[track_id] = name
#
#         # Maintain only last 50 entries
#         if len(tracking_dict) > MAX_RECENT:
#             tracking_dict.popitem(last=False)
#         return "insert"
#
#
#
# # DB Functions
# def connect_db():
#     global db_connection
#     try:
#         conn_str = f'Driver={{ODBC Driver 17 for SQL Server}};Server={DATABASE_HOST};DATABASE={DATABASE_NAME};UID=sa;PWD=root1234'
#         db_connection = pyodbc.connect(conn_str, autocommit=True)
#     except Exception as e:
#         print(f"DB Connection Error: {e}")
#
# def init_db():
#     cursor = db_connection.cursor()
#     cursor.execute(f"SELECT database_id FROM sys.databases WHERE name = '{DATABASE_NAME}'")
#     if not cursor.fetchone():
#         cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
#         db_connection.commit()
#
#     print(" Tables ready.")
#
# def close_db():
#     if db_connection:
#         db_connection.close()
#         print(" DB connection closed.")
#
# def get_next_tracking_id():
#     global next_custom_id
#     cursor = db_connection.cursor()
#     cursor.execute("SELECT ISNULL(MAX(TrackingID), 0) FROM event_details")
#     next_custom_id = cursor.fetchone()[0] + 1
#
#
# # def load_known_faces():
# #     path = "D:\\face_recogniton_Mamali\\saved_images\\New folder"
# #     for person_name in os.listdir(path):
# #         person_folder = os.path.join(path, person_name)
# #         if os.path.isdir(person_folder):
# #             embeddings = []
# #             for file in os.listdir(person_folder):
# #                 if file.lower().endswith(('.jpg','jfif' ,'.png')):
# #                     img_path = os.path.join(person_folder, file)
# #                     print("Reading Image File: " + img_path)
# #                     img = Image.open(img_path).convert("RGB")
# #                     aligned = mtcnn(img)
# #                     if aligned is not None:
# #                         if aligned.ndim == 3:
# #                             aligned = aligned.unsqueeze(0)
# #                         embedding = resnet(aligned.to(DEVICE)).detach().cpu().numpy()
# #                         embeddings.append(embedding[0])
# #             if embeddings:
# #                 mean_embedding = np.mean(embeddings, axis=0)
# #                 known_face_embeddings.append(mean_embedding)
# #                 known_face_names.append(person_name)
# #     save_known_faces()
#
#
# def load_known_faces_from_db():
#     # Connect to SQL Server
#     connection = pyodbc.connect(
#         f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details['str_server']};UID={dict_db_details['str_username']};PWD={dict_db_details['str_password']}",
#         autocommit=True)
#     cursor = connection.cursor()
#
#     # Fetch person info and mean_image strings
#     query = """
#         SELECT [id], [full_name], [mean_image]
#         FROM [FR_DB_NEW].[dbo].[personregister]
#     """
#     cursor.execute(query)
#     rows = cursor.fetchall()
#
#     for row in rows:
#         person_id = row.id
#         person_name = row.full_name
#         mean_str = row.mean_image
#
#         try:
#             # Convert string to Python list safely
#             mean_list = ast.literal_eval(mean_str)
#             mean_embedding = np.array(mean_list, dtype=np.float32)
#
#             # Append to memory
#             known_face_embeddings.append(mean_embedding)
#             known_face_names.append((person_id, person_name))
#         except Exception as e:
#             print(f"Error parsing mean_image for {person_name}: {e}")
#
#     cursor.close()
#     connection.close()
#
#
# def update_person_mean(id , new_name , new_encode):
#     global known_face_embeddings,known_face_names
#     try:
#         # Find the index of the tuple containing the ID
#         index = next((i for i, (person_id, name,) in enumerate(known_face_names) if person_id == id), None)
#
#         if index is None:
#             print(f"ID '{id}' not found in known faces.")
#             return False
#
#         # Update name in the known_face_names list
#         old_name = known_face_names[index][1]
#         known_face_names[index] = (id, new_name)
#         if isinstance(new_encode, np.ndarray):
#             known_face_embeddings[index] = new_encode
#
#         print(f"Updated local name from '{old_name}' to '{new_name}' for ID {id}.")
#         return True
#
#     except Exception as e:
#         print(f"Unexpected error in update_person_name: {str(e)}")
#         return False
#
#
# def add_person_mean(id , new_name , new_encode):
#     global known_face_embeddings, known_face_names
#     try:
#         known_face_names.append((id,new_name))
#         known_face_embeddings.append(new_encode)
#
#     except Exception as e:
#         print(f"Unexpected error in update_person_name: {str(e)}")
#         return False
#
#
# def delete_person(id):
#     global known_face_embeddings, known_face_names
#     try:
#         index = next((i for i, (person_id, _) in enumerate(known_face_names) if person_id == id), None)
#         if index is None:
#             print(f"ID '{id}' not found in known faces.")
#             return False
#
#         known_face_embeddings.pop(index)
#         removed_name = known_face_names.pop(index)[1]
#         print(f"Deleted {removed_name} (ID: {id}) from known faces.")
#
#     except Exception as e:
#         print(f"Error in delete_person: {str(e)}")
#         return False
#
#
# def perform_recognition_for_validation(embedding,threshold = 0.6):
#     name = "Unknown"
#
#     if known_face_embeddings:
#         scores = cosine_similarity([embedding], known_face_embeddings)[0]
#         best_match_idx = np.argmax(scores)
#         max_sim = scores[best_match_idx]
#
#         best_embedding = known_face_embeddings[best_match_idx]
#         dist = np.linalg.norm(embedding - best_embedding)
#
#         if max_sim > threshold and dist < 0.65:
#             id, name = known_face_names[best_match_idx]
#             return name, True, id
#
#     return "",False, 0
#
#
#
# def enhance_image(img):
#     img = ImageEnhance.Contrast(img).enhance(1.3)
#     img = ImageEnhance.Sharpness(img).enhance(2.0)
#     return img
#
#
# # Custom ID map
# def get_custom_id(original_id):
#     global next_custom_id, custom_id_map
#     if original_id not in custom_id_map:
#         custom_id_map[original_id] = next_custom_id
#         next_custom_id += 1
#     return custom_id_map[original_id]
#
#
#
# # === Utils ===
# def calculate_iou(box1, box2):
#     xA = max(box1[0], box2[0])
#     yA = max(box1[1], box2[1])
#     xB = min(box1[2], box2[2])
#     yB = min(box1[3], box2[3])
#
#     interArea = max(0, xB - xA) * max(0, yB - yA)
#     box1Area = (box1[2] - box1[0]) * (box1[3] - box1[1])
#     box2Area = (box2[2] - box2[0]) * (box2[3] - box2[1])
#
#     unionArea = box1Area + box2Area - interArea
#     return interArea / unionArea if unionArea != 0 else 0
#
#
# def frame_reader():
#     global flag, RTSP_LINK, cap
#
#     while not flag:
#         new_rtsp_link = current_camera_details.get('rtsp_url', None)
#
#         # Acquire lock to update RTSP safely
#         with lock:
#             if new_rtsp_link and new_rtsp_link != RTSP_LINK:
#                 RTSP_LINK = new_rtsp_link
#                 print(f"RTSP link changed. RestartRTSP_LINKing stream: {RTSP_LINK}")
#
#                 # Release old capture if it exists
#                 if cap is not None:
#                     cap.release()
#                     cap = None  # Ensure old object is cleared
#
#                 # Start new video capture
#                 cap = cv2.VideoCapture(RTSP_LINK, cv2.CAP_FFMPEG)
#                 if not cap.isOpened():
#                     print(f"Failed to open stream: {RTSP_LINK}")
#                     cap = None  # Reset cap if opening fails
#                     continue
#
#         # Ensure cap is valid before reading frames
#         if cap is None or not cap.isOpened():
#             continue  # Wait until a valid RTSP link is set
#
#         ret, frame = cap.read()
#         if not ret or frame is None or frame.size == 0:
#             continue
#
#         if not frame_queue.full():
#
#             frame= cv2.resize(frame,(2560,1440))
#             frame_queue.put(frame)
#     with lock:
#         if cap is not None:
#             cap.release()
#             cap = None
#
# def processFrame():
#     global flag, event_log, known_face_names,known_face_embeddings
#     cursor = db_connection.cursor()
#     cooldown_time = 2
#     last_recognition_time = {}
#
#     while True:
#         if not cropped_faces:
#             time.sleep(0.01)
#             continue
#
#         try:
#             track_id, face_crop = cropped_faces.pop(0)
#             print(f"---------------------Locked ID : {locked_ID}---------------------")
#
#             if face_crop is None or face_crop.size == 0:
#                 continue
#
#             now = time.time()
#             if track_id in last_recognition_time and (now - last_recognition_time[track_id] < cooldown_time):
#                 continue
#             last_recognition_time[track_id] = now
#
#             # Reject too-small faces
#             if face_crop.shape[0] < 100 or face_crop.shape[1] < 100:
#                 continue
#
#             # Resize to help
#             time.sleep(0.1)
#             face_crop_resized = cv2.resize(face_crop, (175, 175))
#             head_crop_rgb = cv2.cvtColor(face_crop_resized, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(head_crop_rgb)
#
#             aligned = mtcnn(img)
#
#             if aligned is None or (isinstance(aligned, list) and not aligned):
#                 continue
#
#             if isinstance(aligned, list):
#                 aligned = aligned[0]
#
#             if aligned.ndim == 3:
#                 aligned = aligned.unsqueeze(0)
#
#             aligned = aligned.to(DEVICE)
#             embedding = resnet(aligned).detach().cpu().numpy()[0]
#             embedding = embedding / np.linalg.norm(embedding)
#
#             name = "Unknown"
#             threshold = 0.6
#
#             if known_face_embeddings:
#                 scores = cosine_similarity([embedding], known_face_embeddings)[0]
#                 best_match_idx = np.argmax(scores)
#                 max_sim = scores[best_match_idx]
#
#                 best_embedding = known_face_embeddings[best_match_idx]
#                 dist = np.linalg.norm(embedding - best_embedding)
#
#                 if max_sim > threshold and dist < 0.65:
#                    id ,name = known_face_names[best_match_idx]
#
#             decision = update_tracking_dict(track_id,name )
#             update_name = False
#             skip_insertion = False
#
#             if decision == "insert":
#                 update_name = False
#             elif decision == "updated":
#                 update_name = True
#             elif decision == "skip":
#                 skip_insertion = True
#
#             timestamp = int(time.time())
#             pil_img = Image.fromarray(cv2.cvtColor(face_crop_resized, cv2.COLOR_BGR2RGB))
#             buffer = BytesIO()
#             pil_img.save(buffer, format="PNG")
#             face_base64 = base64.b64encode(buffer.getvalue()).decode()
#
#             if skip_insertion:
#                continue
#             if update_name:
#                 cursor.execute(
#                     "UPDATE event_details SET captured_img = ?, person_name = ? WHERE TrackingID = ? AND person_name ='Unknown'",
#                     face_base64, name, track_id
#                 )
#                 db_connection.commit()
#             else:
#                 cursor.execute(
#                     "INSERT INTO event_details (TrackingID, captured_img, person_name, start_time) VALUES (?, ?, ?, ?)",
#                     track_id, face_base64, name, timestamp
#                 )
#                 db_connection.commit()
#
#
#         except Exception as e:
#             print(f"[ERROR] in processFrame: {e}")
#             continue
#
#
#
#
# def mainTracker():
#     global next_custom_id
#
#     print("[INFO] Starting detection and tracking...")
#     # Dictionary to store bounding boxes for click detection
#     global bbox_mapping
#     bbox_mapping = {}
#
#     # Flag to indicate if tracking mode is enabled for a specific ID
#     global track_specific_id
#     track_specific_id = None
#
#     try:
#         while True:
#             start_time = time.time()
#
#             try:
#                 frame = frame_queue.get(timeout=1)
#             except queue.Empty:
#                 print("[INFO] Waiting for frame...")
#                 time.sleep(0.01)
#                 continue
#
#             # Validate frame before processing
#             if frame is None or frame.size == 0:
#                 print("[ERROR] Invalid frame received. Skipping...")
#                 continue
#
#             height, width, _ = frame.shape  # Get frame dimensions
#             copied_frame= frame.copy()
#
#             # Calculate ROI boundaries in pixels
#             roi_x1 = int((current_camera_details["roi_start_width"] / 100) * width)
#             roi_x2 = int((current_camera_details["roi_end_width"] / 100) * width)
#             roi_y1 = int((current_camera_details["roi_start_height"] / 100) * height)
#             roi_y2 = int((current_camera_details["roi_end_height"] / 100) * height)
#
#             # Draw the ROI rectangle
#             cv2.rectangle(copied_frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0,0, 255), 5)
#             cv2.putText(copied_frame, "ROI", (roi_x1 + 5, roi_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#
#             x1, y1, x2, y2 = ROI
#
#             cropped_frame = copied_frame
#
#             if cropped_frame is None or cropped_frame.size == 0:
#                 print("[ERROR] Invalid cropped frame. Skipping...")
#                 continue
#
#             # Resize frames to be the same size if necessary
#             if frame.shape[:2] != cropped_frame.shape[:2]:
#                 print("[INFO] Resizing cropped_frame to match original frame size...")
#                 cropped_frame = cv2.resize(cropped_frame, (frame.shape[1], frame.shape[0]))
#
#             try:
#                 # Try to track objects with model
#                 results = model.track(
#                     source=cropped_frame,
#                     persist=True,
#                     stream=False,
#                     conf=CONF_THRESHOLD,
#                     iou=IOU_THRESHOLD,
#                     classes=[TARGET_CLASS],
#                     tracker="botsort.yaml"
#                 )
#             except Exception as e:
#                 print(f"[ERROR] model.track failed: {e}")
#                 continue  # Skip this frame and continue processing the next one
#
#             boxes_data = []
#             # Clear bbox_mapping for this frame
#             bbox_mapping.clear()
#             for result in results:
#                 if result.boxes is not None:
#                     for box in result.boxes:
#                         x1_crop, y1_crop, x2_crop, y2_crop = map(int, box.xyxy[0].tolist())
#                         conf = float(box.conf[0])
#                         orig_id = int(box.id[0]) if box.id is not None else -1
#
#                         track_id = get_custom_id(orig_id)
#                         x1_orig = x1 + x1_crop
#                         y1_orig = y1 + y1_crop
#                         x2_orig = x1 + x2_crop
#                         y2_orig = y1 + y2_crop
#
#                         width = x2_orig - x1_orig
#                         height = y2_orig - y1_orig
#
#                         # Check if object is within ROI
#                         if x1_orig >= roi_x1 and x2_orig <= roi_x2 and y1_orig >= roi_y1 and y2_orig <= roi_y2:
#                             if width * height >= 800:
#                                 boxes_data.append({
#                                     "track_id": track_id,
#                                     "bbox": (x1_orig, y1_orig, x2_orig, y2_orig),
#                                     "conf": conf,
#                                     "area": width * height
#                                 })
#
#             visible_track_ids = set()
#             hidden_track_ids = set()
#
#             # Track object visibility and identify new tracks
#             for i in range(len(boxes_data)):
#                 box_i = boxes_data[i]
#                 is_hidden = False
#                 for j in range(len(boxes_data)):
#                     if i == j:
#                         continue
#                     box_j = boxes_data[j]
#                     iou = calculate_iou(box_i["bbox"], box_j["bbox"])
#                     if iou > 0.4:
#                         if box_i["conf"] < box_j["conf"] or box_i["area"] < box_j["area"]:
#                             is_hidden = True
#                             break
#                 track_id = box_i["track_id"]
#                 if not is_hidden:
#                     visible_track_ids.add(track_id)
#                     track_last_seen[track_id] = time.time()
#
#                     if track_id not in active_tracks:
#                         print(f"[ENTRY] ID {track_id}")
#                         active_tracks.add(track_id)
#                 else:
#                     hidden_track_ids.add(track_id)
#
#             # Process visible tracks and draw boxes
#             for track in boxes_data:
#                 track_id = track["track_id"]
#                 if track_id in visible_track_ids:
#                     x1_draw, y1_draw, x2_draw, y2_draw = track["bbox"]
#                     box = (int(x1_draw), int(y1_draw), int(x2_draw), int(y2_draw))
#                     if tracking_dict.get(track_id, "") in ["", "Unknown"]:
#                         head_crop = copied_frame[y1_draw-5:y2_draw+5, x1_draw-5:x2_draw+5]
#                         if head_crop is not None and head_crop.shape[0] > 0 and head_crop.shape[1] > 0:
#                             head_crop_resized = cv2.resize(head_crop, (160, 160))
#                             cropped_faces.append((track_id, head_crop_resized))
#
#
#                     #     cv2.rectangle(frame, (x1_draw, y1_draw), (x2_draw, y2_draw), (0, 255, 0), 6)
#                     #     cv2.putText(frame, f"ID: {track_id}", (x1_draw, y1_draw - 10),
#                     #                 cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
#                     # else:
#                     #     cv2.rectangle(frame, (x1_draw, y1_draw), (x2_draw, y2_draw), (255, 0, 0), 6)
#                     #     cv2.putText(frame, f"ID: {track_id}", (x1_draw, y1_draw - 10),
#                     #                 cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
#
#             live_feed_queue.put((copied_frame,boxes_data))
#
#             # Detect exits and update database
#             now = time.time()
#             for tid in list(active_tracks):
#                 if tid not in visible_track_ids:
#                     last_seen = track_last_seen.get(tid, 0)
#                     if now - last_seen > EXIT_TIMEOUT:
#                         print(f"[EXIT] ID {tid}")
#                         timestamp = int(now)
#
#                         try:
#                             cursor = db_connection.cursor()
#                             cursor.execute(
#                                 "UPDATE event_details SET end_time = ? WHERE TrackingID = ? AND end_time IS NULL",
#                                 timestamp, tid
#                             )
#                             db_connection.commit()
#                         except Exception as e:
#                             print(f"[DB ERROR] Exit update: {e}")
#
#                         active_tracks.remove(tid)
#
#             # Manage shared_queue (handle errors properly)
#             try:
#                 if shared_queue.qsize() < 50:
#                     pass
#                 #     shared_queue.put(copied_frame)
#                 # else:
#                 #     shared_queue.get_nowait()
#                 #     shared_queue.put(copied_frame)
#             except Exception as e:
#                 logging.error(f"Error managing shared_queue: {e}")
#
#             elapsed = time.time() - start_time
#             if elapsed < FRAME_DELAY:
#                 time.sleep(FRAME_DELAY - elapsed)
#
#     except KeyboardInterrupt:
#         print("\n[INFO] Exiting...")
#
# def split_rtsp_url(rtsp_url):
#
#         rtsp_pattern = re.compile(
#             r"^rtsp://(?:(?P<username>[a-zA-Z0-9_.+@-]+)(?::(?P<password>[a-zA-Z0-9_.+@-]+))?@)?(?P<ip>(?:\d{1,3}\.){3}\d{1,3})(?::(?P<port>\d{1,5}))?(/(?P<path>[a-zA-Z0-9_.@/-]+))?$"
#         )
#
#         match = rtsp_pattern.match(rtsp_url)
#
#         if match:
#
#             components = match.groupdict()
#
#             username = components.get('username')
#             password = components.get('password')
#             ip = components.get('ip')
#             port = components.get('port')
#             path = components.get('path')
#
#             return {
#                 "username": username if username else "",
#                 "password": password if password else "",
#                 "ip": ip,
#                 "port": int(port) if port else '554',
#                 "path": path if path else ""
#             }
#         else:
#             return {
#                 "username": "",
#                 "password": "",
#                 "ip": "",
#                 "port": '',
#                 "path": ""
#             }
#
#
# def mainfun():
#     global  RTSP_LINK, cap
#     data = fetch_first_camera()
#     update_camera_details(data[0], data[2], data[3], data[4], data[5], data[6], data[1])
#
#     RTSP_LINK = current_camera_details['rtsp_url']
#     result= split_rtsp_url(RTSP_LINK)
#     cap = cv2.VideoCapture(RTSP_LINK, cv2.CAP_FFMPEG)
#     initialize_ptz(result['ip'],80,result['username'],result['password'])
#
#     connect_db()
#     init_db()
#     get_next_tracking_id()
#     load_known_faces_from_db()
#     # === Start Frame Reader Thread ===
#     thread = threading.Thread(target=frame_reader, daemon=True)
#     thread.start()
#
#
#     trackthread = threading.Thread(target=mainTracker, daemon=True)
#     trackthread.start()
#
#     recognitionhread = threading.Thread(target=processFrame, daemon=True)
#     recognitionhread.start()
#
#
#     thread.join()
#     trackthread.join()
#     recognitionhread.join()
#
#
#
#
#
#
#
#
#








#
#
#
# import ast
# import datetime
# import logging
# import re
#
# import cv2
# import torch
# import numpy as np
# import time
# import threading
# import queue
# import base64
# from io import BytesIO
# from PIL import Image,ImageEnhance
# import pyodbc
# from facenet_pytorch import MTCNN, InceptionResnetV1
# from ultralytics import YOLO
# from onvif import ONVIFCamera
# from collections import OrderedDict
# from sklearn.metrics.pairwise import cosine_similarity
# from Core.face_image import fetch_first_camera
# from shared_queue import shared_queue, update_camera_details, current_camera_details, live_feed_queue, \
#      locked_ID
#
# tracking_dict = OrderedDict()
# MAX_RECENT = 50  # only keep last 50 unique entries
#
# DATABASE_HOST = 'ITDT14'
# DATABASE_NAME = 'FR_DB_NEW'
# DEVICE = 'cuda' #if torch.cuda.is_available() else 'cpu'
# lock = threading.Lock()
# MODEL_PATH = "Resources/headtrackeryolo11.pt"
# RTSP_LINK = ""
# cap = None
# CONF_THRESHOLD = 0.50
# IOU_THRESHOLD = 0.3
# TARGET_CLASS = 0
# TARGET_FPS = 10
# FRAME_DELAY = 1 / TARGET_FPS
# ROI = (0, 0, 1200, 1000)
#
# # === Load Model ===
# model = YOLO(MODEL_PATH)
# model.fuse()
#
# # === Globals ===
# frame_queue = queue.Queue(maxsize=5)
# stop_thread = False
# hidden_tracks = {}
# cropped_faces = []
# known_face_embeddings = []
# known_face_names = []
# custom_id_map = {}
# next_custom_id = 1
# event_log = {}
# flag = False
# db_connection = None
# last_ptz_vector = {"x": 0.0, "y": 0.0}
# last_move_time = 0
# EXIT_TIMEOUT = 2
# track_last_seen = {}
# locked_id_last_seen = time.time()
# LOCKED_ID_TIMEOUT = 3.0
# active_tracks = set()
# pre_lock_ptz_position=None
# curr_center_x_fst=None
# curr_center_y_fst=None
# prev_x = None
# prev_y = None
# New_Locked_ID= None
#
# dict_db_details = {
#     "str_server": "ITDT14",
#     "str_username": "sa",
#     "str_password": "root1234",
#     "str_db_name": "FR_DB_NEW",
#     "str_user_table": "user_details",
#     "str_person_table": "person_details",
#     "str_person_tracking_table": "person_tracking_details",
#     "str_event_details_table": "event_details",
#     "str_camera_details": "Camera_Details",
#     "str_persion_tabel": "personregister"
# }
#
#
# # Models
# mtcnn = MTCNN(keep_all=True,min_face_size=80,thresholds=[0.7,0.8,0.9] ,factor=0.9,device= 'cuda' )
# resnet = InceptionResnetV1(pretrained='vggface2').eval().to(DEVICE)
#
# ptz_enabled = True
# onvif_cam = None
# media_service = None
# ptz_service = None
# profile_token = None
#
#
# # PTZ Initialization
# def initialize_ptz(ptz_camera_ip, ptz_camera_port, ptz_camera_user, ptz_camera_pass):
#     global onvif_cam, media_service, ptz_service, profile_token
#     try:
#         onvif_cam = ONVIFCamera(ptz_camera_ip, ptz_camera_port, ptz_camera_user, ptz_camera_pass)
#         media_service = onvif_cam.create_media_service()
#         ptz_service = onvif_cam.create_ptz_service()
#         profiles = media_service.GetProfiles()
#         profile_token = profiles[0].token
#
#     except Exception as e:
#         print(f"[ERROR] PTZ initialization failed: {e}")
#
#
#
#
#
#
#
# def update_tracking_dict(track_id, name):
#     global tracking_dict
#
#     if track_id in tracking_dict:
#         existing_name = tracking_dict[track_id]
#
#         if existing_name == "Unknown" and name != "Unknown":
#             tracking_dict[track_id] = name
#             return "updated"
#         elif existing_name == "Unknown" and name == "Unknown":
#             tracking_dict[track_id] = name
#             return "updated"
#         elif existing_name == name or (existing_name != "Unknown" and name != "Unknown"):
#             return "skip"
#         elif existing_name != "Unknown" and name == "Unknown":
#             return "skip"
#     else:
#         # Add new entry
#         tracking_dict[track_id] = name
#
#         # Maintain only last 50 entries
#         if len(tracking_dict) > MAX_RECENT:
#             tracking_dict.popitem(last=False)
#         return "insert"
#
#
#
# # DB Functions
# def connect_db():
#     global db_connection
#     try:
#         conn_str = f'Driver={{ODBC Driver 17 for SQL Server}};Server={DATABASE_HOST};DATABASE={DATABASE_NAME};UID=sa;PWD=root1234'
#         db_connection = pyodbc.connect(conn_str, autocommit=True)
#     except Exception as e:
#         print(f"DB Connection Error: {e}")
#
# def init_db():
#     cursor = db_connection.cursor()
#     cursor.execute(f"SELECT database_id FROM sys.databases WHERE name = '{DATABASE_NAME}'")
#     if not cursor.fetchone():
#         cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
#         db_connection.commit()
#
#     print(" Tables ready.")
#
# def close_db():
#     if db_connection:
#         db_connection.close()
#         print(" DB connection closed.")
#
# def get_next_tracking_id():
#     global next_custom_id
#     cursor = db_connection.cursor()
#     cursor.execute("SELECT ISNULL(MAX(TrackingID), 0) FROM event_details")
#     next_custom_id = cursor.fetchone()[0] + 1
#
#
# # def load_known_faces():
# #     path = "D:\\face_recogniton_Mamali\\saved_images\\New folder"
# #     for person_name in os.listdir(path):
# #         person_folder = os.path.join(path, person_name)
# #         if os.path.isdir(person_folder):
# #             embeddings = []
# #             for file in os.listdir(person_folder):
# #                 if file.lower().endswith(('.jpg','jfif' ,'.png')):
# #                     img_path = os.path.join(person_folder, file)
# #                     print("Reading Image File: " + img_path)
# #                     img = Image.open(img_path).convert("RGB")
# #                     aligned = mtcnn(img)
# #                     if aligned is not None:
# #                         if aligned.ndim == 3:
# #                             aligned = aligned.unsqueeze(0)
# #                         embedding = resnet(aligned.to(DEVICE)).detach().cpu().numpy()
# #                         embeddings.append(embedding[0])
# #             if embeddings:
# #                 mean_embedding = np.mean(embeddings, axis=0)
# #                 known_face_embeddings.append(mean_embedding)
# #                 known_face_names.append(person_name)
# #     save_known_faces()
#
#
# def load_known_faces_from_db():
#     # Connect to SQL Server
#     connection = pyodbc.connect(
#         f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details['str_server']};UID={dict_db_details['str_username']};PWD={dict_db_details['str_password']}",
#         autocommit=True)
#     cursor = connection.cursor()
#
#     # Fetch person info and mean_image strings
#     query = """
#         SELECT [id], [full_name], [mean_image]
#         FROM [FR_DB_NEW].[dbo].[personregister]
#     """
#     cursor.execute(query)
#     rows = cursor.fetchall()
#
#     for row in rows:
#         person_id = row.id
#         person_name = row.full_name
#         mean_str = row.mean_image
#
#         try:
#             # Convert string to Python list safely
#             mean_list = ast.literal_eval(mean_str)
#             mean_embedding = np.array(mean_list, dtype=np.float32)
#
#             # Append to memory
#             known_face_embeddings.append(mean_embedding)
#             known_face_names.append((person_id, person_name))
#         except Exception as e:
#             print(f"Error parsing mean_image for {person_name}: {e}")
#
#     cursor.close()
#     connection.close()
#
#
# def update_person_mean(id , new_name , new_encode):
#     global known_face_embeddings,known_face_names
#     try:
#         # Find the index of the tuple containing the ID
#         index = next((i for i, (person_id, name,) in enumerate(known_face_names) if person_id == id), None)
#
#         if index is None:
#             print(f"ID '{id}' not found in known faces.")
#             return False
#
#         # Update name in the known_face_names list
#         old_name = known_face_names[index][1]
#         known_face_names[index] = (id, new_name)
#         if isinstance(new_encode, np.ndarray):
#             known_face_embeddings[index] = new_encode
#
#         print(f"Updated local name from '{old_name}' to '{new_name}' for ID {id}.")
#         return True
#
#     except Exception as e:
#         print(f"Unexpected error in update_person_name: {str(e)}")
#         return False
#
#
# def add_person_mean(id , new_name , new_encode):
#     global known_face_embeddings, known_face_names
#     try:
#         known_face_names.append((id,new_name))
#         known_face_embeddings.append(new_encode)
#
#     except Exception as e:
#         print(f"Unexpected error in update_person_name: {str(e)}")
#         return False
#
#
# def delete_person(id):
#     global known_face_embeddings, known_face_names
#     try:
#         index = next((i for i, (person_id, _) in enumerate(known_face_names) if person_id == id), None)
#         if index is None:
#             print(f"ID '{id}' not found in known faces.")
#             return False
#
#         known_face_embeddings.pop(index)
#         removed_name = known_face_names.pop(index)[1]
#         print(f"Deleted {removed_name} (ID: {id}) from known faces.")
#
#     except Exception as e:
#         print(f"Error in delete_person: {str(e)}")
#         return False
#
#
# def perform_recognition_for_validation(embedding,threshold = 0.6):
#     name = "Unknown"
#
#     if known_face_embeddings:
#         scores = cosine_similarity([embedding], known_face_embeddings)[0]
#         best_match_idx = np.argmax(scores)
#         max_sim = scores[best_match_idx]
#
#         best_embedding = known_face_embeddings[best_match_idx]
#         dist = np.linalg.norm(embedding - best_embedding)
#
#         if max_sim > threshold and dist < 0.65:
#             id, name = known_face_names[best_match_idx]
#             return name, True, id
#
#     return "",False, 0
#
#
#
# def enhance_image(img):
#     img = ImageEnhance.Contrast(img).enhance(1.3)
#     img = ImageEnhance.Sharpness(img).enhance(2.0)
#     return img
#
#
# # Custom ID map
# def get_custom_id(original_id):
#     global next_custom_id, custom_id_map
#     if original_id not in custom_id_map:
#         custom_id_map[original_id] = next_custom_id
#         next_custom_id += 1
#     return custom_id_map[original_id]
#
#
#
# # === Utils ===
# def calculate_iou(box1, box2):
#     xA = max(box1[0], box2[0])
#     yA = max(box1[1], box2[1])
#     xB = min(box1[2], box2[2])
#     yB = min(box1[3], box2[3])
#
#     interArea = max(0, xB - xA) * max(0, yB - yA)
#     box1Area = (box1[2] - box1[0]) * (box1[3] - box1[1])
#     box2Area = (box2[2] - box2[0]) * (box2[3] - box2[1])
#
#     unionArea = box1Area + box2Area - interArea
#     return interArea / unionArea if unionArea != 0 else 0
#
#
# def frame_reader():
#     global flag, RTSP_LINK, cap
#
#     while not flag:
#         new_rtsp_link = current_camera_details.get('rtsp_url', None)
#
#         # Acquire lock to update RTSP safely
#         with lock:
#             if new_rtsp_link and new_rtsp_link != RTSP_LINK:
#                 RTSP_LINK = new_rtsp_link
#                 print(f"RTSP link changed. RestartRTSP_LINKing stream: {RTSP_LINK}")
#
#                 # Release old capture if it exists
#                 if cap is not None:
#                     cap.release()
#                     cap = None  # Ensure old object is cleared
#
#                 # Start new video capture
#                 cap = cv2.VideoCapture(RTSP_LINK, cv2.CAP_FFMPEG)
#                 if not cap.isOpened():
#                     print(f"Failed to open stream: {RTSP_LINK}")
#                     cap = None  # Reset cap if opening fails
#                     continue
#
#         # Ensure cap is valid before reading frames
#         if cap is None or not cap.isOpened():
#             continue  # Wait until a valid RTSP link is set
#
#         ret, frame = cap.read()
#         if not ret or frame is None or frame.size == 0:
#             continue
#
#         if not frame_queue.full():
#
#             frame= cv2.resize(frame,(2560,1440))
#             frame_queue.put(frame)
#     with lock:
#         if cap is not None:
#             cap.release()
#             cap = None
#
# def processFrame():
#     global flag, event_log, known_face_names,known_face_embeddings,New_Locked_ID
#     cursor = db_connection.cursor()
#     cooldown_time = 2
#     last_recognition_time = {}
#
#     while True:
#         if not cropped_faces:
#             time.sleep(0.01)
#             continue
#
#         try:
#             track_id, face_crop = cropped_faces.pop(0)
#             print(f"---------------------Locked ID : {New_Locked_ID}---------------------")
#
#             if face_crop is None or face_crop.size == 0:
#                 continue
#
#             now = time.time()
#             if track_id in last_recognition_time and (now - last_recognition_time[track_id] < cooldown_time):
#                 continue
#             last_recognition_time[track_id] = now
#
#             # Reject too-small faces
#             if face_crop.shape[0] < 100 or face_crop.shape[1] < 100:
#                 continue
#
#             # Resize to help
#             time.sleep(0.1)
#             face_crop_resized = cv2.resize(face_crop, (175, 175))
#             head_crop_rgb = cv2.cvtColor(face_crop_resized, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(head_crop_rgb)
#
#             aligned = mtcnn(img)
#
#             if aligned is None or (isinstance(aligned, list) and not aligned):
#                 continue
#
#             if isinstance(aligned, list):
#                 aligned = aligned[0]
#
#             if aligned.ndim == 3:
#                 aligned = aligned.unsqueeze(0)
#
#             aligned = aligned.to(DEVICE)
#             embedding = resnet(aligned).detach().cpu().numpy()[0]
#             embedding = embedding / np.linalg.norm(embedding)
#
#             name = "Unknown"
#             threshold = 0.6
#
#             if known_face_embeddings:
#                 scores = cosine_similarity([embedding], known_face_embeddings)[0]
#                 best_match_idx = np.argmax(scores)
#                 max_sim = scores[best_match_idx]
#
#                 best_embedding = known_face_embeddings[best_match_idx]
#                 dist = np.linalg.norm(embedding - best_embedding)
#
#                 if max_sim > threshold and dist < 0.65:
#                    id ,name = known_face_names[best_match_idx]
#
#             decision = update_tracking_dict(track_id,name )
#             update_name = False
#             skip_insertion = False
#
#             if decision == "insert":
#                 update_name = False
#             elif decision == "updated":
#                 update_name = True
#             elif decision == "skip":
#                 skip_insertion = True
#
#             timestamp = int(time.time())
#             pil_img = Image.fromarray(cv2.cvtColor(face_crop_resized, cv2.COLOR_BGR2RGB))
#             buffer = BytesIO()
#             pil_img.save(buffer, format="PNG")
#             face_base64 = base64.b64encode(buffer.getvalue()).decode()
#
#             if skip_insertion:
#                continue
#             if update_name:
#                 cursor.execute(
#                     "UPDATE event_details SET captured_img = ?, person_name = ? WHERE TrackingID = ? AND person_name ='Unknown'",
#                     face_base64, name, track_id
#                 )
#                 db_connection.commit()
#             else:
#                 cursor.execute(
#                     "INSERT INTO event_details (TrackingID, captured_img, person_name, start_time) VALUES (?, ?, ?, ?)",
#                     track_id, face_base64, name, timestamp
#                 )
#                 db_connection.commit()
#
#
#         except Exception as e:
#             print(f"[ERROR] in processFrame: {e}")
#             continue
# #
# # def set_temp_preset(ptz_service, profile_token):
# #     try:
# #         # Create a temporary preset name
# #         preset_name = "TEMP_PRE_LOCK_POS"
# #
# #         # Set a new preset
# #         preset_token = ptz_service.SetPreset({
# #             'ProfileToken': profile_token,
# #             'PresetName': preset_name
# #         })
# #
# #         print(f"[PTZ] Temporary preset '{preset_name}' set with token: {preset_token}")
# #         return preset_token
# #     except Exception as e:
# #         print(f"[PTZ ERROR] Could not set temporary preset: {e}")
# #         return None
# #
# #
# # def goto_temp_preset(ptz_service, profile_token, preset_token):
# #     try:
# #         ptz_service.Stop({'ProfileToken': profile_token})
# #
# #         ptz_service.GotoPreset({
# #             'ProfileToken': profile_token,
# #             'PresetToken': preset_token
# #         })
# #
# #         print(f"[PTZ] Moved to temporary preset (token: {preset_token})")
# #     except Exception as e:
# #         print(f"[PTZ ERROR] Failed to go to temporary preset: {e}")
# #
# # def remove_temp_preset(ptz_service, profile_token, preset_token):
# #     try:
# #         ptz_service.RemovePreset({
# #             'ProfileToken': profile_token,
# #             'PresetToken': preset_token
# #         })
# #         print(f"[PTZ] Temporary preset removed.")
# #     except Exception as e:
# #         print(f"[PTZ ERROR] Could not remove temporary preset: {e}")
#
#
# def move_ptz(dx, dy, frame_shape, ptz_service, profile_token, speed=0.5, threshold=10):
#     global last_ptz_vector, last_move_time
#
#     frame_height, frame_width = frame_shape
#
#     normalized_dx = dx / frame_width
#     normalized_dy = dy / frame_height
#
#     pan_speed = max(min(normalized_dx * speed, 1.0), -1.0)
#     tilt_speed = max(min(normalized_dy * speed, 1.0), -1.0)
#     if dx is None and dy is None:
#         # No coordinates found: move camera to center (stop movement)
#         try:
#             ptz_service.Stop({'ProfileToken': profile_token})
#             last_ptz_vector = {"x": frame_width/2, "y": frame_height/2}
#             print("[PTZ] No target detected. Camera stopped (centered).")
#         except Exception as e:
#             print(f"[PTZ ERROR] Failed to stop: {e}")
#         return
#
#     if abs(dx) < threshold and abs(dy) < threshold:
#         if last_ptz_vector["x"] != 0 or last_ptz_vector["y"] != 0:
#             try:
#                 ptz_service.Stop({'ProfileToken': profile_token})
#                 # last_ptz_vector = {"x": 0.0, "y": 0.0}
#             except Exception as e:
#                 print(f"[PTZ ERROR] Stop failed: {e}")
#             return
#
#     now = time.time()
#     if now - last_move_time < 0.05 and abs(pan_speed - last_ptz_vector["x"]) < 0.01 and abs(tilt_speed - last_ptz_vector["y"]) < 0.01:
#         return
#
#     ptz_vector = {
#         'PanTilt': {'x': pan_speed, 'y': -tilt_speed},
#         'Zoom': {'x': 0}
#     }
#
#     try:
#         ptz_service.ContinuousMove({
#             'ProfileToken': profile_token,
#             'Velocity': ptz_vector
#         })
#         last_ptz_vector = {'x': pan_speed, 'y': -tilt_speed}
#         last_move_time = now
#     except Exception as e:
#         print(f"[PTZ ERROR] Failed to move: {e}")
#
# def move_ptz_to_home(dx, dy, frame_shape, ptz_service, profile_token, speed=0.5, threshold=10):
#     frame_height, frame_width = frame_shape
#
#     if dx is None or dy is None:
#         try:
#             ptz_service.Stop({'ProfileToken': profile_token})
#             print("[PTZ] No target detected. Camera stopped.")
#         except Exception as e:
#             print(f"[PTZ ERROR] Failed to stop: {e}")
#         return
#
#     # Ignore small adjustments
#     if abs(dx) < threshold and abs(dy) < threshold:
#         try:
#             ptz_service.Stop({'ProfileToken': profile_token})
#         except Exception as e:
#             print(f"[PTZ ERROR] Stop failed: {e}")
#         return
#
#     # Normalize movement to [-1, 1]
#     normalized_dx = dx / frame_width
#     normalized_dy = dy / frame_height
#
#     # Scale movement
#     pan_distance = max(min(normalized_dx * speed, 1.0), -1.0)
#     tilt_distance = max(min(normalized_dy * speed, 1.0), -1.0)
#
#     ptz_vector = {
#         'PanTilt': {
#             'x': pan_distance,
#             'y': -tilt_distance  # Invert to match camera tilt direction
#         }
#     }
#
#     try:
#         ptz_service.RelativeMove({
#             'ProfileToken': profile_token,
#             'Translation': ptz_vector
#         })
#         print(f"[PTZ] Moving by pan: {pan_distance:.3f}, tilt: {-tilt_distance:.3f}")
#     except Exception as e:
#         print(f"[PTZ ERROR] Failed to move: {e}")
#
# def resize_frame_and_detections( frame, detections, target_width=1041, target_height=908):
#
#         t0 = time.time()
#
#         original_height, original_width = frame.shape[:2]
#         scale_x = target_width / original_width
#         scale_y = target_height / original_height
#
#
#         frame_gpu = cv2.UMat(frame)
#         resized_gpu = cv2.resize(frame_gpu, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
#
#
#         resized_frame = resized_gpu.get()
#         resized_detections = []
#         if detections:
#             boxes = np.array([det["bbox"] for det in detections])
#             boxes[:, [0, 2]] = (boxes[:, [0, 2]] * scale_x).astype(int)
#             boxes[:, [1, 3]] = (boxes[:, [1, 3]] * scale_y).astype(int)
#
#             for i, det in enumerate(detections):
#                 updated_det = det.copy()
#                 updated_det["bbox"] = tuple(boxes[i])
#                 resized_detections.append(updated_det)
#
#         t1 = time.time()
#         print(f"Total time with GPU (UMat): {t1 - t0:.6f} seconds")
#
#         return resized_detections, resized_frame
#
#
#
#
# def mainTracker():
#     global next_custom_id, locked_id_last_seen,pre_lock_ptz_position,LOCKED_ID_TIMEOUT,curr_center_x_fst,curr_center_y_fst,prev_x,prev_y
#
#     locked_id_last_seen = time.time()
#
#
#     try:
#         while True:
#             start_time = time.time()
#
#             try:
#                 frame = frame_queue.get(timeout=1)
#             except queue.Empty:
#                 print("[INFO] Waiting for frame...")
#                 time.sleep(0.01)
#                 continue
#
#             if frame is None or frame.size == 0:
#                 print("[ERROR] Invalid frame received. Skipping...")
#                 continue
#
#             height, width, _ = frame.shape
#             copied_frame = frame.copy()
#
#             roi_x1 = int((current_camera_details["roi_start_width"] / 100) * width)
#             roi_x2 = int((current_camera_details["roi_end_width"] / 100) * width)
#             roi_y1 = int((current_camera_details["roi_start_height"] / 100) * height)
#             roi_y2 = int((current_camera_details["roi_end_height"] / 100) * height)
#
#             cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 0, 255), 5)
#             cv2.putText(frame, "ROI", (roi_x1 + 5, roi_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#
#             x1, y1, x2, y2 = ROI
#             cropped_frame = copied_frame
#
#             if cropped_frame is None or cropped_frame.size == 0:
#                 print("[ERROR] Invalid cropped frame. Skipping...")
#                 continue
#
#             if frame.shape[:2] != cropped_frame.shape[:2]:
#                 cropped_frame = cv2.resize(cropped_frame, (frame.shape[1], frame.shape[0]))
#
#             try:
#                 results = model.track(
#                     source=cropped_frame,
#                     persist=True,
#                     stream=False,
#                     conf=CONF_THRESHOLD,
#                     iou=IOU_THRESHOLD,
#                     classes=[TARGET_CLASS],
#                     tracker="botsort.yaml"
#                 )
#             except Exception as e:
#                 print(f"[ERROR] model.track failed: {e}")
#                 continue
#
#             boxes_data = []
#
#             for result in results:
#                 if result.boxes is not None:
#                     for box in result.boxes:
#                         x1_crop, y1_crop, x2_crop, y2_crop = map(int, box.xyxy[0].tolist())
#                         conf = float(box.conf[0])
#                         orig_id = int(box.id[0]) if box.id is not None else -1
#
#                         track_id = get_custom_id(orig_id)
#                         x1_orig = x1 + x1_crop
#                         y1_orig = y1 + y1_crop
#                         x2_orig = x1 + x2_crop
#                         y2_orig = y1 + y2_crop
#
#                         width = x2_orig - x1_orig
#                         height = y2_orig - y1_orig
#
#                         if x1_orig >= roi_x1 and x2_orig <= roi_x2 and y1_orig >= roi_y1 and y2_orig <= roi_y2:
#                             if width * height >= 800:
#                                 boxes_data.append({
#                                     "track_id": track_id,
#                                     "bbox": (x1_orig, y1_orig, x2_orig, y2_orig),
#                                     "conf": conf,
#                                     "area": width * height
#                                 })
#
#             visible_track_ids = set()
#             hidden_track_ids = set()
#
#             for i in range(len(boxes_data)):
#                 box_i = boxes_data[i]
#                 is_hidden = False
#                 for j in range(len(boxes_data)):
#                     if i == j:
#                         continue
#                     box_j = boxes_data[j]
#                     iou = calculate_iou(box_i["bbox"], box_j["bbox"])
#                     if iou > 0.4:
#                         if box_i["conf"] < box_j["conf"] or box_i["area"] < box_j["area"]:
#                             is_hidden = True
#                             break
#                 track_id = box_i["track_id"]
#                 if not is_hidden:
#                     visible_track_ids.add(track_id)
#                     track_last_seen[track_id] = time.time()
#                     if track_id not in active_tracks:
#                         print(f"[ENTRY] ID {track_id}")
#                         active_tracks.add(track_id)
#                 else:
#                     hidden_track_ids.add(track_id)
#
#
# #------------------------------------------------------------ this part is running every time unnecessarily so it is taking much time thats why frame is lagging
#             # clicked_x= clicked_ID["X"]
#             # clicked_y= clicked_ID["Y"]
#             # if clicked_x != None and clicked_y != None:
#             #     if prev_x != clicked_x and prev_y != clicked_y:
#             #         resized_detections, resized_frame=resize_frame_and_detections(frame,boxes_data)
#             #         for track in resized_detections:
#             #             track_id = track["track_id"]
#             #             if track_id in visible_track_ids:
#             #                 x1_draw, y1_draw, x2_draw, y2_draw = track["bbox"]
#             #                 if x1_draw <= clicked_x <= x2_draw and y1_draw <= clicked_y <= y2_draw:
#             #                     prev_x= clicked_x
#             #                     prev_y= clicked_y
#             #                     print(f"Clicked on box ID: {track_id} get by new code !")
#             #                     if track_id != New_Locked_ID:
#             #                         New_Locked_ID= track_id
#             #                     else:
#             #                         New_Locked_ID = None
#
#
# #------------------------------------------------------------------------------
#             for track in boxes_data:
#                 track_id = track["track_id"]
#
#                 if track_id in visible_track_ids:
#                     x1_draw, y1_draw, x2_draw, y2_draw = track["bbox"]
#
#                     if tracking_dict.get(track_id, "") in ["", "Unknown"]:
#                         head_crop = copied_frame[y1_draw - 5:y2_draw + 5, x1_draw - 5:x2_draw + 5]
#                         if head_crop is not None and head_crop.shape[0] > 0 and head_crop.shape[1] > 0:
#                             head_crop_resized = cv2.resize(head_crop, (160, 160))
#                             cropped_faces.append((track_id, head_crop_resized))
#
#                             cv2.rectangle(frame, (x1_draw, y1_draw), (x2_draw, y2_draw), (0, 255, 0), 6)
#                             cv2.putText(frame, f"ID: {track_id}", (x1_draw, y1_draw - 10),
#                                         cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
#
#                     if track_id == locked_ID["locked_id"]:
#                         if locked_ID["locked_id"] is not None:
#                             cv2.rectangle(frame, (x1_draw, y1_draw), (x2_draw, y2_draw), (255, 0, 0), 6)
#
#                         if pre_lock_ptz_position is None and locked_ID["locked_id"] is not None:
#                             curr_center_x_fst = cropped_frame.shape[1] // 2
#                             curr_center_y_fst = cropped_frame.shape[1] // 2
#                             pre_lock_ptz_position = (curr_center_x_fst, curr_center_y_fst)
#
#                         curr_center_x = (x1_draw + x2_draw) // 2
#                         curr_center_y = (y1_draw + y2_draw) // 2
#
#                         # Frame center
#                         frame_center_x = cropped_frame.shape[1] // 2
#                         frame_center_y = cropped_frame.shape[0] // 2
#
#                         dx = curr_center_x - frame_center_x
#                         dy = curr_center_y - frame_center_y
#
#                         move_ptz(dx, dy, cropped_frame.shape[:2], ptz_service, profile_token)
#                         locked_id_last_seen = time.time()
#
#             if locked_ID["locked_id"] is not None:
#                 if locked_ID["locked_id"] not in visible_track_ids:
#                     time_since_last_seen = time.time() - locked_id_last_seen
#                     if time_since_last_seen > LOCKED_ID_TIMEOUT and pre_lock_ptz_position is not None:
#                         try:
#                             ptz_service.Stop({'ProfileToken': profile_token})
#                             # # Get current frame center
#                             # frame_center_x = cropped_frame.shape[1] // 2
#                             # frame_center_y = cropped_frame.shape[0] // 2
#                             #
#                             # # Use saved pre-lock position to calculate offset
#                             # dx = pre_lock_ptz_position[0] - frame_center_x
#                             # dy = pre_lock_ptz_position[1] - frame_center_y
#                             #
#                             # move_ptz_to_home(dx, dy, cropped_frame.shape[:2], ptz_service, profile_token)
#
#                             print(
#                                 f"[PTZ] Locked ID {locked_ID["locked_id"]} lost. Returning to saved pre-lock position.")
#                             locked_id_last_seen = time.time()  # Avoid repeated triggering
#
#                         except Exception as e:
#                             print(f"[PTZ ERROR] Failed to return to pre-lock position: {e}")
#
#             # if track_id == locked_ID["locked_id"]:
#                     #     if pre_lock_ptz_position is None and locked_ID["locked_id"] is not None:
#                     #         curr_center_x_fst =cropped_frame.shape[1] // 2
#                     #         curr_center_y_fst = cropped_frame.shape[1] // 2
#                     #         pre_lock_ptz_position = (curr_center_x_fst, curr_center_y_fst)
#                     #
#                     #     curr_center_x = (x1_draw + x2_draw) // 2
#                     #     curr_center_y = (y1_draw + y2_draw) // 2
#                     #
#                     #     # Frame center
#                     #     frame_center_x = cropped_frame.shape[1] // 2
#                     #     frame_center_y = cropped_frame.shape[0] // 2
#                     #
#                     #     dx = curr_center_x - frame_center_x
#                     #     dy = curr_center_y - frame_center_y
#                     #
#                     #     move_ptz(dx, dy, cropped_frame.shape[:2], ptz_service, profile_token)
#                     #     locked_id_last_seen = time.time()
#
#
#             # if locked_ID["locked_id"] is not None:
#             #     if  locked_ID["locked_id"] not in visible_track_ids :
#             #         time_since_last_seen = time.time() - locked_id_last_seen
#             #         if time_since_last_seen > LOCKED_ID_TIMEOUT:
#             #             try:
#             #                 ptz_service.Stop({'ProfileToken': profile_token})
#             #                 # frame_center_x1 = cropped_frame.shape[1] // 2
#             #                 # frame_center_y1 = cropped_frame.shape[0] // 2
#             #                 #
#             #                 # dx1 = curr_center_x_fst - frame_center_x1
#             #                 # dy1 = curr_center_y_fst - frame_center_y1
#             #                 # move_ptz(dx1, dy1, cropped_frame.shape[:2], ptz_service, profile_token)
#             #                 # ptz_service.Stop({'ProfileToken': profile_token})
#             #                 print(f"[PTZ] Locked ID {locked_ID['locked_id']} lost. Returning to home position.")
#             #                 locked_id_last_seen = time.time()  # Avoid repeated triggering
#             #             except Exception as e:
#             #                 print(f"[PTZ ERROR] Failed to go home: {e}")
#
#
#             live_feed_queue.put((frame,boxes_data))
#
#             now = time.time()
#             for tid in list(active_tracks):
#                 if tid not in visible_track_ids:
#                     last_seen = track_last_seen.get(tid, 0)
#                     if now - last_seen > EXIT_TIMEOUT:
#                         print(f"[EXIT] ID {tid}")
#                         timestamp = int(now)
#
#                         try:
#                             cursor = db_connection.cursor()
#                             cursor.execute(
#                                 "UPDATE event_details SET end_time = ? WHERE TrackingID = ? AND end_time IS NULL",
#                                 timestamp, tid
#                             )
#                             db_connection.commit()
#                         except Exception as e:
#                             print(f"[DB ERROR] Exit update: {e}")
#
#                         active_tracks.remove(tid)
#
#             try:
#                 if shared_queue.qsize() < 50:
#                     pass
#             except Exception as e:
#                 logging.error(f"Error managing shared_queue: {e}")
#
#             elapsed = time.time() - start_time
#             if elapsed < FRAME_DELAY:
#                 time.sleep(FRAME_DELAY - elapsed)
#         # remove_temp_preset(ptz_service, profile_token, pre_lock_ptz_position)
#     except KeyboardInterrupt:
#         print("\n[INFO] Exiting...")
#
# def split_rtsp_url(rtsp_url):
#
#         rtsp_pattern = re.compile(
#             r"^rtsp://(?:(?P<username>[a-zA-Z0-9_.+@-]+)(?::(?P<password>[a-zA-Z0-9_.+@-]+))?@)?(?P<ip>(?:\d{1,3}\.){3}\d{1,3})(?::(?P<port>\d{1,5}))?(/(?P<path>[a-zA-Z0-9_.@/-]+))?$"
#         )
#
#         match = rtsp_pattern.match(rtsp_url)
#
#         if match:
#
#             components = match.groupdict()
#
#             username = components.get('username')
#             password = components.get('password')
#             ip = components.get('ip')
#             port = components.get('port')
#             path = components.get('path')
#
#             return {
#                 "username": username if username else "",
#                 "password": password if password else "",
#                 "ip": ip,
#                 "port": int(port) if port else '554',
#                 "path": path if path else ""
#             }
#         else:
#             return {
#                 "username": "",
#                 "password": "",
#                 "ip": "",
#                 "port": '',
#                 "path": ""
#             }
#
#
# def mainfun():
#     global  RTSP_LINK, cap
#     data = fetch_first_camera()
#     update_camera_details(data[0], data[2], data[3], data[4], data[5], data[6], data[1])
#
#     RTSP_LINK = current_camera_details['rtsp_url']
#     result= split_rtsp_url(RTSP_LINK)
#     cap = cv2.VideoCapture(RTSP_LINK, cv2.CAP_FFMPEG)
#     initialize_ptz(result['ip'],80,result['username'],result['password'])
#
#     connect_db()
#     init_db()
#     get_next_tracking_id()
#     load_known_faces_from_db()
#     # === Start Frame Reader Thread ===
#     thread = threading.Thread(target=frame_reader, daemon=True)
#     thread.start()
#
#
#     trackthread = threading.Thread(target=mainTracker, daemon=True)
#     trackthread.start()
#
#     recognitionhread = threading.Thread(target=processFrame, daemon=True)
#     recognitionhread.start()
#
#
#     thread.join()
#     trackthread.join()
#     recognitionhread.join()
#







import ast
import logging
import cv2
import torch
import numpy as np
import time
import threading
import queue
import base64
from io import BytesIO
from PIL import Image, ImageEnhance
import pyodbc
from facenet_pytorch import MTCNN, InceptionResnetV1
from ultralytics import YOLO
from onvif import ONVIFCamera
from collections import OrderedDict
from sklearn.metrics.pairwise import cosine_similarity
from Core.face_image import fetch_first_camera
from shared_queue import shared_queue, update_camera_details, current_camera_details, live_feed_queue, locked_ID, \
     split_rtsp_url
from FR_Detection.ptz_controller import PTZController
# from ptz_controller import PTZController
tracking_dict = OrderedDict()
MAX_RECENT = 50

DATABASE_HOST = 'ITDT14'
DATABASE_NAME = 'FR_DB_NEW'
DEVICE = 'cuda'
lock = threading.Lock()
MODEL_PATH = "Resources/headtrackeryolo11.pt"
RTSP_LINK = ""
cap = None
CONF_THRESHOLD = 0.70
IOU_THRESHOLD = 0.3
TARGET_CLASS = 0
TARGET_FPS = 10
FRAME_DELAY = 1 / TARGET_FPS
ROI = (0, 0, 1200, 1000)

# === Load Model ===
model = YOLO(MODEL_PATH)
model.fuse()
obj_ptz_controller=PTZController()


# === Globals ===
frame_queue = queue.Queue(maxsize=5)
stop_thread = False
hidden_tracks = {}
cropped_faces = []
known_face_embeddings = []
known_face_names = []
custom_id_map = {}
next_custom_id = 1
event_log = {}
flag = False
db_connection = None
last_ptz_vector = {"x": 0.0, "y": 0.0}
last_move_time = 0
EXIT_TIMEOUT = 2
track_last_seen = {}
locked_id_last_seen = time.time()
LOCKED_ID_TIMEOUT = 3.0
ptz_home=False
active_tracks = set()
frame_count=0
dict_db_details = {
    "str_server": "ITDT14",
    "str_username": "sa",
    "str_password": "root1234",
    "str_db_name": "FR_DB_NEW",
    "str_user_table": "user_details",
    "str_person_table": "person_details",
    "str_person_tracking_table": "person_tracking_details",
    "str_event_details_table": "event_details",
    "str_camera_details": "Camera_Details",
    "str_persion_tabel": "personregister"
}

# Models
mtcnn = MTCNN(keep_all=True, min_face_size=80, thresholds=[0.7, 0.8, 0.9], factor=0.9, device='cuda')
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(DEVICE)


def update_tracking_dict(track_id, name):
    global tracking_dict

    if track_id in tracking_dict:
        existing_name = tracking_dict[track_id]

        if existing_name == "Unknown" and name != "Unknown":
            tracking_dict[track_id] = name
            return "updated"
        elif existing_name == "Unknown" and name == "Unknown":
            tracking_dict[track_id] = name
            return "updated"
        elif existing_name == name or (existing_name != "Unknown" and name != "Unknown"):
            return "skip"
        elif existing_name != "Unknown" and name == "Unknown":
            return "skip"
    else:
        # Add new entry
        tracking_dict[track_id] = name

        # Maintain only last 50 entries
        if len(tracking_dict) > MAX_RECENT:
            tracking_dict.popitem(last=False)
        return "insert"


# DB Functions
def connect_db():
    global db_connection
    try:
        conn_str = f'Driver={{ODBC Driver 17 for SQL Server}};Server={DATABASE_HOST};DATABASE={DATABASE_NAME};UID=sa;PWD=root1234'
        db_connection = pyodbc.connect(conn_str, autocommit=True)
    except Exception as e:
        print(f"DB Connection Error: {e}")


def init_db():
    cursor = db_connection.cursor()
    cursor.execute(f"SELECT database_id FROM sys.databases WHERE name = '{DATABASE_NAME}'")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
        db_connection.commit()

    print(" Tables ready.")

def get_next_tracking_id():
    global next_custom_id
    cursor = db_connection.cursor()
    cursor.execute("SELECT ISNULL(MAX(TrackingID), 0) FROM event_details")
    next_custom_id = cursor.fetchone()[0] + 1


def load_known_faces_from_db():
    # Connect to SQL Server
    connection = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details['str_server']};UID={dict_db_details['str_username']};PWD={dict_db_details['str_password']}",
        autocommit=True)
    cursor = connection.cursor()

    query = """
         SELECT [id], [full_name], [mean_image]
         FROM [FR_DB_NEW].[dbo].[personregister]
         ORDER BY [id] ASC
     """
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        person_id = row.id
        person_name = row.full_name
        mean_str = row.mean_image

        try:
            # Convert string to Python list safely
            mean_list = ast.literal_eval(mean_str)
            mean_embedding = np.array(mean_list, dtype=np.float32)

            # Append to memory
            known_face_embeddings.append(mean_embedding)
            known_face_names.append((person_id, person_name))
        except Exception as e:
            print(f"Error parsing mean_image for {person_name}: {e}")

    cursor.close()
    connection.close()


def update_person_mean(id, new_name, new_encode):
    global known_face_embeddings, known_face_names
    try:
        # Find the index of the tuple containing the ID
        index = next((i for i, (person_id, name,) in enumerate(known_face_names) if person_id == id), None)
        if index is None:
            print(f"ID '{id}' not found in known faces.")
            return False

        # Update name in the known_face_names list
        old_name = known_face_names[index][1]
        known_face_names[index] = (id, new_name)
        if isinstance(new_encode, np.ndarray):
            known_face_embeddings[index] = new_encode

        print(f"Updated local name from '{old_name}' to '{new_name}' for ID {id}.")
        return True

    except Exception as e:
        print(f"Unexpected error in update_person_name: {str(e)}")
        return False


def add_person_mean(id, new_name, new_encode):
    global known_face_embeddings, known_face_names
    try:
        known_face_names.append((id, new_name))
        known_face_embeddings.append(new_encode)

    except Exception as e:
        print(f"Unexpected error in update_person_name: {str(e)}")
        return False


def delete_person(id):
    global known_face_embeddings, known_face_names
    try:
        index = next((i for i, (person_id, _) in enumerate(known_face_names) if person_id == id), None)
        if index is None:
            print(f"ID '{id}' not found in known faces.")
            return False

        known_face_embeddings.pop(index)
        removed_name = known_face_names.pop(index)[1]
        print(f"Deleted {removed_name} (ID: {id}) from known faces.")

    except Exception as e:
        print(f"Error in delete_person: {str(e)}")
        return False


def perform_recognition_for_validation(embedding, threshold=0.6):
    name = "Unknown"

    if known_face_embeddings:
        scores = cosine_similarity([embedding], known_face_embeddings)[0]
        best_match_idx = np.argmax(scores)
        max_sim = scores[best_match_idx]

        best_embedding = known_face_embeddings[best_match_idx]
        dist = np.linalg.norm(embedding - best_embedding)

        if max_sim > threshold and dist < 0.55:
            id, name = known_face_names[best_match_idx]
            return name, True, id

    return "", False, 0


def enhance_image(img):
    img = ImageEnhance.Contrast(img).enhance(1.3)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    return img


# Custom ID map
def get_custom_id(original_id):
    global next_custom_id, custom_id_map
    if original_id not in custom_id_map:
        custom_id_map[original_id] = next_custom_id
        next_custom_id += 1
    return custom_id_map[original_id]


# === Utils ===
def calculate_iou(box1, box2):
    xA = max(box1[0], box2[0])
    yA = max(box1[1], box2[1])
    xB = min(box1[2], box2[2])
    yB = min(box1[3], box2[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    box1Area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2Area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    unionArea = box1Area + box2Area - interArea
    return interArea / unionArea if unionArea != 0 else 0


def frame_reader():
    global flag, RTSP_LINK, cap

    while not flag:
        new_rtsp_link = current_camera_details.get('rtsp_url', None)
        # Acquire lock to update RTSP safely
        with lock:
            if new_rtsp_link and new_rtsp_link != RTSP_LINK:
                RTSP_LINK = new_rtsp_link
                print(f"RTSP link changed. RestartRTSP_LINKing stream: {RTSP_LINK}")

                # Release old capture if it exists
                if cap is not None:
                    cap.release()
                    cap = None  # Ensure old object is cleared

                # Start new video capture
                cap = cv2.VideoCapture(RTSP_LINK, cv2.CAP_FFMPEG)
                if not cap.isOpened():
                    print(f"Failed to open stream: {RTSP_LINK}")
                    cap = None  # Reset cap if opening fails
                    continue

        # Ensure cap is valid before reading frames
        if cap is None or not cap.isOpened():
            continue  # Wait until a valid RTSP link is set

        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            continue

        if not frame_queue.full():
            # frame = cv2.resize(frame, (1920, 1080))
            frame_queue.put(frame)
    with lock:
        if cap is not None:
            cap.release()
            cap = None


def processFrame():
    global flag, event_log, known_face_names, known_face_embeddings
    cursor = db_connection.cursor()
    cooldown_time = 2
    last_recognition_time = {}

    while True:
        if not cropped_faces:
            time.sleep(0.01)
            continue

        try:
            track_id, face_crop = cropped_faces.pop(0)

            if face_crop is None or face_crop.size == 0:
                continue

            now = time.time()
            if track_id in last_recognition_time and (now - last_recognition_time[track_id] < cooldown_time):
                continue
            last_recognition_time[track_id] = now
            if face_crop.shape[0] < 100 or face_crop.shape[1] < 100:
                continue

            # Resize to help
            time.sleep(0.1)
            recognition_start_time = time.time()
            face_crop_resized = cv2.resize(face_crop, (175, 175))
            head_crop_rgb = cv2.cvtColor(face_crop_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(head_crop_rgb)

            boxes, probs = mtcnn.detect(img)
            # if boxes is None or len(boxes) == 0 or probs[0] < 0.5:
            #     continue
            box = boxes[0]
            x1, y1, x2, y2 = box
            face_area = (x2 - x1) * (y2 - y1)
            frame_area = img.size[0] * img.size[1]
            visible_percentage = face_area / frame_area

            if visible_percentage < 0.3:
                continue

            aligned = mtcnn(img)

            if aligned is None or (isinstance(aligned, list) and not aligned):
                continue

            if isinstance(aligned, list):
                aligned = aligned[0]

            if aligned.ndim == 3:
                aligned = aligned.unsqueeze(0)

            aligned = aligned.to(DEVICE)
            embedding = resnet(aligned).detach().cpu().numpy()[0]
            embedding = embedding / np.linalg.norm(embedding)

            name = "Unknown"
            threshold = 0.61

            if known_face_embeddings:
                scores = cosine_similarity([embedding], known_face_embeddings)[0]
                best_match_idx = np.argmax(scores)
                max_sim = scores[best_match_idx]


                best_embedding = known_face_embeddings[best_match_idx]
                dist = np.linalg.norm(embedding - best_embedding)

                if max_sim > threshold and dist < 0.61:
                    id, name = known_face_names[best_match_idx]
                    recognition_duration = time.time()  - recognition_start_time
                    print(f"[INFO] Recognition for Track ID {track_id},{name} took {recognition_duration:.3f} seconds")

            decision = update_tracking_dict(track_id, name)
            update_name = False
            skip_insertion = False

            if decision == "insert":
                update_name = False
            elif decision == "updated":
                update_name = True
            elif decision == "skip":
                skip_insertion = True

            timestamp = int(time.time())
            pil_img = Image.fromarray(cv2.cvtColor(face_crop_resized, cv2.COLOR_BGR2RGB))
            buffer = BytesIO()
            pil_img.save(buffer, format="PNG")
            face_base64 = base64.b64encode(buffer.getvalue()).decode()

            if skip_insertion:
                continue
            if update_name:
                cursor.execute(
                    "UPDATE event_details SET captured_img = ?, person_name = ? WHERE TrackingID = ? AND person_name ='Unknown'",
                    face_base64, name, track_id
                )
                db_connection.commit()
            else:
                cursor.execute(
                    "INSERT INTO event_details (TrackingID, captured_img, person_name, start_time) VALUES (?, ?, ?, ?)",
                    track_id, face_base64, name, timestamp
                )
                db_connection.commit()


        except Exception as e:
            print(f"[ERROR] in processFrame: {e}")
            continue


def mainTracker():
    global next_custom_id, locked_id_last_seen, LOCKED_ID_TIMEOUT,ptz_home,frame_count,obj_ptz_controller

    locked_id_last_seen = time.time()

    try:
        while True:
            start_time = time.time()

            try:
                frame = frame_queue.get(timeout=1)
            except queue.Empty:
                print("[INFO] Waiting for frame...")
                time.sleep(0.01)
                continue

            if frame is None or frame.size == 0:
                print("[ERROR] Invalid frame received. Skipping...")
                continue

            height, width, _ = frame.shape
            copied_frame = frame.copy()

            roi_x1 = int((current_camera_details["roi_start_width"] / 100) * width)
            roi_x2 = int((current_camera_details["roi_end_width"] / 100) * width)
            roi_y1 = int((current_camera_details["roi_start_height"] / 100) * height)
            roi_y2 = int((current_camera_details["roi_end_height"] / 100) * height)

            cv2.rectangle(copied_frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 0, 255), 5)
            cv2.putText(copied_frame, "ROI", (roi_x1 + 5, roi_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            x1, y1, x2, y2 = ROI
            cropped_frame = copied_frame

            if cropped_frame is None or cropped_frame.size == 0:
                print("[ERROR] Invalid cropped frame. Skipping...")
                continue

            if frame.shape[:2] != cropped_frame.shape[:2]:
                cropped_frame = cv2.resize(cropped_frame, (frame.shape[1], frame.shape[0]))

            try:
                results = model.track(
                    source=cropped_frame,
                    persist=True,
                    stream=False,
                    conf=CONF_THRESHOLD,
                    iou=IOU_THRESHOLD,
                    classes=[TARGET_CLASS],
                    tracker="botsort.yaml"
                )
            except Exception as e:
                print(f"[ERROR] model.track failed: {e}")
                continue

            boxes_data = []

            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        x1_crop, y1_crop, x2_crop, y2_crop = map(int, box.xyxy[0].tolist())
                        conf = float(box.conf[0])
                        orig_id = int(box.id[0]) if box.id is not None else -1

                        track_id = get_custom_id(orig_id)
                        x1_orig = x1 + x1_crop
                        y1_orig = y1 + y1_crop
                        x2_orig = x1 + x2_crop
                        y2_orig = y1 + y2_crop

                        width = x2_orig - x1_orig
                        height = y2_orig - y1_orig

                        if x1_orig >= roi_x1 and x2_orig <= roi_x2 and y1_orig >= roi_y1 and y2_orig <= roi_y2:
                            if width * height >= 800:
                                boxes_data.append({
                                    "track_id": track_id,
                                    "bbox": (x1_orig, y1_orig, x2_orig, y2_orig),
                                    "conf": conf,
                                    "area": width * height
                                })

            visible_track_ids = set()
            hidden_track_ids = set()

            for i in range(len(boxes_data)):
                box_i = boxes_data[i]
                is_hidden = False
                for j in range(len(boxes_data)):
                    if i == j:
                        continue
                    box_j = boxes_data[j]
                    iou = calculate_iou(box_i["bbox"], box_j["bbox"])
                    if iou > 0.4:
                        if box_i["conf"] < box_j["conf"] or box_i["area"] < box_j["area"]:
                            is_hidden = True
                            break
                track_id = box_i["track_id"]
                if not is_hidden:
                    visible_track_ids.add(track_id)
                    track_last_seen[track_id] = time.time()
                    if track_id not in active_tracks:
                        print(f"[ENTRY] ID {track_id}")
                        active_tracks.add(track_id)
                else:
                    hidden_track_ids.add(track_id)

            for track in boxes_data:
                track_id = track["track_id"]
                if track_id in visible_track_ids:
                    x1_draw, y1_draw, x2_draw, y2_draw = track["bbox"]

                    if tracking_dict.get(track_id, "") in ["", "Unknown"]:
                        head_crop = copied_frame[y1_draw - 5:y2_draw + 5, x1_draw - 5:x2_draw + 5]
                        if head_crop is not None and head_crop.shape[0] > 0 and head_crop.shape[1] > 0:
                            head_crop_resized = cv2.resize(head_crop, (160, 160))
                            cropped_faces.append((track_id, head_crop_resized))

                    if track_id == locked_ID["locked_id"]:

                        curr_center_x = (x1_draw + x2_draw) // 2
                        curr_center_y = (y1_draw + y2_draw) // 2

                        # Frame center
                        frame_center_x = cropped_frame.shape[1] // 2
                        frame_center_y = cropped_frame.shape[0] // 2

                        dx = curr_center_x - frame_center_x
                        dy = curr_center_y - frame_center_y

                        obj_ptz_controller.move(dx, dy, cropped_frame.shape[:2])
                        locked_id_last_seen = time.time()
                        ptz_home=False

                        if frame_count % 50 == 0:
                            try:
                                obj_ptz_controller.move(0, 0, frame.shape[:2])
                                frame_count=0
                                print("[PTZ KEEP-ALIVE] Sent small keep-alive move to prevent idle timeout.")
                            except Exception as e:
                                print(f"[PTZ ERROR] Keep-alive failed: {e}")
                        else:
                            frame_count+=1

            if locked_ID["locked_id"] is not None:
                if locked_ID["locked_id"] not in visible_track_ids:
                    time_since_last_seen = time.time() - locked_id_last_seen
                    if time_since_last_seen > LOCKED_ID_TIMEOUT and not ptz_home:
                        try:
                            # ptz_service.Stop({'ProfileToken': profile_token})
                            result = obj_ptz_controller.get_home_position()

                            if result["source"] == "preset":
                                try:
                                    obj_ptz_controller.goto_preset(result["position"].token)
                                except Exception as e:
                                   print(f"Failed to go to preset: {e}")
                            elif result["source"] == "home":
                                try:
                                    obj_ptz_controller.GotoHomePosition({'ProfileToken': obj_ptz_controller.profile_token})
                                    print("Returning to Home Position")
                                except Exception as e:
                                    print(f"Failed to go to Home Position: {e}")
                            else:
                                print("No Home or Preset set")

                            locked_id_last_seen = time.time()
                            locked_ID["locked_id"]=None
                            ptz_home=True
                        except Exception as e:
                            print(f"[PTZ ERROR] Failed to move to center: {e}")
            elif locked_ID["locked_id"] is  None and not ptz_home:
                try:
                    if obj_ptz_controller.ptz_eligibility:
                        obj_ptz_controller.ptz_service.Stop({'ProfileToken': obj_ptz_controller.profile_token})
                    result = obj_ptz_controller.get_home_position()

                    if result["source"] == "preset":
                        try:
                            obj_ptz_controller.goto_preset(result["position"].token)
                        except Exception as e:
                            print(f"Failed to go to preset: {e}")
                    elif result["source"] == "home":
                        try:
                            obj_ptz_controller.GotoHomePosition({'ProfileToken': obj_ptz_controller.profile_token})
                            print("Returning to Home Position")
                        except Exception as e:
                            print(f"Failed to go to Home Position: {e}")
                    else:
                        print("No Home or Preset set")
                    ptz_home = True
                except Exception as e:
                    print(f"[PTZ ERROR] Failed to move to homer: {e}")

            live_feed_queue.put((copied_frame, boxes_data))

            now = time.time()
            for tid in list(active_tracks):
                if tid not in visible_track_ids:
                    last_seen = track_last_seen.get(tid, 0)
                    if now - last_seen > EXIT_TIMEOUT:
                        print(f"[EXIT] ID {tid}")
                        timestamp = int(now)

                        try:
                            cursor = db_connection.cursor()
                            cursor.execute(
                                "UPDATE event_details SET end_time = ? WHERE TrackingID = ? AND end_time IS NULL",
                                timestamp, tid
                            )
                            db_connection.commit()
                        except Exception as e:
                            print(f"[DB ERROR] Exit update: {e}")

                        active_tracks.remove(tid)

            try:
                if shared_queue.qsize() < 50:
                    pass
            except Exception as e:
                logging.error(f"Error managing shared_queue: {e}")

            elapsed = time.time() - start_time
            if elapsed < FRAME_DELAY:
                time.sleep(FRAME_DELAY - elapsed)

    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")


def mainfun():
    global RTSP_LINK, cap, obj_ptz_controller
    data = fetch_first_camera()
    update_camera_details(data[0], data[2], data[3], data[4], data[5], data[6], data[1])

    RTSP_LINK = current_camera_details['rtsp_url']
    result = split_rtsp_url(RTSP_LINK)
    cap = cv2.VideoCapture(RTSP_LINK, cv2.CAP_FFMPEG)
    obj_ptz_controller= PTZController(result['ip'], 80, result['username'], result['password'])
    # initialize_ptz(result['ip'], 80, result['username'], result['password'])

    connect_db()
    init_db()
    get_next_tracking_id()
    load_known_faces_from_db()
    # === Start Frame Reader Thread ===
    thread = threading.Thread(target=frame_reader, daemon=True)
    thread.start()

    trackthread = threading.Thread(target=mainTracker, daemon=True)
    trackthread.start()

    recognitionhread = threading.Thread(target=processFrame, daemon=True)
    recognitionhread.start()

    thread.join()
    trackthread.join()
    recognitionhread.join()

