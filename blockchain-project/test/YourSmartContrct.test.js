const { expect } = require("chai");

describe("YourSmartContract", function () {
    it("should upload and retrieve a file hash", async function () {
        const YourSmartContract = await ethers.getContractFactory("YourSmartContract");
        const contract = await YourSmartContract.deploy();
        await contract.deployed();

        const fileHash = "example_file_hash";
        await contract.uploadFile(fileHash);

        expect(await contract.getFile()).to.equal(fileHash);
    });
});
