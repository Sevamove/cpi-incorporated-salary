################################################################################
"""IMPORTING Dependencies"""
################################################################################


from scripts.helpful_scripts import get_contract, get_account, fund_with_link
from brownie import CPIIncorporatedSalary, GoldToken, config, network
from web3 import Web3
import time


################################################################################
"""DEFINING Global Variables and Types"""
################################################################################


LATEST_CPI = {
    "belgie": {
        "url": "https://bestat.statbel.fgov.be/bestat/api/views/876acb9d-4eae-408e-93d9-88eae4ad1eaf/result/JSON",
        "path": "facts.-1.Consumptieprijsindex"
    }
}

allowed_tokens_to_token_id = {
    "ETH": 0,
    "DAI": 1
}


################################################################################
"""DEFINING Functions"""
################################################################################


def deploy_cpi_incorporated_salary_and_gold_token():
    """
    Deploy CPI Incorporated Salary Contract
    and Gold Token contracts.

    """
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
    gold_token = GoldToken.deploy(
        "Gold",
        "GLD",
        21000000,
        {"from": account}
    )
    cpi_incorporated_salary = CPIIncorporatedSalary.deploy(
        oracle,
        Web3.toHex(text=job_id),
        fee,
        link_token,
        {"from": account},
        publish_source=publish_source
    )
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    # ADDING ALLOWED TOKENS.====================================================
    allowed_tokens_to_price_feed = {
        "usd": {
            "currency": "usd",
            "tokens": {
                gold_token: get_contract("dai_usd_price_feed"),
                fau_token: get_contract("dai_usd_price_feed"),
                weth_token: get_contract("eth_usd_price_feed"),
            }
        }
    }
    add_allowed_tokens(
        cpi_incorporated_salary,
        allowed_tokens_to_price_feed["usd"]["currency"],
        allowed_tokens_to_price_feed["usd"]["tokens"],
        account
    )
    print(
        f"CPI Incorporated Salary deployed to {cpi_incorporated_salary.address}"
    )
    return cpi_incorporated_salary, gold_token
################################################################################
def add_allowed_tokens(
    cpi_incorporated_salary,
    currency,
    allowed_tokens_to_price_feed,
    account
):
    """Loop through all diferent tokens and call setAllowedTokens function."""
    for token in allowed_tokens_to_price_feed:
        tx = cpi_incorporated_salary.addAllowedTokens(
            0,
            token,
            {"from": account}
        )
        tx.wait(1)
        tx = cpi_incorporated_salary.setPriceFeedContract(
            token,
            currency,
            allowed_tokens_to_price_feed[token],
            {"from": account}
        )
        tx.wait(1)
    return True
################################################################################
def set_api_data_base():
    """Assign URL and JSON path to value."""
    url = LATEST_CPI["belgie"]["url"]
    path = LATEST_CPI["belgie"]["path"]
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    cpi_incorporated_salary.setAPIDataBase(url, path, {"from": account})
################################################################################
def check_upkeep():
    """"""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    time.sleep(5)
    upkeepNeeded, performData = cpi_incorporated_salary.checkUpkeep.call(
        "",
        {"from": account},
    )
    print(f"The status of this upkeep is currently: {upkeepNeeded}")
    print(f"Here is the perform data: {performData}")
################################################################################
def request_data():
    """Request CPI data."""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    tx = fund_with_link(
        cpi_incorporated_salary.address,
        amount=config["networks"][network.show_active()]["fee"]
    )
    tx.wait(1)
    tx = cpi_incorporated_salary.requestCPIData(
        {"from": account}
    )
    tx.wait(1)
    print("Data requested!")
    time.sleep(config["networks"][network.show_active()]["wait_seconds"])
    print(cpi_incorporated_salary.recentCPI())
################################################################################
def add_employee():
    """"""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    employee = get_account(index=0, wallet="account_1")
    initial_salary = Web3.toWei(300, "ether") # 3,000 usd
    payment_interval = 3 #2592000 # seconds in 30 days
    prefered_payment_token = allowed_tokens_to_token_id["ETH"]
    tx = cpi_incorporated_salary.addEmployee(
        employee,
        initial_salary,
        payment_interval,
        prefered_payment_token,
        {"from": account}
    )
    tx.wait(1)
    print(f"Added new employee: {employee}")
################################################################################
def fund():
    """"""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    tx = cpi_incorporated_salary.getMinimumFundAmount({"from": account})
    tx.wait(1)
    value = cpi_incorporated_salary.minimumFundAmount() + 10000000000000000
    tx = cpi_incorporated_salary.fund({"from": account, "value": value})
    tx.wait(1)
    print(f"Funded to {cpi_incorporated_salary.address}")
    print(f"Balance of the contract: {cpi_incorporated_salary.balance()}")
################################################################################
def pay_employee():
    """"""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    tx = cpi_incorporated_salary.payEmployee(
        {"from": account}
    )
    tx.wait(1)
    print("Paid!")

def main():
    deploy_cpi_incorporated_salary_and_gold_token()
    #set_api_data_base()
    #request_data()
    #add_employee()
    #check_upkeep()

    #fund()
    #pay_employee()
    #check_upkeep()
