from brownie import CPIIncorporatedSalary, interface, network, config, chain
from scripts.helpful_scripts import (
    get_account, get_balance, get_contract, get_weth,
    approve_erc20, approve_weth, transfer_erc20_from
)
from web3 import Web3


def main():
    fund()

def fund():
    """"""
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    account = get_account()

    tx_transfer_weth = None
    tx_swap = None

    message = str(f"Funded to {cpi_incorporated_salary.address}\n") + str(
        "Updated balance of the contract in")

    amount_to_fund_in_weth, amount_to_fund_in_dai = get_minimum_fund_amount()
    amount_of_dai_in_weth = cpi_incorporated_salary.getConversionRate(
        "DAI/ETH", amount_to_fund_in_dai, {"from": account}
    )
    amount_in_weth = amount_to_fund_in_weth + amount_of_dai_in_weth
    weth = get_weth(amount_in_weth)

    if amount_to_fund_in_weth > 0:
        tx_approve_weth = weth.approve(
            account, amount_to_fund_in_weth, {"from": account}
        )
        tx_approve_weth.wait(1)

        tx_transfer_weth = weth.transferFrom(
            account,
            cpi_incorporated_salary,
            amount_to_fund_in_weth,
            {"from": account}
        )
        tx_transfer_weth.wait(1)

        print(
            message, "WETH" + f": {get_balance(cpi_incorporated_salary, weth)}"
        )

    if amount_to_fund_in_dai > 0:
        dai = interface.IERC20(get_contract("dai_token"))
        swap_fee = config["networks"][network.show_active()]["swap_fee"]

        tx_swap = swap(
            weth,
            dai,
            swap_fee,
            cpi_incorporated_salary.address,
            chain.time() + 600,
            amount_to_fund_in_dai,
            amount_to_fund_in_dai,
            0
        )

        print(
            message, "DAI" + f": {get_balance(cpi_incorporated_salary, dai)}"
        )

    return tx_transfer_weth, tx_swap

def get_minimum_fund_amount():
    """Return amounts to fund of supported tokens."""
    account = get_account()
    cpi_incorporated_salary = CPIIncorporatedSalary[-1]
    tx_get_minimum_fund_amount = cpi_incorporated_salary.getMinimumFundAmount(
        {"from": account}
    )
    tx_get_minimum_fund_amount.wait(1)
    amount_to_fund_in_weth = cpi_incorporated_salary.minimumFundAmountInWeth()
    amount_to_fund_in_dai = cpi_incorporated_salary.minimumFundAmountInDai()
    if amount_to_fund_in_weth:
        print(f"Minimum amount to fund: {amount_to_fund_in_weth} WETH")
    if amount_to_fund_in_dai:
        print(f"Minimum amount to fund: {amount_to_fund_in_dai} DAI")
    return amount_to_fund_in_weth, amount_to_fund_in_dai

def swap(
    token_in,
    token_out,
    fee,
    recipient,
    deadline,
    amount_out,
    amount_in_maximum,
    sqrt_price_limit_x96
):
    print(f"Swapping WETH for {amount_out} of DAI...")

    account = get_account()
    swap_router = interface.ISwapRouter(get_contract("swap_router"))

    tx_approve_token_in = token_in.approve(
        swap_router, amount_in_maximum, {"from": account}
    )
    tx_approve_token_in.wait(1)

    tx_swap = swap_router.exactOutputSingle(
        [
            token_in,
            token_out,
            fee,
            recipient,
            deadline,
            amount_out,
            amount_in_maximum,
            sqrt_price_limit_x96
        ], {"from": account}
    )
    tx_swap.wait(1)

    print("Swapped!")
    return tx_swap
