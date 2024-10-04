from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By

AUTH = 'USER:PASS'
SBR_WEBDRIVER = f'https://brd-customer-hl_6d74c8bf-zone-scraping_browser1:b2xp0qn79kih@brd.superproxy.io:9515'

def main():
    print('Connecting to Scraping Browser...')
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
    
    # Initialize Remote WebDriver
    with Remote(sbr_connection, options=ChromeOptions()) as driver:
        print('Connected! Navigating...')
        
        # Navigate to the URL
        driver.get('https://visa.vfsglobal.com/aze/en/ltp/login')

        # CAPTCHA handling
        # print('Waiting captcha to solve.....')

        # solve_res = driver.execute('executeCdpCommand', {
        #     'cmd': 'Captcha.waitForSolve',
        #     'params': {'detectTimeout': 10000},
        # })

        # print('Captcha solve status:', solve_res['value']['status'])
        
        # Take screenshot
        # print('Taking page screenshot to file page.png')
        # driver.get_screenshot_as_file('./page.png')
        
        # Scrape page content
        print('Navigated! Scraping page content...')
        html = driver.page_source
        print(html)

# Check if the script is executed directly
if __name__ == '__main__':
    main()
