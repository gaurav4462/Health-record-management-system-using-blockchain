import React from 'react';
import { Link } from 'react-router-dom';
import './Signup.css'; // Ensure this path is correct

function Signup() {
  return (
    <div className="signup-container fancy-form">
      <h2>Select Signup Option</h2>
      <div className="signup-options">
        <Link to="/doctor_signup">
          <button className="btn-signup-option">Sign Up as Doctor</button>
        </Link>
        <Link to="/user_signup">
          <button className="btn-signup-option">Sign Up as User</button>
        </Link>
        <Link to="/admin_signup">
          <button className="btn-signup-option">Sign Up as Admin</button>
        </Link>
      </div>
    </div>
  );
}

export default Signup;
