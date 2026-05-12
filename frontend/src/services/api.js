import axios from 'axios';
import { demoDashboard, demoData, demoLanding, isEmptyPayload } from './demoData';

const isDev = import.meta.env.MODE !== 'production';
const apiBaseUrl = isDev ? '/api' : import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: apiBaseUrl
});

const safeOrigin = /^https?:\/\//i.test(window.location.origin)
  ? window.location.origin
  : 'http://localhost:5173';

const apiOrigin = new URL(api.defaults.baseURL, safeOrigin).origin;

export function mediaUrl(url) {
  if (!url) return '';
  if (/^https?:\/\//i.test(url)) return url;
  return `${apiOrigin}${url.startsWith('/') ? url : `/${url}`}`;
}

export function liveSocketUrl() {
  const baseURL = import.meta.env.VITE_API_URL || '/api';
  
  let wsUrl;
  if (/^https?:\/\//i.test(baseURL)) {
    const url = new URL(baseURL);
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    url.pathname = `${url.pathname.replace(/\/$/, '')}/ws/live`;
    wsUrl = url.toString();
  } else {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = /^[^:]+:\/\//.test(window.location.origin)
      ? window.location.host
      : 'localhost:5174';
    wsUrl = `${protocol}//${host}${baseURL.replace(/\/$/, '')}/ws/live`;
  }
  
  return wsUrl;
}

export function directivaSocketUrl() {
  const baseURL = import.meta.env.VITE_API_URL || '/api';
  const token = localStorage.getItem('neighbor_token');
  
  let wsUrl;
  if (/^https?:\/\//i.test(baseURL)) {
    const url = new URL(baseURL);
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    url.pathname = `${url.pathname.replace(/\/$/, '')}/ws/directiva`;
    if (token) url.searchParams.set('token', token);
    wsUrl = url.toString();
  } else {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = /^[^:]+:\/\//.test(window.location.origin)
      ? window.location.host
      : 'localhost:5174';
    wsUrl = `${protocol}//${host}${baseURL.replace(/\/$/, '')}/ws/directiva${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  }
  
  return wsUrl;
}

const isDashboardEmpty = (payload) => isEmptyPayload(payload);
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
const sanitizeString = (value) => (typeof value === 'string' ? value.trim().replace(/<[^>]*>/g, '') : value);
const sanitizePayload = (value) => {
  if (value instanceof FormData) return value;
  if (Array.isArray(value)) return value.map(sanitizePayload);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, nestedValue]) => [key, sanitizePayload(nestedValue)]));
  }
  return sanitizeString(value);
};
const mergeWithDemo = (fallback, payload) => {
  if (!Array.isArray(payload) || !Array.isArray(fallback)) return filterDeletedDemo(payload);
  // Mezclar arrays: datos reales primero, luego ejemplos demo.
  const merged = [...filterDeletedDemo(payload), ...filterDeletedDemo(fallback)];
  const seen = new Set();
  const unique = merged.filter((item) => {
    if (item?.id && seen.has(item.id)) return false;
    if (item?.id) seen.add(item.id);
    return true;
  });
  return unique;
};
const demoFor = (fallback, payload, shouldUseDemo = isEmptyPayload) => {
  return shouldUseDemo(payload) ? filterDeletedDemo(fallback) : filterDeletedDemo(payload);
};
const getWithDemo = (request, fallback, shouldUseDemo = isEmptyPayload) => request.then((r) => {
  const payload = r.data;
  if (Array.isArray(payload) && Array.isArray(fallback)) return mergeWithDemo(fallback, payload);
  return demoFor(fallback, payload, shouldUseDemo);
}).catch(() => filterDeletedDemo(fallback));
const getAndMergeDemo = (request, fallback) => request.then((r) => mergeWithDemo(fallback, r.data)).catch(() => filterDeletedDemo(fallback));
const getRealList = (request) => request.then((r) => filterDeletedDemo(r.data || []));
const mergeLandingData = (payload) => ({
  comunicados: mergeWithDemo(demoLanding.comunicados, payload?.comunicados || []),
  noticias: mergeWithDemo(demoLanding.noticias, payload?.noticias || []),
  votaciones: filterDeletedDemo((payload?.votaciones || []).filter((item) => !isDemoId(item?.id))),
  pagos: filterDeletedDemo(payload?.pagos || []),
  reuniones: filterDeletedDemo(payload?.reuniones || []),
  directiva: Array.isArray(payload?.directiva) ? filterDeletedDemo(payload.directiva) : filterDeletedDemo(demoLanding.directiva)
});
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
  if (config.data && !(config.data instanceof FormData)) {
    config.data = sanitizePayload(config.data);
  }
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
  requestPasswordReset: (data) => api.post('/v2/auth/password-reset/request', data).then((r) => r.data),
  confirmPasswordReset: (data) => api.post('/v2/auth/password-reset/confirm', data).then((r) => r.data),
  getSectors: () => api.get('/v2/sectors').then((r) => r.data)
};

export const notificationService = {
  getPreferences: () => api.get('/v2/notifications/preferences').then((r) => r.data).catch(() => ({})),
  updatePreferences: (data) => api.patch('/v2/notifications/preferences', data).then((r) => r.data),
  getAll: () => api.get('/v2/notifications').then((r) => r.data),
  markAsRead: (id) => api.patch(`/v2/notifications/${id}/read`).then((r) => r.data),
  delete: (id) => api.delete(`/v2/notifications/${id}`).then((r) => r.data)
};

export const dataService = {
  getNotificationPreferences: () => notificationService.getPreferences(),
  updateNotificationPreferences: (data) => notificationService.updatePreferences(data),
  dashboard: () => getWithDemo(api.get('/dashboard'), demoDashboard, isDashboardEmpty),
  landing: () => api.get('/public/landing').then((r) => mergeLandingData(r.data)).catch(() => ({
    ...demoLanding,
    votaciones: []
  })),
  vecinos: () => getWithDemo(api.get('/vecinos'), []),
  actualizarVecino: (id, data) => api.patch(`/vecinos/${id}`, data).then((r) => r.data),
  eliminarVecino: (id) => deleteWithDemo(id, () => api.delete(`/vecinos/${id}`)),
  aprobarVecino: (id) => api.patch(`/vecinos/${id}/aprobar`).then((r) => r.data),
  cambiarRolVecino: (id, rol) => api.patch(`/vecinos/${id}/rol/${rol}`).then((r) => r.data),
  morosos: () => getWithDemo(api.get('/vecinos/morosos'), []),
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
  votaciones: () => getRealList(api.get('/votaciones')),
  crearVotacion: (data) => {
    const formData = buildFormData(data, 'imagen');
    return api.post('/votaciones/form', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  actualizarVotacion: (id, data) => {
    const formData = buildFormData(data, 'imagen');
    return api.patch(`/votaciones/${id}/form`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  eliminarVotacion: (id) => deleteWithDemo(id, () => api.delete(`/votaciones/${id}`)),
  votar: (id, opcion) => api.post(`/votaciones/${id}/votar`, { opcion }).then((r) => r.data),
  cancelarVoto: (id) => api.delete(`/votaciones/${id}/votar`).then((r) => r.data),
  finalizarEleccion: (id) => api.post(`/votaciones/${id}/finalizar-eleccion`).then((r) => r.data),
  pagos: () => api.get('/cuotas/pagos').then((r) => r.data),
  crearPago: (data) => api.post('/finanzas/pagos', data).then((r) => r.data),
  checkoutProjectContribution: (data) => api.post('/payments/strike', data).then((r) => r.data),
  crearPagoSolicitud: (data) => api.post('/finanzas/pagos/solicitud', data).then((r) => r.data),
  actualizarPago: (id, data) => api.patch(`/finanzas/pagos/${id}`, data).then((r) => r.data),
  eliminarPago: (id) => deleteWithDemo(id, () => api.delete(`/finanzas/pagos/${id}`)),
  transacciones: () => getRealList(api.get('/finanzas/transacciones')),
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
   getNoticiaComments: (id) => api.get(`/noticias/${id}/comments`).then((r) => r.data || []),
   createNoticiaComment: (id, contenido) => {
     const formData = new FormData();
     formData.append('contenido', contenido);
     return api.post(`/noticias/${id}/comments`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
   },
   deleteNoticiaComment: (id) => api.delete(`/noticias/comments/${id}`).then((r) => r.data),
   getComunicadoComments: (id) => api.get(`/comunicados/${id}/comments`).then((r) => r.data || []),
   createComunicadoComment: (id, contenido) => {
     const formData = new FormData();
     formData.append('contenido', contenido);
     return api.post(`/comunicados/${id}/comments`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
   },
   deleteComunicadoComment: (id) => api.delete(`/comunicados/comments/${id}`).then((r) => r.data),
  directiva: () => getRealList(api.get('/directiva')),
  crearDirectivo: (data) => {
    const formData = buildFormData(data, 'imagen');
    return api.post('/directiva/form', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  actualizarDirectivo: (id, data) => {
    const formData = buildFormData(data, 'imagen');
    return api.patch(`/directiva/${id}/form`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
  },
  eliminarDirectivo: (id) => deleteWithDemo(id, () => api.delete(`/directiva/${id}`)),
  reunionesDirectiva: () => getRealList(api.get('/directiva/reuniones')),
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
  eliminarDocumento: (id) => api.delete(`/documentos/${id}`).then((r) => r.data),
  reporteUrl: (tipo, formato) => `${api.defaults.baseURL}/reportes/${tipo}.${formato}`,
  getStatistics: (endpoint) => api.get(`/v2/statistics/${endpoint}`).then((r) => r.data),
  getAnalytics: () => api.get('/v2/statistics/analytics').then((r) => r.data),
  getNotifications: (limit = 20) => api.get('/v2/notifications', { params: { limit } }).then((r) => r.data),
  getUnreadNotificationCount: () => api.get('/v2/notifications/unread/count').then((r) => r.data),
  markNotificationAsRead: (id) => api.patch(`/v2/notifications/${id}/read`).then((r) => r.data),
  markAllNotificationsAsRead: () => api.post('/v2/notifications/mark-multiple-read', { ids: [] }).then((r) => r.data),
   getNotificationPreferences: () => api.get('/v2/notifications/preferences').then((r) => r.data),
   updateNotificationPreferences: (preferences) => api.patch('/v2/notifications/preferences', preferences).then((r) => r.data),
   checkDirectivaAccess: () => api.get('/live/directiva/check').then((r) => r.data).catch(() => ({ access: false })),
   getDirectivaChatHistory: () => api.get('/live/directiva/chat/history').then((r) => r.data).catch(() => ({ messages: [] })),
   getProyectos: () => api.get('/proyectos').then((r) => r.data).catch(() => []),
   getProyecto: (id) => api.get(`/proyectos/${id}`).then((r) => r.data),
   crearProyecto: (data) => {
     const formData = new FormData();
     formData.append('title', data.title);
     formData.append('description', data.description);
     formData.append('presupuesto_estimado', String(data.presupuesto_estimado));
     formData.append('fecha_inicio', data.fecha_inicio);
     formData.append('fecha_fin_estimada', data.fecha_fin_estimada);
     formData.append('status', data.status || 'planeado');
     formData.append('prioridad', data.prioridad || 'media');
     return api.post('/proyectos', formData, {
       headers: { 'Content-Type': 'multipart/form-data' }
     }).then((r) => r.data);
   },
   actualizarProyecto: (id, data) => api.patch(`/v2/projects/${id}`, data).then((r) => r.data),
   eliminarProyecto: (id) => api.delete(`/v2/projects/${id}`),
   getContribucionesProyecto: (id) => api.get(`/v2/projects/${id}/contributions`).then((r) => r.data),
   aportarProyecto: (projectId, monto, concepto) => {
     const formData = new FormData();
     formData.append('monto', String(monto));
     if (concepto) formData.append('concepto', concepto);
     return api.post(`/v2/projects/${projectId}/contribute`, formData, {
       headers: { 'Content-Type': 'multipart/form-data' }
     }).then((r) => r.data);
   },
   checkContribucionStatus: (projectId, contributionId) =>
     api.get(`/v2/projects/${projectId}/contributions/${contributionId}/status`).then((r) => r.data),
};

export default api;
