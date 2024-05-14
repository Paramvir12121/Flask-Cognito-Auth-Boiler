import React, { useState } from 'react';
import "./Login.css"
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // Import useNavigate instead of useHistory

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate(); // useNavigate for navigation

    const handleLogin = async (event) => {
        event.preventDefault();

        try {
            const response = await axios.post('http://localhost:5000/auth/login/', {
                email: email,
                password: password,
            }, {
                withCredentials: true  // Important for credentials, such as cookies
            });

            // Assuming the backend sends the token in a secure HttpOnly cookie,
            // we just check if the login was successful then redirect.
            console.log('Login successful');
            navigate('/home'); // Using useNavigate to redirect
        } catch (error) {
            console.error('Login failed:', error.response || error);
            setError('Failed to log in. Please check your credentials.');
        }
    };

    return (
        <div className="container-fluid">
            <div className="row">
                <div className="col-md-6 order-md-1 d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
                    <div className="p-4 m-4 w-100">
                        <h2>Login</h2>
                        <form onSubmit={handleLogin} className="col-md-8 mt-4">
                            <div className="mb-3">
                                <label htmlFor="email" className="form-label">Email</label>
                                <input
                                    className="form-control"
                                    type="email"
                                    value={email}
                                    onChange={e => setEmail(e.target.value)}
                                    placeholder="Enter email"
                                    required
                                />
                            </div>
                            <div className="mb-3">
                                <label htmlFor="password" className="form-label">Password</label>
                                <input
                                    className="form-control"
                                    type="password"
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                    placeholder="Enter password"
                                    required
                                />
                            </div>
                            {error && <div className="alert alert-danger">{error}</div>}
                            <button type="submit" className="btn btn-primary">Login</button>
                        </form>
                    </div>
                </div>
                <div className="col-md-6 d-none d-lg-block order-md-2" id='svg'>
                    {/* Background SVG Image should be here */}
                </div>
            </div>
        </div>
    );
};

export default Login;
