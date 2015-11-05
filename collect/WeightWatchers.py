#!/usr/bin/env python
# Collect weight watchers locations

import json
import requests

class Scraper(object):
    def __init__(self):
        self.search_request = {
            "Page":1,
            "Count":80, # max seems to be 100
            "Country":"US",
            "Type":"Zip", # "State"
            "ZipCode":"19004"
            #"City":"PA"
        }

        self.headers = {
            'content-type': 'application/json'
        }

        self.url = 'https://mobile.weightwatchers.com/MeetingsService.svc/FindwithfullDetails'

    def scrape(self, zip_code='19004', count=80):
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
    scraper = Scraper()
    print scraper.scrape('11238')
