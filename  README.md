Binance Historical Data Scraper
======

This Python script scrapes historical data for all Binance trading pairs that end with "USDT". It uses asynchronous programming with the asyncio and aiohttp libraries to speed up the process. The scraped data is stored in a Pandas DataFrame and exported to a CSV file.

### Requirements

    Python 3.7+
    aiohttp
    pandas
    tqdm

### Usage

The script accepts two optional arguments:

    --limit (-l): The number of candles to retrieve for each trading pair. Must be an integer between 1 and 1000.
    --tf (-t): The desired timeframe for the candles. Must be one of the following values: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 8h, 1d.

If these arguments are not provided, the script will prompt the user to enter them.

#### To run the script with default values:

python binance_historical_data_scraper.py

#### To specify the limit and timeframe:

python binance_historical_data_scraper.py --limit 500 --tf 1h

### Output

The scraped data is saved as a CSV file named binance_historical_data.csv in the same directory as the script. The file contains the following columns: Symbol, Open, High, Low, Close, and Volume.

Acknowledgments
-------------------

    The tqdm library is used to show a progress bar during the scraping process.
    The Binance API documentation was referenced to construct the URLs used to fetch the data.