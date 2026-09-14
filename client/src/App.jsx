import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";

import { AuthProvider } from "./context/AuthContext";
import { LanguageProvider } from "./context/LanguageContext";
import useOfflineSync from "./hooks/useOfflineSync";

import Home from "./pages/Home";
import FinancialCalculator from "./pages/FinancialCalculator";
import FeasibilityForm from "./pages/FeasibilityForm";
import FeasibilityReport from "./pages/FeasibilityReport";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Footer from "./components/common/Footer";

function OfflineBanner() {
  const { isOnline } = useOfflineSync();
  if (isOnline) return null;
  return (
    <div className="offline-banner">
      ⚠️ You're offline — some data may be out of date until you reconnect.
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <BrowserRouter>
          <OfflineBanner />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/calculator" element={<FinancialCalculator />} />
            <Route path="/feasibility" element={<FeasibilityForm />} />
            <Route path="/report" element={<FeasibilityReport />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="*" element={<Home />} />
          </Routes>
          <Footer />
        </BrowserRouter>
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;
