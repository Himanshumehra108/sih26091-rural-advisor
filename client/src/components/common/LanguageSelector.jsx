import React from "react";
import { SUPPORTED_LANGUAGES, useLanguage } from "../../context/LanguageContext";

export default function LanguageSelector({ value = "en", onChange }) {
  const { t } = useLanguage();
  return (
    <select
      className="language-select"
      value={value}
      onChange={(event) => onChange?.(event.target.value)}
      aria-label={t("language.select")}
    >
      {Object.entries(SUPPORTED_LANGUAGES).map(([code, label]) => (
        <option key={code} value={code}>
          {label}
        </option>
      ))}
    </select>
  );
}
