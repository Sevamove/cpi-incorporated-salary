from brownie import CPIIncorporatedSalary, interface
from scripts.helpful_scripts import (
    get_account, get_balance, get_contract
)

def pay_employee():
    """"""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    weth = interface.IWeth(get_contract("weth_token"))
    dai = interface.IERC20(get_contract("dai_token"))
    message = "Updated balance of the contract in"
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        tx_1 = cpi_incorporated_salary.employeesToPayLength = 4
    tx_pay_employee = cpi_incorporated_salary.payEmployee(
        {"from": account}
    )
    tx_pay_employee.wait(1)
    print("Paid!")
    print(message, "WETH", f":{get_balance(cpi_incorporated_salary, weth)}")
    print(message, "DAI", f":{get_balance(cpi_incorporated_salary, dai)}")


def main():
    pay_employee()
