import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { authService } from '../services/api';

const defaultAuthContext = {
  user: null,
  loading: false,
  login: async () => {
    throw new Error('AuthProvider not mounted: cannot call login()');
  },
  register: async () => {
    throw new Error('AuthProvider not mounted: cannot call register()');
  },
  updateProfile: async () => {
    throw new Error('AuthProvider not mounted: cannot call updateProfile()');
  },
  changePassword: async () => {
    throw new Error('AuthProvider not mounted: cannot call changePassword()');
  },
  logout: () => {},
  hasRole: () => false,
};

const AuthContext = createContext(defaultAuthContext);

function normalizeUser(user) {
  if (!user) return null;
  return {
    ...user,
    rol: user.rol || user.role_name || user.role || 'vecino'
  };
}

function isApprovedUser(user) {
  return user?.rol === 'admin' || ['aprobado', 'activo'].includes(user?.estado);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('neighbor_token');
        if (!token) {
          setLoading(false);
          return;
        }

        // Intentar obtener el usuario actual
        const userData = await authService.me();

        if (userData && isApprovedUser(userData)) {
          setUser(normalizeUser(userData));
          setError(null);
        } else {
          // Token inválido, limpiarlo
          localStorage.removeItem('neighbor_token');
          setUser(null);
        }
      } catch (err) {
        console.warn('Auth initialization failed:', err);
        // No mostrar error al usuario, solo limpiar estado
        localStorage.removeItem('neighbor_token');
        setUser(null);
        setError(null);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const value = useMemo(() => ({
    user,
    loading,
    error,
    login: async (credentials) => {
      try {
        setError(null);
        const response = await authService.login(credentials);
        if (!response.access_token || !isApprovedUser(response.user)) {
          localStorage.removeItem('neighbor_token');
          setUser(null);
          throw new Error('Tu cuenta aún no está activa');
        }
        localStorage.setItem('neighbor_token', response.access_token);
        setUser(normalizeUser(response.user));
        return response;
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Error de inicio de sesión');
        throw err;
      }
    },
    register: async (credentials) => {
      try {
        setError(null);
        const response = await authService.register(credentials);
        localStorage.removeItem('neighbor_token');
        setUser(null);
        return response;
      } catch (err) {
        setError(err.response?.data?.detail || 'Error de registro');
        throw err;
      }
    },
    updateProfile: async (data) => {
      try {
        setError(null);
        const updated = await authService.updateMe(data);
        setUser(normalizeUser(updated));
        return updated;
      } catch (err) {
        setError(err.response?.data?.detail || 'Error al actualizar perfil');
        throw err;
      }
    },
    changePassword: async (data) => {
      try {
        setError(null);
        return await authService.changePassword(data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Error al cambiar contraseña');
        throw err;
      }
    },
    logout: () => {
      localStorage.removeItem('neighbor_token');
      setUser(null);
      setError(null);
    },
    hasRole: (...roles) => !!user && roles.includes(user.rol),
    clearError: () => setError(null)
  }), [user, loading, error]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
