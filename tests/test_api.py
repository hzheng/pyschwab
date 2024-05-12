from datetime import datetime
from typing import Dict, List

import pytest
import logging
import yaml

from pyschwab.auth import Authorizer
from pyschwab.log import logger
from pyschwab.market import MarketApi
from pyschwab.market_models import OptionChain, OptionDetail
from pyschwab.trading import TradingApi
from pyschwab.trading_models import Order, TradingData
from pyschwab.utils import is_subset_object


@pytest.fixture(scope="module")
def app_config():
    with open("config/pyschwab.yaml", 'r') as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="function")
def logging_config():
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    yield logger
 
    logger.removeHandler(stream_handler)
    stream_handler.close()


def check_trading_data(trading_data: TradingData):
    assert trading_data is not None, "Expected trading data to be fetched"
    assert trading_data.initial_balances is not None, "Expected initial balance to be fetched"
    assert trading_data.current_balances is not None, "Expected current balance to be fetched"
    assert trading_data.projected_balances is not None, "Expected projected balance to be fetched"
    assert trading_data.account is not None, "Expected account to be fetched"
    assert trading_data.positions is not None, "Expected positions to be fetched"
    for position in trading_data.positions:
        assert position.instrument is not None, "Expected instrument to be fetched"
        assert position.instrument.asset_type is not None, "Expected asset type to be fetched"
        assert position.instrument.cusip is not None, "Expected cusip to be fetched"
        assert position.instrument.symbol is not None, "Expected symbol to be fetched"
        assert position.instrument.net_change is not None, "Expected net change to be fetched"


def check_orders(trading_api: TradingApi, orders: List[Order]):
    for order in orders:
        assert order is not None, "Expected order to be fetched"
        assert order.order_id is not None, "Expected order id to be fetched"
        assert order.order_type is not None, "Expected order type to be fetched"
        assert order.session is not None, "Expected order session to be fetched"
        assert order.status is not None, "Expected order status to be fetched"
        assert order.price is not None, "Expected order price to be fetched"
        assert order.quantity is not None, "Expected order quantity to be fetched"
        assert order.filled_quantity is not None, "Expected order filled quantity to be fetched"
        assert order.remaining_quantity is not None, "Expected order remaining quantity to be fetched"
        assert order.duration is not None, "Expected order duration to be fetched"
        assert order.entered_time is not None, "Expected order entered time to be fetched"
        # assert order.close_time is not None, "Expected order close time to be fetched"
        assert order.complex_order_strategy_type is not None, "Expected complex_order_strategy_type to be fetched"
        assert order.requested_destination is not None, "Expected requested_destination to be fetched"
        assert order.destination_link_name is not None, "Expected destination_link_name to be fetched"
        assert order.cancelable is not None, "Expected order cancelable to be fetched"
        assert order.editable is not None, "Expected order editable to be fetched"
        assert order.account_number is not None, "Expected order account number to be fetched"
        for leg in order.order_leg_collection:
            assert leg is not None, "Expected leg to be fetched"
            assert leg.order_leg_type is not None, "Expected order leg type to be fetched"
            assert leg.leg_id is not None, "Expected leg id to be fetched"
            assert leg.quantity is not None, "Expected leg quantity to be fetched"
            assert leg.instruction is not None, "Expected leg instruction to be fetched"
            assert leg.position_effect is not None, "Expected leg postion effect to be fetched"
            assert leg.instrument is not None, "Expected leg instrument to be fetched"
            assert leg.instrument.asset_type is not None, "Expected asset type to be fetched"
            assert leg.instrument.cusip is not None, "Expected cusip to be fetched"
            assert leg.instrument.symbol is not None, "Expected symbol to be fetched"
            assert leg.instrument.instrument_id is not None, "Expected instrument id to be fetched"
        for activity in order.order_activity_collection:
            assert activity is not None, "Expected activity to be fetched"
            assert activity.activity_type is not None, "Expected activity type to be fetched"
            assert activity.execution_type is not None, "Expected execution type to be fetched"
            assert activity.quantity is not None, "Expected quantity to be fetched"
            assert activity.order_remaining_quantity is not None, "Expected remaining quantity to be fetched"
            assert activity.execution_legs is not None, "Expected execution legs to be fetched"
            for leg in activity.execution_legs:
                assert leg is not None, "Expected leg to be fetched"
                assert leg.leg_id is not None, "Expected leg id to be fetched"
                assert leg.price is not None, "Expected price to be fetched"
                assert leg.quantity is not None, "Expected quantity to be fetched"
                assert leg.mismarked_quantity is not None, "Expected mismarked quantity to be fetched"
                assert leg.instrument_id is not None, "Expected instrument id to be fetched"
                assert leg.time is not None, "Expected time to be fetched"
                assert isinstance(leg.time, datetime), "Expected execution leg time to be a datetime"

        detailed_order = trading_api.get_order(order.account_number, order.order_id)
        assert detailed_order == order, "Expected detailed order to match order"


