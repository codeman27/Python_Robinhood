import requests
import time
import uuid
import json

millis = lambda: int(time.time())

class Price:
    def __init__(self, json=None):
        self.ask = 0.00
        self.bid = 0.00
        self.mark = 0.00
        self.symbol = "ETHUSD"
        if json is not None:
            try:
                self.ask = float(json['ask_price'])
                self.bid = float(json['bid_price'])
                self.mark = float(json['mark_price'])
                self.symbol = json['symbol']
            except KeyError as e:
                print(e)

class CryptoMarket:
    def __init__(self):
        self.session = requests.Session()
        # self.session.headers.update({'Accept': 'application/json'})
        d = {'username': '', 'password': '', 'grant_type': 'password', 'scope': 'internal', 'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS', 'expires-in': '86400'}
        r = self.session.post('https://api.robinhood.com/oauth2/token/', data=d)
        #print(r.json())
        self.token = r.json()['access_token']
        self.session.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
        r = self.session.get('https://nummus.robinhood.com/accounts/')
        self.account_id = r.json()['results'][0]['id']

    @property
    def buying_power(self):
        r = self.session.get('https://api.robinhood.com/accounts/')
        b = r.json()['results'][0]['cash_balances']['buying_power']
        #print(r.json())
        return float(b)

    def get_price(self, symbol):
        # r = requests.get("https://min-api.cryptocompare.com/data/price?fsym={}&tsyms=USD".format(symbol))
        # price = r.json()["USD"]
        # h = {'Authorization': 'Token {}'.format(self.token)}
        # print(h)
        # print(self.session.headers)
        r = self.session.get('https://api.robinhood.com/marketdata/forex/quotes/76637d50-c702-4ed1-bcb5-5b0732a81f48/')
        return Price(r.json())

    def get_buy_price(self, symbol="ETH"):
        r = self.session.get('https://api.robinhood.com/marketdata/forex/quotes/76637d50-c702-4ed1-bcb5-5b0732a81f48/')
        price = r.json()['ask_price']
        return float(price)

    def get_sell_price(self, symbol="ETH"):
        r = self.session.get('https://api.robinhood.com/marketdata/forex/quotes/76637d50-c702-4ed1-bcb5-5b0732a81f48/')
        price = r.json()['bid_price']
        return float(price)

    def get_order_status(self, id):
        r = self.session.get('https://nummus.robinhood.com/orders/{}'.format(id))
        return r.json()['state']

    def buy(self, amount, price, symbol="ETH", units="USD"):
        amount = round(amount, 6)
        #print("Bought {} for {} {}.".format(symbol, self.get_price(symbol), units))
        d = {'account_id': self.account_id,
            'currency_pair_id': '76637d50-c702-4ed1-bcb5-5b0732a81f48',
            'price': price,
            'quantity': amount,
            'ref_id': str(uuid.uuid4()),
            'side': 'buy',
            'time_in_force': 'gtc',
            'type': 'market'}
        r = self.session.post('https://nummus.robinhood.com/orders/', json=d)
        #orderid = r['id']
        #print(r.json())
        #while self.get_order_status(orderid) != 'filled':
            #time.sleep(5)
        return amount

    def sell(self, amount, price, symbol="ETH", units="USD"):
        amount = round(amount, 6)
        #print("Sold {} for {} {}.".format(symbol, self.get_price(symbol), units))
        d = {'account_id': self.account_id,
            'currency_pair_id': '76637d50-c702-4ed1-bcb5-5b0732a81f48',
            'price': round(price, 6),
            'quantity': amount,
            'ref_id': str(uuid.uuid4()),
            'side': 'sell',
            'time_in_force': 'gtc',
            'type': 'market'}
        r = self.session.post('https://nummus.robinhood.com/orders/', json=d)
        #orderid = r['id']
        #print(r.json())
        #while self.get_order_status(orderid) != 'filled':
            #time.sleep(5)
        return amount

    def __del__(self):
        # h = {'Authorization': 'Token {}'.format(self.token)}
        r = self.session.post('https://api.robinhood.com/api-token-logout/')


class PriceTracker:
    def __init__(self):
        self.history = []
        self.units = "USD"

    def __getitem__(self, key):
        return self.history[key]["price"]

    def recent_min(self):
        r = 0.0
        if len(self.history) > 1:
            i = len(self.history) - 1
            r = self[i]
            while i > 0 and self[i] <= self[i-1]:
                i -= 1
            while i > 0 and self[i] > self[i-1]:
                i -= 1
                r = self[i]
        return r

    def recent_max(self):
        r = 0.0
        if len(self.history) > 1:
            # print('history > 1')
            i = len(self.history) - 1
            r = self[i]
            # print(i)
            while i > 0 and self[i] >= self[i-1]:
                i -= 1
                # print('Price {}, i {}'.format(self[i], i))
            while i > 0 and self[i] < self[i-1]:
                i -= 1
                r = self[i]
                # print('Price {}, i {}'.format(self[i], i))
        return r

    def record(self, price):
        self.history.append({"price": price, "time": millis()})

    def data(self):
        datapoints = []
        prices = []
        times = []
        for p in self.history:
            prices.append(p["price"])
            times.append(p["time"])
        datapoints.append({"x": times, "y": prices, "type": "bar", "name": "Prices"})
        return datapoints
