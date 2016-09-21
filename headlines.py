import feedparser, datetime, re, json, urllib, urllib2
from flask import render_template
from flask import Flask
from flask import request
from apiKeys import weatherUrl, currencyUrl
from feeds import feeds

app = Flask(__name__)

defaults = {'publication':'standaard',
        'city':'Antwerpen',
        'currency_from': 'EUR',
        'currency_to': 'USD'}

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
    if not publication:
	    publication = defaults['publication']
    # if nothing is entered use 'standaard'
    articles = get_news(publication)
    
    for article in articles:
        article.summary = re.sub('<[^<]+?>', '', article.summary)
	article.summary = article.summary.replace('&#8226;', '')

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
		    publicatie=publication, rate=rate, currencies = sorted(currencies), feeds=feeds,
		    keys=feeds.keys(),currency_from=currency_from, currency_to=currency_to )

def get_news(query):
    publication = query.lower()
    feed = feedparser.parse((feeds[publication]).encode('utf-8'))
    return feed['entries'] 
            
if __name__ == '__main__':
	app.run(port=5000, debug=True)
