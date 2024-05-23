from enum import Enum, auto
from typing import Optional, Type, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator


class PeriodFrequency(BaseModel):
    period_type: str = Field(default="day", description="The chart period being requested", json_schema_extra={"example": "day"})
    period: Optional[int] = Field(None, description="The number of chart period types", json_schema_extra={"example": 10})
    frequency_type: Optional[str] = Field(None, description="The time frequencyType", json_schema_extra={"example": "minute"})
    frequency: Optional[int] = Field(None, description="The time frequency duration", json_schema_extra={"example": 1})

    @field_validator('period_type')
    def validate_period_type(cls, v):
        if v not in ['day', 'month', 'year', 'ytd']:
            raise ValueError('Invalid period_type, must be one of: day, month, year, ytd')
        return v

    @model_validator(mode="before")
    def set_defaults(cls, values):
        if values.get('period_type') is None:
            values['period_type'] = 'day'
        if values.get('period') is None:
            default_periods = {
                'day': 10,
                'month': 1,
                'year': 1,
                'ytd': 1
            }
            values['period'] = default_periods.get(values.get('period_type'))

        if values.get('frequency_type') is None:
            default_frequency_types = {
                'day': 'minute',
                'month': 'weekly',
                'year': 'monthly',
                'ytd': 'weekly'
            }
            values['frequency_type'] = default_frequency_types.get(values.get('period_type'))

        if values.get('frequency') is None:
            values['frequency'] = 1

        return values

    @field_validator('period')
    def validate_period(cls, v, info):
        if 'period_type' in info.data:
            valid_periods = {
                'day': [1, 2, 3, 4, 5, 10],
                'month': [1, 2, 3, 6],
                'year': [1, 2, 3, 5, 10, 15, 20],
                'ytd': [1]
            }
            period_type = info.data['period_type']
            valid_period = valid_periods.get(period_type, None)
            if not valid_period:
                raise ValueError(f'Invalid period type: {period_type}')
            if v not in valid_period:
                raise ValueError(f'Invalid period for period_type {period_type}, must be one of: {valid_period}')
        return v

    @field_validator('frequency_type')
    def validate_frequency_type(cls, v, info):
        if 'period_type' in info.data:
            valid_frequency_types = {
                'day': ['minute'],
                'month': ['daily', 'weekly'],
                'year': ['daily', 'weekly', 'monthly'],
                'ytd': ['daily', 'weekly']
            }
            period_type = info.data['period_type']
            valid_frequency_type = valid_frequency_types.get(period_type, None)
            if not valid_frequency_type:
                raise ValueError(f'Invalid period type: {period_type}')
            if v not in valid_frequency_type:
                raise ValueError(f'Invalid frequency_type for period_type {period_type}, must be one of: {valid_frequency_type}')

        return v

    @field_validator('frequency')
    def validate_frequency(cls, v, info):
        if 'frequency_type' in info.data:
            valid_frequencies = {
                'minute': [1, 5, 10, 15, 30],
                'daily': [1],
                'weekly': [1],
                'monthly': [1]
            }
            frequency_type = info.data['frequency_type']
            valid_frequency = valid_frequencies.get(frequency_type, None)
            if not valid_frequency:
                raise ValueError(f'Invalid frequency type: {frequency_type}')
            if v not in valid_frequency:
                raise ValueError(f'Invalid frequency for frequency_type {frequency_type}, must be one of: {valid_frequency}')
        return v


T = TypeVar('T', bound='AutoName')


