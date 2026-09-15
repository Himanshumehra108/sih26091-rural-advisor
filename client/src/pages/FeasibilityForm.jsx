import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import VoiceInputButton from "../components/common/VoiceInputButton";
import LocationAutocomplete from "../components/common/LocationAutocomplete";
import {
  BLOCKS_BY_DISTRICT,
  DISTRICTS_BY_STATE,
  INDIA_STATES,
  findOfficialDistrict,
  findOfficialState,
} from "../data/indiaLocations";
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
  const { language, voiceLocale, t } = useLanguage();

  const [businessCategory, setBusinessCategory] = useState("");
  const [otherCategory, setOtherCategory] = useState("");

  // Backend's LocationInput requires all four fields.
  const [village, setVillage] = useState("");
  const [block, setBlock] = useState("");
  const [district, setDistrict] = useState("");
  const [state, setState] = useState("");
  const [pincode, setPincode] = useState("");
  const [pincodeError, setPincodeError] = useState("");
  const [pincodeLoading, setPincodeLoading] = useState(false);
  const [postOffices, setPostOffices] = useState([]);
  const pincodeCache = useRef(new Map());
  const pincodeRequest = useRef(0);

  const [capital, setCapital] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const resolvedCategory =
    businessCategory === "Other" ? otherCategory : businessCategory;

  const selectedState = findOfficialState(state);
  const selectedDistrict = findOfficialDistrict(selectedState, district);
  const districtSuggestions = DISTRICTS_BY_STATE[selectedState] || [];
  const blockSuggestions = BLOCKS_BY_DISTRICT[selectedDistrict] || [];

  const handleStateChange = (value) => {
    setState(value);
    if (value !== state) {
      setDistrict("");
      setBlock("");
    }
  };

  const handleStateSelect = (value) => {
    setState(value);
    setDistrict("");
    setBlock("");
  };

  const handleDistrictChange = (value) => {
    setDistrict(value);
    if (value !== district) setBlock("");
  };

  const handlePincodeOffice = (event) => {
    const office = postOffices.find((item) => item.Name === event.target.value);
    if (!office) return;
    setVillage(office.Name || "");
    setBlock(office.Block || office.Taluk || "");
  };

  useEffect(() => {
    const digits = pincode.replace(/\D/g, "").slice(0, 6);
    if (digits !== pincode) setPincode(digits);
    if (digits.length !== 6) {
      setPincodeError("");
      setPostOffices([]);
      setPincodeLoading(false);
      return undefined;
    }

    const cached = pincodeCache.current.get(digits);
    if (cached) {
      setState(cached.state);
      setDistrict(cached.district);
      setBlock(cached.block);
      setVillage(cached.village);
      setPostOffices(cached.postOffices);
      setPincodeError("");
      return undefined;
    }

    const requestId = ++pincodeRequest.current;
    const controller = new AbortController();
    setPincodeLoading(true);
    setPincodeError("");

    fetch(`https://api.postalpincode.in/pincode/${digits}`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("pincode request failed");
        return response.json();
      })
      .then((payload) => {
        if (requestId !== pincodeRequest.current) return;
        const offices = payload?.[0]?.Status === "Success" ? payload[0].PostOffice || [] : [];
        if (offices.length === 0) throw new Error("pincode not found");
        const first = offices[0];
        const result = {
          state: first.State || "",
          district: first.District || "",
          block: first.Block || first.Taluk || "",
          village: offices.length === 1 ? first.Name || "" : "",
          postOffices: offices,
        };
        pincodeCache.current.set(digits, result);
        setState(result.state);
        setDistrict(result.district);
        setBlock(result.block);
        setVillage(result.village);
        setPostOffices(offices);
        setPincodeError("");
      })
      .catch((fetchError) => {
        if (fetchError.name === "AbortError" || requestId !== pincodeRequest.current) return;
        setPostOffices([]);
        setPincodeError(t("feasibility.pincodeNotFound"));
      })
      .finally(() => {
        if (requestId === pincodeRequest.current) setPincodeLoading(false);
      });

    return () => controller.abort();
  }, [pincode, t]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!isRequired(resolvedCategory)) {
      setError(t("feasibility.chooseBusiness"));
      return;
    }
    if (!isRequired(district) || !isRequired(state)) {
      setError(t("feasibility.districtStateRequired"));
      return;
    }
    if (pincode && pincode.length !== 6) {
      setError(t("feasibility.invalidPincode"));
      return;
    }
    if (!isPositiveNumber(capital)) {
      setError(t("feasibility.invalidCapital"));
      return;
    }

    try {
      setLoading(true);
      setError("");

      const result = await getFeasibilityReport({
        businessCategory: resolvedCategory,
        location: { village, block, district, state, pincode },
        availableMargin: capital,
        language,
      });

      sessionStorage.setItem(
        "feasibilityReport",
        JSON.stringify({
          ...result,
          _meta: { businessCategory: resolvedCategory, location: { village, block, district, state, pincode } },
        })
      );

      navigate("/report");
    } catch (err) {
      setError(err.message || t("feasibility.generateFailed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />

      <main className="page">
        <div className="page-header">
          <div className="page-badge">📍 {t("feasibility.badge")}</div>
          <h1>{t("feasibility.title")}</h1>
          <p>{t("feasibility.subtitle")}</p>
        </div>

        <form className="feasibility-form" onSubmit={handleSubmit}>
          <div className="form-section">
            <div className="step">01</div>
            <div className="form-content">
              <h2>{t("feasibility.step1Title")}</h2>
              <p>{t("feasibility.step1Body")}</p>

              <div className="business-options">
                {BUSINESS_CATEGORIES.map(([name, icon]) => (
                  <button
                    type="button"
                    key={name}
                    className={businessCategory === name ? "business-option selected" : "business-option"}
                    onClick={() => setBusinessCategory(name)}
                  >
                    <span>{icon}</span>
                    {t(`business.${name}`)}
                  </button>
                ))}
              </div>

              {businessCategory === "Other" && (
                <input
                  className="text-input"
                  value={otherCategory}
                  onChange={(e) => setOtherCategory(e.target.value)}
                  placeholder={t("feasibility.otherPlaceholder")}
                />
              )}
            </div>
          </div>

          <div className="form-section">
            <div className="step">02</div>
            <div className="form-content">
              <h2>{t("feasibility.step2Title")}</h2>
              <p>{t("feasibility.step2Body")}</p>

              <div className="location-grid">
                <div className="location-field">
                  <LocationAutocomplete
                    id="village"
                    value={village}
                    onChange={setVillage}
                    placeholder={t("feasibility.village")}
                    suggestions={postOffices.map((office) => office.Name).filter(Boolean)}
                    noResultsText={t("feasibility.noLocationsFound")}
                  />
                  <VoiceInputButton onTranscript={setVillage} language={voiceLocale} />
                </div>
                <div className="location-field">
                  <LocationAutocomplete
                    id="block"
                    value={block}
                    onChange={setBlock}
                    placeholder={t("feasibility.block")}
                    suggestions={blockSuggestions}
                    noResultsText={t("feasibility.noLocationsFound")}
                  />
                </div>
                <div className="location-field">
                  <LocationAutocomplete
                    id="district"
                    value={district}
                    onChange={handleDistrictChange}
                    onSelect={setDistrict}
                    placeholder={t("feasibility.district")}
                    suggestions={districtSuggestions}
                    disabled={!selectedState}
                    noResultsText={t("feasibility.noDistrictsFound")}
                  />
                </div>
                <div className="location-field">
                  <LocationAutocomplete
                    id="state"
                    value={state}
                    onChange={handleStateChange}
                    onSelect={handleStateSelect}
                    placeholder={t("feasibility.state")}
                    suggestions={INDIA_STATES}
                    noResultsText={t("feasibility.noStatesFound")}
                  />
                </div>
                <div className="location-field pincode-field">
                  <input
                    id="pincode"
                    className="text-input"
                    value={pincode}
                    onChange={(event) => setPincode(event.target.value)}
                    placeholder={t("feasibility.pincode")}
                    inputMode="numeric"
                    maxLength={6}
                    aria-describedby="pincode-status"
                  />
                  <span id="pincode-status" className="location-status" role="status">
                    {pincodeLoading ? t("feasibility.pincodeLoading") : pincodeError}
                  </span>
                </div>
                {postOffices.length > 1 && (
                  <div className="location-field">
                    <select className="text-input" defaultValue="" onChange={handlePincodeOffice} aria-label={t("feasibility.postOffice")}>
                      <option value="">{t("feasibility.postOffice")}</option>
                      {postOffices.map((office) => <option key={office.Name} value={office.Name}>{office.Name}</option>)}
                    </select>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="step">03</div>
            <div className="form-content">
              <h2>{t("feasibility.step3Title")}</h2>
              <p>{t("feasibility.step3Body")}</p>

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
            {loading ? t("feasibility.generating") : t("feasibility.generate")}
          </button>
        </form>
      </main>
    </>
  );
}

export default FeasibilityForm;
