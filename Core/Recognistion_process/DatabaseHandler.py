
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



    # @staticmethod
    # def insert_vehicle_data(cursor, insert_query, vehicle_data, detection_result, status, alarm_code, connection):
    #     cursor.execute(insert_query, (
    #         vehicle_data['vehicle_id'],
    #         detection_result['plate_number'],
    #         detection_result['color'],
    #         detection_result['country'],
    #         detection_result['vehicle_img'],
    #         detection_result['plate_img'],
    #         1,
    #         detection_result['system_time'],
    #         status,
    #         alarm_code
    #     ))
    #     connection.commit()
