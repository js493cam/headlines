from flask import Flask, render_template, request
import feedparser as fp
import json
import requests
import urllib

DEFAULTS = {"publication":"bbc",
			"city":"London,UK",
			"currency_frm":"GBP",
			"currency_to":"USD"}

RSS_FEEDS = {'bbc': "http://feeds.bbci.co.uk/news/rss.xml",
			 'cnn': "http://rss.cnn.com/rss/edition.rss",
			 'fox': "http://feeds.foxnews.com/foxnews/latest",
			 "iol": "http://www.iol.co.za/cmlink/1.640"}
 
app = Flask(__name__)

@app.route("/")
def home():
	# get news articles
	publication = request.args.get("publication")
	if not publication:
		publication = DEFAULTS["publication"]	
	articles = get_news(publication)
	
	# get weather
	city = request.args.get("city")
	if not city:
		city = DEFAULTS["city"]
	weather = get_weather(city)
	
	# get currency
	currency_frm = request.args.get("currency_frm")
	if not currency_frm:
		currency_frm = DEFAULTS["currency_frm"]
	currency_to = request.args.get("currency_to")
	if not currency_to:
		currency_to = DEFAULTS["currency_to"]
	
	rate = get_rate(currency_frm, currency_to)

	
	return render_template("home.html", 
							articles = articles, 
							weather = weather,
							currency_frm=currency_frm,
							currency_to=currency_to,
							rate=rate)
	

def get_news(query):
	if not query or query.lower() not in RSS_FEEDS:
		publication = DEFAULTS["publication"]
	else:
		publication = query.lower()

	feed = fp.parse(RSS_FEEDS[publication])
	return feed["entries"]
	
	
def get_weather(query):
	WEATHERAPIKEY = "e411b68a8090cd4c21b0267d06dea6fb"
	CURRENCYADDRESS = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=%s"%WEATHERAPIKEY
	
	query=urllib.parse.quote(query)
	url = CURRENCYADDRESS.format(query)
	
	data=requests.get(url).text
	parsed = json.loads(data)
	weather = None
	if parsed.get("weather"):
		weather = {"description":parsed["weather"][0]["description"],
					"temperature":parsed["main"]["temp"],
					"city":parsed["name"],
					"country": parsed["sys"]["country"]
					}
	return weather
				
def get_rate(frm, to):

	CURRENCYADDRESS = "https://openexchangerates.org/api/latest.json?app_id=a97f20e0536c49aeba37d8b8b6d97d4e"
	
	all_currency = requests.get(CURRENCYADDRESS).text
	parsed = json.loads(all_currency)["rates"]
	
	print("%s currencies found."%len(parsed))
	frm_rate = parsed.get(frm.upper())
	if not frm_rate:
		frm_rate = 1
	to_rate = parsed.get(to.upper())
	if not to_rate:
		to_rate = 1
	
	print("From: ", frm, frm_rate, " To: ", to, to_rate)
	
	return to_rate/frm_rate
	
	
if __name__ == "__main__":
	app.run(port=5000, debug=True)
	