class AutoName(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

    @classmethod
    def from_str(cls: Type[T], s: str | T) -> T:
        if s is None or isinstance(s, cls):
            return s
        try:
            return cls[s]
        except KeyError:
            raise ValueError(f"{s} is not a valid {cls.__name__}")


class AutoNameLower(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower().replace('_', '-')


class MarketSession(AutoName):
    NORMAL = auto()
    AM = auto()
    PM = auto()
    SEAMLESS = auto()


class OrderType(AutoName):
    MARKET = auto()
    LIMIT = auto()
    STOP = auto()
    STOP_LIMIT = auto()
    TRAILING_STOP = auto()
    CABINET = auto()
    NON_MARKETABLE = auto()
    MARKET_ON_CLOSE = auto()
    EXERCISE = auto()
    TRAILING_STOP_LIMIT = auto()
    NET_DEBIT = auto()
    NET_CREDIT = auto()
    NET_ZERO = auto()
    LIMIT_ON_CLOSE = auto()
    UNKNOWN = auto()


class OrderInstruction(AutoName):
    BUY = auto()
    SELL = auto()
    BUY_TO_COVER = auto()
    SELL_SHORT = auto()
    BUY_TO_OPEN = auto()
    BUY_TO_CLOSE = auto()
    SELL_TO_OPEN = auto()
    SELL_TO_CLOSE = auto()
    EXCHANGE = auto()
    SELL_SHORT_EXEMPT = auto()


class OrderDuration(AutoName):
    DAY = auto()
    GOOD_TILL_CANCEL = auto()
    FILL_OR_KILL = auto()
    IMMEDIATE_OR_CANCEL = auto()
    END_OF_WEEK = auto()
    END_OF_MONTH = auto()
    NEXT_END_OF_MONTH = auto()
    UNKNOWN = auto


class OrderStrategyType(AutoName):
    SINGLE = auto()
    CANCEL = auto()
    RECALL = auto()
    PAIR = auto()
    FLATTEN = auto()
    TWO_DAY_SWAP = auto()
    BLAST_ALL = auto()
    OCO = auto()
    TRIGGER = auto()


class ComplexOrderStrategyType(AutoName):
    NONE = auto()
    COVERED = auto()
    VERTICAL = auto()
    BACK_RATIO = auto()
    CALENDAR = auto()
    DIAGONAL = auto()
    STRADDLE = auto()
    STRANGLE = auto()
    COLLAR_SYNTHETIC = auto()
    BUTTERFLY = auto()
    CONDOR = auto()
    IRON_CONDOR = auto()
    VERTICAL_ROLL = auto()
    COLLAR_WITH_STOCK = auto()
    DOUBLE_DIAGONAL = auto()
    UNBALANCED_BUTTERFLY = auto()
    UNBALANCED_CONDOR = auto()
    UNBALANCED_IRON_CONDOR = auto()
    UNBALANCED_VERTICAL_ROLL = auto()
    MUTUAL_FUND_SWAP = auto()
    CUSTOM = auto()


class PositionEffect(AutoName):
    OPENING = auto()
    CLOSING = auto()
    AUTOMATIC = auto()


class QuantityType(AutoName):
    ALL_SHARES = auto()
    DOLLARS = auto()
    SHARES = auto()


class AssetType(AutoName):
    EQUITY = auto()
    OPTION = auto()
    INDEX = auto()
    MUTUAL_FUND = auto()
    CASH_EQUIVALENT = auto()
    FIXED_INCOME = auto()
    CURRENCY = auto()
    COLLECTIVE_INVESTMENT = auto()


class OptionAssetType(AutoName):
    EQUITY = AssetType.EQUITY.value
    OPTION = AssetType.OPTION.value
    INDEX = AssetType.INDEX.value
    MUTUAL_FUND = AssetType.MUTUAL_FUND.value
    CASH_EQUIVALENT = AssetType.CASH_EQUIVALENT.value
    FIXED_INCOME = AssetType.FIXED_INCOME.value
    CURRENCY = AssetType.CURRENCY.value
    COLLECTIVE_INVESTMENT = AssetType.COLLECTIVE_INVESTMENT.value
    FUTURE = auto()
    FOREX = auto()
    PRODUCT = auto()


class OptionActionType(AutoName):
    PUT = auto()
    CALL = auto()
    UNKNOWN = auto()


class OrderStatus(AutoName):
    AWAITING_PARENT_ORDER = auto()
    AWAITING_CONDITION = auto()
    AWAITING_STOP_CONDITION = auto()
    AWAITING_MANUAL_REVIEW = auto()
    ACCEPTED = auto()
    AWAITING_UR_OUT = auto()
    PENDING_ACTIVATION = auto()
    QUEUED = auto()
    WORKING = auto()
    REJECTED = auto()
    PENDING_CANCEL = auto()
    CANCELED = auto()
    PENDING_REPLACE = auto()
    REPLACED = auto()
    FILLED = auto()
    EXPIRED = auto()
    NEW = auto()
    AWAITING_RELEASE_TIME = auto()
    PENDING_ACKNOWLEDGEMENT = auto()
    PENDING_RECALL = auto()
    UNKNOWN = auto()


class RequestedDestination(AutoName):
    INET = auto()
    ECN_ARCA = auto()
    CBOE = auto()
    AMEX = auto()
    PHLX = auto()
    ISE = auto()
    BOX = auto()
    NYSE = auto()
    NASDAQ = auto()
    BATS = auto()
    C2 = auto()
    AUTO = auto()


class TransactionType(AutoName):
    TRADE = auto()
    RECEIVE_AND_DELIVER = auto()
    DIVIDEND_OR_INTEREST = auto()
    ACH_RECEIPT = auto()
    ACH_DISBURSEMENT = auto()
    CASH_RECEIPT = auto()
    CASH_DISBURSEMENT = auto()
    ELECTRONIC_FUND = auto()
    WIRE_OUT = auto()
    WIRE_IN = auto()
    JOURNAL = auto()
    MEMORANDUM = auto()
    MARGIN_CALL = auto()
    MONEY_MARKET = auto()
    SMA_ADJUSTMENT = auto()


class SecuritySearch(AutoNameLower):
    SYMBOL_SEARCH = auto()
    SYMBOL_REGEX = auto()
    DESC_SEARCH = auto()
    DESC_REGEX = auto()
    SEARCH = auto()
    FUNDAMENTAL = auto()


class MarketType(AutoNameLower):
    EQUITY = auto()
    OPTION = auto()
    BOND= auto()
    FUTURE = auto()
    FOREX = auto()


class OptionStrategy(AutoName):
    SINGLE = auto()
    ANALYTICAL = auto()
    COVERED = auto()
    VERTICAL = auto()
    CALENDAR = auto()
    STRANGLE = auto()
    STRADDLE = auto()
    BUTTERFLY = auto()
    CONDOR = auto()
    DIAGONAL = auto()
    COLLAR = auto()
    ROLL = auto()


class MoverSort(AutoName):
    VOLUME = auto()
    TRADES = auto()
    PERCENT_CHANGE_UP = auto()
    PERCENT_CHANGE_DOWN = auto()
