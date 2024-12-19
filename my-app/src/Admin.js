import React, { useState, useEffect } from 'react';
import './Admin.css';

function Admin() {
  const [doctors, setDoctors] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [selectedUser, setSelectedUser] = useState('');
  const [message, setMessage] = useState('');

  // Fetch doctors and users data from backend
  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch doctor names
        const doctorResponse = await fetch('http://localhost:8000/admin/doctors');
        const doctorData = await doctorResponse.json();
        if (doctorResponse.ok) {
          setDoctors(doctorData);
        } else {
          setMessage('Error fetching doctors data');
        }

        // Fetch user names
        const userResponse = await fetch('http://localhost:8000/admin/users');
        const userData = await userResponse.json();
        if (userResponse.ok) {
          setUsers(userData);
        } else {
          setMessage('Error fetching users data');
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setMessage('An error occurred while fetching data.');
      }
    }

    fetchData();
  }, []);

  // Handle the "Add" button click
  const handleAdd = async () => {
    if (!selectedDoctor || !selectedUser) {
      setMessage('Please select both a doctor and a user.');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/admin/add-record', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          doctor_username: selectedDoctor,
          user_username: selectedUser,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setMessage('Record added successfully!');
      } else {
        setMessage(data.detail || 'Error adding record');
      }
    } catch (error) {
      console.error('Error adding record:', error);
      setMessage('An error occurred while adding the record.');
    }
  };

  return (
    <div className="admin-container">
      <h1>Admin Dashboard</h1>

      <div className="dropdown-container">
        <div className="dropdown-block">
          <label htmlFor="doctor-select">Select Doctor:</label>
          <select
            id="doctor-select"
            value={selectedDoctor}
            onChange={(e) => setSelectedDoctor(e.target.value)}
          >
            <option value="">--Select Doctor--</option>
            {doctors.map((doctor) => (
              <option key={doctor.username} value={doctor.username}>
                {doctor.username}
              </option>
            ))}
          </select>
        </div>

        <div className="dropdown-block">
          <label htmlFor="user-select">Select User:</label>
          <select
            id="user-select"
            value={selectedUser}
            onChange={(e) => setSelectedUser(e.target.value)}
          >
            <option value="">--Select User--</option>
            {users.map((user) => (
              <option key={user.username} value={user.username}>
                {user.username}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button className="add-btn" onClick={handleAdd}>
        Add
      </button>

      {message && <p>{message}</p>}
    </div>
  );
}

export default Admin;
