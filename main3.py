import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import re

# TwoCaptcha API Key
API_KEY = 'd52fe3a0bd3f66413f3eef7f5ccb6449'

# Function to solve CAPTCHA using TwoCaptcha
def solve_captcha(site_key, url, captcha_type='userrecaptcha'):
    """
    Solves CAPTCHA using TwoCaptcha API.

    :param site_key: The site key for the CAPTCHA.
    :param url: The URL where the CAPTCHA is located.
    :param captcha_type: Type of CAPTCHA ('userrecaptcha' for reCAPTCHA, 'hcaptcha' for hCaptcha).
    :return: The CAPTCHA solution token.
    """
    print(f"Requesting CAPTCHA solution for site_key: {site_key} and url: {url}")
    
    # Prepare the data payload based on CAPTCHA type
    data = {
        'key': API_KEY,
        'method': captcha_type,
        'pageurl': url,
        'json': 1
    }
    
    if captcha_type == 'userrecaptcha':
        data['googlekey'] = site_key
    elif captcha_type == 'hcaptcha':
        data['sitekey'] = site_key
    else:
        raise ValueError("Unsupported CAPTCHA type.")
    
    # Send request to TwoCaptcha to initiate CAPTCHA solving
    response = requests.post("http://2captcha.com/in.php", data=data)
    result = response.json()
    print(f"TwoCaptcha in.php response: {result}")
    
    if result['status'] != 1:
        raise Exception(f"Error from 2Captcha: {result.get('request')}")
    
    captcha_id = result['request']
    
    # Poll for CAPTCHA solution
    for attempt in range(24):  # Wait up to 2 minutes
        time.sleep(5)
        res = requests.get(
            "http://2captcha.com/res.php",
            params={
                'key': API_KEY,
                'action': 'get',
                'id': captcha_id,
                'json': 1
            }
        )
        res_json = res.json()
        print(f"TwoCaptcha res.php response: {res_json}")
        
        if res_json['status'] == 1:
            print("CAPTCHA solved successfully.")
            return res_json['request']
        elif res_json['request'] == 'CAPCHA_NOT_READY':
            print("CAPTCHA not ready yet. Waiting...")
            continue
        else:
            raise Exception(f"Error from 2Captcha: {res_json.get('request')}")
    
    raise Exception("CAPTCHA solving timed out.")

# Initialize undetected_chromedriver
driver = uc.Chrome()

try:
    # Navigate to the login page
    url = 'https://visa.vfsglobal.com/aze/en/ltp/login'
    driver.get(url)

    # Wait for the page to load
    wait = WebDriverWait(driver, 20)

    # Accept cookies if prompted
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]")))
        cookie_button.click()
        print("Cookies accepted.")
    except Exception as e:
        print("Cookies popup not found or failed to close:", e)

    # Locate the CAPTCHA iframe to extract the site key
    try:
        # Adjust the XPath based on actual CAPTCHA type and page structure
        captcha_iframe = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
        ))
        src = captcha_iframe.get_attribute('src')
        print(f"CAPTCHA iframe src: {src}")
        
        # Extract the site_key using regex
        match = re.search(r'sitekey=([\w-]+)', src)
        if match:
            site_key = match.group(1)
            print(f"Extracted site_key: {site_key}")
        else:
            raise Exception("Could not find site_key in CAPTCHA iframe src.")
    except Exception as e:
        print("Error locating CAPTCHA site key:", e)
        driver.quit()
        exit(1)

    # Solve CAPTCHA using TwoCaptcha
    try:
        captcha_solution = solve_captcha(site_key, url, captcha_type='userrecaptcha')

        # Inject the CAPTCHA solution into the page
        # For reCAPTCHA, set the value of 'g-recaptcha-response' textarea
        driver.execute_script("""
            document.getElementById('g-recaptcha-response').style.display = 'block';
            document.getElementById('g-recaptcha-response').value = arguments[0];
        """, captcha_solution)
        print("CAPTCHA solved and submitted.")
        
        # Optionally, you might need to trigger an event to notify the page of the CAPTCHA solution
        driver.execute_script("""
            var event = new Event('change');
            document.getElementById('g-recaptcha-response').dispatchEvent(event);
        """)
    except Exception as e:
        print("Error solving CAPTCHA:", e)
        driver.quit()
        exit(1)

    # Locate the email input field
    try:
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys("florella16@awgarstone.com")
        print("Email field filled.")
    except Exception as e:
        print("Error locating email field:", e)
        driver.quit()
        exit(1)

    # Locate the password input field
    try:
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_field.send_keys("Aj*@12345678$#")
        print("Password field filled.")
    except Exception as e:
        print("Error locating password field:", e)
        driver.quit()
        exit(1)

    # Submit the form
    try:
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login')]")))
        submit_button.click()
        print("Form submitted.")
    except Exception as e:
        print("Error submitting form:", e)
        driver.quit()
        exit(1)

    # Wait for redirection to confirm login success
    try:
        wait.until(EC.url_changes(url))
        print("Login successful. Redirected to the next page.")
    except Exception as e:
        print("Error during redirection:", e)

finally:
    # Clean up by closing the browser
    driver.quit()
