import base64
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
        self.obj_homeController = HomeController(Core,Interface)

        self.bind_buttons()

        self.obj_VehicleListInterface.entry_search.bind("<KeyRelease>", self.search_vehicle)
        self.obj_VehicleListInterface.entry_selected_owner.bind("<KeyRelease>", self.search_owner)

        self.obj_VehicleListInterface.entry_selected_type.bind("<KeyRelease>", self.search_type)
        # self.obj_VehicleListInterface.entry_selected_color.bind("<KeyRelease>", self.search_color)
        self.obj_VehicleListInterface.entry_selected_owner.bind("<Button-1>",self.obj_VehicleListInterface.close_filter_dropdown)
        self.obj_VehicleListInterface.entry_selected_type.bind("<Button-1>", self.obj_VehicleListInterface.close_filter_dropdown)
        # self.obj_VehicleListInterface.entry_selected_color.bind("<Button-1>", self.obj_VehicleListInterface.close_filter_dropdown)

        self.obj_VehicleListInterface.on_form_add_ready = self.bind_add_popup_buttons
        self.obj_VehicleListInterface.on_form_edit_ready = self.bind_edit_popup_buttons
        
    def bind_buttons(self):
        self.obj_VehicleListInterface.button_filter.configure(command=self.filter_popup)
        self.obj_VehicleListInterface.button_select_owner.configure(command=self.popup_owner_dropdown)
        self.obj_VehicleListInterface.button_select_type.configure(command=self.popup_type_dropdown)
        # self.obj_VehicleListInterface.button_select_color.configure(command=self.popup_color_dropdown)
        self.obj_VehicleListInterface.button_ok.configure(command=self.onclick_ok)
        self.obj_VehicleListInterface.button_cancel.configure(command=self.onclick_cancel)

        self.obj_VehicleListInterface.button_next.configure(command = self.onclick_next)
        self.obj_VehicleListInterface.button_previous.configure(command = self.onclick_previous)

        self.obj_VehicleListInterface.button_Add.configure(command=self.onclick_add)

        self.obj_VehicleListInterface.button_Edit.configure(command=self.onclick_edit)
        self.obj_VehicleListInterface.button_Delete_selected.configure(command=self.onclick_delete)

        for key, value in self.obj_VehicleListInterface.dict_columns_buttons.items():
            value[0].configure(command=lambda k=key: self.onclick_column_headings(k))

    def bind_add_popup_buttons(self):
       
        self.obj_VehicleListInterface.button_add_save.configure(command=self.onclick_add_save)
        self.obj_VehicleListInterface.button_cancel.configure(command=self.onclick_Add_cancel)
        self.obj_VehicleListInterface.entry_first_name.bind("<KeyRelease>", self.validate_first_name)
        self.obj_VehicleListInterface.entry_middle_name.bind("<KeyRelease>", self.validate_middle_name)
        self.obj_VehicleListInterface.entry_last_name.bind("<KeyRelease>", self.validate_last_name)
        self.obj_VehicleListInterface.entry_age.bind("<KeyRelease>", self.validate_age)
        # self.obj_VehicleListInterface.entry_date.bind("<KeyRelease>", self.validate_manufacturing_year)
        # self.obj_VehicleListInterface.entry_selected_company.bind("<KeyRelease>", self.validate_)

        
        # self.obj_VehicleListInterface.entry_selected_status.bind("<KeyRelease>", 
        #                            lambda e: self.obj_VehicleListInterface.button_select_gender)
       
        # self.obj_VehicleListInterface.entry_selected_status.bind("<KeyRelease>", 
        #                            lambda e: self.search_Add_type_new(self.obj_VehicleListInterface.entry_selected_status,4,3, self.obj_VehicleListInterface,self.obj_VehicleListInterface.frame_form_rcol,0
        #                                                                                       ))
        # self.obj_VehicleListInterface.entry_selected_company.bind("<KeyRelease>", 
        #                             lambda e: self.search_Add_type_new(self.obj_VehicleListInterface.entry_selected_company,4,3, self.obj_VehicleListInterface,self.obj_VehicleListInterface.frame_form_lcol,1
          
        #                                                                                     ))
    
    
    def search_Add_type_new(self, entryfield,row=0,rowspan=2,interface_obj=None,parent=None,fun=0,event= None):
        pass
        
        # self.list_gender = ["Male", "Female", "Other"]
        # self.list_status = ["WhiteList", "BlackList"]

        # text_entered = entryfield.get().lstrip(" ")
        # text_entered = text_entered
        # dict_status=[]
        # if fun==0:
        #     dict_status = self.obj_core.obj_Vehicle.search_vehicle_type(text_entered)
        #     if len(dict_status)==1 and dict_status[0]==text_entered and dict_status[0]!='All':
        #         entryfield.configure(border_color="green")
        #         self.obj_VehicleListInterface.label_error.configure(text="")
        #     else:
        #         self.obj_VehicleListInterface.label_error.configure(text="Vehcile Type should be selected from the dropdown")
        #         entryfield.configure(border_color="red")

            
            

        # elif fun ==1:
        #      dict_status = self.obj_core.obj_Vehicle.search_vehicle_company(text_entered)
        #      if len(dict_status)==1 and dict_status[0]==text_entered and dict_status[0]!='All':
        #         self.obj_VehicleListInterface.label_error.configure(text="")
        #         entryfield.configure(border_color="green")
        #      else:
        #         self.obj_VehicleListInterface.label_error.configure(text="Selected from the dropdown")
        #         entryfield.configure(border_color="red")

            

        # interface_obj.popup_Add_dropdown(parent,dict_status, entry_destination = entryfield, i_row = row, i_rowspan=rowspan,type=0)

      

