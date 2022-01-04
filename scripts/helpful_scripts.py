from brownie import (
    accounts, config, network, interface,
    VRFCoordinatorMock,
    LinkToken,
    MockOracle,
    MockV3AggregatorETHUSD,
    MockV3AggregatorDAIUSD,
    MockV3AggregatorDAIETH,
    MockDAI,
    MockWETH,
    Contract,
)
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
INITIAL_PRICE_FEED_VALUE_DAI_USD = 1000000000000000000 # 1 usd for 1 dai
DECIMALS_DAI_USD = 18
INITIAL_PRICE_FEED_VALUE_DAI_ETH = Web3.toWei(0.00025, "ether") # so much for 1 dai in eth
DECIMALS_DAI_ETH = 18
INITIAL_PRICE_FEED_VALUE_ETH_USD = 4000000000000000000000 # 4,000 usd for 1 eth
DECIMALS_ETH_USD = 18

def get_account(index=None, id=None, wallet=None):
    """Return current user account."""
    if index and (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS):
        return accounts[index]
    elif network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    elif id:
        return accounts.load(id)
    elif wallet:
        return config["wallets"][wallet]
    return accounts.add(config["wallets"]["from_key"])

def get_balance(_contract, _erc20=None):
    """Return balance of a contract address in ETH or in a specific ERC20."""
    if _erc20:
        return _erc20.balanceOf(_contract.address)
    return _contract.balance()

def get_supported_tokens():
    """"""
    CURRENCY_PAIRS = [
        "ETH/USD",
        "DAI/USD",
        "DAI/ETH"
    ]
    PRICE_FEED_PROXIES = [
        get_contract("eth_usd_price_feed"),
        get_contract("dai_usd_price_feed"),
        get_contract("dai_eth_price_feed")
    ]
    return CURRENCY_PAIRS, PRICE_FEED_PROXIES

def get_api_data():
    LATEST_CPI = {
        "belgie": {
            "url": "https://bestat.statbel.fgov.be/bestat/api/views/876acb9d-4eae-408e-93d9-88eae4ad1eaf/result/JSON",
            "path": "facts.-1.Consumptieprijsindex"
        }
    }
    url = LATEST_CPI["belgie"]["url"]
    path = LATEST_CPI["belgie"]["path"]
    return url, path



contract_to_mock = {
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
    "oracle": MockOracle,
    "eth_usd_price_feed": MockV3AggregatorETHUSD,
    "dai_usd_price_feed": MockV3AggregatorDAIUSD,
    "dai_eth_price_feed": MockV3AggregatorDAIETH,
    "fau_token": MockDAI,
    "weth_token": MockWETH,
    "dai_token": MockDAI,
}

