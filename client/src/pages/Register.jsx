import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import { useAuth } from "../context/AuthContext";
import { isRequired } from "../utils/validators";
import { useLanguage } from "../context/LanguageContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const { t } = useLanguage();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isRequired(email) || !isRequired(password)) {
      setError(t("register.required"));
      return;
    }
    if (password.length < 6) {
      setError(t("register.passwordLength"));
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
      setError(err.message || t("register.failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="page auth-page">
        <div className="auth-card">
          <div className="page-badge">🌱 {t("register.badge")}</div>
          <h1>{t("register.title")}</h1>
          <p>{t("register.subtitle")}</p>

          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              {t("register.name")}
              <input
                className="text-input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={t("register.namePlaceholder")}
              />
            </label>

            <label>
              {t("register.email")}
              <input
                type="email"
                className="text-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </label>

            <label>
              {t("register.password")}
              <input
                type="password"
                className="text-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t("register.passwordPlaceholder")}
              />
            </label>

            {error && <div className="error-message">⚠️ {error}</div>}

            <button className="generate-button" type="submit" disabled={loading}>
              {loading ? t("register.submitting") : t("register.submit")}
            </button>
          </form>

          <p className="auth-switch">
            {t("register.haveAccount")} <Link to="/login">{t("register.logIn")}</Link>
          </p>
        </div>
      </main>
    </>
  );
}
