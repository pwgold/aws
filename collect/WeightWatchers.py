#!/usr/bin/env python
# Collect weight watchers locations

# References: http://toddhayton.com/2015/03/11/scraping-ajax-pages-with-python/
#             http://stackoverflow.com/questions/9746303/how-do-i-send-a-post-request-as-a-json
#             http://stackoverflow.com/questions/13303449/urllib2-httperror-http-error-403-forbidden

import json
import requests

class Scraper(object):
    def __init__(self):
        self.search_request = {
            "Page":1,
            "Count":1, # max seems to be 100
            "Country":"US",
            "Type":"Zip", # "State"
            "ZipCode":"19004"
            #"City":"PA"
        }

        self.headers = {
            'content-type': 'application/json'
        }

        self.url = 'https://mobile.weightwatchers.com/MeetingsService.svc/FindwithfullDetails'

    def scrape(self, zip_code='19004', count=1):
        self.search_request['ZipCode'] = zip_code
        self.search_request['Count'] = count
        payload = json.dumps(self.search_request)

        r = requests.post(
            url=self.url,
            data=payload,
            headers=self.headers
        )
        
        response = r.json()
        return response

if __name__ == '__main__':
    import pandas as pd
    scraper = Scraper()

    zip_codes = pd.read_csv('../config/zip_code_database.csv', index_col=0) # NB: Does this convert to integer?
    standard_zip_codes = [str(e).zfill(5) for e in zip_codes.query(" type == 'STANDARD' ").index] # standard 5 digit zip codes
    standard_zip_codes_checked = pd.Series(False, index=standard_zip_codes)

    unchecked_zips = standard_zip_codes_checked.replace(True, pd.np.nan).dropna()    
    #for i in range(10): # for now
    while len(unchecked_zips) > 0:
        z = unchecked_zips.index[0] # unchecked_zips[0] # next unchecked
        initial_n = sum(1 - standard_zip_codes_checked)
        data = scraper.scrape(zip_code=z, count=100)
        if data['TotalCount'] > 0:
            pd.to_pickle(data, '../data/20151105/%s.pkl'%z)
        checked_zips = [m['Address']['ZipCode'] for m in data['meetingLocations']] + [z] # add back [z] in case it wasn't seen (i.e., no location)
        #unchecked_zips = [k for k in unchecked_zips if k not in checked_zips] # remove these from unchecked list
        ok_idx = [k for k in checked_zips if k in standard_zip_codes]
        unrecognized_zips = [k for k in checked_zips if k not in standard_zip_codes]
        if len(unrecognized_zips) > 0:
            print unrecognized_zips
        standard_zip_codes_checked.ix[ok_idx] = True
        #print checked_zips
        unchecked_zips = standard_zip_codes_checked.replace(True, pd.np.nan).dropna()            
        #assert len(unchecked_zips) == initial_n - len(set(checked_zips)) # Verify that unchecked_zips has 1 fewer member for each zip code checked
        print '|'.join([str(e) for e in [len(data['meetingLocations']), z, len(unchecked_zips)]])
        
