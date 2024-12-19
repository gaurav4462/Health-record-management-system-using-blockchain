import React, { useEffect, useState } from 'react';
import './UserPage.css';
import { FaUserMd, FaEnvelope, FaUser, FaSignOutAlt, FaPlus, FaMinus, FaBell } from 'react-icons/fa';
import { Link, useNavigate } from 'react-router-dom';
import { ethers } from 'ethers';
import PatientRecordContract from './PatientRecord.json'; // Import the ABI

const contractAddress = '0x4c79414779c2ef1bdbfeb926982fc104c013849e';  // Replace with actual contract address

const UserPage = () => {
    const navigate = useNavigate();
    const [userInfo, setUserInfo] = useState(null);
    const [doctors, setDoctors] = useState([]);
    const [files, setFiles] = useState([]);  // Store files fetched from blockchain
    const [remarks, setRemarks] = useState({}); // Store remarks indexed by doctor username
    const [error, setError] = useState(null);
    const [showRemarks, setShowRemarks] = useState(false); // State for showing remarks

    const handleLogout = () => {
        navigate('/');
    };

    const fetchUserData = async () => {
        const username = localStorage.getItem('userUsername'); // Get username from local storage
        try {
            const response = await fetch(`http://localhost:8000/user/${username}/doctors`);
            if (!response.ok) {
                throw new Error('User not found');
            }
            const data = await response.json();
            setUserInfo(data.user);
            setDoctors(data.doctors);
        } catch (err) {
            setError(err.message);
        }
    };

    const fetchRemarksForDoctors = async () => {
        if (userInfo && doctors.length > 0) {
            const doctorUsernames = doctors.map(doctor => doctor.username); // Collect all doctor usernames
            try {
                const response = await fetch(`http://localhost:8000/remarks/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        patient_phone: userInfo.phone,  // Use the correct patient phone from userInfo
                        doctor_usernames: doctorUsernames, // Pass all doctor usernames at once
                    }),
                });

                if (response.ok) {
                    const remarksData = await response.json();
                    setRemarks(remarksData); // Set remarks data for all doctors
                } else {
                    setRemarks({});
                }
            } catch (error) {
                console.error('Error fetching remarks:', error);
                setError('Error fetching remarks');
            }
        }
    };

    const fetchFilesFromBlockchain = async () => {
        if (window.ethereum && userInfo) {
            try {
                const provider = new ethers.BrowserProvider(window.ethereum);
                const signer = await provider.getSigner();
                const contract = new ethers.Contract(contractAddress, PatientRecordContract.abi, signer);

                const patientId = userInfo.id;

                const patientFiles = await contract.getPatientFiles(patientId);

                const fileData = patientFiles.map((file) => ({
                    doctorGovId: file.doctorGovId,
                    ipfsUrl: file.ipfsUrl,
                    timestamp: new Date(Number(file.timestamp.toString()) * 1000).toLocaleString(),
                }));

                setFiles(fileData);
            } catch (error) {
                console.error('Error fetching files from blockchain:', error);
                setError('Error fetching files from blockchain');
            }
        } else {
            alert('Please install MetaMask to interact with the blockchain.');
        }
    };

    const handleAddAccess = async (doctorGovId) => {
        try {
            const userId = userInfo.id;
            const response = await fetch('http://localhost:8000/add-access/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    doctor_gov_id: doctorGovId,
                    user_id: userId,
                }),
            });

            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                setDoctors(doctors.map(doctor => 
                    doctor.gov_id === doctorGovId ? { ...doctor, access: 'yes' } : doctor
                ));
            } else {
                alert(result.detail);
            }
        } catch (error) {
            console.error('Error adding access:', error);
            alert('Failed to grant access');
        }
    };

    const handleRemoveAccess = async (doctorGovId) => {
        try {
            const userId = userInfo.id;
            const response = await fetch('http://localhost:8000/remove-access/', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    doctor_gov_id: doctorGovId,
                    user_id: userId,
                }),
            });

            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                setDoctors(doctors.map(doctor => 
                    doctor.gov_id === doctorGovId ? { ...doctor, access: 'no' } : doctor
                ));
            } else {
                alert(result.detail);
            }
        } catch (error) {
            console.error('Error removing access:', error);
            alert('Failed to remove access');
        }
    };

    useEffect(() => {
        fetchUserData();
    }, []);

    useEffect(() => {
        if (userInfo && doctors.length > 0) {
            fetchFilesFromBlockchain();
            fetchRemarksForDoctors();  // Now calls fetchRemarksForDoctors only after doctors are fetched
        }
    }, [userInfo, doctors]);

    if (error) {
        return <p style={{ color: 'red' }}>{error}</p>;
    }

    if (!userInfo) {
        return <p>Loading...</p>;
    }

    // Toggle the visibility of the remarks
    const toggleRemarks = () => {
        setShowRemarks(!showRemarks);
    };

    return (
        <div className="dashboard-container">
            <nav className="navbar">
                <div className="nav-links">
                    <Link to="/dashboard" className="link">Dashboard</Link>
                </div>
                <div className="profile">
                    <FaUser className="profile-icon" />
                    <button className="link" onClick={handleLogout}>
                        <FaSignOutAlt /> Logout
                    </button>
                </div>
                {/* Notification Button */}
                <div className="notification-btn" onClick={toggleRemarks}>
                    <FaBell size={30} color={remarks && Object.keys(remarks).length > 0 ? 'red' : 'black'} />
                </div>
            </nav>

            {/* Show remarks in a box with close button */}
            
            {showRemarks && (
                
                

                
                <div className="remarks-container">
                    <div className="remarks-header">
                        <h2>Remarks</h2>
                        <button className="close-btn" onClick={toggleRemarks}>×</button>
                    </div>
                    {Object.keys(remarks).length === 0 ? (
                        <p>No remarks available.</p>
                    ) : (
                        Object.keys(remarks).map((doctorUsername) => (
                            <div key={doctorUsername} className="remarks-section">
                                {remarks[doctorUsername].map((remark, index) => (
                                    // <p><strong>Doc ID:</strong> {doctor.gov_id}</p>
                                    <p key={index}><strong>Remark {index + 1}:</strong> {remark.remark}</p>
                                ))}
                            </div>
                        ))
                    )}
                </div>
            )}

            <div className="user-info-card">
                <h2>User Information</h2>
                <div className="user-details">
                    <p><strong>id:</strong> {userInfo.id}</p>
                    <p><strong>Name:</strong> {userInfo.name}</p>
                    <p><strong>Address:</strong> {userInfo.address}</p>
                    <p><strong>Phone:</strong> {userInfo.phone}</p>
                    <p><strong>Email:</strong> {userInfo.email}</p>
                </div>
            </div>

            {/* Doctors Section */}
            {doctors.length > 0 ? (
                <div className="doctor-cards-container">
                    {doctors.map((doctor) => (
                        <div key={doctor.username} className="doctor-card">
                            <div className="doctor-info">
                                <h4>{doctor.name}</h4>
                                <p><strong>Doc ID:</strong> {doctor.gov_id}</p>
                                <p><strong>Email:</strong> {doctor.email}</p>
                                <p><strong>Degree:</strong> {doctor.degree}</p>
                                <p><strong>Practitioner Type:</strong> {doctor.practitioner_type}</p>
                            </div>

                            {/* Plus and Minus icons */}
                            <div className="doctor-card-actions">
                                <FaPlus 
                                    className="doctor-card-action-icon" 
                                    onClick={() => handleAddAccess(doctor.gov_id)} 
                                />
                                <FaMinus 
                                    className="doctor-card-action-icon" 
                                    onClick={() => handleRemoveAccess(doctor.gov_id)} 
                                />
                            </div>

                            {/* Files section */}
                            <div className="files-list">
                                {files.filter(file => file.doctorGovId === doctor.gov_id).length > 0 ? (
                                    <div className="files-container">
                                        {files.filter(file => file.doctorGovId === doctor.gov_id).map((file, index) => (
                                            <div key={index} className="file-card">
                                                <p><strong>File {index + 1}:</strong></p>
                                                <p><strong>Uploaded On:</strong> {file.timestamp}</p>
                                                <p><strong>Open File:</strong> <a href={file.ipfsUrl} target="_blank" rel="noopener noreferrer">View File</a></p>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p>No files uploaded for this doctor.</p>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <p>No associated doctors found.</p>
            )}
        </div>
    );
};

export default UserPage;