def get_contract(contract_name):
    """
    If you want to use this function, go to the brownie config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the variable 'contract_to_mock'.
    You'll see examples like the 'link_token'.
        This script will then either:
            - Get a address from the config
            - Or deploy a mock to use for a network that doesn't have it

        Args:
            contract_name (string): This is the name that is refered to in the
            brownie config and 'contract_to_mock' variable.

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specificed by the dictonary. This could be either
            a mock or the 'real' contract on a live network.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract

def get_job_id():
    """Return a Chainlink oracle job ID."""
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return 0
    if network.show_active() in config["networks"]:
        return Web3.toHex(text=config["networks"][network.show_active()]["job_id"])

def deploy_mocks():
    """
    Deploy mocks to a testnet.

    Call the function if you want to deploy mocks to a testnet.
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()
    print("Deploying Mock LinkToken...")
    link_token = LinkToken.deploy({"from": account})
    print(f"Link Token deployed to {link_token.address}")
    print("Deploying Mock VRF Coordinator...")
    vrf_coordinator = VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print(f"VRFCoordinator deployed to {vrf_coordinator.address}")
    print("Deploying Mock Oracle...")
    mock_oracle = MockOracle.deploy(link_token.address, {"from": account})
    print(f"Deployed to {mock_oracle.address}")
    print("Deploying Mock Price Feed...")
    mock_price_feed_eth_usd = MockV3AggregatorETHUSD.deploy(
        DECIMALS_ETH_USD, INITIAL_PRICE_FEED_VALUE_ETH_USD, {"from": account}
    )
    print(f"Deployed to {mock_price_feed_eth_usd.address}")
    mock_price_feed_dai_usd = MockV3AggregatorDAIUSD.deploy(
        DECIMALS_DAI_USD, INITIAL_PRICE_FEED_VALUE_DAI_USD, {"from": account}
    )
    print(f"Deployed to {mock_price_feed_dai_usd.address}")
    mock_price_feed_dai_eth = MockV3AggregatorDAIETH.deploy(
        DECIMALS_DAI_ETH, INITIAL_PRICE_FEED_VALUE_DAI_ETH, {"from": account}
    )
    print(f"Deployed to {mock_price_feed_dai_eth.address}")
    print("Deploying Mock DAI...")
    mock_dai = MockDAI.deploy({"from": account})
    print(f"Deployed to {mock_dai.address}")
    print("Deploying Mock WETH...")
    mock_weth = MockWETH.deploy({"from": account})
    print(f"Deployed to {mock_weth.address}")
    print("Mocks Deployed!")

def fund_with_link(
    contract_address,
    account=None,
    link_token=None,
    amount=Web3.toWei(20, "ether")
):
    """Fund Link Token to contract."""
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx_fund_with_link = link_token.transfer(
        contract_address, amount, {"from": account}
    )
    tx_fund_with_link.wait(1)
    print(f"Funded {contract_address}")
    return tx_fund_with_link

def get_weth(_amount_weth=None, _erc20=None, _amount_erc20=None):
    print("Converting ETH to WETH...")
    account = get_account()
    weth = interface.IWeth(get_contract("weth_token"))
    tx_get_weth = weth.deposit({"from": account, "value": _amount_weth})
    tx_get_weth.wait(1)
    print(f"Recieved {_amount_weth} WETH")
    return weth

def get_price(_proxy_address, _account=None):
    account = _account if _account else get_account()
    proxy = _proxy_address
    (
        roundID,
        price,
        startedAt,
        timeStamp,
        answeredInRound
    ) = proxy.latestRoundData({"from": account})
    return price, proxy.decimals()

def approve_erc20(_spender, _amount, _erc20, _account):
    """"""
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(_erc20)
    tx_approve_erc20 = erc20.approve(_spender, _amount, {"from": _account})
    tx_approve_erc20.wait(1)
    print("Approved ERC20 token.")
    return tx_approve_erc20

def approve_weth(_spender, _amount, _weth, _account):
    """"""
    print("Approving WETH token...")
    weth = interface.IWeth(_weth)
    tx_approve_weth = weth.approve(_spender, _amount, {"from": _account})
    tx_approve_weth.wait(1)
    print("Approved WETH token.")
    return tx_approve_weth

def transfer_erc20_from(_from, _to, _erc20, _value, _account):
    """Transfer ERC20 token using `transferFrom` method."""
    print(f"Transfering ERC20 token from {_from} to {_to}...")
    erc20 = interface.IERC20(_erc20)
    tx_transfer_erc20_from = erc20.transferFrom(_from, _to, _value, {"from": _account})
    tx_transfer_erc20_from.wait(1)
    print("Transfered ERC20 token.")
    return tx_transfer_erc20_from

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
    account = get_account()
    swap_router = interface.ISwapRouter(get_contract("swap_router"))
    amount_approve = config["networks"][network.show_active()][
        "amount_weth_approve"
    ]
    tx_approve_erc20 = token_in.approve(
        swap_router, amount_approve, {"from": account}
    )
    tx_approve_erc20.wait(1)
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
    print(f"Swapped WETH for {amount_out} of DAI.")
    return tx_swap
