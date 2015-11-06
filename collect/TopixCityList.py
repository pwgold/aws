#!/usr/bin/env python
# Collect Topix City List

import urllib2
import BeautifulSoup

class Scraper(object):
    def __init__(self):
        self.headers = {
            'User-Agent':'Mozilla/5.0'
        }

        self.root_url = 'http://www.topix.com/city/list'

    def scrape(self, page=1):
        url = self.root_url + '/p%s'%page
        
        r = urllib2.Request(
            url=url,
            headers=self.headers
        )
        html = urllib2.urlopen(r).read()
        soup = BeautifulSoup.BeautifulSoup(html)
        locations = [e.text for e in soup.findAll('a',t='dir-list-all-childnode')]
        return locations

if __name__ == '__main__':
    scraper = Scraper()
    for page in range(1,26):
        print '\n'.join(scraper.scrape(page))
        
