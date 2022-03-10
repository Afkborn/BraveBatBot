#import

from concurrent.futures import process
import logging
from os import path, mkdir, system, remove,environ
from datetime import datetime
from sys import platform
from time import sleep, time
from unittest import addModuleCleanup
import winreg
from Python.Model.Process import Process
import subprocess
import win32gui
import pyautogui
import re
from bs4 import BeautifulSoup
            

FOLDER_NAME= ["Log","Screenshot"]

class Brave:
    software_list = []
    process_list = []
    brave_version = 0
    publisher = "Brave Software Inc"
    first_start_brave_open = True
    is_brave_open = False
    username = environ.get('USERNAME')
    brave_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    win32gui_brave_handler = None
    sys_platform = ""

    operation_time = 0 # for controller, dont change
    earn_unverified_bat_change = False    
    sucess_count = 0
    unsuccess_count = 0

    #configure 
    operation_count = 30
    operation_controller_cool_down = 60
    refresh_count = 20
    refresh_cool_down = 200
    success_cool_down_time_in_seconds = 60 * 60
    unsuccess_cool_down_time_in_seconds = 20 * 60

    #balance
    total_bat = 0
    earn_verified_bat = 0
    earn_unverified_bat = 0
    giving_bat = 0



    def __init__(self, debug) -> None:
        self.debugEnable = debug
        self.set_logging()
        


        self.check_compatibility()
        self.check_folder()
        self.check_brave_is_loaded()

        if not self.check_brave_is_open():
            self.open_brave()
            sleep(3)
            self.first_start_brave_open = False
        
        self.get_brave_handler()
        
        logging.info("init is done")
        print("Ready to use")

        #print(self.get_bat_count_with_ocr()) # get bat count with OCR (not recommend)


    def get_time_day(self):
        return datetime.now().strftime("%d")

    def get_time_log_config(self):
        return datetime.now().strftime("%H_%M_%S_%d_%m_%Y")

    def set_logging(self):
        if self.debugEnable:
            logging.basicConfig(filename=fr'Log/log_{self.get_time_log_config()}.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
            logging.info("logging is set")


    def check_compatibility(self):
        if platform == "win32":
            logging.info("compatibility is OK")
            print("compatibility is OK")
            self.sys_platform = "win32"
        else:
            logging.error("compatibility is not OK, exit...")
            print("windows only")
            exit()

    def check_folder(self):
        for folder in FOLDER_NAME:
            if not path.exists(folder):
                mkdir(folder)
                logging.info(f"created folder {folder}")

    def get_software_list(self,hive, flag):
        aReg = winreg.ConnectRegistry(None, hive)
        aKey = winreg.OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                            0, winreg.KEY_READ | flag)

        count_subkey = winreg.QueryInfoKey(aKey)[0]

        software_list = []

        for i in range(count_subkey):
            software = {}
            try:
                asubkey_name = winreg.EnumKey(aKey, i)
                asubkey = winreg.OpenKey(aKey, asubkey_name)
                software['name'] = winreg.QueryValueEx(asubkey, "DisplayName")[0]

                try:
                    software['version'] = winreg.QueryValueEx(asubkey, "DisplayVersion")[0]
                except EnvironmentError:
                    software['version'] = 'undefined'
                try:
                    software['publisher'] = winreg.QueryValueEx(asubkey, "Publisher")[0]
                except EnvironmentError:
                    software['publisher'] = 'undefined'
                software_list.append(software)
            except EnvironmentError:
                continue

        return software_list

    def check_brave_is_loaded(self):
        self.software_list.clear() 
        self.software_list = self.get_software_list(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + self.get_software_list(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + self.get_software_list(winreg.HKEY_CURRENT_USER, 0)
        for software in self.software_list:
            if software['name'] == "Brave":
            
                logging.info(f"{software['name']} is loaded, version: {software['version']}, publisher: {software['publisher']}")
                print(f"{software['name']} is loaded, version: {software['version']}")
                self.brave_version = software['version']
                self.publisher = software['publisher']
                return True
        logging.error(f"Brave is not loaded")
        print(f"Brave is not loaded")
        exit()

    def get_process_list(self):
        self.process_list.clear()

        Data = subprocess.check_output(['wmic', 'process', 'list', 'brief'])
        data_str = str(Data)
        data_list = data_str.split("\\r\\r\\n")
        data_list.pop(0)
        data_list.pop(0)
        data_list.pop(-1)
        data_list.pop(-1)
        try:
            for data in data_list:
                data_str = data.split()
                if (len(data_str) ==6):
                    my_process = Process(data_str[0],data_str[1],data_str[2],data_str[3],data_str[4],data_str[5])
                    self.process_list.append(my_process)
        except IndexError as e:
            pass

    def check_brave_is_open(self):
        self.get_process_list()
        for process in self.process_list:
            if process.name == "brave.exe":
                logging.info(f"Brave is open, version: {process.process_id}, priority: {process.priority}, handle_count: {process.handle_count}, thread_count: {process.thread_count}, working_set_size: {process.working_set_size}")
                print(f"Brave is already open..")
                self.is_brave_open = True
                return True
        logging.info(f"Brave is not open, open it")
        print(f"Brave is not open, open it")
        return False

    def check_file_exists(self,fileloc):
        if path.exists(fileloc):
            logging.info(f"{fileloc} exists")
            return True
        else:
            logging.error(f"{fileloc} does not exist")
            return False

    def open_brave(self):
        if self.check_file_exists(self.brave_location):

            # system(f'"{self.brave_location}"')
            subprocess.Popen([self.brave_location])
            logging.info('Brave is open')
            print("Brave is open")
            self.is_brave_open = True
        else:
            logging.error(f"{self.brave_location} does not exist")
            print("Brave does not exist")
            exit()

    def get_brave_handler(self):

        handler_list = []

        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                if ("- Brave" in win32gui.GetWindowText(hwnd)):
                    # print(hex(hwnd), win32gui.GetWindowText( hwnd ))
                    handler_list.append(hwnd)
                    self.win32gui_brave_handler = hwnd
        win32gui.EnumWindows(winEnumHandler, None)
        if len(handler_list) > 1:
            logging.error(f"more than one brave window is open")
            print("more than one brave window is open")

        return self.win32gui_brave_handler

    def get_tab_name(self):
        tab_name = win32gui.GetWindowText(self.win32gui_brave_handler)
        logging.info(f"tab name: {tab_name}")
        return tab_name
    
    def set_active_window_brave(self):
        try:

            win32gui.SetForegroundWindow(self.win32gui_brave_handler)
            win32gui.SetActiveWindow(self.win32gui_brave_handler)

            logging.info(f"Brave is active window")

            # win32gui.GetWindowRect(self.win32gui_brave_handler)  # returns program location
            win32gui.MoveWindow(self.win32gui_brave_handler, 0, 0, 1280, 720, True)
            logging.info(f"Brave move to 0,0,1280,720")

            print("Brave is active window at 0,0,1280,720")
        except Exception as e:
            logging.error(f"{e}")
            print(f"{e}")
            
    
    def open_new_tab(self):
        self.set_active_window_brave()
        sleep(0.1)
        pyautogui.hotkey("ctrl","t")
        sleep(0.1)
        if "Yeni Sekme" in self.get_tab_name():
            return True
        return False

    def get_screenshot(self,location_x,location_y,width,height,file_name):
        file_name = f"{file_name}_{self.get_time_log_config()}.png"
        file_loc = fr"Screenshot/{file_name}"
        pyimage = pyautogui.screenshot(file_loc,region=(location_x,location_y,width,height))
        logging.info(f"{file_name} is taken")
        print(f"{file_name} is taken")
        return (file_loc,pyimage)
           


    def get_bat_count_with_ocr(self):
        bat_odeme = False
        day_int = int(self.get_time_day())
        logging.info("getting bat count")
        if not "Yeni Sekme" in self.get_tab_name():
            self.open_new_tab()
        else:
            self.set_active_window_brave()
        fileLocOriginal, pyimage = self.get_screenshot(0,0,1280,720,"brave_ana_ekran")
        start_x = 958
        stary_y = 263
        area_x = 285
        if (day_int < 8):
            area_y = 375
            bat_odeme = True
        else:
            area_y = 331
        file_name = f"bat_area_{self.get_time_log_config()}.png"
        file_loc_bat_area = fr"Screenshot/{file_name}"
        croppyimage = pyimage.crop((start_x,stary_y,start_x+area_x,stary_y+area_y))
        croppyimage.save(file_loc_bat_area)

        start_x = 19
        area_x = 100
        area_y = 30
        if bat_odeme:
            start_y = 300

        else:
            start_y = 250
        file_name = f"bat_earn_area_{self.get_time_log_config()}.png"
        file_loc_bat_earn_area = fr"Screenshot/{file_name}"
        bat_earn_area = croppyimage.crop((start_x,start_y,start_x+area_x,start_y+area_y))
        bat_earn_area.save(file_loc_bat_earn_area)

        if not self.debugEnable:
            remove(fileLocOriginal)
            remove(file_loc_bat_area)
        return 0 

    def get_bat_with_source(self):
        logging.info("getting bat count")
        day_int = int(self.get_time_day())
        if not "Yeni Sekme" in self.get_tab_name():
            self.open_new_tab()
        else:
            self.set_active_window_brave()

        sleep(0.3)
        pyautogui.hotkey("ctrl","s")
        sleep(0.3)
        pyautogui.hotkey("enter")
        sleep(0.3)
        fileLoc = fr'C:\Users\{self.username}\Desktop\New Tab.html'
        if not self.check_file_exists(fileLoc):
            logging.error(f"{fileLoc} does not exist")
            print(f"{fileLoc} does not exist")
            logging.fatal("program is terminated")
            exit()
        else:
            HTMLFile = open(fileLoc, "r", encoding="utf-8")
            
            index = HTMLFile.read()

            S = BeautifulSoup(index, 'html.parser')

            balanceAmount = S.find_all('div', {'class': re.compile("^balanceAmount--..............$")})[0]
            progressItemAmount_list = S.find_all('div', {'class': re.compile("^progressItemAmount--..............$")})
            progressItemAmount_earn = progressItemAmount_list[0]
            progressItemAmount_spend = progressItemAmount_list[1]
            balanceExchangeAmount = S.find_all('div', {'class': re.compile("^balanceExchangeAmount--.............$")})[0]

            self.total_bat = float(balanceAmount.find('span', {'class': 'amount'}).text.replace(",","."))
            self.earn_unverified_bat = float(progressItemAmount_earn.find('span', {'class': 'amount'}).text.replace(",","."))
            self.giving_bat = float(progressItemAmount_spend.find('span', {'class': 'amount'}).text.replace(",","."))
            self.total_bat_usd = float(balanceExchangeAmount.find('span', {'class': 'amount'}).text.replace(",","."))

            HTMLFile.close()

            remove(fileLoc)
            logging.info(f"Total Bat: {self.total_bat}, Total Bat USD: {self.total_bat_usd}, Earn Verified Bat: {self.earn_verified_bat}, Earn Unverified Bat: {self.earn_unverified_bat}, Giving Bat: {self.giving_bat}")
            #time 
            print(f"Total Bat: {self.total_bat}, Total Bat USD: {self.total_bat_usd}, Earn Verified Bat: {self.earn_verified_bat}, Earn Unverified Bat: {self.earn_unverified_bat}, Giving Bat: {self.giving_bat}")
            return (self.total_bat,self.earn_verified_bat,self.earn_unverified_bat,self.giving_bat,self.total_bat_usd)



    def refresh_page(self,count, interval= 1000):
        for _ in range(count):
            pyautogui.hotkey("f5")
            sleep(interval/1000)
        logging.info(f"Page refreshed {count} times. Interval: {interval}")

    def configure(self):
        default_values = """
Operation Count = 30 time
Operation Controller Interval = 60 sec
Refresh Count = 20 time
Refresh Interval = 200 ms 
Successful Operation Cool Down = 60 minute 
Unsuccessful Operation Cool Down = 20 minute
"""
        menu = """
1. Change Operation Count
2. Change Operation Controller Interval
3. Change Refresh Count
4. Change Refresh Interval
5. Change Successful Operation Cool Down
6. Change Unsuccessful Operation Cool Down
7. Print Default Values
8. Print Current Values
9. Back to Main Menu

Enter your choice: """
        while True:
            choice = input(menu)
            if choice == "1":
                self.operation_count = int(input(f"Enter Operation Count (Default 3): "))
                print(f"\nOperation Count is set to {self.operation_count}")
                logging.info(f"Operation Count is set to {self.operation_count}")
            elif choice == "2":
                self.operation_controller_cool_down = int(input("Enter Operation Controller Interval (Default 10 sec): "))
                print(f"\nOperation Controller Interval is set to {self.operation_controller_cool_down}")
                logging.info(f"Operation Controller Interval is set to {self.operation_controller_cool_down}")
            elif choice == "3":
                self.refresh_count = int(input("Enter Refresh Count (Default 10): "))
                print(f"\nRefresh Count is set to {self.refresh_count}")
                logging.info(f"Refresh Count is set to {self.refresh_count}")
            elif choice == "4":
                self.refresh_cool_down = int(input("Enter Refresh Interval  (Default 500 ms): "))
                print(f"\nRefresh Interval is set to {self.refresh_cool_down}")
                logging.info(f"Refresh Interval is set to {self.refresh_cool_down}")
            elif choice == "5":
                self.success_cool_down_time_in_seconds = int(input("Enter Successful Operation Cool Down (Default 45 minute): ")) * 60
                print(f"\nSuccessful Operation Cool Down is set to {self.success_cool_down_time_in_seconds}")
                logging.info(f"Successful Operation Cool Down is set to {self.success_cool_down_time_in_seconds}")
            elif choice == "6":
                self.unsuccess_cool_down_time_in_seconds = int(input("Enter Unsuccessful Operation Cool Down  (Default 10 minute): ")) * 60
                print(f"\nUnsuccessful Operation Cool Down is set to {self.unsuccess_cool_down_time_in_seconds}")
                logging.info(f"Unsuccessful Operation Cool Down is set to {self.unsuccess_cool_down_time_in_seconds}")
            elif choice == "7":
                print(default_values)
            elif choice == "8":
                print(f"\nOperation Count = {self.operation_count} time\nOperation Controller Interval = {self.operation_controller_cool_down} sec\nRefresh Count = {self.refresh_count} time\nRefresh Interval = {self.refresh_cool_down} ms\nSuccessful Operation Cool Down = {self.success_cool_down_time_in_seconds / 60} minute\nUnsuccessful Operation Cool Down = {self.unsuccess_cool_down_time_in_seconds / 60} minute")
            elif choice == "9":
                break



    def get_bat(self):
        logging.info("getting bat")
        self.operation_time = time()
        _, _, old_earn_unverified_bat, _ , _ = self.get_bat_with_source() # get bat count with source code (recommend)

        self.refresh_page(self.refresh_count,self.refresh_cool_down)

        self.get_bat_with_source()
        if (old_earn_unverified_bat != self.earn_unverified_bat):
            self.earn_unverified_bat_change = True
            self.earn_unverified_bat_change_amount = self.earn_unverified_bat - old_earn_unverified_bat
            logging.info(f"Earn Bat Count: {self.earn_unverified_bat_change_amount}")
            print(f"Successfully!!")
            self.sucess_count += 1
            print(f"Earn Bat Count: {self.earn_unverified_bat_change_amount}")
        else:
            self.earn_unverified_bat_change = False
            self.earn_unverified_bat_change_amount = 0
            logging.info(f"Earn Bat Count: {self.earn_unverified_bat_change_amount}")
            print(f"Unsuccessfully!!")
            self.unsuccess_count += 1
            print(f"Earn Bat Count: {self.earn_unverified_bat_change_amount}")
        logging.info("getting bat is over. ")


    def start_brave_bat_bot(self):
        operation_count_controller = 0
        while_controller = True

        while while_controller:
            if (self.operation_count <= operation_count_controller):
                while_controller = False
                #işlem bitti
                print(f"Operation is over.\nSuccessful Operation Count: {self.sucess_count}\nUnsuccessful Operation Count: {self.unsuccess_count}")
                logging.info(f"Operation is over.\nSuccessful Operation Count: {self.sucess_count}\nUnsuccessful Operation Count: {self.unsuccess_count}")

            else:
                if ( not self.earn_unverified_bat_change and time() > (self.operation_time + self.unsuccess_cool_down_time_in_seconds)):
                    self.get_bat()
                    operation_count_controller += 1
                elif (self.earn_unverified_bat_change and time() > (self.operation_time + self.success_cool_down_time_in_seconds) ):
                    self.get_bat()
                    operation_count_controller += 1
                else:
                    if (self.earn_unverified_bat_change):
                        remaning_time_in_sec = self.operation_time + self.success_cool_down_time_in_seconds - time()
                        print(f"Wait for success cool down time. Remaning time in seconds: {int(remaning_time_in_sec)}")
                        logging.info(f"Wait for success cool down time. Remaning time in seconds: {int(remaning_time_in_sec)}")
                    else:
                        remaning_time_in_sec = self.operation_time + self.unsuccess_cool_down_time_in_seconds - time()
                        print(f"Wait for unsuccess cool down time. Remaning time in seconds: {int(remaning_time_in_sec)}")
                        logging.info(f"Wait for unsuccess cool down time. Remaning time in seconds: {int(remaning_time_in_sec)}")
                    sleep(self.operation_controller_cool_down)



            

