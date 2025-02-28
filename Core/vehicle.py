import pyodbc
import datetime

class Vehicle():

    def __init__(self, dict_db_details, dict_user_data):

        self.dict_db_details = dict_db_details
        self.dict_user_data = dict_user_data

        super().__init__()

    import pyodbc



    def add_vehicle(self, str_company : str, str_model : str,
                    str_type : str, str_number : str,
                    str_color : str,i_date : int,
                    str_owner, i_status):
        dict_status = {
            "str_error_msg_heading" : "",
            "str_error_msg" : ""
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
            insert_query = f"""INSERT INTO [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}]
                                (vehicle_number, added_by, vehicle_company, vehicle_model, vehicle_type, vehicle_color, vehicle_owner, manufacturing_year, vehicle_status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """
            cursor.execute(insert_query, str_number, int(self.dict_user_data["i_user_id"]), str_company, str_model, str_type, str_color, str_owner, int(i_date), i_status)
        except pyodbc.Error as e:
            if (e.args[0] == '23000' and "duplicate" in e.args[1]):
                dict_status["str_error_msg_heading"] = "Error! Duplicate Entries"
                dict_status["str_error_msg"] = "Duplicate vehicle not allowed."
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
        return  dict_status

    def fetch_vehicle_details(self, dict_filter_criteria: dict):

        list_vehicle = []

        try:
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                        SERVER={self.dict_db_details["str_server"]};
                                        UID={self.dict_db_details["str_username"]};
                                        PWD={self.dict_db_details["str_password"]}""",
                                        autocommit=True)
            cursor = connection.cursor()
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)

            select_all_query = f"""SELECT vehicle_number, vehicle_type, vehicle_color, vehicle_owner, manufacturing_year, vehicle_company, vehicle_model, vehicle_status FROM 
                                    [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}] 
                                    WHERE vehicle_owner LIKE ? AND vehicle_type LIKE ? AND vehicle_color LIKE ?"""
            cursor.execute(select_all_query, dict_filter_criteria["str_owner"], dict_filter_criteria["str_type"],
                           dict_filter_criteria["str_color"])
            vehicles_list = cursor.fetchall()

            if vehicles_list:
                columns = [column[0] for column in cursor.description]  # Fetch column names
                for data in vehicles_list:
                    record_dict = {columns[i]: data[i] for i in range(len(columns))}  # Map columns to data
                    list_vehicle.append(record_dict)

        except Exception as e:
            pass

        finally:
            cursor.close()
            connection.close()

        return list_vehicle

    def fetch_single_vehicle_data(self, str_vehicle: str):
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": "",
            "vehicle_data": None
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

            fetch_query = f"""SELECT * FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}]
                               WHERE vehicle_number = ?"""
            cursor.execute(fetch_query, str_vehicle)
            row = cursor.fetchone()

            if row:
                dict_status["vehicle_data"] = row
            else:
                dict_status["str_error_msg_heading"] = "Error! Vehicle Not Found"
                dict_status["str_error_msg"] = "No vehicle found with the given number. Please check and try again."

        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = e

        finally:
            cursor.close()
            connection.close()

        return dict_status

    def get_data_count(self, dict_filter_criteria : dict):
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
            
            data_count_query = f"""SELECT COUNT(*) FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}] WHERE vehicle_owner LIKE ? AND vehicle_type LIKE ? AND vehicle_color LIKE ? """
            cursor.execute(data_count_query, dict_filter_criteria["str_owner"], dict_filter_criteria["str_type"], dict_filter_criteria["str_color"])
            result = cursor.fetchone()
            i_data_count = int(result[0])

        except Exception as e:
            pass

        finally:
            cursor.close()
            connection.close()

        return  i_data_count


    def sort_vehicle_data(self, list_vehicle_data: list, str_column: str, bool_sort_type: bool):
        if (str_column == "manufacturing_year"):
            list_vehicle = sorted(list_vehicle_data, key=lambda x: x[str_column], reverse=bool_sort_type)
        else:
            list_vehicle = sorted(list_vehicle_data, key=lambda x: x[str_column].upper(), reverse=bool_sort_type)
        return list_vehicle


    def search_vehicle_number(self, list_vehicle_data : list, str_vehicle_number : str):
        list_vehicle = []
        
        for data in list_vehicle_data:
            if(str_vehicle_number in data["vehicle_number"]):
                list_vehicle.append(data)

        return  list_vehicle

    def search_vehicle_owner(self, str_vehicle_owner: str):
        list_owner = []
        dict_status = self.get_all_vehicle_owner()

        for data in dict_status["list_owner"]:
            # Assuming 'name' is the key for the owner's name and 'data' is a dictionary
            owner_name = data.upper()  # Convert to uppercase for case-insensitive comparison

            if str_vehicle_owner.upper() in owner_name:  # Compare in uppercase for case-insensitive search
                list_owner.append(data)

        return list_owner

    def search_vehicle_type(self, str_vehicle_type: str):
        list_type = []
        dict_status = list(["Personal", "Truck", "Motorcycle", "Bus", "Van", "Auto", "Taxi"])

        for data in dict_status:
            # Assuming 'name' is the key for the owner's name and 'data' is a dictionary
            vehicle_type = data.upper()  # Convert to uppercase for case-insensitive comparison

            if str_vehicle_type.upper() in vehicle_type:  # Compare in uppercase for case-insensitive search
                list_type.append(data)

        return list_type
    def search_vehicle_company(self, str_vehicle_company: str):
        list_company = []
        dict_status = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen", "Hyundai", "Nissan"]

        for data in dict_status:
            # Assuming 'name' is the key for the owner's name and 'data' is a dictionary
            company_name = data.upper()  # Convert to uppercase for case-insensitive comparison

            if str_vehicle_company.upper() in company_name:  # Compare in uppercase for case-insensitive search
                list_company.append(data)

        return list_company

    def search_vehicle_color(self, str_vehicle_color: str):
        list_color = []
        dict_status = self.get_all_vehicle_color()

        for data in dict_status["list_color"]:
            # Assuming 'name' is the key for the owner's name and 'data' is a dictionary
            vehicle_color = data.upper()  # Convert to uppercase for case-insensitive comparison

            if str_vehicle_color.upper() in vehicle_color:  # Compare in uppercase for case-insensitive search
                list_color.append(data)

        return list_color


    def delete_vehicle(self, str_vehicle : str, str_password : str):
        dict_status = {
            "str_error_msg_heading" : "",
            "str_error_msg" : ""
            }
        
        if(str_password != self.dict_user_data["str_password"]):
            dict_status["str_error_msg_heading"] = "Error! Incorrect Password"
            dict_status["str_error_msg"] = "The password that you've entered is incorrect. Please try again."
            return dict_status
        
        try:
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                        SERVER={self.dict_db_details["str_server"]};
                                        UID={self.dict_db_details["str_username"]};
                                        PWD={self.dict_db_details["str_password"]}""", 
                                        autocommit=True)
            cursor = connection.cursor()
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)
            delete_query = f"""DELETE FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}]
                                WHERE vehicle_number = ?
                            """
            cursor.execute(delete_query, str_vehicle)
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Something went wrong. Please contact with support team."
        finally:
            cursor.close()
            connection.close()
        return  dict_status
    

    def delete_vechiles(self, vehicle_names):
        
        cursor = None
 
        if not vehicle_names:
            print("No camera names provided for deletion.")
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
            placeholders = ', '.join(['?'] * len(vehicle_names))
            delete_query = f"""
            DELETE FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}]
            WHERE vehicle_number IN ({placeholders})
            """
 
            # Execute the delete query
            cursor.execute(delete_query, vehicle_names)
 
            print(f"Deleted vechile: {', '.join(vehicle_names)} successfully.")
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

    
    def get_user_added_vehicles(self):
        dict_status = {
                "str_error_msg_heading" : "",
                "str_error_msg" : "",
                "list_vehicles" : []
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
            # fetch_vehicle_query = f"""SELECT vehicle_number FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}]
            #                     WHERE added_by = ?
            #                 """
            fetch_vehicle_query = f"""SELECT vehicle_number FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}]
                                           
                                       """
            cursor.execute(fetch_vehicle_query)
            vehicles_list = cursor.fetchall()
            if vehicles_list:
                for data in vehicles_list:
                   dict_status["list_vehicles"].append(data.vehicle_number)
            else:
                dict_status["str_error_msg_heading"] = "No Data Found"
                dict_status["str_error_msg"] = "You have's entered any vehciles data yet."
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Unable to fetch the user added vehicles from Database."
        finally:
            cursor.close()
            connection.close()
        return  dict_status
        

    def get_all_vehicle_owner(self):
        dict_status = {
                "str_error_msg_heading" : "",
                "str_error_msg" : "",
                "list_owner" : []
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
            fetch_owner_query = f"""SELECT DISTINCT  vehicle_owner FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}]"""
            cursor.execute(fetch_owner_query)
            owner_list = cursor.fetchall()
            if owner_list:
                for data in owner_list:
                   dict_status["list_owner"].append(data.vehicle_owner)
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Unable to fetch the owners list."
        finally:
            cursor.close()
            connection.close()
        return  dict_status
    

    def get_all_vehicle_type(self):
        dict_status = {
                "str_error_msg_heading" : "",
                "str_error_msg" : "",
                "list_type" : []
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
            fetch_type_query = f"""SELECT DISTINCT  vehicle_type FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}]"""
            cursor.execute(fetch_type_query)
            type_list = cursor.fetchall()
            if type_list:
                for data in type_list:
                   dict_status["list_type"].append(data.vehicle_type)
        except Exception as e:
            dict_status["str_error_msg_heading"] = "Error! Something went wrong"
            dict_status["str_error_msg"] = "Unable to fetch the vehicle types."
        finally:
            cursor.close()
            connection.close()
        return  dict_status


    def get_all_vehicle_color(self):
            dict_status = {
                    "str_error_msg_heading" : "",
                    "str_error_msg" : "",
                    "list_color" : []
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
                fetch_color_query = f"""SELECT DISTINCT  vehicle_color FROM [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}]"""
                cursor.execute(fetch_color_query)
                color_list = cursor.fetchall()
                if color_list:
                    for data in color_list:
                        dict_status["list_color"].append(data.vehicle_color)
            except Exception as e:
                dict_status["str_error_msg_heading"] = "Error! Something went wrong"
                dict_status["str_error_msg"] = "Unable to fetch vehicle colors."
            finally:
                cursor.close()
                connection.close()
            return  dict_status


    def validate_company(self, str_company : str) -> str:
        if str_company == "Select an option":
            return "ⓘ Company name can't be empty"
        return ""
    

    def validate_model(self, str_model : str) -> str:
        if len(str_model) == 0:
            return "ⓘ Model name can't be empty"
        return ""
        

    def validate_type(self, str_type : str) -> str:
        if str_type == "Select an option":
            return "ⓘ Vehicle type can't be empty"
        return ""


    def validate_number(self, str_number : str) -> str:
        if len(str_number) == 0:
            return "ⓘ Vehicle number can't be empty"
        return ""
    

    def validate_color(self, str_color : str) -> str:
        if len(str_color) == 0:
            return "ⓘ Vehicle color can't be empty"
        return ""


    def validate_date(self, str_date : str) -> str:
        if len(str_date) == 0:
            return "ⓘ Manufacturing date can't be empty"
        if len(str_date) != 4:
            return "ⓘ Invalid year"
        if not str_date.isdigit():
            return "ⓘ Invalid year"
        current_year = datetime.datetime.now().year
        past_50_year = current_year - 50
        input_year = int(str_date)
        if(input_year > current_year or past_50_year > input_year):
            return f"ⓘ Year must be with in {past_50_year} - {current_year}"
        return ""
        

    def validate_owner(self, str_owner : str) -> str:
        if len(str_owner) == 0:
            return "ⓘ Owner name can't be empty"
        return ""
    

    def validate_user_vehicle(self, str_user_vehicle : str) -> str:
        if str_user_vehicle == "Select an option":
            return "ⓘ Company name can't be empty"
        return ""
    

    def validate_password(self, str_user_password : str) -> str:
        if str_user_password == "":
            return "ⓘ Password can't be empty"
        return ""
    


    def update_vehicle(self, str_company, str_model, 
                   str_type, str_number,
                   str_color, date,
                   str_owner, str_blacklist, added_by):
    
        dict_status = {
            "str_error_msg_heading": "",
            "str_error_msg": ""
        }
        
        try:
            # Use Windows Authentication (Trusted Connection) for connection to the database
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                            SERVER={self.dict_db_details["str_server"]};
                                            UID={self.dict_db_details["str_username"]};
                                            PWD={self.dict_db_details["str_password"]}""", 
                                            autocommit=True)
            cursor = connection.cursor()
            select_db_query = f"USE {self.dict_db_details['str_db_name']};"
            cursor.execute(select_db_query)
            
            # Update query
            update_query = f"""UPDATE [{self.dict_db_details["str_db_name"]}].[dbo].[{self.dict_db_details["str_vehicle_table"]}]
                            SET vehicle_company = ?, 
                                vehicle_model = ?, 
                                vehicle_type = ?, 
                                vehicle_color = ?, 
                                vehicle_owner = ?, 
                                manufacturing_year = ?, 
                                vehicle_status = ?
                            WHERE vehicle_number = ?"""
            
            # Execute the update query with the provided parameters
            cursor.execute(update_query, 
                        str_company, str_model, str_type, 
                        str_color, str_owner, int(date), 
                        int(str_blacklist), 
                        str_number)  # Use the vehicle_number to identify the vehicle
         
            
        except pyodbc.Error as e:
            print(e)
            if (e.args[0] == '23000' and "duplicate" in e.args[1]):
                dict_status["str_error_msg_heading"] = "Error! Duplicate Entries"
                dict_status["str_error_msg"] = "Duplicate vehicle not allowed."
            else:
                dict_status["str_error_msg_heading"] = "Error! Something went wrong"
                dict_status["str_error_msg"] = "Something went wrong. Please verify the inputs and try again."
        except Exception as e:
                print(e)
                dict_status["str_error_msg_heading"] = "Error! Something went wrong"
                dict_status["str_error_msg"] = "Something went wrong. Please contact support."
        finally:
            
            pass
            # cursor.close()
            # connection.close()
        
        return dict_status


                