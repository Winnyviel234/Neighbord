import { Bell, Check, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { dataService } from '../services/api';

export default function NotificationCenterPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const [error, setError] = useState('');

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const data = await dataService.getNotifications?.();
      if (data) {
        setNotifications(data);
        setUnreadCount(data.filter(n => !n.leida).length);
      }
    } catch (err) {
      setError('Error al cargar notificaciones');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await dataService.markNotificationAsRead?.(notificationId);
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId ? { ...n, leida: true } : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await dataService.markAllNotificationsAsRead?.();
      setNotifications(prev => prev.map(n => ({ ...n, leida: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Error marking all as read:', err);
    }
  };

  const getNotificationColor = (tipo) => {
    const colors = {
      votacion: 'bg-purple-50 border-purple-200',
      reunion: 'bg-blue-50 border-blue-200',
      pago: 'bg-green-50 border-green-200',
      solicitud: 'bg-orange-50 border-orange-200',
      comunicado: 'bg-yellow-50 border-yellow-200',
      directiva: 'bg-indigo-50 border-indigo-200'
    };
    return colors[tipo] || 'bg-slate-50 border-slate-200';
  };

  const getNotificationIcon = (tipo) => {
    const icons = {
      votacion: '🗳️',
      reunion: '📅',
      pago: '💰',
      solicitud: '📝',
      comunicado: '📢',
      directiva: '👔'
    };
    return icons[tipo] || '📬';
  };

  if (loading) {
    return (
      <section>
        <h1 className="page-title">Centro de Notificaciones</h1>
        <div className="mt-6 flex items-center justify-center">
          <p className="text-slate-500">Cargando notificaciones...</p>
        </div>
      </section>
    );
  }

  return (
    <section>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="page-title">Centro de Notificaciones</h1>
          <p className="mt-1 text-sm font-semibold text-slate-500">
            Tienes {unreadCount} notificaciones sin leer
          </p>
        </div>
        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllAsRead}
            className="btn-secondary text-sm"
          >
            <Check className="h-4 w-4" /> Marcar todo como leído
          </button>
        )}
      </div>

      {error && (
        <div className="mt-6 rounded-lg bg-red-50 p-4 border border-red-200">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="mt-6 space-y-3">
        {notifications.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center">
            <Bell className="mx-auto h-12 w-12 text-slate-300" />
            <p className="mt-4 font-semibold text-neighbor-navy">Sin notificaciones</p>
            <p className="mt-1 text-sm text-slate-500">Cuando tengas nuevas notificaciones aparecerán aquí</p>
          </div>
        ) : (
          notifications.map((notification) => (
            <div
              key={notification.id}
              className={`rounded-lg border-l-4 p-4 flex items-start justify-between gap-4 ${getNotificationColor(
                notification.tipo
              )} ${notification.leida ? 'opacity-75' : ''}`}
            >
              <div className="flex items-start gap-4 flex-1 min-w-0">
                <span className="text-2xl flex-shrink-0">{getNotificationIcon(notification.tipo)}</span>
                <div className="min-w-0 flex-1">
                  <h3 className="font-semibold text-neighbor-navy">{notification.titulo}</h3>
                  <div
                    className="mt-2 text-sm text-slate-600 prose prose-sm max-w-none"
                    dangerouslySetInnerHTML={{ __html: notification.contenido }}
                  />
                  <p className="mt-2 text-xs text-slate-500">
                    {new Date(notification.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
              {!notification.leida && (
                <button
                  onClick={() => handleMarkAsRead(notification.id)}
                  className="btn-secondary px-3 py-2 flex-shrink-0"
                  title="Marcar como leído"
                >
                  <Check className="h-4 w-4" />
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </section>
  );
}
