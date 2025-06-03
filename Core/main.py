import threading

from .audio import AudioThreadManager
from .authentication import Authentication
from .camera import Camera
from .person import person
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
            "str_person_table": "person_details",
            "str_person_tracking_table": "person_tracking_details",
            "str_event_details_table": "event_details",
            "str_camera_details": "Camera_Details",
            "str_person_tabel": "personregister"
        }

        self.obj_Authentication = Authentication(self.dict_db_details, self.dict_user_data)
        self.obj_person = person(self.dict_db_details, self.dict_user_data)
        self.obj_event = Event(self.dict_db_details, self.dict_user_data)
        self.obj_Camera = Camera(self.dict_db_details, self.dict_user_data)

        if self.check_alpr_database(self.dict_db_details):

            print(f"\nDatabase '{self.dict_db_details["str_db_name"]}' created successfully.")
            if self.check_userdetails_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details["str_user_table"]}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details["str_user_table"]}' creation failed!")

            if self.check_persons_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details["str_person_table"]}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details["str_person_table"]}' creation failed!")

            if self.check_persons_tracking_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details["str_person_tracking_table"]}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details["str_person_tracking_table"]}' creation failed!")

            if self.check_camera_table(self.dict_db_details):
                print(f"\nTable '{self.dict_db_details["str_camera_details"]}' created successfully.")
            else:
                print(f"\nTable '{self.dict_db_details["str_camera_details"]}' creation failed!")


            if self.check_person_event_table(self.dict_db_details):
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

    def check_persons_table(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details["str_server"]};UID={dict_db_details["str_username"]};PWD={dict_db_details["str_password"]}",
                autocommit=True)
            cursor = connection.cursor()

            select_db_query = f"USE {dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?""",
                           (dict_db_details["str_person_table"],))
            bool_table_exists = cursor.fetchone() is not None

            if not bool_table_exists:
                create_query = f"""CREATE TABLE {self.dict_db_details["str_person_table"]} (
                                  person_number varchar(50) PRIMARY KEY,
                                  added_by INT NOT NULL,
                                  person_company VARCHAR(50) NOT NULL,
                                  person_model VARCHAR(50) NOT NULL,
                                  person_type VARCHAR(50) NOT NULL,
                                  person_color VARCHAR(20) NOT NULL,
                                  person_owner VARCHAR(50) NOT NULL,
                                  manufacturing_year INT NOT NULL,
                                  FOREIGN KEY (added_by) REFERENCES user_details(user_id)
								  )"""
                cursor.execute(create_query)

            cursor.close()
            connection.close()
            return True

        except:
            return False

    def check_persons_tracking_table(self, dict_db_details: dict) -> bool:
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={dict_db_details["str_server"]};UID={dict_db_details["str_username"]};PWD={dict_db_details["str_password"]}",
                autocommit=True)
            cursor = connection.cursor()

            select_db_query = f"USE {dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?""",
                           (dict_db_details["str_person_tracking_table"],))
            bool_table_exists = cursor.fetchone() is not None

            if not bool_table_exists:
                create_query = f"""
                                  CREATE TABLE {self.dict_db_details["str_person_tracking_table"]} (
                                  person_Id VARCHAR(25) PRIMARY KEY,       -- Primary key column for person_Id
                                  Tracking_Id BIGINT,                       -- Tracking Id of the person
                                  person_img_1 VARCHAR(MAX),               -- Image 1 of the person
                                  person_img_2 VARCHAR(MAX),               -- Image 2 of the person
                                  person_img_3 VARCHAR(MAX),               -- Image 3 of the person
                                  person_img_4 VARCHAR(MAX),               -- Image 4 of the person
                                  person_img_5 VARCHAR(MAX),               -- Image 5 of the person
                                  Entry_Exit_Status INT,                    -- Entry/Exit status of the person (binary value)
                                  Flag BIT,                                 -- Flag (binary value)
                                  Time DATETIME                             -- Timestamp of the person entry/exit event
                                  );
                                  """
                cursor.execute(create_query)

            cursor.close()
            connection.close()
            return True

        except Exception as e:
            print(e)
            return False

    def check_person_event_table(self, dict_db_details: dict) -> bool:
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
                                person_name VARCHAR(50),                     -- Person name
                                person_img VARCHAR(MAX),                       -- Person image
                                captured_img VARCHAR(MAX),                  -- Captured image  
                                start_time bigint,                             --Timestamp for start time
                                end_time bigint,                            --Timestamp for end time
                                age VARCHAR(20),                              -- Person's age
                                gender VARCHAR(20),                           -- Person's gender
                                person_type VARCHAR(20),                     -- Person type
                                acknowledgment_time bigint,               -- Time of acknowledgment
                                acknowledgment_message VARCHAR(200)         -- Acknowledgment message
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