order_dict = {
    "orderType": "LIMIT", "session": "NORMAL", "duration": "DAY", "orderStrategyType": "SINGLE", "price": '100.00',
    "orderLegCollection": [
        {"instruction": "BUY", "quantity": 1, "instrument": {"symbol": "TSLA", "assetType": "EQUITY"}}
    ]
    }

test_account_number = 0 # CHANGE this to actual account number
test_order_id = 0 # CHANGE this to actual order id
test_order_type = [None, 'place_dict', 'place_obj', 'replace', 'cancel', 'preview'][0] # choose to test place order(dict/obj), replace, cancel, preview, or None


@pytest.mark.integration
def test_authentication_and_trading_data(app_config, logging_config):
    authorizer = Authorizer(app_config['auth'])
    access_token = authorizer.get_access_token()
    assert access_token is not None, "Failed to retrieve access token"

    trading_api = TradingApi(access_token, app_config['trading'])
    accounts_hash = trading_api.get_accounts_hash()
    assert isinstance(accounts_hash, dict), "Expected accounts hash to be a dict"
    assert len(accounts_hash) > 0, "Expected at least one account to be fetched"

    assert len(trading_api.get_accounts()) == 0, "Expected no accounts to be fetched initially"
    account_count = 0
    for account_num in accounts_hash:
        assert len(account_num) > 0, "Expected a non-empty account number to be fetched"
        trading_data = trading_api.fetch_trading_data(account_num)
        check_trading_data(trading_data)
        account_count += 1
        assert len(trading_api.get_accounts()) == account_count, f"Expected {account_count} account(s)"

    trading_data_map = trading_api.fetch_all_trading_data()
    assert isinstance(trading_data_map, dict), "Expected trading_data_map to be a dict"
    for account_num, trading_data in trading_data_map.items():
        assert len(account_num) > 0, "Expected a non-empty account number to be fetched"
        check_trading_data(trading_data)

    for account_num in accounts_hash:
        transactions = trading_api.get_transactions(account_num)
        for transaction in transactions:
            assert transaction is not None, "Expected transaction to be fetched"
            assert transaction.activity_id is not None, "Expected activity id to be fetched"
            assert transaction.time is not None, "Expected time to be fetched"
            assert transaction.type is not None, "Expected transaction type to be fetched"
            assert transaction.status is not None, "Expected status to be fetched"
            assert transaction.position_id is not None, "Expected position id to be fetched"
            assert transaction.net_amount is not None, "Expected net amount to be fetched"
            assert transaction.account_number is not None, "Expected account number to be fetched"
            assert transaction.sub_account is not None, "Expected sub account to be fetched"
            assert transaction.sub_account is not None, "Expected sub account to be fetched"
            transfer_items = transaction.transfer_items
            assert transfer_items is not None, "Expected transfer items to be fetched"
            for transfer_item in transfer_items:
                assert transfer_item.instrument is not None, "Expected instrument to be fetched"
                assert transfer_item.amount is not None, "Expected amount to be fetched"
                assert transfer_item.cost is not None, "Expected cost to be fetched"
                assert transfer_item.price is not None, "Expected price to be fetched"

            transaction_detail = trading_api.get_transaction(account_num, transaction.activity_id) 
            assert transaction_detail == transaction, "Expected transaction detail to match transaction"

        orders = trading_api.get_orders(account_num)
        check_orders(trading_api, orders)

    orders = trading_api.get_all_orders()
    check_orders(trading_api, orders)

    if not test_account_number or not test_order_type: # no order placement, change, cancellation, or preview
        return

    if test_order_type == 'place_dict':
        print("Testing place order by order dict")
        trading_api.place_order(order_dict, test_account_number)
    elif test_order_type == 'place_obj':
        print("Testing place order by order obj")
        order = Order.from_dict(order_dict)
        trading_api.place_order(order, test_account_number)
    else:
        for order in orders:
            leg = order.order_leg_collection[0]
            if leg.instrument.symbol == 'TSLA':
                if test_order_type == 'cancel':
                    print("Testing cancel order")
                    trading_api.cancel_order(test_order_id, test_account_number)
                elif test_order_type == 'replace':
                    print("Testing replace order")
                    order.order_id = test_order_id
                    order.price = 102
                    order.quantity = 2
                    trading_api.replace_order(order)
                break


