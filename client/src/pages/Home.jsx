import React from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/common/Navbar";

function Home() {
  return (
    <>
      <Navbar />

      <main className="home">
        <section className="hero">

          <div className="hero-content">

            <div className="hero-badge">
              🌱 Built for rural entrepreneurs
            </div>

            <h1>
              Start your business
              <span> with confidence.</span>
            </h1>

            <p>
              Find out which business could work in your area
              and understand how much funding you may be able
              to access.
            </p>

            <div className="hero-buttons">

              <Link
                to="/feasibility"
                className="primary-button"
              >
                📍 Check my business
              </Link>

              <Link
                to="/calculator"
                className="secondary-button"
              >
                💰 Calculate my loan
              </Link>

            </div>

          </div>

          <div className="hero-visual">

            <div className="floating-card card-one">
              <span>👥</span>
              <div>
                <strong>Market</strong>
                <small>Potential customers</small>
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
                <strong>Funding</strong>
                <small>Loan & EMI estimate</small>
              </div>
            </div>

          </div>

        </section>

        <section className="features">

          <div className="section-heading">
            <span>HOW IT WORKS</span>
            <h2>Two questions. One simple tool.</h2>
          </div>

          <div className="feature-grid">

            <div className="feature-card">
              <div className="feature-number">01</div>
              <div className="feature-icon">📍</div>

              <h3>Can my business work here?</h3>

              <p>
                Get a simple feasibility report based on
                your location, business and available capital.
              </p>

              <Link to="/feasibility">
                Check business →
              </Link>
            </div>

            <div className="feature-card">
              <div className="feature-number">02</div>
              <div className="feature-icon">💰</div>

              <h3>How much can I borrow?</h3>

              <p>
                Enter your own contribution and understand
                your possible project size, loan and repayment.
              </p>

              <Link to="/calculator">
                Calculate loan →
              </Link>
            </div>

          </div>

        </section>
      </main>
    </>
  );
}

export default Home;