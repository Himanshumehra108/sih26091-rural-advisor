import React, { createContext, useContext, useState } from "react";

// Mirrors server/app/core/constants.py SUPPORTED_LANGUAGES so the
// dropdown never offers a language the backend can't (eventually)
// translate into via Bhashini.
export const SUPPORTED_LANGUAGES = {
  en: "English",
  hi: "हिंदी",
  mr: "मराठी",
  bn: "বাংলা",
  ta: "தமிழ்",
  te: "తెలుగు",
};

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState("en");
  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
