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
    import sys

    scraper = Scraper()
    # NB: Does this convert to integer?
    zip_codes = pd.read_csv('../config/zip_code_database.csv', index_col=0) 
    zip_codes = zip_codes.sort(columns='estimated_population', ascending=False)
    # standard 5 digit zip codes
    standard_zip_codes = [str(e).zfill(5) for e in zip_codes.index] # zip_codes.query(" type == 'STANDARD' ").index] 
    # NB: Shouldn't restrict to just STANDARD
    # 75120,"PO BOX",Ennis,,,TX,"Ellis County",America/Chicago,214,32.33,-96.62,NA,US,0,1086,
    # ensure no duplicates
    assert len(standard_zip_codes) == len(set(standard_zip_codes))
    standard_zip_codes_checked = pd.Series(False, index=standard_zip_codes)
    output = {} # NB: growing
    # Base case:
    unchecked_zips = standard_zip_codes_checked.replace(True, pd.np.nan).dropna()    
    while len(unchecked_zips) > 0:
    #while len(output) < 150:
        z = unchecked_zips.index[0] # unchecked_zips[0] # next unchecked
        initial_n = sum(1 - standard_zip_codes_checked)
        # scrape data
        try:
            data = scraper.scrape(zip_code=z, count=75) 
        except Exception as e:
            print z,e
            sys.stdout.flush()
            continue
            
            
        # Count == 100 was throwing an error, even for valid zip codes, like:
        # {u'Message': u'UnexpectedException', u'ExceptionType': 61704, u'DateTime': u'11/05/2015 18:56:33'}

        if 'ExceptionType' in data:
            print z, data
            sys.stdout.flush()
            # Option A:
            # just update with z itself
            #standard_zip_codes_checked.ix[z] = True
            #unchecked_zips = standard_zip_codes_checked.replace(True, pd.np.nan).dropna()         
            #continue
            # Option B:
            # try again with lower count
            try:
                data = scraper.scrape(zip_code=z, count=20) 
            except Exception as e:
                print z,e
                continue            

        # write if non-empty
        if len(data) > 0 and data['TotalCount'] > 0:
            #path = '../data/20151105/%s.json'%z
            #with open(path, 'wb') as f:
            #    f.write(json.dumps(data))
            #    f.write('\n') # safe to add this for readability
            # TODO: o periodically write output
            # NB: assuming LocationId is unique
            retrieved_location_ids = [e['LocationId'] for e in data['meetingLocations']]
            # verify these are unique, so safe to create dictionary below
            assert len(retrieved_location_ids) == len(set(retrieved_location_ids))
            retrieved_data = dict((e['LocationId'], e) for e in data['meetingLocations'])
            # TODO: o should verify that data matches on all matching locationIds
            output.update(retrieved_data)
            # TODO: o save incrementally

        checked_zips = [m['Address']['ZipCode'] for m in data['meetingLocations']]
        # NB: this list of meeting locations may contain locations also returned
        #     in another search
        if z not in checked_zips:
            checked_zips += [z] # add back [z] in case it wasn't seen (i.e., no location)
        ok_idx = [k for k in checked_zips if k in standard_zip_codes]
        # print ok_idx
        unrecognized_zips = [k for k in checked_zips if k not in standard_zip_codes]
        if len(unrecognized_zips) > 0:
            print 'Unrecognized: ' + '|'.join(unrecognized_zips)
        standard_zip_codes_checked.ix[ok_idx] = True 
        #standard_zip_codes_checked.ix[checked_zips] = True # NB: this may be growing & this fails
        unchecked_zips = standard_zip_codes_checked.replace(True, pd.np.nan).dropna()            
        print '|'.join([str(e) for e in [z, len(data['meetingLocations']), len(unchecked_zips), len(output)]])
        sys.stdout.flush()
        # NB: below doesn't work b/c not guaranteed that all returned checked_zips are new
        #a,b,c = len(unchecked_zips), initial_n, len(set(checked_zips))
        #assert a == b - c, '%s,%s,%s'%(a,b,c)
        # assert len(unchecked_zips) == initial_n - len(set(checked_zips)) 
        # Verify that unchecked_zips has 1 fewer member for each zip code checked

    filename = pd.datetime.now().strftime('%s')+'.json'
    data_dir = '/home/ubuntu/aws/data/WeightWatchers'
    with open('%s/%s'%(data_dir,filename), 'wb') as f:
        f.write(json.dumps(output))
        f.write('\n') # safe to add this for readability
