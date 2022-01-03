from brownie import (
    config, network
)
import pytest

@pytest.fixture
def data_url():
    return "https://bestat.statbel.fgov.be/bestat/api/views/876acb9d-4eae-408e-93d9-88eae4ad1eaf/result/JSON"

@pytest.fixture
def data_url_json_path():
    return "facts.-1.Consumptieprijsindex"

@pytest.fixture
def get_data():
    return 115740000000000400000

