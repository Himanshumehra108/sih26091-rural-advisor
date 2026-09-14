import React, { createContext, useContext, useState } from "react";

// -----------------------------------------------------------------------
// NOTE FOR BACKEND INTEGRATION:
// server/app/api/v1/routes_auth.py currently only exposes GET /auth/status.
// There is no real /auth/login or /auth/register endpoint, and
// server/app/core/security.py's password hashing + token creation are
// placeholders (not real hashing, not a signed JWT).
//
// Until those are real, this context stores a mock "session" in memory
// so the rest of the app (Navbar, Dashboard, protected pages) can be
// built and tested against a real auth *shape* without waiting on the
// backend. Swap `mockLogin` / `mockRegister` below for real calls to
// `api.js` once the backend endpoints exist — the shape (user object,
// token string) is designed to match what a real JWT login response
// would look like.
// -----------------------------------------------------------------------

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  const login = async (email, _password) => {
    // TODO: replace with `await api.post('/api/v1/auth/login', { email, password })`
    // once the backend implements real authentication.
    const mockUser = { email, name: email.split("@")[0] };
    setUser(mockUser);
    setToken("mock-token");
    return mockUser;
  };

  const register = async (email, _password, name) => {
    // TODO: replace with `await api.post('/api/v1/auth/register', ...)`
    // once the backend implements real authentication.
    const mockUser = { email, name: name || email.split("@")[0] };
    setUser(mockUser);
    setToken("mock-token");
    return mockUser;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, token, isAuthenticated: Boolean(user), login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
