# This tool is outdated

# CatMyPhish
Search for categorized domain that can be used during red teaming engagement. Perfect to setup whitelisted domain for your 
Cobalt Strike beacon C&C. 

It relies on expireddomains.net to obtain a list of expired domains. The domain availability is validated using checkdomain.com

# Usage
```
$ python CatMyFish.py -h
CatMyPhish v1.0 - Search for available already categorized domain
Mr.Un1k0d3r - RingZer0 Team 2016

usage: CatMyPhish.py [-h] [-v] [-e] [-f FILENAME] [-o OUTPUT]
                    [keywords [keywords ...]]

positional arguments:
  keywords              Keyword to use when search for expired domains

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         More verbose output
  -e, --exitone         Stop querying Symantec after first success
  -f FILENAME, --filename FILENAME
                        Loads domains to check from a text file, instead of
                        searching
  -o OUTPUT, --output OUTPUT
                        Write unregistered, categorized domains to a file.
```

# Example
```
$ python CatMyPhish.py sugar
CatMyPhish v1.0 - Search for available already categorized domain
Mr.Un1k0d3r - RingZer0 Team 2016

[+] (25) domains found using the keyword "sugar".
[+] Symantec categorization check may take several minutes. Bot check is pretty aggressive...
[+] Potential candidate: SugarNines.com categorized as Personal Sites.
[+] Potential candidate: CreativeSugarFlowers.com categorized as Restaurants/Dining/Food.
[+] Potential candidate: mysugargrove.com categorized as Society/Daily Living.
[+] Potential candidate: SugarTreeScrapbook.com categorized as Society/Daily Living.
[+] Potential candidate: SugarlandMania.com categorized as Entertainment.
[+] Potential candidate: SugarTreeProperties.com categorized as Real Estate.
[+] Potential candidate: BloodSugarTips.com categorized as Health.
[+] Potential candidate: SugarmillWoodsNews.com categorized as Real Estate.
[+] (8) candidates found.
[+] Awesome "SugarNines.com" is categorized and available.
[+] Awesome "CreativeSugarFlowers.com" is categorized and available.
[+] Awesome "mysugargrove.com" is categorized and available.
[+] Awesome "SugarTreeScrapbook.com" is categorized and available.
[+] Awesome "SugarlandMania.com" is categorized and available.
[+] Awesome "SugarTreeProperties.com" is categorized and available.
[+] Awesome "BloodSugarTips.com" is categorized and available.
[+] Awesome "SugarmillWoodsNews.com" is categorized and available.
[+] Search completed.
```

# Warning
the Symantec categorization search is slow to avoid captcha. Using proxychains and Tor is a good workaround. 

# TODO
- Categorization check against other vendors.
- Populate the blacklisted categories 

# Credit
Mr.Un1k0d3r RingZer0 Team
