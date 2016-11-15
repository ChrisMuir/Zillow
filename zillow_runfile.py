import time
import pandas as pd
import zillow_functions as zl

# Define search term (must be str object).
search_term = '11201'

# Initialize the webdriver.
driver = zl.init_driver()

# Go to www.zillow.com/homes
zl.navigate_to_website(driver, "http://www.zillow.com/homes")

# Click the "buy" button.
zl.click_buy_button(driver)

# Enter search term and execute search.
zl.enter_search_term(driver, search_term)

# Check to see if any results were returned from the search.
# If there were none, an error will be raised.
zl.results_test(driver, search_term)

# Pull the html for each page of search results. Zillow caps results at 
# 20 pages, each page can contain 26 home listings, thus the cap on home 
# listings per search is 520.
rawdata = zl.get_html(driver)

# Close the webdriver connection.
zl.close_connection(driver)

# Take the extracted HTML and split it up by individual home listings.
listings = zl.get_listings(rawdata)

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
    df.loc[n, ["address", "city", "state", "zip"]] = address.strip(), city, state, zipcode
    
    # Price
    df.loc[n, "price"] = zl.get_price(listings[n])
    
    # Square footage
    df.loc[n, "sqft"] = zl.get_sqft(listings[n])

    # Number of bedrooms
    df.loc[n, "bedrooms"] = zl.get_bedrooms(listings[n])

    # Number of bathrooms
    df.loc[n, "bathrooms"] = zl.get_bathrooms(listings[n])

    # Days on the Market/Zillow
    df.loc[n, "days_on_zillow"] = zl.get_days_on_market(listings[n])
    
    # Sale Type (House for Sale, New Construction, Foreclosure, etc.)
    df.loc[n, "sale_type"] = zl.get_sale_type(listings[n])
    
    # url for each house listing
    df.loc[n, "url"] = zl.get_url(listings[n])
    
# Write df to CSV.
columns = ['address', 'city', 'state', 'zip', 'price', 'sqft', 'bedrooms', 
           'bathrooms', 'days_on_zillow', 'sale_type', 'url']
df = df[columns]
dt = time.strftime("%Y-%m-%d") + "_" + time.strftime("%H%M%S")
filename = str(search_term) + "_" + str(dt) + ".csv"
df.to_csv(filename, index = False)