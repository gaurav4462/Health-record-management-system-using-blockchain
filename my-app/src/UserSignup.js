// src/Signup.js
import React, { useState } from 'react';
import './UserSignup.css';

const Signup = () => {
    const [formData, setFormData] = useState({
        name: '',
        address: '',
        phone: '',
        email: '',
        username: '',
        password: '',
        confirmPassword: ''
    });
    
    const [errors, setErrors] = useState({});
    const [message, setMessage] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const validate = () => {
        const newErrors = {};
        const phoneRegex = /^[0-9]{10}$/; // Example for 10-digit phone number
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!formData.name) newErrors.name = 'Name is required';
        if (!formData.address) newErrors.address = 'Address is required';
        if (!phoneRegex.test(formData.phone)) newErrors.phone = 'Invalid phone number';
        if (!emailRegex.test(formData.email)) newErrors.email = 'Invalid email address';
        if (!formData.username) newErrors.username = 'Username is required';
        if (!formData.password) newErrors.password = 'Password is required';
        if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';

        return newErrors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const validationErrors = validate();
        if (Object.keys(validationErrors).length === 0) {
            try {
                const response = await fetch('http://localhost:8000/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: formData.name,
                        address: formData.address,
                        phone: formData.phone,
                        email: formData.email,
                        username: formData.username,
                        password: formData.password,
                    }),
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    setMessage(data.message);
                    // Clear the form
                    setFormData({
                        name: '',
                        address: '',
                        phone: '',
                        email: '',
                        username: '',
                        password: '',
                        confirmPassword: ''
                    });
                    setErrors({});
                } else {
                    setMessage(data.detail || 'Registration failed');
                }
            } catch (error) {
                console.error('Error during registration:', error);
                setMessage('An error occurred. Please try again.');
            }
        } else {
            setErrors(validationErrors);
        }
    };

    return (
        <div>
            <h2>User Signup</h2>
            {message && <p>{message}</p>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Name:</label>
                    <input type="text" name="name" value={formData.name} onChange={handleChange} />
                    {errors.name && <span>{errors.name}</span>}
                </div>
                <div>
                    <label>Address:</label>
                    <input type="text" name="address" value={formData.address} onChange={handleChange} />
                    {errors.address && <span>{errors.address}</span>}
                </div>
                <div>
                    <label>Phone Number:</label>
                    <input type="text" name="phone" value={formData.phone} onChange={handleChange} />
                    {errors.phone && <span>{errors.phone}</span>}
                </div>
                <div>
                    <label>Email:</label>
                    <input type="email" name="email" value={formData.email} onChange={handleChange} />
                    {errors.email && <span>{errors.email}</span>}
                </div>
                <div>
                    <label>Username:</label>
                    <input type="text" name="username" value={formData.username} onChange={handleChange} />
                    {errors.username && <span>{errors.username}</span>}
                </div>
                <div>
                    <label>Password:</label>
                    <input type="password" name="password" value={formData.password} onChange={handleChange} />
                    {errors.password && <span>{errors.password}</span>}
                </div>
                <div>
                    <label>Confirm Password:</label>
                    <input type="password" name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} />
                    {errors.confirmPassword && <span>{errors.confirmPassword}</span>}
                </div>
                <button type="submit">Create Account</button>
            </form>
        </div>
    );
};

export default Signup;
