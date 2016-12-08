"""
Zillow scraper functions, these are sourced at the top of zillow_runfile.py
"""

import time
import zipcode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

def zipcodes_list(st_items):
    if type(st_items) == str:
        zcObjects = zipcode.islike(st_items)
        output = []
        for i in zcObjects:
            output.append(str(i).split(" ", 1)[1].split(">")[0])
    elif type(st_items) == list:
        zcObjects = []
        for i in st_items:
            zcObjects = zcObjects + zipcode.islike(i)
        output = []
        for i in zcObjects:
            output.append(str(i).split(" ", 1)[1].split(">")[0])
    else:
        raise ValueError("input 'st_items' must be of type str or list")
    return(output)

def init_driver(filepath):
    driver = webdriver.Chrome(executable_path = filepath)
    driver.wait = WebDriverWait(driver, 10)
    return(driver)

def navigate_to_website(driver, site):
    driver.get(site)

def click_buy_button(driver):
    try:
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "nav-header")))
        button.click()
        time.sleep(10)
    except (TimeoutException, NoSuchElementException):
        raise ValueError("Clicking the 'Buy' button failed")

def enter_search_term(driver, search_term, k, numSearchTerms):
    try:
        searchBar = driver.wait.until(EC.presence_of_element_located(
            (By.ID, "citystatezip")))
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "zsg-icon-searchglass")))
        searchBar.clear()
        time.sleep(3)
        searchBar.send_keys(search_term)
        time.sleep(3)
        button.click()
        time.sleep(3)
        return(True)
    except (TimeoutException, NoSuchElementException):
        return(False)

def results_test(driver, search_term):
    try:
        no_results = driver.find_element_by_css_selector(
            '.zoom-out-message').is_displayed()
    except NoSuchElementException:
        no_results = False
    return(no_results)        

def get_html(driver):
    output = []
    keep_going = True
    while keep_going:
        # Pull page HTML
        output.append(driver.page_source)
        try:
            # Check to see if a "next page" link exists
            keep_going = driver.find_element_by_class_name(
                'zsg-pagination-next').is_displayed()
        except NoSuchElementException:
            keep_going = False
        if keep_going:
            # Test to ensure the "updating results" image isnt displayed.
            tries = 5
            try:
                cover = driver.find_element_by_class_name(
                    'list-loading-message-cover').is_displayed()
            except (TimeoutException, NoSuchElementException):
                cover = False
            while cover and tries > 0:
                time.sleep(5)
                tries -= 1
                try:
                    cover = driver.find_element_by_class_name(
                        'list-loading-message-cover').is_displayed()
                except (TimeoutException, NoSuchElementException):
                    cover = False
            # If 'cover' is False, click next page. If its True, give up on 
            # trying to click thru to the next page of house results.
            if cover == False:
                try:
                    driver.wait.until(EC.element_to_be_clickable(
                        (By.CLASS_NAME, 'zsg-pagination-next'))).click()
                    time.sleep(3)
                except TimeoutException:
                    keep_going = False
            else:
                keep_going = False
        #else:
            #print(str(len(output)) + " pages of listings found")
    return(output)

def get_listings(list_obj):
    # Split the HTML within rawdata into segments, one for each house listing.
    # Find out how many listings the search result returned:
    firstPages = (len(list_obj) - 1) * 26
    lastPage = list_obj[len(list_obj) - 1].split('" id="zpid_')
    numListings = firstPages + (len(lastPage) - 1)
    print(str(numListings)+" home listings scraped")
    # Split the raw HTML into segments, one for each listing:
    output = []
    for i in list_obj:
        htmlSplit = i.split('" id="zpid_')[1:]
        output += htmlSplit
    # Check to make sure the segmentation caught all the listings:
    if numListings != len(output):
        print("Warning: output will only contain info on " + 
              str(len(output)) + " homes")
    print("***")
    return(output)

def get_street_address(str_obj):
    try:
        addressSplit = str_obj.split('" data-address="', 1)
        address = addressSplit[1].split(', ', 1)[0]
    except IndexError:
        try:
            addressSplit = str_obj.split('Sign in for details (', 1)
            address = addressSplit[1].split(', ', 1)[0]
        except IndexError:
            addressSplit = 'NA'
            address = 'NA'
    if len(address) > 50 or address == 'null':
        address = 'NA'
    return(addressSplit, address)
    
