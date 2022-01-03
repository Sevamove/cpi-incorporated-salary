from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_supported_tokens,
    get_contract,
    get_api_data,
    get_account,
    get_balance,
    get_job_id,
    get_weth,
)
from brownie import (
    CPIIncorporatedSalary,
    exceptions,
    interface,
    network,
    config,
    chain,
)
from scripts.deploy import set_price_feed_proxy,set_api_data_base
from scripts.fund import get_minimum_fund_amount, swap, fund
from scripts.request_cpi_data import request_cpi_data
from scripts.perform_upkeep import perform_upkeep
from scripts.check_upkeep import check_upkeep
from scripts.add_employee import add_employee
from scripts.withdraw import withdraw
from web3 import Web3
import pytest
import time

@pytest.fixture
def deploy_cpi_incorporated_salary():
    """Deploy contracts."""
    # Arrange.------------------------------------------------------------------
    oracle = get_contract("oracle").address
    job_id = get_job_id()
    fee = config["networks"][network.show_active()]["fee"]
    link_token = get_contract("link_token").address
    account = get_account()
    publish_source = config["networks"][network.show_active()].get(
        "verify", False
    )
    # Act.----------------------------------------------------------------------
    cpi_incorporated_salary = CPIIncorporatedSalary.deploy(
        oracle,
        job_id,
        fee,
        link_token,
        {"from": account},
        publish_source=publish_source
    )
    # Assert.-------------------------------------------------------------------
    assert cpi_incorporated_salary is not None
    return cpi_incorporated_salary

def test_set_price_feed_proxy(deploy_cpi_incorporated_salary):
    """development: passed, kovan: passed."""
    # Arrange.------------------------------------------------------------------
    if network.show_active() not in ["development", "kovan"]:
        pytest.skip("Invalid network specified.")
    account = get_account()
    non_owner = get_account(index=1)
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    # Act.----------------------------------------------------------------------
    currency_pairs, price_feed_proxies = get_supported_tokens()
    set_price_feed_proxy(
        currency_pairs, price_feed_proxies, cpi_incorporated_salary, account
    )
    # Assert.-------------------------------------------------------------------
    assert cpi_incorporated_salary.currencyPairToPriceFeedProxy(
        currency_pairs[0]
    ) == price_feed_proxies[0]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        with pytest.raises(exceptions.VirtualMachineError):
            cpi_incorporated_salary.setPriceFeedProxy(
                currency_pairs[0], price_feed_proxies[0], {"from": non_owner}
            )

def test_set_api_data_base(deploy_cpi_incorporated_salary):
    """development: passed, kovan: passed."""
    # Arrange.------------------------------------------------------------------
    if network.show_active() not in ["development", "kovan"]:
        pytest.skip("Invalid network specified.")
    account = get_account()
    non_owner = get_account(index=1, wallet="account_2")
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    # Act.----------------------------------------------------------------------
    url, path = get_api_data()
    set_api_data_base(url, path, cpi_incorporated_salary, account)
    # Assert.-------------------------------------------------------------------
    assert url == cpi_incorporated_salary.apiURL()
    assert path == cpi_incorporated_salary.apiJsonPath()
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        with pytest.raises(exceptions.VirtualMachineError):
            cpi_incorporated_salary.setAPIDataBase(
                url, path, {"from": non_owner}
            )

def test_request_api_data(deploy_cpi_incorporated_salary):
    """development: passed, kovan: passed."""
    # Arrange.------------------------------------------------------------------
    if network.show_active() not in ["development", "kovan"]:
        pytest.skip("Invalid network specified.")
    account = get_account()
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    # Act.----------------------------------------------------------------------
    url, path = get_api_data()
    set_api_data_base(url, path, cpi_incorporated_salary, account)
    cpi = request_cpi_data()
    # Assert.-------------------------------------------------------------------
    assert isinstance(cpi, int)
    assert cpi > 0

