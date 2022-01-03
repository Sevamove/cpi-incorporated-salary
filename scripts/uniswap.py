from brownie import TokenSwap, interface, config, network
from scripts.helpful_scripts import get_account, get_contract
from web3 import Web3


def convert_company_tokens_to_employee_tokens():
    """"""

    account = get_account()
    token_swap = TokenSwap[-1]

    company_prefered_payment_token = interface.IERC20(get_contract("weth_token"))
    employee_prefered_payment_token = get_contract("dai_token")
    contract_address = token_swap.address
    balance_of_contract_in_company_token = company_prefered_payment_token.balanceOf(contract_address)
    company_tokens_to_send = Web3.toWei(balance_of_contract_in_company_token, "ether")
    company_tokens_to_send_max = balance_of_contract_in_company_token
    employee_tokens_to_recieve = Web3.toWei(201, "ether")
    employee = get_account(wallet="account_1")

    swap_tx = token_swap.convertCompanyTokensToEmployeeTokens(
        company_prefered_payment_token,
        employee_prefered_payment_token,
        company_tokens_to_send,
        company_tokens_to_send_max,
        employee_tokens_to_recieve,
        employee,
        {"from": account}
    )
    swap_tx.wait(1)
    print("Swapped")
    return swap_tx

def main():
    convert_company_tokens_to_employee_tokens()
