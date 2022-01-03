// SPDX-License-Identifier: MIT
//
pragma solidity ^0.8.7;


////////////////////////////////////////////////////////////////////////////////
// IMPORTING Dependencies
////////////////////////////////////////////////////////////////////////////////


import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/interfaces/KeeperCompatibleInterface.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./TokenSwap.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


////////////////////////////////////////////////////////////////////////////////
// DEFINING Contract
////////////////////////////////////////////////////////////////////////////////


contract CPIIncorporatedSalary is
    Ownable,
    TokenSwap,
    ChainlinkClient,
    KeeperCompatibleInterface
{
    using Chainlink for Chainlink.Request;

    ////////////////////////////////////////////////////////////////////////////
    // DEFINING State Variables and Types
    ////////////////////////////////////////////////////////////////////////////

    struct Employee {
        string pair;
        
        address employee;
        
        IERC20 preferedPaymentToken;
        
        uint256 paidTimes;
        uint256 previousSalary;
        uint256 previousUsedCPI;
        uint256 paymentInterval;
        uint256 previousPaymentTimestamp;
    }

    bytes32 public jobId;
    
    string public apiURL;
    string public apiJsonPath;
    
    address public oracle;
    address[] public employees;
    address payable public company;
    address[] public employeesToPay;
    address payable public employee;
    
    uint256 public fee;
    uint256 public recentCPI;
    uint256 public employeesToPayLength;
    uint256 public minimumFundAmountInDai;
    uint256 public minimumFundAmountInWeth;

    mapping(address => Employee) public employeeToRecentData;
    mapping(string => address) public currencyPairToPriceFeedProxy;

    ////////////////////////////////////////////////////////////////////////////
    // DEFINING Constructor
    ////////////////////////////////////////////////////////////////////////////

    constructor(
        address _oracle,
        string memory _jobId,
        uint256 _fee,
        address _link
    )
    {
        if (_link == address(0)) {
            setPublicChainlinkToken();
        } else {
            setChainlinkToken(_link);
        }
        
        oracle = _oracle;
        jobId = bytes32(bytes(_jobId)); // Begin v0.8.7 supported.
        //jobId = stringToBytes32(_jobId);
        fee = _fee; // (Varies by network and job)
        
        company = payable(msg.sender);
    }

    ////////////////////////////////////////////////////////////////////////////
    // DEFINING Preparation Functions.
    ////////////////////////////////////////////////////////////////////////////

    /**
     *  Assign `_currencyPair` to Chainlink Price Feed proxy address.
     *  @param _currencyPair e.g. ETH/USD, DAI/USD
     *  @param _priceFeedProxy Chainlink Ethereum Price Data Feeds.
     */
    function setPriceFeedProxy(
        string memory _currencyPair, address _priceFeedProxy
    )
        public
        onlyOwner
    {
        currencyPairToPriceFeedProxy[_currencyPair] = _priceFeedProxy;
    }
    
    /**
     * Assign API URL and Json path to the state variables.
     */ 
    function setAPIDataBase(string memory _url, string memory _jsonPath) 
        public
        onlyOwner
    {
        apiURL = _url;
        apiJsonPath = _jsonPath;
    }
    
    ////////////////////////////////////////////////////////////////////////////
    // DEFINING Functions.
    ////////////////////////////////////////////////////////////////////////////
    
    /**
     * Create a Chainlink request to retrieve API response, find the target
     * data, then multiply by 1000000000000000000 
     * (to remove decimal places from data).
     */
    function requestCPIData() public returns (bytes32 requestId) 
    {
        Chainlink.Request memory request = buildChainlinkRequest(
            jobId, address(this), this.fulfill.selector
        );
        // Set the URL to perform the GET request on
        request.add("get", apiURL);
        request.add("path", apiJsonPath);
        // Multiply the result by 1000000000000000000 to remove decimals
        int256 timesAmount = 10**18;
        request.addInt("times", timesAmount);
        // Sends the request
        return sendChainlinkRequestTo(oracle, request, fee);
    }
    
    /**
     * Receive the response in the form of uint256
     */ 
    function fulfill(bytes32 _requestId, uint256 _recentCPI)
        public 
        recordChainlinkFulfillment(_requestId)
    {
        recentCPI = _recentCPI;
    }

    /**
     * Add a new employee.
     */
    function addEmployee(
        address _employee,
        uint256 _initialSalary,
        uint256 _payInterval,
        address _preferedPaymentToken,
        string memory _pair
    ) 
        public
        onlyOwner
    {
        employees.push(_employee); // In ^0.8.0 msg.sender is not auto. payable.
        employeeToRecentData[_employee].employee = _employee;
        employeeToRecentData[_employee].previousSalary = _initialSalary;
        employeeToRecentData[_employee].previousUsedCPI = recentCPI;
        employeeToRecentData[_employee].previousPaymentTimestamp = block.timestamp; 
        employeeToRecentData[_employee].preferedPaymentToken = IERC20(_preferedPaymentToken);
        employeeToRecentData[_employee].paymentInterval = _payInterval;
        employeeToRecentData[_employee].paidTimes = 0;
        employeeToRecentData[_employee].pair = _pair;
    }
    
    /**
     * Checks if the contract requires work to be done.
     */
    function checkUpkeep(bytes calldata checkData)
        external
        override
        returns (bool upkeepNeeded, bytes memory performData)
    {    
        address[] memory tempEmployeesToPay = new address[](employees.length);
        uint256 numberEmployeesToPay = 0;

        for (uint256 i = 0; i < employees.length; i++) {
            employee = payable(employees[i]);
            uint256 paymentInterval = employeeToRecentData[employee].paymentInterval;
            uint256 previousPaidTimestamp = employeeToRecentData[employee].previousPaymentTimestamp;
            
            if ((block.timestamp - previousPaidTimestamp) > paymentInterval) {
                upkeepNeeded = true;
                tempEmployeesToPay[numberEmployeesToPay] = employee;
                numberEmployeesToPay++;
            } 
        }
        return (
            upkeepNeeded,
            abi.encode(tempEmployeesToPay, numberEmployeesToPay)
        );
    }

    /**
     * Performs the work on the contract, if instructed by checkUpkeep().
     */
    function performUpkeep(bytes calldata performData) external override {
        (employeesToPay, employeesToPayLength) = abi.decode(
            performData,(address[], uint256)
        );
        require(employeesToPay.length > 0, "Error!");
        payEmployee();
    }
    
    /**
     * Fund the contract with Ether.
     */
    function fund() public payable {
        require(msg.value >= minimumFundAmountInDai || msg.value >= minimumFundAmountInWeth, "Not enough funded!");
    }
    
    /**
     * Set minimum fund amount based on sum of USD salaries of the employees.
     */
    function getMinimumFundAmount() public returns (uint256) {
        minimumFundAmountInDai = 0;
        minimumFundAmountInWeth = 0;
        for (uint256 i = 0; i < employees.length; i++) {
            employee = payable(employees[i]);
            uint256 minimumFundAmountInUSD = 0;
            string memory pair = employeeToRecentData[employee].pair;
            // Just compering in the Solidity way if `pair == "ETH/USD"` 
            // calling hash and bytes functions.
            if ((keccak256(bytes(pair)) == keccak256(bytes("ETH/USD"))) && (bytes(pair).length == bytes("ETH/USD").length))  {
                minimumFundAmountInUSD = employeeToRecentData[employee].previousSalary;
                minimumFundAmountInWeth += getConversionRate(
                    pair, minimumFundAmountInUSD
                );
            }
            if ((keccak256(bytes(pair)) == keccak256(bytes("DAI/USD"))) && (bytes(pair).length == bytes("DAI/USD").length))  {
                minimumFundAmountInUSD = employeeToRecentData[employee].previousSalary;
                minimumFundAmountInDai += getConversionRate(
                    pair, minimumFundAmountInUSD
                );
            }
        }
    }

    function getConversionRate(
        string memory _pair,
        uint256 _amount
    )
        public
        view
        returns (uint256) 
    {
        if ((keccak256(bytes(_pair)) == keccak256(bytes("DAI/ETH"))) && (bytes(_pair).length == bytes("DAI/ETH").length))  {
            (uint256 price, uint8 decimals) = getPrice(_pair);
            uint256 amountInDAI = (price * _amount) / (10**uint256(decimals));
            return amountInDAI;
        } else {
            (uint256 price, uint8 decimals) = getPrice(_pair);
            uint256 amountInToken = (_amount * (10**uint256(decimals)) / price);
            return amountInToken;
        }
    }
 
    /**
     * Return price of token.
     */
    function getPrice(string memory _pair)
        public
        view
        returns (uint256, uint8)
    {
        address proxy = currencyPairToPriceFeedProxy[_pair];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            proxy
        );
        (
            uint80 roundID,
            int256 price,
            uint256 startedAt,
            uint256 timeStamp,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        return (uint256(price), priceFeed.decimals());
    }

    /**
     * We could instead use 
     *  `payable(msg.sender).transfer(100000000000000000);`
     * but this method is not really recommended.
     *
     * Take self-regulating swap proces over using TokenSwap contract
     * from running Python off-chain script severally.
     */
    function payEmployee() public {
        for (uint256 i = 0; i < employeesToPayLength; i++) {
            employee = payable(employeesToPay[i]);
            uint256 salaryInUSD = getEmployeeUpdatedSalaryInUSD(employee);
            string memory pair = employeeToRecentData[employee].pair;
            IERC20 erc20 = employeeToRecentData[employee].preferedPaymentToken;
            uint256 salaryInERC20 = getConversionRate(pair, salaryInUSD);
            // Paying.
            erc20.approve(address(this), salaryInERC20);
            erc20.transferFrom(address(this), employee, salaryInERC20);
            employeeToRecentData[employee].previousPaymentTimestamp = block.timestamp;
            employeeToRecentData[employee].paidTimes += 1;
        }
    }
    
    /**
     * Return a new updated salary of an employee based on recent CPI.
     */
    function getEmployeeUpdatedSalaryInUSD(address _employee)
        public
        returns (uint256) 
    {
        employee = payable(_employee);
        uint256 previousSalary = employeeToRecentData[employee].previousSalary;
        uint256 previousUsedCPI = employeeToRecentData[employee].previousUsedCPI;
        uint256 newSalary = (previousSalary * recentCPI) / previousUsedCPI;
        // Updating.
        employeeToRecentData[employee].previousSalary = newSalary;
        employeeToRecentData[employee].previousUsedCPI = recentCPI;
        return newSalary;
    }

    /**
     * Convert string object to bytes and return the result.
     */
    function stringToBytes32(string memory source)
        public
        pure
        returns (bytes32 result) 
    {
        bytes memory tempEmptyStringTest = bytes(source);
        if (tempEmptyStringTest.length == 0) return 0x0;
        assembly {
            result := mload(add(source, 32))
        }
    }

    function withdraw() public onlyOwner {
        for (uint256 i = 0; i < employees.length; i++) {
            employee = payable(employees[i]);
            IERC20 erc20 = employeeToRecentData[employee].preferedPaymentToken;
            // Withdraw ERC20.
            uint256 amount = erc20.balanceOf(address(this));
            erc20.approve(address(this), amount);
            erc20.transferFrom(address(this), company, amount);
        }
        // Withdraw Ether.
        (bool sent, bytes memory data) = company.call{value: address(this).balance}("");
        require(sent, "Failed to withdraw");
    }
}
