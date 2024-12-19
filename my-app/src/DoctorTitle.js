import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import PatientRecordContract from './PatientRecord.json';
import './DoctorTitle.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserCircle } from '@fortawesome/free-solid-svg-icons';
import { Link, useNavigate } from 'react-router-dom';

const contractAddress = '0x4c79414779c2ef1bdbfeb926982fc104c013849e'; 

const DoctorTitle = () => {
  const navigate = useNavigate();
  const [doctorData, setDoctorData] = useState(null);
  const [patientsData, setPatientsData] = useState([]); 
  const [patientAccess, setPatientAccess] = useState({}); 
  const [error, setError] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState({}); 
  const [remarks, setRemarks] = useState({}); 
  const [isUpdated, setIsUpdated] = useState({}); 
  const [patientFiles, setPatientFiles] = useState({}); 

  useEffect(() => {
    const username = localStorage.getItem('doctorUsername');
    if (username) {
      fetchDoctorPatientInfo(username);
    } else {
      setError('No doctor username found!');
    }
  }, []);

  const fetchDoctorPatientInfo = async (doctorUsername) => {
    try {
      const response = await fetch(`http://localhost:8000/doctor/${doctorUsername}/patients`);
      const data = await response.json();
      if (response.ok) {
        setDoctorData(data.doctor);
        setPatientsData(data.patients);
        checkAccessForPatients(data.patients, data.doctor.gov_id); 
      } else {
        setError(data.detail || 'Failed to fetch doctor-patient data.');
      }
    } catch (err) {
      setError('An error occurred while fetching data.');
      console.error(err);
    }
  };

  const checkAccessForPatients = async (patients, doctorGovId) => {
    const accessData = {};
    for (const patient of patients) {
      try {
        const response = await fetch(
          `http://localhost:8000/check-access/?doctor_gov_id=${doctorGovId}&user_id=${patient.id}`
        );
        const data = await response.json();
        accessData[patient.id] = data.has_access;
      } catch (err) {
        console.error('Error checking access:', err);
      }
    }
    setPatientAccess(accessData);
  };

  const handleLogout = () => {
    navigate('/');
  };

  const handleFileChange = (e, patientId) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFiles((prevState) => ({
        ...prevState,
        [patientId]: file, 
      }));
    }
  };

  const handleFileUpload = async (patientId) => {
    if (selectedFiles[patientId]) {
      try {
        const added = await uploadFileToIPFS(selectedFiles[patientId]);
        const url = `https://ipfs.io/ipfs/${added}`;
        console.log(url);
        await uploadToBlockchain(patientId, url);
        alert(`File uploaded successfully for patient ${patientId}!`);
      } catch (error) {
        console.error('Error uploading file to IPFS:', error);
        alert('Error uploading file to IPFS. Please check the console for details.');
      }
    } else {
      alert('Please select a file to upload.');
    }
  };

  const handleRemarksChange = (e, patientphone) => {
    setRemarks((prevRemarks) => ({
      ...prevRemarks,
      [patientphone]: e.target.value,
    }));
  };

  const handleUpdateOrAddRemark = async (patientPhone) => {
    if (remarks[patientPhone]) {
      try {
        const response = await fetch('http://localhost:8000/add_or_update_remark', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            doctorUsername: localStorage.getItem('doctorUsername'),
            patientPhone,
            remark: remarks[patientPhone],
          }),
        });

        if (response.ok) {
          const data = await response.json();
          alert(data.message);  
          setIsUpdated((prevState) => ({
            ...prevState,
            [patientPhone]: true,  
          }));
        } else {
          const data = await response.json();
          alert(data.detail || 'Failed to update remark');
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error occurred while processing the remark.');
      }
    } else {
      alert('Please enter a remark.');
    }
  };

  const uploadFileToIPFS = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const pinataUrl = 'https://api.pinata.cloud/pinning/pinFileToIPFS';
      const headers = {
        'pinata_api_key': '4436b54272344587ff3e',  
        'pinata_secret_api_key': 'c6a6e8c96ea47d0747650f7322928ceefbb56706bfa1a57aa836e84d1ccbb57a',  
      };
      const response = await fetch(pinataUrl, {
        method: 'POST',
        headers: headers,
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to upload file to Pinata: ${errorText}`);
      }

      const data = await response.json();
      return data.IpfsHash; 
    } catch (error) {
      console.error('Error uploading file to Pinata:', error);
      throw error;
    }
  };

  const uploadToBlockchain = async (patientId, ipfsUrl) => {
    if (window.ethereum) {
      try {
        if (!PatientRecordContract || !PatientRecordContract.abi) {
          throw new Error('Contract ABI is undefined or incorrect');
        }
        await window.ethereum.request({ method: 'eth_requestAccounts' }); 
        const provider = new ethers.BrowserProvider(window.ethereum);
        const signer = await provider.getSigner();
        const contract = new ethers.Contract(contractAddress, PatientRecordContract.abi, signer);

        const doctorGovId = doctorData ? doctorData.gov_id : ''; 

        console.log('Contract instance:', contract);
        const tx = await contract.uploadFile(patientId, doctorGovId, ipfsUrl);
        await tx.wait(); 

        alert('File uploaded to blockchain successfully!');
      } catch (error) {
        console.error('Error uploading to blockchain:', error);
        alert('Error uploading to blockchain. Please check the console for details.');
      }
    } else {
      alert('Please install MetaMask to interact with the blockchain.');
    }
  };

  const fetchFilesFromBlockchain = async (patientId) => {
    if (window.ethereum && doctorData) {
      try {
        const provider = new ethers.BrowserProvider(window.ethereum);
        const signer = await provider.getSigner();
        const contract = new ethers.Contract(contractAddress, PatientRecordContract.abi, signer);

        const patientFilesFromBlockchain = await contract.getPatientFiles(patientId);

        const fileData = patientFilesFromBlockchain.map((file) => ({
          doctorGovId: file.doctorGovId,
          ipfsUrl: file.ipfsUrl,
          timestamp: new Date(Number(file.timestamp.toString()) * 1000).toLocaleString(),
        }));

        // Store files in the patientFiles state by patientId
        setPatientFiles((prevFiles) => ({
          ...prevFiles,
          [patientId]: fileData,
        }));
      } catch (error) {
        console.error('Error fetching files from blockchain:', error);
        setError('Error fetching files from blockchain');
      }
    } else {
      alert('Please install MetaMask to interact with the blockchain.');
    }
  };

  return (
    <div className="doctor-container">
      <div className="doctor-header">
  <FontAwesomeIcon icon={faUserCircle} size="3x" />
  <h1>Welcome, {doctorData?.name || 'Doctor'}</h1>
  {/* <p>{doctorData?.gov_id}</p> */}
  <button onClick={handleLogout} className="logout-btn">Logout</button>
</div>


      <h3>Doctor Information</h3>
      {doctorData && (
        <div className="doctor-info">
          <p><strong>Name:</strong> {doctorData.name}</p>
          <p><strong>Government ID:</strong> {doctorData.gov_id}</p>
          <p><strong>Email:</strong> {doctorData.email}</p>
        </div>
      )}

      <h3>Patient List</h3>

      {patientsData.length > 0 ? (
        patientsData.map((patient) => (
          <div className="patient-info-card" key={patient.id}>
            <div className="patient-card-header">
              {patientAccess[patient.id] && (
                <button
                  className="access-btn"
                  onClick={() => fetchFilesFromBlockchain(patient.id)}
                >
                  Access Granted
                </button>
              )}
            </div>

            <h3>Patient Information</h3>
            <p><strong>id:</strong> {patient.id}</p>
            <p><strong>Name:</strong> {patient.name}</p>
            <p><strong>Email:</strong> {patient.email}</p>
            <p><strong>Phone:</strong> {patient.phone}</p>

            <div className="file-upload-section">
              <input
                type="file"
                onChange={(e) => handleFileChange(e, patient.id)}
                className="file-input"
              />
              <button
                onClick={() => handleFileUpload(patient.id)}
                className="btn-upload"
              >
                Upload File
              </button>
            </div>

            <div className="remarks-section">
              <textarea
                value={remarks[patient.phone] || ''}
                onChange={(e) => handleRemarksChange(e, patient.phone)}
                placeholder="Enter remark"
                rows="4"
                className="remarks-input"
              ></textarea>
              <button
                onClick={() =>
                  isUpdated[patient.phone] ? handleUpdateOrAddRemark(patient.phone) : handleUpdateOrAddRemark(patient.phone)
                }
                className="btn-accept"
              >
                {isUpdated[patient.phone] ? 'Update' : 'update'}
              </button>
            </div>

            {/* Display the files for this specific patient */}
            {patientFiles[patient.id] && patientFiles[patient.id].length > 0 && (
              <div className="files-section">
                <h4>Patient Files</h4>
                <ul>
                  {patientFiles[patient.id].map((file, index) => (
                    <li key={index}>
                      <a href={file.ipfsUrl} target="_blank" rel="noopener noreferrer">
                        File (Uploaded on {file.timestamp})
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))
      ) : (
        <p>No patients found for this doctor.</p>
      )}
    </div>
  );
};

export default DoctorTitle;
