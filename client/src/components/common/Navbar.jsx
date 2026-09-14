import React from "react";
import { Link, NavLink } from "react-router-dom";
import LanguageSelector from "./LanguageSelector";
import { useLanguage } from "../../context/LanguageContext";
import { useAuth } from "../../context/AuthContext";

function Navbar() {
  const { language, setLanguage } = useLanguage();
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        <div className="brand-icon">🌾</div>
        <div>
          <div className="brand-name">Rural Advisor</div>
          <div className="brand-subtitle">Business made simple</div>
        </div>
      </Link>

      <div className="nav-links">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
          Home
        </NavLink>
        <NavLink to="/calculator" className={({ isActive }) => (isActive ? "active" : "")}>
          Loan Calculator
        </NavLink>
        <NavLink to="/feasibility" className={({ isActive }) => (isActive ? "active" : "")}>
          Business Check
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "active" : "")}>
          Saved Reports
        </NavLink>

        <LanguageSelector value={language} onChange={setLanguage} />

        {isAuthenticated ? (
          <button className="language-btn" onClick={logout}>
            👋 {user?.name}
          </button>
        ) : (
          <Link to="/login" className="language-btn">
            Log in
          </Link>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
