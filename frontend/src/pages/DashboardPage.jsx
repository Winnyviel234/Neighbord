import { AlertCircle, BarChart2, Bell, CalendarDays, CheckCircle2, FileText, Megaphone, TrendingUp, Users, Vote, WalletCards } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Badge, EmptyState, Spinner, StatCard } from '../components/common';
import { dataService } from '../services/api';
import { dateTime, money, shortDate } from '../lib/utils';
import { useAuth } from '../context/AuthContext';

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    dataService.dashboard()
      .then(setData)
      .catch(err => setError(err.message || 'Error al cargar el dashboard'));
  }, []);

  if (error) return (
    <section>
      <div className="card p-8 text-center">
        <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
        <h2 className="mt-4 text-lg font-bold text-slate-700">Error al cargar</h2>
        <p className="mt-2 text-sm text-slate-500">{error}</p>
        <button className="btn-primary mt-4" onClick={() => { setError(null); setData(null); dataService.dashboard().then(setData).catch(e => setError(e.message)); }}>
          Reintentar
        </button>
      </div>
    </section>
  );

  if (!data) return <Spinner />;

  const votingStats = data.votaciones_activas?.reduce((acc, v) => {
    acc.totalVotos += (v.total_votos || 0);
    acc.totalOptions += (v.opciones_stats?.length || 0);
    return acc;
  }, { totalVotos: 0, totalOptions: 0 }) || { totalVotos: 0, totalOptions: 0 };

  return (
    <section>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="mt-1 text-sm font-semibold text-slate-500">Bienvenido, {user?.nombre}. {data.resumen?.estado}</p>
        </div>
        <Badge>{roleText(user?.rol)}</Badge>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-5">
        <StatCard icon={Users} label="Vecinos" value={data.vecinos} tone="blue" />
        <StatCard icon={FileText} label="Reportes" value={data.solicitudes} tone="green" />
        <StatCard icon={Bell} label="Eventos" value={data.reuniones} tone="sky" />
        <StatCard icon={Vote} label="Votaciones activas" value={data.votaciones} tone="navy" />
        <StatCard icon={TrendingUp} label="Votos emitidos" value={votingStats.totalVotos} tone="blue" />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Panel icon={Megaphone} title="Ultimos anuncios">
          {data.ultimos_anuncios?.length ? data.ultimos_anuncios.map((item) => (
            <Row key={`${item.id}-${item.titulo}`} title={item.titulo} text={item.contenido || item.resumen || 'Publicacion comunitaria'} />
          )) : <EmptyState title="Sin anuncios" />}
        </Panel>

        <Panel icon={Bell} title="Notificaciones">
          {data.notificaciones?.map((item) => (
            <Row key={item.titulo} title={item.titulo} text={item.mensaje} />
          ))}
        </Panel>

        <Panel icon={FileText} title="Reportes recientes">
          {data.reportes_recientes?.length ? data.reportes_recientes.map((item) => (
            <Row key={item.id} title={item.titulo} text={`${item.estado || 'abierta'} - ${item.descripcion}`} />
          )) : <EmptyState title="Sin reportes recientes" />}
        </Panel>

        <Panel icon={CalendarDays} title="Eventos proximos">
          {data.eventos_proximos?.length ? data.eventos_proximos.map((item) => (
            <Row key={item.id} title={item.titulo} text={`${item.lugar} - ${dateTime(item.fecha)}`} />
          )) : <EmptyState title="Sin eventos" />}
        </Panel>

<Panel icon={Vote} title="Votaciones activas">
          {data.votaciones_activas?.length ? data.votaciones_activas.map((item) => (
            <div key={item.id} className="space-y-2">
              <Row title={item.titulo} text={item.descripcion || 'Disponible para votar'} />
              {item.opciones_stats && item.opciones_stats.length > 0 && (
                <div className="ml-4 space-y-1">
                  <p className="text-xs font-bold text-slate-500">RESULTADOS ({item.total_votos || 0} votos)</p>
                  {item.opciones_stats.map((stat) => (
                    <div key={stat.opcion} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-700">{stat.opcion}</span>
                        <span className="font-bold text-neighbor-blue">{stat.count} ({stat.percentage}%)</span>
                      </div>
                      <div className="h-1.5 overflow-hidden rounded-full bg-slate-100">
                        <div className="h-full rounded-full bg-neighbor-blue" style={{ width: `${stat.percentage}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )) : <EmptyState title="Sin votaciones activas" />}
        </Panel>

        <Panel icon={WalletCards} title="Cuotas y pagos">
          {data.cuotas_activas?.length ? data.cuotas_activas.map((item) => (
            <Row key={item.id} title={item.titulo} text={`${money(item.monto)} - vence ${shortDate(item.fecha_vencimiento)}`} />
          )) : <EmptyState title="Sin cuotas activas" />}
        </Panel>
      </div>
    </section>
  );
}

function Panel({ icon: Icon, title, children }) {
  return (
    <section className="card p-5">
      <h2 className="flex items-center gap-2 font-black text-neighbor-navy"><Icon className="h-5 w-5 text-neighbor-green" /> {title}</h2>
      <div className="mt-4 space-y-3">{children}</div>
    </section>
  );
}

function Row({ title, text }) {
  return (
    <article className="rounded-md border border-slate-100 bg-white p-3">
      <p className="font-bold text-neighbor-navy">{title}</p>
      <p className="mt-1 line-clamp-2 text-sm text-slate-600">{text}</p>
    </article>
  );
}

function roleText(role) {
  return {
    admin: 'Administrador',
    directiva: 'Directiva',
    tesorero: 'Tesorero',
    vecino: 'Vecino'
  }[role] || role;
}