#----------------------------------------------------------[validation add page]-------------------------------------------------------------------------------------

    

    def validate_first_name(self, event=None) -> bool:
        first_name = self.obj_VehicleListInterface.entry_first_name.get().strip()

        # Check if the first name length is between 2 and 20 (you can adjust this range)
        if not (2 <= len(first_name) <= 20):
            self.obj_VehicleListInterface.label_error.configure(text="First name length should be between 2 and 20 characters")
            self.obj_VehicleListInterface.entry_first_name.configure(border_color="red")
            return False  # Exit the function if the length is incorrect

        # If the name length is correct, check if it contains only alphabets
        if  first_name.isalpha():
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_first_name.configure(border_color="green")
            return True  # Valid first name
        else:
            self.obj_VehicleListInterface.label_error.configure(text="First name should only contain alphabets!")
            self.obj_VehicleListInterface.entry_first_name.configure(border_color="red")
            return False  # Invalid first name
        
    def validate_middle_name(self, event=None):
        middle_name = self.obj_VehicleListInterface.entry_middle_name.get().strip()
        # Check if middle name is empty
        if len(middle_name) == 0:
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_middle_name.configure(border_color="green")
            return True  # Empty middle name is valid
        
        # Check if middle name contains only alphabetic characters
        elif not middle_name.isalpha():
            self.obj_VehicleListInterface.label_error.configure(text="Middle name should only contain alphabets!")
            self.obj_VehicleListInterface.entry_middle_name.configure(border_color="red")
            return False  # Invalid if it contains non-alphabetic characters
        
        # Check if middle name length is between 1 and 3 characters
        elif len(middle_name) < 1 or len(middle_name) > 10:
            self.obj_VehicleListInterface.label_error.configure(text="Middle name should be between 1 and 3 characters!")
            self.obj_VehicleListInterface.entry_middle_name.configure(border_color="red")
            return False  # Invalid if length is not between 1 and 3
        
        else:
            # If it passes all checks, it's valid
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_middle_name.configure(border_color="green")
            return True
    def validate_last_name(self, event=None) -> bool:
        last_name = self.obj_VehicleListInterface.entry_last_name.get().strip()

        # Check if the first name length is between 2 and 20 (you can adjust this range)
        if not (2 <= len(last_name) <= 20):
            self.obj_VehicleListInterface.label_error.configure(text="Last name length should be between 2 and 20 characters")
            self.obj_VehicleListInterface.entry_last_name.configure(border_color="red")
            return False  # Exit the function if the length is incorrect

        # If the name length is correct, check if it contains only alphabets
        if last_name.isalpha():
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_last_name.configure(border_color="green")
            return True  # Valid first name
        else:
            self.obj_VehicleListInterface.label_error.configure(text="Last name should only contain alphabets!")
            self.obj_VehicleListInterface.entry_last_name.configure(border_color="red")
            return False  # Invalid first name

    

    def validate_age(self, event=None):
        age = self.obj_VehicleListInterface.entry_age.get().strip()

        # Check if the age field is empty
        if len(age) == 0:
            self.obj_VehicleListInterface.label_error.configure(text="Please Enter Age")
            self.obj_VehicleListInterface.entry_age.configure(border_color="red")
            return False

        # Check if the age is a valid number
        if not age.isdigit():  # Ensures the input consists only of digits
            self.obj_VehicleListInterface.label_error.configure(text="Age must be a number")
            self.obj_VehicleListInterface.entry_age.configure(border_color="red")
            return False

        # Convert the age to an integer
        age = int(age)

        # Check if the age is within the valid range (e.g., between 0 and 120)
        if age < 0 or age > 120:
            self.obj_VehicleListInterface.label_error.configure(text="Age must be between 0 and 120")
            self.obj_VehicleListInterface.entry_age.configure(border_color="red")
            return False

        # If all checks pass, set the border color to green and clear any error
        self.obj_VehicleListInterface.label_error.configure(text="")
        self.obj_VehicleListInterface.entry_age.configure(border_color="green")
        return True
        
    

