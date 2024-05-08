from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .utils import camel_to_snake, str_to_time


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
class Instrument:
    """
    Represents the financial instrument in a trading position.
    
    Attributes:
        asset_type (str): The type of the asset, e.g., 'EQUITY'.
        cusip (str): The CUSIP identifier for the instrument.
        symbol (str): The trading symbol for the instrument.
        net_change (float): The net change in the instrument's value since the last close.
        instrument_id (int): The id of the instrument
    """
    asset_type: str
    cusip: str
    symbol: str
    net_change: float = 0.0
    instrument_id: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Instrument':
        """
        Create an instrument instance from a dictionary with camelCase keys.
        """
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
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
    activity_type: str
    execution_type: str
    quantity: int
    order_remaining_quantity: int
    execution_legs: List[ExecutionLeg]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderActivity':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['execution_legs'] = [ExecutionLeg.from_dict(leg) for leg in converted_data['execution_legs']]
        return cls(**converted_data)


@dataclass
class OrderLeg:
    order_leg_type: str
    leg_id: int
    instrument: Instrument
    instruction: str
    position_effect: str
    quantity: int
    quantity_type: str = None
    div_cap_gains: str = None
    to_symbol: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderLeg':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['instrument'] = Instrument.from_dict(converted_data['instrument'])
        return cls(**converted_data)


@dataclass
class Order:
    order_id: int
    order_type: str
    session: str
    status: str
    price: float
    quantity: int
    filled_quantity: int
    remaining_quantity: int
    duration: str
    entered_time: datetime
    close_time: datetime
    release_time: datetime
    complex_order_strategy_type: str
    requested_destination: str
    destination_link_name: str
    cancelable: bool
    editable: bool
    account_number: int
    order_leg_collection: List[OrderLeg] = None
    order_activity_collection: List[OrderActivity] = None
    stop_price: float = 0.0
    stop_price_link_basis: str = None
    stop_price_link_type: str = None
    stop_price_offset: float = None
    stop_type: str = None
    price_link_basis: str = None
    price_link_type: str = None
    tax_lot_method: str = None
    activation_price: float = 0.0
    special_instruction: str = None
    order_strategy_type: str = None
    cancel_time: datetime = None
    tag: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        for key in ['cancel_time', 'release_time', 'entered_time', 'close_time']:
            converted_data[key] = str_to_time(converted_data.get(key, None))
        converted_data['order_leg_collection'] = [OrderLeg.from_dict(leg) for leg in converted_data.get('order_leg_collection', [])]
        converted_data['order_activity_collection'] = [OrderActivity.from_dict(activity) for activity in converted_data.get('order_activity_collection', [])]
        return cls(**converted_data)
