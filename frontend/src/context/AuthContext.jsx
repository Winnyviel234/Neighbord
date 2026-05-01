import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('neighbor_token');
    if (!token) {
      setLoading(false);
      return;
    }
    authService.me().then(setUser).catch(() => localStorage.removeItem('neighbor_token')).finally(() => setLoading(false));
  }, []);

  const value = useMemo(() => ({
    user,
    loading,
    login: async (credentials) => {
      const response = await authService.login(credentials);
      localStorage.setItem('neighbor_token', response.access_token);
      setUser(response.user);
      return response;
    },
    register: authService.register,
    updateProfile: async (data) => {
      const updated = await authService.updateMe(data);
      setUser(updated);
      return updated;
    },
    changePassword: authService.changePassword,
    logout: () => {
      localStorage.removeItem('neighbor_token');
      setUser(null);
    },
    hasRole: (...roles) => !!user && roles.includes(user.rol)
  }), [user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
