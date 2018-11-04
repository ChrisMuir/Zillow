# -*- coding: utf-8 -*-
# Zillow scraper functions, these are sourced at the top of zillow_runfile.py

import re as re
import numpy as np
import time
import zipcode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

def zipcodes_list(st_items):
    # If st_items is a single zipcode string.
    if isinstance(st_items, str):
        zc_objects = zipcode.islike(st_items)
    # If st_items is a list of zipcode strings.
    elif isinstance(st_items, list):
        zc_objects = [n for i in st_items for n in zipcode.islike(str(i))]
    else:
        raise ValueError("arg 'st_items' must be of type str or list")
    
    output = [str(i).split(" ", 1)[1].split(">")[0] for i in zc_objects]
    return(output)

def init_driver(file_path):
    # Starting maximized fixes https://github.com/ChrisMuir/Zillow/issues/1
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(executable_path=file_path, 
                              chrome_options=options)
    driver.wait = WebDriverWait(driver, 10)
    return(driver)

# Helper function for checking for the presence of a web element.
def _is_element_displayed(driver, elem_text, elem_type):
    if elem_type == "class":
        try:
            out = driver.find_element_by_class_name(elem_text).is_displayed()
        except (NoSuchElementException, TimeoutException):
            out = False
    elif elem_type == "css":
        try:
            out = driver.find_element_by_css_selector(elem_text).is_displayed()
        except (NoSuchElementException, TimeoutException):
            out = False
    else:
        raise ValueError("arg 'elem_type' must be either 'class' or 'css'")
    return(out)

# If captcha page is displayed, this function will run indefinitely until the 
# captcha page is no longer displayed (checks for it every 30 seconds).
# Purpose of the function is to "pause" execution of the scraper until the 
# user has manually completed the captcha requirements.
def _pause_for_captcha(driver):
    while True:
        time.sleep(30)
        if not _is_element_displayed(driver, "captcha-container", "class"):
            break

# Check to see if the page is currently stuck on a captcha page. If so, pause 
# the scraper until user has manually completed the captcha requirements.
def check_for_captcha(driver):
    if _is_element_displayed(driver, "captcha-container", "class"):
        print("\nCAPTCHA!\n"\
              "Manually complete the captcha requirements.\n"\
              "Once that's done, if the program was in the middle of scraping "\
              "(and is still running), it should resume scraping after ~30 seconds.")
        _pause_for_captcha(driver)

def navigate_to_website(driver, site):
    driver.get(site)
    # Check to make sure a captcha page is not displayed.
    check_for_captcha(driver)

def click_buy_button(driver):
    try:
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "nav-header")))
        button.click()
        time.sleep(10)
    except (TimeoutException, NoSuchElementException):
        raise ValueError("Clicking the 'Buy' button failed")
    # Check to make sure a captcha page is not displayed.
    check_for_captcha(driver)

def enter_search_term(driver, search_term):
    if not isinstance(search_term, str):
        search_term = str(search_term)
    try:
        search_bar = driver.wait.until(EC.presence_of_element_located(
            (By.ID, "citystatezip")))
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "zsg-icon-searchglass")))
        search_bar.clear()
        time.sleep(3)
        search_bar.send_keys(search_term)
        time.sleep(3)
        button.click()
        time.sleep(3)
        return(True)
    except (TimeoutException, NoSuchElementException):
        return(False)
    # Check to make sure a captcha page is not displayed.
    check_for_captcha(driver)

def test_for_no_results(driver):
    # Check to see if the "zoom out" msg exists (an indication that no results
    # were returned from the search).
    no_results = _is_element_displayed(driver, ".zoom-out-message", "css")
    # If the zoom-out msg is not displayed, check for "invalid zip" msg.
    if not no_results:
        no_results = _is_element_displayed(driver, "zsg-icon-x-thick", "class")
    # Check to make sure a captcha page is not displayed.
    check_for_captcha(driver)
    return(no_results)

