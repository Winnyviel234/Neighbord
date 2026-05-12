import { useEffect, useState } from 'react';
import { dataService, mediaUrl } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { EmptyState, Spinner, Badge } from '../components/common';
import { Plus, Edit2, Trash2, X, MessageSquare, Newspaper, Megaphone, Eye, EyeOff } from 'lucide-react';

export default function AdminPublicacionesPage() {
  const { user, hasRole } = useAuth();
  const [activeTab, setActiveTab] = useState('noticias');
  const [noticias, setNoticias] = useState(null);
  const [comunicados, setComunicados] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [message, setMessage] = useState('');

  const [noticiaForm, setNoticiaForm] = useState({ titulo: '', resumen: '', contenido: '', imagen: null, publicado: true });
  const [comunicadoForm, setComunicadoForm] = useState({ titulo: '', contenido: '', categoria: 'general', publicado: true });
  const [preview, setPreview] = useState(null);

  const load = () => {
    setLoading(true);
    Promise.all([
      dataService.noticiasAdmin().catch(() => []),
      dataService.comunicados().catch(() => [])
    ]).then(([noticiasData, comunicadosData]) => {
      setNoticias(Array.isArray(noticiasData) ? noticiasData : []);
      setComunicados(Array.isArray(comunicadosData) ? comunicadosData : []);
    }).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  function resetForm() {
    setEditing(null);
    setNoticiaForm({ titulo: '', resumen: '', contenido: '', imagen: null, publicado: true });
    setComunicadoForm({ titulo: '', contenido: '', categoria: 'general', publicado: true });
    setPreview(null);
    setShowForm(false);
  }

  function handleImageChange(e) {
    const file = e.target.files[0];
    if (file) {
      setNoticiaForm({ ...noticiaForm, imagen: file });
      setPreview(URL.createObjectURL(file));
    }
  }

  async function saveNoticia(e) {
    e.preventDefault();
    try {
      if (editing) {
        await dataService.actualizarNoticia(editing.id, noticiaForm);
        setMessage('Noticia actualizada correctamente.');
      } else {
        await dataService.crearNoticia(noticiaForm);
        setMessage('Noticia publicada correctamente.');
      }
      resetForm();
      load();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error: ' + (error?.response?.data?.detail || error.message));
    }
  }

  async function saveComunicado(e) {
    e.preventDefault();
    try {
      if (editing) {
        await dataService.actualizarComunicado(editing.id, comunicadoForm);
        setMessage('Comunicado actualizado correctamente.');
      } else {
        await dataService.crearComunicado(comunicadoForm);
        setMessage('Comunicado publicado correctamente.');
      }
      resetForm();
      load();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error: ' + (error?.response?.data?.detail || error.message));
    }
  }

  function editNoticia(item) {
    setEditing(item);
    setActiveTab('noticias');
    setNoticiaForm({
      titulo: item.titulo || '',
      resumen: item.resumen || '',
      contenido: item.contenido || '',
      imagen: null,
      publicado: item.publicado !== false
    });
    setShowForm(true);
  }

  function editComunicado(item) {
    setEditing(item);
    setActiveTab('comunicados');
    setComunicadoForm({
      titulo: item.titulo || '',
      contenido: item.contenido || '',
      categoria: item.categoria || 'general',
      publicado: item.publicado !== false
    });
    setShowForm(true);
  }

  async function deleteNoticia(item) {
    if (!window.confirm('Eliminar esta noticia?')) return;
    try {
      await dataService.eliminarNoticia(item.id);
      setMessage('Noticia eliminada.');
      load();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error al eliminar: ' + error.message);
    }
  }

  async function deleteComunicado(item) {
    if (!window.confirm('Eliminar este comunicado?')) return;
    try {
      await dataService.eliminarComunicado(item.id);
      setMessage('Comunicado eliminado.');
      load();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error al eliminar: ' + error.message);
    }
  }

  if (loading) return <section><h1 className="page-title">Publicaciones</h1><div className="mt-8 card p-8 text-center"><Spinner /></div></section>;

  const currentItems = activeTab === 'noticias' ? noticias : comunicados;

  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="page-title">Publicaciones</h1>
        <button
          className="btn-primary flex items-center gap-2"
          onClick={() => { resetForm(); setShowForm(true); }}
        >
          <Plus className="h-4 w-4" /> Nueva publicación
        </button>
      </div>

      {message && <p className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">{message}</p>}

      <div className="mt-6 flex gap-1 border-b border-slate-200">
        <button
          className={`px-4 py-2 font-bold text-sm border-b-2 transition ${activeTab === 'noticias' ? 'border-neighbor-blue text-neighbor-blue' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
          onClick={() => setActiveTab('noticias')}
        >
          <Newspaper className="h-4 w-4 inline mr-2" />
          Noticias ({(noticias || []).length})
        </button>
        <button
          className={`px-4 py-2 font-bold text-sm border-b-2 transition ${activeTab === 'comunicados' ? 'border-neighbor-blue text-neighbor-blue' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
          onClick={() => setActiveTab('comunicados')}
        >
          <Megaphone className="h-4 w-4 inline mr-2" />
          Comunicados ({(comunicados || []).length})
        </button>
      </div>

      {showForm && (
        <div className="mt-6 card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-neighbor-navy text-lg">
              {editing ? 'Editar' : 'Nueva'} {activeTab === 'noticias' ? 'noticia' : 'comunicado'}
            </h2>
            <button className="text-slate-400 hover:text-slate-600" onClick={resetForm}>
              <X className="h-5 w-5" />
            </button>
          </div>

          {activeTab === 'noticias' ? (
            <form onSubmit={saveNoticia} className="space-y-4">
              <input
                className="input"
                placeholder="Título"
                value={noticiaForm.titulo}
                onChange={(e) => setNoticiaForm({ ...noticiaForm, titulo: e.target.value })}
                required
              />
              <input
                className="input"
                placeholder="Resumen"
                value={noticiaForm.resumen}
                onChange={(e) => setNoticiaForm({ ...noticiaForm, resumen: e.target.value })}
                required
              />
              <div>
                <label className="label">Imagen relacionada</label>
                <input className="input" type="file" accept="image/*" onChange={handleImageChange} />
                {preview && <img src={preview} alt="Preview" className="mt-2 h-32 w-auto rounded-md object-cover" />}
                {editing?.imagen_url && !preview && <img src={mediaUrl(editing.imagen_url)} alt="Actual" className="mt-2 h-32 w-auto rounded-md object-cover" />}
              </div>
              <textarea
                className="input min-h-36"
                placeholder="Contenido"
                value={noticiaForm.contenido}
                onChange={(e) => setNoticiaForm({ ...noticiaForm, contenido: e.target.value })}
                required
              />
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={noticiaForm.publicado}
                  onChange={(e) => setNoticiaForm({ ...noticiaForm, publicado: e.target.checked })}
                />
                <span className="text-sm font-semibold text-slate-600">Publicado</span>
              </label>
              <div className="flex gap-2">
                <button type="submit" className="btn-primary">{editing ? 'Actualizar' : 'Publicar'} noticia</button>
                <button type="button" className="btn-secondary" onClick={resetForm}>Cancelar</button>
              </div>
            </form>
          ) : (
            <form onSubmit={saveComunicado} className="space-y-4">
              <input
                className="input"
                placeholder="Título"
                value={comunicadoForm.titulo}
                onChange={(e) => setComunicadoForm({ ...comunicadoForm, titulo: e.target.value })}
                required
              />
              <input
                className="input"
                placeholder="Categoría"
                value={comunicadoForm.categoria}
                onChange={(e) => setComunicadoForm({ ...comunicadoForm, categoria: e.target.value })}
                required
              />
              <textarea
                className="input min-h-36"
                placeholder="Contenido"
                value={comunicadoForm.contenido}
                onChange={(e) => setComunicadoForm({ ...comunicadoForm, contenido: e.target.value })}
                required
              />
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={comunicadoForm.publicado}
                  onChange={(e) => setComunicadoForm({ ...comunicadoForm, publicado: e.target.checked })}
                />
                <span className="text-sm font-semibold text-slate-600">Publicado</span>
              </label>
              <div className="flex gap-2">
                <button type="submit" className="btn-primary">{editing ? 'Actualizar' : 'Publicar'} comunicado</button>
                <button type="button" className="btn-secondary" onClick={resetForm}>Cancelar</button>
              </div>
            </form>
          )}
        </div>
      )}

      <div className="mt-6 grid gap-4">
        {!currentItems || currentItems.length === 0 ? (
          <EmptyState title={`No hay ${activeTab} aún`} />
        ) : (
          currentItems.map((item) => (
            <article key={item.id} className="card p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex gap-4 min-w-0">
                  {activeTab === 'noticias' && item.imagen_url && (
                    <img
                      src={mediaUrl(item.imagen_url)}
                      alt={item.titulo}
                      className="h-20 w-20 rounded-lg object-cover flex-shrink-0"
                    />
                  )}
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-bold text-neighbor-navy truncate">{item.titulo}</h3>
                      {item.publicado === false ? (
                        <Badge className="bg-amber-50 text-amber-700 flex items-center gap-1">
                          <EyeOff className="h-3 w-3" /> Borrador
                        </Badge>
                      ) : (
                        <Badge className="bg-green-50 text-green-700 flex items-center gap-1">
                          <Eye className="h-3 w-3" /> Publicado
                        </Badge>
                      )}
                      {item.categoria && <Badge>{item.categoria}</Badge>}
                    </div>
                    {item.resumen && <p className="mt-1 text-sm text-slate-600 line-clamp-2">{item.resumen}</p>}
                    {item.contenido && !item.resumen && <p className="mt-1 text-sm text-slate-600 line-clamp-2">{item.contenido}</p>}
                    <p className="mt-2 text-xs text-slate-400">
                      {item.created_at ? new Date(item.created_at).toLocaleDateString('es-ES', { dateStyle: 'medium' }) : ''}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  {activeTab === 'noticias' ? (
                    <>
                      <button className="btn border border-slate-200 p-2" onClick={() => editNoticia(item)} title="Editar">
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button className="btn border border-red-200 text-red-600 p-2 hover:bg-red-50" onClick={() => deleteNoticia(item)} title="Eliminar">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </>
                  ) : (
                    <>
                      <button className="btn border border-slate-200 p-2" onClick={() => editComunicado(item)} title="Editar">
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button className="btn border border-red-200 text-red-600 p-2 hover:bg-red-50" onClick={() => deleteComunicado(item)} title="Eliminar">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
