import { createContext, useContext, useEffect, useState } from "react";
import { getMe, login as apiLogin, register as apiRegister } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      setLoading(false);
      return;
    }
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setLoading(false));
  }, []);

  const saveAuth = (res) => {
    localStorage.setItem("token", res.data.token);
    setUser(res.data.user);
  };

  const login = async (email, password) => saveAuth(await apiLogin({ email, password }));
  const register = async (name, email, password) =>
    saveAuth(await apiRegister({ name, email, password }));

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);