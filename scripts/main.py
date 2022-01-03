from scripts.deploy import deploy_cpi_incorporated_salary
from scripts.request_cpi_data import request_cpi_data
from scripts.perform_upkeep import perform_upkeep
from scripts.check_upkeep import check_upkeep
from scripts.add_employee import add_employee
from brownie import config, network, chain
from scripts.withdraw import withdraw
from scripts.fund import fund

from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_contract,
    get_account,
)
from web3 import Web3
import time

"""
Note:
    time.sleep() is needed in order to
    decrease the chance of tx drapping in kovan network.
"""

def main():
    deploy_cpi_incorporated_salary()
    #time.sleep(5)
    request_cpi_data()
    #time.sleep(5)
    add_employee(
        get_account(index=4, wallet="account_4"),
        Web3.toWei(101, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
       get_contract("weth_token"),
        "ETH/USD"
    )
    #time.sleep(5)
    add_employee(
        get_account(index=2, wallet="account_2"),
        Web3.toWei(98, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("weth_token"),
        "ETH/USD"
    )
    #time.sleep(5)
    # Delete this if statement if there is MockUniswap already.
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        add_employee(
            get_account(index=3, wallet="account_3"),
            Web3.toWei(102, "ether"),
            config["networks"][network.show_active()]["payment_interval"],
            get_contract("dai_token"),
            "DAI/USD"
        )
        #time.sleep(5)
        add_employee(
            get_account(index=1, wallet="account_1"),
            Web3.toWei(99, "ether"),
            config["networks"][network.show_active()]["payment_interval"],
            get_contract("dai_token"),
            "DAI/USD"
        )
        #time.sleep(5)
    fund()
    #time.sleep(5)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.time() + 10
        check_upkeep()
        #time.sleep(5)
        perform_upkeep()
        #time.sleep(5)
    else:
        check_upkeep()
        #time.sleep(5)
        #perform_upkeep()
    withdraw()
