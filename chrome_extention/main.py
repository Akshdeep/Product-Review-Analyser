from flask import Flask, request
from flaskext.mysql import MySQL
import requests
import re
import json
from textblob import TextBlob
import itertools

import pickle

# Disable request waring
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from amazon_scraper import AmazonScraper

amzn = AmazonScraper("AKIAJ5G4TDSHO2D54APQ", "DkMW4edxLB91MGcnDhChkciqj2XumqlySi9yOhT6", "beproject0d-20", Region='IN',
                     MaxQPS=0.9, Timeout=5.0)

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'turtle'
app.config['MYSQL_DATABASE_DB'] = 'review_data'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()
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


def reviewer_ease(asin):
    category_reviewer_ease = 4.2

    cursor.execute("select AVG(reviewer_ease_score) as book_reviewer_ease \
                                    from (select avg(overall) as reviewer_ease_score \
                                          from (select * \
                                          from reviews_table \
                                          where asin = '" + asin + "') as X\
                                    group by reviewerID ) as T")
    book_reviewer_ease = cursor.fetchall()[0][0]
    conn.commit()
    print book_reviewer_ease

    if (book_reviewer_ease - category_reviewer_ease) > 0.2:
        print "Warning: There is an indication of unnatural reviews."
        text_result = "Warning: There is an indication of unnatural reviews."
    else:
        print "Pass: No unnatural reviews detected."
        text_result = "Pass: No unnatural reviews detected."
    return text_result

def if_none(x):
    if x is None:
        return 0
    else:
        return x


def unverified_purchases(asin):
    cursor.execute(
        "select count(reviewType), AVG(overall) from reviews_table where reviewType = 'Verified Purchase' and asin = '" + asin + "'")
    data_ver = cursor.fetchall()
    cursor.execute(
        "select count(reviewType), AVG(overall) from reviews_table where reviewType = 'Unverified Purchase' and asin = '" + asin + "'")
    data_unver = cursor.fetchall()
    cursor.execute("select count(reviewerId) from reviews_table where asin = '" + asin + "'")
    total_no_reviews_product = cursor.fetchall()[0][0]
    conn.commit()
    verified_percent = data_ver[0][0] / total_no_reviews_product * 100
    unverified_percent = data_unver[0][0] / total_no_reviews_product * 100

    print "Percent of verified reviews:", verified_percent, "%"
    print "Average rating of verified reviews:", data_ver[0][1]
    print "Percent of unverified reviews:", unverified_percent, "%"
    print "Average rating of unverified reviews:", if_none(data_unver[0][1])


# def one_hit_wonders(asin):
#     ur_ids = []
#     p = amzn.lookup(ItemId=asin)
#     rs = p.reviews()
#     for r in rs:
#         ur = r.user_reviews()
#         for u in ur:
#             ur_ids.append(u.id)
#         print ur_ids, len(ur_ids)
#

def review_summary(asin):
    cursor.execute("select reviewText from reviews_table where asin = '%s'" % asin)
    reviews = cursor.fetchall()
    conn.commit()
    all_sentences = []
    for review in reviews:
        all_sentences.append(TextBlob(review[0]).sentences)
    all_sentences = list(itertools.chain.from_iterable(all_sentences))

    positive = ""
    negative = ""
    for sentence in all_sentences:
        polarity = TextBlob(str(sentence)).sentiment.polarity
        if polarity > 0.2:
            positive += str(sentence) + " "
        if polarity < -0.3:
            negative += str(sentence) + " "

    from gensim.summarization import summarize
    positive = summarize(positive, word_count=100, split=True)
    negative = summarize(negative, word_count=100, split=True)
    if positive is None:
        positive = ["We could not find any pros from the reviews."]

    if negative is None:
        negative = ["We could not find any cons from the reviews."]

    print positive, negative
    return positive, negative


def predict_helpful(asin):
    from sklearn.linear_model import LogisticRegression
    from sklearn.feature_extraction.text import CountVectorizer
    model = pickle.load(open("finalized_model.sav", 'rb'))
    vectorizer = pickle.load(open("vectorizer.sav", 'rb'))
    cursor.execute("select reviewText, overall from reviews_table where asin = '%s'" % asin)
    reviews = cursor.fetchall()
    conn.commit()
    rating_new = 0
    i = 0
    for r in reviews:
        pred = model.predict(vectorizer.transform([r[0]]))[0]
        #print pred
        if pred == 1:
            rating_new += r[1]
            i += 1
    print rating_new
    if rating_new != 0:
        rating_new /= i
    print rating_new

@app.route('/', methods=['GET', 'POST'])
def index():
    data = {}
    url = request.form['url']
    asin = get_amazon_item_id(url)
    print asin
    p = amzn.lookup(ItemId=asin)
    rs = p.reviews()
    cursor.execute("SELECT count(asin) FROM reviews_table where asin = '%s'" % asin)
    review_check = cursor.fetchall()
    conn.commit()
    print review_check
    if review_check[0][0] == 0:
        for r in rs:
            if str(r.soup.find("span", class_="a-size-mini a-color-state a-text-bold").contents[0]).__contains__(
                    "Verified Purchase"):
                verified = "Verified Purchase"
            else:
                verified = "Unverified Purchase"

            #print (asin, r.rating, r.full_review().text, r.date, r.id, r.name, r.title)
            cursor.callproc('add_review_data',
                            (asin, r.full_review().rating * 5, r.full_review().text, r.date, r.id, r.name, r.title,
                             verified))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                print 'Row created successfully !'
            else:
                print 'error'
    text_result = reviewer_ease(asin)
    unverified_purchases(asin)
    #one_hit_wonders(asin)
    pros, cons = review_summary(asin)
    predict_helpful(asin)
    data["title"] = p.title
    data["image_url"] = p.large_image_url
    cursor.execute("select avg(overall) from reviews_table where asin = '%s'" % asin)
    data["rating"] = cursor.fetchall()[0][0]
    conn.commit()
    data["pros"] = pros
    data["cons"] = cons
    data["text_result"] = text_result
    return json.dumps(data)


if __name__ == "__main__":
    app.run()
