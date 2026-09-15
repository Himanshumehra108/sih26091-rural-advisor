import React from "react";
import { useLanguage } from "../../context/LanguageContext";

export default function Footer() {
  const { t } = useLanguage();
  return (
    <footer className="site-footer">
      <span>🌾 {t("footer.brand")}</span>
      <span className="site-footer-note">
        {t("footer.note")}
      </span>
    </footer>
  );
}
