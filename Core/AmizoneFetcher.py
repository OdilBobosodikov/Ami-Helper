from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from  datetime import date

class AmizoneFetcher:
    __amizone_url='https://s.amizone.net/'
    __amizone_login=''
    __amizone_password=''
    __wrong_credentials = False
    __wrong_credentials_message = "Invalid login or password"
    __statistics = {}
    __attendence_updated_time = date(1,1,1)
    __attendence = []
    __time_table = []

    __dict_of_colors = {"255, 0, " : "red", "79, 204, 7": "green", "58, 135, 17": "gray"}

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 30) 

    def setCredentials(self, login, password):
        self.__amizone_login = login
        self.__amizone_password = password
        
    def __login_validation(self):
        try: 
            self.driver.find_element(By.NAME, '_UserName').send_keys(self.__amizone_login)
        except NoSuchElementException:
            return False
        return True
    
    def login(self):
        self.driver.get(self.__amizone_url)
        self.driver.find_element(By.NAME, '_UserName').send_keys(self.__amizone_login)
        self.driver.find_element(By.NAME, '_Password').send_keys(self.__amizone_password)
        self.driver.find_element(By.CLASS_NAME, 'login100-form-btn').click()
  
        # since warnings does not appear on screen I am checking if login field still exists
        if self.__login_validation():
            self.__wrong_credentials = True
            return False
        else:
             self.__wrong_credentials = False      

        self.wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(@class, 'btn btn-default')])[2]")))
        self.driver.find_element(By.XPATH, "(//button[contains(@class, 'btn btn-default')])[2]").click()

        # For testing purposes
        #self.driver.find_element(By.XPATH, "//button[contains(@class, 'fc-prev-button fc-button fc-state-default fc-corner-left')]").click()
        #self.driver.find_element(By.XPATH, "//button[contains(@class, 'fc-prev-button fc-button fc-state-default fc-corner-left')]").click()

        return True
    
    def fetch_time_table(self):
        self.login()

        if self.__wrong_credentials:
            return self.__wrong_credentials_message
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'fc-list-item class-schedule-color')]")))
            schedule_items = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'fc-list-item class-schedule-color')]")
            attendance_dots = self.driver.find_elements(By.CLASS_NAME, "fc-event-dot")
            
        except NoSuchElementException: 
            return "Time table is not available right now"
     
        for i,j in zip(schedule_items, attendance_dots):
            subject = i.get_attribute("innerText").replace("\n","").replace("\t", "").strip()
            style = j.get_attribute("style")

            t = style[style.index("(") + 1: len(style) - 3]
            dot = self.__dict_of_colors[t]
            self.__time_table.append((subject, dot))

        return self.__time_table

    def __fetch_attendance(self):
        self.login()

        if self.__wrong_credentials:
            return self.__wrong_credentials_message
        
        self.__attendence = []
        try:
            lst_of_subjects = self.driver.find_element(By.ID, "tasks")
        except NoSuchElementException: 
            return "Attendence is not available right now"
        
        subjects = lst_of_subjects.find_elements(By.CSS_SELECTOR, "li")
        
        for i in subjects:
            self.__attendence.append(i.get_attribute("innerText").replace("\n"," ").strip())
        
        self.__attendence_updated_time = date.today()

    def compute_overall_statistics(self):
        
        """ Returns a dictionary of information about student's attendence in the format {subject: [attended_lessons, all_lessons]}"""
        self.__fetch_attendance()

        for i in self.__attendence:
            words = i.split(" ")
            subject = words[0:len(words)-2]
            days = words[-1].split('/')

            self.__statistics[str(" ".join(subject[1:len(subject)+1]))] = (int(days[0]), int(days[1]))

        return self.__statistics
    
    def dispose(self):
        self.driver.quit()




    

        