import { useState, useEffect, useCallback } from 'react';

// Tipos para el cache
interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  storage?: 'localStorage' | 'sessionStorage' | 'memory';
}

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

// Cache en memoria para datos temporales
const memoryCache = new Map<string, CacheItem<any>>();

// Hook personalizado para cache
export function useCache<T>(
  key: string,
  options: CacheOptions = {}
) {
  const {
    ttl = 5 * 60 * 1000, // 5 minutos por defecto
    storage = 'localStorage'
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Obtener storage apropiado
  const getStorage = useCallback(() => {
    try {
      if (storage === 'sessionStorage') {
        return sessionStorage;
      }
      return localStorage;
    } catch {
      return null; // Fallback si storage no está disponible
    }
  }, [storage]);

  // Verificar si un item del cache es válido
  const isValidCacheItem = useCallback((item: CacheItem<T>): boolean => {
    const now = Date.now();
    return (now - item.timestamp) < item.ttl;
  }, []);

  // Obtener datos del cache
  const getCachedData = useCallback((): T | null => {
    try {
      if (storage === 'memory') {
        const item = memoryCache.get(key);
        if (item && isValidCacheItem(item)) {
          return item.data;
        }
        return null;
      }

      const storageInstance = getStorage();
      if (!storageInstance) return null;

      const cached = storageInstance.getItem(key);
      if (!cached) return null;

      const item: CacheItem<T> = JSON.parse(cached);
      if (!isValidCacheItem(item)) {
        storageInstance.removeItem(key);
        return null;
      }

      return item.data;
    } catch (err) {
      console.warn('Error reading from cache:', err);
      return null;
    }
  }, [key, storage, getStorage, isValidCacheItem]);

  // Guardar datos en cache
  const setCachedData = useCallback((newData: T) => {
    try {
      const item: CacheItem<T> = {
        data: newData,
        timestamp: Date.now(),
        ttl
      };

      if (storage === 'memory') {
        memoryCache.set(key, item);
        return;
      }

      const storageInstance = getStorage();
      if (!storageInstance) return;

      storageInstance.setItem(key, JSON.stringify(item));
    } catch (err) {
      console.warn('Error writing to cache:', err);
    }
  }, [key, storage, ttl, getStorage]);

  // Limpiar cache
  const clearCache = useCallback(() => {
    try {
      if (storage === 'memory') {
        memoryCache.delete(key);
        return;
      }

      const storageInstance = getStorage();
      if (!storageInstance) return;

      storageInstance.removeItem(key);
    } catch (err) {
      console.warn('Error clearing cache:', err);
    }
  }, [key, storage, getStorage]);

  // Cargar datos con cache
  const loadWithCache = useCallback(async (
    fetcher: () => Promise<T>,
    forceRefresh = false
  ): Promise<T> => {
    setLoading(true);
    setError(null);

    try {
      // Intentar obtener del cache primero
      if (!forceRefresh) {
        const cachedData = getCachedData();
        if (cachedData !== null) {
          setData(cachedData);
          setLoading(false);
          return cachedData;
        }
      }

      // Si no hay cache o se fuerza refresh, hacer fetch
      const freshData = await fetcher();
      setCachedData(freshData);
      setData(freshData);
      setLoading(false);
      return freshData;

    } catch (err) {
      setError(err as Error);
      setLoading(false);
      throw err;
    }
  }, [getCachedData, setCachedData]);

  // Efecto para cargar datos iniciales del cache
  useEffect(() => {
    const cachedData = getCachedData();
    if (cachedData !== null) {
      setData(cachedData);
    }
  }, [getCachedData]);

  return {
    data,
    loading,
    error,
    loadWithCache,
    clearCache,
    setData: setCachedData,
    getData: getCachedData
  };
}

// Hook para cache de API responses
export function useApiCache<T>(
  endpoint: string,
  options: CacheOptions = {}
) {
  const cacheKey = `api:${endpoint}`;

  return useCache<T>(cacheKey, {
    ttl: 10 * 60 * 1000, // 10 minutos para APIs
    storage: 'sessionStorage', // Usar sessionStorage para datos de API
    ...options
  });
}

// Hook para cache de configuración
export function useConfigCache<T>(
  configKey: string,
  options: CacheOptions = {}
) {
  const cacheKey = `config:${configKey}`;

  return useCache<T>(cacheKey, {
    ttl: 60 * 60 * 1000, // 1 hora para configuración
    storage: 'localStorage', // Persistir configuración
    ...options
  });
}

// Hook para cache de usuario
export function useUserCache<T>(
  userKey: string,
  options: CacheOptions = {}
) {
  const cacheKey = `user:${userKey}`;

  return useCache<T>(cacheKey, {
    ttl: 30 * 60 * 1000, // 30 minutos para datos de usuario
    storage: 'sessionStorage',
    ...options
  });
}

// Utilidades para limpiar cache
export const cacheUtils = {
  // Limpiar todo el cache de un tipo
  clearByPrefix: (prefix: string, storage: 'localStorage' | 'sessionStorage' = 'localStorage') => {
    try {
      const storageInstance = storage === 'sessionStorage' ? sessionStorage : localStorage;
      const keys = Object.keys(storageInstance);

      keys.forEach(key => {
        if (key.startsWith(prefix)) {
          storageInstance.removeItem(key);
        }
      });
    } catch (err) {
      console.warn('Error clearing cache by prefix:', err);
    }
  },

  // Limpiar cache de API
  clearApiCache: () => {
    cacheUtils.clearByPrefix('api:', 'sessionStorage');
  },

  // Limpiar cache de usuario
  clearUserCache: () => {
    cacheUtils.clearByPrefix('user:', 'sessionStorage');
  },

  // Limpiar cache de configuración
  clearConfigCache: () => {
    cacheUtils.clearByPrefix('config:', 'localStorage');
  },

  // Limpiar todo el cache
  clearAllCache: () => {
    try {
      localStorage.clear();
      sessionStorage.clear();
      memoryCache.clear();
    } catch (err) {
      console.warn('Error clearing all cache:', err);
    }
  }
};