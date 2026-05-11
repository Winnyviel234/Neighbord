import { BarChart2, CheckCircle, Clock, TrendingUp, Users, Vote } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Badge, EmptyState, Spinner, StatCard } from '../components/common';
import { dataService, mediaUrl } from '../services/api';
import { dateTime, shortDate, datetimeLocalToISO } from '../lib/utils';
import { useAuth } from '../context/AuthContext';

const blankForm = {
  titulo: '',
  descripcion: '',
  fecha_inicio: '',
  fecha_fin: '',
  opciones: '',
  estado: 'activa',
  modo: 'normal',
  rol_objetivo: 'directiva',
  candidatos: [],
  imagen: null
};

export default function VotacionesPage() {
  const { hasRole } = useAuth();
  const [rows, setRows] = useState(null);
  const [vecinos, setVecinos] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(blankForm);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [voting, setVoting] = useState(null);
  const [preview, setPreview] = useState(null);

  const load = () => dataService.votaciones()
    .then(setRows)
    .catch(() => {
      setRows([]);
      setError('No se pudieron cargar las votaciones reales.');
    });

  useEffect(() => {
    load();
    if (hasRole('admin')) dataService.vecinos().then(setVecinos).catch(() => setVecinos([]));
  }, []);

  const stats = useMemo(() => {
    if (!rows) return null;
    const activas = rows.filter(r => r.estado === 'activa').length;
    const cerradas = rows.filter(r => r.estado === 'cerrada').length;
    const totalVotos = rows.reduce((sum, r) => sum + (r.total_votos || 0), 0);
    return { total: rows.length, activas, cerradas, totalVotos };
  }, [rows]);

  function handleImageChange(e) {
    const file = e.target.files[0];
    if (file) {
      setForm({ ...form, imagen: file });
      setPreview(URL.createObjectURL(file));
    }
  }

  async function submit(event) {
    event.preventDefault();
    setError('');
    
    if (!form.titulo || !form.fecha_inicio || !form.fecha_fin) {
      setError('Por favor completa todos los campos requeridos');
      return;
    }

    // Convertir datetime-local (YYYY-MM-DDTHH:mm) a ISO string
    let fechaInicio, fechaFin;
    try {
      fechaInicio = datetimeLocalToISO(form.fecha_inicio);
      fechaFin = datetimeLocalToISO(form.fecha_fin);
      
      // Validar que fecha_inicio < fecha_fin
      if (new Date(fechaInicio) >= new Date(fechaFin)) {
        setError('La fecha de inicio debe ser anterior a la fecha de fin');
        return;
      }
    } catch {
      setError('Formato de fecha inválido');
      return;
    }

    const opciones = form.modo === 'eleccion'
      ? form.candidatos.map((id) => {
        const vecino = vecinos.find((item) => item.id === id);
        return `election|role=${form.rol_objetivo}|user=${id}|name=${encodeURIComponent(vecino?.nombre || 'Candidato')}`;
      })
      : form.opciones.split(',').map((item) => item.trim()).filter(Boolean);

    if (!opciones.length) {
      setError('Agrega al menos una opcion o candidato.');
      return;
    }

    const payload = {
      titulo: form.titulo,
      descripcion: form.descripcion,
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
      opciones,
      estado: form.estado,
      imagen: form.imagen
    };
    
    try {
      if (editing) await dataService.actualizarVotacion(editing.id, payload);
      else await dataService.crearVotacion(payload);
      setEditing(null);
      setForm({ ...blankForm, imagen: null });
      setPreview(null);
      setMessage(form.modo === 'eleccion' ? 'Eleccion guardada.' : 'Votacion guardada.');
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar la votacion.');
    }
  }

  function edit(row) {
    const electionOptions = (row.opciones || []).map(parseElectionOption).filter(Boolean);
    setEditing(row);
    setForm({
      titulo: row.titulo || '',
      descripcion: row.descripcion || '',
      fecha_inicio: row.fecha_inicio ? row.fecha_inicio.slice(0, 16) : '',
      fecha_fin: row.fecha_fin ? row.fecha_fin.slice(0, 16) : '',
      opciones: electionOptions.length ? '' : (row.opciones || []).join(', '),
      estado: row.estado || 'activa',
      modo: electionOptions.length ? 'eleccion' : 'normal',
      rol_objetivo: electionOptions[0]?.role || 'directiva',
      candidatos: electionOptions.map((option) => option.user),
      imagen: null
    });
    setPreview(mediaUrl(row.imagen_url) || null);
  }

  async function remove(row) {
    if (!window.confirm(`Eliminar la votacion "${row.titulo}"?`)) return;
    await dataService.eliminarVotacion(row.id);
    load();
  }

  async function finishElection(row) {
    try {
      const result = await dataService.finalizarEleccion(row.id);
      setMessage(`${result.ganador.nombre} gano y ahora tiene rol ${roleLabel(result.rol_asignado)}.`);
      setError('');
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo finalizar la eleccion.');
    }
  }

  async function cancelVote(row) {
    try {
      setError('');
      setMessage('');
      setVoting(row.id);
      await dataService.cancelarVoto(row.id);
      setMessage('Tu voto fue cancelado.');
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo cancelar el voto.');
    } finally {
      setVoting(null);
    }
  }

  function toggleCandidate(id) {
    const selected = form.candidatos.includes(id);
    setForm({ ...form, candidatos: selected ? form.candidatos.filter((item) => item !== id) : [...form.candidatos, id] });
  }

  if (!rows) return <Spinner />;
  return (
    <section>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="page-title">Votaciones</h1>
          <p className="mt-1 text-sm font-semibold text-slate-500">Participacion democratica en tiempo real</p>
        </div>
        {stats && (
          <div className="flex gap-2">
            <Badge>{stats.total} total</Badge>
            <Badge>{stats.activas} activas</Badge>
            <Badge>{stats.totalVotos} votos</Badge>
          </div>
        )}
      </div>

      {stats && (
        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <StatCard icon={Vote} label="Total votaciones" value={stats.total} />
          <StatCard icon={CheckCircle} label="Activas" value={stats.activas} tone="green" />
          <StatCard icon={Clock} label="Cerradas" value={stats.cerradas} tone="navy" />
          <StatCard icon={Users} label="Total votos" value={stats.totalVotos} tone="blue" />
        </div>
      )}

      {message && <p className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">{message}</p>}
      {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}

      {hasRole('admin') && (
        <form onSubmit={submit} className="card mt-6 grid gap-3 p-5 md:grid-cols-2">
          <h2 className="font-bold text-neighbor-navy md:col-span-2">{editing ? 'Editar votacion' : 'Crear votacion'}</h2>
          <select className="input" value={form.modo} onChange={(e) => setForm({ ...form, modo: e.target.value, candidatos: [], opciones: '' })}>
            <option value="normal">Votacion normal</option>
            <option value="eleccion">Eleccion con asignacion de rol</option>
          </select>
          <select className="input" value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })}>
            <option value="activa">Activa</option>
            <option value="cerrada">Cerrada</option>
            <option value="cancelada">Cancelada</option>
          </select>
          <input className="input" placeholder="Titulo" value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} required />
          <input className="input" type="datetime-local" value={form.fecha_inicio} onChange={(e) => setForm({ ...form, fecha_inicio: e.target.value })} required />
          <input className="input" type="datetime-local" value={form.fecha_fin} onChange={(e) => setForm({ ...form, fecha_fin: e.target.value })} required />

          {form.modo === 'normal' ? (
            <input className="input md:col-span-2" placeholder="Opciones separadas por coma" value={form.opciones} onChange={(e) => setForm({ ...form, opciones: e.target.value })} required />
          ) : (
            <div className="md:col-span-2">
              <select className="input max-w-sm" value={form.rol_objetivo} onChange={(e) => setForm({ ...form, rol_objetivo: e.target.value })}>
                <option value="directiva">Asignar rol Directiva</option>
                <option value="tesorero">Asignar rol Tesorero</option>
                <option value="vocero">Asignar rol Vocero</option>
                <option value="secretaria">Asignar rol Secretaria</option>
                <option value="vecino">Asignar rol Vecino</option>
              </select>
              <div className="mt-3 grid gap-2 md:grid-cols-2">
                {vecinos.map((vecino) => (
                  <label key={vecino.id} className="flex items-center gap-2 rounded-md border border-slate-200 bg-white p-3 text-sm font-semibold">
                    <input type="checkbox" checked={form.candidatos.includes(vecino.id)} onChange={() => toggleCandidate(vecino.id)} />
                    {vecino.nombre}
                  </label>
                ))}
              </div>
            </div>
          )}

          <textarea className="input min-h-24 md:col-span-2" placeholder="Descripcion" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          <div className="flex gap-2">
            <button className="btn-primary">{editing ? 'Guardar cambios' : 'Crear'}</button>
            {editing && <button type="button" className="btn-secondary" onClick={() => { setEditing(null); setForm({...blankForm, imagen: null }); setPreview(null); }}>Cancelar</button>}
          </div>
        </form>
      )}

      <div className="mt-6 grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {rows.length ? rows.map((row) => {
          const isElection = (row.opciones || []).some((option) => parseElectionOption(option));
          const isActive = row.estado === 'activa';
          const hasVoted = Boolean(row.mi_voto);
          return (
            <article key={row.id} className="card overflow-hidden p-0 flex flex-col">
              {row.imagen_url && (
                <div className="img-container-aspect-video">
                  <img src={mediaUrl(row.imagen_url)} alt={row.titulo} className="img-responsive" />
                </div>
              )}
              <div className="border-b border-slate-100 bg-neighbor-mist p-5">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-bold text-neighbor-navy">{row.titulo}</h3>
                  <div className="flex gap-2">
                    <Badge>{isElection ? 'Eleccion' : 'Votacion'}</Badge>
                    <Badge className={isActive ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-600'}>{row.estado}</Badge>
                  </div>
                </div>
                <p className="mt-2 text-sm text-slate-600">{row.descripcion}</p>
                <p className="mt-2 text-xs font-semibold text-slate-400">
                  {shortDate(row.fecha_inicio)} - {shortDate(row.fecha_fin)}
                </p>
              </div>

              {row.opciones_stats && row.opciones_stats.length > 0 && (
                <div className="space-y-3 p-5">
                  <p className="text-xs font-bold text-slate-500">RESULTADOS EN VIVO ({row.total_votos || 0} votos)</p>
                  {row.opciones_stats.map((stat) => (
                    <div key={stat.opcion} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-700">{optionLabel(stat.opcion)}</span>
                        <span className="font-bold text-neighbor-blue">{stat.count} votos ({stat.percentage}%)</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                        <div className="h-full rounded-full bg-neighbor-blue transition-all" style={{ width: `${stat.percentage}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="border-t border-slate-100 bg-white p-4">
                {isActive ? (
                  <div className="flex flex-wrap gap-2">
                    {hasVoted && (
                      <p className="w-full rounded-md bg-green-50 p-2 text-xs font-bold text-green-700">
                        Ya votaste: {optionLabel(row.mi_voto)}
                      </p>
                    )}
                    {(row.opciones || []).map((op) => (
                      <button
                        key={op}
                        onClick={async () => {
                          try {
                            setVoting(row.id);
                            await dataService.votar(row.id, op);
                            setMessage('Voto registrado exitosamente.');
                            load();
                          } catch (err) {
                            setError(err.response?.data?.detail || 'No se pudo votar.');
                          } finally {
                            setVoting(null);
                          }
                        }}
                        disabled={voting === row.id || hasVoted}
                        className={hasVoted && row.mi_voto === op ? 'btn-primary' : 'btn-secondary'}
                      >
                        {optionLabel(op)}
                      </button>
                    ))}
                    {isActive && hasVoted && (
                      <button
                        type="button"
                        onClick={() => cancelVote(row)}
                        disabled={voting === row.id}
                        className="btn-secondary btn-sm"
                      >
                        Cancelar voto
                      </button>
                    )}
                  </div>
                ) : (
                  <p className="text-xs font-semibold text-slate-400">Votacion cerrada</p>
                )}

                {hasRole('admin') && (
                  <div className="mt-3 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
                    <button className="btn-secondary btn-sm" onClick={() => edit(row)}>Editar</button>
                    {isElection && isActive && (
                      <button className="btn-primary btn-sm" onClick={() => finishElection(row)}>Finalizar y asignar rol</button>
                    )}
                    <button className="btn btn-sm border border-red-200 text-red-600 hover:bg-red-50" onClick={() => remove(row)}>Eliminar</button>
                  </div>
                )}
              </div>
            </article>
          );
        }) : <EmptyState title="No hay votaciones" />}
      </div>
    </section>
  );
}

function parseElectionOption(option) {
  if (!option?.startsWith('election|')) return null;
  return option.split('|').slice(1).reduce((acc, part) => {
    const [key, value] = part.split('=');
    acc[key] = value;
    return acc;
  }, {});
}

function optionLabel(option) {
  if (!option) return '';
  if (typeof option === 'object') return option.opcion || '';
  if (option.startsWith('election|')) {
    const parts = option.split('|').slice(1);
    for (const part of parts) {
      const [key, value] = part.split('=');
      if (key === 'name') return decodeURIComponent(value || 'Candidato');
    }
    return 'Candidato';
  }
  return option;
}

function roleLabel(role) {
  return {
    admin: 'Admin',
    directiva: 'Vice Presidente',
    tesorero: 'Tesorero',
    vocero: 'Vocero',
    secretaria: 'Secretaria',
    vecino: 'Vecino'
  }[role] || role;
}
