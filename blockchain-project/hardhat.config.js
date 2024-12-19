require('@nomiclabs/hardhat-ethers');
require('dotenv').config();

const { ALCHEMY_API_KEY, DEPLOYER_PRIVATE_KEY } = process.env;

module.exports = {
  solidity: "0.8.0", // Adjust the version as needed
  networks: {
    goerli: {
      url: `https://eth-goerli.alchemyapi.io/v2/${ALCHEMY_API_KEY}`,
      accounts: [`0x${DEPLOYER_PRIVATE_KEY}`]
    }
  }
};
