import { createContext, useContext, useMemo, useState } from "react";

const TOKEN_KEY = "vball_token";
const USERNAME_KEY = "vball_username";
const USER_ID_KEY = "vball_user_id";

export type AuthState = {
  token: string | null;
  username: string | null;
  userId: string | null;
  login: (token: string, username: string, userId: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [username, setUsername] = useState<string | null>(() =>
    localStorage.getItem(USERNAME_KEY)
  );
  const [userId, setUserId] = useState<string | null>(() => localStorage.getItem(USER_ID_KEY));

  const login = (newToken: string, newUsername: string, newUserId: string) => {
    localStorage.setItem(TOKEN_KEY, newToken);
    localStorage.setItem(USERNAME_KEY, newUsername);
    localStorage.setItem(USER_ID_KEY, newUserId);
    setToken(newToken);
    setUsername(newUsername);
    setUserId(newUserId);
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USERNAME_KEY);
    localStorage.removeItem(USER_ID_KEY);
    setToken(null);
    setUsername(null);
    setUserId(null);
  };

  const value = useMemo(
    () => ({ token, username, userId, login, logout }),
    [token, username, userId]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
