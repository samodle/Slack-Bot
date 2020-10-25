import os
import random
import pyowm
import requests

from textblob import Word
from bs4 import BeautifulSoup
#from apiclient.discovery import build
from urllib.parse import urlencode, quote_plus


def check_weather(command):
    """Uses Pyowm API to check weather results for specified region"""
    fluff_words = ["out", "in", "over", "there", "like", "here"]
    command = command.replace("?", "").split('weather')[1].split(", ")
    command = ",".join(filter(lambda x: x not in fluff_words, command))

    if len(command.strip()) <= 1:
        command = "new york,ny"

    # pyowm key is set as an environmental variable
    owm = pyowm.OWM(os.environ.get('PYOWM_KEY'))
    observation = owm.weather_at_place(command)
    w = observation.get_weather()

    report = "It's {temp} degrees, and I would describe the condition as {condition}".format(
        temp=w.get_temperature(unit='fahrenheit')["temp"],  condition=w.get_detailed_status())
    return report


def comic(_):
    """Fetches random XKCD comic"""
    response = requests.get("https://xkcd.com/{}/info.0.json".format(random.randint(1, 1837)))
    return response.json()["img"]


def define(command):
    """Word definitions from textblob"""
    word = Word(command.split("define")[1].strip())
    return word.definitions[0]


def get_pic(command):
    """Queries Google custom search API for image"""
    query = command.split('pics')[1].strip()
    params = {
        "cx": os.environ.get("GOOGLE_IMAGE_CX"),
        "key": os.environ.get("GOOGLE_IMAGE_KEY"),
        "searchType": "image",
        "q": query
    }
    resp = requests.get('https://www.googleapis.com/customsearch/v1', params=params)
    images = [im['link'] for im in resp.json()['items']]
    return random.choice(images)


def get_quote(command):
    """Gets real time financial data for a ticker or benchmarks"""

    secret = os.environ["IEX_API_TOKEN"]
    ticker = command.split('quote ')[1].split()[0].upper()

    # make request
    response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{ticker}/quote?token={secret}")

    data = response.json()

    # parse price data
    price = data['latestPrice']
    pct_change = 100. * data['changePercent']
    mkt_cap = data['marketCap']

    result = f"{ticker} is trading at ${price}. That's a {pct_change:.2f}% move since the last open, which now values " \
             f"the company at ${mkt_cap:,}"

    return result


def joke(_):
    """Scrapes randome joke from theoatmeal.com"""
    url = requests.get('http://theoatmeal.com/djtaf/')
    soup = BeautifulSoup(url.content, 'lxml')
    random_joke = soup.find(class_='part1').get_text()
    random_answer = soup.find(id='part2_0').get_text()
    return "\n".join([random_joke, random_answer])


def search_words(command):
    """Direct link to top Google Search for given input"""
    command = command.replace("look up", "search").replace('google', 'search')
    query = command.split('search ')[1]
    goog = requests.get('https://www.google.com/search?{}'.format(urlencode({'q': query}, quote_via=quote_plus)))
    soup = BeautifulSoup(goog.content, 'lxml')

    all_text = ""

    for i in range(3, 5):
        text_candidate = soup.select_one("div:nth-of-type({})".format(i))
        if text_candidate:
            all_text += '\n' + text_candidate.get_text(separator=' ')

    return all_text


def synonyms(command):
    """Synonyms from textblob"""
    word = Word(command.split("synonyms")[1].strip())
    syns = {l for syn in word.synsets for l in syn.lemma_names()}
    return "\n".join(syns)


def word_count(command):
    """Simple word count"""
    text = command.split("count")[1].strip().split()
    return len(text)
