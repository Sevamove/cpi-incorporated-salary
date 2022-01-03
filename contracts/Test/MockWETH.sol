// SPDX-License-Identifier: MIT

pragma solidity ^0.8.7;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockWETH is ERC20 {
    constructor() public payable ERC20("Mock WETH", "WETH") {
        _mint(msg.sender, 21000000000000000000000000);
    }

    function deposit() public payable {}
}
