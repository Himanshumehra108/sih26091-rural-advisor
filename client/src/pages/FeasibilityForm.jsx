import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import VoiceInputButton from "../components/common/VoiceInputButton";
import { getFeasibilityReport } from "../services/api";
import { useLanguage } from "../context/LanguageContext";
import { isRequired, isPositiveNumber } from "../utils/validators";

// Mirrors server/app/core/constants.py BUSINESS_CATEGORIES — keep this
// list in sync with the backend if it ever changes. There's no
// "list categories" endpoint yet, so this is hardcoded on purpose.
const BUSINESS_CATEGORIES = [
  ["Dairy", "🐄"],
  ["Retail", "🏪"],
  ["Textiles", "🧵"],
  ["Food Processing", "🥫"],
  ["Handicrafts", "🧶"],
  ["Poultry", "🐔"],
  ["Agriculture Inputs", "🌱"],
  ["Tailoring", "🪡"],
  ["Transport", "🚚"],
  ["Other", "✨"],
];

function FeasibilityForm() {
  const navigate = useNavigate();
  const { language } = useLanguage();

  const [businessCategory, setBusinessCategory] = useState("");
  const [otherCategory, setOtherCategory] = useState("");

  // Backend's LocationInput requires all four fields.
  const [village, setVillage] = useState("");
  const [block, setBlock] = useState("");
  const [district, setDistrict] = useState("");
  const [state, setState] = useState("");

  const [capital, setCapital] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const resolvedCategory =
    businessCategory === "Other" ? otherCategory : businessCategory;

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!isRequired(resolvedCategory)) {
      setError("Please choose or describe your business type.");
      return;
    }
    if (!isRequired(district) || !isRequired(state)) {
      setError("District and state are required so we can size your local market.");
      return;
    }
    if (!isPositiveNumber(capital)) {
      setError("Please enter a valid available capital amount.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const result = await getFeasibilityReport({
        businessCategory: resolvedCategory,
        location: { village, block, district, state },
        availableMargin: capital,
        language,
      });

      sessionStorage.setItem(
        "feasibilityReport",
        JSON.stringify({
          ...result,
          _meta: { businessCategory: resolvedCategory, location: { village, block, district, state } },
        })
      );

      navigate("/report");
    } catch (err) {
      setError(err.message || "Could not generate the report. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />

      <main className="page">
        <div className="page-header">
          <div className="page-badge">📍 BUSINESS FEASIBILITY</div>
          <h1>Will your business work here?</h1>
          <p>Tell us a few simple things and we'll help you understand your local opportunity.</p>
        </div>

        <form className="feasibility-form" onSubmit={handleSubmit}>
          <div className="form-section">
            <div className="step">01</div>
            <div className="form-content">
              <h2>What business do you want to start?</h2>
              <p>Choose the type of business you're planning.</p>

              <div className="business-options">
                {BUSINESS_CATEGORIES.map(([name, icon]) => (
                  <button
                    type="button"
                    key={name}
                    className={businessCategory === name ? "business-option selected" : "business-option"}
                    onClick={() => setBusinessCategory(name)}
                  >
                    <span>{icon}</span>
                    {name}
                  </button>
                ))}
              </div>

              {businessCategory === "Other" && (
                <input
                  className="text-input"
                  value={otherCategory}
                  onChange={(e) => setOtherCategory(e.target.value)}
                  placeholder="Describe your business idea..."
                />
              )}
            </div>
          </div>

          <div className="form-section">
            <div className="step">02</div>
            <div className="form-content">
              <h2>Where do you want to start?</h2>
              <p>Village and block are optional, but district and state help us size your market accurately.</p>

              <div className="location-grid">
                <div className="location-field">
                  <input
                    className="text-input"
                    value={village}
                    onChange={(e) => setVillage(e.target.value)}
                    placeholder="Village (optional)"
                  />
                  <VoiceInputButton onTranscript={setVillage} />
                </div>
                <div className="location-field">
                  <input
                    className="text-input"
                    value={block}
                    onChange={(e) => setBlock(e.target.value)}
                    placeholder="Block / Tehsil (optional)"
                  />
                </div>
                <div className="location-field">
                  <input
                    className="text-input"
                    value={district}
                    onChange={(e) => setDistrict(e.target.value)}
                    placeholder="District *"
                  />
                </div>
                <div className="location-field">
                  <input
                    className="text-input"
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    placeholder="State *"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="step">03</div>
            <div className="form-content">
              <h2>How much can you invest?</h2>
              <p>Enter your available capital (your own margin contribution).</p>

              <div className="money-input">
                <span>₹</span>
                <input
                  type="number"
                  value={capital}
                  onChange={(e) => setCapital(e.target.value)}
                  placeholder="1,00,000"
                />
              </div>
            </div>
          </div>

          {error && <div className="error-message">⚠️ {error}</div>}

          <button className="generate-button" type="submit" disabled={loading}>
            {loading ? "Generating report…" : "Generate my feasibility report →"}
          </button>
        </form>
      </main>
    </>
  );
}

export default FeasibilityForm;
