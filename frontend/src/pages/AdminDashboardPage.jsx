import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  AlertCircle,
  ArrowRight,
  BarChart3,
  CalendarClock,
  CheckCircle2,
  ClipboardList,
  Clock3,
  Download,
  FileText,
  Gauge,
  Landmark,
  MessageSquare,
  RefreshCw,
  ShieldCheck,
  TrendingUp,
  UserCheck,
  UserPlus,
  Users,
  Vote,
  WalletCards,
} from 'lucide-react';
import { Badge, Spinner } from '../components/common';
import { dataService } from '../services/api';
import { useAuth } from '../context/AuthContext';

const moneyFormatter = new Intl.NumberFormat('es-BO', {
  style: 'currency',
  currency: 'BOB',
  maximumFractionDigits: 2,
});

const numberFormatter = new Intl.NumberFormat('es-BO');

const statusTone = {
  aprobado: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  activo: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  pendiente: 'bg-amber-50 text-amber-700 border-amber-200',
  moroso: 'bg-orange-50 text-orange-700 border-orange-200',
  rechazado: 'bg-red-50 text-red-700 border-red-200',
  inactivo: 'bg-slate-100 text-slate-600 border-slate-200',
  completado: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  verificado: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  resuelta: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  resuelto: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  abierta: 'bg-sky-50 text-sky-700 border-sky-200',
  'en revision': 'bg-blue-50 text-blue-700 border-blue-200',
  'en proceso': 'bg-blue-50 text-blue-700 border-blue-200',
};

const prettyLabel = (value) => String(value || 'sin dato').replace(/_/g, ' ');
const formatNumber = (value) => numberFormatter.format(Number(value || 0));
const formatMoney = (value) => moneyFormatter.format(Number(value || 0));
const sumValues = (obj = {}) => Object.values(obj).reduce((total, value) => total + Number(value || 0), 0);
const countFrom = (obj = {}, keys = []) => keys.reduce((total, key) => total + Number(obj[key] || 0), 0);
const pct = (value, total) => (total > 0 ? Math.round((Number(value || 0) / total) * 100) : 0);

function StatusBadge({ children }) {
  const key = String(children || '').toLowerCase();
  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-bold capitalize ${statusTone[key] || 'border-slate-200 bg-slate-50 text-slate-600'}`}>
      {prettyLabel(children)}
    </span>
  );
}

function MetricTile({ icon: Icon, label, value, detail, tone = 'blue', trend }) {
  const tones = {
    blue: 'bg-blue-50 text-blue-700 border-blue-100',
    green: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    amber: 'bg-amber-50 text-amber-700 border-amber-100',
    red: 'bg-red-50 text-red-700 border-red-100',
    slate: 'bg-slate-50 text-slate-700 border-slate-200',
    violet: 'bg-violet-50 text-violet-700 border-violet-100',
  };

  return (
    <article className="card p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-black text-neighbor-navy">{value}</p>
          {detail && <p className="mt-1 text-sm font-medium text-slate-500">{detail}</p>}
        </div>
        <div className={`shrink-0 rounded-lg border p-3 ${tones[tone]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center gap-2 border-t border-slate-100 pt-3 text-xs font-bold text-slate-500">
          <TrendingUp className="h-3.5 w-3.5 text-emerald-600" />
          {trend}
        </div>
      )}
    </article>
  );
}

function ProgressBar({ value, total, tone = 'bg-neighbor-blue' }) {
  return (
    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
      <div className={`h-full rounded-full ${tone}`} style={{ width: `${pct(value, total)}%` }} />
    </div>
  );
}

