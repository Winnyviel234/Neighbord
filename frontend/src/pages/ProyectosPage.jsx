import { useState, useEffect } from 'react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { dataService, mediaUrl } from '../services/api';
import { money, shortDate, dateTime } from '../lib/utils';
import { useAuth } from '../context/AuthContext';
import {
  Plus,
  DollarSign,
  CheckCircle2,
  Clock,
  Users,
  Target,
  TrendingUp,
  Zap,
  ExternalLink,
  X,
  Calendar,
  AlertCircle,
  Lock
} from 'lucide-react';

const STATUS_CONFIG = {
  planeado: { label: 'Planeado', color: 'bg-slate-100 text-slate-700 border-slate-200' },
  en_progreso: { label: 'En progreso', color: 'bg-blue-50 text-neighbor-blue border-blue-200' },
  completado: { label: 'Completado', color: 'bg-green-50 text-green-700 border-green-200' },
  cancelado: { label: 'Cancelado', color: 'bg-red-50 text-red-600 border-red-200' }
};

const PRIORIDAD_CONFIG = {
  baja: { label: 'Baja', color: 'bg-slate-100 text-slate-600' },
  media: { label: 'Media', color: 'bg-yellow-50 text-yellow-700' },
  alta: { label: 'Alta', color: 'bg-orange-50 text-orange-700' },
  critica: { label: 'Crítica', color: 'bg-red-50 text-red-700' }
};

