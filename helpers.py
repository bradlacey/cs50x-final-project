from flask import Flask, flash, redirect, render_template, request, session, url_for

import csv
import quandl			# for my API call later
import urllib.request

from flask import redirect, render_template, request, session
from functools import wraps

quandl.ApiConfig.api_key = "Yp6bSmznThD2mfDnUFyQ"

def apology(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""
    
    # debugging
    # used because the data requests seem inconsistent
    # - Yahoo!'s is dead altogether
    # - AlphaAdvantage only works sometimes
    # return {
    # 	"name": "Google",
	# 	"price": 1000,
	# 	"symbol": "GOOG"
	# }

    # reject symbol if it starts with caret
    if symbol.startswith("^"):
        return None

    # reject symbol if it contains comma
    if "," in symbol:
        return None
        
        
	# Here's another shot at it...
	
	# query QuandL for quote
	# https://blog.quandl.com/api-for-stock-data
    try:
        url = "https://www.quandl.com/api/v3/datasets/EOD/"
        url += symbol
        url += ".csv?api_key=Yp6bSmznThD2mfDnUFyQ&column_index=1&rows=1"
        # full URL: https://www.quandl.com/api/v3/datasets/EOD/{{symbol}}.csv?api_key=Yp6bSmznThD2mfDnUFyQ&column_index=1&rows=1
        # e.g.:     https://www.quandl.com/api/v3/datasets/EOD/AAPL.csv?api_key=Yp6bSmznThD2mfDnUFyQ&column_index=1&rows=1
        
        request = "EOD/"
        request += symbol
        
        # shift 48 spaces to account for whitespace in data
        data_start = 48
        
        # ABOVE: TESTED
        
        # see documentation:
        # https://docs.quandl.com/docs/in-depth-usage
        
        # HERE : TESTING
        
        data = quandl.get(request, column_index=1, rows=1)
        data = str(data)
        data = data[data_start:]
		
		# return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
        return {
            "name": symbol,
            "price": Decimal(data).quantize(TWOPLACES),
            "symbol": symbol
        }
        
    except:
    	pass


    # query Yahoo for quote
    # http://stackoverflow.com/a/21351911
    try:

        # GET CSV
        url = f"http://download.finance.yahoo.com/d/quotes.csv?f=snl1&s={symbol}"
        webpage = urllib.request.urlopen(url)

        # read CSV
        datareader = csv.reader(webpage.read().decode("utf-8").splitlines())

        # parse first row
        row = next(datareader)

        # ensure stock exists
        try:
            price = float(row[2])
        except:
            return None

        # return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
        return {
            "name": row[1],
            "price": price,
            "symbol": row[0].upper()
        }

    except:
        pass

    # query Alpha Vantage for quote instead
    # https://www.alphavantage.co/documentation/
    try:

        # GET CSV
        url = f"https://www.alphavantage.co/query?apikey=NAJXWIA8D6VN6A3K&datatype=csv&function=TIME_SERIES_INTRADAY&interval=1min&symbol={symbol}"
        webpage = urllib.request.urlopen(url)

        # parse CSV
        datareader = csv.reader(webpage.read().decode("utf-8").splitlines())

        # ignore first row
        next(datareader)

        # parse second row
        row = next(datareader)

        # ensure stock exists
        try:
            price = float(row[4])
        except:
            return None
        # return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
        return {
            "name": symbol.upper(), # for backward compatibility with Yahoo
            "price": price,
            "symbol": symbol.upper()
        }

    except:
        return None


def usd(value):
    """Formats value as USD."""
    return f"${value:,.2f}"
