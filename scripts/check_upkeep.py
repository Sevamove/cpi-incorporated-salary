from brownie import CPIIncorporatedSalary
from scripts.helpful_scripts import get_account

def check_upkeep():
    """"""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    upkeepNeeded, performData = cpi_incorporated_salary.checkUpkeep.call(
        "",
        {"from": account}
    )
    print(f"The status of this upkeep is currently: {upkeepNeeded}")
    print(f"Here is the perform data: {performData}")
    return upkeepNeeded, performData

def main():
    check_upkeep()
