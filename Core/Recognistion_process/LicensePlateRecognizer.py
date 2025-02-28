import cv2
import json
import time
import base64
import random
import pyodbc
import threading
import numpy as np
from PIL import Image
from io import BytesIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from shared_queue import vehicle_tracking_details_queue         #The mutual queue which will be accessed by both producer and consumer
from Core.Recognistion_process.ConfigLoader import  ConfigLoader
from Core.Recognistion_process.DatabaseHandler import DatabaseHandler
from Core.Recognistion_process.ImageProcessing import ImageProcessing
from Core.Recognistion_process.LicensePlateRecognition import LicensePlateRecognition

class LicensePlateRecognizer:
    def __init__(self):
        self.unique_license_plates = set()
        self.configloader=ConfigLoader("Config/config.json")
        self.license_plate_recognition = LicensePlateRecognition()
        self.image_processing = ImageProcessing()
        self.db_handler = DatabaseHandler()
        self.stop_event = threading.Event()  # Event to signal stopping the thread



    def process_image_for_plate(self, img_base64):
        """
        Recognise the image and return all data about that license plate.
        :param img_base64 : Input image as a encrypted format as base64 string.
        :return: The Recognised data abut the license plate in dictionary.

        """
        try:
            full_image_data = base64.b64decode(img_base64)
            full_image = Image.open(BytesIO(full_image_data))
            full_image = self.image_processing.resize_image(full_image)
            full_image_np = np.array(full_image)
            full_image_cv2 = cv2.cvtColor(full_image_np, cv2.COLOR_RGB2BGR)

            detection_result, plate_base64, vehicle_base64 ,color ,country = self.license_plate_recognition.detect_plate(full_image_cv2)
            now = datetime.now()
            if detection_result != 'N/A':
                return {
                    'plate_number': detection_result,
                    'plate_img': plate_base64,
                    'vehicle_img': vehicle_base64,
                    'color':color,
                    'country':country,
                    'system_time':f"{now.year}-{now.month}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}.{now.microsecond // 1000:03d}"
                }
            else:
                return None

        except Exception as e:
            print(f"Error in  processing image for plate fun : {e}")
            return None

    def process_vehicle_data(self, vehicle_data, connection):
        """
            Insert  the data  in database .
            :param vehicle_data : dictionary about vehicle details.
            :param connection: Database connection to handle DB operation

        """

        try:
            detection_result = None
            for i in range(1, 6):
                img_base64 = vehicle_data.get(f'vehicle_img{i}', ' ')
                if not img_base64:
                    continue

                detection_result = self.process_image_for_plate(img_base64)

                # Check if detection_result is valid and has plate_number
                if detection_result is not None and 'plate_number' in detection_result and detection_result['plate_number'] != 'N/A':
                    status = 'Entry' if vehicle_data.get('status', 0) == 0 else 'Exit'
                    alarm_code = random.randint(0, 2)
                    is_recognizeed = 1 if detection_result['plate_number'] != 'N/A' else 0
                    insert_data = {
                        "vehicle_id": vehicle_data.get('vehicle_id', None),
                        # Ensure to include this in your detection_result
                        "vehicle_number": detection_result.get('plate_number', ""),
                        "number_plate_color": detection_result.get('color', ""),
                        "country": detection_result.get('country', ""),
                        "vehicle_img": detection_result.get('vehicle_img', ""),
                        "number_plate_img": detection_result.get('plate_img', ""),
                        "is_recognized": int(is_recognizeed),
                        "time": detection_result.get('system_time', ""),
                        "status": status,  # Default status or fetched from another logic
                        "alarm": alarm_code
                    }

                    # Insert vehicle data into the database
                    self.db_handler.insert_data(connection, self.db_handler.event_details_table_name,
                                                self.db_handler.event_details_table_columns, list(insert_data.values()))

                    break

            # If no plate was detected, insert N/A data into the database
            if detection_result and detection_result.get('plate_number') == 'N/A':
                status = 'Entry' if vehicle_data.get('status', 0) == 0 else 'Exit'
                alarm_code = random.randint(0, 2)
                is_recognizeed = 0
                insert_data = {
                    "vehicle_id": vehicle_data.get('vehicle_id', None),
                    # Ensure to include this in your detection_result
                    "vehicle_number": detection_result.get('plate_number', ""),
                    "number_plate_color": detection_result.get('color', ""),
                    "country": detection_result.get('country', ""),
                    "vehicle_img": detection_result.get('vehicle_img', ""),
                    "number_plate_img": detection_result.get('plate_img', ""),
                    "is_recognized": int(is_recognizeed),
                    "time": detection_result.get('system_time', ""),
                    "status": status,  # Default status or fetched from another logic
                    "alarm": alarm_code
                }

                self.db_handler.insert_data(connection,self.db_handler.event_details_table_name,self.db_handler.event_details_table_columns,list(insert_data))
            else:
                print(f"No valid detection result for vehicle {vehicle_data.get('vehicle_id', 'N/A')}")

        except Exception as e:
            print(f"Error in  processing vehicle {vehicle_data.get('vehicle_id', 'N/A')}: {e}")



    def main(self):
        """
        main fun that will get the data from shared queue for further process and this will handle all worker threads
        """
        try:
            connection = pyodbc.connect(DatabaseHandler.fun_DSN_FOR_DB(self.configloader.get("database.dsn", "Error_DSN"), self.configloader.get("database.user", "Error_user"), self.configloader.get("database.password", "Error_password")))
            cursor = connection.cursor()
            cursor.execute(DatabaseHandler.fun_USE_DB(self.configloader.get("database.db_name","Error_Database")))

            # Use ThreadPoolExecutor for concurrent processing
            with ThreadPoolExecutor(max_workers=5) as executor:
                while not self.stop_event.is_set():
                    if not vehicle_tracking_details_queue.empty():
                        vehicle_data = vehicle_tracking_details_queue.get()
                        executor.submit(self.process_vehicle_data, vehicle_data, connection)

                    time.sleep(0.1)

        except Exception as e:
            print(f"Database connection error: {e}")
