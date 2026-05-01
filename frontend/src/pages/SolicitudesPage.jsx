import { useEffect, useState } from 'react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { dataService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function SolicitudesPage() {
  const { hasRole } = useAuth();
  const [rows, setRows] = useState(null);
  const [form, setForm] = useState({ titulo: '', descripcion: '', categoria: 'general', prioridad: 'media' });
  const [editing, setEditing] = useState(null);
  const load = () => dataService.solicitudes().then(setRows);
  useEffect(() => { load(); }, []);
  async function submit(e) {
    e.preventDefault();
    if (editing) await dataService.actualizarSolicitud(editing.id, form);
    else await dataService.crearSolicitud(form);
    setEditing(null);
    setForm({ titulo: '', descripcion: '', categoria: 'general', prioridad: 'media' });
    load();
  }
  function edit(row) {
    setEditing(row);
    setForm({ titulo: row.titulo || '', descripcion: row.descripcion || '', categoria: row.categoria || 'general', prioridad: row.prioridad || 'media' });
  }
  async function remove(row) {
    if (!window.confirm(`Eliminar la solicitud "${row.titulo}"?`)) return;
    await dataService.eliminarSolicitud(row.id);
    load();
  }
  if (!rows) return <Spinner />;
  return (
    <section>
      <h1 className="page-title">Quejas y solicitudes</h1>
      <form onSubmit={submit} className="card mt-6 grid gap-4 p-5 md:grid-cols-[1fr_1fr_auto]">
        <input className="input" placeholder="Título" value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} required />
        <input className="input" placeholder="Descripción" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} required />
        <button className="btn-primary">{editing ? 'Guardar' : 'Crear'}</button>
        {editing && <button type="button" className="btn-secondary" onClick={() => { setEditing(null); setForm({ titulo: '', descripcion: '', categoria: 'general', prioridad: 'media' }); }}>Cancelar</button>}
      </form>
      <div className="mt-6 grid gap-4">{rows.length ? rows.map((row) => <article key={row.id} className="card p-5"><div className="flex justify-between"><h3 className="font-bold text-neighbor-navy">{row.titulo}</h3><Badge>{row.estado}</Badge></div><p className="mt-2 text-sm text-slate-600">{row.descripcion}</p>{hasRole('admin') && <div className="mt-4 flex gap-2"><button className="btn-secondary" onClick={() => edit(row)}>Editar</button><button className="btn border border-red-200 text-red-600 hover:bg-red-50" onClick={() => remove(row)}>Eliminar</button></div>}</article>) : <EmptyState />}</div>
    </section>
  );
}
