from brownie import TokenSwap, config, network
from scripts.helpful_scripts import get_account, get_contract
from web3 import Web3

def deploy_token_swap():
    """"""
    account = get_account()
    token_swap = TokenSwap.deploy(
        {"from": account}
    )
    print(f"TokenSwap contract deployed to {token_swap.address}")
    return token_swap

def main():
    deploy_token_swap()
