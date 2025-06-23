import base64
import cv2
import numpy as np
import pyodbc

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
# def check_image_encode(known_face_names, known_face_encodings, new_image_base64):
#     image_blob = new_image_base64
#     # Handle case where image_blob might be None or empty
#     if not image_blob:
#         print(f"No image data found")
#         return 'error', '', ''
#
#     # Decode base64 string to bytes
#     if isinstance(image_blob, str):
#         image_bytes = base64.b64decode(image_blob)
#     else:
#         print(f"Invalid image data type : {type(image_blob)}")
#         return 'error', '', ''
#
#     # Convert bytes to numpy array
#     try:
#         nparr = np.frombuffer(image_bytes, np.uint8)
#         if nparr.size == 0:
#             print(f"Empty numpy array ")
#             return 'error', '', ''
#
#     except ValueError as ve:
#         print(f"Failed to convert bytes to numpy array : {str(ve)}")
#         return 'error', '', ''
#
#     # Decode image from numpy array
#     try:
#         image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         if image is None:
#             print(f"Failed to decode image ")
#             return 'error', '', ''
#
#     except Exception as decode_err:
#         print(f"Image decoding error : {str(decode_err)}")
#         return 'error', '', ''
#
#     # Convert BGR to RGB
#     try:
#         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     except Exception as cvt_err:
#         print(f"Color conversion error : {str(cvt_err)}")
#         return 'error', '', ''
#     face_encoding=''
#     # Get face encoding
#     try:
#         location = face_recognition.face_locations(image, 2, model='cnn')
#         if location:
#             encoding = face_recognition.face_encodings(image, location, num_jitters=3, model='cnn')
#             for face_encoding in encoding:
#                 face_encoding = encoding[0]
#                 matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#                 face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#                 best_match_index = np.argmin(face_distances)
#
#                 threshold = np.mean(face_distances) - np.std(face_distances)
#                 if matches[best_match_index] and face_distances[best_match_index] < threshold - 0.15:
#                     nametemp =known_face_names[best_match_index][1]
#                     id= known_face_names[best_match_index][0]
#                     print(" mathched with name ", nametemp)
#                     return 'matched' , nametemp, id
#
#             return 'unmatched' , face_encoding ,''
#     except Exception as e:
#         print("last error",e)
#         return 'error', '' , ''

def fetch_first_camera():
    cursor = None

    try:
        # Connect to the database
        connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                               SERVER={dict_db_details["str_server"]};
                                               UID={dict_db_details["str_username"]};
                                               PWD={dict_db_details["str_password"]}""",
                                    autocommit=True)
        cursor = connection.cursor()

        # Prepare the query to update camera data
        update_query = f"""
                        SELECT TOP (1) [Camera_name]
                        ,[Camera_direction]
                        ,[URL]
                        ,[ROIStartPercentageHeight]
                        ,[ROIEndPercentageHeight]
                        ,[ROIStartPercentageWidth]
                        ,[ROIEndPercentageWidth]
                        FROM [FR_DB_NEW].[dbo].[Camera_Details]
                       """

        # Execute the update query
        cursor.execute(update_query)
        camera_data = cursor.fetchone()

        return camera_data
    except pyodbc.InterfaceError as e:
        # Handle database interface errors (e.g., issues with the connection)
        print(f"Database interface error: {e}")
        return []
    except pyodbc.DatabaseError as e:
        # Handle database-related errors (e.g., issues with executing the query)
        print(f"Database error: {e}")
        return []
    except pyodbc.OperationalError as e:
        # Handle operational errors (e.g., issues with connecting to the server)
        print(f"Operational error: {e}")
        return []
    except pyodbc.Error as e:
        # General pyodbc errors
        print(f"SQL execution error: {e}")
        return []
    except KeyError as e:
        # Handle missing keys in the camera_data dictionary
        print(f"Missing expected field in camera data: {e}")
        return []
    except Exception as e:
        # Catch all other exceptions
        print(f"An unexpected error occurred: {e}")
        return []
    finally:
        # Clean up and close the connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
