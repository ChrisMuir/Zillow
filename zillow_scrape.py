# -*- coding: utf-8 -*-

import time
import pandas as pd
from re import findall
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def init_driver():
    path_to_chromedriver = '~/chromedriver'
    driver = webdriver.Chrome(executable_path = path_to_chromedriver)
    driver.wait = WebDriverWait(driver, 10)
    return driver

def zillow(driver, search_terms):
    driver.get("http://www.zillow.com/homes")
    
    # Click the "Buy" button on the webpage.
    try:
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "nav-header")))
        button.click()
        time.sleep(10)
    except TimeoutException:
        print("Clicking the 'Buy' button failed")
    
    # Enters the search_terms into Zillow and executes search.
    try:
        searchBar = driver.wait.until(EC.presence_of_element_located(
            (By.ID, "citystatezip")))
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "zsg-icon-searchglass")))
        searchBar.send_keys(search_terms)
        time.sleep(5)
        button.click()
        time.sleep(10)
    except TimeoutException:
        print("search failed")
    

    # Pull the HTML from the search, which contains data on all the search results.
    # HTML from Zillow only displays info of the homes that are shown in the 
    # vertical list on the right side of the webpage (26 homes per page). 
    # The code below scrapes the HTML of the first set (26), then checks to see if there is a 
    # "Next" link at the bottom of the list, if so it clicks it and scrapes the HTML of the
    # the next page (again, 26 listings).  It keeps doing this until it no longer sees a 
    # "Next" link at the bottom.
    rawdata = []
    source = driver.page_source
    rawdata.append(source)    
    try:
        test = driver.find_element_by_class_name('zsg-pagination-next').is_displayed()
        while test == True:
            source = []            
            button = driver.wait.until(EC.element_to_be_clickable(
                (By.CLASS_NAME, 'zsg-pagination-next')))
            button.click()
            time.sleep(5)
            source = driver.page_source
            rawdata.append(source)
            try:
                test = driver.find_element_by_class_name('zsg-pagination-next').is_displayed()
            except:
                print(str(len(rawdata))+" pages of listings found")                
                break
    except:
        print(str(len(rawdata))+" page of listings found")
    urlRaw = driver.current_url
    driver.quit()
        
    
    # Split the HTML within rawdata into segments, one segment for each house listing.
    # First, find out how many listings the search result returned:    
    firstPages = (len(rawdata)-1)*26
    lastPage = rawdata[len(rawdata)-1].split('" id="zpid_')
    numListings = firstPages + (len(lastPage)-1)
    print(str(numListings)+" home listings scraped")    
    # Second, split the raw HTML into segments, one for each listing:
    listings = []
    for i in range(len(rawdata)):
        htmlSplit = rawdata[i].split('" id="zpid_')
        htmlSplit2 = htmlSplit[1:len(htmlSplit)]
        listings += htmlSplit2
    # Third, check to make sure the segmentation caught all the listings:
    checker = numListings == len(listings)
    if checker == False:
        print("warning, output will only contain info on"+str(len(listings))+" homes")
    
    
    # Create 11 variables from the scrapped HTML data.
    # These variables will make up the final output dataframe.
    
    
    # Street Address, City, State and zipcode
    # variables addressDF, cityDF, stateDF and zipcodeDF
    addressDF = []
    cityDF = []
    stateDF = []
    zipcodeDF = []
    for count in range(len(listings)):
        try:        
            addressSplit = listings[count].split('" data-address="', 1)
            address = addressSplit[1].split(', ', 1)[0]
        except:
            try:
                addressSplit = listings[count].split('Sign in for details (', 1)
                address = addressSplit[1].split(', ', 1)[0]
            except:
                address = "NA"
        
        try:
            city = addressSplit[1].split(str(address)+", ")[1].split(',', 1)[0]
        except:
            city = "NA"
        
        try:
            state = addressSplit[1].split(str(city)+", ")[1].split(' ', 1)[0]
            if len(state) > 2:
                state = addressSplit[1].split(str(city)+", ", 1)[1].split(')', 1)[0]
        except:
            state = "NA"
            
        try:
            zipcode = addressSplit[1].split(str(state)+" ")[1].split('"', 1)[0]
        except:
            zipcode = "NA"
        if len(address) > 50 or address == "null":
            address = "NA"
        if len(city) > 50 or city == "null":
            city = "NA"
        if len(state) > 3 or state == "null":
            state = "NA"
        if len(zipcode) > 6 or zipcode == "null":
            zipcode = "NA"
        addressDF.append(address)
        cityDF.append(city)
        stateDF.append(state)
        zipcodeDF.append(zipcode)
            
    # Price - variable priceDF
    priceDF = []
    for count in range(len(listings)):
        try:            
            price = listings[count].split('$', 1)[1]
            p2 = price.split('<', 1)[0]
            p2 = p2.replace(',', '')
            p2 = p2.replace('+', '')
            if len(p2) > 8:
                p2 = price.split('"', 1)[0]
                p2 = p2.replace(',', '')
                p2 = p2.replace('+', '')
            if len(p2) > 8:
                price = "NA"
            if ('K' in p2) == True:
                p2 = p2.split('K', 1)[0]
                p2 = str(p2)+"000"
            if ('M' in p2) == True:
                p2 = p2.split('M', 1)[0]
                if ('.' in p2) != True:
                    p2 = str(p2)+"000000"
                else:
                    mlen = len(p2.split('.')[0])
                    if mlen == 1:
                        pricelen = 7
                    else:
                        pricelen = 8
                    p2 = p2.replace('.', '')
                    diff = pricelen-len(p2)
                    p2 = str(p2)+(diff*'0')
        except:
            price = "NA"
        if len(p2) > 8 or len(p2) < 5 or p2 == "null":
            price = "NA"
        else:
            price = p2
        priceDF.append(price)
            
    # Square Footage - variable sqftDF
    sqftDF = []
    for count in range(len(listings)):
        try:
            sqft = listings[count].split(',"sqft":', 1)[1].split(',')[0]
        except:
            sqft = "NA"
        if len(sqft) > 8 or sqft == "null":
            sqft = "NA"
        sqftDF.append(sqft)
            
    # Number of bedrooms - variable bedroomsDF
    bedroomsDF = []
    for count in range(len(listings)):
        try:
            bedrooms = listings[count].split('{"bed":', 1)[1].split(',')[0]
        except:
            bedrooms = "NA"
        if len(bedrooms) > 4 or bedrooms == "null":
            bedrooms = "NA"
        bedroomsDF.append(bedrooms)
        
    # Number of bathrooms - variable bathroomsDF
    bathroomsDF = []
    for count in range(len(listings)):
        try:
            bathrooms = listings[count].split('bds', 1)[1].split('ba')[0]
            bathrooms = bathrooms.replace(' ', '')
            bathrooms = bathrooms[1:]
        except:
            bathrooms = "NA"
        if len(bathrooms) > 4 or bathrooms == "null":
            bathrooms = "NA"
        bathroomsDF.append(bathrooms)

    # Number of days on it's been listed on Zillow - variable daysonmarkDF
    daysonmarkDF = []    
    for count in range(len(listings)):
        try:
            dom = listings[count].split('days', 1)[0]
            dom = dom[-11:-1].split('>', 1)[1]
        except:
            dom = "NA"
        if len(dom) > 6 or dom == "null":
            dom = "NA"
        daysonmarkDF.append(dom)
            
    # Type of Listing - variable saletypeDF
    # Results should be "House for Sale", "Foreclosure", etc.
    saletypeDF = []
    answers = ['House For Sale', 'Condo For Sale', 'Foreclosure', 'New Construction', 'Townhouse For Sale', 
               'Apartment For Sale']    
    for count in range(len(listings)):
        try:
            for i in range(len(answers)):
                xyz = len(findall(answers[i], listings[count]))
                if xyz > 0:
                    saletype = answers[i]
                    break
                else:
                    saletype = "NA"
        except:
            saletype = "NA"
        if len(saletype) > 25 or saletype == "null":
            saletype = "NA"
        saletypeDF.append(saletype)
        
        
    # Listing URL - variable urlDF
    # Step one, extract the home ID for each listing:
    homeID = []
    for count in range(len(listings)):
        try:
            homeIDvect = listings[count].split('"', 1)[0]
        except:
            homeIDvect = "NA"
        homeID.append(homeIDvect)
    # Step two, use the individual home ID's to create a url string for each listing:
    urlDF = []
    if ('/any_days' in urlRaw) == True:
        url1 = 'http://www.zillow.com/homes/for_sale/'
        url3 = urlRaw[urlRaw.index('/any_days'):]
        for count in range(len(homeID)):
            if homeID[count] != "NA":        
                url2 = homeID[count]+'_zpid'
                url = [url1+url2+url3]
                urlDF += url
            else:
                url = "NA"
                urlDF.append(url)
    else:
        url1 = 'http://www.zillow.com/homes/for_sale/'
        url3 = '_zpid/any_days/globalrelevanceex_sort/29.759534,-95.335321,29.675003,-95.502863_rect/12_zm/'
        for count in range(len(homeID)):
            if homeID[count] != "NA":        
                url2 = homeID[count]
                url = [url1+url2+url3]
                urlDF += url
            else:
                url = "NA"
                urlDF.append(url)
            
            
    #Create a list of the column names, write the data to a dataframe.    
    columns = ['Address', 'City', 'State', 'Zip', 'Price', 'Sqft', 'bedrooms', 'bathrooms', 
               'days_on_zillow', 'sale_type', 'url']
        
    #Create the dataframe which will house the data for the final output.
    df = pd.DataFrame()
    df = pd.DataFrame.from_items([(columns[0], addressDF), 
                                  (columns[1], cityDF), 
                                  (columns[2], stateDF), 
                                  (columns[3], zipcodeDF), 
                                  (columns[4], priceDF), 
                                  (columns[5], sqftDF), 
                                  (columns[6], bedroomsDF), 
                                  (columns[7], bathroomsDF), 
                                  (columns[8], daysonmarkDF), 
                                  (columns[9], saletypeDF), 
                                  (columns[10], urlDF)])
        
    # Write "df" to a CSV file that is saved to your working directory.
    df.to_csv("zillow "+str(search_terms)+".csv", index=False)
