import { createContext, useState, useEffect, useCallback } from "react";
import { fetchAPI } from "@/lib/api";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAPI("/auth/me")
      .then((data) => setUser(data.user))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const loginTeacher = useCallback(async (email, password) => {
    const data = await fetchAPI("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setUser(data.user);
    return data.user;
  }, []);

  const loginStudent = useCallback(async (matricule) => {
    const data = await fetchAPI("/auth/scan", {
      method: "POST",
      body: JSON.stringify({ matricule }),
    });
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await fetchAPI("/auth/logout", { method: "POST" });
    } catch {}
    setUser(null);
  }, []);

  const value = {
    user,
    loading,
    loginTeacher,
    loginStudent,
    logout,
    isAuthenticated: !!user,
    isTeacher: user?.role === "teacher",
    isAdmin: !!user?.is_admin,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
