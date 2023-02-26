import asyncio
import aiohttp
import pandas as pd
import argparse
from tqdm import tqdm


class BinanceHistoricalDataScraper:
    """
    BinanceHistoricalDataScraper is a class that scrapes historical data of Binance USDT trading pairs.

    Attributes:
        symbols_url (str): URL to get the list of trading pairs on Binance.
        symbols_list (list): List of USDT trading pairs to scrape data for.
        params (dict): Dictionary of scraping parameters including timeframe and limit.
        historical_data (DataFrame): Pandas DataFrame to store the scraped historical data.

    Methods:
        fetch(session, url):
            Asynchronously fetches data from the specified URL using the provided session.

        get_historical_data(session, symbol, pbar):
            Asynchronously gets the historical data for a given symbol using the provided session and progress bar.

        scrape():
            Asynchronously scrapes historical data for all symbols in symbols_list and saves it to a CSV file.

    Args:
        tf (str): Timeframe for scraping the data. Allowed values are [1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 8h, 1d].
        limit (int): Limit number of candles for scraping the data. Allowed values are from 1 to 1000.

    Raises:
        None

    Returns:
        None
    """
    def __init__(self, tf, limit):
        self.symbols_url = 'https://api.binance.com/api/v3/exchangeInfo'
        self.symbols_list = []
        self.params = {'tf': tf, 'limit': limit}
        self.historical_data = pd.DataFrame()

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.json()

    async def get_historical_data(self, session, symbol, pbar):
        endpoint = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={self.params["tf"]}&limit={self.params["limit"]}'
        response = await self.fetch(session, endpoint)
        symbol_df = pd.DataFrame(response, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                                                    'Quote asset volume', 'Number of trades',
                                                    'Taker buy base asset volume', 'Taker buy quote asset volume',
                                                    'Ignore'])
        symbol_df['Symbol'] = symbol
        pbar.update(1)
        return symbol_df

    async def scrape(self):
        async with aiohttp.ClientSession() as session:
            response = await self.fetch(session, self.symbols_url)
            symbols_data = response['symbols']
            self.symbols_list = [symbol['symbol'] for symbol in symbols_data if symbol['symbol'].endswith('USDT')
                                 and symbol['status'] == "TRADING"]

            tasks = []
            with tqdm(total=len(self.symbols_list), desc="Async Progressbar") as pbar:
                for symbol in self.symbols_list:
                    task = asyncio.ensure_future(self.get_historical_data(session, symbol, pbar))
                    tasks.append(task)

                results = await asyncio.gather(*tasks)

        for result in tqdm(results, desc="Concatenate Symbols"):
            self.historical_data = pd.concat([self.historical_data, result], ignore_index=True)

        self.historical_data['Open time'] = pd.to_datetime(self.historical_data['Open time'], unit='ms')
        self.historical_data['Close time'] = pd.to_datetime(self.historical_data['Close time'], unit='ms')

        self.historical_data.set_index('Open time', inplace=True)

        self.historical_data.drop(
            ['Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
             'Taker buy quote asset volume', 'Ignore'], axis=1, inplace=True)

        self.historical_data.to_csv('binance_historical_data.csv')


# Create An ArgumentParser Object
parser = argparse.ArgumentParser(description='ArgumentParser Object For Getting Binance Scraper Pramaters In Console')

# Limit Keyword Arg
parser.add_argument('--limit', type=int, nargs='?', help='Limit Number of Candles (1 to 1000).')

# Timeframe Keyword Arg
parser.add_argument('--tf', type=str, nargs='?', help='Desired Timeframe [1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 8h, 1d].')

# Parse The Command-Line Arguments
args = parser.parse_args()

### Limit
if args.limit is None:
    limit = int(input('Enter Limit Number of Candles (1 to 1000): '))
else:
    limit = args.limit

### TF
if args.tf is None:
    tf = str(input('Enter Desired Timeframe [1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 8h, 1d]: '))
else:
    tf = args.tf


scraper = BinanceHistoricalDataScraper(tf=tf, limit=limit)
asyncio.run(scraper.scrape())