def get_html(driver):
    output = []
    keep_going = True
    while keep_going:
        # Pull page HTML
        try:
            output.append(driver.page_source)
        except TimeoutException:
            pass
        # Check to see if a "next page" link exists.
        keep_going = _is_element_displayed(driver, "zsg-pagination-next", 
                                           "class")
        if keep_going:
            # Test to ensure the "updating results" image isnt displayed. 
            # Will try up to 5 times before giving up, with a 5 second wait 
            # between each try.             
            tries = 5
            cover = _is_element_displayed(driver, 
                                          "list-loading-message-cover", 
                                          "class")
            while cover and tries > 0:
                time.sleep(5)
                tries -= 1
                cover = _is_element_displayed(driver, 
                                              "list-loading-message-cover", 
                                              "class")
            # If the "updating results" image is confirmed to be gone 
            # (cover == False), click next page. Otherwise, give up on trying 
            # to click thru to the next page of house results, and return the 
            # results that have been scraped up to the current page.
            if not cover:
                try:
                    driver.wait.until(EC.element_to_be_clickable(
                        (By.CLASS_NAME, "zsg-pagination-next"))).click()
                    time.sleep(3)
                    # Check to make sure a captcha page is not displayed.
                    check_for_captcha(driver)
                except TimeoutException:
                    keep_going = False
            else:
                keep_going = False
    return(output)

# Teardown webdriver.
def close_connection(driver):
    driver.quit()

# Split the raw page source into segments, one for each home listing.
def get_listings(list_obj):
    output = []
    for i in list_obj:
        htmlSplit = i.split('" id="zpid_')[1:]
        output += htmlSplit
    return(output)

