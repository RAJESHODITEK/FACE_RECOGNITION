from base64 import b64decode
import base64
import io
from pickletools import uint8
from tkinter import Image
# from tkinter import Image
from customtkinter import CTkImage
from cv2 import IMREAD_COLOR, imdecode
from numpy import frombuffer
import pyodbc
import datetime


class person():

    def __init__(self, dict_db_details, dict_user_data):

        self.dict_db_details = dict_db_details
        self.dict_user_data = dict_user_data

        super().__init__()

    def base64_to_tkinter_image(self, base64_image, requiredWidth, requiredHeight):
        # Decode the base64 string to get the raw bytes
        image_data = base64.b64decode(base64_image)

        # Convert the raw bytes to a PIL Image object
        image = Image.open(io.BytesIO(image_data))

        # Resize the image to the required width and height
        image_resized = image.resize((requiredWidth, requiredHeight), Image.Resampling.LANCZOS)

        # Convert the PIL Image object to a Tkinter-compatible photo image
        tkinter_image = Image.PhotoImage(image_resized)

        return tkinter_image

    def add_person(self,id:int,str_first_name: str, str_middle_name: str, str_last_name: str,
                    str_age: int, str_gender: str, str_status: str,
                    str_photo_path: str,str_photo_path2: str,str_photo_path3: str,str_photo_path4: str,str_photo_path5: str, mean_encode):
        print("db is here ")
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": ""
        }
        mean_encode = ','.join(map(str, mean_encode))
        try:
            print("db is connected")
            # Connect to the database
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                                SERVER={self.dict_db_details["str_server"]};
                                                UID={self.dict_db_details["str_username"]};
                                                PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()

            # Select the database
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            # Combine first and last name for full name
            if str_middle_name != "":
                full_name = str_first_name + " " + str_middle_name + " " + str_last_name
            else:
                full_name = str_first_name + " " + str_last_name

            # Insert query for the personregister table
            insert_query = f"""INSERT INTO [{self.dict_db_details["str_db_name"]}].[dbo].[personregister]
                                    (id,full_name, age, gender, status, photo_path,photo_path2, photo_path3, photo_path4,photo_path5,mean_image)
                                    VALUES (?,?, ?, ?, ?, ?,?,?,?,?,?)
                                """
            # Execute the insert query
            print("data is in insert query")
            cursor.execute(insert_query,id, full_name.upper(), int(str_age), str_gender, str_status,str_photo_path,str_photo_path2 ,str_photo_path3,str_photo_path4,str_photo_path5,mean_encode)
            print("db is inserted ")

            # Success message (could be optional)
            dict_status["str_error_msg_heading"] = "Success"
            dict_status["str_error_msg"] = "Person successfully added."

        except pyodbc.Error as e:
            print(e)
            if e.args[0] == '23000' and "duplicate" in e.args[1]:
                dict_status["str_error_msg_heading"] = "Error! Duplicate Entries"
                dict_status["str_error_msg"] = "Duplicate person not allowed."
            else:
                dict_status["str_error_msg_heading"] = "Error! Something went wrong"
                dict_status["str_error_msg"] = "Something went wrong. Please verify the inputs and try again."
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Something went wrong. Please contact with support team."
            print(e)
        finally:
            cursor.close()
            connection.close()

        return dict_status



    def fetch_person_details(self, dict_filter_criteria: dict):

        list_persons = []

        try:
            print("filter params : ",dict_filter_criteria)
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                    SERVER={self.dict_db_details["str_server"]};
                                    UID={self.dict_db_details["str_username"]};
                                    PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()

            # Select the database
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            # Query to select person details
            select_all_query = f"""SELECT TOP (500) [full_name], [age], [gender], [status], [photo_path],  [photo_path2],  [photo_path3], [photo_path4], [photo_path5],[id]
                                   FROM [FR_DB_NEW].[dbo].[personregister]
                                   WHERE gender LIKE ? AND status LIKE ?  AND full_name LIKE ?"""

            cursor.execute(select_all_query, [
                f"{dict_filter_criteria['gender']}%",
                f"%{dict_filter_criteria['status']}%",
                f"%{dict_filter_criteria['full_name']}%"
            ])

            # Fetch all the records
            persons_list = cursor.fetchall()

            if persons_list:
                columns = [column[0] for column in cursor.description]  # Fetch column names
                for data in persons_list:
                    record_dict = {columns[i]: data[i] for i in range(len(columns))}  # Map columns to data
                    # photo=self.base64_to_tkinter_image(data[4], 200, 135)

                    # print('row data is ',photo)
                    list_persons.append(record_dict)




        except Exception as e:
            # Handle exceptions (optional: log the error or re-raise)
            print(f"An error occurred: {e}")

        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()

        return list_persons

    def fetch_single_person_data(self, name: str, id= None):
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": "",
            "person_data": None
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
            if id is None:
                fetch_query = f"""SELECT * FROM [{self.dict_db_details["str_db_name"]}].[dbo].[personregister]
                                   WHERE name = ?"""
                cursor.execute(fetch_query, name)
            else:
                fetch_query = f"""SELECT * FROM [{self.dict_db_details["str_db_name"]}].[dbo].[personregister]
                                                   WHERE id = ?"""
                cursor.execute(fetch_query, id)


            row = cursor.fetchone()

            if row:
                dict_status["persion_data"] = row
            else:
                dict_status["str_error_msg_heading"] = "Error! Person Not Found"
                dict_status["str_error_msg"] = "No Face found with the given number. Please check and try again."

        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = e

        finally:
            cursor.close()
            connection.close()

        return dict_status


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

            data_count_query = f"""SELECT COUNT(*) FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_person_table"]}] WHERE person_owner LIKE ? AND person_type LIKE ? AND person_color LIKE ? """
            cursor.execute(data_count_query, dict_filter_criteria["str_owner"], dict_filter_criteria["str_type"],
                           dict_filter_criteria["str_color"])
            result = cursor.fetchone()
            i_data_count = int(result[0])

        except Exception as e:
            pass

        finally:
            cursor.close()
            connection.close()

        return i_data_count

    def sort_person_data(self, list_person_data: list, str_column: str, bool_sort_type: bool):
        list_person = sorted(list_person_data, key=lambda x: x[str_column], reverse=bool_sort_type)
        return list_person

    def search_person_number(self, list_person_data: list, str_person_number: str):
        print(str_person_number, "***********str_person_number")
        list_person = []

        for data in list_person_data:
            if (str_person_number in data["full_name"]):
                list_person.append(data)

        return list_person

    def search_person_owner(self, str_person_owner: str):
        list_owner = []
        dict_status = ['Male','Female','Other']

        for data in dict_status:
            # Assuming 'name' is the key for the owner's name and 'data' is a dictionary
            owner_name = data.upper()  # Convert to uppercase for case-insensitive comparison

            if str_person_owner.upper() in owner_name:  # Compare in uppercase for case-insensitive search
                list_owner.append(data)

        return list_owner

    def highest_id(self):
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

            data_count_query = f""" SELECT MAX(id) AS max_id FROM [FR_DB_NEW].[dbo].[personregister];"""
            cursor.execute(data_count_query)
            result = cursor.fetchone()
            i_data_count = int(result[0])

        except Exception as e:
            pass

        finally:
            cursor.close()
            connection.close()

        return i_data_count


    def search_person_type(self, str_person_type: str):
        list_type = []
        dict_status = ['WhiteList','BlackList']
        for data in dict_status:
            # Assuming 'name' is the key for the owner's name and 'data' is a dictionary
            person_type = data.upper()  # Convert to uppercase for case-insensitive comparison

            if str_person_type.upper() in person_type:  # Compare in uppercase for case-insensitive search
                list_type.append(data)

        return list_type

    def search_person_company(self, str_person_company: str):
        list_company = []
        dict_status = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen", "Hyundai", "Nissan"]

        for data in dict_status:
            # Assuming 'name' is the key for the owner's name and 'data' is a dictionary
            company_name = data.upper()  # Convert to uppercase for case-insensitive comparison

            if str_person_company.upper() in company_name:  # Compare in uppercase for case-insensitive search
                list_company.append(data)

        return list_company

    def search_person_color(self, str_person_color: str):
        list_color = []
        dict_status = self.get_all_person_color()

        for data in dict_status["list_color"]:
            # Assuming 'name' is the key for the owner's name and 'data' is a dictionary
            person_color = data.upper()  # Convert to uppercase for case-insensitive comparison

            if str_person_color.upper() in person_color:  # Compare in uppercase for case-insensitive search
                list_color.append(data)

        return list_color



    def delete_person(self, face_names):

        cursor = None

        if not face_names:
            print("No Face  names provided for deletion.")
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
            placeholders = ', '.join(['?'] * len(face_names))


            delete_query = f"""
            DELETE FROM [{self.dict_db_details["str_db_name"]}].[dbo].[personregister]
            WHERE full_name IN ({placeholders})
            """

            # Execute the delete query
            cursor.execute(delete_query, face_names)

            print(f"Deleted Persion: {', '.join(face_names)} successfully.")
            return True
        except pyodbc.InterfaceError as e:
            print(f"Database interface error: {e}")
            return False
        except pyodbc.DatabaseError as e:
            print(f"Database error: {e}")
            return False
        except pyodbc.OperationalError as e:
            print(f"Operational error: {e}")
            return False
        except pyodbc.Error as e:
            print(f"SQL execution error: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    def get_user_added_persons(self):
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": "",
            "list_persons": []
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
            # fetch_person_query = f"""SELECT person_number FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_person_table"]}]
            #                     WHERE added_by = ?
            #                 """
            fetch_person_query = f"""SELECT person_number FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_person_table"]}]

                                       """
            cursor.execute(fetch_person_query)
            persons_list = cursor.fetchall()
            if persons_list:
                for data in persons_list:
                    dict_status["list_persons"].append(data.person_number)
            else:
                dict_status["str_error_msg_heading"] = "No Data Found"
                dict_status["str_error_msg"] = "You have's entered any vehciles data yet."
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Unable to fetch the user added persons from Database."
        finally:
            cursor.close()
            connection.close()
        return dict_status

    def get_all_person_owner(self):
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": "",
            "list_owner": []
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
            fetch_owner_query = f"""SELECT DISTINCT  person_owner FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_person_table"]}]"""
            cursor.execute(fetch_owner_query)
            owner_list = cursor.fetchall()
            if owner_list:
                for data in owner_list:
                    dict_status["list_owner"].append(data.person_owner)
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Unable to fetch the owners list."
        finally:
            cursor.close()
            connection.close()
        return dict_status

    def get_all_person_type(self):
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": "",
            "list_type": []
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
            fetch_type_query = f"""SELECT DISTINCT  person_type FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_person_table"]}]"""
            cursor.execute(fetch_type_query)
            type_list = cursor.fetchall()
            if type_list:
                for data in type_list:
                    dict_status["list_type"].append(data.person_type)
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Unable to fetch the person types."
        finally:
            cursor.close()
            connection.close()
        return dict_status

    def get_all_person_color(self):
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": "",
            "list_color": []
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
            fetch_color_query = f"""SELECT DISTINCT  person_color FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_person_table"]}]"""
            cursor.execute(fetch_color_query)
            color_list = cursor.fetchall()
            if color_list:
                for data in color_list:
                    dict_status["list_color"].append(data.person_color)
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Unable to fetch person colors."
        finally:
            cursor.close()
            connection.close()
        return dict_status

    def validate_company(self, str_company: str) -> str:
        if str_company == "Select an option":
            return "ⓘ Company name can't be empty"
        return ""

    def validate_model(self, str_model: str) -> str:
        if len(str_model) == 0:
            return "ⓘ Model name can't be empty"
        return ""

    def validate_type(self, str_type: str) -> str:
        if str_type == "Select an option":
            return "ⓘ person type can't be empty"
        return ""

    def validate_number(self, str_number: str) -> str:
        if len(str_number) == 0:
            return "ⓘ person number can't be empty"
        return ""

    def validate_color(self, str_color: str) -> str:
        if len(str_color) == 0:
            return "ⓘ person color can't be empty"
        return ""

    def validate_date(self, str_date: str) -> str:
        if len(str_date) == 0:
            return "ⓘ Manufacturing date can't be empty"
        if len(str_date) != 4:
            return "ⓘ Invalid year"
        if not str_date.isdigit():
            return "ⓘ Invalid year"
        current_year = datetime.datetime.now().year
        past_50_year = current_year - 50
        input_year = int(str_date)
        if (input_year > current_year or past_50_year > input_year):
            return f"ⓘ Year must be with in {past_50_year} - {current_year}"
        return ""

    def validate_owner(self, str_owner: str) -> str:
        if len(str_owner) == 0:
            return "ⓘ Owner name can't be empty"
        return ""

    def validate_user_person(self, str_user_person: str) -> str:
        if str_user_person == "Select an option":
            return "ⓘ Company name can't be empty"
        return ""

    def validate_password(self, str_user_password: str) -> str:
        if str_user_password == "":
            return "ⓘ Password can't be empty"
        return ""

    def update_person(self, str_name: str,
                       str_age: int, str_gender: str, str_status: str,
                       str_photo_path1: str,str_photo_path2: str,str_photo_path3: str,str_photo_path4: str,str_photo_path5: str, str_id: int, added_by,mean_image):
        # print(str_name, str_age, str_gender, str_status, str_id, str_photo_path1,str_photo_path2,str_photo_path3,str_photo_path4,str_photo_path5,"******************")
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": ""
        }
        mean_image = ','.join(map(str, mean_image))
        try:
            print("db is connected")
            # Connect to the database
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                                SERVER={self.dict_db_details["str_server"]};
                                                UID={self.dict_db_details["str_username"]};
                                                PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()

            # Select the database
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)


            update_query = f"""UPDATE [{self.dict_db_details["str_db_name"]}].[dbo].[personregister]
                                SET full_name = ?, 
                                    age = ?, 
                                    gender = ?, 
                                    status = ?, 
                                   photo_path= ?,
                                    photo_path2= ?,
                                    photo_path3= ?,
                                    photo_path4= ?,
                                    photo_path5= ?,
                                    mean_image= ?
                                WHERE id = ?"""

            # Execute the update query with the provided parameters
            cursor.execute(update_query,
                           str_name.upper(), int(str_age), str_gender, str_status,
                           str_photo_path1,str_photo_path2,str_photo_path3,str_photo_path4,str_photo_path5,
                           mean_image,int(str_id))

        except pyodbc.Error as e:
            print(e)
            if (e.args[0] == '23000' and "duplicate" in e.args[1]):
                dict_status["str_error_msg_heading"] = "Error! Duplicate Entries"
                dict_status["str_error_msg"] = "Duplicate Person not allowed."
            else:
                dict_status["str_error_msg_heading"] = "Error! Something went wrong"
                dict_status["str_error_msg"] = "Something went wrong. Please verify the inputs and try again."
        except Exception as e:
            print(e)
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Something went wrong. Please contact support."
        finally:

            pass

        return dict_status
