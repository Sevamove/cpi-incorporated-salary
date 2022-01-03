from brownie import interface, config, network, chain
from scripts.helpful_scripts import get_account

def swap(
    token_in,
    token_out,
    fee=config["networks"][network.show_active()]["swap_fee"],
    account=get_account(),
    deadline=chain.time() + 600,
    amount_in=0,
    amount_out_minimum=0,
    sqrt_price_limit_x96=0,
):
    """"""
    account = get_account()
    swap_router = interface.ISwapRouter(
        config["networks"][network.show_active()]["swap_router"]
    )
    approve_erc20(amount_in, swap_router.address, token_in, account)
    swap_tx = swap_router.exactInputSingle(
        [
            token_in,
            token_out,
            fee,
            account,
            deadline,
            amount_in,
            amount_out_minimum,
            sqrt_price_limit_x96,
        ],
        {"from": account}
    )
    swap_tx.wait(1)
    return swap_tx

def approve_erc20(amount, spender, erc20_address, account):
    """"""
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    approve_tx = erc20.approve(spender, amount, {"from": account})
    approve_tx.wait(1)
    print("Approved!")
    return approve_tx

def get_weth():
    """"""
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    get_weth_tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    get_weth_tx.wait(1)
    print("Recieved 0.1 WETH")

def main():
    account = get_account()
    print("Converting ETH to WETH...")
    get_weth()

    print("Swapping WETH for DAI...")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    swap(
        token_out=config["networks"][network.show_active()]["weth_token"],
        token_in=dai_address,
        amount_in=0.1 * 10 ** 18,
        account=account
    )
    print("Swapped!")
