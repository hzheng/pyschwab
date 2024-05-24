from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .types import ActivityType, AssetType, ComplexOrderStrategyType, ExecutionType, MarketSession, OptionActionType, \
    OptionAssetType, OrderDuration, OrderInstruction, OrderStatus, OrderStrategyType, OrderType, \
    PositionEffect, QuantityType, RequestedDestination
from .utils import camel_to_snake, dataclass_to_dict, to_time


@dataclass
class SecuritiesAccount:
    """
    Represents a security account with various properties related to trading.
    
    Attributes:
        type (str): Type of the account (e.g., 'MARGIN').
        account_number (str): Unique identifier for the account.
        round_trips (int): Number of round trip transactions.
        is_day_trader (bool): True if the account is flagged as a day trader.
        is_closing_only_restricted (bool): True if the account is restricted to closing only trades.
        pfcb_flag (bool): Flag used for additional account policies (purpose not defined).
    """
    type: str
    account_number: str
    round_trips: int
    is_day_trader: bool
    is_closing_only_restricted: bool
    pfcb_flag: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecuritiesAccount':
        """
        Create a security account instance from a dictionary with camelCase keys.
        """
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        return cls(**converted_data)


@dataclass
class Deliverable:
    asset_type: OptionAssetType
    status: str
    symbol: str
    instrument_id: int
    closing_price: float
    type: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Deliverable':
        if data is None:
            return None
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['asset_type'] = OptionAssetType.from_str(converted_data['asset_type'])
        return cls(**converted_data)


@dataclass
class OptionDeliverable:
    deliverable_units: float
    deliverable: Deliverable
    root_symbol: str = None
    symbol: str = None
    strike_percent: int = None
    deliverable_number: int = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptionDeliverable':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        deliverable = converted_data.get('deliverable', None)
        converted_data['deliverable'] = Deliverable.from_dict(deliverable)
        return cls(**converted_data)


@dataclass
class Instrument:
    """
    Represents the financial instrument in a trading position.
    
    Attributes:
        asset_type (AssetType): The type of the asset, e.g., AssetType.EQUITY.
        symbol (str): The trading symbol for the instrument.
        cusip (str): The CUSIP identifier for the instrument.
        net_change (float): The net change in the instrument's value since the last close.
        instrument_id (int): The id of the instrument
    """
    symbol: str
    asset_type: AssetType = AssetType.EQUITY
    cusip: str = None
    net_change: float = None
    instrument_id: int = None
    description: str = None
    closing_price: float = None
    status: str = None
    type: str = None
    expiration_date: datetime = None
    option_deliverables: List[Deliverable] = None
    option_premium_multiplier: float = None
    put_call: OptionActionType = None
    strike_price: float = None
    underlying_symbol: str = None
    underlying_cusip: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Instrument':
        """
        Create an instrument instance from a dictionary with camelCase keys.
        """
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        expiration_time = converted_data.get('expiration_date', None)
        if expiration_time:
            converted_data['expiration_date'] = datetime.fromisoformat(expiration_time)
        deliverables = converted_data.get('option_deliverables', None)
        if deliverables:
            converted_data['option_deliverables'] = [OptionDeliverable.from_dict(deliverable) for deliverable in converted_data['option_deliverables']]
        converted_data['asset_type'] = AssetType.from_str(converted_data['asset_type'])
        converted_data['put_call'] = OptionActionType.from_str(converted_data.get('put_call', None))
        return cls(**converted_data)


@dataclass
class Position:
    """
    Represents a trading position.

    Attributes:
        short_quantity (float): Quantity of short positions.
        average_price (float): The average purchase price of the position.
        current_day_profitLoss (float): Profit or loss for the current trading day.
        current_day_profit_loss_percentage (float): Profit or loss percentage for the current trading day.
        long_quantity (float): Quantity of long positions.
        settled_long_quantity (float): Settled long quantity.
        settled_short_quantity (float): Settled short quantity.
        instrument (Instrument): The financial instrument involved in the position.
        market_value (float): Current market value of the position.
        maintenance_requirement (float): Maintenance requirement of the position.
        average_long_price (float): Average price of the long positions.
        tax_lot_average_long_price (float): Tax lot average price of the long positions.
        long_open_profit_loss (float): Open profit or loss on long positions.
        previous_session_long_quantity (float): Quantity of long positions from the previous session.
        current_day_cost (float): The cost associated with the current day's trading.
    """
    short_quantity: float = 0.0
    average_price: float = 0.0
    current_day_profit_loss: float = 0.0
    current_day_profit_loss_percentage: float = 0.0
    long_quantity: float = 0.0
    settled_long_quantity: float = 0.0
    settled_short_quantity: float = 0.0
    instrument: Instrument = None
    market_value: float = 0.0
    maintenance_requirement: float = 0.0
    average_long_price: float = 0.0
    tax_lot_average_long_price: float = 0.0
    long_open_profit_loss: float = 0.0
    previous_session_long_quantity: float = 0.0
    current_day_cost: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        """
        Create a position instance from a dictionary with camelCase keys.
        """
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        instrument_data = converted_data.pop('instrument')
        position = cls(**converted_data)
        position.instrument = Instrument.from_dict(instrument_data)
        return position

    @classmethod
    def from_list(cls, positions_data: List[dict]) -> List['Position']:
        return [Position.from_dict(position_data) for position_data in positions_data]


