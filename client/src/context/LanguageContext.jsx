import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import en from "../locales/en.json";
import hi from "../locales/hi.json";
import pa from "../locales/pa.json";
import ta from "../locales/ta.json";
import te from "../locales/te.json";
import mr from "../locales/mr.json";
import bn from "../locales/bn.json";
import gu from "../locales/gu.json";
import kn from "../locales/kn.json";
import ml from "../locales/ml.json";
import or from "../locales/or.json";

// Mirrors server/app/core/constants.py SUPPORTED_LANGUAGES so the
// dropdown never offers a language the backend can't (eventually)
// translate into via Bhashini.
export const SUPPORTED_LANGUAGES = {
  en: "English",
  hi: "हिंदी",
  pa: "ਪੰਜਾਬੀ",
  ta: "தமிழ்",
  te: "తెలుగు",
  mr: "मराठी",
  bn: "বাংলা",
  gu: "ગુજરાતી",
  kn: "ಕನ್ನಡ",
  ml: "മലയാളം",
  or: "ଓଡ଼ିଆ",
};

const LOCALES = { en, hi, pa, ta, te, mr, bn, gu, kn, ml, or };
export const VOICE_LOCALES = {
  en: "en-IN", hi: "hi-IN", pa: "pa-IN", ta: "ta-IN", te: "te-IN",
  mr: "mr-IN", bn: "bn-IN", gu: "gu-IN", kn: "kn-IN", ml: "ml-IN", or: "od-IN",
};

function getValue(source, path) {
  return path.split(".").reduce((value, key) => value?.[key], source);
}

function translate(locale, key, values) {
  const value = getValue(LOCALES[locale], key) ?? getValue(en, key) ?? key;
  if (typeof value !== "string") return value;
  return value.replace(/{{(\w+)}}/g, (_, name) => String(values?.[name] ?? `{{${name}}}`));
}

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    const saved = window.localStorage.getItem("language");
    return saved && LOCALES[saved] ? saved : "en";
  });

  useEffect(() => {
    window.localStorage.setItem("language", language);
    document.documentElement.lang = language;
  }, [language]);

  const value = useMemo(() => ({
    language,
    setLanguage,
    voiceLocale: VOICE_LOCALES[language],
    t: (key, values) => translate(language, key, values),
  }), [language]);

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
