import React, { useState } from 'react';
import axios from 'axios';
import './DoctorSignup.css';

const DoctorSignup = () => {
    const [govID, setGovID] = useState('');
    const [otp, setOtp] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [message, setMessage] = useState('');
    const [otpStatus, setOtpStatus] = useState('');
    const [otpSent, setOtpSent] = useState(false);
    const [otpVerified, setOtpVerified] = useState(false);

    // Fields for signup
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    // send OTP
    const handleIDCheck = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8000/check-government-id/', {
                gov_id: govID,
            });
            console.log(response);
            setMessage(response.data.message);
            setOtpStatus(response.data.otp_status);
            setPhoneNumber(response.data.phone_number); 
            setOtpSent(true); 
        } catch (error) {
            const errorMessage = extractErrorMessage(error);
            setMessage(errorMessage);
        }
    };

    // verify OTP
    const handleOTPVerify = async (e) => {
        e.preventDefault();
    
        console.log('Phone Number:', phoneNumber);
        console.log('OTP:', otp);
    
        if (!otp) {
            setMessage('OTP is required.');
            return;
        }
    
        try {
            const response = await axios.post('http://localhost:8000/verify-otp/', new URLSearchParams({
                phone_number: phoneNumber,
                otp: otp,
            }));
            setMessage(response.data.message);
            setOtpVerified(true);
        } catch (error) {
            console.error(error);
            const errorMessage = extractErrorMessage(error);
            setMessage(errorMessage);
        }
    };

    const handleSignup = async (e) => {
        e.preventDefault();

        // Check OTP is verified
        if (!otpVerified) {
            setMessage('Please verify OTP first.');
            return;
        }

        // Check passwords match
        if (password !== confirmPassword) {
            setMessage('Passwords do not match.');
            return;
        }

        try {
            const response = await axios.post('http://localhost:8000/signup/', {
                gov_id: govID,
                username: username,
                email: email,
                password: password,
            });
            setMessage(response.data.message); // Success message
        } catch (error) {
            const errorMessage = extractErrorMessage(error);
            setMessage(errorMessage);
        }
    };

    const extractErrorMessage = (error) => {
        if (error.response && error.response.data) {
            const { detail } = error.response.data;
            if (Array.isArray(detail)) {
                return detail.map((err) => err.msg || err.message).join(', ');
            }
            return detail || 'An unexpected error occurred';
        }
        return 'An error occurred. Please try again.';
    };

    return (
        <div className="doctor-signup-container">
            <form className="fancy-form" onSubmit={handleIDCheck}>
                <h2>Doctor Signup</h2>

                {/* Government ID Field */}
                <div className="form-group">
                    <label htmlFor="govID">Government ID</label>
                    <input
                        type="text"
                        id="govID"
                        className="input"
                        value={govID}
                        onChange={(e) => setGovID(e.target.value)}
                        required
                    />
                </div>

                {/* Username Field */}
                <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input
                        type="text"
                        id="username"
                        className="input"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>

                {/* Email Field */}
                <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        className="input"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>

                {/* Password Field */}
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        className="input"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>

                {/* Confirm Password Field */}
                <div className="form-group">
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        className="input"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                </div>

                {/* OTP Input and Verify Button */}
                {otpSent && (
                    <div className="form-group">
                        <label htmlFor="otp">Enter OTP</label>
                        <input
                            type="text"
                            id="otp"
                            className="input"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            required
                        />
                    </div>
                )}

                {/* Button to check Government ID and initiate OTP sending */}
                <button type="submit" className="btn-submit">
                    {otpSent ? 'Resend OTP' : 'Check Government ID'}
                </button>

                {/* Button to verify OTP */}
                {otpSent && !otpVerified && (
                    <button className="btn-submit" onClick={handleOTPVerify}>
                        Verify OTP
                    </button>
                )}

                {/* Display message or error */}
                {message && <div className="message">{message}</div>}

                {/* Signup Button, enabled only after OTP is verified */}
                {otpVerified && (
                    <button
                        className="btn-submit"
                        onClick={handleSignup}
                    >
                        Signup
                    </button>
                )}
            </form>
        </div>
    );
};

export default DoctorSignup;
