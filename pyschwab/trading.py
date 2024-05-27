from datetime import datetime, timedelta
from typing import Any, Dict, List

from dotenv import load_dotenv

from .utils import format_params, remove_none_values, request, time_to_str, to_date, to_json_str
from .trading_models import AccountInfo, Instrument, Order, OrderLeg, SecuritiesAccount, TradingData, Transaction, UserPreference
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
        self.current_account_num = None
        self.primary_account_num = None
        self.securities_accounts: Dict[str, SecuritiesAccount] = {}
        self.accounts_info: Dict[str, AccountInfo] = {}
        self._init_accounts()

    def _init_accounts(self) -> None:
        response = request(f'{self.base_trader_url}/accounts/accountNumbers', headers=self.auth).json()
        accounts_hash = {account.get('accountNumber'): account.get('hashValue') for account in response}
        for account in self.get_user_preference().accounts:
            account_num = account.account_number
            account_hash = accounts_hash.get(account_num, None)
            is_primary = account.primary_account
            self.accounts_info[account_num] = AccountInfo(account_number=account_num,
                                                          account_hash=account_hash,
                                                          is_primary=is_primary,
                                                          type=account.type,
                                                          nick_name=account.nick_name,
                                                          display_id=account.display_acct_id)
            if is_primary:
                self.current_account_num = self.primary_account_num = account_num
 
    def get_accounts_info(self) -> Dict[str, AccountInfo]:
        return self.accounts_info
 
    def get_account_info(self, account_num: int | str) -> AccountInfo:
        account_info = self.accounts_info.get(str(account_num), None)
        if account_info is None:
            raise ValueError(f"Account number {account_num} not found.")

        return account_info
 
    def set_current_account_number(self, account_number: str=None) -> None:
        """Set the current account number. If not provided, it will be set to primary account's number."""
        self.current_account_num = account_number or self.primary_account_num

    def get_current_account_number(self) -> str:
        """Get the current account number. Initially it's primary account's number"""
        return self.current_account_num

    def get_securities_accounts(self) -> Dict[str, SecuritiesAccount]:
        return self.securities_accounts
 
    def get_securities_account(self, account_number: str=None) -> SecuritiesAccount:
        return self.securities_accounts.get(account_number or self.current_account_num, None)

    def _get_account_hash(self, account_num: int | str=None) -> str:
        account_num = account_num or self.current_account_num
        if not account_num:
            raise ValueError("Account number not set")

        account_info = self.get_account_info(account_num)
        return account_info.account_hash
 
    def get_user_preference(self) -> UserPreference:
        response = request(f'{self.base_trader_url}/userPreference', headers=self.auth).json()
        return UserPreference.from_dict(response)

    def fetch_trading_data(self, include_pos: bool=True) -> TradingData:
        account_hash = self._get_account_hash()
        params = {'fields': ['positions'] if include_pos else []}
        resp = request(f'{self.base_trader_url}/accounts/{account_hash}', headers=self.auth, params=params).json()
        trading_data = TradingData.from_dict(resp)
        account = trading_data.account
        self.securities_accounts[account.account_number] = account
        return trading_data

    def fetch_all_trading_data(self, include_pos: bool=True) -> Dict[str, TradingData]:
        params = {'fields': ['positions'] if include_pos else []}
        trading_data_map = {}
        for resp in request(f'{self.base_trader_url}/accounts/', headers=self.auth, params=params).json():
            trading_data = TradingData.from_dict(resp)
            account = trading_data.account
            account_num = account.account_number
            trading_data_map[account_num] = trading_data
            self.securities_accounts[account_num] = account
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
 
    def trade_spread(self, underlying: str, price: float, expiration: datetime | str, buy_sell: bool, call_put: bool, strikes: List[float], quantity: int,
                    duration: OrderDuration=OrderDuration.DAY, session: MarketSession=MarketSession.NORMAL) -> None:
        if len(strikes) != 2:
            raise ValueError("Must provide 2 strikes for a spread order.")

        if buy_sell ^ call_put: # For bear call spreads and bull put spreads, reverse the order
            strikes.reverse()
        else:
            strikes.sort()
        order_type = OrderType.NET_DEBIT if buy_sell else OrderType.NET_CREDIT
        instructions = [OrderInstruction.BUY_TO_OPEN, OrderInstruction.SELL_TO_OPEN]
        
        expiration_dt = to_date(expiration)
        leg_collection = []
        for i in range(2):
            symbol = Symbol(underlying, expiration=expiration_dt, call_put=call_put, strike=strikes[i])
            instrument = Instrument(symbol=str(symbol), asset_type=AssetType.OPTION)
            leg = OrderLeg(instrument=instrument, quantity=quantity, instruction=instructions[i])
            leg_collection.append(leg)
        order = Order(price=price, order_leg_collection=leg_collection, order_strategy_type=OrderStrategyType.SINGLE,
                      order_type=order_type, duration=duration, session=session)
        self.place_order(order)

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
