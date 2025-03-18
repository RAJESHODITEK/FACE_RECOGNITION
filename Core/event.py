import re
import pyodbc
from base64 import b64decode
from numpy import frombuffer, uint8
from customtkinter import CTkImage
from cv2 import imdecode, IMREAD_COLOR
from PIL import Image
import datetime

class Event():

    def __init__(self, dict_db_details : dict, dict_user_data : dict):
        cursor = None
        super().__init__()

        self.dict_db_details = dict_db_details
        self.dict_user_data = dict_user_data

    def fetch_events(self, i_start_index: int, dict_filter_criteria: dict):
        list_event = []
        start_date = ""

        try:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.dict_db_details['str_server']};UID={self.dict_db_details['str_username']};PWD={self.dict_db_details['str_password']}"
            connection = pyodbc.connect(connection_string, autocommit=True)

            cursor = connection.cursor()

            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            if (dict_filter_criteria["str_start_timeperiod"] == "" and dict_filter_criteria[
                "str_end_timeperiod"] == "" and dict_filter_criteria["str_vehicle_number"] == ""):
                query = f"""SELECT vehicle_img, number_plate_img, vehicle_number, number_plate_color, country, time, status,alarm,acknowledgment_message,acknowledgment_time,event_id
                            FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                            ORDER BY time DESC OFFSET ? ROWS FETCH NEXT 10 ROWS ONLY 
                         """
                cursor.execute(query, i_start_index)
            else:
                query = f"""SELECT vehicle_img, number_plate_img, vehicle_number, number_plate_color, country, time, status,alarm,acknowledgment_message,acknowledgment_time,event_id
                            FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                            WHERE CAST(time AS DATETIME) BETWEEN ? AND ? AND vehicle_number LIKE ?
                            ORDER BY time DESC OFFSET ? ROWS FETCH NEXT 10 ROWS ONLY 
                        """
                cursor.execute(query, dict_filter_criteria["str_start_timeperiod"],
                               dict_filter_criteria["str_end_timeperiod"], dict_filter_criteria["str_vehicle_number"],
                               i_start_index)

            response = cursor.fetchall()

            if response:
                columns = [column[0] for column in cursor.description]  # Fetch column names
                for data in response:
                    if data.vehicle_img != "N/A" and data.number_plate_img != "N/A":
                        record_dict = {columns[i]: data[i] for i in range(len(columns))}  # Map columns to data
                        record_dict['time'] = record_dict['time'].replace(microsecond=0)
                        list_event.append(record_dict)

                for data in list_event:
                    data["vehicle_img"] = self.base64_to_cv2mat_or_pillow_image_converter(data["vehicle_img"], 200, 135)
                    data["number_plate_img"] = self.base64_to_cv2mat_or_pillow_image_converter(data["number_plate_img"],
                                                                                               180, 50)

                query = f"""
                            SELECT TOP 1 FORMAT(time, 'dd-MM-yyyy')
                            FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                            ORDER BY time ASC
                        """
                cursor.execute(query)

                start_date = (cursor.fetchall())[0][0]

        except Exception as e:
            print(e)

        finally:
            cursor.close()
            connection.close()
        return list_event, start_date

    def insert_acknowledgment(self, vehicle_number: str, acknowledgment_note: str):
        """
        Insert acknowledgment details for a specific vehicle
        """
        try:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.dict_db_details['str_server']};UID={self.dict_db_details['str_username']};PWD={self.dict_db_details['str_password']}"
            connection = pyodbc.connect(connection_string, autocommit=True)
            cursor = connection.cursor()

            # Print debug info
            print(f"Database: {self.dict_db_details['str_db_name']}")
            print(f"Table: {self.dict_db_details['str_event_details_table']}")
            print(f"Vehicle Number: {vehicle_number}")

            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            # First verify if the record exists
            verify_query = f"""
                SELECT COUNT(*) 
                FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                WHERE event_id = ?
            """
            cursor.execute(verify_query, (vehicle_number,))
            count = cursor.fetchone()[0]
            print(f"Found {count} matching records")

            if count == 0:
                print("No matching record found")
                return False

            # Update query to add acknowledgment details
            update_query = f"""
                UPDATE [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                SET acknowledgment_message = ?,
                    acknowledgment_time = GETDATE()
                WHERE event_id = ?
            """

            print("Executing update query...")
            print(f"Parameters: message='{acknowledgment_note}', event_id='{vehicle_number}'")

            cursor.execute(update_query, (acknowledgment_note, vehicle_number))
            connection.commit()

            print("Update successful")
            return True

        except Exception as e:
            import traceback
            print(f"Error inserting acknowledgment: {str(e)}")
            print("Full traceback:")
            print(traceback.format_exc())
            return False

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
    def fetch_unrecognized_vehicles(self):
        """
        Fetch unacknowledged vehicles, excluding those already acknowledged
        """
        list_unrecognized_event = []
        try:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.dict_db_details['str_server']};UID={self.dict_db_details['str_username']};PWD={self.dict_db_details['str_password']}"
            connection = pyodbc.connect(connection_string, autocommit=True)

            cursor = connection.cursor()
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            query = f"""
                      SELECT TOP 10 * 
                      FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                      WHERE alarm = 2 
                      AND acknowledgment_time IS NULL
                      ORDER BY time DESC
                   """
            cursor.execute(query)

            response = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            for data in response:
                record_dict = {columns[i]: data[i] for i in range(len(columns))}
                list_unrecognized_event.append(record_dict)

            for data in list_unrecognized_event:
                data["vehicle_img"] = self.base64_to_cv2mat_or_pillow_image_converter(data["vehicle_img"], 200, 130)
                data["number_plate_img"] = self.base64_to_cv2mat_or_pillow_image_converter(data["number_plate_img"],
                                                                                           180, 50)

        except Exception as e:
            print(e)
        finally:
            cursor.close()
            connection.close()

        return list_unrecognized_event

    def get_data_count(self, dict_filter_criteria: dict):

        i_data_count = 0

        try:
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                        SERVER={self.dict_db_details["str_server"]};
                                        UID={self.dict_db_details["str_username"]};
                                        PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            if (dict_filter_criteria["str_start_timeperiod"] == "" and dict_filter_criteria[
                "str_end_timeperiod"] == "" and dict_filter_criteria["str_vehicle_number"] == ""):
                query = f"""SELECT COUNT(*)
                            FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                         """
                cursor.execute(query)
            else:
                query = f"""SELECT COUNT(*)
                            FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                            WHERE CAST(time AS DATETIME) BETWEEN ? AND ? AND vehicle_number LIKE ?
                         """
                cursor.execute(query, dict_filter_criteria["str_start_timeperiod"],
                               dict_filter_criteria["str_end_timeperiod"], dict_filter_criteria["str_vehicle_number"])

            result = cursor.fetchone()
            i_data_count = int(result[0])

        except Exception as e:
            pass

        finally:
            cursor.close()
            connection.close()

        return i_data_count

    def get_distinct_vehicles(self, search_text=None):
        list_vehicles = []

        try:
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                        SERVER={self.dict_db_details["str_server"]};
                                        UID={self.dict_db_details["str_username"]};
                                        PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            if search_text:
                fetch_vehicles_query = f"""
                    SELECT DISTINCT vehicle_number 
                    FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_event_details_table"]}]
                    WHERE vehicle_number LIKE ?
                """
                cursor.execute(fetch_vehicles_query, f'%{search_text}%')
            else:
                fetch_vehicles_query = f"""
                    SELECT DISTINCT vehicle_number 
                    FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_event_details_table"]}]
                """
                cursor.execute(fetch_vehicles_query)

            response = cursor.fetchall()
            if response:
                list_vehicles = [data.vehicle_number for data in response]
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            connection.close()
        return list_vehicles

    def validate_filter_criteria(self, str_start_date: str,
                                 str_end_date: str,
                                 str_start_hour: str,
                                 str_end_hour: str,
                                 str_start_minute: str,
                                 str_end_minute: str,
                                 str_vehicle_number: str):

        dict_response = {
            "str_error_msg_heading": "",
            "str_error_msg": "",
            "dict_filter_criteria": {
                "str_start_timeperiod": "",
                "str_end_timeperiod": "",
                "str_vehicle_number": "",
            }
        }

        start_date = None
        end_date = None

        if (str_vehicle_number == "All"):
            str_vehicle_number = "%"

        start_date = datetime.datetime.strptime(str_start_date, "%d-%m-%Y")
        end_date = datetime.datetime.strptime(str_end_date, "%d-%m-%Y")

        if (start_date > end_date):
            dict_response["str_error_msg_heading"] = "Invalid Date Range!"
            dict_response["str_error_msg"] = "'Starting Date' must be less than 'Ending Date'"
            return dict_response

        elif (start_date == end_date or str_start_date == str_end_date):
            if (int(str_start_hour) > int(str_end_hour)):
                dict_response["str_error_msg_heading"] = "Invalid Time Range!"
                dict_response["str_error_msg"] = "'Starting Time' must be less than 'Ending Time'"
                return dict_response
            elif (int(str_start_hour) == int(str_end_hour)):
                if (int(str_start_minute) > int(str_end_minute)):
                    dict_response["str_error_msg_heading"] = "Invalid Time Range!"
                    dict_response["str_error_msg"] = "'Starting Time' must be less than 'Ending Time'"
                    return dict_response

        dict_response["dict_filter_criteria"][
            "str_start_timeperiod"] = f"{start_date.year}-{start_date.month}-{start_date.day} {str_start_hour}:{str_start_minute}:00.000"
        dict_response["dict_filter_criteria"][
            "str_end_timeperiod"] = f"{end_date.year}-{end_date.month}-{end_date.day} {str_end_hour}:{str_end_minute}:00.000"
        dict_response["dict_filter_criteria"]["str_vehicle_number"] = str_vehicle_number

        return dict_response


    def base64_to_cv2mat_or_pillow_image_converter(self, base64_image,requiredWidth,requiredHeight):


        image_data = b64decode(base64_image) #Decode the base64 string to get the raw bytes

        image_array = frombuffer(image_data, dtype=uint8) # Convert the raw bytes to a NumPy array

        image_mat = imdecode(image_array, IMREAD_COLOR) #Decode the NumPy array as an image using OpenCV
        thumbnail_plate = Image.fromarray(image_mat).resize((requiredWidth, requiredHeight),
                                                            Image.Resampling.LANCZOS)

        photo = CTkImage(light_image=thumbnail_plate, size=(requiredWidth, requiredHeight))

        return photo

    def fetch_vehicle_data_and_count(self, dict_filter_criteria: dict):
        list_filtered_data = []
        entry_count = exit_count = 0
        try:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.dict_db_details['str_server']};UID={self.dict_db_details['str_username']};PWD={self.dict_db_details['str_password']}"
            connection = pyodbc.connect(connection_string, autocommit=True)
            cursor = connection.cursor()

            # Select the database
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            # Prepare the LIKE query part for vehicle_number
            vehicle_number_filter = dict_filter_criteria["str_vehicle_number"]
            if vehicle_number_filter == "":  # If the vehicle number is blank, treat it as '%' for all vehicle numbers
                vehicle_number_filter = "%"

            # 1. Get total count of rows with status 'Entry'
            entry_count_query = f"""
                SELECT COUNT(*) 
                FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                WHERE CAST(time AS DATETIME) BETWEEN ? AND ? 
                AND vehicle_number LIKE ? 
                AND status = 'Entry'
            """
            cursor.execute(entry_count_query, dict_filter_criteria["str_start_timeperiod"],
                           dict_filter_criteria["str_end_timeperiod"], vehicle_number_filter)

            entry_count = cursor.fetchone()[0]

            exit_count_query = f"""
                           SELECT COUNT(*) 
                           FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                           WHERE CAST(time AS DATETIME) BETWEEN ? AND ? 
                           AND vehicle_number LIKE ? 
                           AND status = 'Exit'
                       """
            cursor.execute(exit_count_query, dict_filter_criteria["str_start_timeperiod"],
                           dict_filter_criteria["str_end_timeperiod"], vehicle_number_filter)

            exit_count = cursor.fetchone()[0]

            return entry_count, exit_count, entry_count-exit_count
        except Exception as e:
            print(e)
            return entry_count, exit_count, entry_count-exit_count
        finally:
            cursor.close()
            connection.close()
