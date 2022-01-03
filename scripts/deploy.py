from brownie import CPIIncorporatedSalary, config, network
from scripts.helpful_scripts import (
    get_account, get_contract, get_supported_tokens, get_api_data
)
from web3 import Web3

def deploy_cpi_incorporated_salary():
    """Deploy CPIIncorporatedSalary contract."""
    # DEFINING VARIABLES.=======================================================
    oracle = get_contract("oracle")
    job_id = config["networks"][network.show_active()]["job_id"]
    fee = config["networks"][network.show_active()]["fee"]
    link_token = get_contract("link_token").address
    account = get_account()
    publish_source = config["networks"][network.show_active()].get(
        "verify", False
    )
    # DEPLOYING CONTRACTS.======================================================
    cpi_incorporated_salary = CPIIncorporatedSalary.deploy(
        oracle,
        Web3.toHex(text=job_id),
        fee,
        link_token,
        {"from": account},
        publish_source=publish_source
    )
    # SETTING CHAINLINK PRICE FEED PROXIES.=====================================
    currency_pairs, price_feed_proxies = get_supported_tokens()
    set_price_feed_proxy(
        currency_pairs, price_feed_proxies, cpi_incorporated_salary, account
    )
    # SETTING API FOR CPI DATA.=================================================
    url, path = get_api_data()
    set_api_data_base(url, path, cpi_incorporated_salary, account)
    print(
        f"CPI Incorporated Salary deployed to {cpi_incorporated_salary.address}"
    )
    return cpi_incorporated_salary

def set_price_feed_proxy(
    currency_pairs, price_feed_proxies, cpi_incorporated_salary, account
):
    print("Setting currency pairs with price feed proxies...")
    tx1_set_price_feed_proxy = cpi_incorporated_salary.setPriceFeedProxy(
        currency_pairs[0],
        price_feed_proxies[0],
        {"from": account}
    )
    tx1_set_price_feed_proxy.wait(1)
    tx2_set_price_feed_proxy = cpi_incorporated_salary.setPriceFeedProxy(
        currency_pairs[1],
        price_feed_proxies[1],
        {"from": account}
    )
    tx2_set_price_feed_proxy.wait(1)
    tx3_set_price_feed_proxy = cpi_incorporated_salary.setPriceFeedProxy(
        currency_pairs[2],
        price_feed_proxies[2],
        {"from": account}
    )
    tx3_set_price_feed_proxy.wait(1)
    print("Assigned currency pairs with Chainlink price feed contracts.")

def set_api_data_base(url, path, cpi_incorporated_salary, account):
    """Assign defined URL and Path of a current CPI."""
    print("Setting API data base...")
    url, path = get_api_data()
    tx_set_api_data_base = cpi_incorporated_salary.setAPIDataBase(
        url, path, {"from": account}
    )
    tx_set_api_data_base.wait(1)
    print("Setted API database.")

def main():
    deploy_cpi_incorporated_salary()
