import base64
import datetime
import re
import numpy as np
from Core.main import Core

from FlowControl.home import HomeController
from Interface.main import Interface
from tkinter import messagebox
from PIL import Image
import io
import torch

from torchvision import transforms


# from FR_Detection.Recognition import FaceProcessor
# from Core.face_image import check_image_encode


class personListController:

    def __init__(self, Core: Core, Interface: Interface):
        global pkl_file_update_status
        self.obj_core = Core
        self.obj_Interface = Interface

        self.obj_personListInterface = self.obj_Interface.dict_frames["person_list"]
        self.obj_HomeInterface = self.obj_Interface.dict_frames["home"]
        self.obj_homeController = HomeController(Core, Interface)
        self.TEMP_ID = 0
        self.DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'


        self.current_image_index = 0

        self.more_face=0

        self.image_changed= False

        self.bind_buttons()

        self.obj_personListInterface.entry_search.bind("<KeyRelease>", self.search_person)
        self.obj_personListInterface.entry_selected_owner.bind("<KeyRelease>", self.search_owner)

        self.obj_personListInterface.entry_selected_type.bind("<KeyRelease>", self.search_type)
        # self.obj_personListInterface.entry_selected_color.bind("<KeyRelease>", self.search_color)
        self.obj_personListInterface.entry_selected_owner.bind("<Button-1>",
                                                               self.obj_personListInterface.close_filter_dropdown)
        self.obj_personListInterface.entry_selected_type.bind("<Button-1>",
                                                              self.obj_personListInterface.close_filter_dropdown)
        # self.obj_personListInterface.entry_selected_color.bind("<Button-1>", self.obj_personListInterface.close_filter_dropdown)

        self.obj_personListInterface.on_form_add_ready = self.bind_add_popup_buttons
        self.obj_personListInterface.on_form_edit_ready = self.bind_edit_popup_buttons

    def bind_buttons(self):

        self.obj_personListInterface.button_filter.configure(command=self.filter_popup)
        self.obj_personListInterface.button_select_owner.configure(command=self.popup_owner_dropdown)
        self.obj_personListInterface.button_select_type.configure(command=self.popup_type_dropdown)
        # self.obj_personListInterface.button_select_color.configure(command=self.popup_color_dropdown)
        self.obj_personListInterface.button_ok.configure(command=self.onclick_ok)
        self.obj_personListInterface.button_cancel.configure(command=self.onclick_cancel)

        self.obj_personListInterface.button_next.configure(command=self.onclick_next)
        self.obj_personListInterface.button_previous.configure(command=self.onclick_previous)

        self.obj_personListInterface.button_Add.configure(command=self.onclick_add)

        self.obj_personListInterface.button_Edit.configure(command=self.onclick_edit)
        self.obj_personListInterface.button_Delete_selected.configure(command=self.onclick_delete)

        for key, value in self.obj_personListInterface.dict_columns_buttons.items():
            value[0].configure(command=lambda k=key: self.onclick_column_headings(k))

    def bind_add_popup_buttons(self):

        self.obj_personListInterface.button_add_save.configure(command=self.onclick_add_save)
        self.obj_personListInterface.button_cancel.configure(command=self.onclick_Add_cancel)
        self.obj_personListInterface.entry_first_name.bind("<KeyRelease>", self.validate_first_name)
        self.obj_personListInterface.entry_middle_name.bind("<KeyRelease>", self.validate_middle_name)
        self.obj_personListInterface.entry_last_name.bind("<KeyRelease>", self.validate_last_name)
        self.obj_personListInterface.entry_age.bind("<KeyRelease>", self.validate_age)

    def validate_first_name(self, event=None) -> bool:
        first_name = self.obj_personListInterface.entry_first_name.get().strip()

        # Check if the first name length is between 2 and 20 (you can adjust this range)
        if not (2 <= len(first_name) <= 20):
            self.obj_personListInterface.label_error.configure(
                text="First name length should be between 2 and 20 characters")
            self.obj_personListInterface.entry_first_name.configure(border_color="red")
            return False  # Exit the function if the length is incorrect

        # If the name length is correct, check if it contains only alphabets
        if first_name.isalpha():
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_first_name.configure(border_color="green")
            return True  # Valid first name
        else:
            self.obj_personListInterface.label_error.configure(text="First name should only contain alphabets!")
            self.obj_personListInterface.entry_first_name.configure(border_color="red")
            return False  # Invalid first name

    def validate_middle_name(self, event=None):
        middle_name = self.obj_personListInterface.entry_middle_name.get().strip()
        # Check if middle name is empty
        if len(middle_name) == 0:
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_middle_name.configure(border_color="green")
            return True  # Empty middle name is valid

        # Check if middle name contains only alphabetic characters
        elif not middle_name.isalpha():
            self.obj_personListInterface.label_error.configure(text="Middle name should only contain alphabets!")
            self.obj_personListInterface.entry_middle_name.configure(border_color="red")
            return False  # Invalid if it contains non-alphabetic characters

        # Check if middle name length is between 1 and 3 characters
        elif len(middle_name) < 1 or len(middle_name) > 10:
            self.obj_personListInterface.label_error.configure(text="Middle name should be between 1 and 3 characters!")
            self.obj_personListInterface.entry_middle_name.configure(border_color="red")
            return False  # Invalid if length is not between 1 and 3

        else:
            # If it passes all checks, it's valid
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_middle_name.configure(border_color="green")
            return True

    def validate_last_name(self, event=None) -> bool:
        last_name = self.obj_personListInterface.entry_last_name.get().strip()

        # Check if the first name length is between 2 and 20 (you can adjust this range)
        if not (2 <= len(last_name) <= 20):
            self.obj_personListInterface.label_error.configure(
                text="Last name length should be between 2 and 20 characters")
            self.obj_personListInterface.entry_last_name.configure(border_color="red")
            return False  # Exit the function if the length is incorrect

        # If the name length is correct, check if it contains only alphabets
        if last_name.isalpha():
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_last_name.configure(border_color="green")
            return True  # Valid first name
        else:
            self.obj_personListInterface.label_error.configure(text="Last name should only contain alphabets!")
            self.obj_personListInterface.entry_last_name.configure(border_color="red")
            return False  # Invalid first name

    def validate_age(self, event=None):
        age = self.obj_personListInterface.entry_age.get().strip()

        # Check if the age field is empty
        if len(age) == 0:
            self.obj_personListInterface.label_error.configure(text="Please Enter Age")
            self.obj_personListInterface.entry_age.configure(border_color="red")
            return False

        # Check if the age is a valid number
        if not age.isdigit():  # Ensures the input consists only of digits
            self.obj_personListInterface.label_error.configure(text="Age must be a number")
            self.obj_personListInterface.entry_age.configure(border_color="red")
            return False

        # Convert the age to an integer
        age = int(age)

        # Check if the age is within the valid range (e.g., between 0 and 120)
        if age < 15 or age > 120:
            self.obj_personListInterface.label_error.configure(text="Age must be between 15 and 120")
            self.obj_personListInterface.entry_age.configure(border_color="red")
            return False

        # If all checks pass, set the border color to green and clear any error
        self.obj_personListInterface.label_error.configure(text="")
        self.obj_personListInterface.entry_age.configure(border_color="green")
        return True

    def validate_owner(self, event=None):
        owner_name = self.obj_personListInterface.entry_owner.get().strip()
        if 3 <= len(owner_name) <= 50:
            if self.validate_owner_name(owner_name):
                # No invalid characters, valid length
                self.obj_personListInterface.label_error.configure(text="")
                self.obj_personListInterface.entry_owner.configure(border_color="green")
            else:
                # Invalid characters (contains digits or special characters)
                self.obj_personListInterface.label_error.configure(
                    text="Owner Name: [(A-Z),(a-z) and spaces only] required")
                self.obj_personListInterface.entry_owner.configure(border_color="red")
        else:
            # Length is not within the required range
            self.obj_personListInterface.label_error.configure(text="Owner Name Length between: [3-50] required")
            self.obj_personListInterface.entry_owner.configure(border_color="red")

    def validate_owner_name(self, owner_name):
        return owner_name.replace(" ", "").isalpha()

    def validate_number(self, event=None) -> bool:
        person_number = self.obj_personListInterface.entry_number.get().strip()

        # First, check if the length of the person number is between 6 and 15
        if not (6 <= len(person_number) <= 15):
            self.obj_personListInterface.label_error.configure(text="person number length between: [8-10] required")
            self.obj_personListInterface.entry_number.configure(border_color="red")
            return False  # Exit the function if the length is incorrect

        # If length is correct, then check if it matches the pattern [A-Z, 0-9] with at least 4 letters and 4 digits
        if self.validate_person_number(person_number):
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_number.configure(border_color="green")
            return True  # Valid person number
        else:
            self.obj_personListInterface.label_error.configure(text="Vehcile Number should in Indian RTO format !")
            self.obj_personListInterface.entry_number.configure(border_color="red")
            return False  # Invalid person number

    def validate_person_number(self, person_number):
        pass

    def validate_model(self, event=None):
        person_model = self.obj_personListInterface.entry_model.get().strip()
        if not (1 <= len(person_model) <= 10):
            self.obj_personListInterface.label_error.configure(text=" Model Name length between: [1-10] required")
            self.obj_personListInterface.entry_model.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_person_model(person_model):
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_model.configure(border_color="green")
        else:
            self.obj_personListInterface.label_error.configure(text="Model Name: [(A-Z),(a-z),(0-9),(-)] required")
            self.obj_personListInterface.entry_model.configure(border_color="red")

    def validate_person_model(self, person_model):
        pattern = r'^[A-Z a-z0-9-]+$'  # Allows uppercase letters and digits only
        return bool(re.match(pattern, person_model.upper()))

    def validate_colour(self, event=None):
        colour = self.obj_personListInterface.entry_color.get().strip()

        if not 3 <= len(colour) and len(colour) <= 10:
            self.obj_personListInterface.label_error.configure(text="colour length between: [3-15] required")
            self.obj_personListInterface.entry_color.configure(border_color="red")

        elif self.validate_person_colour(colour):
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_color.configure(border_color="green")



        else:
            self.obj_personListInterface.label_error.configure(text=" valid colour name: [(A-Z),(a-z)] required")
            self.obj_personListInterface.entry_color.configure(border_color="red")

    def validate_person_colour(self, colour):
        return colour.isalpha()

    def validate_manufacturing_year(self, event=None):
        year = self.obj_personListInterface.entry_date.get().strip()

        if self.validate_person_year(year):  # Just pass 'year'
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_date.configure(border_color="green")
        elif len(year) == 0:
            self.obj_personListInterface.label_error.configure(text="Enter Manufacturing year")
            self.obj_personListInterface.entry_date.configure(border_color="red")
        else:
            current_year = datetime.datetime.now().year  # Get current year
            self.obj_personListInterface.label_error.configure(
                text=f"Manufacturing date must be number between: {current_year - 50} and {current_year}"
            )
            self.obj_personListInterface.entry_date.configure(border_color="red")

    def validate_person_year(self, year):
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
        type = self.obj_personListInterface.entry_type.cget().strip()
        print(f"Selected Type: {type}")  # Debugging line

        if self.validate_person_type(type):
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_type.configure(border_color="green")

    def validate_person_type(self, type):
        return type in ["WhiteList", "BlackList"]

    # ----------------------------------------------------------[validiation add ends]----------------------------------------------------------------------------------------------------

    def bind_edit_popup_buttons(self):
        #  self.obj_personListInterface.entry_edit_selected_status.bind("<KeyRelease>", self.search_edit_status)
        self.obj_personListInterface.Edit_button_add_save.configure(command=self.onclick_edit_save)
        self.obj_personListInterface.Edit_entry_first_name.bind("<KeyRelease>", self.validate_Edit_first_name)
        self.obj_personListInterface.Edit_entry_last_name.bind("<KeyRelease>", self.validate_Edit_last_name)
        self.obj_personListInterface.Edit_entry_middle_name.bind("<KeyRelease>", self.validate_Edit_middle_name)
        self.obj_personListInterface.Edit_entry_age.bind("<KeyRelease>", self.validate_Edit_age)
        # self.obj_personListInterface.Edit_button_prev.configure(command=self.onclick_edit_prev_image)
        # self.obj_personListInterface.Edit_button_next.configure(command=self.onclick_edit_next_image)

    def validate_Edit_first_name(self, event=None) -> bool:
        first_name = self.obj_personListInterface.Edit_entry_first_name.get().strip()

        # Check if the first name length is between 2 and 20 (you can adjust this range)
        if not (2 <= len(first_name) <= 20):
            self.obj_personListInterface.Edit_label_error.configure(
                text="First name length should be between 2 and 20 characters")
            self.obj_personListInterface.Edit_entry_first_name.configure(border_color="red")
            return False  # Exit the function if the length is incorrect

        # If the name length is correct, check if it contains only alphabets
        if first_name.isalpha():
            self.obj_personListInterface.Edit_label_error.configure(text="")
            self.obj_personListInterface.Edit_entry_first_name.configure(border_color="green")
            return True  # Valid first name
        else:
            self.obj_personListInterface.Edit_label_error.configure(text="First name should only contain alphabets!")
            self.obj_personListInterface.Edit_entry_first_name.configure(border_color="red")
            return False  # Invalid first name

    def validate_Edit_middle_name(self, event=None):
        middle_name = self.obj_personListInterface.Edit_entry_middle_name.get().strip()
        # Check if middle name is empty
        if len(middle_name) == 0:
            self.obj_personListInterface.Edit_label_error.configure(text="")
            self.obj_personListInterface.Edit_entry_middle_name.configure(border_color="green")
            return True  # Empty middle name is valid

        # Check if middle name contains only alphabetic characters
        elif not middle_name.isalpha():
            self.obj_personListInterface.Edit_label_error.configure(text="Middle name should only contain alphabets!")
            self.obj_personListInterface.Edit_entry_middle_name.configure(border_color="red")
            return False  # Invalid if it contains non-alphabetic characters

        # Check if middle name length is between 1 and 3 characters
        elif len(middle_name) < 1 or len(middle_name) > 10:
            self.obj_personListInterface.Edit_label_error.configure(
                text="Middle name should be between 1 and 3 characters!")
            self.obj_personListInterface.Edit_entry_middle_name.configure(border_color="red")
            return False  # Invalid if length is not between 1 and 3

        else:
            # If it passes all checks, it's valid
            self.obj_personListInterface.Edit_label_error.configure(text="")
            self.obj_personListInterface.Edit_entry_middle_name.configure(border_color="green")
            return True

    def validate_Edit_last_name(self, event=None) -> bool:
        last_name = self.obj_personListInterface.Edit_entry_last_name.get().strip()

        # Check if the first name length is between 2 and 20 (you can adjust this range)
        if not (2 <= len(last_name) <= 20):
            self.obj_personListInterface.Edit_label_error.configure(
                text="Last name length should be between 2 and 20 characters")
            self.obj_personListInterface.Edit_entry_last_name.configure(border_color="red")
            return False  # Exit the function if the length is incorrect

        # If the name length is correct, check if it contains only alphabets
        if last_name.isalpha():
            self.obj_personListInterface.Edit_label_error.configure(text="")
            self.obj_personListInterface.Edit_entry_last_name.configure(border_color="green")
            return True  # Valid first name
        else:
            self.obj_personListInterface.Edit_label_error.configure(text="Last name should only contain alphabets!")
            self.obj_personListInterface.Edit_entry_last_name.configure(border_color="red")
            return False  # Invalid first name

    def validate_Edit_age(self, event=None):
        age = self.obj_personListInterface.Edit_entry_age.get().strip()

        # Check if the age field is empty
        if len(age) == 0:
            self.obj_personListInterface.Edit_label_error.configure(text="Enter Age")
            self.obj_personListInterface.Edit_entry_age.configure(border_color="red")
            return False

        # Check if the age is a valid number
        if not age.isdigit():  # Ensures the input consists only of digits
            self.obj_personListInterface.Edit_label_error.configure(text="Age must be a number")
            self.obj_personListInterface.Edit_entry_age.configure(border_color="red")
            return False

        # Convert the age to an integer
        age = int(age)

        # Check if the age is within the valid range (e.g., between 0 and 120)
        if age < 15 or age > 120:
            self.obj_personListInterface.Edit_label_error.configure(text="Age must be between 15 and 120")
            self.obj_personListInterface.Edit_entry_age.configure(border_color="red")
            return False

        # If all checks pass, set the border color to green and clear any error
        self.obj_personListInterface.Edit_label_error.configure(text="")
        self.obj_personListInterface.Edit_entry_age.configure(border_color="green")
        return True

    def validate_edit_owner(self, event=None):
        owner_name = self.obj_personListInterface.entry_edit_owner.get().strip()
        if not 3 <= len(owner_name) <= 50:
            self.obj_personListInterface.label_error.configure(text="Owner Name length  between [3-50] required")
            self.obj_personListInterface.entry_edit_owner.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_owner_name(owner_name):
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_edit_owner.configure(border_color="green")
        else:
            self.obj_personListInterface.label_error.configure(
                text=" Owner Name should be: [(A-Z),(a-z),and spaces] required")
            self.obj_personListInterface.entry_edit_owner.configure(border_color="red")

    def validate_owner_name(self, owner_name):
        return owner_name.replace(" ", "").isalpha()

    def validate_edit_model(self, event=None):
        person_model = self.obj_personListInterface.entry_edit_model.get().strip()
        if not (1 <= len(person_model) <= 10):
            self.obj_personListInterface.label_error.configure(text=" Model Name length between: [1-10] required")
            self.obj_personListInterface.entry_edit_model.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_person_model(person_model):
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_edit_model.configure(border_color="green")
        else:
            self.obj_personListInterface.label_error.configure(text="Model Name: [(A-Z),(a-z),(0-9),(-)] required")
            self.obj_personListInterface.entry_edit_model.configure(border_color="red")

    def validate_person_model(self, person_model):
        pattern = r'^[A-Z a-z0-9-]+$'  # Allows uppercase letters and digits only
        return bool(re.match(pattern, person_model.upper()))

    def validate_edit_colour(self, event=None):
        colour = self.obj_personListInterface.entry_edit_color.get().strip()
        if not 3 <= len(colour) <= 10:
            self.obj_personListInterface.label_error.configure(text="Color length: [3-10] required")
            self.obj_personListInterface.entry_edit_color.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_person_colour(colour):
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_edit_color.configure(border_color="green")
        else:
            self.obj_personListInterface.label_error.configure(text="Colour should be: [(A-Z),(a-z)] required")
            self.obj_personListInterface.entry_edit_color.configure(border_color="red")

    def validate_person_colour(self, colour):
        return colour.isalpha()

    def validate_edit_manufacturing_year(self, event=None):
        year = self.obj_personListInterface.entry_edit_date.get().strip()

        # Get the current year dynamically
        current_year = datetime.datetime.now().year

        if not year:
            self.obj_personListInterface.label_error.configure(text="Please enter Manufacture year")
            self.obj_personListInterface.entry_edit_date.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_person_year(year):
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_edit_date.configure(border_color="green")
        else:
            self.obj_personListInterface.label_error.configure(
                text=f"Manufacturing date must be number between [{current_year - 50} - {current_year}]")
            self.obj_personListInterface.entry_edit_date.configure(border_color="red")

    def validate_person_year(self, year):
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
        type = self.obj_personListInterface.entry_edit_type.get().strip()
        if not type:
            self.obj_personListInterface.label_error.configure(text="Please Enter Vehcile Type")
            self.obj_personListInterface.entry_edit_type.configure(
                border_color="red")  # Reset to default gray if empty or spaces
        elif self.validate_person_type(type):
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_edit_type.configure(border_color="green")
        else:
            self.obj_personListInterface.label_error.configure(text="Please Select Vehcile Type from dropdown")
            self.obj_personListInterface.entry_edit_type.configure(border_color="red")

    def validate_person_type(self, type):
        return type in ["WhiteList", "BlackList"]

    def search_Edit_type_new(self, entryfield, row=0, rowspan=2, interface_obj=None, parent=None, fun=0, event=None):

        text_entered = entryfield.get().lstrip(" ")
        text_entered = text_entered
        dict_status = []
        if fun == 0:
            dict_status = self.obj_core.obj_person.search_person_type(text_entered)
            if len(dict_status) == 1 and dict_status[0] == text_entered and dict_status[0] != 'All':
                entryfield.configure(border_color="green")
                self.obj_personListInterface.label_error.configure(text="")
            else:
                self.obj_personListInterface.label_error.configure(
                    text="Vehcile Type should be selected from the dropdown")
                entryfield.configure(border_color="red")

        elif fun == 1:
            dict_status = self.obj_core.obj_person.search_person_company(text_entered)

            if len(dict_status) == 1 and dict_status[0] == text_entered and dict_status[0] != 'All':
                entryfield.configure(border_color="green")
                self.obj_personListInterface.label_error.configure(text="")
            else:
                self.obj_personListInterface.label_error.configure(
                    text="Vehcile Company should be selected from the dropdown")
                entryfield.configure(border_color="red")

        interface_obj.popup_Edit_dropdown(parent, dict_status, entry_destination=entryfield, i_row=row,
                                          i_rowspan=rowspan, type=0)

    # ____________________________________________________________[filter search]___________________________________________________________________________________________

    def search_person(self, event):
        if (self.obj_personListInterface.bool_type_dropdown_opened):
            self.obj_personListInterface.close_dropdown(None)
            self.obj_personListInterface.bool_type_dropdown_opened = False
        elif (self.obj_personListInterface.bool_color_dropdown_opened):
            self.obj_personListInterface.close_dropdown(None)
            self.obj_personListInterface.bool_color_dropdown_opened = False

        if (self.obj_personListInterface.bool_owner_dropdown_opened):
            self.obj_personListInterface.close_dropdown(None)
            self.obj_personListInterface.bool_owner_dropdown_opened = False

        # str_person_number = self.obj_personListInterface.entry_search.get().lstrip(" ")
        # str_person_number = str_person_number.upper()

        # list_person_data = self.obj_core.obj_person.search_person_number(
        #     self.obj_Interface.dict_frames["person_list"].person_data, str_person_number)
        # self.obj_Interface.dict_frames["person_list"].update_table(list_person_data)

        # str_full_name = (self.obj_personListInterface.entry_search.get().lstrip(" ")).upper()
        str_full_name = (self.obj_personListInterface.entry_search.get().lstrip(" ")).upper()
        list_searched_data = []

        if (str_full_name != ""):
            list_searched_data = self.obj_core.obj_person.search_person_number(
                self.obj_personListInterface.person_data, str_full_name)
            self.obj_personListInterface.i_total_data = len(list_searched_data)
        else:
            list_searched_data = self.obj_personListInterface.person_data
            self.obj_personListInterface.i_total_data = len(self.obj_personListInterface.person_data)

        if (self.obj_personListInterface.i_total_data > 0):
            self.obj_personListInterface.i_start_index = 1
            self.obj_personListInterface.i_end_index = 5 if self.obj_personListInterface.i_total_data >= 5 else self.obj_personListInterface.i_total_data

        # self.obj_personListInterface.dict_filter_criteria["str_person_number"] = str_person_number
        self.obj_personListInterface.update_table(list_searched_data[0:5])

    def search_owner(self, event):
        if (self.obj_personListInterface.bool_type_dropdown_opened):
            self.obj_personListInterface.popup_dropdown()
            self.obj_personListInterface.bool_type_dropdown_opened = False
        elif (self.obj_personListInterface.bool_color_dropdown_opened):
            self.obj_personListInterface.popup_dropdown()
            self.obj_personListInterface.bool_color_dropdown_opened = False

        if (self.obj_personListInterface.bool_owner_dropdown_opened):
            self.obj_personListInterface.popup_dropdown()
            self.obj_personListInterface.bool_owner_dropdown_opened = False
        str_owner_name = self.obj_personListInterface.entry_selected_owner.get().lstrip(" ")
        str_owner_name = str_owner_name
        if str_owner_name != "":
            dict_status = self.obj_core.obj_person.search_person_owner(str_owner_name)

            self.obj_personListInterface.popup_dropdown(list_data=dict_status,
                                                        entry_destination=self.obj_personListInterface.entry_selected_owner,
                                                        i_row=4,
                                                        i_rowspan=3)
            self.obj_personListInterface.bool_owner_dropdown_opened = True
        else:
            self.obj_personListInterface.bool_owner_dropdown_opened = False

    def search_type(self, event):
        if (self.obj_personListInterface.bool_type_dropdown_opened):
            self.obj_personListInterface.popup_dropdown()
            self.obj_personListInterface.bool_type_dropdown_opened = False
        elif (self.obj_personListInterface.bool_color_dropdown_opened):
            self.obj_personListInterface.popup_dropdown()
            self.obj_personListInterface.bool_color_dropdown_opened = False

        if (self.obj_personListInterface.bool_owner_dropdown_opened):
            self.obj_personListInterface.close_dropdown()
            self.obj_personListInterface.bool_owner_dropdown_opened = False

        str_person_type = self.obj_personListInterface.entry_selected_type.get().lstrip(" ")
        str_person_type = str_person_type
        dict_status = self.obj_core.obj_person.search_person_type(str_person_type)

        self.obj_personListInterface.popup_dropdown(list_data=dict_status,
                                                    entry_destination=self.obj_personListInterface.entry_selected_type,
                                                    i_row=6,
                                                    i_rowspan=3)
        self.obj_personListInterface.bool_type_dropdown_opened = True

    def search_color(self, event):
        str_person_color = self.obj_personListInterface.entry_selected_color.get().lstrip(" ")
        str_person_color = str_person_color
        dict_status = self.obj_core.obj_person.search_person_color(str_person_color)

        self.obj_personListInterface.popup_dropdown(list_data=dict_status,
                                                    entry_destination=self.obj_personListInterface.entry_selected_color,
                                                    i_row=8,
                                                    i_rowspan=2)
        self.obj_personListInterface.bool_color_dropdown_opened = True

    def filter_popup(self):
        self.obj_personListInterface.toggle_filter_popup()

    def popup_owner_dropdown(self):
        if (self.obj_personListInterface.bool_type_dropdown_opened):
            current_type = self.obj_personListInterface.entry_selected_type.get()
            if current_type not in ["Select Status", "All", 'Male', 'Female', 'Other']:
                # Revert type dropdown to original state
                self.obj_personListInterface.entry_selected_type.delete(0, 'end')
                self.obj_personListInterface.entry_selected_type.insert(0, "Select Status")

            # self.obj_personListInterface.popup_dropdown(None)
            self.obj_personListInterface.bool_type_dropdown_opened = False
        elif (self.obj_personListInterface.bool_color_dropdown_opened):
            # Check if color dropdown has a value selected
            current_color = self.obj_personListInterface.entry_selected_color.get()
            if current_color not in ["Select ", "All", "WhiteList", "BlackList"]:
                # Revert color dropdown to original state
                self.obj_personListInterface.entry_selected_color.delete(0, 'end')
                self.obj_personListInterface.entry_selected_color.insert(0, "Select person Color")

            # self.obj_personListInterface.popup_dropdown(None)
            self.obj_personListInterface.bool_color_dropdown_opened = False

        # Handle owner dropdown
        if (self.obj_personListInterface.bool_owner_dropdown_opened):
            # self.obj_personListInterface.popup_dropdown(None)
            self.obj_personListInterface.close_filter_dropdown(None)

            self.obj_personListInterface.bool_owner_dropdown_opened = False
        else:
            dict_status = self.obj_core.obj_person.get_all_person_owner()
            dict_status["list_owner"].append("All")
            self.obj_personListInterface.popup_dropdown(list_data=["Male", "Female", "Other", "All"],
                                                        entry_destination=self.obj_personListInterface.entry_selected_owner,
                                                        i_row=4,
                                                        i_rowspan=3)
            self.obj_personListInterface.bool_owner_dropdown_opened = True
        self.obj_personListInterface.entry_selected_owner.focus()

    def popup_type_dropdown(self):
        # Check if owner dropdown is open and close it
        if (self.obj_personListInterface.bool_owner_dropdown_opened):
            # Check if owner dropdown has a value selected
            current_owner = self.obj_personListInterface.entry_selected_owner.get()
            if current_owner not in ["Select Gender", "All"]:
                # Revert owner dropdown to original state
                self.obj_personListInterface.entry_selected_owner.delete(0, 'end')
                self.obj_personListInterface.entry_selected_owner.insert(0, "Select Gender")
            self.obj_personListInterface.close_filter_dropdown(None)
            self.obj_personListInterface.popup_dropdown()
            self.obj_personListInterface.bool_owner_dropdown_opened = False
        elif (self.obj_personListInterface.bool_color_dropdown_opened):
            # Check if color dropdown has a value selected
            current_color = self.obj_personListInterface.entry_selected_color.get()
            if current_color not in ["Select Status", "All"]:
                # Revert color dropdown to original state
                self.obj_personListInterface.entry_selected_color.delete(0, 'end')
                self.obj_personListInterface.entry_selected_color.insert(0, "Select person Color")

            # self.obj_personListInterface.popup_dropdown(None)
            self.obj_personListInterface.bool_color_dropdown_opened = False

        # Handle type dropdown
        if (self.obj_personListInterface.bool_type_dropdown_opened is True):
            self.obj_personListInterface.close_filter_dropdown(None)

            # self.obj_personListInterface.popup_dropdown(None)
            self.obj_personListInterface.bool_type_dropdown_opened = False
        else:
            dict_status = self.obj_core.obj_person.get_all_person_type()
            dict_status["list_type"].append("All")
            self.obj_personListInterface.popup_dropdown(list_data=["WhiteList", "BlackList", 'All'],
                                                        entry_destination=self.obj_personListInterface.entry_selected_type,
                                                        i_row=6,
                                                        i_rowspan=3)
            self.obj_personListInterface.bool_type_dropdown_opened = True
        self.obj_personListInterface.entry_selected_type.focus()

    def popup_color_dropdown(self):
        # Check if type dropdown is open and close it
        if (self.obj_personListInterface.bool_type_dropdown_opened):
            # Check if type dropdown has a value selected
            current_type = self.obj_personListInterface.entry_selected_type.get()
            if current_type not in ["Select person Type", "All"]:
                # Revert type dropdown to original state
                self.obj_personListInterface.entry_selected_type.delete(0, 'end')
                self.obj_personListInterface.entry_selected_type.insert(0, "Select person Type")
            self.obj_personListInterface.close_dropdown()

            # self.obj_personListInterface.popup_dropdown(None)
            self.obj_personListInterface.bool_type_dropdown_opened = False
        elif (self.obj_personListInterface.bool_owner_dropdown_opened):
            # Check if owner dropdown has a value selected
            current_owner = self.obj_personListInterface.entry_selected_owner.get()
            if current_owner not in ["Select Owner Name", "All"]:
                # Revert owner dropdown to original state
                self.obj_personListInterface.entry_selected_owner.delete(0, 'end')
                self.obj_personListInterface.entry_selected_owner.insert(0, "Select Owner Name")

            self.obj_personListInterface.close_filter_dropdown(None)
            # self.obj_personListInterface.close_dropdown(None)
            self.obj_personListInterface.popup_dropdown()
            self.obj_personListInterface.bool_owner_dropdown_opened = False

        # Handle color dropdown
        if (self.obj_personListInterface.bool_color_dropdown_opened is True):
            self.obj_personListInterface.close_filter_dropdown(None)
            self.obj_personListInterface.bool_color_dropdown_opened = False
        else:
            dict_status = self.obj_core.obj_person.get_all_person_color()
            dict_status["list_color"].append("All")
            self.obj_personListInterface.popup_dropdown(list_data=dict_status["list_color"],
                                                        entry_destination=self.obj_personListInterface.entry_selected_color,
                                                        i_row=8,
                                                        i_rowspan=2)
            self.obj_personListInterface.bool_color_dropdown_opened = True

        self.obj_personListInterface.entry_selected_color.focus()

    def onclick_ok(self):
        str_owner = self.obj_personListInterface.entry_selected_owner.get().strip().upper()

        self.obj_personListInterface.dict_filter_criteria["gender"] = "%" if (
                str_owner == "ALL" or str_owner == "") else str_owner

        str_type = self.obj_personListInterface.entry_selected_type.get().lstrip(" ")
        self.obj_personListInterface.dict_filter_criteria["status"] = "%" if (
                str_type == "All" or str_type == "") else str_type

        self.obj_personListInterface.reset_interface()
        self.obj_Interface.obj_RootInterface.focus_set()
        self.obj_personListInterface.person_data = []
        self.obj_personListInterface.person_data = self.obj_core.obj_person.fetch_person_details(
            self.obj_personListInterface.dict_filter_criteria)
        self.obj_personListInterface.i_total_data = len(self.obj_personListInterface.person_data)
        if (self.obj_personListInterface.i_total_data > 0):
            self.obj_Interface.dict_frames["person_list"].i_start_index = 1
            self.obj_Interface.dict_frames[
                "person_list"].i_end_index += 5 if self.obj_personListInterface.i_total_data >= 5 else self.obj_personListInterface.i_total_data

        self.obj_personListInterface.update_table((self.obj_personListInterface.person_data)[0:5])

    def onclick_cancel(self):
        self.obj_personListInterface.reset_filter_form()
        if (self.obj_personListInterface.bool_filter_popup is True):
            self.obj_personListInterface.popup_dropdown()
            self.obj_personListInterface.reset_filter_form()
            self.obj_personListInterface.toggle_filter_popup()

    def onclick_column_headings(self, str_column: str):
        # col_name=str_column
        # self.obj_personListInterface.sort_column(col_name)

        str_db_column = "full_name"

        if (str_column == "Age"):
            str_db_column = "age"
        elif (str_column == "Gender"):
            str_db_column = "gender"
        if (str_column == "full_name"):
            str_db_column = "name"
        elif (str_column == "Status"):
            str_db_column = "status"

        self.obj_personListInterface.person_data = self.obj_core.obj_person.sort_person_data(
            self.obj_personListInterface.person_data,
            str_db_column,
            self.obj_personListInterface.dict_columns_buttons[str_column][1])
        self.obj_personListInterface.sort_column(str_column,
                                                 self.obj_personListInterface.dict_columns_buttons[str_column][1])

        self.obj_personListInterface.dict_columns_buttons[str_column][1] = not \
            self.obj_personListInterface.dict_columns_buttons[str_column][1]

        self.obj_personListInterface.update_table(self.obj_personListInterface.person_data)

    def onclick_next(self):

        self.obj_Interface.obj_RootInterface.focus_set()
        if (self.obj_personListInterface.bool_filter_popup is True):
            # self.obj_personListInterface.close_dropdown(None)
            # self.obj_personListInterface.popup_dropdown(None)
            self.obj_personListInterface.reset_filter_form()
            self.obj_personListInterface.toggle_filter_popup()

        data = []
        required_data = []
        if (self.obj_personListInterface.dict_filter_criteria["full_name"] != ""):
            temp_name = self.obj_personListInterface.entry_search.get()
            self.obj_personListInterface.dict_filter_criteria["full_name"] = temp_name.upper()
            data = self.obj_core.obj_person.search_person_number(self.obj_personListInterface.person_data,
                                                                 self.obj_personListInterface.dict_filter_criteria[
                                                                     "full_name"])
        else:
            data = self.obj_personListInterface.person_data

        required_data = data[
                        (self.obj_personListInterface.i_end_index): ((self.obj_personListInterface.i_end_index) + 5)]
        i_data_count = len(required_data)
        if (i_data_count > 0):
            self.obj_personListInterface.i_start_index = self.obj_personListInterface.i_end_index + 1
            self.obj_personListInterface.i_end_index = self.obj_personListInterface.i_end_index + i_data_count

        self.obj_personListInterface.update_table(required_data)

        # data = []
        # required_data = []
        # if(self.obj_PersonListInterface.dict_filter_criteria["full_name"] != ""):
        #     data = self.obj_core.obj_Vehicle.search_vehicle_number(self.obj_PersonListInterface.vehicle_data, self.obj_PersonListInterface.dict_filter_criteria["str_vehicle_number"])
        # else:
        #     data = self.obj_PersonListInterface.vehicle_data

        # required_data = data[(self.obj_PersonListInterface.i_end_index) : ((self.obj_PersonListInterface.i_end_index) + 5)]
        # i_data_count = len(required_data)
        # if(i_data_count > 0 ):
        #     self.obj_PersonListInterface.i_start_index = self.obj_PersonListInterface.i_end_index + 1
        #     self.obj_PersonListInterface.i_end_index = self.obj_PersonListInterface.i_end_index + i_data_count

        # self.obj_PersonListInterface.update_table(required_data)

    def onclick_previous(self):
        self.obj_Interface.obj_RootInterface.focus_set()
        if (self.obj_personListInterface.bool_filter_popup is True):
            self.obj_personListInterface.close_dropdown(None)
            self.obj_personListInterface.reset_filter_form()
            self.obj_personListInterface.toggle_filter_popup()

        data = []
        required_data = []
        if (self.obj_personListInterface.dict_filter_criteria["full_name"] != ""):
            data = self.obj_core.obj_person.search_person_number(self.obj_personListInterface.person_data,
                                                                 self.obj_personListInterface.dict_filter_criteria[
                                                                     "full_name"])
        else:
            data = self.obj_personListInterface.person_data

        required_data = data[((self.obj_personListInterface.i_start_index) - 6): (
                (self.obj_personListInterface.i_start_index) - 1)]
        i_data_count = len(required_data)
        if (i_data_count > 0):
            self.obj_personListInterface.i_end_index = (self.obj_personListInterface.i_start_index) - 1
            self.obj_personListInterface.i_start_index = (self.obj_personListInterface.i_start_index) - 5

        self.obj_personListInterface.update_table(required_data)

    def onclick_add(self):
        self.obj_personListInterface.Add_Face_Form()

    def onclick_Add_cancel(self):
        self.obj_personListInterface.destroy_registration_form()



    # def cosine_similarity(self,emb1, emb2):
    #     emb1 = emb1 / emb1.norm(p=2, dim=1, keepdim=True)
    #     emb2 = emb2 / emb2.norm(p=2, dim=1, keepdim=True)
    #     return torch.nn.functional.cosine_similarity(emb1, emb2)
    #
    #     # Function to get face embedding
    #
    #
    #     # Function to validate if all faces belong to the same person
    # def validate_faces(self,embeddings, threshold=0.6):
    #     fail_count = 0
    #     total_comparisons = 0
    #
    #     for i in range(len(embeddings)):
    #         for j in range(i + 1, len(embeddings)):
    #             sim = self.cosine_similarity(embeddings[i], embeddings[j])
    #             print(f"Similarity between Image {i + 1} and Image {j + 1}: {sim.item():.4f}")
    #             total_comparisons += 1
    #             if sim.item() < threshold:
    #                 fail_count += 1
    #
    #     allowed_failures = 1
    #
    #     if fail_count <= allowed_failures:
    #         print("\n✅ All faces belong to the same person!")
    #         return True
    #     else:
    #         print("\n❌ Faces do NOT belong to the same person.")
    #         return False
    #
    #
    #
    def find_mean_of_images_base64(self, pic1, pic2, pic3, pic4, pic5):

        images_base64 = [pic1, pic2, pic3, pic4, pic5]
        embeddings = []
        face_num=0

        for b64_image in images_base64:
            try:
                # Decode base64 to PIL Image
                img_data = base64.b64decode(b64_image)
                img = Image.open(io.BytesIO(img_data)).convert('RGB')

                # Detect face
                boxes, _ = self.mtcnn.detect(img)

                if boxes is not None and len(boxes) == 1:
                    face_num= 0
                    x1, y1, x2, y2 = map(int, boxes[0])

                    # Crop and preprocess
                    face_crop = img.crop((x1, y1, x2, y2)).resize((160, 160))
                    face_tensor = transforms.ToTensor()(face_crop).unsqueeze(0).to(self.DEVICE)

                    # Generate embedding
                    with torch.no_grad():
                        embedding = self.resnet(face_tensor).cpu().numpy()
                        embeddings.append(embedding[0])
                else:
                    if boxes is not None and (len(boxes) > 1):
                        face_num=1
                        break
                    else:
                       face_num = 3
                       break

            except Exception as e:
                face_num = 2
                print(f"[Warning] Failed to process image: {e}")
                break

        if embeddings:
            mean_embedding = np.mean(embeddings, axis=0)
            return mean_embedding, face_num
        else:
            print("[Error] No valid face found in any image.")
            return None, face_num





    # def find_mean_of_images_base64(self, pic1, pic2, pic3, pic4, pic5):
    #     face_num=0
    #     images_base64 = [pic1, pic2, pic3, pic4, pic5]
    #
    #
    #     embeddings_for_db = []
    #     embeddings_for_validation= []
    #
    #     for b64_image in images_base64:
    #         try:
    #             # Decode base64 to PIL Image
    #             img_data = base64.b64decode(b64_image)
    #             img = Image.open(io.BytesIO(img_data)).convert('RGB')
    #
    #             # Detect face
    #             boxes, _ = self.mtcnn.detect(img)
    #
    #             if boxes is not None and len(boxes) == 1:
    #                 x1, y1, x2, y2 = map(int, boxes[0])
    #
    #                 # Crop and preprocess
    #                 face = img.crop((x1, y1, x2, y2)).resize((160, 160))
    #                 face = transforms.ToTensor()(face).unsqueeze(0).to(self.DEVICE)
    #
    #
    #                 # Optional Flip Trick
    #                 face_flipped = torch.flip(face, dims=[3])  # horizontal flip
    #
    #                 with torch.no_grad():
    #                     emb_original = self.resnet(face)
    #                     emb_flipped = self.resnet(face_flipped)
    #
    #                 # Average embeddings
    #                 embedding = (emb_original + emb_flipped) / 2.0
    #                 if embedding is None:
    #                     face_num = 2
    #                 embeddings_for_validation.append(embedding)
    #
    #                 face_num = 0
    #                 x1, y1, x2, y2 = map(int, boxes[0])
    #
    #                 # Crop and preprocess
    #                 face_crop = img.crop((x1, y1, x2, y2)).resize((160, 160))
    #                 face_tensor = transforms.ToTensor()(face_crop).unsqueeze(0).to(self.DEVICE)
    #
    #                 # Generate embedding
    #                 with torch.no_grad():
    #                     embedding_db_format = self.resnet(face_tensor).cpu().numpy()
    #                     embeddings_for_db.append(embedding_db_format[0])
    #             else:
    #                 if boxes is not None and (len(boxes) > 1):
    #                     face_num=1
    #                     break
    #                 else:
    #                    face_num = 3
    #                    break
    #
    #         except Exception as e:
    #             face_num = 2
    #             print(f"[Warning] Failed to process image: {e}")
    #             break
    #
    #     if embeddings_for_db:
    #         mean_embedding = np.mean(embeddings_for_db, axis=0)
    #         # print("img -------------  \n", embeddings_for_validation, "\n")
    #         return mean_embedding , face_num
    #     else:
    #         print("[Error] No valid face found in any image.")
    #         return None,face_num
    # Cosine similarity function with normalization


    def cosine_similarity(self,emb1, emb2):
        emb1 = emb1 / emb1.norm(p=2, dim=1, keepdim=True)
        emb2 = emb2 / emb2.norm(p=2, dim=1, keepdim=True)
        return torch.nn.functional.cosine_similarity(emb1, emb2)

        # Function to get face embedding

    def get_embedding(self,img):

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        img_data = base64.b64decode(img_base64)
        img = Image.open(io.BytesIO(img_data)).convert('RGB')

        faces = self.mtcnnValidation(img)

        if faces is None or len(faces.shape) != 4:
            print(f"No face detected ")
            return None

        # Select biggest detected face
        if faces.shape[0] > 1:
            areas = [(face.shape[1] * face.shape[2]) for face in faces]
            biggest_idx = np.argmax(areas)
            face = faces[biggest_idx]
        else:
             face = faces[0]

        face = face.unsqueeze(0).to(self.DEVICE)

        # Optional Flip Trick
        face_flipped = torch.flip(face, dims=[3])
        with torch.no_grad():
            emb_original = self.resnet(face)
            emb_flipped = self.resnet(face_flipped)

        # Average embeddings
        embedding = (emb_original + emb_flipped) / 2.0
        return embedding

        # Function to validate if all faces belong to the same person

    def validate_faces(self,image_paths, threshold=0.6):
        embeddings = []

        for path in image_paths:
            embedding = self.get_embedding(path)

            if embedding is None:
                print(f"Skipping {path} due to detection failure.")
                return False
            embeddings.append(embedding)


        # Compare all embeddings
        fail_count = 0
        total_comparisons = 0

        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = self.cosine_similarity(embeddings[i], embeddings[j])
                print(f"Similarity between Image {i + 1} and Image {j + 1}: {sim.item():.4f}")
                total_comparisons += 1
                if sim.item() < threshold:
                    fail_count += 1

        allowed_failures = 1

        if fail_count <= allowed_failures:
            print("\n✅ All faces belong to the same person!")
            return True
        else:
            print("\n❌ Faces do NOT belong to the same person.")
            return False

    def onclick_add_save(self):
        global pkl_file_update_status
        # Retrieve data from the interface
        str_path = self.obj_personListInterface.photo_path
        str_first_name = self.obj_personListInterface.entry_first_name.get().strip()
        str_middle_name = self.obj_personListInterface.entry_middle_name.get().strip()

        str_last_name = self.obj_personListInterface.entry_last_name.get().strip()
        str_age = self.obj_personListInterface.entry_age.get().strip()
        str_gender = self.obj_personListInterface.entry_selected_gender.get().strip()
        str_status = self.obj_personListInterface.entry_selected_status.get().strip()
        error_count = 0

        photo_count = len(self.obj_personListInterface.photos)
        # if photo_count == 5:
        #     # self.obj_personListInterface.label_error.configure(text=" Please upload 5 photos.'")
        #     self.obj_personListInterface.img_label.configure(border_color="green")
        # if self.more_face==1:
        #     error_count=+1
        #     latest_error_message = " More than one person face is visible."

        if photo_count < 5:
            error_count += 1
            latest_error_message = "Please upload 5 photos."
            self.obj_personListInterface.label_error.configure(text=" Please upload 5 photos.'")
            # self.obj_personListInterface.img_label.configure(border_color="red")
            # You can also show a messagebox if it's a GUI app:
            # messagebox.showerror("Upload Error", "Please upload exactly 5 photos.")
        elif photo_count > 5:
            error_count+=1
            print("⚠️ Error: You can upload a maximum of 5 photos.")
            latest_error_message = "You can upload a maximum of 5 photos."
            self.obj_personListInterface.label_error.configure(text="  You can upload a maximum of 5 photos.'")
            # self.obj_personListInterface.img_label.configure(border_color="red")
            # messagebox.showerror("Upload Error", "You can upload a maximum of 5 photos.")
        else:
            # Exactly 5 photos — safe to proceed
            pic1 = self.obj_personListInterface.photos[0]['photo_base64']
            pic2 = self.obj_personListInterface.photos[1]['photo_base64']
            pic3 = self.obj_personListInterface.photos[2]['photo_base64']
            pic4 = self.obj_personListInterface.photos[3]['photo_base64']
            pic5 = self.obj_personListInterface.photos[4]['photo_base64']

        if not str_status.strip():
            latest_error_message = "Status can not be empty."
            self.obj_personListInterface.label_error.configure(text="Status can not be empty")
            self.obj_personListInterface.entry_selected_status.configure(border_color="red")
            error_count += 1

        if str_status not in ["WhiteList", "BlackList"]:
            latest_error_message = "Please Enter Status   ."

            error_count += 1
            self.obj_personListInterface.label_error.configure(text="Please choose 'WhiteList' or 'BlackList'")
            self.obj_personListInterface.entry_selected_status.configure(border_color="red")
        else:
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_selected_status.configure(border_color="green")

        if str_gender not in ["Male", "Female", "Other"]:
            latest_error_message = "Please Enter  Gender "
            error_count += 1
            self.obj_personListInterface.entry_selected_gender.configure(border_color="red")
        else:
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_selected_gender.configure(border_color="green")

        if len(str_age) == 0:
            latest_error_message = "Please enter a valid age."
            error_count += 1
            self.obj_personListInterface.label_error.configure(text="Please enter a valid age.")
            self.obj_personListInterface.entry_age.configure(border_color="red")
        elif not str_age.isdigit():  # Ensure the input is a numbe
            latest_error_message = "Age must be a number."
            error_count += 1
            self.obj_personListInterface.label_error.configure(text="Age must be a number.")
            self.obj_personListInterface.entry_age.configure(border_color="red")
        else:
            # Convert age to an integer and check if it's within the valid range (0 to 120)
            age = int(str_age)
            if age < 15 or age > 120:
                latest_error_message = "Age must be between 0 and 120."
                error_count += 1
                self.obj_personListInterface.label_error.configure(text="Age must be between 15 and 120.")
                self.obj_personListInterface.entry_age.configure(border_color="red")
            else:
                # If all checks pass, clear the error and set the border color to green
                self.obj_personListInterface.label_error.configure(text="")
                self.obj_personListInterface.entry_age.configure(border_color="green")

        if not (2 <= len(str_last_name) <= 20):
            latest_error_message = "Last name length should be between 2 and 20 characters"
            self.obj_personListInterface.label_error.configure(
                text="Last name length should be between 2 and 20 characters")
            self.obj_personListInterface.entry_last_name.configure(border_color="red")

        # If the name length is correct, check if it contains only alphabets
        if str_last_name.isalpha():
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_last_name.configure(border_color="green")

        else:
            latest_error_message = "Last name should only contain alphabets!"
            self.obj_personListInterface.label_error.configure(text="Last name should only contain alphabets!")
            self.obj_personListInterface.entry_last_name.configure(border_color="red")

        if not (2 <= len(str_last_name) <= 20):
            error_count += 1
            latest_error_message = "Last name length should be between 2 and 20 characters"
            self.obj_personListInterface.label_error.configure(
                text="Last name length should be between 2 and 20 characters")
            self.obj_personListInterface.entry_last_name.configure(border_color="red")

        if len(str_middle_name) == 0:
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_middle_name.configure(border_color="green")

        # Check if middle name contains only alphabetic characters
        elif not str_middle_name.isalpha():
            latest_error_message = "Middle name should only contain alphabets!"
            error_count += 1
            self.obj_personListInterface.label_error.configure(text="Middle name should only contain alphabets!")
            self.obj_personListInterface.entry_middle_name.configure(border_color="red")

        # Check if middle name length is between 1 and 3 characters
        elif len(str_middle_name) < 1 or len(str_middle_name) > 10:
            latest_error_message = "Middle name should be between 1 and 3 characters!."
            error_count += 1
            self.obj_personListInterface.label_error.configure(text="Middle name should be between 1 and 3 characters!")
            self.obj_personListInterface.entry_middle_name.configure(border_color="red")


        else:
            # If it passes all checks, it's valid
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_middle_name.configure(border_color="green")

        if not (2 <= len(str_first_name) <= 20):
            latest_error_message = "First name length should be between 2 and 20 characters."
            error_count += 1
            self.obj_personListInterface.label_error.configure(
                text="First name length should be between 2 and 20 characters")
            self.obj_personListInterface.entry_first_name.configure(border_color="red")

        # If the name length is correct, check if it contains only alphabets
        if str_first_name.isalpha():
            self.obj_personListInterface.label_error.configure(text="")
            self.obj_personListInterface.entry_first_name.configure(border_color="green")

        else:
            error_count += 1
            latest_error_message = "First name should only contain alphabets!."
            self.obj_personListInterface.label_error.configure(text="First name should only contain alphabets!")
            self.obj_personListInterface.entry_first_name.configure(border_color="red")

        # if error_count > 0 and latest_error_message:
        #     print("Latest error message:", latest_error_message)
        #     # Optionally display the message on a label or a dialog
        #     self.obj_personListInterface.label_error.configure(text=latest_error_message)

        id = self.obj_core.obj_person.highest_id() + 1
        print("---------------------------------------------------------------rgdkdhult---------------------------",id)
        paths = [photo["image"] for photo in self.obj_personListInterface.photos]


        # if len(self.obj_personListInterface.photos) > 0:
        #     encoded_photo = paths[0]
        if len(self.obj_personListInterface.photos) < 5:
            error_count = +1
            latest_error_message = "Please provide 5 faces ."
        else:
            mean_encode,face_num= self.find_mean_of_images_base64(pic1,pic2,pic3,pic4,pic5)
            if face_num==1:
                error_count=+1
                latest_error_message = " More than one person face is visible."

            elif face_num==2:
                error_count=+1
                latest_error_message = " Invalid Image ."
            elif face_num==3:
                error_count=+1
                latest_error_message = " No face detected."

            else:

                if not self.validate_faces(paths,0.6):
                    error_count = +1
                    latest_error_message = "Images are not belongs to same person."

                else:
                    name, val, tempid= perform_recognition_for_validation(mean_encode)

                    if val:
                        error_count = +1
                        latest_error_message = f"Person already present  with name: {name}."


        if error_count > 0 and latest_error_message:
            print("Latest error message:", latest_error_message)
            # Optionally display the message on a label or a dialog
            self.obj_personListInterface.label_error.configure(text=latest_error_message)



        # Add the person/person to the database
        if (error_count == 0):
            dict_status = self.obj_core.obj_person.add_person(id,
                                                              str_first_name, str_middle_name, str_last_name, str_age,
                                                              str_gender, str_status, pic1, pic2, pic3, pic4, pic5, mean_encode
                                                              )

            # Handle errors or success messages
            if dict_status["str_error_msg_heading"] == "Error! Duplicate Entries":
                # If duplicate person is found, show a popup
                self.obj_Interface.on_error(
                    "home",
                    "Error! Duplicate Entries",
                    f"A person with the Name '{str_first_name + " " + str_middle_name + " " + str_last_name}' already present.",
                    "#FF4B4B"
                )

            # User clicked "No" - Show error popup
            elif dict_status["str_error_msg_heading"] == "Success":
                # If no errors, show success message
                self.obj_Interface.on_error(
                    "home",
                    "Data Added Successfully",
                    "",
                    "#63CA6D",  # Green for success
                    50
                )
                full_name = str_first_name + " " + str_middle_name + " " + str_last_name
                add_person_mean(id,full_name,mean_encode)

                self.onclick_Add_cancel()
                self.obj_personListInterface.i_total_data += 1
                bool_update_data = (((self.obj_personListInterface.dict_filter_criteria["gender"] == "%") and
                                     (self.obj_personListInterface.dict_filter_criteria["status"] == "%") or
                                     ((self.obj_personListInterface.dict_filter_criteria["gender"] == str_gender) or
                                      (self.obj_personListInterface.dict_filter_criteria["status"] == str_status)
                                      )))
                str_full_name = str_first_name + " " + str_middle_name + " " + str_last_name
                # self.obj_FaceProcessor.add_person(id,str_full_name.upper(),encoded_photo)
                if (bool_update_data):
                    self.obj_personListInterface.i_total_data = len(self.obj_personListInterface.person_data) + 1

                    self.obj_personListInterface.person_data.append({

                        "full_name": str_full_name.upper(),
                        "age": str_age,
                        "gender": str_gender,
                        "status": str_status,
                        "photo_path": pic1,
                        "photo_path2": pic2,
                        "photo_path3": pic3,
                        "photo_path4": pic4,
                        "photo_path5": pic5,

                        "id": id,
                    })

                if (self.obj_personListInterface.dict_filter_criteria["full_name"] != ""):
                    self.obj_personListInterface.dict_filter_criteria["full_name"] = ""
                    self.obj_personListInterface.entry_search.delete(0, "end")
                    self.obj_personListInterface.entry_search.configure(placeholder_text="Enter Name..")
                    self.obj_Interface.obj_RootInterface.focus_set()

                    if (not bool_update_data):
                        self.obj_personListInterface.i_total_data = len(self.obj_personListInterface.person_data)

                    self.obj_Interface.dict_frames["person_list"].i_start_index = 1
                    self.obj_Interface.dict_frames[
                        "person_list"].i_end_index = 5 if self.obj_personListInterface.i_total_data >= 5 else self.obj_personListInterface.i_total_data
                else:
                    # if (bool_update_data):
                    #     if (((self.obj_PersonListInterface.i_end_index - self.obj_PersonListInterface.i_start_index) + 1) < 5):
                    #         self.obj_PersonListInterface.i_end_index += 1
                    if (bool_update_data):
                        i_data_count = 5 if (
                                self.obj_personListInterface.i_total_data % 5 == 0) else self.obj_personListInterface.i_total_data % 5
                        self.obj_personListInterface.i_end_index = self.obj_personListInterface.i_total_data
                        self.obj_personListInterface.i_start_index = (
                                                                             self.obj_personListInterface.i_end_index - i_data_count) + 1

                data = (self.obj_Interface.dict_frames["person_list"].person_data)[

                       ((self.obj_personListInterface.i_start_index) - 1):(self.obj_personListInterface.i_end_index)]
                self.obj_personListInterface.update_table(data)

                # self.obj_personListInterface.person_data = self.obj_core.obj_person.fetch_person_details(
                #     self.obj_personListInterface.dict_filter_criteria)

                # self.obj_personListInterface.update_table(self.obj_Interface.dict_frames["person_list"].person_data)

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
            f"Are you sure you want to delete {len(self.obj_personListInterface.selected_face_set), self.obj_personListInterface.selected_face_set} Selected Persion ? ",
            icon='warning'
        )

        if confirm_delete:

            if self.obj_core.obj_person.delete_person(list(self.obj_personListInterface.selected_face_set)):

                self.obj_Interface.on_error(
                    "home",
                    "Data Deleted Successfully",
                    "",
                    "#63CA6D",
                    50
                )
                for id in self.obj_personListInterface.selected_id:
                    delete_person(id)
                self.obj_personListInterface.selected_id.clear()
                self.obj_personListInterface.i_total_data = self.obj_personListInterface.i_total_data - len(
                    self.obj_personListInterface.selected_face_set)
                self.obj_personListInterface.selected_face_set.clear()
                self.obj_personListInterface.selected_rows.clear()

                self.obj_personListInterface.person_data.clear()
                self.obj_personListInterface.person_data = self.obj_core.obj_person.fetch_person_details(
                    self.obj_personListInterface.dict_filter_criteria)

                if (self.obj_personListInterface.dict_filter_criteria["full_name"] != ""):
                    self.obj_personListInterface.i_total_data = len(self.obj_personListInterface.person_data)
                    self.obj_personListInterface.dict_filter_criteria["full_name"] = ""
                    self.obj_personListInterface.entry_search.delete(0, "end")
                    self.obj_personListInterface.entry_search.configure(placeholder_text="Enter Full Name..")
                    self.obj_Interface.obj_RootInterface.focus_set()

                self.obj_personListInterface.i_total_data = self.obj_personListInterface.i_total_data - len(
                    self.obj_personListInterface.selected_face_set)

                self.obj_personListInterface.person_data = self.obj_core.obj_person.fetch_person_details(
                    self.obj_personListInterface.dict_filter_criteria)


                data = []
                while (True):
                    if (len(self.obj_personListInterface.person_data) == 0):
                        self.obj_personListInterface.i_start_index = 0
                        self.obj_personListInterface.i_end_index = 0
                        break

                    data = (self.obj_personListInterface.person_data)[
                           ((self.obj_personListInterface.i_start_index) - 1):(
                                   (self.obj_personListInterface.i_start_index) + 4)]

                    if (len(data) > 0):
                        self.obj_personListInterface.i_end_index = (self.obj_personListInterface.i_start_index + len(
                            data)) - 1
                        break
                    else:
                        self.obj_personListInterface.i_start_index -= 5
                        self.obj_personListInterface.i_end_index -= 5

                self.obj_personListInterface.update_table(data)

                self.obj_personListInterface.reset_checkbox()

            else:
                self.obj_Interface.on_error(
                    "home",
                    "Error! Invalid Data",
                    "Check if the entered data fulfill the required conditions.",
                    "#FF4B4B"

                )

    def imageList_base64_compare(self,Stored_old_photos, current_photos):
        for i in range(0,5):
            if Stored_old_photos[i] != current_photos[i]['photo_base64']:
                return True

        return False


    def onclick_edit(self):
        self.obj_personListInterface.edit_selected_person()

    def onclick_edit_prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index = self.current_image_index - 1
            currentphoto = self.obj_personListInterface.Edit_photos[self.current_image_index]["ctk_image"]
            self.obj_personListInterface.Edit_img_label.configure(image=currentphoto)

    def onclick_edit_next_image(self):
        if self.current_image_index < self.obj_personListInterface.photolength - 1:
            self.current_image_index = self.current_image_index + 1
            currentphoto = self.obj_personListInterface.Edit_photos[self.current_image_index]["ctk_image"]
            self.obj_personListInterface.Edit_img_label.configure(image=currentphoto)

    def onclick_edit_save(self):
        global pkl_file_update_status
        str_path = self.obj_personListInterface.photo_path
        str_first_name = self.obj_personListInterface.Edit_entry_first_name.get().strip()
        str_middle_name = self.obj_personListInterface.Edit_entry_middle_name.get().strip()

        str_last_name = self.obj_personListInterface.Edit_entry_last_name.get().strip()
        str_age = self.obj_personListInterface.Edit_entry_age.get().strip()
        str_gender = self.obj_personListInterface.Edit_entry_selected_gender.get().strip()
        str_status = self.obj_personListInterface.Edit_entry_selected_status.get().strip()
        if not hasattr(self.obj_personListInterface, 'person'):
            str_id = self.TEMP_ID
        else:
            str_id = self.obj_personListInterface.person.get("id", 'N/A')

        ans = name = prevID = ''

        matching = 0
        error_count = 0

        if str_path:  # Only encode if the path is not empty
            try:
                with open(str_path, "rb") as photo_file:
                    # Read the photo file as binary
                    photo_binary = photo_file.read()
                    # Convert the binary data to base64
                    encoded_photo = base64.b64encode(photo_binary).decode("utf-8")

                    # ans, name, prevID = check_image_encode(self.obj_FaceProcessor.known_face_names,
                    #                                        self.obj_FaceProcessor.known_face_encodings, encoded_photo)
                    # if ans == "matched":
                    #     self.obj_Interface.on_error(
                    #         "home",
                    #         "Error! Duplicate Entries",
                    #         f"A person with this image already present with name : {name}.",
                    #         "#FF4B4B"
                    #     )
                    #     self.onclick_Add_cancel()
                    #     return

            except Exception as e:
                # Handle errors (file not found, etc.)
                print(f"Error encoding photo: {e}")
                encoded_photo = None
        else:
            encoded_photo = None

        if (str_path == None):
            matching += 1
            str_path = self.obj_personListInterface.old_photo
            encoded_photo = str_path

        full_name = str_first_name + " " + str_middle_name + " " + str_last_name
        photo_keys = [
            self.obj_personListInterface.person.get('photo_path', ""),
            self.obj_personListInterface.person.get('photo_path2', ""),
            self.obj_personListInterface.person.get('photo_path3', ""),
            self.obj_personListInterface.person.get('photo_path4', ""),
            self.obj_personListInterface.person.get('photo_path5', "")
        ]
        print(len(self.obj_personListInterface.Edit_photos),"------------------")
        if len(self.obj_personListInterface.Edit_photos)<5:
            latest_error_message = "Status can not be empty."

        paths = [photo["image"] for photo in self.obj_personListInterface.Edit_photos]
        if self.obj_personListInterface.Edit_photos:
            pic1 = self.obj_personListInterface.Edit_photos[0]['photo_base64']
            pic2 = self.obj_personListInterface.Edit_photos[1]['photo_base64']
            pic3 = self.obj_personListInterface.Edit_photos[2]['photo_base64']
            pic4 = self.obj_personListInterface.Edit_photos[3]['photo_base64']
            pic5 = self.obj_personListInterface.Edit_photos[4]['photo_base64']

        if (self.obj_personListInterface.person['full_name'] == full_name):
            matching += 1

        if (int(self.obj_personListInterface.person['age']) == int(str_age)):
            matching += 1

        if (self.obj_personListInterface.person['gender'] == str_gender):
            matching += 1

        if (self.obj_personListInterface.person['status'] == str_status):
            matching += 1

        self.image_changed = self.imageList_base64_compare(photo_keys,self.obj_personListInterface.Edit_photos)
        if matching == 5 and self.image_changed == False:
            print("data already preset")
            self.obj_personListInterface.Edit_label_error.configure(text="Data is already present")

        if not str_status.strip():
            latest_error_message = "Status can not be empty."
            self.obj_personListInterface.Edit_label_error.configure(text="Status can not be empty")
            self.obj_personListInterface.Edit_entry_selected_status.configure(border_color="red")
            error_count += 1

        # Check for valid vehicle type
        if str_status not in ["WhiteList", "BlackList"]:
            latest_error_message = "Please Enter Status ."

            error_count += 1
            self.obj_personListInterface.Edit_label_error.configure(text="Please choose 'WhiteList' or 'BlackList'")
            self.obj_personListInterface.Edit_entry_selected_status.configure(border_color="red")
        else:
            self.obj_personListInterface.Edit_label_error.configure(text="")
            self.obj_personListInterface.Edit_entry_selected_status.configure(border_color="green")

        if str_gender not in ["Male", "Female", "Other"]:
            latest_error_message = "Please Enter  Gender "
            error_count += 1
            self.obj_personListInterface.Edit_entry_selected_gender.configure(border_color="red")
        else:
            self.obj_personListInterface.Edit_label_error.configure(text="")
            self.obj_personListInterface.Edit_entry_selected_gender.configure(border_color="green")

        if len(str_age) == 0:
            latest_error_message = "Please enter a valid age."
            error_count += 1
            self.obj_personListInterface.Edit_label_error.configure(text="Please enter a valid age.")
            self.obj_personListInterface.Edit_entry_age.configure(border_color="red")
        elif not str_age.isdigit():  # Ensure the input is a numbe
            latest_error_message = "Age must be a number."
            error_count += 1
            self.obj_personListInterface.Edit_label_error.configure(text="Age must be a number.")
            self.obj_personListInterface.Edit_entry_age.configure(border_color="red")
        else:
            # Convert age to an integer and check if it's within the valid range (0 to 120)
            age = int(str_age)
            if age < 15 or age > 120:
                latest_error_message = "Age must be between 0 and 120."
                error_count += 1
                self.obj_personListInterface.Edit_label_error.configure(text="Age must be between 15 and 120.")
                self.obj_personListInterface.Edit_entry_age.configure(border_color="red")
            else:
                # If all checks pass, clear the error and set the border color to green
                self.obj_personListInterface.Edit_label_error.configure(text="")
                self.obj_personListInterface.Edit_entry_age.configure(border_color="green")

        if not (2 <= len(str_last_name) <= 20):
            latest_error_message = "Last name length should be between 2 and 20 characters"
            self.obj_personListInterface.Edit_label_error.configure(
                text="Last name length should be between 2 and 20 characters")
            self.obj_personListInterface.Edit_entry_last_name.configure(border_color="red")

        # If the name length is correct, check if it contains only alphabets
        if str_last_name.isalpha():
            self.obj_personListInterface.Edit_label_error.configure(text="")
            self.obj_personListInterface.Edit_entry_last_name.configure(border_color="green")

        else:
            error_count += 1
            latest_error_message = "Last name should only contain alphabets!"
            self.obj_personListInterface.Edit_label_error.configure(text="Last name should only contain alphabets!")
            self.obj_personListInterface.Edit_entry_last_name.configure(border_color="red")

        if not (2 <= len(str_last_name) <= 20):
            error_count += 1
            latest_error_message = "Last name length should be between 2 and 20 characters"
            self.obj_personListInterface.Edit_label_error.configure(
                text="Last name length should be between 2 and 20 characters")
            self.obj_personListInterface.Edit_entry_last_name.configure(border_color="red")

        if len(str_middle_name) == 0:
            self.obj_personListInterface.Edit_label_error.configure(text="")
            self.obj_personListInterface.Edit_entry_middle_name.configure(border_color="green")

        # Check if middle name contains only alphabetic characters
        elif not str_middle_name.isalpha():
            latest_error_message = "Middle name should only contain alphabets!"
            error_count += 1
            self.obj_personListInterface.Edit_label_error.configure(text="Middle name should only contain alphabets!")
            self.obj_personListInterface.Edit_entry_middle_name.configure(border_color="red")

        # Check if middle name length is between 1 and 3 characters
        elif len(str_middle_name) < 1 or len(str_middle_name) > 10:
            latest_error_message = "Middle name should be between 1 and 3 characters!."
            error_count += 1
            self.obj_personListInterface.Edit_label_error.configure(
                text="Middle name should be between 1 and 3 characters!")
            self.obj_personListInterface.Edit_entry_middle_name.configure(border_color="red")


        else:
            # If it passes all checks, it's valid
            self.obj_personListInterface.Edit_label_error.configure(text="")
            self.obj_personListInterface.Edit_entry_middle_name.configure(border_color="green")

        if not (2 <= len(str_first_name) <= 20):
            latest_error_message = "First name length should be between 2 and 20 characters."
            error_count += 1
            self.obj_personListInterface.Edit_label_error.configure(
                text="First name length should be between 2 and 20 characters")
            self.obj_personListInterface.Edit_entry_first_name.configure(border_color="red")

        # If the name length is correct, check if it contains only alphabets
        if str_first_name.isalpha():
            self.obj_personListInterface.Edit_label_error.configure(text="")
            self.obj_personListInterface.Edit_entry_first_name.configure(border_color="green")

        else:
            error_count += 1
            latest_error_message = "First name should only contain alphabets!."
            self.obj_personListInterface.Edit_label_error.configure(text="First name should only contain alphabets!")
            self.obj_personListInterface.Edit_entry_first_name.configure(border_color="red")

        if error_count > 0 and latest_error_message:
            print("Latest error message:", latest_error_message)
            # Optionally display the message on a label or a dialog
            self.obj_personListInterface.Edit_label_error.configure(text=latest_error_message)

        if matching == 5 and self.image_changed == False:
            # Data already present
            self.obj_personListInterface.Edit_label_error.configure(text="Data is already present")

        elif error_count == 0:

            mean_image,face_num= self.find_mean_of_images_base64(pic1,pic2,pic3,pic4,pic5)
            if face_num == 1:
                error_count = +1
                latest_error_message = " More than one person face is visible."

            elif face_num == 2:
                error_count = +1
                latest_error_message = " Invalid Image ."
            elif face_num == 3:
                error_count = +1
                latest_error_message = " No face detected."
            else:

                if not self.validate_faces(paths, 0.6):
                    error_count = +1
                    latest_error_message = "Images are not belongs to same person."

                else:
                    name, val, id = perform_recognition_for_validation(mean_image)

                    if val and str_id != id:
                        error_count = +1
                        latest_error_message = f"Person already present  with name: {name}."

            if error_count > 0 and latest_error_message:
                print("Latest error message:", latest_error_message)
                # Optionally display the message on a label or a dialog
                self.obj_personListInterface.Edit_label_error.configure(text=latest_error_message)
                self.obj_Interface.on_error(
                    "home",
                    "Invalid Image",
                    latest_error_message,
                    "#FF4B4B"
                )

            # Add the person/person to the database
            if (error_count == 0):
                dict_status = self.obj_core.obj_person.update_person(
                    full_name, str_age, str_gender, str_status, pic1, pic2, pic3, pic4, pic5, str_id=str_id, added_by="Anu",mean_image= mean_image)

                # Check if the update was successful
                if dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == "":
                    self.obj_Interface.switch_frames('person_list')

                    # Display success message
                    self.obj_Interface.on_error(
                        "home",
                        "Data Edited Successfully",
                        "",
                        "#63CA6D",
                        50
                    )

                    update_person_mean(str_id,full_name,mean_image)

                    self.obj_personListInterface.destroy_registration_form()
                    # self.obj_FaceProcessor.update_person(str_id,full_name.upper(),name)
                    self.obj_personListInterface.selected_id.clear()
                    self.obj_personListInterface.selected_face_set.clear()
                    self.obj_personListInterface.selected_rows.clear()
                    self.obj_personListInterface.update_button_states()

                    data = []
                    start_pos = (self.obj_personListInterface.i_start_index) - 1
                    end_pos = self.obj_personListInterface.i_end_index
                    print(self.obj_personListInterface.dict_filter_criteria["full_name"],
                          "___________________________dict critera")
                    temp_name = self.obj_personListInterface.entry_search.get()
                    self.obj_personListInterface.dict_filter_criteria["full_name"] = temp_name.upper()
                    if (self.obj_personListInterface.dict_filter_criteria["full_name"] == ""):
                        print("entered inside serach filed ", "_-------------------------")
                        for i in range(start_pos, end_pos):
                            print(self.obj_personListInterface.person_data[i]["id"],
                                  "__________________________________self.obj_personListInterface.person_data")
                            if (self.obj_personListInterface.person_data[i]["id"] == str_id):
                                self.obj_personListInterface.person_data[i]["full_name"] = full_name.upper()
                                self.obj_personListInterface.person_data[i]["age"] = str_age
                                self.obj_personListInterface.person_data[i]["gender"] = str_gender
                                self.obj_personListInterface.person_data[i]["status"] = str_status
                                self.obj_personListInterface.person_data[i]["photo_path"] = pic1
                                self.obj_personListInterface.person_data[i]["photo_path2"] = pic2
                                self.obj_personListInterface.person_data[i]["photo_path3"] = pic3
                                self.obj_personListInterface.person_data[i]["photo_path4"] = pic4
                                self.obj_personListInterface.person_data[i]["photo_path5"] = pic5
                                break
                        data = self.obj_core.obj_person.search_person_number(
                            self.obj_personListInterface.person_data,
                            self.obj_personListInterface.dict_filter_criteria["full_name"])

                        self.obj_personListInterface.update_table(
                            (self.obj_personListInterface.person_data)[start_pos:end_pos])

                    else:
                        for i in range(0, len(self.obj_personListInterface.person_data)):
                            if (self.obj_personListInterface.person_data[i]["id"] == str_id):
                                self.obj_personListInterface.person_data[i]["full_name"] = full_name.upper()
                                self.obj_personListInterface.person_data[i]["age"] = str_age
                                self.obj_personListInterface.person_data[i]["gender"] = str_gender
                                self.obj_personListInterface.person_data[i]["status"] = str_status
                                self.obj_personListInterface.person_data[i]["photo_path"] = pic1
                                self.obj_personListInterface.person_data[i]["photo_path2"] = pic2
                                self.obj_personListInterface.person_data[i]["photo_path3"] = pic3
                                self.obj_personListInterface.person_data[i]["photo_path4"] = pic4
                                self.obj_personListInterface.person_data[i]["photo_path5"] = pic5
                                break
                        data = self.obj_core.obj_person.search_person_number(
                            self.obj_personListInterface.person_data,
                            self.obj_personListInterface.dict_filter_criteria["full_name"])
                        self.obj_personListInterface.update_table(data[start_pos:end_pos])

                else:
                    # Display error message if update failed
                    self.obj_Interface.on_error(
                        "home",
                        dict_status["str_error_msg_heading"],
                        dict_status["str_error_msg"],
                        "#FF4B4B"
                    )

