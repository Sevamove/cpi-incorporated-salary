from brownie import CPIIncorporatedSalary
from scripts.helpful_scripts import get_account

def withdraw():
    """"""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    tx_withdraw = cpi_incorporated_salary.withdraw({"from": account})
    tx_withdraw.wait(1)
    print("Successfully withdrawed.")
    return tx_withdraw

def main():
    withdraw()
