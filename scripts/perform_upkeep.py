from brownie import CPIIncorporatedSalary, network
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.check_upkeep import check_upkeep

def perform_upkeep():
    """"""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    upkeep_needed, perform_data = check_upkeep()
    if upkeep_needed == True:
        cpi_incorporated_salary.performUpkeep.call(
            perform_data,
            {"from": account}
        )
        print("Performed Upkeep!")
        return True
    else:
        print("Did not perform upkeep.")
        return False

def main():
    perform_upkeep()