def test_order_json():
    order = Order.from_dict(order_dict)
    order_dict2 = order.to_dict()
    assert is_subset_object(order_dict, order_dict2), "Expected order to be serialized and deserialized correctly"


@pytest.mark.integration
def test_market_data(app_config, logging_config):
    authorizer = Authorizer(app_config['auth'])
    access_token = authorizer.get_access_token()

    market_api = MarketApi(access_token, app_config['market'])
    symbols = ['TSLA', 'NVDA']
    quotes = market_api.get_quotes(symbols)
    for symbol in symbols:
        quote = quotes[symbol] 
        assert quote is not None, "Expected quote to be fetched"
        assert quote.asset_main_type is not None, "Expected asset main type to be fetched"
        assert quote.asset_sub_type is not None, "Expected asset sub type to be fetched"
        assert quote.realtime is not None, "Expected realtime to be fetched"
        assert quote.ssid is not None, "Expected ssid to be fetched"
        assert quote.symbol is not None, "Expected symbol to be fetched"
        assert quote.fundamental is not None, "Expected fundamental to be fetched"
        assert quote.quote is not None, "Expected quote to be fetched"
        assert quote.reference is not None, "Expected reference to be fetched"
        assert quote.regular is not None, "Expected regular to be fetched"

        quote_detail = market_api.get_quote(symbol)
        assert quote == quote_detail, "Expected quote detail to match quote"

    option_chain = market_api.get_option_chains('TSLA')
    assert option_chain is not None, "Expected option chain to be fetched"
    assert option_chain.symbol is not None, "Expected symbol to be fetched"
    assert option_chain.status is not None, "Expected status to be fetched"
    assert option_chain.asset_main_type is not None, "Expected asset main type to be fetched"
    assert option_chain.asset_sub_type is not None, "Expected asset sub type to be fetched"
    assert option_chain.strategy is not None, "Expected strategy to be fetched"
    assert option_chain.interval is not None, "Expected interval to be fetched"
    assert option_chain.is_delayed is not None, "Expected is_delayed to be fetched"
    assert option_chain.is_index is not None, "Expected is_index to be fetched"
    assert option_chain.is_chain_truncated is not None, "Expected is_chain_truncated to be fetched"
    assert option_chain.days_to_expiration is not None, "Expected days_to_expiration to be fetched"
    assert option_chain.number_of_contracts is not None, "Expected number_of_contracts to be fetched"
    assert option_chain.interest_rate is not None, "Expected interest_rate to be fetched"
    assert option_chain.underlying_price is not None, "Expected underlying_price to be fetched"
    assert option_chain.volatility is not None, "Expected volatility to be fetched"
    check_exp_date_map(option_chain, "call_exp_date_map")
    check_exp_date_map(option_chain, "put_exp_date_map")
    
    expiration_chains = market_api.get_option_expiration_chain('TSLA')
    for chain in expiration_chains:
        assert chain is not None, "Expected expiration chain to be fetched"
        assert chain.expiration_date is not None, "Expected expiration date to be fetched"
        assert chain.days_to_expiration is not None, "Expected days_to_expiration to be fetched"
        assert chain.expiration_type is not None, "Expected expiration type to be fetched"
        assert chain.settlement_type is not None, "Expected settlement type to be fetched"
        assert chain.option_roots is not None, "Expected option roots to be fetched"
        assert chain.standard is not None, "Expected standard to be fetched"


