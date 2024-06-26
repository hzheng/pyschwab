
# Schwab API Python Library

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A Python library for interacting with the Schwab API, providing simple access to trading and market data.

## Prerequisites
1. You need to have a Schwab brokerage account.
2. Become an Individual Developer via the [Schwab Developer Portal](https://developer.schwab.com/).
3. Create an individual developer app and wait until its status is "Ready for use".

## Installation

Install the library using pip:

```bash
pip install pyschwab
```

## Preparation

1. Change directory to your project directory
2. Copy [pyschwab.yaml](https://github.com/hzheng/pyschwab/blob/main/config/pyschwab.yaml) to your project's `config` directory.
3. Copy [env_example](https://github.com/hzheng/pyschwab/blob/main/env_example) to `.env` and replace the placeholders with your settings.

## Warning
**WARNING**: This library can place real orders on your Schwab brokerage account. Use this API at your own risk. The author and contributors are not responsible for any financial losses or unintended trades that may occur as a result of using this library. Ensure you fully understand the functionality and risks before using it in a live trading environment.

## Usage

Here are some sample usages:

```python
import yaml

from pyschwab.auth import Authorizer
from pyschwab.trading import TradingApi
from pyschwab.types import Symbol
from pyschwab.market import MarketApi

# Load configuration
with open("config/pyschwab.yaml", 'r') as file:
    app_config = yaml.safe_load(file)

# Authorization
# On the first run, this will open a browser for authorization.
# Follow the instructions. Subsequent runs will auto-refresh the access token.
# When refresh token expires, it will open browser for authorization again.
authorizer = Authorizer(app_config['auth'])

access_token = authorizer.get_access_token()
print(access_token)

# Example usage of trading APIs
trading_api = TradingApi(access_token, app_config['trading'])
trading_data = trading_api.fetch_trading_data()
# List positions
for position in trading_data.positions:
    print("position:", position)

# List transactions 
for transaction in trading_api.get_transactions():
    print("transaction:", transaction)

# Buy/Sell equity
trading_api.buy_equity("TSLA", quantity=10, price=100)
trading_api.sell_equity("TSLA", quantity=10, price=200)

# Buy/Sell option
symbol = Symbol("RDDT", expiration="260116", call_put=True, strike=50.00)
trading_api.buy_single_option(symbol, quantity=1, price=10)
# Or: trading_api.buy_option("RDDT  260116C00050000", quantity=1, price=10)

trading_api.sell_single_option(symbol, quantity=1, price=30)

# Buy Call Spread
trading_api.trade_spread("TSLA", 0.9,  "2024-05-31", buy_sell=True, call_put=True, strikes=[177.5, 180], quantity=1)

# List orders
for order in trading_api.get_orders():
    print("order:", order)

# Example usage of market APIs
market_api = MarketApi(access_token, app_config['market'])

# Get quotes
symbols = ['TSLA', 'NVDA']
quotes = market_api.get_quotes(symbols)
for symbol in symbols:
    print("quote for ", symbol, ":", quotes[symbol])

# Get option chains
option_chain = market_api.get_option_chains('TSLA')
print(option_chain)

# Get price history 
history = market_api.get_price_history('TSLA')
print(history)
```

## Tests

To run the tests, use the following command:

```bash
pytest -s
```

You can customize the tests by editing the `test_api.json` file. Each test case has enabled/dry_run attribute that you can toggle. 

---

## License

MIT License

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
