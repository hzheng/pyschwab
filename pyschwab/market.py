from typing import Any, Dict, List

from dotenv import load_dotenv

from .utils import format_params, request, format_list
from .market_models import Quote


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
