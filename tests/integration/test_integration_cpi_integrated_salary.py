from brownie import (
    network,
    config,
    CPIIncorporatedSalary,
    exceptions,
    interface,
)
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_supported_tokens,
    get_contract,
    get_api_data,
    get_balance,
    get_account,
    get_job_id,
)
from scripts.deploy import deploy_cpi_incorporated_salary
from scripts.fund import fund, get_minimum_fund_amount
from scripts.request_cpi_data import request_cpi_data
from scripts.perform_upkeep import perform_upkeep
from scripts.check_upkeep import check_upkeep
from scripts.add_employee import add_employee
from scripts.withdraw import withdraw
from web3 import Web3
import pytest
import time

def test_cpi_integrated_salary():
    """development: not passed (make MockUniswap), kovan: passed."""
    # Deploying...
    deploy_cpi_incorporated_salary()
    # Requesting CPI data...
    request_cpi_data()
    # Adding a few employees...
    add_employee(
        get_account(index=4, wallet="account_4"),
        Web3.toWei(101, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("weth_token"),
        "ETH/USD"
    )
    add_employee(
        get_account(index=2, wallet="account_2"),
        Web3.toWei(98, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("weth_token"),
        "ETH/USD"
    )
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # Make MockUniswap for local testing.
        add_employee(
            get_account(index=1, wallet="account_1"),
            Web3.toWei(99, "ether"),
            config["networks"][network.show_active()]["payment_interval"],
            get_contract("dai_token"),
            "DAI/USD"
        )
        add_employee(
            get_account(index=3, wallet="account_3"),
            Web3.toWei(102, "ether"),
            config["networks"][network.show_active()]["payment_interval"],
            get_contract("dai_token"),
            "DAI/USD"
        )
    # Funding smart contract with ERC20...
    fund()
    # Paying to employees...
    time.sleep(config["networks"][network.show_active()]["payment_interval"])
    # You have to register Chainlink keeper first.
    check_upkeep()
    # To get back left tokens from the contract if this is the case.
    withdraw()
    assert CPIIncorporatedSalary[-1].balance() == 0
    assert interface.IWeth(
        get_contract("weth_token")).balanceOf(
            CPIIncorporatedSalary[-1], {"from": get_account()}) == 0
    assert interface.IERC20(
        get_contract("dai_token")).balanceOf(
            CPIIncorporatedSalary[-1], {"from": get_account()}) == 0
