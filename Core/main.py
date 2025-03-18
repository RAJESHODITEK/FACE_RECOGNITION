import threading

from .audio import AudioThreadManager
from .authentication import Authentication
from .camera import Camera
from .vehicle import Vehicle
from .event import Event
import pyodbc


class Core:

    def __init__(self):

        self.dict_user_data = {
            "i_user_id": "",
            "str_user_name": "",
            "str_email_id": "",
            "str_phone_number": "",
            "str_password": ""
        }

        self.dict_db_details = {
            "str_server": "ITDT14",
            "str_username": "sa",
            "str_password": "root1234",
            "str_db_name": "FR_DB_NEW",
            "str_user_table": "user_details",
            # "str_vehicle_table": "vehicle_details",
            # "str_vehicle_tracking_table": "vehicle_tracking_details",
            "str_event_details_table": "event_details",
            # "str_camera_details": "Camera_Details",
            "str_persion_tabel": "personregister"
           
        }

        self.obj_Authentication = Authentication(self.dict_db_details, self.dict_user_data)
        self.obj_Vehicle = Vehicle(self.dict_db_details, self.dict_user_data)
        self.obj_event = Event(self.dict_db_details, self.dict_user_data)
        self.obj_Camera = Camera(self.dict_db_details, self.dict_user_data)

        if self.check_alpr_database(self.dict_db_details):
            print("================================HELLO WORLD!================================")
            print(f"\nDatabase '{self.dict_db_details["str_db_name"]}' created successfully.")
            if self.check_userdetails_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details["str_user_table"]}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details["str_user_table"]}' creation failed!")

            if self.check_persion_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details["str_persion_tabel"]}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details["str_persion_tabel"]}' creation failed!")

            # if self.check_vehicles_table(self.dict_db_details):
            #     print(f"\nTable '{self.dict_db_details["str_vehicle_table"]}' created successfully.")
            # else:
            #     print(f"\nTable '{self.dict_db_details["str_vehicle_table"]}' creation failed!")

            # if self.check_vehicles_tracking_table(self.dict_db_details):
            #     print(f"\nTable '{self.dict_db_details["str_vehicle_tracking_table"]}' created successfully.")
            # else:
            #     print(f"\nTable '{self.dict_db_details["str_vehicle_tracking_table"]}' creation failed!")

            if self.check_vehicle_event_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details["str_event_details_table"]}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details["str_event_details_table"]}' creation failed!")

        else:
            print(f"\nDatabase '{self.dict_db_details["str_db_name"]}' creation failed!")

    def check_alpr_database(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details["str_server"]};UID={dict_db_details["str_username"]};PWD={dict_db_details["str_password"]}",
                autocommit=True)
            cursor = connection.cursor()
            cursor.execute(f"SELECT name FROM sys.databases WHERE name = ?", (dict_db_details["str_db_name"]))
            bool_db_exists = cursor.fetchone() is not None

            if not bool_db_exists:
                cursor.execute(f"CREATE DATABASE {dict_db_details["str_db_name"]}")

            cursor.close()
            connection.close()
            return True

        except:
            return False

    def check_userdetails_table(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details["str_server"]};UID={dict_db_details["str_username"]};PWD={dict_db_details["str_password"]}",
                autocommit=True)
            cursor = connection.cursor()

            select_db_query = f"USE {dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?""",
                           (dict_db_details["str_user_table"],))
            bool_table_exists = cursor.fetchone() is not None

            if not bool_table_exists:
                create_query = f"""CREATE TABLE {self.dict_db_details["str_user_table"]} (
                                  user_id INT PRIMARY KEY IDENTITY(1,1),
                                  user_name VARCHAR(50) NOT NULL,
                                  email_id VARCHAR(50) UNIQUE NOT NULL,
                                  phone_number VARCHAR(15) UNIQUE NOT NULL,
                                  password VARCHAR(255) NOT NULL)
                                """
                cursor.execute(create_query)

            cursor.close()
            connection.close()
            return True

        except:
            return False
    

        
    
    def check_persion_table(self, dict_db_details: dict) -> bool:
        try:
            # Establish database connection
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details['str_server']};UID={dict_db_details['str_username']};PWD={dict_db_details['str_password']}",
                autocommit=True)
            cursor = connection.cursor()

            # Switch to the correct database
            select_db_query = f"USE {dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            # Check if the table exists
            cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?""",
                        (dict_db_details['str_person_table'],))
            bool_table_exists = cursor.fetchone() is not None

            # If the table doesn't exist, create it
            if not bool_table_exists:
                create_query = f"""CREATE TABLE {dict_db_details['str_person_table']} (
                                full_name VARCHAR(255) NOT NULL,
                                middle_name VARCHAR(50) NULL,  -- middle_name can be NULL
                                age INT NOT NULL,
                                gender VARCHAR(10) NOT NULL,
                                status VARCHAR(20) NOT NULL,
                                photo_path VARCHAR(MAX) NOT NULL  -- photo_path can be NULL if no photo is provided
                                );"""
                cursor.execute(create_query)

            # Close the cursor and connection
            cursor.close()
            connection.close()
            
            return True  # Table creation successful or table exists

        except Exception as e:
            print(f"Error: {e}")
            return False  # Error occurred during execution

    def check_vehicles_tracking_table(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details["str_server"]};UID={dict_db_details["str_username"]};PWD={dict_db_details["str_password"]}",
                autocommit=True)
            cursor = connection.cursor()

            select_db_query = f"USE {dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?""",
                           (dict_db_details["str_vehicle_tracking_table"],))
            bool_table_exists = cursor.fetchone() is not None

            if not bool_table_exists:
                create_query = f"""
                                  CREATE TABLE {self.dict_db_details["str_vehicle_tracking_table"]} (
                                  Vehicle_Id VARCHAR(25) PRIMARY KEY,       -- Primary key column for Vehicle_Id
                                  Tracking_Id BIGINT,                       -- Tracking Id of the vehicle
                                  Vehicle_img_1 VARCHAR(MAX),               -- Image 1 of the vehicle
                                  Vehicle_img_2 VARCHAR(MAX),               -- Image 2 of the vehicle
                                  Vehicle_img_3 VARCHAR(MAX),               -- Image 3 of the vehicle
                                  Vehicle_img_4 VARCHAR(MAX),               -- Image 4 of the vehicle
                                  Vehicle_img_5 VARCHAR(MAX),               -- Image 5 of the vehicle
                                  Entry_Exit_Status INT,                    -- Entry/Exit status of the vehicle (binary value)
                                  Flag BIT,                                 -- Flag (binary value)
                                  Time DATETIME                             -- Timestamp of the vehicle entry/exit event
                                  );
                                  """
                cursor.execute(create_query)

            cursor.close()
            connection.close()
            return True

        except Exception as e:
            print(e)
            return False

    def check_vehicle_event_table(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details["str_server"]};UID={dict_db_details["str_username"]};PWD={dict_db_details["str_password"]}",
                autocommit=True)
            cursor = connection.cursor()

            select_db_query = f"USE {dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?""",
                           (dict_db_details["str_event_details_table"],))
            bool_table_exists = cursor.fetchone() is not None

            if not bool_table_exists:
                create_query = f"""
                                CREATE TABLE {self.dict_db_details["str_event_details_table"]} (
                                event_id INT IDENTITY(1,1) PRIMARY KEY,         -- Auto-incremented primary key
                                vehicle_number VARCHAR(50),                     -- Registration number
                                number_plate_color VARCHAR(30),                 -- Plate color
                                country VARCHAR(50),                            -- Country
                                vehicle_img VARCHAR(MAX),                       -- Vehicle image
                                number_plate_img VARCHAR(MAX),                  -- License plate image
                                is_recognized BIT,                              -- Recognition flag (1 for recognized, 0 for not)
                                time DATETIME,                                  -- Timestamp for the recognition
                                status  VARCHAR(10)                             -- Status flag (1 for active, 0 for inactive)
                                );
                                """
                cursor.execute(create_query)

            cursor.close()
            connection.close()
            return True

        except Exception as e:
            print(e)
            return False

    def check_camera_table(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details["str_server"]};UID={dict_db_details["str_username"]};PWD={dict_db_details["str_password"]}",
                autocommit=True)
            cursor = connection.cursor()

            select_db_query = f"USE {dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?""",
                           (dict_db_details["str_camera_details"],))
            bool_table_exists = cursor.fetchone() is not None

            if not bool_table_exists:
                create_query = f"""CREATE TABLE {self.dict_db_details["str_vehicle_table"]} (
                                       vehicle_number varchar(50) PRIMARY KEY,
                                       added_by INT NOT NULL,
                                       vehicle_company VARCHAR(50) NOT NULL,
                                       vehicle_model VARCHAR(50) NOT NULL,
                                       vehicle_type VARCHAR(50) NOT NULL,
                                       vehicle_color VARCHAR(20) NOT NULL,
                                       vehicle_owner VARCHAR(50) NOT NULL,
                                       manufacturing_year INT NOT NULL,
                                       FOREIGN KEY (added_by) REFERENCES user_details(user_id)
     								  )"""
                cursor.execute(create_query)

            cursor.close()
            connection.close()
            return True

        except:
            return False