@dataclass
class Balance:
    """
    Represents the balance information for an account.
    """
    accrued_interest: float = 0.0
    available_funds_non_marginable_trade: float = 0.0
    bond_value: float = 0.0
    buying_power: float = 0.0
    cash_balance: float = 0.0
    cash_available_for_trading: float = 0.0
    cash_receipts: float = 0.0
    day_trading_buying_power: float = 0.0
    day_trading_buying_power_call: float = 0.0
    day_trading_equity_call: float = 0.0
    equity: float = 0.0
    equity_percentage: float = 0.0
    liquidation_value: float = 0.0
    long_margin_value: float = 0.0
    long_option_market_value: float = 0.0
    long_stock_value: float = 0.0
    maintenance_call: float = 0.0
    maintenance_requirement: float = 0.0
    margin: float = 0.0
    margin_equity: float = 0.0
    money_market_fund: float = 0.0
    mutual_fund_value: float = 0.0
    reg_t_call: float = 0.0
    short_margin_value: float = 0.0
    short_option_market_value: float = 0.0
    short_stock_value: float = 0.0
    total_cash: float = 0.0
    is_in_call: bool = False
    pending_deposits: float = 0.0
    margin_balance: float = 0.0
    short_balance: float = 0.0
    account_value: float = 0.0
    # other fields that don't appear in currentBalances
    available_funds: float = 0.0
    stock_buying_power: float = 0.0
    long_market_value: float = 0.0
    savings: float = 0.0
    short_market_value: float = 0.0
    buying_power_non_marginable_trade: float = 0.0
    sma: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a Balance instance from a dictionary with camelCase keys.
        """
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        return cls(**converted_data)


@dataclass
class TradingData:
    """
    Encapsulates all trading-related data fetched from an API call.
    
    Attributes:
        initial_balances (Balance): The initial balance details.
        current_balances (Balance): The current balance details.
        projected_balances (Optional[Balance]): The projected balance details, if available.
        positions (List[Position]): A list of positions.
        securities_account (SecuritiesAccount): Details of the securities account.
    """
    initial_balances: Balance
    current_balances: Balance
    projected_balances: Optional[Balance]
    positions: List[Position]
    account: SecuritiesAccount

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingData':
        """
        Create a TradingData instance from a dictionary with camelCase keys.
        """
        trading_info = data['securitiesAccount']
        initial_balances_data = trading_info.pop('initialBalances')
        initial_balances = Balance.from_dict(initial_balances_data)

        current_balances_data = trading_info.pop('currentBalances')
        current_balances = Balance.from_dict(current_balances_data)

        projected_balances_data = trading_info.pop('projectedBalances')
        projected_balances = Balance.from_dict(projected_balances_data)

        positions_data = trading_info.pop('positions', [])
        positions = Position.from_list(positions_data)

        account = SecuritiesAccount.from_dict(trading_info)

        return cls(
            initial_balances=initial_balances,
            current_balances=current_balances,
            projected_balances=projected_balances,
            positions=positions,
            account=account
        )


@dataclass
class ExecutionLeg:
    leg_id: int
    price: float
    quantity: int
    mismarked_quantity: int
    instrument_id: int
    time: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionLeg':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['time'] = datetime.fromisoformat(converted_data['time'])
        return cls(**converted_data)


@dataclass
class OrderActivity:
    activity_type: ActivityType
    execution_type: ExecutionType
    quantity: int
    order_remaining_quantity: int
    execution_legs: List[ExecutionLeg]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderActivity':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['activity_type'] = ActivityType.from_str(converted_data.get('activity_type', None))
        converted_data['execution_type'] = ExecutionType.from_str(converted_data.get('execution_type', None))
        converted_data['execution_legs'] = [ExecutionLeg.from_dict(leg) for leg in converted_data['execution_legs']]
        return cls(**converted_data)


@dataclass
class OrderLeg:
    instrument: Instrument
    instruction: OrderInstruction
    quantity: int
    position_effect: PositionEffect = None
    order_leg_type: AssetType = None
    quantity_type: QuantityType = None
    leg_id: int = None
    div_cap_gains: str = None
    to_symbol: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderLeg':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['instrument'] = Instrument.from_dict(converted_data['instrument'])
        converted_data['instruction'] = OrderInstruction.from_str(converted_data['instruction'])
        converted_data['position_effect'] = PositionEffect.from_str(converted_data.get('position_effect', None))
        converted_data['order_leg_type'] = AssetType.from_str(converted_data.get('order_leg_type', None))
        converted_data['quantity_type'] = QuantityType.from_str(converted_data.get('quantity_type', None))
        return cls(**converted_data)


@dataclass
class Order:
    price: float
    entered_time: datetime = None
    close_time: datetime = None
    release_time: datetime = None
    order_type: OrderType = OrderType.LIMIT
    duration: OrderDuration = OrderDuration.DAY
    session: MarketSession = MarketSession.NORMAL
    order_strategy_type: OrderStrategyType = OrderStrategyType.SINGLE
    order_id: int = None
    account_number: int = None
    status: OrderStatus = None
    quantity: int = None
    filled_quantity: int = None
    remaining_quantity: int = None
    complex_order_strategy_type: ComplexOrderStrategyType = None
    requested_destination: RequestedDestination = None
    destination_link_name: str = None
    order_leg_collection: List[OrderLeg] = None
    order_activity_collection: List[OrderActivity] = None
    stop_price: float = None
    stop_price_link_basis: str = None
    stop_price_link_type: str = None
    stop_price_offset: float = None
    stop_type: str = None
    price_link_basis: str = None
    price_link_type: str = None
    tax_lot_method: str = None
    activation_price: float = None
    special_instruction: str = None
    cancelable: bool = None
    editable: bool = None
    cancel_time: datetime = None
    tag: str = None
    status_description: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        for key in ['cancel_time', 'release_time', 'entered_time', 'close_time']:
            converted_data[key] = to_time(converted_data.get(key, None))
        converted_data['order_leg_collection'] = [OrderLeg.from_dict(leg) for leg in converted_data.get('order_leg_collection', [])]
        converted_data['order_activity_collection'] = [OrderActivity.from_dict(activity) for activity in converted_data.get('order_activity_collection', [])]
        converted_data['order_type'] = OrderType.from_str(converted_data['order_type'])
        converted_data['duration'] = OrderDuration.from_str(converted_data['duration'])
        converted_data['session'] = MarketSession.from_str(converted_data['session'])
        converted_data['order_strategy_type'] = OrderStrategyType.from_str(converted_data['order_strategy_type'])
        converted_data['status'] = OrderStatus.from_str(converted_data.get('status', None))
        converted_data['complex_order_strategy_type'] = ComplexOrderStrategyType.from_str(converted_data.get('complex_order_strategy_type', None))
        return cls(**converted_data)

    def to_dict(self, clean_keys: bool=False) -> Dict[str, Any]:
        order_dict = dataclass_to_dict(self)
        if clean_keys:
            for key in ['enteredTime', 'closeTime', 'releaseTime', 'cancelTime', # time
                        'remainingQuantity', 'filledQuantity', 'quantity', # quanity
                        'priceLinkBasis', 'priceLinkType', 'activationPrice', # price
                        'stopPriceLinkBasis', 'stopPrice', 'stopPriceOffset', 'stopType', # stop
                        'destinationLinkName', 'requestedDestination', # destination
                        'status', 'statusDescription', # status
                        'tag', # tag
                        'orderActivityCollection',
                        ]:
                del order_dict[key]
        return order_dict


@dataclass
class TransferItem:
    instrument: Instrument
    amount: float
    cost: float
    price: float = 0.0
    fee_type: str = None
    position_effect: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransferItem':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['instrument'] = Instrument.from_dict(converted_data['instrument'])
        return cls(**converted_data)


@dataclass
class User:
    cd_domain_id: str
    login: str
    type: str
    user_id: int
    system_user_name: str
    first_name: str
    last_name: str
    broker_rep_code: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        if data is None:
            return None

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        return cls(**converted_data)


@dataclass
class Transaction:
    activity_id: int
    time: datetime
    type: str
    status: str
    net_amount: float
    account_number: str
    sub_account: str
    transfer_items: List[TransferItem]
    user: User = None
    order_id: int = None
    position_id: int = None
    trade_date: datetime = None
    settlement_date: datetime = None
    description: str = None
    activity_type: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['user'] = User.from_dict(converted_data.get('user', None))
        for dt_key in ['time', 'trade_date', 'settlement_date']:
            dt = converted_data.get(dt_key, None)
            if dt:
                converted_data[dt_key] = datetime.fromisoformat(dt)
        converted_data['transfer_items'] = [TransferItem.from_dict(item) for item in converted_data['transfer_items']]
        return cls(**converted_data)


@dataclass
class Account:
    account_number: str
    primary_account: bool
    type: str
    nick_name: str
    display_acct_id: str
    auto_position_effect: bool
    account_color: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        return cls(**converted_data)


@dataclass
class StreamerInfo:
    streamer_socket_url: str
    schwab_client_customer_id: str
    schwab_client_correl_id: str
    schwab_client_channel: str
    schwab_client_function_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StreamerInfo':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        return cls(**converted_data)


@dataclass
class Offer:
    level2_permissions: bool
    mkt_data_permission: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Offer':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        return cls(**converted_data)


@dataclass
class UserPreference:
    accounts: List[Account]
    streamer_info: List[StreamerInfo]
    offers: List[Offer]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Offer':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['accounts'] = [Account.from_dict(account) for account in converted_data['accounts']]
        converted_data['streamer_info'] = [StreamerInfo.from_dict(streamer) for streamer in converted_data['streamer_info']]
        converted_data['offers'] = [Offer.from_dict(offer) for offer in converted_data['offers']]
        return cls(**converted_data)
