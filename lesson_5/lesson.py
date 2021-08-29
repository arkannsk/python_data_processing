from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from pymongo import MongoClient
import json

chrome_options = Options()
chrome_options.add_argument('--start-maximized')

driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)

driver.get('https://www.mvideo.ru')

button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.c-btn_close.font-icon.icon-delete')))
button.click()

element = driver.find_element_by_xpath("//h2[contains(text(), 'Новинки')][1]")

actions = ActionChains(driver)
actions.move_to_element(element).perform()
# just for visibility
driver.execute_script('arguments[0].scrollIntoView(true);', element)

root_section = element.find_element_by_xpath(".//..//..//..//..//div[@class='section']")
next_button = root_section.find_element_by_xpath(".//a[contains(@class, 'next-btn')]")

while next_button.is_displayed():
    next_button.click()

links = root_section.find_elements_by_xpath(".//a[contains(@class, 'fl-product-tile-title__link')]")

result = []
for link in links:
    data = json.loads(link.get_attribute('data-product-info'))
    if data is not None:
        result.append(data)

client = MongoClient('localhost', 27017, username='root', password='password')
db = client['test_database']
db.mvideo.drop()

collection = db.mvideo
collection.insert_many(result)

client.close()
