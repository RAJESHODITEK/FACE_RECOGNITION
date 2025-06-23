import threading

from .audio import AudioThreadManager
from .authentication import Authentication
from .camera import Camera
from .vehicle import Vehicle
from .event import Event
import pyodbc
from Config.configloader import ConfigLoader


class Core:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Core, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return  # Prevent re-initialization

        self.config=ConfigLoader()

        self.dict_user_data = {
            "i_user_id": "",
            "str_user_name": "",
            "str_email_id": "",
            "str_phone_number": "",
            "str_password": ""
        }
        abcd=self.config.get('database','N/A')
        self.dict_db_details = {
            "str_server": abcd.get('server','N/A'),
            "str_username": abcd.get('user','N/A'),
            "str_password": abcd.get('password','N/A'),
            "str_db_name": abcd.get('db_name','N/A'),
            "str_user_table": "user_details",
            "str_vehicle_table": "vehicle_details",
            "str_vehicle_tracking_table": "vehicle_tracking_details",
            "str_event_details_table": "event_details",
            "str_camera_details": "Camera_Details",
            "str_missed_event_details_table": "missed_event_details"
        }

        self.obj_Authentication = Authentication(self.dict_db_details, self.dict_user_data)
        self.obj_Vehicle = Vehicle(self.dict_db_details, self.dict_user_data)
        self.obj_event = Event(self.dict_db_details, self.dict_user_data)
        self.obj_Camera = Camera(self.dict_db_details, self.dict_user_data)

        if self.check_alpr_database(self.dict_db_details):
            print(f"\nDatabase '{self.dict_db_details['str_db_name']}' created successfully.")
            if self.check_userdetails_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details['str_user_table']}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details['str_user_table']}' creation failed!")

            if self.check_vehicles_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details['str_vehicle_table']}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details['str_vehicle_table']}' creation failed!")

            if self.check_camera_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details['str_camera_details']}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details['str_camera_details']}' creation failed!")

            if self.check_missed_vehicle_event_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details['str_missed_event_details_table']}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details['str_missed_event_details_table']}' creation failed!")


            if self.check_vehicle_event_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details['str_event_details_table']}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details['str_event_details_table']}' creation failed!")
        else:
            print(f"\nDatabase '{self.dict_db_details['str_db_name']}' creation failed!")

        self.__initialized = True

    def check_alpr_database(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details['str_server']};UID={dict_db_details['str_username']};PWD={dict_db_details['str_password']}",
                autocommit=True)
            cursor = connection.cursor()
            cursor.execute(f"SELECT name FROM sys.databases WHERE name = ?", (dict_db_details['str_db_name']))
            bool_db_exists = cursor.fetchone() is not None

            if not bool_db_exists:
                cursor.execute(f"CREATE DATABASE {dict_db_details['str_db_name']}")

            cursor.close()
            connection.close()
            return True

        except:
            return False

    def check_userdetails_table(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details['str_server']};UID={dict_db_details['str_username']};PWD={dict_db_details['str_password']}",
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

                insert_query=   f"""
                                INSERT INTO [dbo].{self.dict_db_details["str_user_table"]}
                                ( [user_name], [email_id], [phone_number], [password]) 
                                VALUES 
                                ( 'admin', 'admin@example.com', '1234567890', 'admin');
                                """
                cursor.execute(insert_query)

            cursor.close()
            connection.close()
            return True

        except:
            return False

    def check_vehicles_table(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details['str_server']};UID={dict_db_details['str_username']};PWD={dict_db_details['str_password']}",
                autocommit=True)
            cursor = connection.cursor()

            select_db_query = f"USE {dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?""",
                           (dict_db_details["str_vehicle_table"],))
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
                                  vehicle_status INT NOT NULL,
                                  FOREIGN KEY (added_by) REFERENCES user_details(user_id),
                                  
								  )"""
                cursor.execute(create_query)

            cursor.close()
            connection.close()
            return True

        except:
            return False



    def check_vehicle_event_table(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details['str_server']};UID={dict_db_details['str_username']};PWD={dict_db_details['str_password']}",
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
                                vehicle_id VARCHAR(50),                         -- Concatenation of Camera name, event id and time
                                vehicle_number VARCHAR(50),                     -- Registration number
                                number_plate_color VARCHAR(30),                 -- Plate color
                                country VARCHAR(50),                            -- Country
                                vehicle_img VARCHAR(MAX),                       -- Vehicle image
                                number_plate_img VARCHAR(MAX),                  -- License plate image
                                is_recognized BIT,                              -- Recognition flag (1 for recognized, 0 for not)
                                time DATETIME,                                  -- Timestamp for the recognition
                                status  VARCHAR(10),                            -- Status (Entry or Exit)
                                alarm INT,                                      -- alarm flag (0 for unknown, 1 for verified, 2 for restricted)
                                acknowledgment_message VARCHAR(150),            -- acknowledgment message
                                acknowledgment_time DATETIME ,                  -- acknowledgment update time
                                object_type VARCHAR(50),
                                camera_name VARCHAR(50)
                                );
                                """
                cursor.execute(create_query)

            cursor.close()
            connection.close()
            return True

        except Exception as e:
            print(e)
            return False

    def check_missed_vehicle_event_table(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details['str_server']};UID={dict_db_details['str_username']};PWD={dict_db_details['str_password']}",
                autocommit=True)
            cursor = connection.cursor()

            select_db_query = f"USE {dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?""",
                           (dict_db_details["str_missed_event_details_table"],))
            bool_table_exists = cursor.fetchone() is not None

            if not bool_table_exists:
                create_query = f"""
                                   CREATE TABLE {self.dict_db_details["str_missed_event_details_table"]} (
                                   event_id INT IDENTITY(1,1) PRIMARY KEY,         -- Auto-incremented primary key
                                   vehicle_id VARCHAR(50),                         -- Concatenation of Camera name, event id and time
                                   vehicle_number VARCHAR(50),                     -- Registration number
                                   number_plate_color VARCHAR(30),                 -- Plate color
                                   country VARCHAR(50),                            -- Country
                                   vehicle_img VARCHAR(MAX),                       -- Vehicle image
                                   number_plate_img VARCHAR(MAX),                  -- License plate image
                                   is_recognized BIT,                              -- Recognition flag (1 for recognized, 0 for not)
                                   time DATETIME,                                  -- Timestamp for the recognition
                                   status  VARCHAR(10),                            -- Status (Entry or Exit)
                                   alarm INT,                                      -- alarm flag (0 for unknown, 1 for verified, 2 for restricted)
                                   acknowledgment_message VARCHAR(150),            -- acknowledgment message
                                   acknowledgment_time DATETIME                    -- acknowledgment update time
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
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details['str_server']};UID={dict_db_details['str_username']};PWD={dict_db_details['str_password']}",
                autocommit=True)
            cursor = connection.cursor()

            select_db_query = f"USE {dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?""",
                           (dict_db_details["str_camera_details"],))
            bool_table_exists = cursor.fetchone() is not None

            if not bool_table_exists:
                create_query = f"""CREATE TABLE {self.dict_db_details["str_camera_details"]} (
                                       Camera_name varchar(255) PRIMARY KEY,
                                       Camera_direction varchar(7) ,
                                       URL VARCHAR(255) NOT NULL,
                                       ROIStartPercentageHeight INT NOT NULL,
                                       ROIEndPercentageHeight INT NOT NULL,
                                       ROICoordinates varchar(300) ,
                                       ROIStartPercentageWidth INT NOT NULL,
                                       ROIEndPercentageWidth INT NOT NULL
     								  )"""
                cursor.execute(create_query)

            cursor.close()
            connection.close()
            return True

        except:
            return False