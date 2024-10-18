from selenium import webdriver 
from selenium.webdriver.common.by import By
from scrapy_selenium import SeleniumRequest
# driver.find_element(By.CLASS_NAME, 'event-item')

def parse(response):
    #driver = response.meta['driver']  # Get the Selenium WebDriver
    # Extract initial events listed on the page
    list = response.css('.lw_cal_event_list')
    print(list)

url = 'https://events.cmu.edu/'
SeleniumRequest(url=url, callback=parse)

# list = t.find_element(By.CLASS_NAME, 'lw_cal_event_list')
# print(button)
# button = browser.find_element_by_class_name('lw_cal_next') 
# button.click()