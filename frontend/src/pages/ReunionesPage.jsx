import { useEffect, useState } from 'react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { dateTime, datetimeLocalToISO } from '../lib/utils';
import { dataService, mediaUrl } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function ReunionesPage() {
  const { hasRole } = useAuth();
  const [rows, setRows] = useState(null);
  const [form, setForm] = useState({ titulo: '', descripcion: '', fecha: '', lugar: '', tipo: 'general', estado: 'programada', imagen: null });
  const [preview, setPreview] = useState(null);
  const [editing, setEditing] = useState(null);
  const load = () => dataService.reuniones().then(setRows);

  useEffect(() => { load(); }, []);

  function handleImageChange(e) {
    const file = e.target.files[0];
    if (file) {
      setForm({ ...form, imagen: file });
      setPreview(URL.createObjectURL(file));
    }
  }

  async function submit(event) {
    event.preventDefault();
    if (!form.fecha || !form.titulo || !form.lugar) {
      alert('Por favor completa todos los campos requeridos');
      return;
    }
    
    let fechaISO;
    try {
      // Convertir datetime-local (YYYY-MM-DDTHH:mm) a ISO string
      fechaISO = datetimeLocalToISO(form.fecha);
    } catch {
      alert('Formato de fecha inválido');
      return;
    }

    const payload = { 
      ...form, 
      fecha: fechaISO,
      imagen: form.imagen 
    };
    
    try {
      if (editing) await dataService.actualizarReunion(editing.id, payload);
      else await dataService.crearReunion(payload);
      setEditing(null);
      setForm({ titulo: '', descripcion: '', fecha: '', lugar: '', tipo: 'general', estado: 'programada', imagen: null });
      setPreview(null);
      load();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error al guardar la reunión');
    }
  }

  function edit(row) {
    setEditing(row);
    setForm({ titulo: row.titulo || '', descripcion: row.descripcion || '', fecha: row.fecha ? row.fecha.slice(0, 16) : '', lugar: row.lugar || '', tipo: row.tipo || 'general', estado: row.estado || 'programada', imagen: null });
    setPreview(mediaUrl(row.imagen_url) || null);
  }

  async function remove(row) {
    if (!window.confirm(`Eliminar la reunion "${row.titulo}"?`)) return;
    await dataService.eliminarReunion(row.id);
    load();
  }

  if (!rows) return <Spinner />;

  return (
    <section>
      <h1 className="page-title">Reuniones y asambleas</h1>
      {hasRole('admin', 'directiva') && (
        <form onSubmit={submit} className="card mt-6 grid gap-4 p-5 md:grid-cols-2">
          <h2 className="font-bold text-neighbor-navy md:col-span-2">{editing ? 'Editar reunion' : 'Crear reunion'}</h2>
          <input className="input" placeholder="Titulo" value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} required />
          <input className="input" placeholder="Lugar" value={form.lugar} onChange={(e) => setForm({ ...form, lugar: e.target.value })} required />
          <input className="input" type="datetime-local" value={form.fecha} onChange={(e) => setForm({ ...form, fecha: e.target.value })} required />
          <select className="input" value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
            <option value="general">Asamblea general</option>
            <option value="directiva">Reunion de directiva</option>
          </select>
          <textarea className="input min-h-24 md:col-span-2" placeholder="Descripcion" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          <div className="md:col-span-2">
            <label className="label">Imagen (opcional)</label>
            <input type="file" accept="image/*" onChange={handleImageChange} className="input" />
            {preview && <img src={preview} alt="Preview" className="mt-2 h-32 w-auto rounded-md object-cover" />}
          </div>
          <div className="flex gap-2">
            <button className="btn-primary w-fit">{editing ? 'Guardar cambios' : 'Crear reunion'}</button>
            {editing && <button type="button" className="btn-secondary" onClick={() => { setEditing(null); setForm({ titulo: '', descripcion: '', fecha: '', lugar: '', tipo: 'general', estado: 'programada', imagen: null }); setPreview(null); }}>Cancelar</button>}
          </div>
        </form>
      )}
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {rows.length ? rows.map((row) => (
          <article key={row.id} className="card overflow-hidden p-0">
            {row.imagen_url && (
              <div className="aspect-video w-full overflow-hidden bg-gradient-to-br from-neighbor-mist to-slate-100">
                <img src={mediaUrl(row.imagen_url)} alt={row.titulo} className="h-full w-full object-cover" />
              </div>
            )}
            <div className="p-5">
              <div className="flex items-start justify-between gap-3">
                <h3 className="font-bold text-neighbor-navy">{row.titulo}</h3>
                <Badge>{row.tipo === 'directiva' ? 'Directiva' : 'General'}</Badge>
              </div>
              <p className="text-sm text-slate-600">{row.lugar} - {dateTime(row.fecha)}</p>
              <p className="text-sm text-slate-600">{row.descripcion}</p>
              {hasRole('admin') && <div className="mt-4 flex gap-2"><button className="btn-secondary" onClick={() => edit(row)}>Editar</button><button className="btn border border-red-200 text-red-600 hover:bg-red-50" onClick={() => remove(row)}>Eliminar</button></div>}
            </div>
          </article>
        )) : <EmptyState />}
      </div>
    </section>
  );
}
