import pandas as pd
import numpy as np
import yfinance as yf
from collections import defaultdict

TICKERS = {
    # Dividend
    'OTP': 'OTP.BD',
    'MOL': 'MOL.BD',
    'Alteo': 'ALTEO.BD',
    'Waberers': 'WABERERS.BD',
    # Accumulating
    'Opus': 'OPUS.BD',
    'Appeninn': 'APPENINN.BD',
    # '4iG': '4IG.BD',  # too op
    # Data issue
    # 'Magyar Telekom': 'MTEL.BD',
    # 'Richter': 'RICHT.BD',
    # 'Autowallis': 'AUTOW.BD',
    'Microsoft': 'MSFT',
    'Apple': 'AAPL',
}


def load_data(stock_name, period):
    df = yf.Ticker(TICKERS[stock_name]).history(period=f'{period}y').reset_index()
    df['Date'] = pd.to_datetime(df.Date, utc=True).dt.floor('24H')
    df.columns = df.columns.str.lower()
    first_day = df.iloc[0]
    df['date'] = df.date
    # df['day'] = range(len(df))
    base_value = 100
    df['rel_open'] = base_value * df.open / first_day.open
    df['rel_close'] = base_value * df.close / first_day.open
    df['rel_high'] = base_value * df.high / first_day.open
    df['rel_low'] = base_value * df.low / first_day.open
    return df


def combine_data(stocks):
    combined = []
    for name, df in stocks.items():
        df = df.copy()
        df['name'] = name
        combined.append(df)

    combined = pd.concat(combined)
    return combined


class NotEnoughException(Exception):
    pass


class Game:
    def __init__(self, stocks, initial_funds=1000, period=3, initial_days=30, salary_period=30):
        self.stock_data = {stock: load_data(stock, period) for stock in stocks}
        self.day_progress = defaultdict(lambda: initial_days)
        self.funds = defaultdict(lambda: initial_funds)
        self.stock_amount = defaultdict(lambda: defaultdict(int))
        self.salary_period = salary_period
        self.salary = initial_funds
        self.last_salary_at = defaultdict(lambda: initial_days)

    def buy(self, player, stock, n):
        required_funds = np.ceil(self.stock_price(stock, self.day_progress[player]) * n)
        if required_funds > self.funds[player]:
            raise NotEnoughException('Not enough funds to buy!')
        else:
            self.funds[player] -= required_funds
            self.stock_amount[player][stock] += n

    def sell(self, player, stock, n):
        if n > self.stock_amount[player][stock]:
            raise NotEnoughException('Not enough stocks to sell!')
        else:
            self.funds[player] += np.floor(n * self.stock_price(stock, self.day_progress[player]))
            self.stock_amount[player][stock] -= n

    def progress_days(self, player, n):
        self.day_progress[player] += n
        salaries_owed = (self.day_progress[player] - self.last_salary_at[player]) // self.salary_period
        self.funds[player] += salaries_owed * self.salary

    def stock_price(self, stock, day):
        return self.stock_data[stock].iloc[day - 1].rel_close

    def get_stock_value(self, player):
        return float(sum([amount * self.stock_price(stock, self.day_progress[player])
                          for stock, amount in self.stock_amount[player].items()]))

    def get_total_value(self, player):
        return self.get_stock_value(player) + self.funds[player]

    def max_order(self, player, stock, order):
        if order.lower() == 'buy':
            return int(self.funds[player] // self.stock_price(stock, self.day_progress[player]))
        elif order.lower() == 'sell':
            return self.stock_amount[player][stock]
        else:
            raise Exception(f'Unknown order: {order}')

    def get_available_stock_data(self, player):
        day_progress = self.day_progress[player]
        return {name: df.iloc[:day_progress] for name, df in self.stock_data.items()}