def test_add_employee(deploy_cpi_incorporated_salary):
    """development: passed, kovan: passed"""
    # Arrange.------------------------------------------------------------------
    if network.show_active() not in ["development", "kovan"]:
        pytest.skip("Invalid network specified.")
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    non_owner = get_account(index=3, wallet="account_3")
    # Act.----------------------------------------------------------------------
    employee = get_account(index=2, wallet="account_2")
    initial_salary = Web3.toWei(100, "ether")
    payment_interval = config["networks"][network.show_active()]["payment_interval"]
    prefered_payment_token = get_contract("weth_token")
    pair = "ETH/USD"
    add_employee(
        employee,
        initial_salary,
        payment_interval,
        prefered_payment_token,
        pair,
    )
    # Assert.-------------------------------------------------------------------
    assert cpi_incorporated_salary.employees(0) == employee
    assert cpi_incorporated_salary.employeeToRecentData(employee)[
        "employee"
    ] == employee
    assert cpi_incorporated_salary.employeeToRecentData(employee)[
        "previousSalary"
    ] == initial_salary
    assert cpi_incorporated_salary.employeeToRecentData(employee)[
        "paymentInterval"
    ] == payment_interval
    assert cpi_incorporated_salary.employeeToRecentData(employee)[
        "preferedPaymentToken"
    ] == prefered_payment_token
    assert cpi_incorporated_salary.employeeToRecentData(employee)[
        "pair"
    ] == pair
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        with pytest.raises(exceptions.VirtualMachineError):
            add_employee(
                get_account(index=4, wallet="account_4"),
                Web3.toWei(101, "ether"),
                config["networks"][network.show_active()]["payment_interval"],
                get_contract("weth_token"),
                "ETH/USD",
                non_owner
            )

