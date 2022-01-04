# Employee's salary incorporated with the most recent consumer price index (CPI) in Belgium.
> _This project was created in order to understand DeFi and Blockchain developent in general. If you would like to experiment with it by yourself please consider to deploy the contract on the testnet only._


- [What the contract can do](#what-the-contract-can-do "Goto what-the-contract-can-do")
- [Prerequisites](#prerequisites "Goto prerequisites")
- [Installation](#installation "Goto installation")
- [Usage](#usage "Goto usage")
- [Todo's](#todos "Goto todos")

## What the contract can do:
* Keep track of unlimited number of employees in the smart contract by defining them with their wallet address.
* Request the most recent consumer price index with the help of Chainlink API Calls.
* Pay employees automatically on a regular basis with the assistance of Chainlink Keepers.
* Allow company to store its assets in the smart contract in WETH and DAI tokens.
* Allow employees to receive their payment in WETH or DAI as they prefer.
* Withdraw left funds to company address.

## Prerequisites

Please install or have installed the following:

- [nodejs and npm](https://nodejs.org/en/download/)
- [python](https://www.python.org/downloads/)
## Installation

1. [Install Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html), if you haven't already. Here is a simple way to install brownie.

```bash
pip3 install eth-brownie
```

2. Clone this repo
```
git clone https://github.com/moonwake769/cpi-incorporated-salary
cd cpi-incorporated-salary
```

3. [Install ganache-cli](https://www.npmjs.com/package/ganache-cli)

```bash
npm install -g ganache-cli
```

If you want to be able to deploy to testnets, do the following. 

4. Set your environment variables

Set your `WEB3_INFURA_PROJECT_ID`, and `PRIVATE_KEY` [environment variables](https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html). 

You can get a `WEB3_INFURA_PROJECT_ID` by getting a free trial of [Infura](https://infura.io/). At the moment, it does need to be infura with brownie. You can find your `PRIVATE_KEY` from your ethereum wallet like [metamask](https://metamask.io/). 

You'll also need testnet rinkeby or Kovan ETH and LINK. You can get LINK and ETH into your wallet by using the [kovan faucets located here](https://docs.chain.link/docs/link-token-contracts#kovan). If you're new to this, [watch this video.](https://www.youtube.com/watch?v=P7FX_1PePX0)

You'll also want an [Etherscan API Key](https://etherscan.io/apis) to verify your smart contracts. 

You can add your environment variables to the `.env` file:
```bash
export WEB3_INFURA_PROJECT_ID=<PROJECT_ID>
export PRIVATE_KEY=<PRIVATE_KEY>
export ETHERSCAN_TOKEN=<YOUR_TOKEN>
```
> DO NOT SEND YOUR KEYS TO GITHUB
> If you do that, people can steal all your funds. Ideally use an account with no real money in it. 

## Usage:
This will deploy the contracts as well as mock contracts, request recent CPI data, add a few employees, fund the contract, and check upkeep.
```bash
brownie run scripts/main.py
```
This will do the same thing... but on Kovan. Make sure that you have minimum 0.5 ETH and 100 LINK on your Kovan testnet account. After that you want to register [new Upkeep](https://keepers.chain.link/). Set the GAS limit to 600000 and add 50 LINK. 
```bash
brownie run scripts/main.py --network kovan
```
