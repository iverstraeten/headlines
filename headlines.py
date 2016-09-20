import feedparser
import re
from flask import render_template
from flask import Flask
from flask import request
import json
import urllib
import urllib2

app = Flask(__name__)

defaults = {'publication':'standaard',
        'city':'Dendermonde',
        'currency_from': 'EUR',
        'currency_to': 'USD'}

currencyUrl = "https://openexchangerates.org/api/latest.json?app_id=8b7e1d43c0ce410981a06ac374c6565d"
weatherUrl = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=cf6a1af0983b8ed91c5c8086f2e0db02'

feeds = {'yandex': 'https://news.yandex.ua/index.uk.rss',
	'standaard': 'http://www.standaard.be' \
        '/rss/section/1f2838d4-99ea-49f0-9102-138784c7ea7',
        'deredactie': 'http://deredactie.be/cm/vrtnieuws?mode=atom',
	'techzine': 'http://feeds.techzine.nl/techzine/nieuws?format=xml',
        'volkskrant': 'http://www.volkskrant.nl/nieuws-voorpagina/rss.xml',
        'hln': 'http://www.hln.be/rss.xml',
        'tijd': 'http://www.tijd.be/rss/top_stories.xml',
        'knack': 'http://datanews.knack.be/ict/nieuws/feed.rss',
        'newsru':'http://rss.newsru.com/top/main/',
        'tweakers': 'http://feeds.feedburner.com/tweakers/mixed'}

def get_rate(frm, to):
    all_currencies = urllib2.urlopen(currencyUrl).read()
    parsed = json.loads(all_currencies).get('rates')
    from_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/from_rate, parsed.keys())

def get_weather(query):
    query = urllib.quote(query)
    url = weatherUrl.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description":parsed["weather"][0]["description"],
                "temperature":parsed["main"]["temp"],
                "city":parsed["name"],
                'country': parsed['sys']['country']}
        return weather

@app.route("/", methods=['GET', 'POST'])
def home():
    #get the headlines < user input
    #retrieve the newspaper using GET
    publication = request.args.get('publication')
    # if nothing is entered use 'standaard'
    if not publication:
        publication = defaults['publication']
    articles = get_news(publication)
    
    for article in articles:
        article.summary = re.sub('<[^<]+?>', '', article.summary)

    #get the city < user in put
    # retrieve it using GET
    city = request.args.get('city')
    if not city:
        city = defaults['city']
    weather = get_weather(city)

    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = defaults['currency_from']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = defaults['currency_to']
    rate, currencies = get_rate(currency_from, currency_to)

    return render_template("home.html", articles=articles, weather=weather, 
		    publicatie=publication.upper(), rate=rate, currencies = sorted(currencies), feeds=feeds,
		    keys=feeds.keys() )

def get_news(query):
    if not query or query.lower() not in feeds:
        publication = defaults["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse((feeds[publication]).encode('utf-8'))
    return feed['entries'] 
            
if __name__ == '__main__':
    app.run(port=80, debug=True)
