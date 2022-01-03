from brownie import CPIIncorporatedSalary, config, network
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    fund_with_link,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS
)
import time

def request_cpi_data():
    """Request CPI data."""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    fund_with_link(
        cpi_incorporated_salary.address,
        amount=config["networks"][network.show_active()]["fee"]
    )
    tx_request_cpi_data = cpi_incorporated_salary.requestCPIData(
        {"from": account}
    )
    tx_request_cpi_data.wait(1)
    print("Data requested...")
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        print("Using mock CPI...")
        mock_cpi = 115740000000000400000
        requestId = tx_request_cpi_data.events["ChainlinkRequested"]["id"]
        get_contract("oracle").fulfillOracleRequest(
            requestId, mock_cpi, {"from": account}
        ).wait(1)
    time.sleep(config["networks"][network.show_active()]["wait_seconds"])
    cpi = cpi_incorporated_salary.recentCPI()
    print(f"CPI: {cpi}")
    return cpi

def main():
    request_cpi_data()
