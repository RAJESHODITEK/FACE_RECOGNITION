from Core.main import Core
from Interface.main import Interface

class AddVehicleController:
    
    def __init__(self, Core : Core, Interface : Interface):
        
        self.obj_core = Core
        self.obj_Interface = Interface
        self.obj_AddVehicleInterface = self.obj_Interface.dict_frames["add_vehicle"]
        
        self.bind_buttons()

        self.obj_AddVehicleInterface.entry_model.bind("<KeyRelease>", self.validate_model)
        self.obj_AddVehicleInterface.entry_number.bind("<KeyRelease>", self.validate_number)
        self.obj_AddVehicleInterface.entry_color.bind("<KeyRelease>", self.validate_color)
        self.obj_AddVehicleInterface.entry_date.bind("<KeyRelease>", self.validate_date)    
        self.obj_AddVehicleInterface.entry_owner.bind("<KeyRelease>", self.validate_owner)   

    def bind_buttons(self):
        self.obj_AddVehicleInterface.button_save.configure(command=self.save)
        self.obj_AddVehicleInterface.button_cancel.configure(command=self.cancel)

    def save(self) -> None:

        bool_is_valid_data = self.validate_company(None)
        bool_is_valid_data = self.validate_type(None) and bool_is_valid_data
        bool_is_valid_data = self.validate_model(None) and bool_is_valid_data
        bool_is_valid_data = self.validate_number(None) and bool_is_valid_data
        bool_is_valid_data = self.validate_color(None) and bool_is_valid_data
        bool_is_valid_data = self.validate_date(None) and bool_is_valid_data
        bool_is_valid_data = self.validate_owner(None) and bool_is_valid_data

        if bool_is_valid_data:
            str_company = self.obj_AddVehicleInterface.entry_selected_company.get()
            str_model = self.obj_AddVehicleInterface.entry_model.get()
            str_type = self.obj_AddVehicleInterface.entry_selected_type.get()
            str_number = self.obj_AddVehicleInterface.entry_number.get()
            str_color = self.obj_AddVehicleInterface.entry_color.get()
            i_date = int(self.obj_AddVehicleInterface.entry_date.get())
            str_owner = self.obj_AddVehicleInterface.entry_owner.get()

            dict_status = self.obj_core.obj_Vehicle.add_vehicle(str_company, str_model, str_type, str_number, str_color, i_date, str_owner)

            if (dict_status["str_error_msg_heading"] == "" and dict_status["str_error_msg"] == ""):
                self.obj_AddVehicleInterface.reset_interface()
                self.obj_Interface.on_error(
                        "home",
                        "Data Added Successfullly", 
                        "",
                       "#63CA6D",
                        50
                    )
            else:
                self.obj_Interface.on_error(
                    "home",
                    dict_status["str_error_msg_heading"], 
                    dict_status["str_error_msg"],
                    "#FF4B4B"
                )
        else:
            self.obj_Interface.on_error(
                "home",
                "Error! Invalid Data", 
                "Check if the entered data fulfill the required conditions.",
                "#FF4B4B"
            )

    def cancel(self):
        self.obj_AddVehicleInterface.reset_interface()

    def validate_company(self, event) -> bool:
        str_company = self.obj_AddVehicleInterface.entry_selected_company.get()
        str_error_msg = self.obj_core.obj_Vehicle.validate_company(str_company)

        if len(str_error_msg) == 0:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_selected_company, 
                                                                 self.obj_AddVehicleInterface.label_company_error, 
                                                                 str_error_msg, 
                                                                 "#DEDEDE")
            return True
        else:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_selected_company, 
                                                                 self.obj_AddVehicleInterface.label_company_error, 
                                                                 str_error_msg, 
                                                                 "#FF0000")
            return False
        
    def validate_model(self, event) -> bool:
        str_model = self.obj_AddVehicleInterface.entry_model.get()
        str_error_msg = self.obj_core.obj_Vehicle.validate_model(str_model)

        if len(str_error_msg) == 0:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_model, 
                                                                 self.obj_AddVehicleInterface.label_model_error, 
                                                                 str_error_msg, 
                                                                 "#DEDEDE")
            return True
        else:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_model, 
                                                                 self.obj_AddVehicleInterface.label_model_error, 
                                                                 str_error_msg, 
                                                                 "#FF0000")
            return False
        

    
    def validate_type(self, event) -> bool:
        str_type = self.obj_AddVehicleInterface.entry_selected_type.get()
        str_error_msg = self.obj_core.obj_Vehicle.validate_type(str_type)

        if len(str_error_msg) == 0:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_selected_type, 
                                                                    self.obj_AddVehicleInterface.label_type_error, 
                                                                    str_error_msg, 
                                                                    "#DEDEDE")
            return True
        else:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_selected_type, 
                                                                    self.obj_AddVehicleInterface.label_type_error, 
                                                                    str_error_msg, 
                                                                    "#FF0000")
            return False
        
        

    def validate_number(self, event) -> bool:
        str_number = self.obj_AddVehicleInterface.entry_number.get()
        str_error_msg = self.obj_core.obj_Vehicle.validate_number(str_number)

        if len(str_error_msg) == 0:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_number, 
                                                                    self.obj_AddVehicleInterface.label_number_error, 
                                                                    str_error_msg, 
                                                                    "#DEDEDE")
            return True
        else:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_number, 
                                                                    self.obj_AddVehicleInterface.label_number_error, 
                                                                    str_error_msg, 
                                                                    "#FF0000")
            return False
        
    
    def validate_color(self, event) -> bool:
        str_color = self.obj_AddVehicleInterface.entry_color.get()
        str_error_msg = self.obj_core.obj_Vehicle.validate_color(str_color)

        if len(str_error_msg) == 0:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_color, 
                                                                    self.obj_AddVehicleInterface.label_color_error, 
                                                                    str_error_msg, 
                                                                    "#DEDEDE")
            return True
        else:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_color, 
                                                                    self.obj_AddVehicleInterface.label_color_error, 
                                                                    str_error_msg, 
                                                                    "#FF0000")
            return False
        
    
    def validate_date(self, event) -> bool:
        str_date = self.obj_AddVehicleInterface.entry_date.get()
        str_error_msg = self.obj_core.obj_Vehicle.validate_date(str_date)

        if len(str_error_msg) == 0:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_date, 
                                                                    self.obj_AddVehicleInterface.label_date_error, 
                                                                    str_error_msg, 
                                                                    "#DEDEDE")
            return True
        else:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_date, 
                                                                    self.obj_AddVehicleInterface.label_date_error, 
                                                                    str_error_msg, 
                                                                    "#FF0000")
            return False
        
    
    def validate_owner(self, event) -> bool:
        str_owner = self.obj_AddVehicleInterface.entry_owner.get()
        str_error_msg = self.obj_core.obj_Vehicle.validate_owner(str_owner)

        if len(str_error_msg) == 0:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_owner, 
                                                                    self.obj_AddVehicleInterface.label_owner_error, 
                                                                    str_error_msg, 
                                                                    "#DEDEDE")
            return True
        else:
            self.obj_AddVehicleInterface.update_on_input_changed(self.obj_AddVehicleInterface.entry_owner, 
                                                                    self.obj_AddVehicleInterface.label_owner_error, 
                                                                    str_error_msg, 
                                                                    "#FF0000")
            return False
