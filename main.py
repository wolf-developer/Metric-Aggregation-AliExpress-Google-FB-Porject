#import requests
#from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
from time import sleep
import pandas as pd
from pytrends.request import TrendReq

class Scrape:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.data = {}
        pass

    def scrape(self, url):
        self._scrapeFacebook(url)

    def _scrapeFacebook(self, url):
        self.driver.get(url)
        sleep(1)
        element = self.driver.find_element_by_class_name('_8gvk')
        product_name = self._removeParenthases(element.text)
        self.data["Product Name"] = product_name
        self.data["Link"] = url
        element = self.driver.find_element_by_class_name('_81hb')
        self.data['Likes'] = element.text
        element = self.driver.find_element_by_class_name('_355t')
        self.data['Shares'] = element.text
        element = self.driver.find_element_by_class_name('timestampContent')
        self.data['Video upload date'] = element.text

        self._findOnAliexpress(product_name)
        self._getGoogleTrendsStatistics(product_name)

    def _findOnAliexpress(self, product_name):
        self.driver.get('https://www.aliexpress.com/wholesale?SearchText=' + product_name)
        sleep(1)
        element = self.driver.find_element_by_class_name('_9tla3')
        href = element.get_attribute('href')
        self.driver.get(href)
        sleep(1)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)
        element = self.driver.find_element_by_xpath('//span[contains(text(), "SPECIFICATIONS")]')
        element.click()
        sleep(1)
        element = self.driver.find_element_by_class_name('child-node')
        self.data['Product Category'] = element.text.strip()
        element = self.driver.find_elements_by_class_name('product-prop')
        for el in element:
            property_title = el.find_element_by_class_name('property-title').text.strip()
            property_value = el.find_element_by_class_name('property-desc').text.strip()
            if property_title == 'Size:':
                self.data['Product Dimensions'] = property_value
            elif property_title == 'Brand Name:':
                self.data['Product Brand'] = property_value
            elif property_title == 'Weight:':
                self.data['Product Weight'] = property_value
        element = self.driver.find_element_by_class_name('overview-rating-average')
        self.data['Customer Review Rating'] = element.text.strip()
        element = self.driver.find_element_by_class_name('product-price-value')
        self.data['Product Price'] = element.text.strip()
        element = self.driver.find_element_by_class_name('product-shipping-price')
        self.data['Shipping Price'] = element.text.strip()

    def _getGoogleTrendsStatistics(self, product_name):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[product_name], cat=0, timeframe='today 3-m', geo='', gprop='')
        df = pytrend.interest_over_time()
        mean = df[product_name].mean()
        median = df[product_name].median()
        maximum = df[product_name].idxmax()
        minimum = df[product_name].idxmin()
        self.data['Date of minimum search '] = minimum
        self.data['Date of maximum search '] = maximum
        self.data['Median search '] = median
        self.data['Average search '] = mean

    def _removeParenthases(self, text):
        return re.sub("[\(\[].*?[\)\]]", "", text)


scrape = Scrape()
scrape.scrape('https://www.facebook.com/Semiwels-Fashion-566790340492329/videos/501525527167675/')
#scrape._findOnAliexpress('Spice Organizer Rack')
#scrape._getGoogleTrendsStatistics('Spice Organizer Rack')

print(scrape.data)
