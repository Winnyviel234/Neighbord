import { Bell, CalendarDays, Check, FileText, Megaphone, Newspaper, Vote, WalletCards } from 'lucide-react';
import { useEffect, useState } from 'react';
import { dataService } from '../services/api';

const typeStyles = {
  votacion: 'bg-violet-50 border-violet-200',
  reunion: 'bg-sky-50 border-sky-200',
  pago: 'bg-emerald-50 border-emerald-200',
  solicitud: 'bg-amber-50 border-amber-200',
  comunicado: 'bg-yellow-50 border-yellow-200',
  noticia: 'bg-cyan-50 border-cyan-200',
  documento: 'bg-slate-50 border-slate-200',
  directiva: 'bg-indigo-50 border-indigo-200'
};

const typeIcons = {
  votacion: Vote,
  reunion: CalendarDays,
  pago: WalletCards,
  solicitud: FileText,
  comunicado: Megaphone,
  noticia: Newspaper,
  documento: FileText,
  directiva: Bell
};

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
      const items = Array.isArray(data) ? data : [];
      setNotifications(items);
      setUnreadCount(items.filter((item) => !item.leida).length);
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
      setNotifications((prev) => prev.map((item) => item.id === notificationId ? { ...item, leida: true } : item));
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await dataService.markAllNotificationsAsRead?.();
      setNotifications((prev) => prev.map((item) => ({ ...item, leida: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Error marking all as read:', err);
    }
  };

  if (loading) {
    return (
      <section>
        <h1 className="page-title">Centro de Notificaciones</h1>
        <div className="mt-6 card p-8 text-center text-slate-500">Cargando notificaciones...</div>
      </section>
    );
  }

  return (
    <section>
      <div className="flex flex-wrap items-end justify-between gap-3 rounded-lg border border-white/80 bg-white/80 p-5 shadow-soft backdrop-blur">
        <div>
          <h1 className="page-title">Centro de Notificaciones</h1>
          <p className="mt-1 text-sm font-semibold text-slate-500">
            Tienes {unreadCount} notificaciones sin leer
          </p>
        </div>
        {unreadCount > 0 && (
          <button onClick={handleMarkAllAsRead} className="btn-secondary text-sm">
            <Check className="h-4 w-4" /> Marcar todo como leido
          </button>
        )}
      </div>

      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="mt-6 grid gap-3">
        {notifications.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-300 bg-white/80 p-8 text-center">
            <Bell className="mx-auto h-12 w-12 text-slate-300" />
            <p className="mt-4 font-semibold text-neighbor-navy">Sin notificaciones</p>
            <p className="mt-1 text-sm text-slate-500">Cuando tengas nuevas notificaciones apareceran aqui</p>
          </div>
        ) : (
          notifications.map((notification) => {
            const Icon = typeIcons[notification.tipo] || Bell;
            return (
              <article
                key={notification.id}
                className={`flex items-start justify-between gap-4 rounded-lg border p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg ${typeStyles[notification.tipo] || 'bg-white border-slate-200'} ${notification.leida ? 'opacity-75' : ''}`}
              >
                <div className="flex min-w-0 flex-1 items-start gap-4">
                  <span className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-lg bg-white text-neighbor-blue shadow-sm">
                    <Icon className="h-5 w-5" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-bold text-neighbor-navy">{notification.titulo}</h3>
                    <div
                      className="mt-2 text-sm leading-6 text-slate-600"
                      dangerouslySetInnerHTML={{ __html: notification.contenido || notification.mensaje || '' }}
                    />
                    <p className="mt-2 text-xs font-semibold text-slate-500">
                      {new Date(notification.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                {!notification.leida && (
                  <button
                    onClick={() => handleMarkAsRead(notification.id)}
                    className="btn-secondary px-3 py-2"
                    title="Marcar como leido"
                  >
                    <Check className="h-4 w-4" />
                  </button>
                )}
              </article>
            );
          })
        )}
      </div>
    </section>
  );
}
