from brownie import CPIIncorporatedSalary, config, network
from scripts.helpful_scripts import get_account, get_contract
from web3 import Web3

def add_employee(
    _employee=None,
    _initial_salary=None,
    _payment_interval=None,
    _prefered_payment_token=None,
    _pair=None,
    _account=None
):
    """"""
    account = _account if _account else get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    tx_add_employee = cpi_incorporated_salary.addEmployee(
        _employee,
        _initial_salary,
        _payment_interval,
        _prefered_payment_token,
        _pair,
        {"from": account}
    )
    tx_add_employee.wait(1)
    print(f"Added new employee: {_employee}")
    return _employee

def main():
    add_employee()