def check_exp_date_map(option_chain: OptionChain, field: str):
    exp_date_map = getattr(option_chain, field)
    assert exp_date_map is not None, f"Expected {field} to be fetched"
    assert len(exp_date_map) > 0, f"Expected {field} to have at least one entry"
    for dt, option_detail_map in exp_date_map.items():
        assert dt is not None, f"Expected date to be fetched"
        assert len(option_detail_map) > 0, f"Expected option detail map to have at least one entry"
        for strike_price, option_detail in option_detail_map.items():
            assert strike_price is not None, f"Expected strike price to be fetched"
            assert option_detail is not None, f"Expected option detail to be fetched"
            assert option_detail.put_call is not None, f"Expected put call to be fetched"
            assert option_detail.symbol is not None, f"Expected symbol to be fetched"
            assert option_detail.description is not None, f"Expected description to be fetched"
            assert option_detail.exchange_name is not None, f"Expected exchange name to be fetched"
            assert option_detail.bid is not None, f"Expected bid price to be fetched"
            assert option_detail.ask is not None, f"Expected ask price to be fetched"
            assert option_detail.last is not None, f"Expected last price to be fetched"
            assert option_detail.mark is not None, f"Expected mark to be fetched"
            assert option_detail.bid_size is not None, f"Expected bid size to be fetched"
            assert option_detail.ask_size is not None, f"Expected ask size to be fetched"
            assert option_detail.last_size is not None, f"Expected last size to be fetched"
            assert option_detail.high_price is not None, f"Expected high price to be fetched"
            assert option_detail.low_price is not None, f"Expected low price to be fetched"
            assert option_detail.open_price is not None, f"Expected open price to be fetched"
            assert option_detail.close_price is not None, f"Expected close price to be fetched"
            assert option_detail.high52_week is not None, f"Expected high52_week to be fetched"
            assert option_detail.low52_week is not None, f"Expected low52_week to be fetched"
            assert option_detail.total_volume is not None, f"Expected total volume to be fetched"
            assert option_detail.quote_time_in_long is not None, f"Expected quote time to be fetched"
            assert option_detail.trade_time_in_long is not None, f"Expected trade time to be fetched"
            assert option_detail.net_change is not None, f"Expected net_change to be fetched"
            assert option_detail.volatility is not None, f"Expected volatility to be fetched"
            assert option_detail.delta is not None, f"Expected delta to be fetched"
            assert option_detail.gamma is not None, f"Expected gamma to be fetched"
            assert option_detail.theta is not None, f"Expected theta to be fetched"
            assert option_detail.vega is not None, f"Expected vega to be fetched"
            assert option_detail.rho is not None, f"Expected rho to be fetched"
            assert option_detail.time_value is not None, f"Expected time_value to be fetched"
            assert option_detail.open_interest is not None, f"Expected open_interest to be fetched"
            assert option_detail.in_the_money is not None, f"Expected in_the_money to be fetched"
            assert option_detail.theoretical_option_value is not None, f"Expected theoretical_option_value to be fetched"
            assert option_detail.theoretical_volatility is not None, f"Expected theoretical_volatility to be fetched"
            assert option_detail.mini is not None, f"Expected mini to be fetched"
            assert option_detail.non_standard is not None, f"Expected non_standard to be fetched"
            assert option_detail.strike_price is not None, f"Expected strike_price to be fetched"
            assert option_detail.expiration_date is not None, f"Expected expiration_date to be fetched"
            assert option_detail.exercise_type is not None, f"Expected exercise_type to be fetched"
            assert option_detail.days_to_expiration is not None, f"Expected days_to_expiration to be fetched"
            assert option_detail.expiration_type is not None, f"Expected expiration_type to be fetched"
            assert option_detail.last_trading_day is not None, f"Expected last_trading_day to be fetched"
            assert option_detail.multiplier is not None, f"Expected multiplier to be fetched"
            assert option_detail.settlement_type is not None, f"Expected settlement_type to be fetched"
            assert option_detail.deliverable_note is not None, f"Expected deliverable_note to be fetched"
            assert option_detail.percent_change is not None, f"Expected percent_change to be fetched"
            assert option_detail.mark_change is not None, f"Expected mark change to be fetched"
            assert option_detail.mark_percent_change is not None, f"Expected mark percent change to be fetched"
            assert option_detail.penny_pilot is not None, f"Expected penny_pilot to be fetched"
            assert option_detail.intrinsic_value is not None, f"Expected intrinsic_value to be fetched"
            assert option_detail.extrinsic_value is not None, f"Expected extrinsic_value to be fetched"
            assert option_detail.option_root is not None, f"Expected option_root to be fetched"
            assert option_detail.option_deliverables_list is not None, f"Expected option_deliverables_list to be fetched"
            assert len(option_detail.option_deliverables_list) > 0, f"Expected option_deliverables_list to have at least one entry"
            for deliverable in option_detail.option_deliverables_list:
                assert deliverable is not None, f"Expected deliverable to be fetched"
                assert deliverable.symbol is not None, f"Expected symbol to be fetched"
                assert deliverable.asset_type is not None, f"Expected asset_type to be fetched"
                assert deliverable.deliverable_units is not None, f"Expected deliverable_units to be fetched"
