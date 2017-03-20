from flask import Flask, request
import requests
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from amazon_scraper import AmazonScraper

amzn = AmazonScraper("AKIAJ5G4TDSHO2D54APQ", "DkMW4edxLB91MGcnDhChkciqj2XumqlySi9yOhT6", "beproject0d-20", Region='IN', MaxQPS=0.9, Timeout=5.0)


app = Flask(__name__)

asin_regex = r'/([A-Z0-9]{10})'
isbn_regex = r'/([0-9]{10})'

def get_amazon_item_id(url):
    # return either ASIN or ISBN
    asin_search = re.search(asin_regex, url)
    isbn_search = re.search(isbn_regex, url)
    if asin_search:
        return asin_search.group(1)
    elif isbn_search:
        return isbn_search.group(1)
    else:
        # log this URL
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    print request
    url = request.form['url']
    id = get_amazon_item_id(url)
    print id
    p = amzn.lookup(ItemId=id)
    # for r in rs.full_reviews():
    #     title = (amzn.review(r.id)).title
    #     print title
    return p.title

if __name__ == "__main__":
    app.run()