def get_city(addressSplit, address):
    try:
        city = addressSplit[1].split(str(address) + ", ")[1].split(',', 1)[0]
    except IndexError:
        city = "NA"
    if len(city) > 50 or city == 'null':
        city = 'NA'
    return(city)

def get_state(addressSplit, city):
    try:
        state = addressSplit[1].split(str(city)+", ")[1].split(' ', 1)[0]
        if len(state) > 2:
            state = addressSplit[1].split(str(city)+", ", 1)[1].split(')', 1)[0]
    except IndexError:
        try:
            state = addressSplit[1].split(str(city)+", ", 1)[1].split(')', 1)[0]
        except IndexError:
            state = 'NA'
    if len(state) > 2 or state == 'null':
        state = 'NA'
    return(state)
    
def get_zipcode(addressSplit, state):
    try:
        zipcode = addressSplit[1].split(str(state)+" ")[1].split('"', 1)[0]
    except IndexError:
        zipcode = "NA"
    if len(zipcode) > 6 or zipcode == 'null':
        zipcode = 'NA'
    return(zipcode)

def get_price(str_obj):
    try:            
        price = str_obj.split('$', 1)[1].split('<', 1)[0]
    except IndexError:
        price = 'NA'
    if price != 'NA':
        p2 = price.replace(',', '')
        p2 = p2.replace('+', '')
        if len(price) > 8:
            p2 = price.split('"', 1)[0]
            p2 = p2.replace(',', '')
            p2 = p2.replace('+', '')
        if len(p2) > 8:
            price = 'NA'
        if ('K' in p2):
            p2 = p2.split('K', 1)[0]
            p2 = str(p2) + "000"
        if ('M' in p2):
            p2 = p2.split('M', 1)[0]
            if ('.' in p2) != True:
                p2 = str(p2) + "000000"
            else:
                mlen = len(p2.split('.')[0])
                if mlen == 1:
                    pricelen = 7
                else:
                    pricelen = 8
                p2 = p2.replace('.', '')
                diff = pricelen - len(p2)
                p2 = str(p2) + (diff * '0')
        if len(p2) > 8 or len(p2) < 5 or p2 == 'null':
            price = 'NA'
        else:
            price = p2
    return(price)

def get_sqft(str_obj):
    try:
        sqft = str_obj.split(',"sqft":', 1)[1].split(',')[0]
    except IndexError:
        sqft = 'NA'
    if len(sqft) > 8 or sqft == 'null':
        sqft = 'NA'
    return(sqft)

def get_bedrooms(str_obj):
    try:
        bedrooms = str_obj.split('{"bed":', 1)[1].split(',')[0]
    except IndexError:
        bedrooms = 'NA'
    if len(bedrooms) > 4 or bedrooms == 'null':
        bedrooms = 'NA'
    return(bedrooms)

def get_bathrooms(str_obj):
    try:
        bathrooms = str_obj.split(',"bath":', 1)[1].split('}')[0]
    except IndexError:
        bathrooms = 'NA'
    if len(bathrooms) > 5:
        bathrooms = bathrooms.split(',', 1)[0]
    if len(bathrooms) > 5 or bathrooms == 'null':
        bathrooms = 'NA'
    return(bathrooms)

def get_days_on_market(str_obj):
    try:
        dom = str_obj.split('days', 1)[0]
        dom = dom[-11:-1].split('>', 1)[1]
    except IndexError:
        dom = "NA"
    if len(dom) > 6 or dom == 'null':
        dom = "NA"
    return(dom)

def get_sale_type(str_obj):
    types = ['House For Sale', 'Condo For Sale', 'Foreclosure', 
    'New Construction', 'Townhouse For Sale', 'Apartment For Sale', 
    'Make Me Move', 'For Sale by Owner', 'Lot/Land For Sale', 'Co-op For Sale']
    saletype = 'NA'
    for i in range(len(types)):
        if types[i] in str_obj:
            saletype = types[i]
            break
    if len(saletype) > 19 or saletype == 'null':
        saletype = 'NA'
    return(saletype)

def get_url(str_obj):
    try:
        homeID = str_obj.split('"', 1)[0]
    except IndexError:
        homeID = 'NA'
    if len(homeID) < 13 and homeID != 'NA':
        url1 = 'http://www.zillow.com/homes/for_sale/'
        url3 = '_zpid/any_days/globalrelevanceex_sort/29.759534,-95.335321,' 
        url4 = '29.675003,-95.502863_rect/12_zm/'
        url = url1 + homeID + url3 + url4
    return(url)

def close_connection(driver):
    driver.quit()
