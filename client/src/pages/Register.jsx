import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import { useAuth } from "../context/AuthContext";
import { isRequired } from "../utils/validators";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isRequired(email) || !isRequired(password)) {
      setError("Please enter both email and password.");
      return;
    }
    if (password.length < 6) {
      setError("Password should be at least 6 characters.");
      return;
    }
    try {
      setLoading(true);
      setError("");
      // NOTE: uses AuthContext's mock register for now — see
      // AuthContext.jsx for what needs to change once the backend
      // exposes a real /auth/register endpoint with actual password
      // hashing (server/app/core/security.py currently stores plaintext).
      await register(email, password, name);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Could not create your account. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="page auth-page">
        <div className="auth-card">
          <div className="page-badge">🌱 GET STARTED</div>
          <h1>Create an account</h1>
          <p>Save your feasibility reports and come back to them anytime.</p>

          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              Name
              <input
                className="text-input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
              />
            </label>

            <label>
              Email
              <input
                type="email"
                className="text-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </label>

            <label>
              Password
              <input
                type="password"
                className="text-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 6 characters"
              />
            </label>

            {error && <div className="error-message">⚠️ {error}</div>}

            <button className="generate-button" type="submit" disabled={loading}>
              {loading ? "Creating account…" : "Create account →"}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account? <Link to="/login">Log in</Link>
          </p>
        </div>
      </main>
    </>
  );
}
