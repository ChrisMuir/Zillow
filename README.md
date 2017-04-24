Zillow Scraping with Python
===========================

WARNING: Use this code at your own risk, scraping is against Zillow's TOC.
-------------------------------------------------------------------------

Basic tool for scraping current home listings from Zillow, written in Python 
using Selenium.  The code takes as input search terms that would normally be 
entered on the Zillow home page.  It creates 11 variables on each home listing 
from the data, saves them to a dataframe, and then writes the df to a CSV file 
that gets saved to your working directory. Using zip codes as search terms 
seems to yield the best results, the scraper works at a rate of about 75 
zip codes per hour (compared to the Zillow API limit of 1000 homes per 24h).

There are two files, `zillow_runfile.py` and `zillow_functions.py`. Save them 
both to your working directory, open the runfile and step through the code 
line-by-line. The zillow functions are sourced at the top of the runfile.

This tool uses a for loop to iterate over a list of input search terms, scrape 
the listings of each, and append the results to a dataframe. Function `zipcodes_list()` 
allows the user to compile a large list of zip codes to use as search terms, 
using the package [zipcode](https://pypi.python.org/pypi/zipcode). For example, 
`st = zipcodes_list(['10', '11', '770'])` 
will yield every US zip code that begins with '10', '11', or '770' as a single 
list. Object `st` could then be passed to the scraper. The scraper 
seems to fly below the radar of Zillows anti-scraping TOC rules.

Some things to keep in mind:
---------------------------
- You will need to edit the input parameter of function `init_driver` within`zillow_runfile.py` 
to point to the local path of your web driver program (required by Selenium).
- The max return for each search term (i.e. each zip code) is 520 home listings.
- There tends to be a small amount of NA's on every search, however foreclosure 
properties seem to be more likely to return NA's. So the more foreclosures 
there are in a search, the more NA's there will be.

Software Requirements/Info
---------------------
- This code was written using [Python 3.5](https://www.python.org/downloads/).
- This code was written using [Selenium v3.0.2](http://www.seleniumhq.org/download/).
- The Selenium package requires a webdriver program. This code was written 
using [Chromedriver v2.25](https://sites.google.com/a/chromium.org/chromedriver/downloads).

Example of the output dataframe:
------------------------

```
df.head(n=6)
```

```
                address     city state    zip    price  sqft bedrooms  \
0         4251 Drake St  Houston    TX  77005   895000  3501        4   
1  6534 Westchester Ave  Houston    TX  77005  1325000  2720        3   
2     2635 Centenary St  Houston    TX  77005  1449000  4114        5   
3     2336 Robinhood St  Houston    TX  77005  1295000  3652        3   
4     3135 Bissonnet St  Houston    TX  77005   359000  1692        2   
5         3824 Byron St  Houston    TX  77005  1100000  3161        3   

  bathrooms days_on_zillow           sale_type  \
0       4.0              4      House For Sale   
1       3.0              8      House For Sale   
2       5.0             NA      House For Sale   
3       4.0             33      House For Sale   
4       2.5             37  Townhouse For Sale   
5       4.0             43      House For Sale   

                                                 url  
0  http://www.zillow.com/homes/for_sale/27825953_...  
1  http://www.zillow.com/homes/for_sale/27792196_...  
2  http://www.zillow.com/homes/for_sale/27812119_...  
3  http://www.zillow.com/homes/for_sale/27836800_...  
4  http://www.zillow.com/homes/for_sale/27834549_...  
5  http://www.zillow.com/homes/for_sale/27823372_...
```
