from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

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
