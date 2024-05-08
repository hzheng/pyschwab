import pytest
import logging
import yaml

from pyschwab.trading import TradingApi
from pyschwab.auth import Authorizer
from pyschwab.log import logger
from pyschwab.trading_models import TradingData


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
