from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import urllib2
import re

# References:
# http://doc.scrapy.org/en/latest/topics/selectors.html

class ConsumerAffairs(object):

    # TODO: o investigate format of "Paul of Mirganville, NJ" review on http://www.consumeraffairs.com/nutrition/sensa.html

    def __init__(self, category='nutrition', company='weight_watchers'):
        self.url = 'http://www.consumeraffairs.com/%s/%s.html'%(category, company)
        1 == 1

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

    for company in nutrition:
        try:
            collection_start = pd.datetime.now().strftime('%s')
            ca = ConsumerAffairs(category=category, company=company)
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
