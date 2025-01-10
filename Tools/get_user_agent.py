from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')

# Create a new Chrome driver instance
driver = webdriver.Chrome(options=chrome_options)

# Get the user agent
user_agent = driver.execute_script("return navigator.userAgent")
print("Your Chrome User Agent:", user_agent)

# Don't forget to close the driver
driver.quit() 