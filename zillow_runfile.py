# -*- coding: utf-8 -*-
'''
WARNING: Use this code at your own risk, scraping is against Zillow's TOC.

Zillow home listings scraper, using Selenium.  The code takes as input search 
terms that would normally be entered on the Zillow home page.  It creates 11 
variables on each home listing from the data, saves them to a data frame, 
and then writes the df to a CSV file that gets saved to your working directory.

Software requirements/info:
- This code was written using Python 3.5.
- Scraping is done with Selenium v3.0.2, which can pip installed, or downloaded
  here: http://www.seleniumhq.org/download/
- The selenium package requires a webdriver program. This code was written 
  using Chromedriver v2.25, which can be downloaded here: 
  https://sites.google.com/a/chromium.org/chromedriver/downloads
  
'''

import time
import pandas as pd
from bs4 import BeautifulSoup
import Zillow.zillow_functions as zl

# Create list of search terms.
# Function zipcodes_list() creates a list of US zip codes that will be 
# passed to the scraper. For example, st = zipcodes_list(["10", "11", "606"])  
# will yield every US zip code that begins with "10", begins with "11", or 
# begins with "606", as a list object.
# I recommend using zip codes, as they seem to be the best option for catching
# as many house listings as possible. If you want to use search terms other 
# than zip codes, simply skip running zipcodes_list() function below, and add 
# a line of code to manually assign values to object st, for example:
# st = ["Chicago", "New Haven, CT", "77005", "Jacksonville, FL"]
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

# Get total number of search terms.
num_search_terms = len(st)

# Initialize list obj that will house all scraped data.
output_data = []

# Start the scraping.
for idx, term in enumerate(st):
    # Enter search term and execute search.
    if zl.enter_search_term(driver, term):
        print("Entering search term %s of %s" % 
              (str(idx + 1), str(num_search_terms)))
    else:
        print("Search term %s failed, moving on to next search term\n***" % 
              str(idx + 1))
        continue

    # Check to see if any results were returned from the search.
    # If there were none, move onto the next search.
    if zl.results_test(driver):
        print("Search %s returned zero results. Moving on to next search\n***" %
              str(term))
        continue

    # Pull the html for each page of search results. Zillow caps results at 
    # 20 pages, each page can contain 26 home listings, thus the cap on home 
    # listings per search is 520.
    raw_data = zl.get_html(driver)
    print("%s pages of listings found" % str(len(raw_data)))

    # Take the extracted HTML and split it up by individual home listings.
    listings = zl.get_listings(raw_data)

    # For each home listing, extract the 11 variables that will populate that 
    # specific observation within the output dataframe.
    for home in listings:
        soup = BeautifulSoup(home, "lxml")
        new_obs = []

        # List that contains number of beds, baths, and total sqft (and 
        # sometimes price as well).
        card_info = zl.get_card_info(soup)

        # Street Address
        new_obs.append(zl.get_street_address(soup))
        
        # City
        new_obs.append(zl.get_city(soup))
        
        # State
        new_obs.append(zl.get_state(soup))
        
        # Zipcode
        new_obs.append(zl.get_zipcode(soup))
        
        # Price
        new_obs.append(zl.get_price(soup, card_info))
        
        # Sqft
        new_obs.append(zl.get_sqft(card_info))
        
        # Bedrooms
        new_obs.append(zl.get_bedrooms(card_info))
        
        # Bathrooms
        new_obs.append(zl.get_bathrooms(card_info))
        
        # Days on the Market/Zillow
        new_obs.append(zl.get_days_on_market(soup))
        
        # Sale Type (House for Sale, New Construction, Foreclosure, etc.)
        new_obs.append(zl.get_sale_type(soup))
        
        # URL for each house listing
        new_obs.append(zl.get_url(soup))
        
        # Append new_obs to list output_data.
        output_data.append(new_obs)

# Close the webdriver connection.
zl.close_connection(driver)

# Write data to data frame, then to CSV file.
file_name = "%s_%s.csv" % (str(time.strftime("%Y-%m-%d")), 
                           str(time.strftime("%H%M%S")))
columns = ["address", "city", "state", "zip", "price", "sqft", "bedrooms", 
           "bathrooms", "days_on_zillow", "sale_type", "url"]
pd.DataFrame(output_data, columns = columns).to_csv(file_name, index = False)
