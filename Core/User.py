#from enum import Enum

# Did not understand how to work with Enums in python

#class Status(Enum):
#    NEW = 1
#    DENIED = 2
#    VALIDATED = 3


class User: 
    __login = ''
    __password = ''
    __validation_status = False

    def set_login(self, login : str):
        self.__login = login

    def set_password(self, password : str):
        self.__password = password
    
    def get_credentials(self):
        return (self.__login, self.__password)
    
    def update_user_validation_status(self, status: bool):
        self.__validation_status = status
    
    def get_validation_status(self):
        return self.__validation_status