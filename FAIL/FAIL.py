'''
    Everything confirmed working on Python 3.8.5

     To install modules needed to run this program run "python -m pip install selenium qdarkstyle pyqt5"   

    Download the chromedriver for your specific version of chrome then drop it in the (python install)\Scripts folder
    
    For no chromedriver pop up go to (selenium install)\webdriver\common\services.py
    Add creationflags=CREATE_NO_WINDOW under stdin=PIPE in start function.
    
    This was made working with Splunk Enterprise Security - Incident Review.
    
    URL removed for security reasons. 
'''


import threading
import time
from gui import Ui_FAIL
from PyQt5.QtWidgets import QApplication, QMainWindow
import qdarkstyle
import ctypes
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        print('thread started')
        return thread
    return wrapper

class mainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(mainWindow, self).__init__()

        self.ui = Ui_FAIL()
        self.ui.setupUi(self)

        self.switchbot = False
        
        # Signals for the buttons.
        self.ui.checkBox.stateChanged.connect(self.keepalive)
        self.ui.pushButton.clicked.connect(self.splunkBotWrapper)
        self.ui.pushButton_2.clicked.connect(self.stopSplunkBot)


    def keepalive(self):
        if self.ui.checkBox.isChecked():
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
            print("Box on")
        else:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            print("box off")
    
    # The splunkBot has to have a wrapper function or else it starts running automatically whenever the program starts up.
    def splunkBotWrapper(self):
        self.splunkBot()

    def stopSplunkBot(self):
        
        self.switchbot = False
        print('Kill Switch')
        print(threading.active_count())

    @threaded
    def splunkBot(self):
        # This function is threaded since it can take a little while to run and their are sleeps in it, so that the gui will still be responsive.  
        # print(threading.active_count())
        runninglabel = self.ui.label_5
        runninglabel.setText('Running')
        runninglabel.setStyleSheet('color: red')


        username = self.ui.lineEdit_2.text()
        password = self.ui.lineEdit.text()
        
        self.switchbot = True
        
        
        while self.switchbot is True:
            runninglabel.setText('Running')
            
            chrome_options = webdriver.ChromeOptions()

            chrome_options.add_argument('--log-level=OFF')
            chrome_options.add_argument('--disable-gpu')
            
            if self.ui.checkBox_2.isChecked():
                chrome_options.add_argument('--headless')
            
            
            driver = webdriver.Chrome(options=chrome_options)  # Open the website
            action = ActionChains(driver)
        
            
            try:
                driver.get( ### URL Not included for security reasons ###)
           
                # Input the username and password because opening up Splunk this way forces you to enter credentials
                driver.find_element_by_id('username').send_keys(username)
                driver.find_element_by_id('password').send_keys(password)
                action.key_down(Keys.ENTER).key_up(Keys.ENTER).perform()

            except:
                driver.quit()
                print('Unable to find website or login error')
                self.switchbot = False
                break
                
            try:
                # This function waits for the page to finish loading and show complete
                loaded = WebDriverWait(driver, 60).until(EC.text_to_be_present_in_element((By.XPATH, "/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div/div/div[1]/div[1]/div/span[1]"), 'Complete'))
                editAllElement = driver.find_element_by_id('editAll')
                action.move_to_element(editAllElement)

                editAllElement.send_keys('\n')

                editIncident = driver.find_element_by_id('logReviewPopupModal')
                
                # These are actions to edit and move around the actual edit incident panel since most tag names and id's are very random in Splunk.
                action \
                    .move_to_element(editIncident) \
                    .send_keys(Keys.TAB) \
                    .pause(1) \
                    .send_keys(Keys.TAB) \
                    .pause(1) \
                    .send_keys(Keys.ENTER) \
                    .pause(1) \
                    .send_keys(Keys.DOWN) \
                    .pause(1) \
                    .send_keys(Keys.DOWN) \
                    .pause(1) \
                    .send_keys(Keys.ENTER) \
                    .pause(1) \
                    .send_keys(Keys.TAB) \
                    .send_keys(Keys.TAB) \
                    .send_keys(Keys.TAB) \
                    .send_keys(Keys.TAB) \
                    .send_keys(Keys.ENTER) \
                    .send_keys(Keys.TAB) \
                    .send_keys('WiP') \
                    .send_keys(Keys.TAB) \
                    .send_keys(Keys.TAB) \
                    .send_keys(Keys.ENTER) \
                    .perform()

                time.sleep(10)
                print('Claimed events')
                driver.quit()
                self.sleeptimer()
                
                
            except:
                time.sleep(3)
                print('No Events')
                self.ui.label_5.setText('Sleeping')
                driver.quit()
                self.sleeptimer()
             
                
        #print(threading.active_count())
        if self.switchbot is False:
            runninglabel2 = self.ui.label_5
            runninglabel2.setText('Not Running')
            runninglabel2.setStyleSheet('color: white')
            driver.quit()

    def sleeptimer(self):

        sleeptime = (self.ui.spinBox.value()*60)
        for i in range(sleeptime):
                    #print(sleeptime - i)
                    self.ui.label_5.setText('Sleeping ' + str(sleeptime - i))
                    sleeptime - 1
                    
                    if self.switchbot is False:
                        break
                    time.sleep(1)
                

        

if __name__ == '__main__':
    import sys

    #print(threading.active_count())
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    gui = mainWindow()
    gui.show()
    sys.exit(app.exec_())

