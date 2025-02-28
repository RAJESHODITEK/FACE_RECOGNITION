import gc
import re

import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
import base64

from Core.Recognistion_process.LicensePlateColorDetector import LicensePlateColorDetector
from Core.Recognistion_process.ConfigLoader import ConfigLoader



class LicensePlateRecognition:
    def __init__(self):
        self.configloader=ConfigLoader("Config/config.json")
        self.license_plate_model = YOLO(self.configloader.get("model_details.license_plate_detection_model_path"))
        self.ocr = PaddleOCR(use_angle_cls=self.configloader.get('ocr_details.use_angle_cls'), lang=self.configloader.get('ocr_details.lang'))



    def check_plate_format(self, input_string):
        """
        Check the country name and valid number
        :param input_string string give by ocr
        :return string  country name and Unknown in failure case

        """
        country_patterns = {
            'India': [
                r'[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}',
                r'[A-Z]{2}[0-9]{1}[A-Z]{3}[0-9]{3}[A-Z]{1}',
                r'[A-Z]{2}[0-9]{1}[A-Z]{3}[0-9]{4}',
                r'[A-Z]{2}[0-9]{2}[A-Z]{1}[0-9]{4}',
                r'[A-Z]{2}[0-9]{6}',
                r'[A-Z]{2}[0-9]{1}[A-Z]{2}[0-9]{4}',
                r'[0-9]{2}[A-Z]{2}[0-9]{4}[A-Z]{2}',
                r'[0-9]{2}[A-Z]{2}[0-9]{4}[A-Z]{1}',
                r'[0-9]{2}[A-Z]{1}[0-9]{6}[A-Z]{1}'
            ],
            'China': [
                r'[A-Z]{1}[0-9]{4}[A-Z]{1}',
                r'[A-Z]{2}[0-9]{3}[A-Z]{1}',
                r'[A-Z]{4}[0-9]{2}',
                r'[A-Z]{3}[0-9]{3}',
                r'[A-Z]{1}[0-9]{1}[A-Z]{1}[0-9]{3}',
                r'[A-Z]{1}[0-9]{3}[A-Z]{1}[0-9]{1}',
            ]
        }

        # Match the input_string with regex patterns for each country
        for country, patterns in country_patterns.items():
            for pattern in patterns:
                if re.fullmatch(pattern, input_string):
                    return country

        # Return Unknown if no pattern matches
        gc.collect()
        return "Unknown"


    def detect_plate(self, image):
        """
            Detect the license plate ,perform ocr , find  its color and country
            :param image vehicle image
            :return vehicle_img, Plate_img as base64 encoding and  license plate color name

        """
        try:
            detection_results = self.license_plate_model(image)
            plate_base64, vehicle_base64 , color = 'N/A', 'N/A', 'N/A'

            # Vehicle image encoding
            _, encoded_vehicle = cv2.imencode('.jpg', image)
            vehicle_base64 = base64.b64encode(encoded_vehicle.tobytes()).decode('utf-8')

            if detection_results[0].boxes:
                for box in detection_results[0].boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    if box.conf[0] > 0.5:
                        plate_image = image[y1:y2, x1:x2]
                        _, encoded_plate = cv2.imencode('.jpg', plate_image)
                        plate_base64 = base64.b64encode(encoded_plate.tobytes()).decode('utf-8')
                        color=LicensePlateColorDetector.guess_plate_color(plate_image)

                        try:
                            ocr_results = self.ocr.ocr(plate_image, cls=True)
                        except Exception:
                            ocr_results = []

                        if ocr_results and isinstance(ocr_results[0], list):
                            detected_text = ' '.join([line[1][0] for line in ocr_results[0] if len(line) > 1])
                            country = self.check_plate_format(detected_text)
                            if country != 'Unknown':
                                return detected_text, plate_base64, vehicle_base64 ,color,country
                            else:
                                return 'N/A', plate_base64, vehicle_base64, color ,'N/A'

        except Exception as e:
            print(f"Error in plate detection: {e}")