function DistributionPanel({ title, subtitle, entries, total, emptyText = 'Sin datos disponibles' }) {
  const normalized = entries.filter(([, count]) => Number(count || 0) > 0);
  return (
    <article className="card p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="font-bold text-neighbor-navy">{title}</h2>
          {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
        </div>
        <Badge>{formatNumber(total)}</Badge>
      </div>
      <div className="mt-5 space-y-4">
        {normalized.length ? normalized.map(([name, count], index) => (
          <div key={name} className="space-y-2">
            <div className="flex items-center justify-between gap-3 text-sm">
              <span className="font-semibold capitalize text-slate-700">{prettyLabel(name)}</span>
              <span className="font-bold text-neighbor-navy">{formatNumber(count)} <span className="text-xs text-slate-400">({pct(count, total)}%)</span></span>
            </div>
            <ProgressBar value={count} total={total} tone={index % 3 === 0 ? 'bg-neighbor-blue' : index % 3 === 1 ? 'bg-emerald-500' : 'bg-amber-500'} />
          </div>
        )) : (
          <p className="rounded-md border border-dashed border-slate-200 p-4 text-sm font-medium text-slate-500">{emptyText}</p>
        )}
      </div>
    </article>
  );
}

function WorkQueueItem({ icon: Icon, title, count, text, to, tone = 'amber' }) {
  const tones = {
    amber: 'bg-amber-50 text-amber-700',
    blue: 'bg-blue-50 text-blue-700',
    red: 'bg-red-50 text-red-700',
    green: 'bg-emerald-50 text-emerald-700',
  };

  return (
    <Link to={to} className="group flex items-center gap-4 rounded-lg border border-slate-200 bg-white p-4 transition hover:border-neighbor-blue hover:shadow-soft">
      <div className={`rounded-lg p-3 ${tones[tone]}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-3">
          <p className="font-bold text-neighbor-navy">{title}</p>
          <span className="text-lg font-black text-neighbor-navy">{formatNumber(count)}</span>
        </div>
        <p className="mt-1 text-sm text-slate-500">{text}</p>
      </div>
      <ArrowRight className="h-4 w-4 text-slate-400 transition group-hover:translate-x-0.5 group-hover:text-neighbor-blue" />
    </Link>
  );
}

function HealthItem({ label, value, detail, state = 'ok' }) {
  const stateConfig = {
    ok: ['Operativo', 'text-emerald-700 bg-emerald-50 border-emerald-200'],
    warn: ['Atención', 'text-amber-700 bg-amber-50 border-amber-200'],
    risk: ['Crítico', 'text-red-700 bg-red-50 border-red-200'],
  };
  const [stateLabel, stateClass] = stateConfig[state] || stateConfig.ok;

  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-100 py-3 last:border-b-0">
      <div>
        <p className="font-semibold text-slate-700">{label}</p>
        <p className="text-sm text-slate-500">{detail}</p>
      </div>
      <div className="text-right">
        <p className="font-black text-neighbor-navy">{value}</p>
        <span className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-xs font-bold ${stateClass}`}>{stateLabel}</span>
      </div>
    </div>
  );
}

function QuickAction({ to, icon: Icon, title, text }) {
  return (
    <Link to={to} className="group rounded-lg border border-slate-200 bg-white p-4 transition hover:border-neighbor-blue hover:shadow-soft">
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-neighbor-mist p-2 text-neighbor-blue">
          <Icon className="h-5 w-5" />
        </div>
        <p className="font-bold text-neighbor-navy">{title}</p>
      </div>
      <p className="mt-3 min-h-10 text-sm text-slate-500">{text}</p>
      <div className="mt-4 flex items-center gap-2 text-sm font-bold text-neighbor-blue">
        Abrir módulo <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
      </div>
    </Link>
  );
}

export default function AdminDashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async ({ silent = false } = {}) => {
    try {
      if (silent) setRefreshing(true);
      else setLoading(true);
      setError(null);
      const stats = await dataService.getStatistics('dashboard');
      setData(stats);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error al cargar las estadísticas del dashboard');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const model = useMemo(() => {
    const users = data?.users || {};
    const payments = data?.payments || {};
    const votings = data?.votings || {};
    const meetings = data?.meetings || {};
    const complaints = data?.complaints || {};
    const chat = data?.chat || {};

    const totalUsers = Number(users.total_users || 0);
    const userStatuses = users.users_by_status || {};
    const paymentStatuses = payments.payments_by_status || {};
    const complaintStatuses = complaints.complaints_by_status || {};
    const pendingUsers = countFrom(userStatuses, ['pendiente']);
    const blockedUsers = countFrom(userStatuses, ['rechazado', 'inactivo']);
    const approvedUsers = countFrom(userStatuses, ['aprobado', 'activo']);
    const pendingPayments = countFrom(paymentStatuses, ['pendiente']);
    const verifiedPayments = countFrom(paymentStatuses, ['verificado', 'completado', 'pagado']);
    const openComplaints = countFrom(complaintStatuses, ['pendiente', 'abierta', 'en revision', 'en proceso']);
    const resolvedComplaints = countFrom(complaintStatuses, ['resuelta', 'resuelto', 'cerrada']);
    const totalComplaints = Number(complaints.total_complaints || sumValues(complaintStatuses));
    const totalPayments = Number(payments.total_payments || sumValues(paymentStatuses));
    const totalVotings = Number(votings.total_votings || 0);
    const activeVotings = Number(votings.active_votings || 0);
    const upcomingMeetings = Number(meetings.upcoming_meetings || 0);
    const totalMessages = Number(chat.total_messages || 0);
    const recentMessages = Number(chat.recent_messages_7d || 0);
    const riskItems = [pendingUsers, pendingPayments, openComplaints].filter((item) => item > 0).length;
    const totalOperationalItems = totalUsers + totalPayments + totalVotings + totalComplaints + Number(chat.total_chat_rooms || 0);

    return {
      users,
      payments,
      votings,
      meetings,
      complaints,
      chat,
      totalUsers,
      pendingUsers,
      blockedUsers,
      approvedUsers,
      pendingPayments,
      verifiedPayments,
      openComplaints,
      resolvedComplaints,
      totalComplaints,
      totalPayments,
      activeVotings,
      upcomingMeetings,
      totalMessages,
      recentMessages,
      totalOperationalItems,
      riskItems,
      approvalRate: pct(approvedUsers, totalUsers),
      collectionRate: pct(verifiedPayments, totalPayments),
      resolutionRate: pct(resolvedComplaints, totalComplaints),
    };
  }, [data]);

  if (loading) {
    return (
      <section className="flex min-h-[460px] items-center justify-center">
        <Spinner label="Cargando panel de administración..." />
      </section>
    );
  }

  if (error) {
    return (
      <section className="flex min-h-[460px] items-center justify-center">
        <div className="card max-w-lg p-8 text-center">
          <AlertCircle className="mx-auto mb-4 h-12 w-12 text-red-500" />
          <h2 className="text-lg font-bold text-slate-700">Error al cargar el panel</h2>
          <p className="mt-2 text-sm text-slate-500">{error}</p>
          <button className="btn-primary mt-5" onClick={() => fetchData()}>
            <RefreshCw className="h-4 w-4" />
            Reintentar
          </button>
        </div>
      </section>
    );
  }

  if (!data) {
    return (
      <section className="flex min-h-[460px] items-center justify-center">
        <div className="card p-8 text-center">
          <h2 className="text-lg font-bold text-slate-700">No hay datos disponibles</h2>
          <p className="mt-1 text-sm text-slate-500">Cuando el backend devuelva estadísticas aparecerán aquí.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-soft">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge>Administración</Badge>
              <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">Sistema operativo</span>
              {model.riskItems > 0 && <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-bold text-amber-700">{model.riskItems} frentes requieren atención</span>}
            </div>
            <h1 className="mt-4 text-3xl font-black text-neighbor-navy">Centro de control comunitario</h1>
            <p className="mt-2 max-w-3xl text-sm font-medium text-slate-500">
              Resumen ejecutivo para priorizar aprobaciones, pagos, solicitudes, participación y actividad operativa de la comunidad.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Link to="/app/reportes" className="btn-secondary">
              <Download className="h-4 w-4" />
              Reportes
            </Link>
            <button className="btn-primary" onClick={() => fetchData({ silent: true })} disabled={refreshing}>
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              Actualizar
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 border-t border-slate-100 pt-5 md:grid-cols-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-slate-400">Usuario</p>
            <p className="mt-1 font-bold text-neighbor-navy">{user?.nombre || 'Administrador'}</p>
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-slate-400">Rol activo</p>
            <p className="mt-1 font-bold capitalize text-neighbor-navy">{prettyLabel(user?.rol || user?.role_name || 'admin')}</p>
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-slate-400">Corte de datos</p>
            <p className="mt-1 font-bold text-neighbor-navy">{data.generated_at ? new Date(data.generated_at).toLocaleString() : 'No informado'}</p>
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-slate-400">Registros supervisados</p>
            <p className="mt-1 font-bold text-neighbor-navy">{formatNumber(model.totalOperationalItems)}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricTile
          icon={Users}
          label="Vecinos registrados"
          value={formatNumber(model.totalUsers)}
          detail={`${model.approvalRate}% aprobados o activos`}
          tone="blue"
          trend={`${formatNumber(model.users.active_users_30d)} registros en los últimos 30 días`}
        />
        <MetricTile
          icon={WalletCards}
          label="Recaudación registrada"
          value={formatMoney(model.payments.total_amount)}
          detail={`${model.collectionRate}% de pagos verificados`}
          tone="green"
          trend={`${formatNumber(model.payments.recent_payments_30d)} pagos recientes`}
        />
        <MetricTile
          icon={ClipboardList}
          label="Solicitudes abiertas"
          value={formatNumber(model.openComplaints)}
          detail={`${model.resolutionRate}% resueltas históricamente`}
          tone={model.openComplaints ? 'amber' : 'green'}
          trend={`${formatNumber(model.complaints.recent_complaints_30d)} casos en 30 días`}
        />
        <MetricTile
          icon={Vote}
          label="Participación cívica"
          value={formatNumber(model.votings.total_votes)}
          detail={`${formatNumber(model.activeVotings)} votaciones activas`}
          tone="violet"
          trend={`${formatNumber(model.votings.recent_votings_30d)} votaciones recientes`}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
        <article className="card p-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="font-bold text-neighbor-navy">Cola de trabajo prioritaria</h2>
              <p className="mt-1 text-sm text-slate-500">Acciones que conviene revisar antes de cerrar la jornada administrativa.</p>
            </div>
            <Gauge className="h-6 w-6 text-neighbor-blue" />
          </div>
          <div className="mt-5 grid gap-3 lg:grid-cols-3">
            <WorkQueueItem
              icon={UserPlus}
              title="Cuentas pendientes"
              count={model.pendingUsers}
              text="Validar identidad, dirección y sector antes de aprobar."
              to="/app/vecinos"
              tone={model.pendingUsers ? 'amber' : 'green'}
            />
            <WorkQueueItem
              icon={WalletCards}
              title="Pagos por verificar"
              count={model.pendingPayments}
              text="Confirmar comprobantes, montos y concepto de cuota."
              to="/app/finanzas"
              tone={model.pendingPayments ? 'amber' : 'green'}
            />
            <WorkQueueItem
              icon={FileText}
              title="Solicitudes abiertas"
              count={model.openComplaints}
              text="Asignar seguimiento y actualizar estado del caso."
              to="/app/solicitudes"
              tone={model.openComplaints ? 'red' : 'green'}
            />
          </div>
        </article>

        <article className="card p-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="font-bold text-neighbor-navy">Salud operativa</h2>
              <p className="mt-1 text-sm text-slate-500">Lectura rápida de riesgos y continuidad.</p>
            </div>
            <ShieldCheck className="h-6 w-6 text-emerald-600" />
          </div>
          <div className="mt-3">
            <HealthItem label="Control de acceso" value={`${model.approvalRate}%`} detail={`${formatNumber(model.pendingUsers)} cuentas pendientes`} state={model.pendingUsers > 0 ? 'warn' : 'ok'} />
            <HealthItem label="Tesorería" value={`${model.collectionRate}%`} detail={`${formatNumber(model.pendingPayments)} pagos sin verificar`} state={model.pendingPayments > 0 ? 'warn' : 'ok'} />
            <HealthItem label="Atención vecinal" value={`${model.resolutionRate}%`} detail={`${formatNumber(model.openComplaints)} solicitudes abiertas`} state={model.openComplaints > 5 ? 'risk' : model.openComplaints > 0 ? 'warn' : 'ok'} />
            <HealthItem label="Actividad comunitaria" value={formatNumber(model.activeVotings + model.upcomingMeetings)} detail="Votaciones activas y reuniones próximas" state="ok" />
          </div>
        </article>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <DistributionPanel
          title="Usuarios por estado"
          subtitle="Aprobación, operación y bloqueos"
          entries={Object.entries(model.users.users_by_status || {})}
          total={sumValues(model.users.users_by_status)}
        />
        <DistributionPanel
          title="Usuarios por rol"
          subtitle="Composición administrativa y vecinal"
          entries={Object.entries(model.users.users_by_role || {})}
          total={sumValues(model.users.users_by_role)}
        />
        <DistributionPanel
          title="Solicitudes por categoría"
          subtitle="Temas con mayor demanda"
          entries={Object.entries(model.complaints.complaints_by_category || {})}
          total={sumValues(model.complaints.complaints_by_category)}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <article className="card p-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-bold text-neighbor-navy">Finanzas y pagos</h2>
              <p className="mt-1 text-sm text-slate-500">Estado de la recaudación y métodos registrados.</p>
            </div>
            <Landmark className="h-6 w-6 text-neighbor-blue" />
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <div className="rounded-lg border border-slate-200 p-4">
              <p className="text-sm font-semibold text-slate-500">Pagos totales</p>
              <p className="mt-2 text-2xl font-black text-neighbor-navy">{formatNumber(model.totalPayments)}</p>
            </div>
            <div className="rounded-lg border border-slate-200 p-4">
              <p className="text-sm font-semibold text-slate-500">Verificados</p>
              <p className="mt-2 text-2xl font-black text-emerald-700">{formatNumber(model.verifiedPayments)}</p>
            </div>
            <div className="rounded-lg border border-slate-200 p-4">
              <p className="text-sm font-semibold text-slate-500">Pendientes</p>
              <p className="mt-2 text-2xl font-black text-amber-700">{formatNumber(model.pendingPayments)}</p>
            </div>
          </div>
          <div className="mt-5 space-y-3">
            {Object.entries(model.payments.payments_by_status || {}).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-2">
                <StatusBadge>{status}</StatusBadge>
                <span className="font-bold text-neighbor-navy">{formatNumber(count)}</span>
              </div>
            ))}
            {!Object.keys(model.payments.payments_by_status || {}).length && <p className="text-sm text-slate-500">No hay estados de pago registrados.</p>}
          </div>
        </article>

        <article className="card p-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-bold text-neighbor-navy">Agenda y participación</h2>
              <p className="mt-1 text-sm text-slate-500">Seguimiento de reuniones, votaciones y conversación comunitaria.</p>
            </div>
            <Activity className="h-6 w-6 text-emerald-600" />
          </div>
          <div className="mt-5 grid gap-3">
            <div className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
              <div className="flex items-center gap-3">
                <CalendarClock className="h-5 w-5 text-neighbor-blue" />
                <div>
                  <p className="font-bold text-neighbor-navy">Reuniones próximas</p>
                  <p className="text-sm text-slate-500">{formatNumber(model.meetings.past_meetings)} reuniones históricas</p>
                </div>
              </div>
              <span className="text-2xl font-black text-neighbor-navy">{formatNumber(model.upcomingMeetings)}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
              <div className="flex items-center gap-3">
                <Vote className="h-5 w-5 text-violet-700" />
                <div>
                  <p className="font-bold text-neighbor-navy">Votaciones activas</p>
                  <p className="text-sm text-slate-500">{formatNumber(model.votings.total_votes)} votos emitidos</p>
                </div>
              </div>
              <span className="text-2xl font-black text-neighbor-navy">{formatNumber(model.activeVotings)}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
              <div className="flex items-center gap-3">
                <MessageSquare className="h-5 w-5 text-emerald-700" />
                <div>
                  <p className="font-bold text-neighbor-navy">Mensajes recientes</p>
                  <p className="text-sm text-slate-500">{formatNumber(model.totalMessages)} mensajes acumulados</p>
                </div>
              </div>
              <span className="text-2xl font-black text-neighbor-navy">{formatNumber(model.recentMessages)}</span>
            </div>
          </div>
        </article>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <QuickAction to="/app/vecinos" icon={UserCheck} title="Gestionar vecinos" text="Aprobar cuentas, revisar estados y mantener el padrón actualizado." />
        <QuickAction to="/app/finanzas" icon={WalletCards} title="Revisar finanzas" text="Validar pagos, cuotas, ingresos, egresos y balance comunitario." />
        <QuickAction to="/app/reportes" icon={BarChart3} title="Emitir reportes" text="Descargar PDF o CSV para asambleas, tesorería y rendición de cuentas." />
        <QuickAction to="/app/reuniones" icon={Clock3} title="Planificar agenda" text="Coordinar reuniones próximas y preparar decisiones comunitarias." />
      </div>
    </section>
  );
}
