import React from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import { useLanguage } from "../context/LanguageContext";

function Home() {
  const { t } = useLanguage();
  return (
    <>
      <Navbar />

      <main className="home">
        <section className="hero">

          <div className="hero-content">

            <div className="hero-badge">
              🌱 {t("home.badge")}
            </div>

            <h1>
              {t("home.title")}
              <span> {t("home.titleAccent")}</span>
            </h1>

            <p>
              {t("home.subtitle")}
            </p>

            <div className="hero-buttons">

              <Link
                to="/feasibility"
                className="primary-button"
              >
                📍 {t("home.checkBusiness")}
              </Link>

              <Link
                to="/calculator"
                className="secondary-button"
              >
                💰 {t("home.calculateLoan")}
              </Link>

            </div>

          </div>

          <div className="hero-visual">

            <div className="floating-card card-one">
              <span>👥</span>
              <div>
                    <strong>{t("home.market")}</strong>
                    <small>{t("home.potentialCustomers")}</small>
              </div>
            </div>

            <div className="main-illustration">
              <div className="sun">☀️</div>

              <div className="illustration-house">
                🏠
              </div>

              <div className="illustration-field">
                🌾🌾🌾🌾
              </div>

              <div className="illustration-person">
                🧑‍🌾
              </div>
            </div>

            <div className="floating-card card-two">
              <span>💰</span>
              <div>
                    <strong>{t("home.funding")}</strong>
                    <small>{t("home.loanEmi")}</small>
              </div>
            </div>

          </div>

        </section>

        <section className="features">

          <div className="section-heading">
            <span>{t("home.howItWorks")}</span>
            <h2>{t("home.twoQuestions")}</h2>
          </div>

          <div className="feature-grid">

            <div className="feature-card">
              <div className="feature-number">01</div>
              <div className="feature-icon">📍</div>

              <h3>{t("home.canBusinessWork")}</h3>

              <p>
                {t("home.feasibilityBlurb")}
              </p>

              <Link to="/feasibility">
                {t("home.checkBusinessLink")}
              </Link>
            </div>

            <div className="feature-card">
              <div className="feature-number">02</div>
              <div className="feature-icon">💰</div>

              <h3>{t("home.howMuchBorrow")}</h3>

              <p>
                {t("home.loanBlurb")}
              </p>

              <Link to="/calculator">
                {t("home.calculateLoanLink")}
              </Link>
            </div>

          </div>

        </section>
      </main>
    </>
  );
}

export default Home;