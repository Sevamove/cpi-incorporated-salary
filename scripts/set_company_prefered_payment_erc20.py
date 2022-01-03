from brownie import CPIIncorporatedSalary
from scripts.helpful_scripts import get_account, get_contract

def set_company_prefered_payment_erc20():
    """"""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    erc20 = get_contract("weth_token")
    tx_set_company = cpi_incorporated_salary.setCompanyPreferedPaymentERC20(
        erc20, {"from": account}
    )
    tx_set_company.wait(1)
    #print(f"New company prefered payment ERC20 token: {cpi_incorporated_salary.companyToRecentData(cpi_incorporated_salary.company()).preferedPaymentToken()}")
    return tx_set_company

def main():
    set_company_prefered_payment_erc20()