# Set of functions to extract specific data from an input html string.
class html_parser:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, "lxml")
        self.card_info = self.get_card_info()
    
    # For most listings, card_info will contain info on number of bedrooms, 
    # number of bathrooms, square footage, and sometimes price.
    def get_card_info(self):
        try:
            card = self.soup.find(
                "span", {"class" : "zsg-photo-card-info"}).get_text().split(u" \xb7 ")
        except (ValueError, AttributeError):
            card = np.nan
        if self._is_empty(card):
            card = np.nan
        return(card)
    
    def get_street_address(self):
        try:
            street = self.soup.find(
                "span", {"itemprop" : "streetAddress"}).get_text().strip()
        except (ValueError, AttributeError):
            street = np.nan
        if self._is_empty(street):
            street = np.nan
        return(street)
    
    def get_city(self):
        try:
            city = self.soup.find(
                "span", {"itemprop" : "addressLocality"}).get_text().strip()
        except (ValueError, AttributeError):
            city = np.nan
        if self._is_empty(city):
            city = np.nan
        return(city)
    
    def get_state(self):
        try:
            state = self.soup.find(
                "span", {"itemprop" : "addressRegion"}).get_text().strip()
        except (ValueError, AttributeError):
            state = np.nan
        if self._is_empty(state):
            state = np.nan
        return(state)
    
    def get_zipcode(self):
        try:
            zipcode = self.soup.find(
                "span", {"itemprop" : "postalCode"}).get_text().strip()
        except (ValueError, AttributeError):
            zipcode = np.nan
        if self._is_empty(zipcode):
            zipcode = np.nan
        return(zipcode)
    
    def get_price(self):
        price = np.nan
        # Look for price within the BeautifulSoup object.
        try:
            price = self.soup.find(
                "span", {"class" : "zsg-photo-card-price"}).get_text().strip()
        except (ValueError, AttributeError):
            if not self._is_empty(self.card_info):
                # If that fails, look for price within card_info.
                try:
                    price = [n for n in self.card_info 
                                 if any(["$" in n, "K" in n, "k" in n])]
                    if len(price) > 0:
                        price = price[0].split(" ")
                        price = [n for n in price if re.search("\d", n)]
                        if len(price[0]) > 0:
                            price = price[0]
                        else:
                            price = np.nan
                    else:
                        price = np.nan
                except (ValueError, AttributeError):
                    price = np.nan
        if not self._is_empty(price):
            # Transformations to the price string.
            price = price.replace(",", "").replace("+", "").replace("$", "").lower()
            if "k" in price:
                price = price.split("k")[0].strip()
                price = price + "000"
            if "m" in price:
                price = price.split("m")[0].strip()
                if "." not in price:
                    price = price + "000000"
                else:
                    pricelen = len(price.split(".")[0]) + 6
                    price = price.replace(".", "")
                    price = price + ((pricelen - len(price)) * "0")
            if self._is_empty(price):
                price = np.nan
        else:
            price = np.nan
        return(price)
    
    def get_sqft(self):
        sqft = [n for n in self.card_info if "sqft" in n]
        if len(sqft) > 0:
            try:
                sqft = float(
                    sqft[0].split("sqft")[0].strip().replace(",", "").replace("+", "")
                )
            except (ValueError, IndexError):
                sqft = np.nan
            if sqft == 0:
                sqft = np.nan
        else:
            sqft = np.nan
        return(sqft)
    
    def get_bedrooms(self):
        beds = [n for n in self.card_info if any(["bd" in n, "tudio" in n])]
        if len(beds) > 0:
            beds = beds[0].lower()
            if beds == "studio":
                return(0.0)
            try:
                beds = float(beds.split("bd")[0].strip())
            except (ValueError, IndexError):
                beds = np.nan
        else:
            beds = np.nan
        return(beds)
    
    def get_bathrooms(self):
        baths = [n for n in self.card_info if "ba" in n]
        if len(baths) > 0:
            try:
                baths = float(baths[0].split("ba")[0].strip())
            except (ValueError, IndexError):
                baths = np.nan
            if baths == 0:
                baths = np.nan
        else:
            baths = np.nan
        return(baths)
    
    def get_days_on_market(self):
        try:
            dom = self.soup.find_all(
                "ul", {"class" : "zsg-list_inline zsg-photo-card-badge"})
            if dom is not None:
                dom = [n.get_text().strip().lower() for n in dom]
                dom = [n for n in dom if "zillow" in n]
                if len(dom) > 0:
                    dom = int(dom[0].split(" ")[0])
                else:
                    dom = np.nan
            else:
                dom = np.nan
        except (ValueError, AttributeError):
            dom = np.nan
        return(dom)
    
    def get_sale_type(self):
        try:
            sale_type = self.soup.find(
                "span", {"class" : "zsg-photo-card-status"}).get_text().strip()
        except (ValueError, AttributeError):
            sale_type = np.nan
        if self._is_empty(sale_type):
            sale_type = np.nan
        return(sale_type)
    
    def get_url(self):
        # Try to find url in the BeautifulSoup object.
        href = [n["href"] for n in self.soup.find_all("a", href = True)]
        url = [i for i in href if "homedetails" in i]
        if len(url) > 0:
            url = "http://www.zillow.com/homes/for_sale/" + url[0]
        else:
            # If that fails, contruct the url from the zpid of the listing.
            url = [i for i in href if "zpid" in i and "avorite" not in i]
            if len(url) > 0:
                zpid = re.findall(r"\d{8,10}", url[0])
                if zpid is not None and len(zpid) > 0:
                    url = "http://www.zillow.com/homes/for_sale/" \
                            + str(zpid[0]) \
                            + "_zpid/any_days/globalrelevanceex_sort/29.759534," \
                            + "-95.335321,29.675003,-95.502863_rect/12_zm/"
                else:
                    url = np.nan
            else:
                url = np.nan
        return(url)
    
    # Helper function for testing if an object is "empty" or not.
    def _is_empty(self, obj):
        if isinstance(obj, float) and np.isnan(obj):
            return(True)
        if any([len(obj) == 0, obj == "null"]):
            return(True)
        else:
            return(False)
