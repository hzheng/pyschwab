from typing import Any, Dict

from dotenv import load_dotenv

from .utils import request
from .trading_models import SecuritiesAccount, TradingData


"""
Schwab Trading API

Reference: https://beta-developer.schwab.com/products/trader-api--individual/details/specifications/Retail%20Trader%20API%20Production
"""
class TradingApi:
    base_trader_url: str

    def __init__(self, access_token: str, trading_config: Dict[str, Any]):
        load_dotenv()
        self.base_trader_url = trading_config['base_trader_url']
        self.auth = {'Authorization': f'Bearer {access_token}'}
        response = request(f'{self.base_trader_url}/accounts/accountNumbers', headers=self.auth).json()
        self.accounts_hash = {account.get('accountNumber'): account.get('hashValue') for account in response}
        self.accounts: Dict[str, SecuritiesAccount] = {}
 
    def get_accounts_hash(self) -> Dict[str, str]:
        return self.accounts_hash
 
    def get_account_hash(self, account_number: str) -> str:
        return self.accounts_hash.get(account_number, None)
 
    def get_accounts(self) -> Dict[str, SecuritiesAccount]:
        return self.accounts
 
    def get_account(self, account_number: str) -> SecuritiesAccount:
        return self.accounts.get(account_number, None)

    def fetch_trading_data(self, account_num: str, include_pos: bool=True) -> TradingData:
        account_hash = self.accounts_hash.get(account_num, None)
        if account_hash is None:
            raise ValueError(f"Account number {account_num} not found.")

        params = {'fields': ['positions'] if include_pos else []}
        resp = request(f'{self.base_trader_url}/accounts/{account_hash}', headers=self.auth, params=params).json()
        trading_data = TradingData.from_dict(resp)
        account = trading_data.account
        self.accounts[account.account_number] = account
        return trading_data


    def fetch_all_trading_data(self, include_pos: bool=True) -> Dict[str, TradingData]:
        params = {'fields': ['positions'] if include_pos else []}
        trading_data_map = {}
        for resp in request(f'{self.base_trader_url}/accounts/', headers=self.auth, params=params).json():
            trading_data = TradingData.from_dict(resp)
            account = trading_data.account
            account_num = account.account_number
            trading_data_map[account_num] = trading_data
            self.accounts[account_num] = account
        return trading_data_map
