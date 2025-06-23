import datetime
import re
from Core.main import Core
from FlowControl.home import HomeController
from Interface.main import Interface
from tkinter import messagebox


class VehicleListController:

    def __init__(self, Core: Core, Interface: Interface):

        self.obj_core = Core
        self.obj_Interface = Interface
        self.obj_VehicleListInterface = self.obj_Interface.dict_frames["vehicle_list"]
        self.obj_HomeInterface = self.obj_Interface.dict_frames["home"]
        self.obj_homeController = HomeController(Core, Interface)

        self.bind_buttons()

        self.obj_VehicleListInterface.entry_search.bind("<KeyRelease>", self.search_vehicle)
        self.obj_VehicleListInterface.entry_selected_owner.bind("<KeyRelease>", self.search_owner)
        self.obj_VehicleListInterface.entry_selected_type.bind("<KeyRelease>", self.search_type)
        self.obj_VehicleListInterface.entry_selected_color.bind("<KeyRelease>", self.search_color)
        self.obj_VehicleListInterface.entry_selected_owner.bind("<Button-1>",
                                                                self.obj_VehicleListInterface.close_filter_dropdown)
        self.obj_VehicleListInterface.entry_selected_type.bind("<Button-1>",
                                                               self.obj_VehicleListInterface.close_filter_dropdown)
        self.obj_VehicleListInterface.entry_selected_color.bind("<Button-1>",
                                                                self.obj_VehicleListInterface.close_filter_dropdown)

        self.obj_VehicleListInterface.on_form_add_ready = self.bind_add_popup_buttons
        self.obj_VehicleListInterface.on_form_edit_ready = self.bind_edit_popup_buttons

    def bind_buttons(self):
        self.obj_VehicleListInterface.button_filter.configure(command=self.filter_popup)
        self.obj_VehicleListInterface.button_select_owner.configure(command=self.popup_owner_dropdown)
        self.obj_VehicleListInterface.button_select_type.configure(command=self.popup_type_dropdown)
        self.obj_VehicleListInterface.button_select_color.configure(command=self.popup_color_dropdown)
        self.obj_VehicleListInterface.button_ok.configure(command=self.onclick_ok)
        self.obj_VehicleListInterface.button_cancel.configure(command=self.onclick_cancel)

        self.obj_VehicleListInterface.button_next.configure(command=self.onclick_next)
        self.obj_VehicleListInterface.button_previous.configure(command=self.onclick_previous)

        self.obj_VehicleListInterface.button_Add.configure(command=self.onclick_add)

        self.obj_VehicleListInterface.button_Edit.configure(command=self.onclick_edit)
        self.obj_VehicleListInterface.button_Delete_selected.configure(command=self.onclick_delete)

        for key, value in self.obj_VehicleListInterface.dict_columns_buttons.items():
            value[0].configure(command=lambda k=key: self.onclick_column_headings(k))

    def bind_add_popup_buttons(self):
        self.obj_VehicleListInterface.button_add_save.configure(command=self.onclick_add_save)
        self.obj_VehicleListInterface.button_cancel.configure(command=self.onclick_Add_cancel)
        self.obj_VehicleListInterface.entry_number.bind("<KeyRelease>", self.validate_number)
        self.obj_VehicleListInterface.entry_model.bind("<KeyRelease>", self.validate_model)
        self.obj_VehicleListInterface.entry_color.bind("<KeyRelease>", self.validate_colour)
        self.obj_VehicleListInterface.entry_owner.bind("<KeyRelease>", self.validate_owner)
        self.obj_VehicleListInterface.entry_date.bind("<KeyRelease>", self.validate_manufacturing_year)
        # self.obj_VehicleListInterface.entry_selected_company.bind("<KeyRelease>", self.validate_)

        self.obj_VehicleListInterface.entry_type.bind("<KeyRelease>",
                                                      lambda e: self.search_Add_type_new(
                                                          self.obj_VehicleListInterface.entry_type, 4, 3,
                                                          self.obj_VehicleListInterface,
                                                          self.obj_VehicleListInterface.frame_form_rcol, 0
                                                          ))
        self.obj_VehicleListInterface.entry_selected_company.bind("<KeyRelease>",
                                                                  lambda e: self.search_Add_type_new(
                                                                      self.obj_VehicleListInterface.entry_selected_company,
                                                                      4, 3, self.obj_VehicleListInterface,
                                                                      self.obj_VehicleListInterface.frame_form_lcol, 1
                                                                      ))

    def search_Add_type_new(self, entryfield, row=0, rowspan=2, interface_obj=None, parent=None, fun=0, event=None):
        self.list_company = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen", "Hyundai", "Nissan"]
        self.list_vehicl_type = ["Personal", "Truck", "Motorcycle", "Bus", "Van", "Auto", "Taxi"]

        text_entered = entryfield.get().lstrip(" ")
        text_entered = text_entered
        dict_status = []
        if fun == 0:
            dict_status = self.obj_core.obj_Vehicle.search_vehicle_type(text_entered)
            if len(dict_status) == 1 and dict_status[0] == text_entered and dict_status[0] != 'All':
                entryfield.configure(border_color="green")
                self.obj_VehicleListInterface.label_error.configure(text="")
            else:
                self.obj_VehicleListInterface.label_error.configure(
                    text="Vehcile Type should be selected from the dropdown")
                entryfield.configure(border_color="red")




        elif fun == 1:
            dict_status = self.obj_core.obj_Vehicle.search_vehicle_company(text_entered)
            if len(dict_status) == 1 and dict_status[0] == text_entered and dict_status[0] != 'All':
                self.obj_VehicleListInterface.label_error.configure(text="")
                entryfield.configure(border_color="green")
            else:
                self.obj_VehicleListInterface.label_error.configure(
                    text="Vehcile Company should be selected from the dropdown")
                entryfield.configure(border_color="red")

        interface_obj.popup_Add_dropdown(parent, dict_status, entry_destination=entryfield, i_row=row,
                                         i_rowspan=rowspan, type=0)

    # ----------------------------------------------------------[validation add page]-------------------------------------------------------------------------------------

    def validate_owner(self, event=None):
        owner_name = self.obj_VehicleListInterface.entry_owner.get().strip()
        if 3 <= len(owner_name) <= 50:
            if self.validate_owner_name(owner_name):
                # No invalid characters, valid length
                self.obj_VehicleListInterface.label_error.configure(text="")
                self.obj_VehicleListInterface.entry_owner.configure(border_color="green")
            else:
                # Invalid characters (contains digits or special characters)
                self.obj_VehicleListInterface.label_error.configure(
                    text="Owner Name: [(A-Z),(a-z) and spaces only] required")
                self.obj_VehicleListInterface.entry_owner.configure(border_color="red")
        else:
            # Length is not within the required range
            self.obj_VehicleListInterface.label_error.configure(text="Owner Name Length between: [3-50] required")
            self.obj_VehicleListInterface.entry_owner.configure(border_color="red")

    def validate_owner_name(self, owner_name):
        return owner_name.replace(" ", "").isalpha()

    def validate_number(self, event=None) -> bool:
        vehicle_number = self.obj_VehicleListInterface.entry_number.get().strip()

        # First, check if the length of the vehicle number is between 6 and 15
        if not (6 <= len(vehicle_number) <= 15):
            self.obj_VehicleListInterface.label_error.configure(text="Vehicle number length between: [8-10] required")
            self.obj_VehicleListInterface.entry_number.configure(border_color="red")
            return False  # Exit the function if the length is incorrect

        # If length is correct, then check if it matches the pattern [A-Z, 0-9] with at least 4 letters and 4 digits
        if self.validate_vehicle_number(vehicle_number):
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_number.configure(border_color="green")
            return True  # Valid vehicle number
        else:
            self.obj_VehicleListInterface.label_error.configure(text="Vehcile Number should in Indian RTO format !")
            self.obj_VehicleListInterface.entry_number.configure(border_color="red")
            return False  # Invalid vehicle number

    def validate_vehicle_number(self, vehicle_number):
        # # Regular expression to validate the vehicle number, allowing uppercase/lowercase letters and digits.
        # # It must contain at least 4 digits and 4 letters.
        # pattern = r'^[A-Za-z0-9]+$'
        #
        def check_plate_format(input_string):
            """
            Check the country name and valid number
            :param input_string string give by ocr
            :return string  country name and Unknown in failure case

            """
            country_patterns = {
                'India': [
                    r'[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}',
                    r'[A-Z]{2}[0-9]{1}[A-Z]{3}[0-9]{3}[A-Z]{1}',
                    r'[A-Z]{2}[0-9]{1}[A-Z]{3}[0-9]{4}',
                    r'[A-Z]{2}[0-9]{2}[A-Z]{1}[0-9]{4}',
                    r'[A-Z]{2}[0-9]{6}',
                    r'[A-Z]{2}[0-9]{1}[A-Z]{2}[0-9]{4}',
                    r'[0-9]{2}[A-Z]{2}[0-9]{4}[A-Z]{2}',
                    r'[0-9]{2}[A-Z]{2}[0-9]{4}[A-Z]{1}',
                    r'[0-9]{2}[A-Z]{1}[0-9]{6}[A-Z]{1}'
                ],
                # 'China': [
                #     r'[A-Z]{1}[0-9]{4}[A-Z]{1}',
                #     r'[A-Z]{2}[0-9]{3}[A-Z]{1}',
                #     r'[A-Z]{4}[0-9]{2}',
                #     r'[A-Z]{3}[0-9]{3}',
                #     r'[A-Z]{1}[0-9]{1}[A-Z]{1}[0-9]{3}',
                #     r'[A-Z]{1}[0-9]{3}[A-Z]{1}[0-9]{1}',
                # ]
            }

            # Match the input_string with regex patterns for each country
            for country, patterns in country_patterns.items():
                for pattern in patterns:
                    if re.fullmatch(pattern, input_string):
                        return True

            return False

        # Check if the vehicle number matches the pattern
        return check_plate_format(str.upper(vehicle_number))

    def validate_model(self, event=None):
        vehicle_model = self.obj_VehicleListInterface.entry_model.get().strip()
        if not (1 <= len(vehicle_model) <= 10):
            self.obj_VehicleListInterface.label_error.configure(text=" Model Name length between: [1-10] required")
            self.obj_VehicleListInterface.entry_model.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_vehicle_model(vehicle_model):
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_model.configure(border_color="green")
        else:
            self.obj_VehicleListInterface.label_error.configure(text="Model Name: [(A-Z),(a-z),(0-9),(-)] required")
            self.obj_VehicleListInterface.entry_model.configure(border_color="red")

    def validate_vehicle_model(self, vehicle_model):
        pattern = r'^[A-Z a-z0-9-]+$'  # Allows uppercase letters and digits only
        return bool(re.match(pattern, vehicle_model.upper()))

    def validate_colour(self, event=None):
        colour = self.obj_VehicleListInterface.entry_color.get().strip()

        if not 3 <= len(colour) and len(colour) <= 10:
            self.obj_VehicleListInterface.label_error.configure(text="colour length between: [3-15] required")
            self.obj_VehicleListInterface.entry_color.configure(border_color="red")

        elif self.validate_vehicle_colour(colour):
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_color.configure(border_color="green")



        else:
            self.obj_VehicleListInterface.label_error.configure(text=" valid colour name: [(A-Z),(a-z)] required")
            self.obj_VehicleListInterface.entry_color.configure(border_color="red")

    def validate_vehicle_colour(self, colour):
        return colour.isalpha()

    def validate_manufacturing_year(self, event=None):
        year = self.obj_VehicleListInterface.entry_date.get().strip()

        if self.validate_vehicle_year(year):  # Just pass 'year'
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_date.configure(border_color="green")
        elif len(year) == 0:
            self.obj_VehicleListInterface.label_error.configure(text="Enter Manufacturing year")
            self.obj_VehicleListInterface.entry_date.configure(border_color="red")
        else:
            current_year = datetime.datetime.now().year  # Get current year
            self.obj_VehicleListInterface.label_error.configure(
                text=f"Manufacturing date must be number between: {current_year - 50} and {current_year}"
            )
            self.obj_VehicleListInterface.entry_date.configure(border_color="red")

    def validate_vehicle_year(self, year):
        # Check if the year is a valid number (digit)
        if not year.isdigit():
            return False

        try:
            # Convert year to an integer
            year_int = int(year)
            current_year = datetime.datetime.now().year  # Get the current year

            # Check if the year is within the valid range
            return current_year - 50 <= year_int <= current_year
        except ValueError:
            return False

    def validate_type(self, event=None):
        type = self.obj_VehicleListInterface.entry_type.cget().strip()
        print(f"Selected Type: {type}")  # Debugging line

        if self.validate_vehicle_type(type):
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_type.configure(border_color="green")

    def validate_vehicle_type(self, type):
        return type in ["WhiteList", "BlackList"]

    # ----------------------------------------------------------[validiation add ends]----------------------------------------------------------------------------------------------------

    def bind_edit_popup_buttons(self):
        #  self.obj_VehicleListInterface.entry_edit_selected_status.bind("<KeyRelease>", self.search_edit_status)
        self.obj_VehicleListInterface.button_edit_save.configure(command=self.onclick_edit_save)
        #  self.obj_VehicleListInterface.entry_Edit_number.bind("<KeyRelease>", self.validate_edit_number)
        self.obj_VehicleListInterface.entry_edit_model.bind("<KeyRelease>", self.validate_edit_model)
        self.obj_VehicleListInterface.entry_edit_color.bind("<KeyRelease>", self.validate_edit_colour)
        self.obj_VehicleListInterface.entry_edit_owner.bind("<KeyRelease>", self.validate_edit_owner)
        self.obj_VehicleListInterface.entry_edit_date.bind("<KeyRelease>", self.validate_edit_manufacturing_year)

        self.obj_VehicleListInterface.entry_edit_type.bind("<KeyRelease>",
                                                           lambda e: self.search_Edit_type_new(
                                                               self.obj_VehicleListInterface.entry_edit_type, 4, 3,
                                                               self.obj_VehicleListInterface,
                                                               self.obj_VehicleListInterface.frame_form_rcol, 0
                                                               ))
        self.obj_VehicleListInterface.entry_edit_selected_company.bind("<KeyRelease>",
                                                                       lambda e: self.search_Edit_type_new(
                                                                           self.obj_VehicleListInterface.entry_edit_selected_company,
                                                                           4, 3, self.obj_VehicleListInterface,
                                                                           self.obj_VehicleListInterface.frame_form_lcol,
                                                                           1
                                                                           ))

    def validate_edit_owner(self, event=None):
        owner_name = self.obj_VehicleListInterface.entry_edit_owner.get().strip()
        if not 3 <= len(owner_name) <= 50:
            self.obj_VehicleListInterface.label_error.configure(text="Owner Name length  between [3-50] required")
            self.obj_VehicleListInterface.entry_edit_owner.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_owner_name(owner_name):
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_owner.configure(border_color="green")
        else:
            self.obj_VehicleListInterface.label_error.configure(
                text=" Owner Name should be: [(A-Z),(a-z),and spaces] required")
            self.obj_VehicleListInterface.entry_edit_owner.configure(border_color="red")

    def validate_owner_name(self, owner_name):
        return owner_name.replace(" ", "").isalpha()

    def validate_edit_model(self, event=None):
        vehicle_model = self.obj_VehicleListInterface.entry_edit_model.get().strip()
        if not (1 <= len(vehicle_model) <= 10):
            self.obj_VehicleListInterface.label_error.configure(text=" Model Name length between: [1-10] required")
            self.obj_VehicleListInterface.entry_edit_model.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_vehicle_model(vehicle_model):
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_model.configure(border_color="green")
        else:
            self.obj_VehicleListInterface.label_error.configure(text="Model Name: [(A-Z),(a-z),(0-9),(-)] required")
            self.obj_VehicleListInterface.entry_edit_model.configure(border_color="red")

    def validate_vehicle_model(self, vehicle_model):
        pattern = r'^[A-Z a-z0-9-]+$'  # Allows uppercase letters and digits only
        return bool(re.match(pattern, vehicle_model.upper()))

    def validate_edit_colour(self, event=None):
        colour = self.obj_VehicleListInterface.entry_edit_color.get().strip()
        if not 3 <= len(colour) <= 10:
            self.obj_VehicleListInterface.label_error.configure(text="Color length: [3-10] required")
            self.obj_VehicleListInterface.entry_edit_color.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_vehicle_colour(colour):
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_color.configure(border_color="green")
        else:
            self.obj_VehicleListInterface.label_error.configure(text="Colour should be: [(A-Z),(a-z)] required")
            self.obj_VehicleListInterface.entry_edit_color.configure(border_color="red")

    def validate_vehicle_colour(self, colour):
        return colour.isalpha()

    def validate_edit_manufacturing_year(self, event=None):
        year = self.obj_VehicleListInterface.entry_edit_date.get().strip()

        # Get the current year dynamically
        current_year = datetime.datetime.now().year

        if not year:
            self.obj_VehicleListInterface.label_error.configure(text="Please enter Manufacture year")
            self.obj_VehicleListInterface.entry_edit_date.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_vehicle_year(year):
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_date.configure(border_color="green")
        else:
            self.obj_VehicleListInterface.label_error.configure(
                text=f"Manufacturing date must be number between [{current_year - 50} - {current_year}]")
            self.obj_VehicleListInterface.entry_edit_date.configure(border_color="red")

    def validate_vehicle_year(self, year):
        # Check if the year is a valid number (digit)
        if not year.isdigit():
            return False

        try:
            # Convert year to an integer
            year_int = int(year)
            current_year = datetime.datetime.now().year  # Get the current year

            # Check if the year is within the valid range
            return current_year - 50 <= year_int <= current_year
        except ValueError:
            return False

    def validate_edit_type(self, event=None):
        type = self.obj_VehicleListInterface.entry_edit_type.get().strip()
        if not type:
            self.obj_VehicleListInterface.label_error.configure(text="Please Enter Vehcile Type")
            self.obj_VehicleListInterface.entry_edit_type.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_vehicle_type(type):
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_type.configure(border_color="green")
        else:
            self.obj_VehicleListInterface.label_error.configure(text="Please Select Vehcile Type from dropdown")
            self.obj_VehicleListInterface.entry_edit_type.configure(border_color="red")

    def validate_vehicle_type(self, type):
        return type in ["WhiteList", "BlackList"]

    def search_Edit_type_new(self, entryfield, row=0, rowspan=2, interface_obj=None, parent=None, fun=0, event=None):

        text_entered = entryfield.get().lstrip(" ")
        text_entered = text_entered
        dict_status = []
        if fun == 0:
            dict_status = self.obj_core.obj_Vehicle.search_vehicle_type(text_entered)
            if len(dict_status) == 1 and dict_status[0] == text_entered and dict_status[0] != 'All':
                entryfield.configure(border_color="green")
                self.obj_VehicleListInterface.label_error.configure(text="")
            else:
                self.obj_VehicleListInterface.label_error.configure(
                    text="Vehcile Type should be selected from the dropdown")
                entryfield.configure(border_color="red")

        elif fun == 1:
            dict_status = self.obj_core.obj_Vehicle.search_vehicle_company(text_entered)

            if len(dict_status) == 1 and dict_status[0] == text_entered and dict_status[0] != 'All':
                entryfield.configure(border_color="green")
                self.obj_VehicleListInterface.label_error.configure(text="")
            else:
                self.obj_VehicleListInterface.label_error.configure(
                    text="Vehcile Company should be selected from the dropdown")
                entryfield.configure(border_color="red")

        interface_obj.popup_Edit_dropdown(parent, dict_status, entry_destination=entryfield, i_row=row,
                                          i_rowspan=rowspan, type=0)

    # ____________________________________________________________[filter search]___________________________________________________________________________________________

    def search_vehicle(self, event):
        if (self.obj_VehicleListInterface.bool_type_dropdown_opened):
            self.obj_VehicleListInterface.close_dropdown(None)
            self.obj_VehicleListInterface.bool_type_dropdown_opened = False
        elif (self.obj_VehicleListInterface.bool_color_dropdown_opened):
            self.obj_VehicleListInterface.close_dropdown(None)
            self.obj_VehicleListInterface.bool_color_dropdown_opened = False

        if (self.obj_VehicleListInterface.bool_owner_dropdown_opened):
            self.obj_VehicleListInterface.close_dropdown(None)
            self.obj_VehicleListInterface.bool_owner_dropdown_opened = False

        # str_vehicle_number = self.obj_VehicleListInterface.entry_search.get().lstrip(" ")
        # str_vehicle_number = str_vehicle_number.upper()
        #
        # list_vehicle_data = self.obj_core.obj_Vehicle.search_vehicle_number(
        #     self.obj_Interface.dict_frames["vehicle_list"].vehicle_data, str_vehicle_number)
        # self.obj_Interface.dict_frames["vehicle_list"].update_table(list_vehicle_data)

        str_vehicle_number = (self.obj_VehicleListInterface.entry_search.get().lstrip(" ")).upper()
        list_searched_data = []

        if (str_vehicle_number != ""):
            list_searched_data = self.obj_core.obj_Vehicle.search_vehicle_number(self.obj_VehicleListInterface.vehicle_data, str_vehicle_number)
            self.obj_VehicleListInterface.i_total_data = len(list_searched_data)
        else:
            list_searched_data = self.obj_VehicleListInterface.vehicle_data
            self.obj_VehicleListInterface.i_total_data = len(self.obj_VehicleListInterface.vehicle_data)

        if (self.obj_VehicleListInterface.i_total_data > 0):
            self.obj_VehicleListInterface.i_start_index = 1
            self.obj_VehicleListInterface.i_end_index = 5 if self.obj_VehicleListInterface.i_total_data >= 5 else self.obj_VehicleListInterface.i_total_data

        self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] = str_vehicle_number
        self.obj_VehicleListInterface.update_table(list_searched_data[0:5])

    def search_owner(self, event):
        if (self.obj_VehicleListInterface.bool_type_dropdown_opened):
            self.obj_VehicleListInterface.popup_dropdown()
            self.obj_VehicleListInterface.bool_type_dropdown_opened = False
        elif (self.obj_VehicleListInterface.bool_color_dropdown_opened):
            self.obj_VehicleListInterface.popup_dropdown()
            self.obj_VehicleListInterface.bool_color_dropdown_opened = False

        if (self.obj_VehicleListInterface.bool_owner_dropdown_opened):
            self.obj_VehicleListInterface.popup_dropdown()
            self.obj_VehicleListInterface.bool_owner_dropdown_opened = False
        str_owner_name = self.obj_VehicleListInterface.entry_selected_owner.get().lstrip(" ")
        str_owner_name = str_owner_name
        if str_owner_name != "":
            dict_status = self.obj_core.obj_Vehicle.search_vehicle_owner(str_owner_name)

            self.obj_VehicleListInterface.popup_dropdown(list_data=dict_status,
                                                         entry_destination=self.obj_VehicleListInterface.entry_selected_owner,
                                                         i_row=4,
                                                         i_rowspan=3)
            self.obj_VehicleListInterface.bool_owner_dropdown_opened = True
        else:
            self.obj_VehicleListInterface.bool_owner_dropdown_opened = False

    def search_type(self, event):
        if (self.obj_VehicleListInterface.bool_type_dropdown_opened):
            self.obj_VehicleListInterface.popup_dropdown()
            self.obj_VehicleListInterface.bool_type_dropdown_opened = False
        elif (self.obj_VehicleListInterface.bool_color_dropdown_opened):
            self.obj_VehicleListInterface.popup_dropdown()
            self.obj_VehicleListInterface.bool_color_dropdown_opened = False

        if (self.obj_VehicleListInterface.bool_owner_dropdown_opened):
            self.obj_VehicleListInterface.close_dropdown()
            self.obj_VehicleListInterface.bool_owner_dropdown_opened = False

        str_vehicle_type = self.obj_VehicleListInterface.entry_selected_type.get().lstrip(" ")
        str_vehicle_type = str_vehicle_type
        dict_status = self.obj_core.obj_Vehicle.search_vehicle_type(str_vehicle_type)

        self.obj_VehicleListInterface.popup_dropdown(list_data=dict_status,
                                                     entry_destination=self.obj_VehicleListInterface.entry_selected_type,
                                                     i_row=6,
                                                     i_rowspan=3)
        self.obj_VehicleListInterface.bool_type_dropdown_opened = True

    def search_color(self, event):
        str_vehicle_color = self.obj_VehicleListInterface.entry_selected_color.get().lstrip(" ")
        str_vehicle_color = str_vehicle_color
        dict_status = self.obj_core.obj_Vehicle.search_vehicle_color(str_vehicle_color)

        self.obj_VehicleListInterface.popup_dropdown(list_data=dict_status,
                                                     entry_destination=self.obj_VehicleListInterface.entry_selected_color,
                                                     i_row=8,
                                                     i_rowspan=2)
        self.obj_VehicleListInterface.bool_color_dropdown_opened = True

    def filter_popup(self):
        self.obj_VehicleListInterface.toggle_filter_popup()

    def popup_owner_dropdown(self):
        if (self.obj_VehicleListInterface.bool_type_dropdown_opened):
            current_type = self.obj_VehicleListInterface.entry_selected_type.get()
            if current_type not in ["Select Vehicle Type", "All"]:
                # Revert type dropdown to original state
                self.obj_VehicleListInterface.entry_selected_type.delete(0, 'end')
                self.obj_VehicleListInterface.entry_selected_type.insert(0, "Select Vehicle Type")

            # self.obj_VehicleListInterface.popup_dropdown(None)
            self.obj_VehicleListInterface.bool_type_dropdown_opened = False
        elif (self.obj_VehicleListInterface.bool_color_dropdown_opened):
            # Check if color dropdown has a value selected
            current_color = self.obj_VehicleListInterface.entry_selected_color.get()
            if current_color not in ["Select Vehicle Color", "All"]:
                # Revert color dropdown to original state
                self.obj_VehicleListInterface.entry_selected_color.delete(0, 'end')
                self.obj_VehicleListInterface.entry_selected_color.insert(0, "Select Vehicle Color")

            # self.obj_VehicleListInterface.popup_dropdown(None)
            self.obj_VehicleListInterface.bool_color_dropdown_opened = False

        # Handle owner dropdown
        if (self.obj_VehicleListInterface.bool_owner_dropdown_opened):
            # self.obj_VehicleListInterface.popup_dropdown(None)
            self.obj_VehicleListInterface.close_filter_dropdown(None)

            self.obj_VehicleListInterface.bool_owner_dropdown_opened = False
        else:
            dict_status = self.obj_core.obj_Vehicle.get_all_vehicle_owner()
            dict_status["list_owner"].append("All")
            self.obj_VehicleListInterface.popup_dropdown(list_data=dict_status["list_owner"],
                                                         entry_destination=self.obj_VehicleListInterface.entry_selected_owner,
                                                         i_row=4,
                                                         i_rowspan=3)
            self.obj_VehicleListInterface.bool_owner_dropdown_opened = True
        self.obj_VehicleListInterface.entry_selected_owner.focus()

    def popup_type_dropdown(self):
        # Check if owner dropdown is open and close it
        if (self.obj_VehicleListInterface.bool_owner_dropdown_opened):
            # Check if owner dropdown has a value selected
            current_owner = self.obj_VehicleListInterface.entry_selected_owner.get()
            if current_owner not in ["Select Owner Name", "All"]:
                # Revert owner dropdown to original state
                self.obj_VehicleListInterface.entry_selected_owner.delete(0, 'end')
                self.obj_VehicleListInterface.entry_selected_owner.insert(0, "Select Owner Name")
            self.obj_VehicleListInterface.close_filter_dropdown(None)
            self.obj_VehicleListInterface.popup_dropdown()
            self.obj_VehicleListInterface.bool_owner_dropdown_opened = False
        elif (self.obj_VehicleListInterface.bool_color_dropdown_opened):
            # Check if color dropdown has a value selected
            current_color = self.obj_VehicleListInterface.entry_selected_color.get()
            if current_color not in ["Select Vehicle Color", "All"]:
                # Revert color dropdown to original state
                self.obj_VehicleListInterface.entry_selected_color.delete(0, 'end')
                self.obj_VehicleListInterface.entry_selected_color.insert(0, "Select Vehicle Color")

            # self.obj_VehicleListInterface.popup_dropdown(None)
            self.obj_VehicleListInterface.bool_color_dropdown_opened = False

        # Handle type dropdown
        if (self.obj_VehicleListInterface.bool_type_dropdown_opened is True):
            self.obj_VehicleListInterface.close_filter_dropdown(None)

            # self.obj_VehicleListInterface.popup_dropdown(None)
            self.obj_VehicleListInterface.bool_type_dropdown_opened = False
        else:
            dict_status = self.obj_core.obj_Vehicle.get_all_vehicle_type()
            dict_status["list_type"].append("All")
            self.obj_VehicleListInterface.popup_dropdown(list_data=dict_status["list_type"],
                                                         entry_destination=self.obj_VehicleListInterface.entry_selected_type,
                                                         i_row=6,
                                                         i_rowspan=3)
            self.obj_VehicleListInterface.bool_type_dropdown_opened = True
        self.obj_VehicleListInterface.entry_selected_type.focus()

    def popup_color_dropdown(self):
        # Check if type dropdown is open and close it
        if (self.obj_VehicleListInterface.bool_type_dropdown_opened):
            # Check if type dropdown has a value selected
            current_type = self.obj_VehicleListInterface.entry_selected_type.get()
            if current_type not in ["Select Vehicle Type", "All"]:
                # Revert type dropdown to original state
                self.obj_VehicleListInterface.entry_selected_type.delete(0, 'end')
                self.obj_VehicleListInterface.entry_selected_type.insert(0, "Select Vehicle Type")
            self.obj_VehicleListInterface.close_dropdown()

            # self.obj_VehicleListInterface.popup_dropdown(None)
            self.obj_VehicleListInterface.bool_type_dropdown_opened = False
        elif (self.obj_VehicleListInterface.bool_owner_dropdown_opened):
            # Check if owner dropdown has a value selected
            current_owner = self.obj_VehicleListInterface.entry_selected_owner.get()
            if current_owner not in ["Select Owner Name", "All"]:
                # Revert owner dropdown to original state
                self.obj_VehicleListInterface.entry_selected_owner.delete(0, 'end')
                self.obj_VehicleListInterface.entry_selected_owner.insert(0, "Select Owner Name")

            self.obj_VehicleListInterface.close_filter_dropdown(None)
            # self.obj_VehicleListInterface.close_dropdown(None)
            self.obj_VehicleListInterface.popup_dropdown()
            self.obj_VehicleListInterface.bool_owner_dropdown_opened = False

        # Handle color dropdown
        if (self.obj_VehicleListInterface.bool_color_dropdown_opened is True):
            self.obj_VehicleListInterface.close_filter_dropdown(None)
            self.obj_VehicleListInterface.bool_color_dropdown_opened = False
        else:
            dict_status = self.obj_core.obj_Vehicle.get_all_vehicle_color()
            dict_status["list_color"].append("All")
            self.obj_VehicleListInterface.popup_dropdown(list_data=dict_status["list_color"],
                                                         entry_destination=self.obj_VehicleListInterface.entry_selected_color,
                                                         i_row=8,
                                                         i_rowspan=2)
            self.obj_VehicleListInterface.bool_color_dropdown_opened = True

        self.obj_VehicleListInterface.entry_selected_color.focus()

    def onclick_ok(self):
        str_owner = self.obj_VehicleListInterface.entry_selected_owner.get().lstrip(" ")
        self.obj_VehicleListInterface.dict_filter_criteria["str_owner"] = "%" if (str_owner == "All" or str_owner == "") else str_owner

        str_type = self.obj_VehicleListInterface.entry_selected_type.get().lstrip(" ")
        self.obj_VehicleListInterface.dict_filter_criteria["str_type"] = "%" if (str_type == "All" or str_type == "") else str_type

        str_color = self.obj_VehicleListInterface.entry_selected_color.get().lstrip(" ")
        self.obj_VehicleListInterface.dict_filter_criteria["str_color"] = "%" if (str_color == "All" or str_color == "") else str_color

        self.obj_VehicleListInterface.reset_interface()
        self.obj_Interface.obj_RootInterface.focus_set()

        # self.obj_VehicleListInterface.i_total_data = self.obj_core.obj_Vehicle.get_data_count(
        #     self.obj_VehicleListInterface.dict_filter_criteria)
        # self.obj_VehicleListInterface.vehicle_data = []
        # if (self.obj_VehicleListInterface.i_total_data > 0):
        #     self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_vehicle_details(
        #         self.obj_VehicleListInterface.i_end_index, self.obj_VehicleListInterface.dict_filter_criteria)
        #     i_total_data_fetched = len(self.obj_VehicleListInterface.vehicle_data)
        #     if (i_total_data_fetched > 0):
        #         self.obj_VehicleListInterface.i_start_index = 1
        #         self.obj_VehicleListInterface.i_end_index += i_total_data_fetched
        #
        # self.obj_VehicleListInterface.update_table(self.obj_VehicleListInterface.vehicle_data)

        self.obj_VehicleListInterface.vehicle_data = []
        self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_vehicle_details(self.obj_VehicleListInterface.dict_filter_criteria)
        self.obj_VehicleListInterface.i_total_data = len(self.obj_VehicleListInterface.vehicle_data)
        if (self.obj_VehicleListInterface.i_total_data > 0):
            self.obj_Interface.dict_frames["vehicle_list"].i_start_index = 1
            self.obj_Interface.dict_frames["vehicle_list"].i_end_index += 5 if self.obj_VehicleListInterface.i_total_data >= 5 else self.obj_VehicleListInterface.i_total_data

        self.obj_VehicleListInterface.update_table((self.obj_VehicleListInterface.vehicle_data)[0:5])

    def onclick_cancel(self):
        self.obj_VehicleListInterface.reset_filter_form()
        if (self.obj_VehicleListInterface.bool_filter_popup is True):
            self.obj_VehicleListInterface.popup_dropdown()
            self.obj_VehicleListInterface.reset_filter_form()
            self.obj_VehicleListInterface.toggle_filter_popup()

    def onclick_column_headings(self, str_column: str):
        str_db_column = "vehicle_number"

        if (str_column == "Vehicle Type"):
            str_db_column = "vehicle_type"
        elif (str_column == "Vehicle Color"):
            str_db_column = "vehicle_color"
        elif (str_column == "Owner Name"):
            str_db_column = "vehicle_owner"
        elif (str_column == "Manufacturing Year"):
            str_db_column = "manufacturing_year"

        # Find the column index in the table headers
        column_index = self.obj_VehicleListInterface.table_headers.index(str_column)

        # Call toggle_sort to update the UI indicators (arrows)
        is_ascending = self.obj_VehicleListInterface.toggle_sort(column_index)

        # Get the data based on any existing filter
        data = []
        if (self.obj_VehicleListInterface.dict_filter_criteria.get("str_vehicle_number", "") == ""):
            data = self.obj_VehicleListInterface.vehicle_data
        else:
            data = self.obj_core.obj_Vehicle.search_vehicle_number(
                self.obj_VehicleListInterface.vehicle_data,
                self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"]
            )

        # Sort the data using the sort direction returned by toggle_sort
        data = self.obj_core.obj_Vehicle.sort_vehicle_data(
            data[(self.obj_VehicleListInterface.i_start_index) - 1:self.obj_VehicleListInterface.i_end_index],
            str_db_column,
            is_ascending  # Use the value returned by toggle_sort
        )

        # Update the table with the sorted data
        self.obj_VehicleListInterface.update_table(data)



    def onclick_next(self):
        self.obj_Interface.obj_RootInterface.focus_set()

        if (self.obj_VehicleListInterface.bool_filter_popup is True):
            self.obj_VehicleListInterface.close_dropdown(None)
            self.obj_VehicleListInterface.reset_filter_form()
            self.obj_VehicleListInterface.toggle_filter_popup()

        # self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_vehicle_details(
        #     self.obj_VehicleListInterface.i_end_index, self.obj_VehicleListInterface.dict_filter_criteria)
        # i_data_count = len(self.obj_VehicleListInterface.vehicle_data)
        # if (i_data_count > 0):
        #     self.obj_VehicleListInterface.i_start_index = self.obj_VehicleListInterface.i_end_index + 1
        #     self.obj_VehicleListInterface.i_end_index = self.obj_VehicleListInterface.i_end_index + i_data_count
        #
        #     self.obj_VehicleListInterface.update_table(self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)

        data = []
        required_data = []
        if (self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] != ""):
            data = self.obj_core.obj_Vehicle.search_vehicle_number(self.obj_VehicleListInterface.vehicle_data,self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"])
        else:
            data = self.obj_VehicleListInterface.vehicle_data

        required_data = data[(self.obj_VehicleListInterface.i_end_index): ((self.obj_VehicleListInterface.i_end_index) + 5)]
        i_data_count = len(required_data)
        if (i_data_count > 0):
            self.obj_VehicleListInterface.i_start_index = self.obj_VehicleListInterface.i_end_index + 1
            self.obj_VehicleListInterface.i_end_index = self.obj_VehicleListInterface.i_end_index + i_data_count

        self.obj_VehicleListInterface.update_table(required_data)

    def onclick_previous(self):
        self.obj_Interface.obj_RootInterface.focus_set()

        if (self.obj_VehicleListInterface.bool_filter_popup is True):
            self.obj_VehicleListInterface.close_dropdown(None)
            self.obj_VehicleListInterface.reset_filter_form()
            self.obj_VehicleListInterface.toggle_filter_popup()


        data = []
        required_data = []
        if (self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] != ""):
            data = self.obj_core.obj_Vehicle.search_vehicle_number(self.obj_VehicleListInterface.vehicle_data,self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"])
        else:
            data = self.obj_VehicleListInterface.vehicle_data

        required_data = data[((self.obj_VehicleListInterface.i_start_index) - 6): ((self.obj_VehicleListInterface.i_start_index) - 1)]
        i_data_count = len(required_data)
        if (i_data_count > 0):
            self.obj_VehicleListInterface.i_end_index = (self.obj_VehicleListInterface.i_start_index) - 1
            self.obj_VehicleListInterface.i_start_index = (self.obj_VehicleListInterface.i_start_index) - 5

        self.obj_VehicleListInterface.update_table(required_data)


    def onclick_add(self):
        self.obj_VehicleListInterface.add_Vechile()

    def onclick_Add_cancel(self):
        self.obj_VehicleListInterface.destroy_add_vehicle_form()

    def onclick_add_save(self):
        str_company = self.obj_VehicleListInterface.entry_selected_company.get()
        str_model = self.obj_VehicleListInterface.entry_model.get()
        str_type = self.obj_VehicleListInterface.entry_type.get()
        str_number = self.obj_VehicleListInterface.entry_number.get().strip().upper()
        str_color = self.obj_VehicleListInterface.entry_color.get()
        str_owner = self.obj_VehicleListInterface.entry_owner.get()
        str_status = self.obj_VehicleListInterface.entry_selected_status.get()
        i_date = self.obj_VehicleListInterface.entry_date.get().strip()
        self.list_company = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen", "Hyundai", "Nissan"]
        self.list_vehicle_type = ["Personal", "Truck", "Motorcycle", "Bus", "Van", "Auto", "Taxi",
                                  "All", "Commercial", "Electric", "SUV"]

        error_count = 0
        latest_error_message = None

        if not str_type.strip():
            latest_error_message = "Vehcile Type cannot be empty."
            self.obj_VehicleListInterface.label_error.configure(text="Vehcile Type cannot be empty")
            self.obj_VehicleListInterface.entry_type.configure(border_color="red")
            error_count += 1

        # Check for valid vehicle type
        elif str_type not in self.list_vehicle_type:
            latest_error_message = f"Vehicle Type '{str_type}' is not valid."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="Please choose from the list")
            self.obj_VehicleListInterface.entry_type.configure(border_color="red")
        else:
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_type.configure(border_color="green")

        # Check for valid company
        if str_company not in self.list_company:
            latest_error_message = f"Company '{str_company}' is not valid."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="Please choose from the list")
            self.obj_VehicleListInterface.entry_selected_company.configure(border_color="red")
        elif str_company.strip():
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_selected_company.configure(border_color="green")
        # check model
        if not (1 <= len(str_model) <= 10):
            latest_error_message = "Model name length should be between [1-10]."
            error_count += 1
            self.obj_VehicleListInterface.entry_model.configure(border_color="red")
            self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)
        elif not re.match(r'^[A-Za-z0-9-]+$', str_model.strip()):
            latest_error_message = "Model name should be: [(A-Z),(a-z),(0-9),(-)]."
            error_count += 1
            self.obj_VehicleListInterface.entry_model.configure(border_color="red")
            self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)
        else:

            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_model.configure(border_color="green")

        str_color= str_color.strip()
        if not 3 <= len(str_color) and len(str_color) <= 10:
            latest_error_message = "Colour length between: [3-10] required."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)
            self.obj_VehicleListInterface.entry_color.configure(border_color="red")

        # Check if colour contains only alphabetic characters
        elif not str_color.isalpha():
            latest_error_message = "Colour should : [(A-Z),(a-z)] required"
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)
            self.obj_VehicleListInterface.entry_color.configure(border_color="red")

        else:
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_color.configure(border_color="green")

        # Check if owner is empty or contains invalid characters

        if not (3 <= len(str_owner) <= 50):
            latest_error_message = "Owner name lenght should be: [3-50]"
            error_count += 1
            self.obj_VehicleListInterface.entry_owner.configure(border_color="red")

        elif not all(char.isalpha() or char.isspace() for char in str_owner.strip()):
            latest_error_message = "Owner name should: [(A-Z),(a-z) and spaces] required"
            error_count += 1
            self.obj_VehicleListInterface.entry_owner.configure(border_color="red")

        else:
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_owner.configure(border_color="green")

        # Check for valid manufacturing date
        current_year = datetime.datetime.now().year
        min_year = current_year - 50


        if i_date.isdigit() and min_year <= int(i_date) <= current_year:
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_date.configure(border_color="green")
        else:
            latest_error_message = f" manufacturing date between {min_year} and {current_year}."
            self.obj_VehicleListInterface.label_error.configure(
                text=f"Please enter a valid manufacturing date between {min_year} and {current_year}")
            self.obj_VehicleListInterface.entry_date.configure(border_color="red")
            error_count += 1

        # Check for blacklist status (0 or 1)
        if str_status in ["WhiteList", "BlackList"]:
            self.obj_VehicleListInterface.entry_selected_status.configure(border_color="green")
        else:
            latest_error_message = "Status must be 'WhiteList' or 'BlackList'."
            self.obj_VehicleListInterface.label_error.configure(text="Status must be 'WhiteList' or 'BlackList'")
            self.obj_VehicleListInterface.entry_selected_status.configure(border_color="red")
            error_count += 1

        if not (8 <= len(str_number) <= 10):
            latest_error_message = "Vehcile Number lenght should be: [8-10]"
            error_count += 1
            self.obj_VehicleListInterface.entry_number.configure(border_color="red")

        elif not self.validate_number(str_number):
            latest_error_message = "Vehcile Number should in Indian RTO format !"
            error_count += 1
            self.obj_VehicleListInterface.entry_number.configure(border_color="red")

        else:
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_number.configure(border_color="green")

        if error_count > 0 and latest_error_message:
            print("Latest error message:", latest_error_message)
            # Optionally display the message on a label or a dialog
            self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)

        # Convert the status to integer (1 for black-list, 0 for white-list)
        i_status = 0
        if str_status == "BlackList":
            i_status = 1
        print(f" before add {len(self.obj_VehicleListInterface.vehicle_data)} vehicles were present.")
        # If no errors, proceed with adding the vehicle
        if error_count == 0:
            dict_status = self.obj_core.obj_Vehicle.add_vehicle(
                str_company, str_model.strip(), str_type, str_number, str_color, i_date, str_owner.strip(), i_status
            )

            if dict_status["str_error_msg_heading"] == "Error! Duplicate Entries":
                # If duplicate vehicle is found, show a popup
                self.obj_Interface.on_error(
                    "home",
                    "Error! Duplicate Entries",
                    f"A vehcile with  the ID '{str_number}' already present.",
                    "#FF4B4B"
                )

            elif dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == "":
                # If no errors, show success message
                self.obj_Interface.on_error(
                    "home",
                    "Data Added Successfully",
                    "",
                    "#63CA6D",  # Green for success
                    50
                )

                bool_update_data = (((self.obj_VehicleListInterface.dict_filter_criteria["str_owner"] == "%") and
                                     (self.obj_VehicleListInterface.dict_filter_criteria["str_type"] == "%") and
                                     (self.obj_VehicleListInterface.dict_filter_criteria["str_color"] == "%")) or
                                    ((self.obj_VehicleListInterface.dict_filter_criteria["str_owner"] == str_owner) or
                                     (self.obj_VehicleListInterface.dict_filter_criteria["str_type"] == str_type) or
                                     (self.obj_VehicleListInterface.dict_filter_criteria["str_color"] == str_color)))

                if (bool_update_data):
                    self.obj_VehicleListInterface.i_total_data = len(self.obj_VehicleListInterface.vehicle_data) + 1

                    self.obj_VehicleListInterface.vehicle_data.append({
                        "vehicle_number": str_number,
                        "vehicle_type": str_type,
                        "vehicle_color": str_color,
                        "vehicle_owner": str_owner,
                        "manufacturing_year": i_date,
                        "vehicle_company": str_company,
                        "vehicle_model": str_model,
                        "vehicle_status": str_status
                    })

                if (self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] != ""):
                    self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] = ""
                    self.obj_VehicleListInterface.entry_search.delete(0, "end")
                    self.obj_VehicleListInterface.entry_search.configure(placeholder_text="Enter Vehicle Number..")
                    self.obj_Interface.obj_RootInterface.focus_set()

                    if (not bool_update_data):
                        self.obj_VehicleListInterface.i_total_data = len(self.obj_VehicleListInterface.vehicle_data)

                    self.obj_Interface.dict_frames["vehicle_list"].i_start_index = 1
                    self.obj_Interface.dict_frames[
                        "vehicle_list"].i_end_index = 5 if self.obj_VehicleListInterface.i_total_data >= 5 else self.obj_VehicleListInterface.i_total_data
                else:
                    if (bool_update_data):
                        if (((
                                     self.obj_VehicleListInterface.i_end_index - self.obj_VehicleListInterface.i_start_index) + 1) < 5):
                            self.obj_VehicleListInterface.i_end_index += 1

                data = (self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)[
                       ((self.obj_VehicleListInterface.i_start_index) - 1):(self.obj_VehicleListInterface.i_end_index)]
                self.obj_VehicleListInterface.update_table(data)
                self.obj_VehicleListInterface.destroy_add_vehicle_form()




        else:
            # Display error message if update failed
            self.obj_Interface.on_error(
                "home",
                "Error! Invalid Data",
                "Check if the entered data fulfiles the require condition",
                "#FF4B4B"

            )

        return

    def onclick_delete(self):
        confirm_delete = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {len(self.obj_VehicleListInterface.selected_vehicle_set)} selected vehicle ? ",
            icon='warning'
        )

        if confirm_delete:
            if self.obj_core.obj_Vehicle.delete_vechiles(list(self.obj_VehicleListInterface.selected_vehicle_set)):

                self.obj_VehicleListInterface.destroy_add_vehicle_form()

                self.obj_Interface.on_error(
                    "home",
                    "Data Deleted Successfully",
                    "",
                    "#63CA6D",
                    50
                )

                if (self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] != ""):
                    self.obj_VehicleListInterface.i_total_data = len(self.obj_VehicleListInterface.vehicle_data)
                    self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] = ""
                    self.obj_VehicleListInterface.entry_search.delete(0, "end")
                    self.obj_VehicleListInterface.entry_search.configure(placeholder_text="Enter Vehicle Number..")
                    self.obj_Interface.obj_RootInterface.focus_set()

                self.obj_VehicleListInterface.i_total_data = self.obj_VehicleListInterface.i_total_data - len(
                    self.obj_VehicleListInterface.selected_vehicle_set)

                self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_vehicle_details(
                    self.obj_VehicleListInterface.dict_filter_criteria)

                data = []
                while (True):
                    if (len(self.obj_VehicleListInterface.vehicle_data) == 0):
                        self.obj_VehicleListInterface.i_start_index = 0
                        self.obj_VehicleListInterface.i_end_index = 0
                        break

                    data = (self.obj_VehicleListInterface.vehicle_data)[
                           ((self.obj_VehicleListInterface.i_start_index) - 1):(
                                       (self.obj_VehicleListInterface.i_start_index) + 4)]

                    if (len(data) > 0):
                        self.obj_VehicleListInterface.i_end_index = (self.obj_VehicleListInterface.i_start_index + len(
                            data)) - 1
                        break
                    else:
                        self.obj_VehicleListInterface.i_start_index -= 5
                        self.obj_VehicleListInterface.i_end_index -= 5

                self.obj_VehicleListInterface.update_table(data)

                self.obj_VehicleListInterface.reset_checkbox()

            else:
                self.obj_Interface.on_error(
                    "home",
                    "Error! Invalid Data",
                    "Check if the entered data fulfill the required conditions.",
                    " "
                )

    def onclick_edit(self):
        self.obj_VehicleListInterface.edit_selected_Vehicle()

    def onclick_edit_save(self):
        error_count = 0
        correct_count = 0
        str_number = self.obj_VehicleListInterface.entry_edit_number.get().strip()
        str_company = self.obj_VehicleListInterface.entry_edit_selected_company.get().strip()
        str_model = self.obj_VehicleListInterface.entry_edit_model.get().strip()
        str_blacklist = self.obj_VehicleListInterface.entry_edit_selected_status.get().strip()
        str_type = self.obj_VehicleListInterface.entry_edit_type.get()
        str_color = self.obj_VehicleListInterface.entry_edit_color.get().strip()
        date = self.obj_VehicleListInterface.entry_edit_date.get().strip()
        str_owner = self.obj_VehicleListInterface.entry_edit_owner.get().strip()
        vehicle = self.obj_VehicleListInterface.vehicle
        wrong = ""

        if str_blacklist == "WhiteList":
            str_blacklist = 0
        else:
            str_blacklist = 1

        matching = 0
        if (vehicle['vehicle_company'] == str_company):
            matching += 1
        if (vehicle['vehicle_model'] == str_model):
            matching += 1

        if (vehicle['vehicle_status'] == str_blacklist):
            matching += 1

        if (vehicle['vehicle_type'] == str_type):
            matching += 1
        if (vehicle['vehicle_color'] == str_color):
            matching += 1

        if vehicle.get('manufacturing_year') and date:
            if int(vehicle['manufacturing_year']) == int(date):
                matching += 1

        else:
            print("Manufacturing year or date is missing.")

        if (vehicle['vehicle_owner'] == str_owner):
            matching += 1

        self.list_company = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen", "Hyundai", "Nissan", "Audi"]
        self.list_vehicle_type = ["Personal", "Truck", "Motorcycle", "Bus", "Van", "Auto", "Taxi",
                                  "All", "Commercial", "Electric", "SUV"]

        # Check for valid vehicle type
        # Variable to store the latest error message
        latest_error_message = None
        if not str_type.strip():
            latest_error_message = "Vehcile Type cannot be empty."
            self.obj_VehicleListInterface.label_error.configure(text="Vehcile Type cannot be empty")
            self.obj_VehicleListInterface.entry_edit_selected_company.configure(border_color="red")
            error_count += 1

        # Check for valid vehicle type
        elif str_type not in self.list_vehicle_type:
            latest_error_message = f"Vehicle Type '{str_type}' is not valid."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="Please choose from the list")
            self.obj_VehicleListInterface.entry_edit_type.configure(border_color="red")
        else:
            correct_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_type.configure(border_color="green")

        # Check for valid company
        if str_company not in self.list_company:
            latest_error_message = f"Company '{str_company}' is not valid."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="Please choose from the list")
            self.obj_VehicleListInterface.entry_edit_selected_company.configure(border_color="red")
        elif str_company.strip():
            correct_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_selected_company.configure(border_color="green")

        # Check if company name is empty
        if not str_company.strip():
            latest_error_message = "Company name cannot be empty."
            self.obj_VehicleListInterface.label_error.configure(text="Company name cannot be empty")
            self.obj_VehicleListInterface.entry_edit_selected_company.configure(border_color="red")
            error_count += 1

        # Check if model is empty
        if not (1 <= len(str_model) <= 10):
            latest_error_message = "Model name length should be between [1-10]."
            error_count += 1
            self.obj_VehicleListInterface.entry_edit_model.configure(border_color="red")
            self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)
        elif not re.match(r'^[A-Za-z0-9-]+$', str_model):
            latest_error_message = "Model name should be: [(A-Z),(a-z),(0-9),(-)]."
            error_count += 1
            self.obj_VehicleListInterface.entry_edit_model.configure(border_color="red")
            self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)
        else:
            correct_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_model.configure(border_color="green")

        # Check if color is empty
        if not 3 <= len(str_color) and len(str_color) <= 10:
            latest_error_message = "Colour length between: [3-10] required."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)
            self.obj_VehicleListInterface.entry_edit_color.configure(border_color="red")

        # Check if colour contains only alphabetic characters
        elif not str_color.isalpha():
            latest_error_message = "Colour should : [(A-Z),(a-z)] required"
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)
            self.obj_VehicleListInterface.entry_edit_color.configure(border_color="red")

        else:
            correct_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_color.configure(border_color="green")

        # Check if owner is empty or contains invalid characters

        if not (3 <= len(str_owner) <= 50):
            latest_error_message = "Owner name lenght should be: [3-50]"
            error_count += 1
            self.obj_VehicleListInterface.entry_edit_owner.configure(border_color="red")

        elif not all(char.isalpha() or char.isspace() for char in str_owner.strip()):
            latest_error_message = "Owner name should: [(A-Z),(a-z) and spaces] required"
            error_count += 1
            self.obj_VehicleListInterface.entry_edit_owner.configure(border_color="red")

        else:
            correct_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_owner.configure(border_color="green")

        # Check for valid manufacturing date
        current_year = datetime.datetime.now().year
        min_year = current_year - 50

        if date.isdigit() and min_year <= int(date) <= current_year:
            correct_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_edit_date.configure(border_color="green")
        else:
            latest_error_message = f" manufacturing date between {min_year} and {current_year}."
            self.obj_VehicleListInterface.label_error.configure(
                text=f"Please enter a valid manufacturing date between {min_year} and {current_year}")
            self.obj_VehicleListInterface.entry_edit_date.configure(border_color="red")
            error_count += 1

        # Check for blacklist status (0 or 1)
        if str_blacklist == 0 or str_blacklist == 1:
            correct_count += 1
            self.obj_VehicleListInterface.entry_edit_selected_status.configure(border_color="green")
        else:
            latest_error_message = "Status must be 'WhiteList' or 'BlackList'."
            self.obj_VehicleListInterface.label_error.configure(text="Status must be 'WhiteList' or 'BlackList'")
            self.obj_VehicleListInterface.entry_edit_selected_status.configure(border_color="red")
            error_count += 1

        # Check if data is already present (matching condition)
        if matching == 7:
            self.obj_VehicleListInterface.label_error.configure(text="Data is already present")
        else:
            # After all validations, show the latest error message if error_count > 0
            if error_count > 0 and latest_error_message:
                self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)
                # Update vehicle using the core method
            if matching == 7:
                self.obj_VehicleListInterface.label_error.configure(text="Data is allready present")
                self.obj_Interface.on_error(
                    "home",
                    "Data is already present",
                    "",
                    "#FF4B4B",
                    50
                )

            else:
                if error_count == 0 and matching < 7:
                    dict_status = self.obj_core.obj_Vehicle.update_vehicle(
                        str_company, str_model, str_type, str_number, str_color, date, str_owner, str_blacklist, "Anu"
                    )
                    self.obj_VehicleListInterface.reset_checkbox()
                    self.obj_VehicleListInterface.destroy_edit_vehicle_form()

                    # Check if the update was successful
                    if dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == "":
                        self.obj_Interface.switch_frames('vehicle_list')

                        # Display success message
                        self.obj_Interface.on_error(
                            "home",
                            "Data Edited Successfully",
                            "",
                            "#63CA6D",
                            50
                        )

                        self.obj_VehicleListInterface.selected_vehicle_set.clear()
                        self.obj_VehicleListInterface.update_button_states()
                        # # self.onclick_action()
                        #
                        # self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_vehicle_details(
                        #     self.obj_VehicleListInterface.i_start_index - 1,
                        #     self.obj_VehicleListInterface.dict_filter_criteria)
                        # self.obj_VehicleListInterface.update_table(
                        #     self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)

                        data = []
                        start_pos = (self.obj_VehicleListInterface.i_start_index) - 1
                        end_pos = self.obj_VehicleListInterface.i_end_index

                        if (self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] == ""):
                            for i in range(start_pos, end_pos):
                                if (self.obj_VehicleListInterface.vehicle_data[i]["vehicle_number"] == str_number):
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_type"] = str_type
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_color"] = str_color
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_owner"] = str_owner
                                    self.obj_VehicleListInterface.vehicle_data[i]["manufacturing_year"] = date
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_company"] = str_company
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_model"] = str_model
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_status"] = str_blacklist
                                    break
                            self.obj_VehicleListInterface.update_table(
                                (self.obj_VehicleListInterface.vehicle_data)[start_pos:end_pos])

                        else:
                            for i in range(0, len(self.obj_VehicleListInterface.vehicle_data)):
                                if (self.obj_VehicleListInterface.vehicle_data[i]["vehicle_number"] == str_number):
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_type"] = str_type
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_color"] = str_color
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_owner"] = str_owner
                                    self.obj_VehicleListInterface.vehicle_data[i]["manufacturing_year"] = date
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_company"] = str_company
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_model"] = str_model
                                    self.obj_VehicleListInterface.vehicle_data[i]["vehicle_status"] = str_blacklist
                                    break
                            data = self.obj_core.obj_Vehicle.search_vehicle_number(
                                self.obj_VehicleListInterface.vehicle_data,
                                self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"])
                            self.obj_VehicleListInterface.update_table(data[start_pos:end_pos])

                    else:
                        # Display error message if update failed
                        self.obj_Interface.on_error(
                            "home",
                            dict_status["str_error_msg_heading"],
                            dict_status["str_error_msg"],
                            "#FF4B4B"
                        )
                else:
                    # Display error message if fields are not filled correctly
                    self.obj_Interface.on_error(
                        "home",
                        "Error! Invalid Data",
                        "Check if the entered data fulfiles the require condition",
                        "#FF4B4B"

                    )

            return