#----------------------------------------------------------[validiation add ends]----------------------------------------------------------------------------------------------------
            
    
    def bind_edit_popup_buttons(self):
        #  self.obj_VehicleListInterface.entry_edit_selected_status.bind("<KeyRelease>", self.search_edit_status)
         self.obj_VehicleListInterface.Edit_button_add_save.configure(command=self.onclick_edit_save)
         self.obj_VehicleListInterface.Edit_entry_first_name.bind("<KeyRelease>", self.validate_Edit_first_name)
         self.obj_VehicleListInterface.Edit_entry_last_name.bind("<KeyRelease>", self.validate_Edit_last_name)
         self.obj_VehicleListInterface.Edit_entry_middle_name.bind("<KeyRelease>", self.validate_Edit_middle_name)
         self.obj_VehicleListInterface.Edit_entry_age.bind("<KeyRelease>", self.validate_Edit_age)
       
        #  self.obj_VehicleListInterface.entry_edit_type.bind("<KeyRelease>", 
        #                            lambda e: self.search_Edit_type_new(self.obj_VehicleListInterface.entry_edit_type,4,3, self.obj_VehicleListInterface,self.obj_VehicleListInterface.frame_form_rcol,0
        #                                                                                       ))
        #  self.obj_VehicleListInterface.entry_edit_selected_company.bind("<KeyRelease>", 
        #                            lambda e: self.search_Edit_type_new(self.obj_VehicleListInterface.entry_edit_selected_company,4,3, self.obj_VehicleListInterface,self.obj_VehicleListInterface.frame_form_lcol,1
                                                                                            #   ))
   
    def validate_Edit_first_name(self, event=None) -> bool:
        first_name = self.obj_VehicleListInterface.Edit_entry_first_name.get().strip()

        # Check if the first name length is between 2 and 20 (you can adjust this range)
        if not (2 <= len(first_name) <= 20):
            self.obj_VehicleListInterface.Edit_label_error.configure(text="First name length should be between 2 and 20 characters")
            self.obj_VehicleListInterface.Edit_entry_first_name.configure(border_color="red")
            return False  # Exit the function if the length is incorrect

        # If the name length is correct, check if it contains only alphabets
        if  first_name.isalpha():
            self.obj_VehicleListInterface.Edit_label_error.configure(text="")
            self.obj_VehicleListInterface.Edit_entry_first_name.configure(border_color="green")
            return True  # Valid first name
        else:
            self.obj_VehicleListInterface.Edit_label_error.configure(text="First name should only contain alphabets!")
            self.obj_VehicleListInterface.Edit_entry_first_name.configure(border_color="red")
            return False  # Invalid first name
        
    def validate_Edit_middle_name(self, event=None):
        middle_name = self.obj_VehicleListInterface.Edit_entry_middle_name.get().strip()
        # Check if middle name is empty
        if len(middle_name) == 0:
            self.obj_VehicleListInterface.Edit_label_error.configure(text="")
            self.obj_VehicleListInterface.Edit_entry_middle_name.configure(border_color="green")
            return True  # Empty middle name is valid
        
        # Check if middle name contains only alphabetic characters
        elif not middle_name.isalpha():
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Middle name should only contain alphabets!")
            self.obj_VehicleListInterface.Edit_entry_middle_name.configure(border_color="red")
            return False  # Invalid if it contains non-alphabetic characters
        
        # Check if middle name length is between 1 and 3 characters
        elif len(middle_name) < 1 or len(middle_name) > 10:
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Middle name should be between 1 and 3 characters!")
            self.obj_VehicleListInterface.Edit_entry_middle_name.configure(border_color="red")
            return False  # Invalid if length is not between 1 and 3
        
        else:
            # If it passes all checks, it's valid
            self.obj_VehicleListInterface.Edit_label_error.configure(text="")
            self.obj_VehicleListInterface.Edit_entry_middle_name.configure(border_color="green")
            return True
    def validate_Edit_last_name(self, event=None) -> bool:
        last_name = self.obj_VehicleListInterface.Edit_entry_last_name.get().strip()

        # Check if the first name length is between 2 and 20 (you can adjust this range)
        if not (2 <= len(last_name) <= 20):
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Last name length should be between 2 and 20 characters")
            self.obj_VehicleListInterface.Edit_entry_last_name.configure(border_color="red")
            return False  # Exit the function if the length is incorrect

        # If the name length is correct, check if it contains only alphabets
        if last_name.isalpha():
            self.obj_VehicleListInterface.Edit_label_error.configure(text="")
            self.obj_VehicleListInterface.Edit_entry_last_name.configure(border_color="green")
            return True  # Valid first name
        else:
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Last name should only contain alphabets!")
            self.obj_VehicleListInterface.Edit_entry_last_name.configure(border_color="red")
            return False  # Invalid first name

    

    def validate_Edit_age(self, event=None):
        age = self.obj_VehicleListInterface.Edit_entry_age.get().strip()

        # Check if the age field is empty
        if len(age) == 0:
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Enter Age")
            self.obj_VehicleListInterface.Edit_entry_age.configure(border_color="red")
            return False

        # Check if the age is a valid number
        if not age.isdigit():  # Ensures the input consists only of digits
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Age must be a number")
            self.obj_VehicleListInterface.Edit_entry_age.configure(border_color="red")
            return False

        # Convert the age to an integer
        age = int(age)

        # Check if the age is within the valid range (e.g., between 0 and 120)
        if age < 0 or age > 120:
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Age must be between 0 and 120")
            self.obj_VehicleListInterface.Edit_entry_age.configure(border_color="red")
            return False

        # If all checks pass, set the border color to green and clear any error
        self.obj_VehicleListInterface.Edit_label_error.configure(text="")
        self.obj_VehicleListInterface.Edit_entry_age.configure(border_color="green")
        return True
    

