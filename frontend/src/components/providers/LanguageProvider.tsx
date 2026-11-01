"use client";

import { createContext, useContext, useMemo } from "react";
import { useTranslation } from "react-i18next";
import i18n from "@/i18n";

export type Language = "en" | "hi";
type TranslationKey = keyof typeof import("@/locales/en/translation.json");

const LanguageContext = createContext<{
  language: Language;
  setLanguage: (language: Language) => void;
  t: (key: TranslationKey) => string;
} | null>(null);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation();
  const language: Language = i18n.language === "hi" ? "hi" : "en";

  const setLanguage = (next: Language) => {
    window.localStorage.setItem("ke-language", next);
    void i18n.changeLanguage(next);
  };

  const value = useMemo(
    () => ({ language, setLanguage, t: (key: TranslationKey) => t(key) }),
    [language, t],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error("useLanguage must be used within LanguageProvider");
  return context;
}
