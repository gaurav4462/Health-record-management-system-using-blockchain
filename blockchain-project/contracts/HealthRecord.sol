pragma solidity ^0.8.0;

contract HealthRecord {
    struct Record {
        string patientId;
        string fileHash;
        address uploader;
    }

    mapping(string => Record[]) public records;

    event FileUploaded(string patientId, string fileHash, address uploader);

    function uploadFile(string memory patientId, string memory fileHash) public {
        records[patientId].push(Record(patientId, fileHash, msg.sender));
        emit FileUploaded(patientId, fileHash, msg.sender);
    }

    function getRecords(string memory patientId) public view returns (Record[] memory) {
        return records[patientId];
    }
}
