import { AlertCircle, BarChart2, Bell, CalendarDays, CheckCircle2, FileText, Megaphone, TrendingUp, Users, Vote, WalletCards, MessageSquare } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Badge, EmptyState, Spinner, StatCard } from '../components/common';
import { dataService } from '../services/api';
import { dateTime, money, shortDate } from '../lib/utils';
import { useAuth } from '../context/AuthContext';

export default function AdminDashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    dataService.getStatistics('dashboard')
      .then(setData)
      .catch(err => setError(err.message || 'Error al cargar estadísticas'));
  }, []);

  if (error) return (
    <section>
      <div className="card p-8 text-center">
        <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
        <h2 className="mt-4 text-lg font-bold text-slate-700">Error al cargar</h2>
        <p className="mt-2 text-sm text-slate-500">{error}</p>
        <button className="btn-primary mt-4" onClick={() => { setError(null); setData(null); dataService.getStatistics('dashboard').then(setData).catch(e => setError(e.message)); }}>
          Reintentar
        </button>
      </div>
    </section>
  );

  if (!data) return <Spinner />;

  const { users, payments, votings, meetings, complaints, chat } = data;

  return (
    <section>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="page-title">Dashboard Administrativo</h1>
          <p className="mt-1 text-sm font-semibold text-slate-500">Estadísticas generales del sistema</p>
        </div>
        <Badge variant="success">Admin</Badge>
      </div>

      {/* Users Statistics */}
      <div className="mt-8">
        <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
          <Users className="h-5 w-5" />
          Estadísticas de Usuarios
        </h2>
        <div className="grid gap-4 md:grid-cols-4">
          <StatCard icon={Users} label="Total Usuarios" value={users.total_users} tone="blue" />
          <StatCard icon={TrendingUp} label="Activos (30d)" value={users.active_users_30d} tone="green" />
          <StatCard icon={CheckCircle2} label="Administradores" value={users.users_by_role?.admin || 0} tone="purple" />
          <StatCard icon={Users} label="Vecinos" value={users.users_by_role?.vecino || 0} tone="blue" />
        </div>
      </div>

      {/* Payments Statistics */}
      <div className="mt-8">
        <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
          <WalletCards className="h-5 w-5" />
          Estadísticas de Pagos
        </h2>
        <div className="grid gap-4 md:grid-cols-4">
          <StatCard icon={WalletCards} label="Total Pagos" value={payments.total_payments} tone="green" />
          <StatCard icon={TrendingUp} label="Monto Total" value={`$${payments.total_amount?.toFixed(2)}`} tone="green" />
          <StatCard icon={CheckCircle2} label="Pagos Completados" value={payments.payments_by_status?.completado || 0} tone="green" />
          <StatCard icon={TrendingUp} label="Pagos Recientes (30d)" value={payments.recent_payments_30d} tone="blue" />
        </div>
      </div>

      {/* Voting Statistics */}
      <div className="mt-8">
        <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
          <Vote className="h-5 w-5" />
          Estadísticas de Votaciones
        </h2>
        <div className="grid gap-4 md:grid-cols-4">
          <StatCard icon={Vote} label="Total Votaciones" value={votings.total_votings} tone="purple" />
          <StatCard icon={CheckCircle2} label="Votaciones Activas" value={votings.active_votings} tone="green" />
          <StatCard icon={BarChart2} label="Total Votos" value={votings.total_votes} tone="blue" />
          <StatCard icon={TrendingUp} label="Votaciones Recientes (30d)" value={votings.recent_votings_30d} tone="orange" />
        </div>
      </div>

      {/* Meetings Statistics */}
      <div className="mt-8">
        <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
          <CalendarDays className="h-5 w-5" />
          Estadísticas de Reuniones
        </h2>
        <div className="grid gap-4 md:grid-cols-4">
          <StatCard icon={CalendarDays} label="Total Reuniones" value={meetings.total_meetings} tone="blue" />
          <StatCard icon={TrendingUp} label="Próximas Reuniones" value={meetings.upcoming_meetings} tone="green" />
          <StatCard icon={CheckCircle2} label="Reuniones Pasadas" value={meetings.past_meetings} tone="gray" />
          <StatCard icon={Users} label="Asistencia Promedio" value={meetings.average_attendance?.toFixed(1)} tone="purple" />
        </div>
      </div>

      {/* Complaints Statistics */}
      <div className="mt-8">
        <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Estadísticas de Solicitudes
        </h2>
        <div className="grid gap-4 md:grid-cols-4">
          <StatCard icon={FileText} label="Total Solicitudes" value={complaints.total_complaints} tone="orange" />
          <StatCard icon={CheckCircle2} label="Resueltas" value={complaints.complaints_by_status?.resuelta || 0} tone="green" />
          <StatCard icon={AlertCircle} label="Pendientes" value={complaints.complaints_by_status?.pendiente || 0} tone="red" />
          <StatCard icon={TrendingUp} label="Solicitudes Recientes (30d)" value={complaints.recent_complaints_30d} tone="blue" />
        </div>
      </div>

      {/* Chat Statistics */}
      <div className="mt-8">
        <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Estadísticas de Chat
        </h2>
        <div className="grid gap-4 md:grid-cols-3">
          <StatCard icon={MessageSquare} label="Salas de Chat" value={chat.total_chat_rooms} tone="blue" />
          <StatCard icon={BarChart2} label="Total Mensajes" value={chat.total_messages} tone="green" />
          <StatCard icon={TrendingUp} label="Mensajes Recientes (7d)" value={chat.recent_messages_7d} tone="orange" />
        </div>
      </div>

      {/* Detailed Tables */}
      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        {/* Users by Role */}
        <div className="card">
          <h3 className="text-lg font-bold text-slate-700 mb-4">Usuarios por Rol</h3>
          <div className="space-y-2">
            {Object.entries(users.users_by_role || {}).map(([role, count]) => (
              <div key={role} className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="capitalize">{role}</span>
                <Badge>{count}</Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Payments by Status */}
        <div className="card">
          <h3 className="text-lg font-bold text-slate-700 mb-4">Pagos por Estado</h3>
          <div className="space-y-2">
            {Object.entries(payments.payments_by_status || {}).map(([status, count]) => (
              <div key={status} className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="capitalize">{status}</span>
                <Badge variant={status === 'completado' ? 'success' : status === 'pendiente' ? 'warning' : 'default'}>{count}</Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Complaints by Category */}
        <div className="card">
          <h3 className="text-lg font-bold text-slate-700 mb-4">Solicitudes por Categoría</h3>
          <div className="space-y-2">
            {Object.entries(complaints.complaints_by_category || {}).map(([category, count]) => (
              <div key={category} className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="capitalize">{category}</span>
                <Badge>{count}</Badge>
              </div>
            ))}
          </div>
        </div>

        {/* System Health */}
        <div className="card">
          <h3 className="text-lg font-bold text-slate-700 mb-4">Estado del Sistema</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>Última actualización</span>
              <span className="text-sm text-slate-500">{new Date(data.generated_at).toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Estado general</span>
              <Badge variant="success">Operativo</Badge>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}