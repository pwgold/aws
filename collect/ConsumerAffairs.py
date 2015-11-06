from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import urllib2

# References:
# http://doc.scrapy.org/en/latest/topics/selectors.html

class ConsumerAffairs(object):

    #url='http://www.consumeraffairs.com/nutrition/weight_watchers.html'
    url = 'http://www.consumeraffairs.com/nutrition/la_weight.html'

    def __init__(self):
        a = 1

    def fetch(self, full_url):
        response = HtmlResponse(url=full_url, body=urllib2.urlopen(full_url).read())
        next_button = 'Next page' in response.body
        xp = lambda x: response.selector.xpath(x).extract()
        return next_button, xp

    def collect(self, xp):
        review = [k for k in xp('//div[starts-with(@class, "review")]') if k.startswith('<div class="review" id="review-')]
        review_post = [k for k in xp('//div[starts-with(@class, "review")]') if k.startswith('<div class="review-post user-post complaint "><div class="post-info clearfix">')]
        assert len(review) == len(review_post)
        return [review[idx] + review_post[idx] for idx in range(len(review))]

if __name__ == "__main__":
    #import sys
    #sys.exit(main(sys.argv))
    ca = ConsumerAffairs()

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