export default function ProyectosPage() {
  const { user, hasRole } = useAuth();
  const [projects, setProjects] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [contributions, setContributions] = useState(null);
  const [showContributeModal, setShowContributeModal] = useState(false);
  const [contributeAmount, setContributeAmount] = useState('25.00');
  const [contributeResult, setContributeResult] = useState(null);
  const [contributeLoading, setContributeLoading] = useState(false);
  const [contributeError, setContributeError] = useState('');
  const [form, setForm] = useState({
    title: '',
    description: '',
    status: 'planeado',
    presupuesto_estimado: '',
    fecha_inicio: new Date().toISOString().slice(0, 10),
    fecha_fin_estimada: '',
    prioridad: 'media'
  });

  const isAdmin = hasRole('admin') || hasRole('directiva');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = () => {
    setLoading(true);
    setError('');
    dataService.getProyectos()
      .then((data) => {
        setProjects(data || []);
        setLoading(false);
      })
      .catch((err) => {
        setError('No se pudieron cargar los proyectos.');
        setProjects([]);
        setLoading(false);
      });
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.title || !form.description || !form.presupuesto_estimado || !form.fecha_fin_estimada) {
      return;
    }

    try {
      const result = await dataService.crearProyecto({
        title: form.title,
        description: form.description,
        presupuesto_estimado: Number(form.presupuesto_estimado),
        fecha_inicio: form.fecha_inicio,
        fecha_fin_estimada: form.fecha_fin_estimada,
        status: form.status,
        prioridad: form.prioridad
      });
      
      if (result?.error) {
        console.error('Error del servidor:', result.detail);
        alert(`Error al crear proyecto: ${result.detail}`);
        return;
      }
      
      setShowCreateModal(false);
      setForm({
        title: '',
        description: '',
        status: 'planeado',
        presupuesto_estimado: '',
        fecha_inicio: new Date().toISOString().slice(0, 10),
        fecha_fin_estimada: '',
        prioridad: 'media'
      });
      loadProjects();
    } catch (err) {
      console.error('Error al crear proyecto:', err);
      const serverError = err?.response?.data?.detail || err?.message || 'Error desconocido';
      alert(`Error al crear proyecto: ${serverError}`);
    }
  };

  const openProject = async (project) => {
    setSelectedProject(project);
    setContributions(null);
    try {
      const data = await dataService.getContribucionesProyecto(project.id);
      setContributions(data);
    } catch (err) {
      console.error('Error al cargar contribuciones:', err);
    }
  };

  const handleContribute = async () => {
    if (!selectedProject || !contributeAmount || Number(contributeAmount) <= 0) return;

    setContributeLoading(true);
    setContributeError('');
    setContributeResult(null);

    try {
      const result = await dataService.aportarProyecto(
        selectedProject.id,
        Number(contributeAmount),
        `Aporte a: ${selectedProject.title}`
      );
      setContributeResult(result);
    } catch (err) {
      setContributeError(err?.response?.data?.detail || 'No se pudo iniciar el pago. Intenta de nuevo.');
    } finally {
      setContributeLoading(false);
    }
  };

  const checkPaymentStatus = async () => {
    if (!contributeResult?.contribution_id || !selectedProject) return;
    try {
      const result = await dataService.checkContribucionStatus(
        selectedProject.id,
        contributeResult.contribution_id
      );
      if (result.paid) {
        alert('¡Pago verificado! Gracias por tu aporte.');
        openProject(selectedProject);
      } else {
        alert(`El pago aún está pendiente. Estado: ${result.status}`);
      }
    } catch (err) {
      console.error('Error al verificar:', err);
    }
  };

  if (loading) return <Spinner label="Cargando proyectos..." />;

  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="page-title">Proyectos Comunitarios</h1>
          <p className="mt-1 text-sm font-semibold text-slate-500">
            Iniciativas para mejorar nuestra comunidad. Apoya los proyectos con aportes económicos.
          </p>
        </div>
        {isAdmin && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary inline-flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Nuevo proyecto
          </button>
        )}
      </div>

      {error && (
        <div className="mt-6 rounded-xl bg-red-50 p-4 text-sm font-semibold text-red-700 flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      {selectedProject ? (
        <div className="mt-6 space-y-6">
          <button
            onClick={() => { setSelectedProject(null); setContributeResult(null); }}
            className="inline-flex items-center gap-2 text-sm font-bold text-neighbor-blue hover:text-neighbor-green transition"
          >
            ← Volver a proyectos
          </button>

          <div className="card overflow-hidden">
            <div className="bg-gradient-to-r from-neighbor-blue/10 to-neighbor-green/10 p-6 md:p-8">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="max-w-3xl">
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <Badge className={STATUS_CONFIG[selectedProject.status]?.color || 'bg-slate-100'}>
                      {STATUS_CONFIG[selectedProject.status]?.label || selectedProject.status}
                    </Badge>
                    <Badge className={PRIORIDAD_CONFIG[selectedProject.prioridad]?.color || 'bg-slate-100'}>
                      Prioridad: {PRIORIDAD_CONFIG[selectedProject.prioridad]?.label || selectedProject.prioridad}
                    </Badge>
                  </div>
                  <h2 className="text-3xl font-black text-neighbor-navy">{selectedProject.title}</h2>
                  <p className="mt-3 text-base text-slate-600 leading-relaxed">{selectedProject.description}</p>
                </div>

                {selectedProject.status !== 'cancelado' && selectedProject.status !== 'completado' && (
                  <button
                    onClick={() => { setShowContributeModal(true); setContributeResult(null); setContributeError(''); }}
                    className="btn-primary inline-flex items-center gap-2 text-base px-6 py-3 shadow-lg shadow-neighbor-blue/20"
                  >
                    <DollarSign className="h-5 w-5" />
                    Aportar a este proyecto
                  </button>
                )}
              </div>

              <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <div className="rounded-2xl bg-white/80 p-4 border border-white/50">
                  <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                    <Target className="h-3.5 w-3.5" />
                    Presupuesto
                  </div>
                  <p className="mt-2 text-2xl font-black text-neighbor-navy">
                    {money(selectedProject.presupuesto_estimado)}
                  </p>
                </div>

                <div className="rounded-2xl bg-white/80 p-4 border border-white/50">
                  <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                    <TrendingUp className="h-3.5 w-3.5" />
                    Recaudado
                  </div>
                  <p className="mt-2 text-2xl font-black text-neighbor-green">
                    {money(contributions?.total_recibido || 0)}
                  </p>
                </div>

                <div className="rounded-2xl bg-white/80 p-4 border border-white/50">
                  <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                    <Users className="h-3.5 w-3.5" />
                    Aportes
                  </div>
                  <p className="mt-2 text-2xl font-black text-neighbor-blue">
                    {contributions?.count || 0}
                  </p>
                </div>

                <div className="rounded-2xl bg-white/80 p-4 border border-white/50">
                  <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                    <Calendar className="h-3.5 w-3.5" />
                    Progreso
                  </div>
                  <p className="mt-2 text-2xl font-black text-neighbor-navy">
                    {selectedProject.progreso || 0}%
                  </p>
                </div>
              </div>

              {selectedProject.presupuesto_estimado > 0 && (
                <div className="mt-6">
                  <div className="flex justify-between text-sm font-semibold mb-2">
                    <span className="text-slate-600">
                      Recaudado: {money(contributions?.total_recibido || 0)}
                    </span>
                    <span className="text-neighbor-blue">
                      Meta: {money(selectedProject.presupuesto_estimado)}
                    </span>
                  </div>
                  <div className="h-4 overflow-hidden rounded-full bg-slate-200">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-neighbor-blue to-neighbor-green transition-all duration-700"
                      style={{
                        width: `${Math.min(100, ((contributions?.total_recibido || 0) / selectedProject.presupuesto_estimado) * 100)}%`
                      }}
                    />
                  </div>
                  <p className="mt-2 text-xs text-slate-500 text-center">
                    {Math.round(((contributions?.total_recibido || 0) / selectedProject.presupuesto_estimado) * 100)}% completado
                  </p>
                </div>
              )}
            </div>
          </div>

          {contributions?.contributions?.length > 0 && (
            <div className="card overflow-hidden">
              <div className="border-b border-slate-200 p-5">
                <h3 className="font-black text-neighbor-navy text-lg">Historial de aportes</h3>
              </div>
              <div className="divide-y divide-slate-100 max-h-[400px] overflow-y-auto">
                {contributions.contributions.map((c) => (
                  <div key={c.id} className="p-5 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-neighbor-blue to-neighbor-green text-white text-xs font-black">
                        {(c.usuarios?.nombre || 'U').charAt(0)}
                      </div>
                      <div className="min-w-0">
                        <p className="font-bold text-slate-700 truncate">{c.usuarios?.nombre || 'Anónimo'}</p>
                        <p className="text-xs text-slate-500">{dateTime(c.created_at)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-black text-neighbor-navy">{money(c.monto)}</span>
                      <Badge className={
                        c.estado === 'verificado' || c.estado === 'pagado'
                          ? 'bg-green-50 text-green-700'
                          : 'bg-yellow-50 text-yellow-700'
                      }>
                        {c.estado === 'verificado' || c.estado === 'pagado' ? (
                          <span className="flex items-center gap-1">
                            <CheckCircle2 className="h-3 w-3" /> Verificado
                          </span>
                        ) : (
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" /> Pendiente
                          </span>
                        )}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="mt-6">
          {!projects?.length ? (
            <EmptyState title="Sin proyectos activos" />
          ) : (
            <div className="grid gap-6 md:grid-cols-2">
              {projects.map((p) => (
                <article
                  key={p.id}
                  className="card overflow-hidden cursor-pointer hover:shadow-xl hover:border-neighbor-blue/30 transition-all duration-300 group"
                  onClick={() => openProject(p)}
                >
                  <div className={`h-2 ${
                    p.status === 'completado' ? 'bg-green-500' :
                    p.status === 'en_progreso' ? 'bg-neighbor-blue' :
                    p.status === 'cancelado' ? 'bg-red-400' : 'bg-slate-300'
                  }`} />
                  
                  <div className="p-6">
                    <div className="flex flex-wrap items-center gap-2 mb-3">
                      <Badge className={STATUS_CONFIG[p.status]?.color || 'bg-slate-100'}>
                        {STATUS_CONFIG[p.status]?.label || p.status}
                      </Badge>
                      <Badge className="bg-slate-100 text-slate-600">
                        {PRIORIDAD_CONFIG[p.prioridad]?.label || p.prioridad}
                      </Badge>
                    </div>

                    <h3 className="font-black text-neighbor-navy text-xl group-hover:text-neighbor-blue transition">
                      {p.title}
                    </h3>
                    <p className="mt-2 text-sm text-slate-600 line-clamp-2">{p.description}</p>

                    <div className="mt-5 grid grid-cols-3 gap-4 pt-4 border-t border-slate-100">
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">Meta</p>
                        <p className="mt-1 font-black text-neighbor-navy">{money(p.presupuesto_estimado)}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">Inicio</p>
                        <p className="mt-1 font-bold text-slate-600">{shortDate(p.fecha_inicio)}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">Progreso</p>
                        <p className="mt-1 font-black text-neighbor-green">{p.progreso || 0}%</p>
                      </div>
                    </div>

                    {p.presupuesto_estimado > 0 && (
                      <div className="mt-4">
                        <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                          <div
                            className={`h-full rounded-full transition-all ${
                              p.status === 'completado' ? 'bg-green-500' :
                              p.status === 'en_progreso' ? 'bg-gradient-to-r from-neighbor-blue to-neighbor-green' :
                              'bg-slate-300'
                            }`}
                            style={{ width: `${Math.min(100, p.progreso || 0)}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto card rounded-3xl">
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <div>
                <h2 className="font-black text-neighbor-navy text-xl">Nuevo Proyecto</h2>
                <p className="text-sm text-slate-500 mt-1">Crea una nueva iniciativa comunitaria</p>
              </div>
              <button onClick={() => setShowCreateModal(false)} className="p-2 hover:bg-slate-100 rounded-lg transition">
                <X className="h-5 w-5 text-slate-500" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="p-6 grid gap-4">
              <label className="block">
                <span className="text-sm font-semibold text-slate-700">Título del proyecto</span>
                <input
                  className="input mt-2"
                  placeholder="Ej: Mejoramiento de parque central"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  required
                />
              </label>

              <label className="block">
                <span className="text-sm font-semibold text-slate-700">Descripción</span>
                <textarea
                  className="input mt-2 min-h-24"
                  placeholder="Describe el proyecto, objetivos y beneficios para la comunidad..."
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  required
                />
              </label>

              <div className="grid gap-4 md:grid-cols-2">
                <label className="block">
                  <span className="text-sm font-semibold text-slate-700">Presupuesto estimado (USD)</span>
                  <input
                    className="input mt-2"
                    type="number"
                    min="1"
                    step="0.01"
                    placeholder="5000.00"
                    value={form.presupuesto_estimado}
                    onChange={(e) => setForm({ ...form, presupuesto_estimado: e.target.value })}
                    required
                  />
                </label>

                <label className="block">
                  <span className="text-sm font-semibold text-slate-700">Prioridad</span>
                  <select
                    className="input mt-2"
                    value={form.prioridad}
                    onChange={(e) => setForm({ ...form, prioridad: e.target.value })}
                  >
                    <option value="baja">Baja</option>
                    <option value="media">Media</option>
                    <option value="alta">Alta</option>
                    <option value="critica">Crítica</option>
                  </select>
                </label>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <label className="block">
                  <span className="text-sm font-semibold text-slate-700">Fecha de inicio</span>
                  <input
                    className="input mt-2"
                    type="date"
                    value={form.fecha_inicio}
                    onChange={(e) => setForm({ ...form, fecha_inicio: e.target.value })}
                    required
                  />
                </label>

                <label className="block">
                  <span className="text-sm font-semibold text-slate-700">Fecha estimada de fin</span>
                  <input
                    className="input mt-2"
                    type="date"
                    value={form.fecha_fin_estimada}
                    onChange={(e) => setForm({ ...form, fecha_fin_estimada: e.target.value })}
                    required
                  />
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button type="submit" className="btn-primary inline-flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Crear proyecto
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="btn-secondary"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Contribute Modal */}
      {showContributeModal && selectedProject && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg max-h-[90vh] overflow-y-auto card rounded-3xl">
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <div>
                <h2 className="font-black text-neighbor-navy text-xl flex items-center gap-2">
                  <Zap className="h-5 w-5 text-neighbor-green" />
                  Aportar a proyecto
                </h2>
                <p className="text-sm text-slate-500 mt-1">{selectedProject.title}</p>
              </div>
              <button
                onClick={() => { setShowContributeModal(false); setContributeResult(null); }}
                className="p-2 hover:bg-slate-100 rounded-lg transition"
              >
                <X className="h-5 w-5 text-slate-500" />
              </button>
            </div>

            {contributeResult ? (
              <div className="p-6">
                <div className="text-center mb-6">
                  <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-green-100 mb-4">
                    <CheckCircle2 className="h-8 w-8 text-green-600" />
                  </div>
                  <h3 className="font-black text-neighbor-navy text-xl">Pago listo</h3>
                  <p className="text-sm text-slate-500 mt-2">
                    Tu aporte de <span className="font-black text-neighbor-green">{money(contributeResult.amount || contributeAmount)}</span> está listo para completarse.
                  </p>
                </div>

                {contributeResult.lnurl && (
                  <a
                    href={contributeResult.lnurl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-neighbor-blue px-5 py-3 text-sm font-bold text-white shadow-lg shadow-neighbor-blue/20 hover:bg-neighbor-navy transition"
                  >
                    <ExternalLink className="h-4 w-4" />
                    Ir a Strike para pagar
                  </a>
                )}

                {contributeResult.payment_request && (
                  <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500 mb-2">
                      Código Lightning
                    </p>
                    <textarea
                      readOnly
                      value={contributeResult.payment_request}
                      className="input w-full min-h-28 bg-white text-xs resize-none"
                    />
                    <p className="mt-2 text-xs text-slate-500">
                      Copia este código y pégalo en tu app compatible con Lightning Network.
                    </p>
                  </div>
                )}

                <div className="mt-6 flex gap-3">
                  <button
                    onClick={checkPaymentStatus}
                    className="btn-secondary flex-1"
                  >
                    Verificar estado del pago
                  </button>
                  <button
                    onClick={() => { setShowContributeModal(false); setContributeResult(null); }}
                    className="btn-primary flex-1"
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-6">
                {contributeError && (
                  <div className="mb-4 rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700 flex items-center gap-2">
                    <AlertCircle className="h-4 w-4" />
                    {contributeError}
                  </div>
                )}

                <div className="mb-6 rounded-2xl bg-gradient-to-r from-neighbor-blue/10 to-neighbor-green/10 p-5 border border-neighbor-blue/20">
                  <div className="flex items-center gap-3">
                    <Lock className="h-5 w-5 text-neighbor-blue" />
                    <div>
                      <p className="text-sm font-bold text-neighbor-navy">Pago seguro con Strike</p>
                      <p className="text-xs text-slate-500 mt-1">
                        Usamos Strike API para pagos Lightning Network. Transferencias rápidas y seguras.
                      </p>
                    </div>
                  </div>
                </div>

                <label className="block">
                  <span className="text-sm font-semibold text-slate-700">Monto del aporte (USD)</span>
                  <input
                    className="input mt-2 text-xl font-black text-center"
                    type="number"
                    min="1"
                    step="0.01"
                    value={contributeAmount}
                    onChange={(e) => setContributeAmount(e.target.value)}
                    required
                  />
                </label>

                <div className="mt-4 grid grid-cols-4 gap-2">
                  {['10.00', '25.00', '50.00', '100.00'].map((amount) => (
                    <button
                      key={amount}
                      type="button"
                      onClick={() => setContributeAmount(amount)}
                      className={`rounded-lg border py-2 text-sm font-bold transition ${
                        contributeAmount === amount
                          ? 'bg-neighbor-blue text-white border-neighbor-blue'
                          : 'bg-white text-slate-600 border-slate-200 hover:border-neighbor-blue/50'
                      }`}
                    >
                      ${amount}
                    </button>
                  ))}
                </div>

                <div className="mt-6 flex gap-3">
                  <button
                    onClick={handleContribute}
                    disabled={contributeLoading || !contributeAmount || Number(contributeAmount) <= 0}
                    className="btn-primary flex-1 inline-flex items-center justify-center gap-2"
                  >
                    {contributeLoading ? (
                      <>Generando pago...</>
                    ) : (
                      <>
                        <Zap className="h-4 w-4" />
                        Iniciar pago
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowContributeModal(false)}
                    className="btn-secondary"
                    disabled={contributeLoading}
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
