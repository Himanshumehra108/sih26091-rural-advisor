import React from "react";
import { Link, NavLink } from "react-router-dom";
import LanguageSelector from "./LanguageSelector";
import { useLanguage } from "../../context/LanguageContext";
import { useAuth } from "../../context/AuthContext";

function Navbar() {
  const { language, setLanguage, t } = useLanguage();
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        <div className="brand-icon">🌾</div>
        <div>
          <div className="brand-name">{t("brand.name")}</div>
          <div className="brand-subtitle">{t("brand.subtitle")}</div>
        </div>
      </Link>

      <div className="nav-links">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
          {t("nav.home")}
        </NavLink>
        <NavLink to="/calculator" className={({ isActive }) => (isActive ? "active" : "")}>
          {t("nav.loanCalculator")}
        </NavLink>
        <NavLink to="/feasibility" className={({ isActive }) => (isActive ? "active" : "")}>
          {t("nav.businessCheck")}
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "active" : "")}>
          {t("nav.savedReports")}
        </NavLink>

        <LanguageSelector value={language} onChange={setLanguage} />

        {isAuthenticated ? (
          <button className="language-btn" onClick={logout}>
            👋 {user?.name}
          </button>
        ) : (
          <Link to="/login" className="language-btn">
            {t("nav.logIn")}
          </Link>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
