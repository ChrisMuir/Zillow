Zillow Scraping with Python
===========================

WARNING: Use this code at your own risk, scraping is against Zillow's TOC.
-------------------------------------------------------------------------

Basic tool for scraping current home listings from Zillow, written in Python using Selenium.  The code takes as input search terms that would normally be entered on the Zillow home page.  It attempts to create 11 variables on each listing from the data, writes them to a data frame, and then prints the df to a CSV file that gets saved to your current working directory.

Source the functions with `from zillow_scrape import zillow, init_driver`
Run `driver = init_driver()` to launch the web driver.
Then run `zillow(driver, "search_terms")` to execute the scraper.



Some things to keep in mind:
---------------------------
1. You will need to edit line 13 of the code to point to the local location of the web driver (required by Selenium). Function `init_driver()` is written for use with    chromedriver.
2. The output of each call to `Zillow` is capped at 520 home listings.
3. There tends to be a small amount of NA's on every search, however foreclosure properties seem to be more likely to throw NA's. So the more foreclosures there are in a search, the more NA's there will be.
4. Code seems to work best with zipcode as the search terms input.



Example of the output df:
------------------------

```
df.head(n=6)
```

```
                  Address     City State    Zip    Price  Sqft bedrooms  \
0  5200 Weslayan St # 104  Houston    TX  77005   224900  1263        2   
1    5917 Wakeforest Ave   Houston    TX  77005  1649000  1534        2   
2      3778 Childress St   Houston    TX  77005  1989000  5085        4   
3  6339 Buffalo Speedway   Houston    TX  77005  2700000  9230        5   
4   3771 University Blvd   Houston    TX  77005   895000  1456        3   
5          5502 Auden St   Houston    TX  77005  1300000  4200        5   

  bathrooms days_on_zillow           sale_type  \
0         2              2  Townhouse For Sale   
1         1             NA    New Construction   
2         5             NA      House For Sale   
3         9              2      House For Sale   
4         2             NA      House For Sale   
5         5             NA      House For Sale   

                                                 url  
0  http://www.zillow.com/homes/for_sale/28441158_...  
1  http://www.zillow.com/homes/for_sale/27840940_...  
2  http://www.zillow.com/homes/for_sale/27885447_...  
3  http://www.zillow.com/homes/for_sale/27791875_...  
4  http://www.zillow.com/homes/for_sale/27827005_...  
5  http://www.zillow.com/homes/for_sale/27795797_...
```
