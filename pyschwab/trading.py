from datetime import datetime, timedelta
from typing import Any, Dict, List

from dotenv import load_dotenv

from .utils import format_params, request, time_to_str, to_json_str
from .trading_models import Order, SecuritiesAccount, TradingData, Transaction, UserPreference
from .types import AssetType, MarketSession, OrderDuration, OrderInstruction, OrderStatus, OrderStrategyType, OrderType, TransactionType


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
        self.auth2 = {**self.auth, 'Content-Type': 'application/json'}
        response = request(f'{self.base_trader_url}/accounts/accountNumbers', headers=self.auth).json()
        self.accounts_hash = {account.get('accountNumber'): account.get('hashValue') for account in response}
        self.accounts: Dict[str, SecuritiesAccount] = {}
        self.current_account_num = None
 
    def get_accounts_hash(self) -> Dict[str, str]:
        return self.accounts_hash
 
    def set_current_account_number(self, account_number: str) -> None:
        self.current_account_num = account_number

    def get_current_account_number(self) -> str:
        return self.current_account_num

    def get_account_hash(self, account_number: str=None) -> str:
        return self.accounts_hash.get(account_number or self.current_account_num, None)
 
    def get_accounts(self) -> Dict[str, SecuritiesAccount]:
        return self.accounts
 
    def get_account(self, account_number: str=None) -> SecuritiesAccount:
        return self.accounts.get(account_number or self.current_account_num, None)

    def _get_account_hash(self, account_num: int | str=None) -> str:
        account_num = account_num or self.current_account_num
        if not account_num:
            raise ValueError("Account number not set")

        account_hash = self.accounts_hash.get(str(account_num), None)
        if account_hash is None:
            raise ValueError(f"Account number {account_num} not found.")
        return account_hash
 
    def get_user_preference(self):
        response = request(f'{self.base_trader_url}/userPreference', headers=self.auth).json()
        return UserPreference.from_dict(response)

    def fetch_trading_data(self, include_pos: bool=True) -> TradingData:
        account_hash = self._get_account_hash()
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

    def get_all_orders(self, start_time: datetime=None, end_time: datetime=None, status: OrderStatus=None, max_results: int=100) -> List[Order]:
        now = datetime.now()
        start = time_to_str(start_time or now - timedelta(days=30))
        end = time_to_str(end_time or now)
        params = {'maxResults': max_results, 'fromEnteredTime': start, 'toEnteredTime': end, 'status': status}
        orders = request(f'{self.base_trader_url}/orders', headers=self.auth, params=format_params(params)).json()
        return [Order.from_dict(order) for order in orders]

    def get_orders(self, start_time: datetime=None, end_time: datetime=None, status: OrderStatus=None, max_results: int=100) -> List[Order]:
        account_hash = self._get_account_hash()
        now = datetime.now()
        start = time_to_str(start_time or now - timedelta(days=30))
        end = time_to_str(end_time or now)
        params = {'maxResults': max_results, 'fromEnteredTime': start, 'toEnteredTime': end, 'status': status}
        orders = request(f'{self.base_trader_url}/accounts/{account_hash}/orders', headers=self.auth, params=format_params(params)).json()
        return [Order.from_dict(order) for order in orders]

    def get_order(self, order_id: str, account_num: int | str=None) -> Order:
        account_hash = self._get_account_hash(account_num)
        order = request(f'{self.base_trader_url}/accounts/{account_hash}/orders/{order_id}', headers=self.auth).json()
        return Order.from_dict(order)

    def place_order(self, order: Dict[str, Any] | Order) -> None:
        account_hash = self._get_account_hash()
        order_dict = self._convert_order(order)
        request(f'{self.base_trader_url}/accounts/{account_hash}/orders', method='POST', headers=self.auth, json=order_dict)

    def cancel_order(self, order_id: int | str) -> None:
        account_hash = self._get_account_hash()
        request(f'{self.base_trader_url}/accounts/{account_hash}/orders/{order_id}', method='DELETE', headers=self.auth)

    def replace_order(self, order: Dict[str, Any] | Order) -> None:
        order_dict = self._convert_order(order)
        order_id = order_dict.get('orderId', None)
        if not order_id:
            raise ValueError("Order ID not found in order data.")

        account_hash = self._get_account_hash()
        order_json = to_json_str(order_dict)
        request(f'{self.base_trader_url}/accounts/{account_hash}/orders/{order_id}', method='PUT', headers=self.auth2, data=order_json)

    def preview_order(self, order: Dict[str, Any] | Order) -> Dict[str, Any]:
        """Coming Soon as per official document"""
        account_hash = self._get_account_hash()
        order_dict = self._convert_order(order)
        order_json = to_json_str(order_dict)
        return request(f'{self.base_trader_url}/accounts/{account_hash}/previewOrder', method='POST', headers=self.auth2, data=order_json).json()

    def _convert_order(self, order: Dict[str, Any] | Order) -> Dict[str, Any]:
        if isinstance(order, Dict):
            return order

        if isinstance(order, Order):
            return order.to_dict(clean_keys=True)
 
        raise ValueError("Order must be a dictionary or Order object.")

    def get_transactions(self, start_time: datetime=None, end_time: datetime=None, symbol: str=None, types: TransactionType=TransactionType.TRADE) -> List[Transaction]:
        account_hash = self._get_account_hash()
        now = datetime.now()
        start = time_to_str(start_time or now - timedelta(days=30))
        end = time_to_str(end_time or now)
        params = {'startDate': start, 'endDate': end, 'symbol': symbol, 'types': types}
        transactions = request(f'{self.base_trader_url}/accounts/{account_hash}/transactions', headers=self.auth, params=format_params(params)).json()
        return [Transaction.from_dict(transaction) for transaction in transactions]

    def get_transaction(self, transaction_id: str) -> Transaction:
        account_hash = self._get_account_hash()
        transaction = request(f'{self.base_trader_url}/accounts/{account_hash}/transactions/{transaction_id}', headers=self.auth).json()
        return Transaction.from_dict(transaction)
