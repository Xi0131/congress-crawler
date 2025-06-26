from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up Selenium WebDriver (Chrome)
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode (no GUI)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Visit the target site
driver.get("https://ivod.ly.gov.tw/Demand?targetSession=current")
time.sleep(3)  # Give time to load

with open('source.html', 'w', encoding='utf-8') as src:
    src.write(driver.page_source)

legislators_lists = driver.find_elements(By.CLASS_NAME, "table-list")
with open('tmp.txt', 'w', encoding='utf-8') as tmp:
    tmp.write(str(legislators_lists))

print("legislators:")
for legislators_list in legislators_lists:
    legislators = legislators_list.find_elements(By.TAG_NAME, "li")
    for legislator in legislators:
        print("-", legislator.get_attribute("a href"))

# Close the browser
driver.quit()
