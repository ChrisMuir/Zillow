'''
WARNING: Use this code at your own risk, scraping is against Zillow's TOC.

Zillow home listings scraper, using Selenium.  The code takes as input search 
terms that would normally be entered on the Zillow home page.  It creates 11 
variables on each home listing from the data, saves them to a data frame, 
and then writes the df to a CSV file that gets saved to your working directory.

Software requirements/info:
- This code was written using Python 3.5.
- Scraping is done with Selenium v3.0.1, which can be downloaded here: 
  http://www.seleniumhq.org/download/
- The selenium package requires a webdriver program. This code was written 
  using Chromedriver v2.25, which can be downloaded here: 
  https://sites.google.com/a/chromium.org/chromedriver/downloads
  
'''

import time
import pandas as pd
import zillow_functions as zl

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
st = zl.zipcodes_list(st_items = ['100', '770'])

# Initialize the webdriver.
driver = zl.init_driver('C:/Users/username/My Documents/chromedriver')

# Go to www.zillow.com/homes
zl.navigate_to_website(driver, "http://www.zillow.com/homes")

# Click the "buy" button.
zl.click_buy_button(driver)

# Create 11 variables from the scrapped HTML data.
# These variables will make up the final output dataframe.
df = pd.DataFrame({'address' : [], 
                   'city' : [], 
                   'state' : [], 
                   'zip' : [], 
                   'price' : [], 
                   'sqft' : [], 
                   'bedrooms' : [], 
                   'bathrooms' : [], 
                   'days_on_zillow' : [], 
                   'sale_type' : [], 
                   'url' : []})

# Establish variable that will keep count of the number of rows of the final 
# output df as it grows during the loop.
count = 0

# Get total number of search terms.
numSearchTerms = len(st)

for k in range(numSearchTerms):
    # Define search term (must be str object).
    search_term = st[k]

    # Enter search term and execute search.
    if zl.enter_search_term(driver, search_term, k, numSearchTerms):
        print("Entering search term number " + str(k+1) + 
              " out of " + str(numSearchTerms))
    elif zl.enter_search_term(driver, search_term, k, numSearchTerms) == False:
        print("Search term " + str(k+1) + 
              " failed, moving onto next search term")
        continue
    
    # Check to see if any results were returned from the search.
    # If there were none, move onto the next search.
    if zl.results_test(driver, search_term):
        print("Search " + str(search_term) + 
              " returned zero results. Moving onto the next search")
        print("***")
        continue
    
    # Pull the html for each page of search results. Zillow caps results at 
    # 20 pages, each page can contain 26 home listings, thus the cap on home 
    # listings per search is 520.
    rawdata = zl.get_html(driver)
    print(str(len(rawdata)) + " pages of listings found")
    
    # Take the extracted HTML and split it up by individual home listings.
    listings = zl.get_listings(rawdata)
    
    # For each home listing, extract the 11 variables that will populate that 
    # specific observation within the output dataframe.
    for n in range(len(listings)):
        # Street address, city, state, and zipcode
        addressSplit, address = zl.get_street_address(listings[n])
        if addressSplit != 'NA':
            city = zl.get_city(addressSplit, address)
            state = zl.get_state(addressSplit, city)
            zipcode = zl.get_zipcode(addressSplit, state)
        else:
            city = 'NA'
            state = 'NA'
            zipcode = 'NA'
        df.loc[n + count, 
               ["address", "city", "state", "zip"]] = address.strip(), city, state, zipcode
    
        # Price
        df.loc[n + count, "price"] = zl.get_price(listings[n])
        
        # Square footage
        df.loc[n + count, "sqft"] = zl.get_sqft(listings[n])
        
        # Number of bedrooms
        df.loc[n + count, "bedrooms"] = zl.get_bedrooms(listings[n])
        
        # Number of bathrooms
        df.loc[n + count, "bathrooms"] = zl.get_bathrooms(listings[n])
        
        # Days on the Market/Zillow
        df.loc[n + count, "days_on_zillow"] = zl.get_days_on_market(listings[n])
        
        # Sale Type (House for Sale, New Construction, Foreclosure, etc.)
        df.loc[n + count, "sale_type"] = zl.get_sale_type(listings[n])
        
        # url for each house listing
        df.loc[n + count, "url"] = zl.get_url(listings[n])
        
    # Increase the count variable to match the current number of rows within df.
    count += len(listings)

# Close the webdriver connection.
zl.close_connection(driver)

# Write df to CSV.
columns = ['address', 'city', 'state', 'zip', 'price', 'sqft', 'bedrooms', 
           'bathrooms', 'days_on_zillow', 'sale_type', 'url']
df = df[columns]
dt = time.strftime("%Y-%m-%d") + "_" + time.strftime("%H%M%S")
filename = str(dt) + ".csv"
df.to_csv(filename, index = False)
