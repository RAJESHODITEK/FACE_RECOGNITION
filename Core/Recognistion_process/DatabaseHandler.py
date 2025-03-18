import random

import pyodbc


class DatabaseHandler:
    def __init__(self):

        self.event_details_table_name="[dbo].[event_details]"

        self.event_details_table_columns= [
            "vehicle_id",
            "vehicle_number",
            "number_plate_color",
            "country",
            "vehicle_img",
            "number_plate_img",
            "is_recognized",
            "time",
            "status",
            "alarm"
        ]

    @staticmethod
    def insert_data(connection, table_name: str, column_names: list, values: list):
        """
        this will insert the data in db
        :param connection this is connection of db
        :param table_name this is table name  of db
        :param column_names this is column names of table
        :param values this is values to insert in table
        :return boolean

        """
        placeholders = ", ".join(["?"] * len(column_names))
        columns = ", ".join(column_names)
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

        with connection.cursor() as cursor:
            try:
                cursor.execute(query, values)
                connection.commit()
                return True
            except Exception as e:
                print(f"Error inserting data: {e}")
                connection.rollback()

                return False

    @staticmethod
    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            return True
        else:
            return False



    @staticmethod
    def fun_DSN_FOR_DB(DSN,UID,PWD):
        return f"DSN={DSN};UID={UID};PWD={PWD};"


    @staticmethod
    def fun_USE_DB(DB_name):
        return f"USE {DB_name}"


    def check_vehicle_availability(self, vehicle_number) -> int:
        try:
            connection = pyodbc.connect(f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                                                SERVER=ITDT14;
                                                UID=sa;
                                                PWD=root1234""",
                                        autocommit=True)
            cursor = connection.cursor()
            select_db_query = f"USE ALPR_DB_NEW;"
            cursor.execute(select_db_query)

            # Check if the vehicle already exists
            check_vehicle_query = f"""SELECT vehicle_status FROM [ALPR_DB_NEW].[dbo].[vehicle_details]
                                          WHERE vehicle_number = ?"""
            cursor.execute(check_vehicle_query, vehicle_number)
            vehicle_status = cursor.fetchone()

            if vehicle_status:
                if vehicle_status[0] == 1:
                    return 2
                else:
                    return 1
            else:

                return 0

        except pyodbc.Error as e:
            print(e)
        except Exception as e:
            print(e)



