import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import { useAuth } from "../context/AuthContext";
import { isRequired } from "../utils/validators";
import { useLanguage } from "../context/LanguageContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { t } = useLanguage();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isRequired(email) || !isRequired(password)) {
      setError(t("login.required"));
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
      setError(err.message || t("login.failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="page auth-page">
        <div className="auth-card">
          <div className="page-badge">👋 {t("login.badge")}</div>
          <h1>{t("login.title")}</h1>
          <p>{t("login.subtitle")}</p>

          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              {t("login.email")}
              <input
                type="email"
                className="text-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t("login.emailPlaceholder")}
              />
            </label>

            <label>
              {t("login.password")}
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
              {loading ? t("login.submitting") : t("login.submit")}
            </button>
          </form>

          <p className="auth-switch">
            {t("login.newHere")} <Link to="/register">{t("login.createAccount")}</Link>
          </p>
        </div>
      </main>
    </>
  );
}