#____________________________________________________________[filter search]___________________________________________________________________________________________
        

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

        # list_vehicle_data = self.obj_core.obj_Vehicle.search_vehicle_number(
        #     self.obj_Interface.dict_frames["vehicle_list"].vehicle_data, str_vehicle_number)
        # self.obj_Interface.dict_frames["vehicle_list"].update_table(list_vehicle_data)

        # str_full_name = (self.obj_VehicleListInterface.entry_search.get().lstrip(" ")).upper()
        str_full_name = (self.obj_VehicleListInterface.entry_search.get().lstrip(" "))
        list_searched_data = []
 
        if(str_full_name != ""):
            list_searched_data = self.obj_core.obj_Vehicle.search_vehicle_number(self.obj_VehicleListInterface.vehicle_data, str_full_name)
            self.obj_VehicleListInterface.i_total_data = len(list_searched_data)
        else:
            list_searched_data = self.obj_VehicleListInterface.vehicle_data
            self.obj_VehicleListInterface.i_total_data = len(self.obj_VehicleListInterface.vehicle_data)
 
 
        if(self.obj_VehicleListInterface.i_total_data > 0):
            self.obj_VehicleListInterface.i_start_index = 1
            self.obj_VehicleListInterface.i_end_index = 5 if self.obj_VehicleListInterface.i_total_data >= 5 else self.obj_VehicleListInterface.i_total_data
 
        # self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] = str_vehicle_number
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
            if current_type not in ["Select Status", "All"]:
                # Revert type dropdown to original state
                self.obj_VehicleListInterface.entry_selected_type.delete(0, 'end')
                self.obj_VehicleListInterface.entry_selected_type.insert(0, "Select Status")

            #self.obj_VehicleListInterface.popup_dropdown(None)
            self.obj_VehicleListInterface.bool_type_dropdown_opened = False
        elif (self.obj_VehicleListInterface.bool_color_dropdown_opened):
            # Check if color dropdown has a value selected
            current_color = self.obj_VehicleListInterface.entry_selected_color.get()
            if current_color not in ["Select ", "All"]:
                # Revert color dropdown to original state
                self.obj_VehicleListInterface.entry_selected_color.delete(0, 'end')
                self.obj_VehicleListInterface.entry_selected_color.insert(0, "Select Vehicle Color")

            #self.obj_VehicleListInterface.popup_dropdown(None)
            self.obj_VehicleListInterface.bool_color_dropdown_opened = False

        # Handle owner dropdown
        if (self.obj_VehicleListInterface.bool_owner_dropdown_opened):
            #self.obj_VehicleListInterface.popup_dropdown(None)
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
            if current_owner not in ["Select Gender", "All"]:
                # Revert owner dropdown to original state
                self.obj_VehicleListInterface.entry_selected_owner.delete(0, 'end')
                self.obj_VehicleListInterface.entry_selected_owner.insert(0, "Select Gender")
            self.obj_VehicleListInterface.close_filter_dropdown(None)
            self.obj_VehicleListInterface.popup_dropdown()
            self.obj_VehicleListInterface.bool_owner_dropdown_opened = False
        elif (self.obj_VehicleListInterface.bool_color_dropdown_opened):
            # Check if color dropdown has a value selected
            current_color = self.obj_VehicleListInterface.entry_selected_color.get()
            if current_color not in ["Select Status", "All"]:
                # Revert color dropdown to original state
                self.obj_VehicleListInterface.entry_selected_color.delete(0, 'end')
                self.obj_VehicleListInterface.entry_selected_color.insert(0, "Select Vehicle Color")

            #self.obj_VehicleListInterface.popup_dropdown(None)
            self.obj_VehicleListInterface.bool_color_dropdown_opened = False

        # Handle type dropdown
        if (self.obj_VehicleListInterface.bool_type_dropdown_opened is True):
            self.obj_VehicleListInterface.close_filter_dropdown(None)


            #self.obj_VehicleListInterface.popup_dropdown(None)
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

            #self.obj_VehicleListInterface.popup_dropdown(None)
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
        self.obj_VehicleListInterface.dict_filter_criteria["gender"] = "%" if (str_owner == "All" or str_owner == "") else str_owner

        str_type = self.obj_VehicleListInterface.entry_selected_type.get().lstrip(" ")
        self.obj_VehicleListInterface.dict_filter_criteria["status"] = "%" if (str_type == "All" or str_type == "") else str_type

        self.obj_VehicleListInterface.reset_interface()
        self.obj_Interface.obj_RootInterface.focus_set()
        self.obj_VehicleListInterface.vehicle_data = []
        self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_person_details(self.obj_VehicleListInterface.dict_filter_criteria)
        self.obj_VehicleListInterface.i_total_data = len(self.obj_VehicleListInterface.vehicle_data)
        if(self.obj_VehicleListInterface.i_total_data > 0):
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
        # col_name=str_column
        # self.obj_VehicleListInterface.sort_column(col_name)

        sort_col_name=""

        str_db_column = "full_name"

        if str_db_column=="full_name":
            sort_col_name="Name"
        
        if (str_column == "Age"):
            sort_col_name = "Age"
            str_db_column = "age"
        elif (str_column == "Gender"):
            sort_col_name = "Gender"
            str_db_column = "gender"
        elif (str_column == "Status"):
            sort_col_name = "Status"
            str_db_column = "status"


        self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.sort_vehicle_data(
            self.obj_VehicleListInterface.vehicle_data,
            str_db_column,
            self.obj_VehicleListInterface.dict_columns_buttons[str_column][1])

        self.obj_VehicleListInterface.sort_column(sort_col_name, self.obj_VehicleListInterface.dict_columns_buttons[str_column][1])

        self.obj_VehicleListInterface.dict_columns_buttons[str_column][1] = not self.obj_VehicleListInterface.dict_columns_buttons[str_column][1]

        self.obj_VehicleListInterface.update_table(self.obj_VehicleListInterface.vehicle_data)

    # def onclick_column_headings(self, str_column: str):
    #     print(str_column,"str__________")
    #     # col_name=str_column
    #     # self.obj_VehicleListInterface.sort_column(col_name)
    #     str_db_column = "vehicle_number"

    #     if (str_column == "Vehicle Type"):
    #         str_db_column = "vehicle_type"
    #     elif (str_column == "Vehicle Color"):
    #         str_db_column = "vehicle_color"
    #     elif (str_column == "Owner Name"):
    #         str_db_column = "vehicle_owner"
    #     elif (str_column == "Manufacturing Year"):
    #         str_db_column = "manufacturing_year"

    #     self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.sort_vehicle_data(
    #         self.obj_VehicleListInterface.vehicle_data,
    #         str_db_column,
    #         self.obj_VehicleListInterface.dict_columns_buttons[str_column][1])

    #     self.obj_VehicleListInterface.dict_columns_buttons[str_column][1] = not \
    #     self.obj_VehicleListInterface.dict_columns_buttons[str_column][1]

    #     self.obj_VehicleListInterface.update_table(self.obj_VehicleListInterface.vehicle_data)

    
    def onclick_next(self):
        self.obj_Interface.obj_RootInterface.focus_set()

        if (self.obj_VehicleListInterface.bool_filter_popup is True):
            #self.obj_VehicleListInterface.close_dropdown(None)
            #self.obj_VehicleListInterface.popup_dropdown(None)
            self.obj_VehicleListInterface.reset_filter_form()
            self.obj_VehicleListInterface.toggle_filter_popup()

        # self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_vehicle_details(self.obj_VehicleListInterface.i_end_index, self.obj_VehicleListInterface.dict_filter_criteria)
        # i_data_count = len(self.obj_VehicleListInterface.vehicle_data)
        # if(i_data_count > 0 ):
        #     self.obj_VehicleListInterface.i_start_index = self.obj_VehicleListInterface.i_end_index + 1
        #     self.obj_VehicleListInterface.i_end_index = self.obj_VehicleListInterface.i_end_index + i_data_count

        #     self.obj_VehicleListInterface.update_table(self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)

        data = []
        required_data = []
        if(self.obj_VehicleListInterface.dict_filter_criteria["full_name"] != ""):
            data = self.obj_core.obj_Vehicle.search_vehicle_number(self.obj_VehicleListInterface.vehicle_data, self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"])
        else:
            data = self.obj_VehicleListInterface.vehicle_data

        required_data = data[(self.obj_VehicleListInterface.i_end_index) : ((self.obj_VehicleListInterface.i_end_index) + 5)]
        i_data_count = len(required_data)
        if(i_data_count > 0 ):
            self.obj_VehicleListInterface.i_start_index = self.obj_VehicleListInterface.i_end_index + 1
            self.obj_VehicleListInterface.i_end_index = self.obj_VehicleListInterface.i_end_index + i_data_count
        
        self.obj_VehicleListInterface.update_table(required_data)
        
        

    def onclick_previous(self):
        print(len(self.obj_VehicleListInterface.selected_face_set),"((((((((((((((((((((((((()))))))))))))))))))))))))")
        self.obj_Interface.obj_RootInterface.focus_set()
        if (self.obj_VehicleListInterface.bool_filter_popup is True):
            self.obj_VehicleListInterface.close_dropdown(None)
            self.obj_VehicleListInterface.reset_filter_form()
            self.obj_VehicleListInterface.toggle_filter_popup()

        data = []
        required_data = []
        if(self.obj_VehicleListInterface.dict_filter_criteria["full_name"] != ""):
            data = self.obj_core.obj_Vehicle.search_vehicle_number(self.obj_VehicleListInterface.vehicle_data, self.obj_VehicleListInterface.dict_filter_criteria["full_name"])
        else:
            data = self.obj_VehicleListInterface.vehicle_data

        required_data = data[((self.obj_VehicleListInterface.i_start_index)-6) : ((self.obj_VehicleListInterface.i_start_index)-1)]
        i_data_count = len(required_data)
        if(i_data_count > 0 ):
            self.obj_VehicleListInterface.i_end_index = (self.obj_VehicleListInterface.i_start_index) - 1
            self.obj_VehicleListInterface.i_start_index = (self.obj_VehicleListInterface.i_start_index)-5
        
        self.obj_VehicleListInterface.update_table(required_data)

        # i_start_index = self.obj_VehicleListInterface.i_start_index - 50
        # if(i_start_index < 0): 
        #     i_start_index = 1

        # self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_vehicle_details(i_start_index-1, self.obj_VehicleListInterface.dict_filter_criteria)
        # i_data_count = len(self.obj_VehicleListInterface.vehicle_data)
        # if(i_data_count > 0):
        #     self.obj_VehicleListInterface.i_start_index = i_start_index
        #     self.obj_VehicleListInterface.i_end_index = (i_start_index + i_data_count) - 1

        #     self.obj_VehicleListInterface.update_table(self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)

        # data = []
        # required_data = []
        # if(self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] != ""):
        #     data = self.obj_core.obj_Vehicle.search_vehicle_number(self.obj_VehicleListInterface.vehicle_data, self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"])
        # else:
        #     data = self.obj_VehicleListInterface.vehicle_data

        # required_data = data[((self.obj_VehicleListInterface.i_start_index)-6) : ((self.obj_VehicleListInterface.i_start_index)-1)]
        # i_data_count = len(required_data)
        # if(i_data_count > 0 ):
        #     self.obj_VehicleListInterface.i_end_index = (self.obj_VehicleListInterface.i_start_index) - 1
        #     self.obj_VehicleListInterface.i_start_index = (self.obj_VehicleListInterface.i_start_index)-5
        
        # self.obj_VehicleListInterface.update_table(required_data)

    # def onclick_action(self):
    #     if (self.obj_VehicleListInterface.bool_filter_popup is True):
    #         self.obj_VehicleListInterface.close_dropdown(None)
    #         self.obj_VehicleListInterface.reset_filter_form()
    #         self.obj_VehicleListInterface.toggle_filter_popup()
    #
    #     i_start_index = self.obj_VehicleListInterface.i_start_index
    #     if (i_start_index < 0):
    #         i_start_index = 1
    #
    #     self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_vehicle_details(i_start_index,
    #                                                                                                  self.obj_VehicleListInterface.dict_filter_criteria)
    #     i_data_count = len(self.obj_VehicleListInterface.vehicle_data)
    #     if (i_data_count > 0):
    #         self.obj_VehicleListInterface.i_start_index = i_start_index
    #         self.obj_VehicleListInterface.i_end_index = (i_start_index + i_data_count) - 1
    #
    #         self.obj_VehicleListInterface.update_table(self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)

    def onclick_add(self):
        self.obj_VehicleListInterface.Add_Face_Form()

    def onclick_Add_cancel(self):
        self.obj_VehicleListInterface.destroy_registration_form()



    def onclick_add_save(self):
        # Retrieve data from the interfac
        str_path = self.obj_VehicleListInterface.photo_path
        str_first_name = self.obj_VehicleListInterface.entry_first_name.get().strip()
        str_middle_name = self.obj_VehicleListInterface.entry_middle_name.get().strip()

        str_last_name = self.obj_VehicleListInterface.entry_last_name.get().strip()
        str_age = self.obj_VehicleListInterface.entry_age.get().strip()
        str_gender = self.obj_VehicleListInterface.entry_selected_gender.get().strip()
        str_status = self.obj_VehicleListInterface.entry_selected_status.get().strip()
        error_count=0
        latest_error_message = None

        # Print the details for debugging purposes
        if(str_path==None):
            print(str_path)
            latest_error_message = "Please Uplaod Photo."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="Please Upload Photo")


        # Encode the photo path into base64
        if str_path:  # Only encode if the path is not empty
            try:
                with open(str_path, "rb") as photo_file:
                    # Read the photo file as binary
                    photo_binary = photo_file.read()
                    # Convert the binary data to base64
                    encoded_photo = base64.b64encode(photo_binary).decode("utf-8")
            except Exception as e:
                # Handle errors (file not found, etc.)
                print(f"Error encoding photo: {e}")
                encoded_photo = None
        else:
            encoded_photo = None



        if not str_status.strip():
            latest_error_message = "Status can not be empty."
            self.obj_VehicleListInterface.label_error.configure(text="Status can not be empty")
            self.obj_VehicleListInterface.entry_selected_status.configure(border_color="red")
            error_count += 1

        # Check for valid vehicle type
        if str_status not in ["WhiteList", "BlackList"]:
            latest_error_message = "Please Enter Status   ."

            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="Please choose 'WhiteList' or 'BlackList'")
            self.obj_VehicleListInterface.entry_selected_status.configure(border_color="red")
        else:
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_selected_status.configure(border_color="green")

        if str_gender not in ["Male", "Female", "Other"]:
            latest_error_message = "Please Enter  Gender "
            error_count += 1
            self.obj_VehicleListInterface.entry_selected_gender.configure(border_color="red")
        else:
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_selected_gender.configure(border_color="green")

        if len(str_age) == 0:
            latest_error_message = "Please enter a valid age."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="Please enter a valid age.")
            self.obj_VehicleListInterface.entry_age.configure(border_color="red")
        elif not str_age.isdigit():  # Ensure the input is a numbe
            latest_error_message = "Age must be a number."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="Age must be a number.")
            self.obj_VehicleListInterface.entry_age.configure(border_color="red")
        else:
            # Convert age to an integer and check if it's within the valid range (0 to 120)
            age = int(str_age)
            if age < 0 or age > 120:
                latest_error_message = "Age must be between 0 and 120."
                error_count += 1
                self.obj_VehicleListInterface.label_error.configure(text="Age must be between 0 and 120.")
                self.obj_VehicleListInterface.entry_age.configure(border_color="red")
            else:
                # If all checks pass, clear the error and set the border color to green
                self.obj_VehicleListInterface.label_error.configure(text="")
                self.obj_VehicleListInterface.entry_age.configure(border_color="green")
           


        if not (2 <= len(str_last_name) <= 20):
            latest_error_message = "Last name length should be between 2 and 20 characters"
            self.obj_VehicleListInterface.label_error.configure(text="Last name length should be between 2 and 20 characters")
            self.obj_VehicleListInterface.entry_last_name.configure(border_color="red")

        # If the name length is correct, check if it contains only alphabets
        if str_last_name.isalpha():
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_last_name.configure(border_color="green")
           
        else:
            latest_error_message = "Last name should only contain alphabets!"
            self.obj_VehicleListInterface.label_error.configure(text="Last name should only contain alphabets!")
            self.obj_VehicleListInterface.entry_last_name.configure(border_color="red")
       
        

        if not (2 <= len(str_last_name) <= 20):
            error_count += 1
            latest_error_message = "Last name length should be between 2 and 20 characters"
            self.obj_VehicleListInterface.label_error.configure(text="Last name length should be between 2 and 20 characters")
            self.obj_VehicleListInterface.entry_last_name.configure(border_color="red")
        

        if len(str_middle_name) == 0:
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_middle_name.configure(border_color="green")
        
        # Check if middle name contains only alphabetic characters
        elif not str_middle_name.isalpha():
            latest_error_message = "Middle name should only contain alphabets!"
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="Middle name should only contain alphabets!")
            self.obj_VehicleListInterface.entry_middle_name.configure(border_color="red")
        
        # Check if middle name length is between 1 and 3 characters
        elif len(str_middle_name) < 1 or len(str_middle_name) > 10:
            latest_error_message = "Middle name should be between 1 and 3 characters!."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="Middle name should be between 1 and 3 characters!")
            self.obj_VehicleListInterface.entry_middle_name.configure(border_color="red")
           
        
        else:
            # If it passes all checks, it's valid
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_middle_name.configure(border_color="green")

        if not (2 <= len(str_first_name) <= 20):
            latest_error_message = "First name length should be between 2 and 20 characters."
            error_count += 1
            self.obj_VehicleListInterface.label_error.configure(text="First name length should be between 2 and 20 characters")
            self.obj_VehicleListInterface.entry_first_name.configure(border_color="red")
           

        # If the name length is correct, check if it contains only alphabets
        if  str_first_name.isalpha():
            self.obj_VehicleListInterface.label_error.configure(text="")
            self.obj_VehicleListInterface.entry_first_name.configure(border_color="green")
           
        else:
            error_count += 1
            latest_error_message = "First name should only contain alphabets!."
            self.obj_VehicleListInterface.label_error.configure(text="First name should only contain alphabets!")
            self.obj_VehicleListInterface.entry_first_name.configure(border_color="red")
          
            



      

        

        if error_count > 0 and latest_error_message:
                print("Latest error message:", latest_error_message)
                # Optionally display the message on a label or a dialog
                self.obj_VehicleListInterface.label_error.configure(text=latest_error_message)

        

       
    
      

        # Add the person/vehicle to the database
        if(error_count==0):
            dict_status = self.obj_core.obj_Vehicle.add_vehicle(
                str_first_name,str_middle_name, str_last_name, str_age, str_gender, str_status, encoded_photo
            )

            if dict_status["str_error_msg_heading"] == "Error! Duplicate Entries":
                # If duplicate vehicle is found, show a popup
                self.obj_Interface.on_error(
                    "home",
                    "Error! Duplicate Entries",
                    f"A PErsion with the Name '{str_first_name + " "+str_middle_name+" "+str_last_name}' already present.",
                    "#FF4B4B"
                )
            elif dict_status["str_error_msg_heading"] == "Success":
                # If no errors, show success message
                self.obj_Interface.on_error(
                    "home",
                    "Data Added Successfully",
                    "",
                    "#63CA6D",  # Green for success
                    50
                )
                self.onclick_Add_cancel()

                self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_person_details(self.obj_VehicleListInterface.dict_filter_criteria)
                

                self.obj_VehicleListInterface.update_table(self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)

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
            f"Are you sure you want to delete {len(self.obj_VehicleListInterface.selected_face_set) ,self.obj_VehicleListInterface.selected_face_set} Selected Persion ? ",
            icon='warning' 
        )
        print(self.obj_VehicleListInterface.selected_face_set)

        if confirm_delete:
          
            if self.obj_core.obj_Vehicle.delete_vechiles(list(self.obj_VehicleListInterface.selected_face_set)):

                self.obj_Interface.on_error(
                    "home",
                    "Data Deleted Successfully",
                    "",
                    "#63CA6D",
                    50
                )
                
                self.obj_VehicleListInterface.i_total_data = self.obj_VehicleListInterface.i_total_data - len(
                    self.obj_VehicleListInterface.selected_face_set)
                self.obj_VehicleListInterface.selected_face_set.clear()

                # self.obj_VehicleListInterface.destroy_add_vehicle_form()
                self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_person_details(self.obj_VehicleListInterface.dict_filter_criteria)
                

                # self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_vehicle_details(
                #     self.obj_VehicleListInterface.i_start_index - 1, self.obj_VehicleListInterface.dict_filter_criteria)
                # self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_vehicle_details(self.obj_VehicleListInterface.dict_filter_criteria)
                # if (self.obj_VehicleListInterface.dict_filter_criteria["full_name"] != ""):
                #     self.obj_VehicleListInterface.i_total_data = len(self.obj_VehicleListInterface.vehicle_data)
                #     self.obj_VehicleListInterface.dict_filter_criteria["full_name"] = ""
                #     self.obj_VehicleListInterface.entry_search.delete(0, "end")
                #     self.obj_VehicleListInterface.entry_search.configure(placeholder_text="Enter Full Name..")
                #     self.obj_Interface.obj_RootInterface.focus_set()
 
                # self.obj_VehicleListInterface.i_total_data = self.obj_VehicleListInterface.i_total_data - len(
                #     self.obj_VehicleListInterface.selected_face_set)
 
                # self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_person_details(
                #     self.obj_VehicleListInterface.dict_filter_criteria)
                print(f"st index: {self.obj_VehicleListInterface.i_start_index} end index: {self.obj_VehicleListInterface.i_end_index} len : {len(self.obj_VehicleListInterface.vehicle_data)}")

                data = []
                while (True):
                    if (len(self.obj_VehicleListInterface.vehicle_data) == 0):
                        self.obj_VehicleListInterface.i_start_index = 0
                        self.obj_VehicleListInterface.i_end_index = 0
                        break
 
                    data = (self.obj_VehicleListInterface.vehicle_data)[
                           ((self.obj_VehicleListInterface.i_start_index) - 1):(
                                       (self.obj_VehicleListInterface.i_start_index) + 4)]
                    
                    print(f"fd: {self.obj_VehicleListInterface.vehicle_data[0]} \n pd: {data[0]}'")
 
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
        str_path = self.obj_VehicleListInterface.photo_path
        str_first_name = self.obj_VehicleListInterface.Edit_entry_first_name.get().strip()
        str_middle_name = self.obj_VehicleListInterface.Edit_entry_middle_name.get().strip()

        str_last_name = self.obj_VehicleListInterface.Edit_entry_last_name.get().strip()
        str_age = self.obj_VehicleListInterface.Edit_entry_age.get().strip()
        str_gender = self.obj_VehicleListInterface.Edit_entry_selected_gender.get().strip()
        str_status = self.obj_VehicleListInterface.Edit_entry_selected_status.get().strip()
        str_id=self.obj_VehicleListInterface.vehicle.get("id")
        matching=0
        error_count=0


        # Print the details for debugging purposes
        # print( str_first_name,str_middle_name,str_last_name,str_age, str_gender, str_status,str_path)
        if str_path:  # Only encode if the path is not empty
            try:
                with open(str_path, "rb") as photo_file:
                    # Read the photo file as binary
                    photo_binary = photo_file.read()
                    # Convert the binary data to base64
                    encoded_photo = base64.b64encode(photo_binary).decode("utf-8")
                   
            except Exception as e:
                # Handle errors (file not found, etc.)
                print(f"Error encoding photo: {e}")
                encoded_photo = None
        else:
            encoded_photo = None

        
      
        

        if(str_path==None):
            matching+=1
            str_path=self.obj_VehicleListInterface.old_photo
            encoded_photo=str_path

        full_name = str_first_name +" "+str_middle_name +" " + str_last_name
  
        if(self.obj_VehicleListInterface.vehicle['full_name']==full_name):
            matching+=1
       
        if (self.obj_VehicleListInterface.vehicle['age'] == str_age):
            matching+=1

        if (self.obj_VehicleListInterface.vehicle['gender'] == str_gender):
            matching+=1

        if (self.obj_VehicleListInterface.vehicle['status'] == str_status):
            matching+=1

      


        if not str_status.strip():
            latest_error_message = "Status can not be empty."
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Status can not be empty")
            self.obj_VehicleListInterface.Edit_entry_selected_status.configure(border_color="red")
            error_count += 1

        # Check for valid vehicle type
        if str_status not in ["WhiteList", "BlackList"]:
            latest_error_message = "Please Enter Status   ."

            error_count += 1
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Please choose 'WhiteList' or 'BlackList'")
            self.obj_VehicleListInterface.Edit_entry_selected_status.configure(border_color="red")
        else:
            self.obj_VehicleListInterface.Edit_label_error.configure(text="")
            self.obj_VehicleListInterface.Edit_entry_selected_status.configure(border_color="green")

        if str_gender not in ["Male", "Female", "Other"]:
            latest_error_message = "Please Enter  Gender "
            error_count += 1
            self.obj_VehicleListInterface.Edit_entry_selected_gender.configure(border_color="red")
        else:
            self.obj_VehicleListInterface.Edit_label_error.configure(text="")
            self.obj_VehicleListInterface.Edit_entry_selected_gender.configure(border_color="green")

        if len(str_age) == 0:
            latest_error_message = "Please enter a valid age."
            error_count += 1
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Please enter a valid age.")
            self.obj_VehicleListInterface.Edit_entry_age.configure(border_color="red")
        elif not str_age.isdigit():  # Ensure the input is a numbe
            latest_error_message = "Age must be a number."
            error_count += 1
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Age must be a number.")
            self.obj_VehicleListInterface.Edit_entry_age.configure(border_color="red")
        else:
            # Convert age to an integer and check if it's within the valid range (0 to 120)
            age = int(str_age)
            if age < 0 or age > 120:
                latest_error_message = "Age must be between 0 and 120."
                error_count += 1
                self.obj_VehicleListInterface.Edit_label_error.configure(text="Age must be between 0 and 120.")
                self.obj_VehicleListInterface.Edit_entry_age.configure(border_color="red")
            else:
                # If all checks pass, clear the error and set the border color to green
                self.obj_VehicleListInterface.Edit_label_error.configure(text="")
                self.obj_VehicleListInterface.Edit_entry_age.configure(border_color="green")
           


        if not (2 <= len(str_last_name) <= 20):
            latest_error_message = "Last name length should be between 2 and 20 characters"
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Last name length should be between 2 and 20 characters")
            self.obj_VehicleListInterface.Edit_entry_last_name.configure(border_color="red")

        # If the name length is correct, check if it contains only alphabets
        if str_last_name.isalpha():
            self.obj_VehicleListInterface.Edit_label_error.configure(text="")
            self.obj_VehicleListInterface.Edit_entry_last_name.configure(border_color="green")
           
        else:
            latest_error_message = "Last name should only contain alphabets!"
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Last name should only contain alphabets!")
            self.obj_VehicleListInterface.Edit_entry_last_name.configure(border_color="red")
       
        

        if not (2 <= len(str_last_name) <= 20):
            error_count += 1
            latest_error_message = "Last name length should be between 2 and 20 characters"
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Last name length should be between 2 and 20 characters")
            self.obj_VehicleListInterface.Edit_entry_last_name.configure(border_color="red")
        

        if len(str_middle_name) == 0:
            self.obj_VehicleListInterface.Edit_label_error.configure(text="")
            self.obj_VehicleListInterface.Edit_entry_middle_name.configure(border_color="green")
        
        # Check if middle name contains only alphabetic characters
        elif not str_middle_name.isalpha():
            latest_error_message = "Middle name should only contain alphabets!"
            error_count += 1
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Middle name should only contain alphabets!")
            self.obj_VehicleListInterface.Edit_entry_middle_name.configure(border_color="red")
        
        # Check if middle name length is between 1 and 3 characters
        elif len(str_middle_name) < 1 or len(str_middle_name) > 10:
            latest_error_message = "Middle name should be between 1 and 3 characters!."
            error_count += 1
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Middle name should be between 1 and 3 characters!")
            self.obj_VehicleListInterface.Edit_entry_middle_name.configure(border_color="red")
           
        
        else:
            # If it passes all checks, it's valid
            self.obj_VehicleListInterface.Edit_label_error.configure(text="")
            self.obj_VehicleListInterface.Edit_entry_middle_name.configure(border_color="green")

        if not (2 <= len(str_first_name) <= 20):
            latest_error_message = "First name length should be between 2 and 20 characters."
            error_count += 1
            self.obj_VehicleListInterface.Edit_label_error.configure(text="First name length should be between 2 and 20 characters")
            self.obj_VehicleListInterface.Edit_entry_first_name.configure(border_color="red")
           

        # If the name length is correct, check if it contains only alphabets
        if  str_first_name.isalpha():
            self.obj_VehicleListInterface.Edit_label_error.configure(text="")
            self.obj_VehicleListInterface.Edit_entry_first_name.configure(border_color="green")
           
        else:
            error_count += 1
            latest_error_message = "First name should only contain alphabets!."
            self.obj_VehicleListInterface.Edit_label_error.configure(text="First name should only contain alphabets!")
            self.obj_VehicleListInterface.Edit_entry_first_name.configure(border_color="red")
          
            



      

        

        if error_count > 0 and latest_error_message:
                print("Latest error message:", latest_error_message)
                # Optionally display the message on a label or a dialog
                self.obj_VehicleListInterface.Edit_label_error.configure(text=latest_error_message)

        
       

        if matching ==4 :
            self.obj_VehicleListInterface.Edit_label_error.configure(text="Data is already present") 
        else:
       
            dict_status = self.obj_core.obj_Vehicle.update_vehicle(
                                full_name , str_age, str_gender, str_status, encoded_photo,str_id ,"Anu")
                
        if dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == "":
                    self.obj_Interface.switch_frames('vehicle_list')
                    self.obj_Interface.on_error(
                        "home",
                        "Data Edited Successfully",
                        "",
                        "#63CA6D",
                        50
                    )
      
                    # bool_update_data = (((self.obj_VehicleListInterface.dict_filter_criteria["full_name"] == "%") and
                    #                     (self.obj_VehicleListInterface.dict_filter_criteria["status"] == "%") and
                    #                     (self.obj_VehicleListInterface.dict_filter_criteria["gender"] == "%")) or
                    #                     ((self.obj_VehicleListInterface.dict_filter_criteria["full_name"] == full_name) or
                    #                     (self.obj_VehicleListInterface.dict_filter_criteria["status"] == str_status) or
                    #                     (self.obj_VehicleListInterface.dict_filter_criteria["gender"] == str_gender)))

                    # if (bool_update_data):
                    #     self.obj_VehicleListInterface.i_total_data = len(self.obj_VehicleListInterface.vehicle_data) + 1

                    #     self.obj_VehicleListInterface.vehicle_data.append({
                    #         "full_name": full_name,
                    #         "status":str_status,
                    #         "gender":str_gender,
                    #         "age":age,
                    #         "photo_path":encoded_photo
                          
                    #     })

                    # if (self.obj_VehicleListInterface.dict_filter_criteria["full_name"] != ""):
                    #     self.obj_VehicleListInterface.dict_filter_criteria["str_vehicle_number"] = ""
                    #     self.obj_VehicleListInterface.entry_search.delete(0, "end")
                    #     self.obj_VehicleListInterface.entry_search.configure(placeholder_text="Enter Vehicle Number..")
                    #     self.obj_Interface.obj_RootInterface.focus_set()

                    #     if (not bool_update_data):
                    #         self.obj_VehicleListInterface.i_total_data = len(self.obj_VehicleListInterface.vehicle_data)

                    #     self.obj_Interface.dict_frames["vehicle_list"].i_start_index = 1
                    #     self.obj_Interface.dict_frames[
                    #         "vehicle_list"].i_end_index = 5 if self.obj_VehicleListInterface.i_total_data >= 5 else self.obj_VehicleListInterface.i_total_data
                    # else:
                    #     if (bool_update_data):
                    #         if (((
                    #                     self.obj_VehicleListInterface.i_end_index - self.obj_VehicleListInterface.i_start_index) + 1) < 5):
                    #             self.obj_VehicleListInterface.i_end_index += 1

                    # data = (self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)[
                    #     ((self.obj_VehicleListInterface.i_start_index) - 1):(self.obj_VehicleListInterface.i_end_index)]
                    # self.obj_VehicleListInterface.update_table(data)
                    # self.obj_VehicleListInterface.destroy_add_vehicle_form()


                    self.obj_VehicleListInterface.selected_face_set.clear()
                    self.obj_VehicleListInterface.update_button_states()
                    self.obj_VehicleListInterface.vehicle_data = self.obj_core.obj_Vehicle.fetch_person_details(self.obj_VehicleListInterface.dict_filter_criteria)
                    

                    self.obj_VehicleListInterface.update_table(self.obj_Interface.dict_frames["vehicle_list"].vehicle_data)
                
 
          
        else:
            # Display error message if update failed
            self.obj_Interface.on_error(
                "home",
                dict_status["str_error_msg_heading"],
                dict_status["str_error_msg"],
                "#FF4B4B"
            )
        


       