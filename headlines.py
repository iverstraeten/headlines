import feedparser, datetime, re, json, urllib, urllib2
from flask import jsonify
from flask import render_template, Flask, request, make_response
from apiKeys import weatherUrl, currencyUrl
from feeds import feeds

app = Flask(__name__)

DEFAULTS = {'publication':'hln',
        'city':'New York',
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

def get_value_with_fallback(key):
	if request.args.get(key):
		return request.args.get(key)
	if request.cookies.get(key):
		return request.cookies.get(key)
	return DEFAULTS[key] 
def clean_articles(articles):
	for article in articles:
        	article.summary = re.sub('<[^<]+?>', '', article.summary)
		article.summary = article.summary.replace('&#8226;', '-')
		article.summary = article.summary.replace(
				'wiadomosci.wp.pl','')
	return articles

def get_news(query):
    publication = query.lower()
    feed = feedparser.parse((feeds[publication]).encode('utf-8'))
    return feed['entries'] 
 
@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
	return jsonify({'ip': request.remote_addr}), 200

@app.route("/")
def home():
    #get the headlines < user input
    #retrieve the newspaper using GET

    publication = get_value_with_fallback("publication")
    articles = get_news(publication)
    articles = clean_articles(articles)

    #get the city < user in put
    # retrieve it using GET
    city = get_value_with_fallback("city")
    weather = get_weather(city)

    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate, currencies = get_rate(currency_from, currency_to)

    response = make_response(render_template("home.html", 
	    articles=articles, 
	    weather=weather,
	    publicatie=publication, 
	    rate=rate, 
	    currencies = sorted(currencies), 
	    feeds=feeds,
	    keys=feeds.keys(),
	    currency_from=currency_from, 
	    currency_to=currency_to))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from",
		    currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response

           
if __name__ == '__main__':
	app.run(port=5000, debug=True)
