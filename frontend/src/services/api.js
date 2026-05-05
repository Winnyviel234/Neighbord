import axios from 'axios';
import { demoDashboard, demoData, demoLanding, isEmptyPayload } from './demoData';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api'
});

const apiOrigin = new URL(api.defaults.baseURL, window.location.origin).origin;

export function mediaUrl(url) {
  if (!url) return '';
  if (/^https?:\/\//i.test(url)) return url;
  return `${apiOrigin}${url.startsWith('/') ? url : `/${url}`}`;
}

export function liveSocketUrl() {
  const baseURL = import.meta.env.VITE_API_URL || '/api';
  
  let wsUrl;
  if (/^https?:\/\//i.test(baseURL)) {
    // URL absoluta (ej: http://localhost:8000)
    const url = new URL(baseURL);
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    url.pathname = `${url.pathname.replace(/\/$/, '')}/ws/live`;
    wsUrl = url.toString();
  } else {
    // URL relativa (ej: /api)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    wsUrl = `${protocol}//${host}${baseURL.replace(/\/$/, '')}/ws/live`;
  }
  
  return wsUrl;
}

const isDashboardEmpty = (payload) => {
  if (!payload || typeof payload !== 'object') return true;
  const counters = ['vecinos', 'solicitudes', 'reuniones', 'votaciones', 'pagos'];
  const lists = ['ultimos_anuncios', 'reportes_recientes', 'eventos_proximos', 'votaciones_activas', 'cuotas_activas', 'pagos_recientes'];
  return counters.every((key) => !Number(payload[key])) && lists.every((key) => !payload[key]?.length);
};
const deletedDemoKey = 'neighbor_deleted_ids';
const isDemoId = (id) => String(id || '').startsWith('demo-');
const deletedDemoIds = () => {
  try {
    return JSON.parse(sessionStorage.getItem(deletedDemoKey) || '[]');
  } catch {
    return [];
  }
};
const rememberDeletedDemo = (id) => {
  const ids = new Set(deletedDemoIds());
  ids.add(id);
  sessionStorage.setItem(deletedDemoKey, JSON.stringify([...ids]));
};
const filterDeletedDemo = (payload) => {
  const deleted = new Set(deletedDemoIds());
  if (!deleted.size) return payload;
  if (Array.isArray(payload)) return payload.filter((item) => !deleted.has(item?.id));
  if (!payload || typeof payload !== 'object') return payload;
  return Object.fromEntries(Object.entries(payload).map(([key, value]) => [key, filterDeletedDemo(value)]));
};
const mergeWithDemo = (fallback, payload) => {
  if (!Array.isArray(payload) || !Array.isArray(fallback)) return filterDeletedDemo(payload);
  // Mezclar arrays: demo primero, luego datos reales
  const merged = [...filterDeletedDemo(fallback), ...filterDeletedDemo(payload)];
  // Eliminar duplicados por ID
  const seen = new Set();
  return merged.filter((item) => {
    if (seen.has(item?.id)) return false;
    seen.add(item?.id);
    return true;
  });
};
const demoFor = (fallback, payload, shouldUseDemo = isEmptyPayload) => (shouldUseDemo(payload) ? filterDeletedDemo(fallback) : filterDeletedDemo(payload));
const getWithDemo = (request, fallback, shouldUseDemo) => request.then((r) => demoFor(fallback, r.data, shouldUseDemo)).catch(() => filterDeletedDemo(fallback));
const getAndMergeDemo = (request, fallback) => request.then((r) => mergeWithDemo(fallback, r.data)).catch(() => filterDeletedDemo(fallback));
const deleteWithDemo = (id, request) => {
  if (isDemoId(id)) {
    rememberDeletedDemo(id);
    return Promise.resolve({ id });
  }
  return request()
    .then((r) => r.data || { id })
    .catch((error) => {
      rememberDeletedDemo(id);
      return { id, local_only: true, error: error.response?.data?.detail || 'Eliminado localmente' };
    });
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('neighbor_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

function buildFormData(data, fileField = 'imagen') {
  const formData = new FormData();
  Object.entries(data).forEach(([key, value]) => {
    if (value instanceof File) {
      formData.append(fileField, value);
    } else if (value !== undefined && value !== null && value !== '') {
      formData.append(key, String(value));
    }
  });
  return formData;
}

export const authService = {
  login: (data) => api.post('/v2/auth/login', data).then((r) => r.data),
  register: (data) => api.post('/v2/auth/register', data).then((r) => r.data),
  me: () => api.get('/v2/auth/me').then((r) => r.data),
  updateMe: (data) => api.patch('/v2/auth/me', data).then((r) => r.data),
  changePassword: (data) => api.post('/v2/auth/change-password', data).then((r) => r.data),
  getSectors: () => api.get('/v2/sectors').then((r) => r.data)
};

export const dataService = {
  dashboard: () => getWithDemo(api.get('/dashboard'), demoDashboard, isDashboardEmpty),
  landing: () => api.get('/public/landing').then((r) => r.data).catch(() => demoLanding),
  vecinos: () => getWithDemo(api.get('/vecinos'), demoData.vecinos),
  actualizarVecino: (id, data) => api.patch(`/vecinos/${id}`, data).then((r) => r.data),
  eliminarVecino: (id) => deleteWithDemo(id, () => api.delete(`/vecinos/${id}`)),
  aprobarVecino: (id) => api.patch(`/vecinos/${id}/aprobar`).then((r) => r.data),
  cambiarRolVecino: (id, rol) => api.patch(`/vecinos/${id}/rol/${rol}`).then((r) => r.data),
  morosos: () => getWithDemo(api.get('/vecinos/morosos'), demoData.vecinos.filter((item) => item.estado === 'moroso')),
  reuniones: (tipo) => getAndMergeDemo(api.get('/reuniones', { params: tipo ? { tipo } : {} }), tipo ? demoData.reuniones.filter((item) => item.tipo === tipo) : demoData.reuniones),
  crearReunion: (data) => {
    const formData = buildFormData(data, 'imagen');
    return api.post('/reuniones/form', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  actualizarReunion: (id, data) => {
    const formData = buildFormData(data, 'imagen');
    return api.patch(`/reuniones/${id}/form`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  eliminarReunion: (id) => deleteWithDemo(id, () => api.delete(`/reuniones/${id}`)),
  votaciones: () => getAndMergeDemo(api.get('/votaciones'), demoData.votaciones),
  crearVotacion: (data) => {
    const formData = buildFormData(data, 'imagen');
    return api.post('/votaciones/form', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  actualizarVotacion: (id, data) => {
    const formData = buildFormData(data, 'imagen');
    return api.patch(`/votaciones/${id}/form`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  eliminarVotacion: (id) => deleteWithDemo(id, () => api.delete(`/votaciones/${id}`)),
  votar: (id, opcion) => {
    if (isDemoId(id)) {
      return Promise.reject({ response: { data: { detail: 'No se puede votar en datos de demostración.' } } });
    }
    return api.post(`/votaciones/${id}/votar`, { opcion }).then((r) => r.data);
  },
  finalizarEleccion: (id) => api.post(`/votaciones/${id}/finalizar-eleccion`).then((r) => r.data),
  pagos: () => api.get('/cuotas/pagos').then((r) => r.data),
  crearPago: (data) => api.post('/finanzas/pagos', data).then((r) => r.data),
  crearPagoSolicitud: (data) => api.post('/finanzas/pagos/solicitud', data).then((r) => r.data),
  actualizarPago: (id, data) => api.patch(`/finanzas/pagos/${id}`, data).then((r) => r.data),
  eliminarPago: (id) => deleteWithDemo(id, () => api.delete(`/finanzas/pagos/${id}`)),
  transacciones: () => getWithDemo(api.get('/finanzas/transacciones'), demoData.transacciones),
  crearTransaccion: (data) => api.post('/finanzas/transacciones', data).then((r) => r.data),
  actualizarTransaccion: (id, data) => api.patch(`/finanzas/transacciones/${id}`, data).then((r) => r.data),
  eliminarTransaccion: (id) => deleteWithDemo(id, () => api.delete(`/finanzas/transacciones/${id}`)),
  cuotas: () => api.get('/cuotas').then((r) => r.data),
  misPagos: () => api.get('/cuotas/mis-pagos').then((r) => r.data),
  crearCuota: (data) => api.post('/cuotas', data).then((r) => r.data),
  actualizarCuota: (id, data) => api.patch(`/cuotas/${id}`, data).then((r) => r.data),
  eliminarCuota: (id) => deleteWithDemo(id, () => api.delete(`/cuotas/${id}`)),
  pagarMiCuota: (id, data) => {
    const formData = buildFormData(data, 'comprobante');
    return api.post(`/cuotas/${id}/pagar/form`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  cambiarEstadoPago: (id, estado) => api.patch(`/cuotas/pagos/${id}/estado/${estado}`).then((r) => r.data),
  solicitudes: () => getWithDemo(api.get('/solicitudes'), demoData.solicitudes),
  crearSolicitud: (data) => api.post('/solicitudes', data).then((r) => r.data),
  actualizarSolicitud: (id, data) => api.patch(`/solicitudes/${id}`, data).then((r) => r.data),
  eliminarSolicitud: (id) => deleteWithDemo(id, () => api.delete(`/solicitudes/${id}`)),
  comunicados: () => getAndMergeDemo(api.get('/comunicados'), demoData.comunicados),
  crearComunicado: (data) => api.post('/comunicados', data).then((r) => r.data),
  actualizarComunicado: (id, data) => api.patch(`/comunicados/${id}`, data).then((r) => r.data),
  eliminarComunicado: (id) => deleteWithDemo(id, () => api.delete(`/comunicados/${id}`)),
  publicComunicados: () => getWithDemo(api.get('/public/comunicados'), demoData.comunicados),
  noticias: () => getAndMergeDemo(api.get('/noticias'), demoData.noticias),
  noticiasAdmin: () => getWithDemo(api.get('/noticias/admin'), demoData.noticias),
  crearNoticia: (data) => {
    const formData = buildFormData(data, 'imagen');
    return api.post('/noticias/form', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  actualizarNoticia: (id, data) => {
    const formData = buildFormData(data, 'imagen');
    return api.patch(`/noticias/${id}/form`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  eliminarNoticia: (id) => deleteWithDemo(id, () => api.delete(`/noticias/${id}`)),
  directiva: () => getWithDemo(api.get('/directiva'), demoData.directiva),
  crearDirectivo: (data) => {
    const formData = buildFormData(data, 'imagen');
    return api.post('/directiva/form', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  actualizarDirectivo: (id, data) => {
    const formData = buildFormData(data, 'imagen');
    return api.patch(`/directiva/${id}/form`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  eliminarDirectivo: (id) => deleteWithDemo(id, () => api.delete(`/directiva/${id}`)),
  reunionesDirectiva: () => getWithDemo(api.get('/directiva/reuniones'), demoData.reuniones.filter((item) => item.tipo === 'directiva')),
  proyectos: () => getWithDemo(api.get('/proyectos'), [
    { id: 'demo-proyecto-1', titulo: 'Mejoramiento de iluminacion', estado: 'en progreso', presupuesto: 1350 },
    { id: 'demo-proyecto-2', titulo: 'Recuperacion de jardin central', estado: 'planificado', presupuesto: 980 }
  ]),
  mapaSector: () => Promise.resolve(filterDeletedDemo(demoData.mapaSector)),
  notificacionesTiempoReal: () => Promise.resolve(filterDeletedDemo(demoData.notificacionesTiempoReal)),
  chatVecinal: () => Promise.resolve(filterDeletedDemo(demoData.chatVecinal)),
  mensajesDirectiva: () => Promise.resolve(filterDeletedDemo(demoData.mensajesDirectiva)),
  auditoria: () => api.get('/auditoria').then((r) => r.data),
  enviarEmail: (data) => api.post('/emails/personalizado', data).then((r) => r.data),
  descargarReporte: (tipo, formato) => api.get(`/reportes/${tipo}.${formato}`, { responseType: 'blob' }).then((r) => r.data),
  documentos: () => getWithDemo(api.get('/documentos'), []),
  subirDocumento: (data) => {
    const formData = buildFormData(data, 'archivo');
    return api.post('/documentos/form', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  reporteUrl: (tipo, formato) => `${api.defaults.baseURL}/reportes/${tipo}.${formato}`,
  getStatistics: (endpoint) => api.get(`/v2/statistics/${endpoint}`).then((r) => r.data),
  getAnalytics: () => api.get('/v2/statistics/analytics').then((r) => r.data),
  getNotifications: (limit = 20) => api.get('/v2/notifications', { params: { limit } }).then((r) => r.data),
  getUnreadNotificationCount: () => api.get('/v2/notifications/unread/count').then((r) => r.data),
  markNotificationAsRead: (id) => api.patch(`/v2/notifications/${id}/read`).then((r) => r.data),
  markAllNotificationsAsRead: () => api.post('/v2/notifications/mark-multiple-read', { ids: [] }).then((r) => r.data),
  getNotificationPreferences: () => api.get('/v2/notifications/preferences').then((r) => r.data),
  updateNotificationPreferences: (preferences) => api.patch('/v2/notifications/preferences', preferences).then((r) => r.data)
};

export default api;
