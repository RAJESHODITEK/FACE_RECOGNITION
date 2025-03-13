import re
import pyodbc
from base64 import b64decode
from numpy import frombuffer, uint8
from customtkinter import CTkImage
from cv2 import imdecode, IMREAD_COLOR, cvtColor, COLOR_BGR2RGB
from PIL import Image
from datetime import datetime

class Event():

    def __init__(self, dict_db_details : dict, dict_user_data : dict):
        cursor = None
        super().__init__()

        self.dict_db_details = dict_db_details
        self.dict_user_data = dict_user_data

    import pyodbc

    def fetch_event_combo_details(self, i_start_index: int, dict_filter_criteria: dict, fetch_mode="standard", page_size=5):
        """
        Fetch events with optional filtering criteria.

        Args:
            i_start_index: Starting index for pagination
            dict_filter_criteria: Dictionary containing filter criteria
            fetch_mode: 'standard' or 'combo' to determine behavior
            page_size: Number of records to return (default 5)

        Returns:
            Tuple of (list_events, start_date)
        """
        list_events = []
        start_date = ""

        try:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.dict_db_details['str_server']};UID={self.dict_db_details['str_username']};PWD={self.dict_db_details['str_password']}"
            connection = pyodbc.connect(connection_string, autocommit=True)
            cursor = connection.cursor()

            # Ensure correct database selection
            cursor.execute(f"USE {self.dict_db_details['str_db_name']};")

            # Define base query for both modes
            base_query = f"""
                SELECT 
                    e.event_id,
                    e.captured_img,
                    e.start_time,
                    e.end_time,
                    e.acknowledgment_time,
                    e.acknowledgment_message,
                    -- Show 'Unknown' if no match in personregister
                    ISNULL(p.full_name, 'Unknown') AS person_name,
                    CASE 
                        WHEN p.full_name IS NULL THEN NULL 
                        ELSE p.age 
                    END AS person_age,
                    CASE 
                        WHEN p.full_name IS NULL THEN NULL 
                        ELSE p.gender 
                    END AS person_gender,
                    CASE 
                        WHEN p.full_name IS NULL THEN NULL 
                        ELSE p.status 
                    END AS status,
                    CASE 
                        WHEN p.full_name IS NULL THEN NULL 
                        ELSE p.photo_path 
                    END AS photo_path
                FROM [{self.dict_db_details['str_db_name']}].[dbo].[event_details] e
                LEFT JOIN [{self.dict_db_details['str_db_name']}].[dbo].[personregister] p
                ON (
                    -- Exact full name match
                    e.person_name = p.full_name 
                    OR 
                    -- Match first and last name parts
                    (
                        LTRIM(RTRIM(SUBSTRING(e.person_name, 1, CHARINDEX(' ', e.person_name + ' ') - 1))) = 
                        LTRIM(RTRIM(SUBSTRING(p.full_name, 1, CHARINDEX(' ', p.full_name + ' ') - 1)))
                        AND 
                        LTRIM(RTRIM(SUBSTRING(e.person_name, CHARINDEX(' ', e.person_name + ' ') + 1, LEN(e.person_name)))) = 
                        LTRIM(RTRIM(SUBSTRING(p.full_name, CHARINDEX(' ', p.full_name + ' ') + 1, LEN(p.full_name))))
                    )
                )
            """

            # Build conditions and parameters based on filter criteria and mode
            conditions = []
            params = []

            # Standard mode time period filtering
            if fetch_mode == "standard" and dict_filter_criteria.get(
                    "str_start_timeperiod") and dict_filter_criteria.get("str_end_timeperiod"):
                conditions.append("start_time >= ? AND end_time <= ?")
                str_start_timeperiod = int(
                    datetime.strptime(dict_filter_criteria["str_start_timeperiod"], "%Y-%m-%d %H:%M:%S.%f").timestamp())
                str_end_timeperiod = int(
                    datetime.strptime(dict_filter_criteria["str_end_timeperiod"], "%Y-%m-%d %H:%M:%S.%f").timestamp())
                params.extend([str_start_timeperiod, str_end_timeperiod])

            # Combo mode person name filtering
            if fetch_mode == "standard" and dict_filter_criteria.get("str_person_name"):
                conditions.append("(e.person_name LIKE ? OR p.full_name LIKE ?)")
                name_pattern = f"%{dict_filter_criteria['str_person_name']}%"
                params.extend([name_pattern, name_pattern])


            if fetch_mode == "combo" and dict_filter_criteria.get("str_gender"):
                conditions.append("p.gender LIKE ?")
                params.append(f"%{dict_filter_criteria['str_gender']}%")

            # Build the final query
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)

            # Add pagination
            base_query += f" ORDER BY e.start_time DESC OFFSET ? ROWS FETCH NEXT {page_size} ROWS ONLY"
            params.append(i_start_index)

            # Execute query
            cursor.execute(base_query, *params)
            response = cursor.fetchall()

            if response:
                columns = [column[0] for column in cursor.description]
                for data in response:
                    # Create record dictionary from query results
                    record_dict = {columns[i]: data[i] for i in range(len(columns))}

                    # Format datetime fields if needed (standard mode check)
                    if fetch_mode == "standard":
                        for key in ["start_time", "end_time", "acknowledgment_time"]:
                            if key in record_dict and isinstance(record_dict[key], (str, bytes)):
                                record_dict[key] = str(record_dict[key]).split('.')[0]

                    # For standard mode, only include records with valid start_time
                    if fetch_mode != "standard" or record_dict.get("start_time", "N/A") != "N/A":
                        list_events.append(record_dict)

                # Process images for standard mode
                if fetch_mode == "standard":
                    for data in list_events:
                        data["person_img"] = self.base64_to_cv2mat_or_pillow_image_converter(data["person_img"], 200,
                                                                                             135)
                        data["captured_img"] = self.base64_to_cv2mat_or_pillow_image_converter(data["captured_img"],
                                                                                               180, 50)

            # Fetch earliest event date (only in standard mode)
            if fetch_mode == "standard":
                query = f"""
                    SELECT TOP 1 CONVERT(varchar, start_time, 105)
                    FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                    ORDER BY start_time ASC
                """
                cursor.execute(query)
                start_date_result = cursor.fetchone()
                if start_date_result:
                    start_date = start_date_result[0]

        except Exception as e:
            print(f"Error in fetch_events: {e}")

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection:
                connection.close()

        return list_events, start_date

    def fetch_unrecognized_vehicles(self):
        """
        Fetch vehicles with BlackList status from the database.
        """
        list_unrecognized_event = []
        try:
            print("Starting database connection...")
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.dict_db_details['str_server']};UID={self.dict_db_details['str_username']};PWD={self.dict_db_details['str_password']}"
            print(
                f"Connection string (without password): DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.dict_db_details['str_server']};UID={self.dict_db_details['str_username']}")

            connection = pyodbc.connect(connection_string, autocommit=True)
            print("Connection established successfully")

            cursor = connection.cursor()
            print(f"Using database: {self.dict_db_details['str_db_name']}")

            # Ensure correct database selection
            cursor.execute(f"USE {self.dict_db_details['str_db_name']};")

            # Main query to fetch BlackList status data
            print("Executing main query to fetch BlackList status data...")
            query = f"""
                   SELECT 
                       ed.event_id,
                       ed.person_name,
                       ed.captured_img,
                       ed.start_time,
                       ed.end_time,
                       ed.acknowledgment_time,
                       ed.acknowledgment_message,
                       pr.full_name,
                       pr.age,
                       pr.gender,
                       pr.status,
                       pr.photo_path,
                       pr.id
                   FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}] ed
                   LEFT JOIN [{self.dict_db_details['str_db_name']}].[dbo].[personregister] pr
                       ON ed.person_name = pr.full_name
                   WHERE pr.status = 'BlackList'
               """
            cursor.execute(query)
            response = cursor.fetchall()
            print(f"Main query executed successfully! Retrieved {len(response)} rows.")

            # Extract column names
            columns = [column[0] for column in cursor.description]
            print(f"Columns: {columns}")

            # Debugging: Print raw fetched data
            print("Fetched raw data:")
            for data in response:
                print(f"Raw record: {data}")
                print(f"Start Time: {data[3]}, End Time: {data[4]}")

            # Convert fetched data to list of dictionaries
            for data in response:
                record_dict = {columns[i]: data[i] for i in range(len(columns))}
                print(f"Processing record ID: {record_dict.get('event_id')}")

                print(
                    f"++++++++++++++++++Fetched start_time: {record_dict.get('start_time')}, end_time: {record_dict.get('end_time')}")

                from datetime import datetime

                # Convert Unix timestamps to readable format
                try:
                    if record_dict.get('start_time'):
                        record_dict['start_time'] = datetime.fromtimestamp(int(record_dict['start_time'])).strftime(
                            '%Y-%m-%d %H:%M:%S')
                    if record_dict.get('end_time'):
                        record_dict['end_time'] = datetime.fromtimestamp(int(record_dict['end_time'])).strftime(
                            '%Y-%m-%d %H:%M:%S')
                except Exception as time_error:
                    print(f"Error converting timestamps: {time_error}")

                print(
                    f"//////////////////////Converted start_time: {record_dict.get('start_time')}, end_time: {record_dict.get('end_time')}")

                # Check if images exist
                if record_dict.get("photo_path") is None:
                    print(f"Warning: photo_path is None for event ID {record_dict.get('event_id')}")
                if record_dict.get("captured_img") is None:
                    print(f"Warning: captured_img is None for event ID {record_dict.get('event_id')}")

                # Process images
                try:
                    if record_dict.get("photo_path"):
                        record_dict["person_img"] = self.base64_to_cv2mat_or_pillow_image_converter(
                            record_dict["photo_path"], 200, 135)
                        print("Processed person image successfully")
                    else:
                        print("Skipping person image conversion - null value")
                        record_dict["person_img"] = None

                    if record_dict.get("captured_img"):
                        record_dict["captured_img"] = self.base64_to_cv2mat_or_pillow_image_converter(
                            record_dict["captured_img"], 320, 270)
                        print("Processed captured image successfully")
                    else:
                        print("Skipping captured image conversion - null value")
                except Exception as img_error:
                    print(f"Error processing images: {img_error}")

                # Standardize field names to match frontend expectations
                record_dict["person_age"] = record_dict.pop("age", None)
                record_dict["person_gender"] = record_dict.pop("gender", None)

                list_unrecognized_event.append(record_dict)

            print(f"Final processed record count: {len(list_unrecognized_event)}")

        except Exception as e:
            print(f"Database error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection:
                connection.close()
            print("Database connection closed")

        return list_unrecognized_event

    def validate_filter_criteria(self, str_start_date: str,
                                 str_end_date: str,
                                 str_start_hour: str,
                                 str_end_hour: str,
                                 str_start_minute: str,
                                 str_end_minute: str,
                                 str_person_name: str,
                                 str_gender: str = None):

        dict_response = {
            "str_error_msg_heading": "",
            "str_error_msg": "",
            "dict_filter_criteria": {
                "str_start_timeperiod": "",
                "str_end_timeperiod": "",
                "str_person_name": "",
                "str_gender": ""
            }
        }

        start_date = None
        end_date = None

        if (str_person_name == "All"):
            str_person_name = "%"

        if (str_gender == "All" or not str_gender):
            str_gender = "%"

        start_date = datetime.strptime(str_start_date, "%d-%m-%Y")
        end_date = datetime.strptime(str_end_date, "%d-%m-%Y")

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
        dict_response["dict_filter_criteria"]["str_person_name"] = str_person_name
        dict_response["dict_filter_criteria"]["str_gender"] = str_gender

        return dict_response


    def insert_acknowledgment(self, person_name: str, acknowledgment_note: str):
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
            print(f"Person Name: {person_name}")

            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            # First verify if the record exists
            verify_query = f"""
                SELECT COUNT(*) 
                FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                WHERE event_id = ?
            """
            cursor.execute(verify_query, (person_name,))
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
            print(f"Parameters: message='{acknowledgment_note}', event_id='{person_name}'")

            cursor.execute(update_query, (acknowledgment_note, person_name))
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
            if dict_filter_criteria["str_start_timeperiod"] != "" and dict_filter_criteria["str_end_timeperiod"] != "":
                str_start_timeperiod = int(
                    datetime.strptime(dict_filter_criteria["str_start_timeperiod"], "%Y-%m-%d %H:%M:%S.%f").timestamp())
                str_end_timeperiod = int(
                    datetime.strptime(dict_filter_criteria["str_end_timeperiod"], "%Y-%m-%d %H:%M:%S.%f").timestamp())

            if (dict_filter_criteria["str_start_timeperiod"] == "" and dict_filter_criteria[
                "str_end_timeperiod"] == "" ):
                query = f"""SELECT COUNT(*)
                            FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                         """
                cursor.execute(query)
            else:
                query = f"""SELECT COUNT(*)
                            FROM [{self.dict_db_details['str_db_name']}].[dbo].[{self.dict_db_details['str_event_details_table']}]
                            WHERE start_time  BETWEEN ? AND ? 
                         """
                cursor.execute(query, str_start_timeperiod,
                               str_end_timeperiod)

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
                    SELECT DISTINCT full_name 
                    FROM [{self.dict_db_details["str_db_name"]}].[dbo].[personregister]
                    WHERE full_name LIKE ?
                """
                cursor.execute(fetch_vehicles_query, f'%{search_text}%')
            else:
                fetch_vehicles_query = f"""
                    SELECT DISTINCT full_name 
                    FROM [{self.dict_db_details["str_db_name"]}].[dbo].[personregister]
                """
                cursor.execute(fetch_vehicles_query)

            response = cursor.fetchall()
            if response:
                list_vehicles = [data.full_name for data in response]
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            connection.close()
        return list_vehicles

    def base64_to_cv2mat_or_pillow_image_converter(self, base64_image, requiredWidth, requiredHeight):
        try:
            # Decode the base64 string to raw bytes
            image_data = b64decode(base64_image)
            image_array = frombuffer(image_data, dtype=uint8)

            # Decode as OpenCV image (in BGR format)
            image_mat = imdecode(image_array, IMREAD_COLOR)

            if image_mat is None:
                raise ValueError("Failed to decode image")

            # ✅ Convert BGR to RGB
            image_mat = cvtColor(image_mat, COLOR_BGR2RGB)

            # ✅ Convert to Pillow image
            thumbnail_plate = Image.fromarray(image_mat).resize(
                (requiredWidth, requiredHeight),
                Image.Resampling.LANCZOS
            )

            # ✅ Create CTkImage from Pillow image
            photo = CTkImage(light_image=thumbnail_plate, size=(requiredWidth, requiredHeight))

            return photo

        except Exception as e:
            print(f"Error decoding base64 image: {e}")
            # Return a blank image in case of an error
            return CTkImage(
                light_image=Image.new('RGB', (requiredWidth, requiredHeight), color=(200, 200, 200)),
                size=(requiredWidth, requiredHeight)
            )

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
