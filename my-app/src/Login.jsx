import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Signup from './Signup';
import DoctorSignup from './DoctorSignup';
import UserSignup from './UserSignup'; 
//import DoctorTitle from './DoctorTitle';
import { useNavigate } from 'react-router-dom';

function App() {
  const navigate = useNavigate();
  const [isSignup, setIsSignup] = useState(false);
  const [role, setRole] = useState('');
  const [loginAs, setLoginAs] = useState('Doctor');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [captcha, setCaptcha] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');
  const [message, setMessage] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const captchaCanvasRef = useRef(null);

  const generateCaptcha = () => {
    const characters = 'ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz0123456789@#+*!';
    let result = '';
    for (let i = 0; i < 6; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    setCaptcha(result);
    drawCaptcha(result);
  };

  const drawCaptcha = (text) => {
    const canvas = captchaCanvasRef.current;
    const ctx = canvas.getContext('2d');

    canvas.width = 200;
    canvas.height = 80;

    ctx.fillStyle = '#f3f4f6';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.font = '40px Arial';
    ctx.fillStyle = '#4a90e2';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, canvas.width / 2, canvas.height / 2);

    for (let i = 0; i < 5; i++) {
      ctx.beginPath();
      ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
      ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
      ctx.strokeStyle = '#4a90e2';
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (captchaInput !== captcha) {
      alert("Captcha doesn't match!");
      return;
    }

if (loginAs === 'Doctor') {
  try {
    const loginResponse = await fetch('http://localhost:8000/doctor/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        password,
      }),
    });
    const loginData = await loginResponse.json();

    if (loginResponse.ok) {
      setMessage('Login successful!');
      setIsLoggedIn(true);
      console.log('Login successful!');

      localStorage.setItem('doctorUsername', username);

      navigate('/doctortitle'); 
    } else {
      setMessage(loginData.detail || 'Login failed');
    }
  } catch (error) {
    console.error('Error:', error);
    setMessage('An error occurred while logging in.');
  }
}


if (loginAs === 'User') {
  try {
    const response = await fetch('http://localhost:8000/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    if (response.ok) {
      setMessage('Login successful!');
      setIsLoggedIn(true);
      localStorage.setItem('userUsername', username); 
      navigate('/userpage'); 
    } else {
      setMessage(data.detail || 'Login failed');
    }
  } catch (error) {
    console.error('Error:', error);
    setMessage('An error occurred while logging in.');
  }
}


    if (loginAs === 'Admin') {
      try {
        const response = await fetch('http://localhost:8000/admin/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username,
            password,
          }),
        });
        const data = await response.json();
        if (response.ok) {
          setMessage('Admin Login successful!');
          setIsLoggedIn(true);
          console.log('Admin data:', data);
          navigate('/Admin');
        } else {
          setMessage(data.detail || 'Login failed');
        }
      } catch (error) {
        console.error('Error:', error);
        setMessage('An error occurred while logging in.');
      }
    }
  };

  useEffect(() => {
    generateCaptcha();
  }, []);

  const handleRoleSelection = (selectedRole) => {
    setRole(selectedRole);
    setIsSignup(true);
  };

  const handleSignupButtonClick = () => {
    setRole('');
    setIsSignup(true);
  };

  return (
    <div className="App fancy-app">
      <div className="left-section fancy-left">
        <div className="left-content">
          <h1>Welcome to Health Record Management System</h1>
          <p>Your gateway to managing and accessing health records.</p>
        </div>
      </div>

      <div className="right-section fancy-right">
        {!isSignup ? (
          <div className="login-form fancy-form">
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
              <div className="form-group">
                <label htmlFor="loginAs">Login as:</label>
                <select
                  id="loginAs"
                  value={loginAs}
                  onChange={(e) => setLoginAs(e.target.value)}
                  className="dropdown fancy-dropdown"
                >
                  <option value="Doctor">Doctor</option>
                  <option value="User">User</option>
                  <option value="Admin">Admin</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="username">Username:</label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  placeholder="Enter your username"
                  className="input fancy-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password:</label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Enter your password"
                  className="input fancy-input"
                />
              </div>

              <div className="form-group captcha-group">
                <label htmlFor="captcha">Captcha:</label>
                <canvas ref={captchaCanvasRef} className="captcha-display"></canvas>
                <input
                  type="text"
                  id="captcha-input"
                  value={captchaInput}
                  onChange={(e) => setCaptchaInput(e.target.value)}
                  required
                  placeholder="Enter the captcha"
                  className="input fancy-input"
                />
              </div>

              <button type="submit" className="btn-submit fancy-button">Submit</button>
            </form>
            {message && <p>{message}</p>}
            <p className="toggle-form">
              Don't have an account?{' '}
              <button className="signup-button fancy-button" onClick={handleSignupButtonClick}>
                Sign Up
              </button>
            </p>
          </div>
        ) : role === '' ? (
          <div className="role-selection fancy-form">
            <h2>Select Your Role</h2>
            <div className="role-buttons">
              <button className="role-button fancy-button" onClick={() => handleRoleSelection('Doctor')}>
                Sign Up as Doctor
              </button>
              <button className="role-button fancy-button" onClick={() => handleRoleSelection('User')}>
                Sign Up as User
              </button>
              <button className="role-button fancy-button" onClick={() => handleRoleSelection('Admin')}>
                Sign Up as Admin
              </button>
            </div>
          </div>
        ) : role === 'Doctor' ? (
          <DoctorSignup setIsSignup={setIsSignup} />
        ) : role === 'User' ? (
          <UserSignup setIsSignup={setIsSignup} />
        ) : (
          <Signup role={role} setIsSignup={setIsSignup} />
        )}
      </div>
    </div>
  );
}

export default App;