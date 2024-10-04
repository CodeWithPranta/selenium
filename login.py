import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    TimeoutException,
)
import time
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("script.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Bright Data Proxy Credentials
# Replace with your actual Bright Data proxy credentials
SBR_WEBDRIVER = 'https://brd-customer-hl_6d74c8bf-zone-scraping_browser1:b2xp0qn79kih@brd.superproxy.io:9515'

# User Credentials
EMAIL = 'florella16@awgarstone.com'
PASSWORD = 'Aj*@12345678$#'

def main():
    logging.info('Connecting to Scraping Browser with Data Proxy...')
    try:
        # Initialize Chrome Options
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        # Remove headless mode for debugging
        # options.add_argument('--headless')  # Uncomment to run in headless mode
        # Additional options to avoid detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        # Initialize Remote WebDriver with Bright Data's Scraping Browser
        logging.info('Initializing Remote WebDriver...')
        driver = webdriver.Remote(
            command_executor=SBR_WEBDRIVER,
            options=options
        )

        # Override the navigator.webdriver property to prevent detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })

        logging.info('Connected! Navigating to the login page...')
        login_url = 'https://visa.vfsglobal.com/aze/en/ltp/login'
        driver.get(login_url)

        # Capture screenshot after navigation
        try:
            driver.save_screenshot('after_navigation.png')
            logging.info("Screenshot taken: after_navigation.png")
        except Exception as e:
            logging.error(f"Error taking screenshot after navigation: {e}")

        wait = WebDriverWait(driver, 30)  # Increased wait time to 30 seconds

        # Accept cookies if prompted
        try:
            logging.info('Waiting for cookies acceptance button...')
            cookie_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[@id='onetrust-accept-btn-handler']")))
            cookie_button.click()
            logging.info("Cookies accepted.")
        except TimeoutException:
            logging.info("Cookies popup not found or failed to close.")
        except Exception as e:
            logging.error(f"Unexpected error when accepting cookies: {e}")

        # Capture screenshot after attempting to accept cookies
        try:
            driver.save_screenshot('after_cookies.png')
            logging.info("Screenshot taken: after_cookies.png")
        except Exception as e:
            logging.error(f"Error taking screenshot after cookies: {e}")

        # Wait for the login form to be visible using the provided XPath
        try:
            logging.info('Waiting for the login form to load...')
            login_form_xpath = "/html/body/app-root/div/div/app-login/section/div/div/mat-card/form"
            login_form = wait.until(EC.visibility_of_element_located(
                (By.XPATH, login_form_xpath)))
            logging.info("Login form is visible.")
        except TimeoutException:
            logging.error("Login form did not load as expected.")
            # Capture a screenshot for debugging
            driver.save_screenshot('login_form_not_loaded.png')
            sys.exit(1)  # Exit the script if login form is not loaded
        except Exception as e:
            logging.error(f"Unexpected error when waiting for login form: {e}")
            driver.save_screenshot('login_form_error.png')
            sys.exit(1)

        # Fill in the email field
        try:
            logging.info('Filling in the email field...')
            email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
            if email_field.is_displayed() and email_field.is_enabled():
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView(true);", email_field)
                time.sleep(1)  # Small delay to ensure scrolling has completed
                email_field.clear()
                email_field.send_keys(EMAIL)
                logging.info("Email field filled.")
            else:
                raise ElementNotInteractableException("Email field is not interactable.")
        except (NoSuchElementException, ElementNotInteractableException) as e:
            logging.error(f"Error locating or filling email field: {e}")
            driver.save_screenshot('error_filling_email.png')
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error when filling email field: {e}")
            driver.save_screenshot('error_filling_email_unexpected.png')
            sys.exit(1)

        # Fill in the password field
        try:
            logging.info('Filling in the password field...')
            password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
            if password_field.is_displayed() and password_field.is_enabled():
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView(true);", password_field)
                time.sleep(1)  # Small delay to ensure scrolling has completed
                password_field.clear()
                password_field.send_keys(PASSWORD)
                logging.info("Password field filled.")
            else:
                raise ElementNotInteractableException("Password field is not interactable.")
        except (NoSuchElementException, ElementNotInteractableException) as e:
            logging.error(f"Error locating or filling password field: {e}")
            driver.save_screenshot('error_filling_password.png')
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error when filling password field: {e}")
            driver.save_screenshot('error_filling_password_unexpected.png')
            sys.exit(1)

        # Submit the login form
        try:
            logging.info('Submitting the login form...')
            # Attempt multiple selectors for the submit button
            selectors = [
                (By.XPATH, "//button[contains(text(),'Login')]"),
                (By.XPATH, "//button[@type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
            ]
            submit_button = None
            for selector in selectors:
                try:
                    submit_button = wait.until(EC.element_to_be_clickable(selector))
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        break
                except TimeoutException:
                    continue

            if not submit_button:
                raise NoSuchElementException("Submit button not found with provided selectors.")

            # Scroll to the submit button
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)  # Small delay to ensure scrolling has completed

            submit_button.click()
            logging.info("Login form submitted.")
        except (NoSuchElementException, ElementNotInteractableException) as e:
            logging.error(f"Error locating or clicking submit button: {e}")
            driver.save_screenshot('error_submitting_form.png')
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error when submitting the form: {e}")
            driver.save_screenshot('error_submitting_form_unexpected.png')
            sys.exit(1)

        # Wait for redirection or confirmation of successful login
        try:
            logging.info('Waiting for redirection after login...')
            wait.until(EC.url_changes(login_url))
            logging.info("Login successful. Redirected to the next page.")
        except TimeoutException:
            logging.error("Error during login or redirection: Timeout waiting for URL to change.")
            driver.save_screenshot('error_post_login_timeout.png')
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error during login or redirection: {e}")
            driver.save_screenshot('error_post_login_unexpected.png')
            sys.exit(1)

        # Optionally, perform additional actions or scrape data
        # For demonstration, we'll print the current URL
        try:
            current_url = driver.current_url
            logging.info(f"Current URL after login: {current_url}")
        except Exception as e:
            logging.error(f"Error retrieving current URL: {e}")

        # Optionally, take a screenshot of the logged-in page
        try:
            screenshot_path = './logged_in_page.png'
            driver.get_screenshot_as_file(screenshot_path)
            logging.info(f"Screenshot taken and saved to {screenshot_path}.")
        except Exception as e:
            logging.error(f"Error taking screenshot: {e}")

    except Exception as e:
        logging.critical(f"Failed to connect to the Scraping Browser: {e}")

    finally:
        # Clean up and close the browser
        try:
            driver.quit()
            logging.info("Browser session ended.")
        except Exception as e:
            logging.error(f"Error closing the browser: {e}")

# Check if the script is executed directly
if __name__ == '__main__':
    main()
