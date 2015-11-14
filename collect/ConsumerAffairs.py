from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import urllib2
import re
from BeautifulSoup import BeautifulSoup

# References:
# http://doc.scrapy.org/en/latest/topics/selectors.html

class ConsumerAffairs(object):

    # TODO: o investigate format of "Paul of Mirganville, NJ" review on http://www.consumeraffairs.com/nutrition/sensa.html

    def __init__(self):
        1 == 1

    def get_categories(self):
        html = urllib2.urlopen('http://www.consumeraffairs.com').read()
        soup = BeautifulSoup(html)
        homepage_links = soup.findAll('a', {'class':'homepage-link'}) # NB: o This doesn't cover everything, e.g., http://www.consumeraffairs.com/computers/apple_imac.html
        categories = list(set([l['href'].split('/')[3] for l in homepage_links]))
        return categories
        #soup = BeautifulSoup(urllib2.urlopen(links[-1]['href']))

    def get_slugs(self, soup):
        #urllib2.urlopen('http://www.consumeraffairs.com/%s/%s.htm'%(cat,cat));
        # if compare reviews for in 
        # Top 7 of the Best Matched Identity Theft Protection Companies (privacy)
        #linksA = soup.findAll('a', {'class':'read-reviews-link'})
        #linksB = soup.findAll('a',{'class':'read-reviews-link disable-print '})
        #linksC = [k['href'].rstrip('#expert-review') for k in soup.findAll('a') if k.text == "Read More"]
        #num_links = re.search('.*(Top ([0-9]+)).*', html).groups(1)[1]
        #print '%s|%s|%s|%s|%s'%(cat, len(linksA), len(linksB), len(linksC), num_links)
        x = str([k for k in soup.findAll('script') if 'needed for displaying' in str(k)][0]).split('\n')[4].lstrip(' ').lstrip('comparison: ').rstrip(',')
        slugs = [e['slug'] for e in json.loads(x)['data']]
        for e in slugs:
            try:
                urllib2.urlopen('http://www.consumeraffairs.com/business-loans-and-financing/%s.html'%e)
                print "OK: %s"%e
            except:
                try:
                    urllib2.urlopen('http://www.consumeraffairs.com/business-loans-and-financing/%s.html'%e.replace('-','_'))
                    print "Renamed: %s"%e.replace('-','_')
                except:
                    print 'Error: %s'%e

    def get_review_pages(self, soup):
        review_pages = [k['href'] for k in soup.findAll('a', {'class':'review_page'})]
        print '\n'.join(['OK_1: %s'%e for e in review_pages])
    
    def get_sub_categories(self, soup):
        sub_categories = [k.find('a')['href'] for k in soup.findAll('div',{'class':'sub-category'})]
        print '\n'.join(['SubCategory: %s'%e for e in sub_categories])

    def get_related_categories(self, soup):
        related_categories = [k['href'] for k in soup.find('ul', {'class':"links"}).findAll('a')]        
        print '\n'.join(['RelatedCategories: %s'%e for e in related_categories])

    def parse_categories(self, categories):
        for cat in categories:
            html = urllib2.urlopen('http://www.consumeraffairs.com/%s/'%cat).read()
            soup = BeautifulSoup(html)
            if 'Compare Reviews for' in html:
                get_slugs(soup)
            else:
                # Either Version 1 e.g., Computer Brands
                # TODO: o check sub-categorey, e.g., Home > Electronics > Computers
                if soup.find('table') is not None:   # <table class="table" id="sortableTable" >
                    get_review_pages(soup)
                else:
                    # or version 2 e.g., Home > Insurance and has related ctegories
                    get_sub_categories(soup)
                    get_related_categories(soup)

    # Scratch
    # [k['href'] for k in soup.find('section', {'class':'entry'}).findAll('a')]
    #    print '%s: %s'%('Compare Reviews for' in html, cat)
    #
    #    except:
    #        try:
    #            urllib2.urlopen('http://www.consumeraffairs.com/%s/'%(cat))
    #            print 'OK2: %s'%cat
    #        except:
    #            print 'ERR: %s'%cat
    # if OK, look at <a href="http://www.consumeraffairs.com/computers/apple_imac.html" class="review_page">, 

    def set_url(self, category='nutrition', company='weight_watchers'):
        self.url = 'http://www.consumeraffairs.com/%s/%s.html'%(category, company)

    def fetch(self, full_url):
        response = HtmlResponse(url=full_url, body=urllib2.urlopen(full_url).read())
        next_button = 'Next page' in response.body
        xp = lambda x: response.selector.xpath(x).extract()
        return next_button, xp

    def collect(self, xp):
        review = [k for k in xp('//div[starts-with(@class, "review")]') if k.startswith('<div class="review" id="review-')]
        review_post = [k for k in xp('//div[starts-with(@class, "review")]') if k.startswith('<div class="review-post user-post complaint "><div class="post-info clearfix">')]
        assert len(review) == len(review_post)
        output = [review[idx] + review_post[idx] for idx in range(len(review))]
        return output

    def convert_to_json(self, input_data):
        pat = re.compile('.*(id="review-([0-9]+)").*') # TODO: o don't compile on every function call
        keys = [pat.search(text).group(2) for text in input_data] # NB: This will error if pattern isn't found
        assert len(keys) == len(set(keys)) # Verify that keys are unique
        output = dict((keys[idx], input_data[idx]) for idx in range(len(keys)))
        return output

if __name__ == "__main__":
    import pandas as pd
    import json
    #import sys
    #sys.exit(main(sys.argv))3

    nutrition = ['nutrisystem','la_weight','weight_watchers',
                 'medifast','herbalife','jenny_craig','provida',
                 'right-size-smoothies','slimfast','bioslim',
                 'metabolife','sensa']
   # health =   ['ediets-com', 'beachbody', 'nutrafit-meals']

    category = 'nutrition'

    ca = ConsumerAffairs()

    for company in nutrition:
        try:
            collection_start = pd.datetime.now().strftime('%s')
            ca.set_url(category=category, company=company)
            # TODO: o move this to class
            def do(idx, output):
                full_url = ca.url + '?page=' + str(idx)
                next_button, xp = ca.fetch(full_url)
                output.extend(ca.collect(xp))
                print idx, len(set(output)), full_url
                return next_button, output

            idx = 1
            next_button, output = do(idx, [])
            while next_button:
                idx += 1
                next_button, output = do(idx, output)

            filename = '../data/ConsumerAffairs/'+collection_start+'.'+category+'.'+company+'.json'
            with open(filename, 'wb') as f:
                f.write(json.dumps(ca.convert_to_json(output)))
                f.write('\n') # safe to add this for readability
        except Exception as e:
            print e, company, idx
