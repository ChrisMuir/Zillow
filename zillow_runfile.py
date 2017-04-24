# -*- coding: utf-8 -*-
'''
WARNING: Use this code at your own risk, scraping is against Zillow's TOC.

Zillow home listings scraper, using Selenium.  The code takes as input search 
terms that would normally be entered on the Zillow home page.  It creates 11 
variables on each home listing from the data, saves them to a data frame, 
and then writes the df to a CSV file that gets saved to your working directory.

Software requirements/info:
- This code was written using Python 3.5.
- Scraping is done with Selenium v3.0.2, which can be downloaded here: 
  http://www.seleniumhq.org/download/
- The selenium package requires a webdriver program. This code was written 
  using Chromedriver v2.25, which can be downloaded here: 
  https://sites.google.com/a/chromium.org/chromedriver/downloads
  
'''

import time
import pandas as pd
import zillow_functions as zl
from bs4 import BeautifulSoup

# Create list of search terms.
# Function zipcodes_list() creates a list of US zip codes that will be 
# passed to the scraper. For example, st = zipcodes_list(['10', '11', '606'])  
# will yield every US zip code that begins with '10', begins with "11", or 
# begins with "606" as a single list.
# I recommend using zip codes, as they seem to be the best option for catching
# as many house listings as possible. If you want to use search terms other 
# than zip codes, simply skip running zipcodes_list() function below, and add 
# a line of code to manually assign values to object st, for example:
# st = ['Chicago', 'New Haven, CT', '77005', 'Jacksonville, FL']
# Keep in mind that, for each search term, the number of listings scraped is 
# capped at 520, so in using a search term like "Chicago" the scraper would 
# end up missing most of the results.
# Param st_items can be either a list of zipcode strings, or a single zipcode 
# string.
st = zl.zipcodes_list(st_items = ["100", "770"])

# Initialize the webdriver.
driver = zl.init_driver("C:/Users/username/chromedriver.exe")

# Go to www.zillow.com/homes
zl.navigate_to_website(driver, "http://www.zillow.com/homes")

# Click the "buy" button.
zl.click_buy_button(driver)

# Create 11 variables from the scrapped HTML data.
# These variables will make up the final output dataframe.
df = pd.DataFrame({'address' : [], 
                   'bathrooms' : [], 
                   'bedrooms' : [], 
                   'city' : [], 
                   'days_on_zillow' : [], 
                   'price' : [], 
                   'sale_type' : [], 
                   'state' : [], 
                   'sqft' : [], 
                   'url' : [], 
                   'zip' : []})

# Get total number of search terms.
num_search_terms = len(st)

# Start the scraping.
for k in range(num_search_terms):
    # Define search term (must be str object).
    search_term = st[k]

    # Enter search term and execute search.
    if zl.enter_search_term(driver, search_term):
        print("Entering search term number " + str(k+1) + 
              " out of " + str(num_search_terms))
    else:
        print("Search term " + str(k+1) + 
              " failed, moving onto next search term\n***")
        continue
    
    # Check to see if any results were returned from the search.
    # If there were none, move onto the next search.
    if zl.results_test(driver):
        print("Search " + str(search_term) + 
              " returned zero results. Moving onto the next search\n***")
        continue
    
    # Pull the html for each page of search results. Zillow caps results at 
    # 20 pages, each page can contain 26 home listings, thus the cap on home 
    # listings per search is 520.
    raw_data = zl.get_html(driver)
    print(str(len(raw_data)) + " pages of listings found")
    
    # Take the extracted HTML and split it up by individual home listings.
    listings = zl.get_listings(raw_data)
    
    # For each home listing, extract the 11 variables that will populate that 
    # specific observation within the output dataframe.
    for n in range(len(listings)):
        soup = BeautifulSoup(listings[n], "lxml")
        new_obs = []
        
        # List that contains number of beds, baths, and total sqft (and 
        # sometimes price as well).
        card_info = zl.get_card_info(soup)
        
        # Street Address
        new_obs.append(zl.get_street_address(soup))
        
        # Bathrooms
        new_obs.append(zl.get_bathrooms(card_info))
        
        # Bedrooms
        new_obs.append(zl.get_bedrooms(card_info))
        
        # City
        new_obs.append(zl.get_city(soup))
        
        # Days on the Market/Zillow
        new_obs.append(zl.get_days_on_market(soup))
        
        # Price
        new_obs.append(zl.get_price(soup, card_info))
        
        # Sale Type (House for Sale, New Construction, Foreclosure, etc.)
        new_obs.append(zl.get_sale_type(soup))
        
        # Sqft
        new_obs.append(zl.get_sqft(card_info))
        
        # State
        new_obs.append(zl.get_state(soup))
        
        # URL for each house listing
        new_obs.append(zl.get_url(soup))
        
        # Zipcode
        new_obs.append(zl.get_zipcode(soup))
    
        # Append new_obs to df as a new observation
        if len(new_obs) == len(df.columns):
            df.loc[len(df.index)] = new_obs

# Close the webdriver connection.
zl.close_connection(driver)

# Write df to CSV.
columns = ['address', 'city', 'state', 'zip', 'price', 'sqft', 'bedrooms', 
           'bathrooms', 'days_on_zillow', 'sale_type', 'url']
df = df[columns]
dt = time.strftime("%Y-%m-%d") + "_" + time.strftime("%H%M%S")
file_name = str(dt) + ".csv"
df.to_csv(file_name, index = False)
