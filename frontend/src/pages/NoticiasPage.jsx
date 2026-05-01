import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { EmptyState, Spinner } from '../components/common';
import { dataService, mediaUrl } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function NoticiasPage({ publicView = false }) {
  const { user, hasRole } = useAuth();
  const [rows, setRows] = useState(null);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ titulo: '', resumen: '', contenido: '', imagen: null, publicado: true });
  const [preview, setPreview] = useState(null);
  const [editing, setEditing] = useState(null);

  const load = () => {
    const request = !publicView && hasRole('admin') ? dataService.noticiasAdmin() : dataService.noticias();
    request
      .then(setRows)
      .catch(() => {
        setError('No se pudieron cargar las noticias. Revisa que el backend y Supabase estén conectados.');
        setRows([]);
      });
  };

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
    if (editing) await dataService.actualizarNoticia(editing.id, form);
    else await dataService.crearNoticia(form);
    setEditing(null);
    setForm({ titulo: '', resumen: '', contenido: '', imagen: null, publicado: true });
    setPreview(null);
    load();
  }

  function edit(row) {
    setEditing(row);
    setForm({ titulo: row.titulo || '', resumen: row.resumen || '', contenido: row.contenido || '', imagen: null, publicado: row.publicado ?? true });
    setPreview(mediaUrl(row.imagen_url) || null);
  }

  async function remove(row) {
    if (!window.confirm(`Eliminar la noticia "${row.titulo}"?`)) return;
    await dataService.eliminarNoticia(row.id);
    load();
  }

  if (!rows) return <Spinner label="Cargando noticias..." />;

  return (
    <main className={publicView ? 'min-h-screen bg-neighbor-mist p-6' : ''}>
      <div className="mx-auto max-w-6xl">
        {publicView && <Link className="font-bold text-neighbor-blue" to="/">← Inicio</Link>}
        <h1 className="page-title mt-4">Noticias del barrio</h1>
        {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}
        {!publicView && user && (
          <form onSubmit={submit} className="card mt-6 grid gap-4 p-5 md:grid-cols-2">
            <h2 className="font-bold text-neighbor-navy md:col-span-2">{editing ? 'Editar noticia vecinal' : 'Publicar noticia vecinal'}</h2>
            <input className="input" placeholder="Titulo" value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} required />
            <input className="input" placeholder="Resumen" value={form.resumen} onChange={(e) => setForm({ ...form, resumen: e.target.value })} required />
            <textarea className="input min-h-28 md:col-span-2" placeholder="Contenido" value={form.contenido} onChange={(e) => setForm({ ...form, contenido: e.target.value })} required />
            <div className="md:col-span-2">
              <label className="label">Imagen (opcional)</label>
              <input type="file" accept="image/*" onChange={handleImageChange} className="input" />
              {preview && <img src={preview} alt="Preview" className="mt-2 h-32 w-auto rounded-md object-cover" />}
            </div>
            <label className="label flex items-center gap-2"><input type="checkbox" checked={form.publicado} onChange={(e) => setForm({ ...form, publicado: e.target.checked })} /> Publicada</label>
            <div className="flex gap-2">
              <button className="btn-primary w-fit">{editing ? 'Guardar cambios' : 'Publicar noticia'}</button>
              {editing && <button type="button" className="btn-secondary" onClick={() => { setEditing(null); setForm({ titulo: '', resumen: '', contenido: '', imagen: null, publicado: true }); setPreview(null); }}>Cancelar</button>}
            </div>
          </form>
        )}
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {rows.length ? rows.map((row) => (
            <article key={row.id} className="card overflow-hidden">
              {row.imagen_url && (
                <div className="aspect-video w-full overflow-hidden bg-gradient-to-br from-neighbor-mist to-slate-100">
                  <img className="h-full w-full object-cover" src={mediaUrl(row.imagen_url)} alt={row.titulo} />
                </div>
              )}
              <div className="p-5">
                <h3 className="font-bold text-neighbor-navy">{row.titulo}</h3>
                <p className="mt-2 text-sm text-slate-600">{row.resumen}</p>
                {!publicView && hasRole('admin') && (
                  <div className="mt-4 flex gap-2">
                    <button className="btn-secondary" onClick={() => edit(row)}>Editar</button>
                    <button className="btn border border-red-200 text-red-600 hover:bg-red-50" onClick={() => remove(row)}>Eliminar</button>
                  </div>
                )}
              </div>
            </article>
          )) : <EmptyState />}
        </div>
      </div>
    </main>
  );
}
