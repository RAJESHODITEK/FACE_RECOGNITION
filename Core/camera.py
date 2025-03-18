import json

import pyodbc
import datetime


class Camera():

    def __init__(self, dict_db_details, dict_user_data):

        self.dict_db_details = dict_db_details
        self.dict_user_data = dict_user_data

        super().__init__()

    def add_camera(self, camera_data):
        """
        Adds a new camera's data to the database.
        :param camera_data: A dictionary containing the camera's details.
        """
        cursor = None

        try:
            # Connect to the database
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                            SERVER={self.dict_db_details["str_server"]};
                                            UID={self.dict_db_details["str_username"]};
                                            PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()

            # Prepare the query to insert camera data
            insert_query = f"""
            INSERT INTO [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_camera_details"]}]
            (Camera_name, URL, Camera_direction, ROIStartPercentageHeight, ROIEndPercentageHeight,ROIStartPercentageWidth,ROIEndPercentageWidth)
            VALUES (?, ?, ?, ?, ?,?,?)
            """

            # Execute the insert query
            cursor.execute(insert_query, (
                camera_data["Camera_name"],
                camera_data["URL"],
                camera_data["Camera_direction"],
                camera_data["ROIStartPercentage"],
                camera_data["ROIEndPercentage"],
                15,90
            ))

            # print(f"Camera {camera_data['Camera_name']} added successfully.")
            return True
        except pyodbc.InterfaceError as e:
            # Handle database interface errors (e.g., issues with the connection)
            # print(f"Database interface error: {e}")
            return False
        except pyodbc.DatabaseError as e:
            # Handle database-related errors (e.g., issues with executing the query)
            # print(f"Database error: {e}")
            return False
        except pyodbc.OperationalError as e:
            # Handle operational errors (e.g., issues with connecting to the server)
            # print(f"Operational error: {e}")
            return False
        except pyodbc.Error as e:
            # General pyodbc errors
            # print(f"SQL execution error: {e}")
            return False
        except KeyError as e:
            # Handle missing keys in the camera_data dictionary
            # print(f"Missing expected field in camera data: {e}")
            return False
        except Exception as e:
            # Catch all other exceptions
            # print(f"An unexpected error occurred: {e}")
            return False
        finally:
            # Clean up and close the connection
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def fetch_all_Camera_data(self):
        cursor = None
        try:
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                        SERVER={self.dict_db_details["str_server"]};
                                        UID={self.dict_db_details["str_username"]};
                                        PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()
            select_all_query = f"""SELECT * FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_camera_details"]}]"""
            cursor.execute(select_all_query)
            rows = cursor.fetchall()

            # Create list of dictionaries properly
            columns = [column[0] for column in cursor.description]
            camera_list = [
                {columns[i]: row[i] for i in range(len(columns))}
                for row in rows
            ]
            return camera_list
        except Exception as e:
            # print(f"Error fetching camera data: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
                connection.close()

    def get_camera_count(self):
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

            data_count_query = f"""SELECT COUNT(*) FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_camera_details"]}] """
            cursor.execute(data_count_query)
            result = cursor.fetchone()
            i_data_count = int(result[0])

        except Exception as e:
            pass

        finally:
            cursor.close()
            connection.close()

        return i_data_count

    def add_roi_coordinates(self, camera_name: str, start_y_percentage: float, end_y_percentage: float,
                            start_x_percentage: float, end_x_percentage: float, coordinates: dict = None):
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": ""
        }
        try:
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                           SERVER={self.dict_db_details["str_server"]};
                                           UID={self.dict_db_details["str_username"]};
                                           PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            # Convert coordinates dictionary to JSON string if not None
            coordinates_json = json.dumps(coordinates) if coordinates is not None else None

            if coordinates_json:
                # Update with ROI coordinates
                update_query = f"""UPDATE [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_camera_details"]}]
                                     SET ROIStartPercentageHeight = ?, 
                                         ROIEndPercentageHeight = ?,
                                         ROIStartPercentageWidth = ?,
                                         ROIEndPercentageWidth = ?,
                                         ROICoordinates = ?
                                     WHERE Camera_name = ?"""
                cursor.execute(update_query, start_y_percentage, end_y_percentage, start_x_percentage,
                               end_x_percentage, coordinates_json, camera_name)
            else:
                # Update only ROI percentages
                update_query = f"""UPDATE [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_camera_details"]}]
                                     SET ROIStartPercentageHeight = ?, 
                                         ROIEndPercentageHeight = ?,
                                         ROIStartPercentageWidth = ?,
                                         ROIEndPercentageWidth = ?
                                     WHERE Camera_name = ?"""
                cursor.execute(update_query, start_y_percentage, end_y_percentage, start_x_percentage, end_x_percentage,
                               camera_name)

            if cursor.rowcount == 0:
                dict_status["str_error_msg_heading"] = "Error! Camera not found"
                dict_status["str_error_msg"] = f"No camera found with name: {camera_name}"

        except pyodbc.Error as e:
            dict_status["str_error_msg_heading"] = "Error! Database operation failed"
            dict_status["str_error_msg"] = f"Database error: {str(e)}"
            # print(e)
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Something went wrong. Please contact support team."
            # print(e)
        finally:
            cursor.close()
            connection.close()
        return dict_status

    def fetch_all_ROI_data(self):
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": "",
            "data": []
        }
        try:
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                               SERVER={self.dict_db_details["str_server"]};
                                               UID={self.dict_db_details["str_username"]};
                                               PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            # Fetch ROI data with updated column names
            fetch_query = f"""SELECT Camera_name, ROIStartPercentageHeight, ROIEndPercentageHeight, 
                                        ROIStartPercentageWidth, ROIEndPercentageWidth, ROICoordinates
                                 FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_camera_details"]}]"""
            cursor.execute(fetch_query)

            # Fetch the data
            rows = cursor.fetchall()

            if rows:
                # Add data to the result dictionary
                dict_status["data"] = [{
                    "Camera_name": row[0],
                    "ROIStartPercentageHeight": row[1],
                    "ROIEndPercentageHeight": row[2],
                    "ROIStartPercentageWidth": row[3],
                    "ROIEndPercentageWidth": row[4],
                    "ROICoordinates": row[5]
                } for row in rows]
            else:
                dict_status["str_error_msg_heading"] = "No data found"
                dict_status["str_error_msg"] = "No ROI data found in the database"

        except pyodbc.Error as e:
            dict_status["str_error_msg_heading"] = "Error! Database operation failed"
            dict_status["str_error_msg"] = f"Database error: {str(e)}"
            # print(e)
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Something went wrong. Please contact support team."
            # print(e)
        finally:
            cursor.close()
            connection.close()

        return dict_status

    def rtsp_of_camera(self, cameraname):
        # print("camera name = ", cameraname)
        camera_data = ''
        cursor = None

        try:
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                        SERVER={self.dict_db_details["str_server"]};
                                        UID={self.dict_db_details["str_username"]};
                                        PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()
            # select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            # cursor.execute(select_db_query)
            select_all_query = f"""SELECT * FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_camera_details"]}] WHERE Camera_name ='{cameraname}' """
            cursor.execute(select_all_query)
            camera_data = cursor.fetchone()
            if camera_data:
                camera_rtsp = f'rtsp://{camera_data[3]}:{camera_data[4]}@{camera_data[1]}/{camera_data[2]}'
                # print("fetch data = ", camera_rtsp)
                return camera_rtsp

        except Exception as e:
            pass

        finally:
            cursor.close()
            connection.close()
        # print("fetch data = ", camera_data)
        return camera_data

    def update_camera(self, camera_data):
        """
        Updates an existing camera's data in the database.
        :param camera_data: A dictionary containing the camera's updated details.
                            The dictionary must include a unique identifier for the camera (e.g., Camera ID).
        """
        cursor = None

        try:
            # Connect to the database
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                            SERVER={self.dict_db_details["str_server"]};
                                            UID={self.dict_db_details["str_username"]};
                                            PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()

            # Ensure the camera_data dictionary includes the unique identifier for the camera
            if "Camera_name" not in camera_data:
                # print("Camera_name is required to update camera details.")
                return False

            # Prepare the query to update camera data
            update_query = f"""
            UPDATE [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_camera_details"]}]
            SET URL = ?, Camera_direction = ?
            WHERE Camera_name = ?
            """

            # Execute the update query
            cursor.execute(update_query, (
                camera_data["URL"],
                camera_data["Camera_direction"],
                camera_data["Camera_name"]
            ))

            # print(f"Camera with ID {camera_data['Camera_name']} updated successfully.")
            return True
        except pyodbc.InterfaceError as e:
            # Handle database interface errors (e.g., issues with the connection)
            # print(f"Database interface error: {e}")
            return False
        except pyodbc.DatabaseError as e:
            # Handle database-related errors (e.g., issues with executing the query)
            print(f"Database error: {e}")
            return False
        except pyodbc.OperationalError as e:
            # Handle operational errors (e.g., issues with connecting to the server)
            # print(f"Operational error: {e}")
            return False
        except pyodbc.Error as e:
            # General pyodbc errors
            # print(f"SQL execution error: {e}")
            return False
        except KeyError as e:
            # Handle missing keys in the camera_data dictionary
            # print(f"Missing expected field in camera data: {e}")
            return False
        except Exception as e:
            # Catch all other exceptions
            # print(f"An unexpected error occurred: {e}")
            return False
        finally:
            # Clean up and close the connection
            if cursor:
                cursor.close()
            if connection:
                connection.close()



    def delete_cameras(self, camera_names):
        """
        Deletes multiple cameras from the database.
        :param camera_names: A list of camera names to be deleted.
        """
        cursor = None

        if not camera_names:
            # print("No camera names provided for deletion.")
            return False

        try:
            # Connect to the database
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                            SERVER={self.dict_db_details["str_server"]};
                                            UID={self.dict_db_details["str_username"]};
                                            PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()

            # Prepare the query to delete camera data
            placeholders = ', '.join(['?'] * len(camera_names))
            delete_query = f"""
            DELETE FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_camera_details"]}]
            WHERE Camera_name IN ({placeholders})
            """

            # Execute the delete query
            cursor.execute(delete_query, camera_names)
            deleted_rows = cursor.rowcount  # Check how many rows were deleted

            if deleted_rows > 0:
                # print(f"Deleted {deleted_rows} cameras: {', '.join(camera_names)} successfully.")
                return True
            else:
                # print("No matching cameras found for deletion.")
                return False

        except pyodbc.InterfaceError as e:
            # print(f"Database interface error: {e}")
            return False
        except pyodbc.DatabaseError as e:
            # print(f"Database error: {e}")
            return False
        except pyodbc.OperationalError as e:
            # print(f"Operational error: {e}")
            return False
        except pyodbc.Error as e:
            # print(f"SQL execution error: {e}")
            return False
        except Exception as e:
            # print(f"An unexpected error occurred: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


