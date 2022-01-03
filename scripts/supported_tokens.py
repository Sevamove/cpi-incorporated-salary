from brownie import Contract
from scripts.helpful_scripts import get_contract

# De huidige ondersteunde cryptomunten om af te betalen:
# WETH, DAI, ETH?

CURRENCY_PAIRS = [
    "ETH/USD",
    "DAI/USD"
]

PRICE_FEED_PROXIES = [
    Contract(get_contract("eth_usd_price_feed")).address,
    Contract(get_contract("dai_usd_price_feed")).address
]

