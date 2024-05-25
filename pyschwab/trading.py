from datetime import datetime, timedelta
from typing import Any, Dict, List

from dotenv import load_dotenv

from .utils import format_params, remove_none_values, request, time_to_str, to_json_str
from .trading_models import Instrument, Order, OrderLeg, SecuritiesAccount, TradingData, Transaction, UserPreference
from .types import AssetType, ExecutionType, MarketSession, OrderDuration, OrderInstruction, OrderStatus, \
    OrderStrategyType, OrderType, Symbol, TransactionType


"""
Schwab Trading API

Reference: https://developer.schwab.com/products/trader-api--individual/details/specifications/Retail%20Trader%20API%20Production
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

    def get_all_orders(self, start_time: datetime=None, end_time: datetime=None, status: OrderStatus=None, max_results: int=None) -> List[Order]:
        now = datetime.now()
        start = time_to_str(start_time or now - timedelta(days=60))
        end = time_to_str(end_time or now + timedelta(days=1))
        params = {'maxResults': max_results, 'fromEnteredTime': start, 'toEnteredTime': end, 'status': status}
        orders = request(f'{self.base_trader_url}/orders', headers=self.auth, params=format_params(params)).json()
        return [Order.from_dict(order) for order in orders]

    def get_orders(self, start_time: datetime=None, end_time: datetime=None, status: OrderStatus=None, max_results: int=None) -> List[Order]:
        account_hash = self._get_account_hash()
        now = datetime.now()
        start = time_to_str(start_time or now - timedelta(days=60))
        end = time_to_str(end_time or now + timedelta(days=1))
        params = {'maxResults': max_results, 'fromEnteredTime': start, 'toEnteredTime': end, 'status': status}
        orders = request(f'{self.base_trader_url}/accounts/{account_hash}/orders', headers=self.auth, params=format_params(params)).json()
        return [Order.from_dict(order) for order in orders]

    @staticmethod
    def is_active_order(order: Order) -> bool:
        if order.status.is_inactive():
            return False

        activities = order.order_activity_collection
        if activities:
            if activities[0].execution_type == ExecutionType.CANCELED:
                return False
        return order.cancel_time is None

    def get_open_orders(self, start_time: datetime=None, end_time: datetime=None) -> List[Order]:
        orders = []
        for status in [OrderStatus.WORKING, OrderStatus.PENDING_ACTIVATION]:
            orders.extend(self.get_orders(start_time, end_time, status=status))
        return orders

    def get_order(self, order_id: str, account_num: int | str=None) -> Order:
        account_hash = self._get_account_hash(account_num)
        order = request(f'{self.base_trader_url}/accounts/{account_hash}/orders/{order_id}', headers=self.auth).json()
        return Order.from_dict(order)

    def place_order(self, order: Dict[str, Any] | Order) -> None:
        account_hash = self._get_account_hash()
        order_dict = self._convert_order(order)
        request(f'{self.base_trader_url}/accounts/{account_hash}/orders', method='POST', headers=self.auth, json=order_dict)
 
    def place_complex_order(self, price: float, leg_collection: List[OrderLeg],
                    strategy_type: OrderStrategyType=OrderStrategyType.SINGLE, order_type: OrderType=OrderType.LIMIT,
                    duration: OrderDuration=OrderDuration.DAY, session: MarketSession=MarketSession.NORMAL) -> None:
        order = Order(price=price, order_leg_collection=leg_collection, order_strategy_type=strategy_type,
                      order_type=order_type, duration=duration, session=session)
        self.place_order(order)

    def place_single_order(self, symbol: str, quantity: int, price: float, instruction: OrderInstruction, 
            asset_type: AssetType=AssetType.EQUITY, order_type: OrderType=OrderType.LIMIT,
            duration: OrderDuration=OrderDuration.DAY, session: MarketSession=MarketSession.NORMAL) -> None:
        instrument = Instrument(symbol=symbol, asset_type=asset_type)
        leg_collection = [OrderLeg(instruction=instruction, quantity=quantity, instrument=instrument)]
        self.place_complex_order(price=price, leg_collection=leg_collection, strategy_type=OrderStrategyType.SINGLE,
                                 order_type=order_type, duration=duration, session=session)
 
    def buy_equity(self, symbol: str, quantity: int, price: float, order_type: OrderType=OrderType.LIMIT,
                   duration: OrderDuration=OrderDuration.DAY, session: MarketSession=MarketSession.NORMAL) -> None:
        self.place_single_order(symbol=symbol, quantity=quantity, price=price, instruction=OrderInstruction.BUY,
                                order_type=order_type, duration=duration, session=session)
 
    def sell_equity(self, symbol: str, price: float, quantity: int, order_type: OrderType=OrderType.LIMIT,
                   duration: OrderDuration=OrderDuration.DAY, session: MarketSession=MarketSession.NORMAL) -> None:
        self.place_single_order(symbol=symbol, quantity=quantity, price=price, instruction=OrderInstruction.SELL,
                                order_type=order_type, duration=duration, session=session)
 
    def buy_single_option(self, symbol: Symbol | str, quantity: int, price: float, order_type: OrderType=OrderType.LIMIT,
                          duration: OrderDuration=OrderDuration.DAY, session: MarketSession=MarketSession.NORMAL) -> None:
        self.place_single_order(symbol=str(symbol), quantity=quantity, price=price, instruction=OrderInstruction.BUY_TO_OPEN,
                                asset_type=AssetType.OPTION, order_type=order_type, duration=duration, session=session)
 
    def sell_single_option(self, symbol: Symbol | str, quantity: int, price: float, order_type: OrderType=OrderType.LIMIT,
                           duration: OrderDuration=OrderDuration.DAY, session: MarketSession=MarketSession.NORMAL) -> None:
        self.place_single_order(symbol=str(symbol), quantity=quantity, price=price, instruction=OrderInstruction.SELL_TO_CLOSE,
                                asset_type=AssetType.OPTION, order_type=order_type, duration=duration, session=session)

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
        order_dict = None
        if isinstance(order, Dict):
            order_dict = order
        elif isinstance(order, Order):
            order_dict = order.to_dict(clean_keys=True)
        else:
            raise ValueError("Order must be a dictionary or Order object.")
        return remove_none_values(order_dict)

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
