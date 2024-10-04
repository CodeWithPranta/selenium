from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import undetected_chromedriver as uc


# service = Service(executable_path="chromedriver.exe")
# driver = webdriver.Chrome(service=service)

driver = uc.Chrome()
driver.get('https://visa.vfsglobal.com/aze/en/ltp/login')

# Wait for the page to load
wait = WebDriverWait(driver, 20)

# Accept cookies if prompted
try:
    cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]")))
    cookie_button.click()
    print("Cookies accepted.")
except Exception as e:
    print("Cookies popup not found or failed to close:", e)

# input_element = driver.find_element(By.CLASS_NAME, 'gLFyf')
# input_element.send_keys('tech with tim' + Keys.ENTER)

time.sleep(10)

driver.quit()
