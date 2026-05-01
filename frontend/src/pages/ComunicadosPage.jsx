import { useEffect, useState } from 'react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { dataService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function ComunicadosPage() {
  const { hasRole } = useAuth();
  const [rows, setRows] = useState(null);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ titulo: '', contenido: '', categoria: 'general', publicado: true });
  const load = () => dataService.comunicados().then(setRows);
  useEffect(() => { load(); }, []);
  async function submit(event) {
    event.preventDefault();
    if (editing) await dataService.actualizarComunicado(editing.id, form);
    else await dataService.crearComunicado(form);
    setEditing(null);
    setForm({ titulo: '', contenido: '', categoria: 'general', publicado: true });
    load();
  }
  function edit(row) {
    setEditing(row);
    setForm({ titulo: row.titulo || '', contenido: row.contenido || '', categoria: row.categoria || 'general', publicado: row.publicado ?? true });
  }
  async function remove(row) {
    if (!window.confirm(`Eliminar el comunicado "${row.titulo}"?`)) return;
    await dataService.eliminarComunicado(row.id);
    load();
  }
  if (!rows) return <Spinner />;
  return (
    <section>
      <h1 className="page-title">Comunicados</h1>
      {hasRole('admin') && (
        <form onSubmit={submit} className="card mt-6 grid gap-4 p-5 md:grid-cols-2">
          <h2 className="font-bold text-neighbor-navy md:col-span-2">{editing ? 'Editar comunicado' : 'Crear comunicado'}</h2>
          <input className="input" placeholder="Titulo" value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} required />
          <input className="input" placeholder="Categoria" value={form.categoria} onChange={(e) => setForm({ ...form, categoria: e.target.value })} required />
          <textarea className="input min-h-24 md:col-span-2" placeholder="Contenido" value={form.contenido} onChange={(e) => setForm({ ...form, contenido: e.target.value })} required />
          <label className="label flex items-center gap-2"><input type="checkbox" checked={form.publicado} onChange={(e) => setForm({ ...form, publicado: e.target.checked })} /> Publicado</label>
          <div className="flex gap-2">
            <button className="btn-primary">{editing ? 'Guardar cambios' : 'Crear'}</button>
            {editing && <button type="button" className="btn-secondary" onClick={() => { setEditing(null); setForm({ titulo: '', contenido: '', categoria: 'general', publicado: true }); }}>Cancelar</button>}
          </div>
        </form>
      )}
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {rows.length ? rows.map((row) => (
          <article className="card p-5" key={row.id}>
            <Badge>{row.categoria}</Badge>
            <h3 className="mt-3 font-bold text-neighbor-navy">{row.titulo}</h3>
            <p className="mt-2 text-sm text-slate-600">{row.contenido}</p>
            {hasRole('admin') && <div className="mt-4 flex gap-2"><button className="btn-secondary" onClick={() => edit(row)}>Editar</button><button className="btn border border-red-200 text-red-600 hover:bg-red-50" onClick={() => remove(row)}>Eliminar</button></div>}
          </article>
        )) : <EmptyState />}
      </div>
    </section>
  );
}