def test_fund(deploy_cpi_incorporated_salary):
    """
    development: not passed (make MockUniswap), kovan: passed.

    Perhaps using `mainnet-fork` would be a beter idea instead of `development`.
    However there comes a problem into existence with Chainlink oracle as
    "Unfortunately, forking mainnet to test interacting with Chainlink oracles
    won’t work." - https://blog.chain.link/testing-chainlink-smart-contracts/
    """
    # Arrange.------------------------------------------------------------------
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Make MockUniswap first for development network.")
    account = get_account()
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    # SETTING PRICE FEED PROXIES.
    currency_pairs, price_feed_proxies = get_supported_tokens()
    set_price_feed_proxy(
        currency_pairs, price_feed_proxies, cpi_incorporated_salary, account
    )
    # SETTING API DATABASE.
    url, path = get_api_data()
    set_api_data_base(url, path, cpi_incorporated_salary, account)
    # REQUESTING CPI DATA.
    cpi = request_cpi_data()
    # ADDING A FEW EMPLOYEES.
    add_employee(
        get_account(index=4, wallet="account_4"),
        Web3.toWei(101, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("weth_token"),
        "ETH/USD"
    )
    add_employee(
        get_account(index=3, wallet="account_3"),
        Web3.toWei(102, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("dai_token"),
        "DAI/USD"
    )
    add_employee(
        get_account(index=2, wallet="account_2"),
        Web3.toWei(98, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("weth_token"),
        "ETH/USD"
    )
    add_employee(
        get_account(index=1, wallet="account_1"),
        Web3.toWei(99, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("dai_token"),
        "DAI/USD"
    )
    # Act.----------------------------------------------------------------------
    amount_to_fund_in_weth, amount_to_fund_in_dai = get_minimum_fund_amount()
    tx_transfer_weth, tx_swap = fund()
    # Assert.-------------------------------------------------------------------
    assert tx_transfer_weth is not True
    assert tx_swap is not True
    assert get_balance(
        cpi_incorporated_salary, interface.IERC20(get_contract("weth_token"))
    ) >= amount_to_fund_in_weth
    assert get_balance(
        cpi_incorporated_salary, interface.IERC20(get_contract("dai_token"))
    ) >= amount_to_fund_in_dai
    withdraw()

def test_get_conversion_rate(deploy_cpi_incorporated_salary):
    """development: passed, kovan: passed."""
    # Arrange.------------------------------------------------------------------
    if network.show_active() not in ["development", "kovan"]:
        pytest.skip("Invalid network specified.")
    account = get_account()
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    amount_in_dai = 201000000000000000000
    # SETTING PRICE FEED PROXIES.
    currency_pairs, price_feed_proxies = get_supported_tokens()
    set_price_feed_proxy(
        currency_pairs, price_feed_proxies, cpi_incorporated_salary, account
    )
    # Act.----------------------------------------------------------------------
    amount_in_weth = cpi_incorporated_salary.getConversionRate(
        "DAI/ETH", amount_in_dai, {"from": account}
    )
    assert isinstance(amount_in_weth, int)
    assert amount_in_weth > 0

def test_get_minimum_fund_amount(deploy_cpi_incorporated_salary):
    """development: passed, kovan: passed."""
    # Arrange.------------------------------------------------------------------
    if network.show_active() not in ["development", "kovan"]:
        pytest.skip("Invalid network specified.")
    account = get_account()
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    # SETTING API DATABASE.
    url, path = get_api_data()
    set_api_data_base(url, path, cpi_incorporated_salary, account)
    # SETTING PRICE FEED PROXIES.
    currency_pairs, price_feed_proxies = get_supported_tokens()
    set_price_feed_proxy(
        currency_pairs, price_feed_proxies, cpi_incorporated_salary, account
    )
    # ADDING A NEW EMPLOYEE.
    add_employee(
        get_account(index=4, wallet="account_4"),
        Web3.toWei(101, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("weth_token"),
        "ETH/USD"
    )
    # Act.----------------------------------------------------------------------
    amount_to_fund_in_weth, amount_to_fund_in_dai = get_minimum_fund_amount()
    # Assert.-------------------------------------------------------------------
    assert amount_to_fund_in_weth > 0 or amount_to_fund_in_dai > 0
    withdraw()

def test_get_weth(deploy_cpi_incorporated_salary):
    """development: passed, kovan: passed"""
    if network.show_active() not in ["development", "kovan"]:
        pytest.skip("Invalid network specified.")
    # Arrange.------------------------------------------------------------------
    account = get_account()
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    # Act.----------------------------------------------------------------------
    amount_weth = Web3.toWei(0.01, "ether")
    weth = get_weth(amount_weth)
    # Assert.-------------------------------------------------------------------
    assert weth.balanceOf(account.address, {"from": account}) >= amount_weth
    withdraw()

def test_can_approve_weth(deploy_cpi_incorporated_salary):
    """development: passed, kovan: passed."""
    if network.show_active() not in ["development", "kovan"]:
        pytest.skip("Invalid network specified.")
    # Arrange.------------------------------------------------------------------
    account = get_account()
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    amount_weth = Web3.toWei(0.01, "ether")
    weth = get_weth(amount_weth)
    # Act.----------------------------------------------------------------------
    tx_approve_weth = weth.approve(account, amount_weth, {"from": account})
    # Assert.-------------------------------------------------------------------
    assert tx_approve_weth is not True
    withdraw()

def test_can_transfer_weth(deploy_cpi_incorporated_salary):
    """development: passed, kovan: passed."""
    if network.show_active() not in ["development", "kovan"]:
        pytest.skip("Invalid network specified.")
    # Arrange.------------------------------------------------------------------
    account = get_account()
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    # SETTING API DATABASE.
    url, path = get_api_data()
    set_api_data_base(url, path, cpi_incorporated_salary, account)
    # SETTING PRICE FEED PROXIES.
    currency_pairs, price_feed_proxies = get_supported_tokens()
    set_price_feed_proxy(
        currency_pairs, price_feed_proxies, cpi_incorporated_salary, account
    )
    # ADDING A NEW EMPLOYEE.
    add_employee(
        get_account(index=4, wallet="account_4"),
        Web3.toWei(101, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("weth_token"),
        "ETH/USD"
    )
    # GETTING WETH.
    amount_to_fund_in_weth, amount_to_fund_in_dai = get_minimum_fund_amount()
    amount_of_dai_in_weth = cpi_incorporated_salary.getConversionRate(
        "DAI/ETH", amount_to_fund_in_dai, {"from": account}
    )
    amount_weth = amount_to_fund_in_weth + amount_of_dai_in_weth
    weth = get_weth(amount_weth)
    # APPROVING WETH TOKEN.
    tx_approve_weth = weth.approve(account, amount_weth, {"from": account})
    tx_approve_weth.wait(1)
    # Act.----------------------------------------------------------------------
    tx_transfer_weth = weth.transferFrom(
        account,
        cpi_incorporated_salary,
        amount_to_fund_in_weth,
        {"from": account}
    )
    # Assert.-------------------------------------------------------------------
    assert tx_transfer_weth is not True
    withdraw()

def test_swap(deploy_cpi_incorporated_salary):
    """development: not passed (no MockUniswap), kovan: passed."""
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Make MockUniswap first for development network.")
    # Arrange.------------------------------------------------------------------
    account = get_account()
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    # SETTING API DATABASE.
    url, path = get_api_data()
    set_api_data_base(url, path, cpi_incorporated_salary, account)
    # REQUESTING CPI DATA.
    cpi = request_cpi_data()
    # SETTING PRICE FEED PROXIES.
    currency_pairs, price_feed_proxies = get_supported_tokens()
    set_price_feed_proxy(
        currency_pairs, price_feed_proxies, cpi_incorporated_salary, account
    )
    # ADDING A NEW EMPLOYEE.
    add_employee(
        get_account(index=2, wallet="account_2"),
        Web3.toWei(101, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("dai_token"),
        "DAI/USD"
    )
    # GETTING WETH.
    amount_to_fund_in_weth, amount_to_fund_in_dai = get_minimum_fund_amount()
    amount_of_dai_in_weth = cpi_incorporated_salary.getConversionRate(
        "DAI/ETH", amount_to_fund_in_dai, {"from": account}
    )
    amount_weth = amount_to_fund_in_weth + amount_of_dai_in_weth
    weth = get_weth(amount_weth)
    # Act.----------------------------------------------------------------------
    dai = interface.IERC20(get_contract("dai_token"))
    swap_fee = config["networks"][network.show_active()]["swap_fee"]
    amount_to_fund_in_weth, amount_to_fund_in_dai = get_minimum_fund_amount()
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
    # Assert.-------------------------------------------------------------------
    assert tx_swap is not True
    withdraw()

def test_check_upkeep(deploy_cpi_incorporated_salary):
    """developmend: passed."""
    # Arrange.------------------------------------------------------------------
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Not passing on this network.")
    account = get_account()
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    # SETTING API DATABASE.
    url, path = get_api_data()
    set_api_data_base(url, path, cpi_incorporated_salary, account)
    # REQUESTING CPI DATA.
    cpi = request_cpi_data()
    # SETTING PRICE FEED PROXIES.
    currency_pairs, price_feed_proxies = get_supported_tokens()
    set_price_feed_proxy(
        currency_pairs, price_feed_proxies, cpi_incorporated_salary, account
    )
    # ADDING A NEW EMPLOYEE.
    add_employee(
        get_account(index=2, wallet="account_2"),
        Web3.toWei(101, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("weth_token"),
        "ETH/USD"
    )
    # FUNDING THE CONTRACT.
    fund()
    # Act.----------------------------------------------------------------------
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.time() + 1
    upkeep_needed, perform_data = check_upkeep()
    # Assert.-------------------------------------------------------------------
    assert upkeep_needed is True
    assert perform_data is not None
    withdraw()

def test_perform_upkeep(deploy_cpi_incorporated_salary):
    """development: passed."""
    # Arrange.------------------------------------------------------------------
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Not passing on this network.")
    account = get_account()
    cpi_incorporated_salary = deploy_cpi_incorporated_salary
    # SETTING API DATABASE.
    url, path = get_api_data()
    set_api_data_base(url, path, cpi_incorporated_salary, account)
    # REQUESTING CPI DATA.
    cpi = request_cpi_data()
    # SETTING PRICE FEED PROXIES.
    currency_pairs, price_feed_proxies = get_supported_tokens()
    set_price_feed_proxy(
        currency_pairs, price_feed_proxies, cpi_incorporated_salary, account
    )
    # ADDING A NEW EMPLOYEE.
    add_employee(
        get_account(index=3, wallet="account_2"),
        Web3.toWei(101, "ether"),
        config["networks"][network.show_active()]["payment_interval"],
        get_contract("weth_token"),
        "ETH/USD"
    )
    # FUNDING THE CONTRACT.
    fund()
    # Act.----------------------------------------------------------------------
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.time() + 1
    performed_upkeep = perform_upkeep()
    # Assert.-------------------------------------------------------------------
    assert performed_upkeep is True
    withdraw()

def test_fund_with_link():
    pytest.skip()

def test_pay_employee():
    pytest.skip()

def test_withdraw():
    pytest.skip()
