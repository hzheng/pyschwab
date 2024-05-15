from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .utils import camel_to_snake, to_time


@dataclass
class Fundamental:
    avg10_days_volume: float
    avg1_year_volume: float
    declaration_date: datetime
    div_amount: float
    div_ex_date: datetime
    div_freq: int
    div_pay_amount: float
    div_pay_date: datetime
    div_yield: float
    eps: float
    fund_leverage_factor: float
    last_earnings_date: datetime
    next_div_ex_date: datetime
    next_div_pay_date: datetime
    pe_ratio: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fundamental':
        if data is None:
            return data

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        for key in ['declaration_date', 'div_ex_date', 'div_pay_date', 'last_earnings_date', 'next_div_ex_date', 'next_div_pay_date']:
            converted_data[key] = to_time(converted_data.get(key, None))
        return cls(**converted_data)


@dataclass
class QuoteDetail:
    _52_week_high: float
    _52_week_low: float
    ask_mic_id: str
    ask_price: float
    ask_size: int
    ask_time: datetime
    bid_mic_id: str
    bid_price: float
    bid_size: int
    bid_time: datetime
    close_price: float
    high_price: float
    last_mic_id: str
    last_price: float
    last_size: int
    low_price: float
    mark: float
    mark_change: float
    mark_percent_change: float
    net_change: float
    net_percent_change: float
    open_price: float
    post_market_change: float
    post_market_percent_change: float
    quote_time: datetime
    security_status: str
    total_volume: int
    trade_time: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuoteDetail':
        if data is None:
            return data

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        for key in ['ask_time', 'bid_time', 'quote_time', 'trade_time']:
            converted_data[key] = to_time(converted_data.get(key, None))
        return cls(**converted_data)


@dataclass
class Reference:
    cusip: str
    description: str
    exchange: str
    exchange_name: str
    is_hard_to_borrow: bool
    is_shortable: bool
    htb_rate: float
    htb_quantity: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reference':
        if data is None:
            return data

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        return cls(**converted_data)


@dataclass
class RegularMarket:
    regular_market_last_price: float
    regular_market_last_size: int
    regular_market_net_change: float
    regular_market_percent_change: float
    regular_market_trade_time: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegularMarket':
        if data is None:
            return data

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        for key in ['regular_market_trade_time']:
            converted_data[key] = to_time(converted_data.get(key, None))
        return cls(**converted_data)


@dataclass
class Quote:
    asset_main_type: str
    asset_sub_type: str
    quote_type: str
    realtime: bool
    ssid: int
    symbol: str
    fundamental: Fundamental
    quote: QuoteDetail
    reference: Reference
    regular: RegularMarket

    @classmethod
    def from_dict(cls, data):
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['fundamental'] = Fundamental.from_dict(converted_data.get('fundamental', None))
        converted_data['quote'] = QuoteDetail.from_dict(converted_data.get('quote', None))
        converted_data['reference'] = Reference.from_dict(converted_data.get('reference', None))
        converted_data['regular'] = RegularMarket.from_dict(converted_data.get('regular', None))
        return cls(**converted_data)


@dataclass
class Deliverable:
    symbol: str
    asset_type: str
    deliverable_units: str
    # currency_type: str
 
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Deliverable':
        if data is None:
            return None

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        return cls(**converted_data)


@dataclass
class OptionDetail:
    put_call: str
    symbol: str
    description: str
    exchange_name: str
    bid: float
    ask: float
    last: float
    mark: float
    bid_ask_size: str
    bid_size: int
    ask_size: int
    last_size: int
    high_price: float
    low_price: float
    open_price: float
    close_price: float
    high52_week: float
    low52_week: float
    total_volume: int
    quote_time_in_long: int
    trade_time_in_long: int
    net_change: float
    volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    time_value: float
    open_interest: int
    in_the_money: bool
    theoretical_option_value: float
    theoretical_volatility: float
    mini: bool
    non_standard: bool
    option_deliverables_list: List[Deliverable]
    strike_price: float
    expiration_date: str
    exercise_type: str
    days_to_expiration: int
    expiration_type: str
    last_trading_day: int
    multiplier: float
    settlement_type: str
    deliverable_note: str
    percent_change: float
    mark_change: float
    mark_percent_change: float
    penny_pilot: bool
    intrinsic_value: float
    extrinsic_value: float
    option_root: str
    trade_date: int = 0
 
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptionDetail':
        if data is None:
            return None

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['option_deliverables_list'] = [Deliverable.from_dict(deliverable) for deliverable in converted_data['option_deliverables_list']]
        return cls(**converted_data)


