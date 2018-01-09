---
output:
  html_document: default
  pdf_document: default
---
Zillow Scraping with Python
===========================

WARNING: Use this code at your own risk, scraping is against Zillow's TOC
-------------------------------------------------------------------------

Basic tool for scraping current home listings from Zillow, written in Python 
using Selenium.  The code takes as input search terms that would normally be 
entered on the Zillow home page.  It creates 11 variables on each home listing 
from the data, saves them to a dataframe, and then writes the df to a CSV file 
that gets saved to your working directory. Using zip codes as search terms 
seems to yield the best results, the scraper works at a rate of about 75 
zip codes per hour (compared to the Zillow API limit of 1000 homes per 24h).

There are two files, `zillow_runfile.py` and `zillow_functions.py`. Clone this 
repo to your working directory, open the runfile and step through the code 
line-by-line. The zillow functions are sourced at the top of the runfile.

This tool uses a for loop to iterate over a list of input search terms, scrape 
the listings of each, and append the results to a dataframe. Function `zipcodes_list()` 
allows the user to compile a large list of zip codes to use as search terms, 
using the package [zipcode](https://pypi.python.org/pypi/zipcode). For example, 
`st = zipcodes_list(['10', '11', '770'])` 
will yield every US zip code that begins with '10', '11', or '770' as a single 
list. Object `st` could then be passed to the scraper.

Some things to keep in mind
---------------------------
- You will need to edit the input parameter of function `init_driver` within `zillow_runfile.py` 
to point to the local path of your web driver program (required by Selenium).
- The max return for each search term (i.e. each zip code) is 520 home listings.
- There tends to be a small amount of NA's on every search, however foreclosure 
properties seem to be more likely to return NA's. So the more foreclosures 
there are in a search, the more NA's there will be.

Software Requirements/Info
--------------------------
- This code was written using [Python 3.5](https://www.python.org/downloads/).
- [Selenium](http://www.seleniumhq.org/download/) (this can be PIP installed, written using v3.0.2).
- The Selenium package requires a webdriver program. This code was written 
using [Chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) v2.25.

Example of the output dataframe
-------------------------------

```py
df.head(n = 6)
```

```
                 address     city state    zip    price  sqft bedrooms  \
0      3011 Bissonnet St  Houston    TX  77005   575000  1820        3   
1          4229 Drake St  Houston    TX  77005   615000  2611        3   
2        2237 Wroxton Rd  HOUSTON    TX  77005  2095000  5492        4   
3      4318 Childress St  Houston    TX  77005   540000  2438        4   
4       2708 Werlein Ave  Houston    TX  77005  1449000  3905        4   
5  5402 Buffalo Speedway  Houston    TX  77005  1995000  4658        3   

  bathrooms days_on_zillow           sale_type  \
0         2             NA      House For Sale   
1         3             NA   For Sale by Owner   
2         5             NA      House For Sale   
3         4              2  Townhouse For Sale   
4         5              1      House For Sale   
5         4              5      House For Sale   

                                                 url  
0  http://www.zillow.com/homes/for_sale//homedeta...  
1  http://www.zillow.com/homes/for_sale//homedeta...  
2  http://www.zillow.com/homes/for_sale//homedeta...  
3  http://www.zillow.com/homes/for_sale//homedeta...  
4  http://www.zillow.com/homes/for_sale//homedeta...  
5  http://www.zillow.com/homes/for_sale//homedeta...  
```
