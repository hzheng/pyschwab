from datetime import datetime, timedelta
from typing import Any, Dict, List

from dotenv import load_dotenv

from .market_models import Quote, OptionChain, OptionExpiration, PriceHistory
from .types import PeriodFrequency
from .utils import format_list, format_params, request, time_to_int


"""
Schwab Market API

Reference: https://beta-developer.schwab.com/products/trader-api--individual/details/specifications/Market%20Data%20Production
"""
class MarketApi:
    base_market_url: str

    def __init__(self, access_token: str, market_config: Dict[str, Any]):
        load_dotenv()
        self.base_market_url = market_config['base_market_url']
        self.auth = {'Authorization': f'Bearer {access_token}'}
 
    def get_quotes(self, symbols: str | List[str], fields: str | List[str]=None, indicative: bool=False) -> Dict[str, Quote]:
        params = {'symbols': format_list(symbols), 'fields': format_list(fields), 'indicative': indicative}
        quotes = request(f'{self.base_market_url}/quotes', headers=self.auth, params=format_params(params)).json()
        return {symbol: Quote.from_dict(quote) for (symbol, quote) in quotes.items()}

    def get_quote(self, symbol: str, fields: str | List[str]=None) -> Quote:
        params = {'fields': format_list(fields)}
        quote = request(f'{self.base_market_url}/{symbol}/quotes', headers=self.auth, params=format_params(params)).json()
        if symbol not in quote:
            raise ValueError(f"Symbol {symbol} not found.")

        return Quote.from_dict(quote[symbol])

    def get_option_chains(self, symbol: str, contract_type=None, strategy=None, start=None, end=None,
                          days_to_expiration=None, exp_month=None, strike=None, strike_count=None,
                          include_underlying_quotes=None, interval=None, range=None, volatility=None,
                          underlying_price=None, interestRate=None, option_type=None, entitlement=None) -> OptionChain:
        params = {'symbol': symbol, 'contractType': contract_type, 'strikeCount': strike_count, 'includeUnderlyingQuotes': include_underlying_quotes, 
                  'strategy': strategy, 'interval': interval, 'strike': strike, 'range': range, 'fromDate': start, 'toDate': end, 'volatility': volatility, 'underlyingPrice': underlying_price,
                    'interestRate': interestRate, 'daysToExpiration': days_to_expiration, 'expMonth': exp_month, 'optionType': option_type, 'entitlement': entitlement}
        chains = request(f'{self.base_market_url}/chains', headers=self.auth, params=format_params(params)).json()
        return OptionChain.from_dict(chains)

    def get_option_expiration_chain(self, symbol: str) -> List[OptionExpiration]:
        params = {'symbol': symbol}
        chains = request(f'{self.base_market_url}/expirationchain', headers=self.auth, params=format_params(params)).json()
        return [OptionExpiration.from_dict(chain) for chain in chains['expirationList']]

    def get_price_history(self, symbol, period_freq: PeriodFrequency=PeriodFrequency(), start_date: datetime=None, end_date: datetime=None,
                          need_extended_hours_data: bool=False, need_previous_close: bool=False):
        now = datetime.now()
        start = time_to_int(start_date or now - timedelta(days=30))
        end = time_to_int(end_date or now)
        params = {'symbol': symbol, 'periodType': period_freq.period_type, 'period': period_freq.period,
                  'frequencyType': period_freq.frequency_type, 'frequency': period_freq.frequency,
                  'startDate': start, 'endDate': end,
                  'needExtendedHoursData': need_extended_hours_data, 'needPreviousClose': need_previous_close}
        history = request(f'{self.base_market_url}/pricehistory', headers=self.auth, params=format_params(params)).json()
        return PriceHistory.from_dict(history)