@dataclass
class Underlying:
    ask: float
    ask_size: int
    bid: float
    bid_size: int
    change: float
    close: float
    delayed: bool
    description: str
    exchange_name: str
    fifty_two_week_high: float
    fifty_two_week_low: float
    high_price: float
    last: float
    low_price: float
    mark: float
    mark_change: float
    mark_percent_change: float
    open_price: float
    percent_change: float
    quote_time: int
    symbol: str
    total_volume: int
    trade_time: int
 
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Underlying':
        if data is None:
            return None

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        return cls(**converted_data)


@dataclass
class OptionChain:
    symbol: str
    status: str
    asset_main_type: str
    asset_sub_type: str
    strategy: str
    interval: float
    is_delayed: bool
    is_index: bool
    is_chain_truncated: bool
    days_to_expiration: int
    number_of_contracts: int
    interest_rate: float
    underlying_price: float
    volatility: float
    call_exp_date_map: Dict[str, Dict[str, OptionDetail]]
    put_exp_date_map: Dict[str, Dict[str, OptionDetail]]
    underlying: Underlying = None
 
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptionChain':
        if data is None:
            return None

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        converted_data['underlying'] = Underlying.from_dict(converted_data.get('underlying', None))
        converted_data['call_exp_date_map'] = cls._exp_date_map_from_dict(converted_data['call_exp_date_map'])
        converted_data['put_exp_date_map'] = cls._exp_date_map_from_dict(converted_data['put_exp_date_map'])
        return cls(**converted_data)

    @classmethod
    def _exp_date_map_from_dict(cls, exp_data_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, OptionDetail]]:
        return {exp_date: {strike_price: OptionDetail.from_dict(option_detail[0]) for strike_price, option_detail in exp_data.items()} for exp_date, exp_data in exp_data_map.items()}


@dataclass
class OptionExpiration:
    expiration_date: str
    days_to_expiration: int
    expiration_type: str
    settlement_type: str
    option_roots: str
    standard: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptionExpiration':
        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        return cls(**converted_data)


@dataclass
class Candle:
    datetime: datetime
    open: float
    close: float
    low: float
    high: float
    volume: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Candle':
        if data is None:
            return data

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        key = 'datetime'
        converted_data[key] = to_time(converted_data.get(key, None))
        return cls(**converted_data)


@dataclass
class PriceHistory:
    candles: List[Candle]
    empty: bool
    symbol: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceHistory':
        if data is None:
            return data

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        candles = converted_data.get('candles', [])
        converted_data['candles'] = [ Candle.from_dict(candle) for candle in candles]
        return cls(**converted_data)


@dataclass
class SessionTime:
    start: datetime
    end: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionTime':
        for key in ['start', 'end']:
            data[key] = to_time(data.get(key, None))
        return cls(**data)


@dataclass
class SessionHours:
    pre_market: List[SessionTime] = field(default_factory=list)
    regular_market: List[SessionTime] = field(default_factory=list)
    post_market: List[SessionTime] = field(default_factory=list)
    outcry_market: List[SessionTime] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionHours':
        if data is None:
            return data

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        for key in ['pre_market', 'regular_market', 'post_market', 'outcry_market']:
            val = converted_data.get(key, None)
            if val:
                converted_data[key] = [SessionTime.from_dict(s) for s in val]
        return cls(**converted_data)


@dataclass
class MarketProduct:
    date: datetime
    market_type: str
    product: str
    is_open: bool
    session_hours: SessionHours
    product_name: str = None
    exchange: Optional[str] = None
    category: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionHours':
        if data is None:
            return data

        converted_data = {camel_to_snake(key): value for key, value in data.items()}
        session_hours = converted_data.get('session_hours', None)
        converted_data['session_hours'] = SessionHours.from_dict(session_hours)
        return cls(**converted_data)

@dataclass
class MarketHours:
    equity: Dict[str, MarketProduct] = field(default_factory=dict)
    option: Dict[str, MarketProduct] = field(default_factory=dict)
    bond: Dict[str, MarketProduct] = field(default_factory=dict)
    future: Dict[str, MarketProduct] = field(default_factory=dict)
    forex: Dict[str, MarketProduct] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionHours':
        if data is None:
            return data

        for key in ['equity', 'option', 'bond', 'future', 'forex']:
            val = data.get(key, {})
            data[key] = {symbol: MarketProduct.from_dict(product) for symbol, product in val.items()}
        return cls(**data)
