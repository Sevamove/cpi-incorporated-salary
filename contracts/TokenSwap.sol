// SPDX-Licence-Identifier: MIT
pragma solidity ^0.8.7;

import "../interfaces/ISwapRouter.sol";
import "../interfaces/IQuoter.sol";
import "./libraries/TransferHelper.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 
contract TokenSwap {

    ISwapRouter public constant swapRouter = ISwapRouter(
        0xE592427A0AEce92De3Edee1F18E0157C05861564
    );
    IQuoter public constant quoter = IQuoter(
        0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6
    );
    uint24 public constant swapFee = 3000; // fee

    /**
     * Convert the specified amount of `_companyToken` and transfer it to the employee.
     */
    function convertCompanyTokensToEmployeeTokens(
        IERC20 _companyToken,
        IERC20 _employeeToken,
        uint256 _valueToConvert,
        uint256 _valueToConvertMaximum,
        uint256 _valueToRecieve,
        address _employee
    ) external returns (uint256 amountIn) {
        IERC20 companyToken = IERC20(_companyToken);
        IERC20 employeeToken = IERC20(_employeeToken);

        companyToken.approve(address(swapRouter), _valueToConvert);
        TransferHelper.safeApprove(address(companyToken), address(swapRouter), _valueToConvertMaximum);

        ISwapRouter.ExactOutputSingleParams memory params =
            ISwapRouter.ExactOutputSingleParams({
                tokenIn: address(companyToken),
                tokenOut: address(employeeToken),
                fee: swapFee,
                recipient: address(_employee),
                deadline: block.timestamp,
                //amountOut: getEstimatedEmployeeTokenAmt(
                //    address(employeeToken),
                //    address(companyToken),
                //    10000000000000000000
                //),//_valueToRecieve,
                amountOut: _valueToRecieve,
                amountInMaximum: _valueToConvertMaximum,
                sqrtPriceLimitX96: 0
            });
        amountIn = swapRouter.exactOutputSingle(params);
        if (_valueToConvert < _valueToConvertMaximum) {
            TransferHelper.safeApprove(address(companyToken), address(swapRouter), 0);
            TransferHelper.safeTransfer(address(companyToken), address(this), _valueToConvertMaximum - _valueToConvert);
        }
    }

    //function getEstimatedEmployeeTokenAmt(
    //    address _employeeToken,
    //    address _companyToken,
    //    uint256 _employeeAdjustedSalaryInDollars
    //) public payable returns (uint256) {
    //    address tokenIn = _employeeToken;
    //    address tokenOut = _companyToken; /// this is the checksummed USDC addr on Ropsten testnet
    //    uint24 fee = 3000; /// 0.30% (medium-risk) fee tier
    //    uint160 sqrtPriceLimitX96 = 0;

    //    /// get a quote denominated in EmployeeToken
    //    return
    //        quoter.quoteExactOutputSingle(
    //            tokenIn,
    //            tokenOut,
    //            fee,
    //            _employeeAdjustedSalaryInDollars,
    //            sqrtPriceLimitX96
    //        );
    //}
}
