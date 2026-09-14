import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import { useAuth } from "../context/AuthContext";
import { isRequired } from "../utils/validators";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

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
    try {
      setLoading(true);
      setError("");
      // NOTE: uses AuthContext's mock login for now — see
      // AuthContext.jsx for what needs to change once the backend
      // exposes a real /auth/login endpoint.
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Could not log in. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="page auth-page">
        <div className="auth-card">
          <div className="page-badge">👋 WELCOME BACK</div>
          <h1>Log in</h1>
          <p>Access your saved reports and calculations.</p>

          <form onSubmit={handleSubmit} className="auth-form">
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
                placeholder="••••••••"
              />
            </label>

            {error && <div className="error-message">⚠️ {error}</div>}

            <button className="generate-button" type="submit" disabled={loading}>
              {loading ? "Logging in…" : "Log in →"}
            </button>
          </form>

          <p className="auth-switch">
            New here? <Link to="/register">Create an account</Link>
          </p>
        </div>
      </main>
    </>
  );
}
