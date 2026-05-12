import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { EmptyState, Spinner } from '../components/common';
import { dataService, mediaUrl } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, MessageCircle, Heart, Trash2 } from 'lucide-react';

export default function NoticiasPage({ publicView = false }) {
  const { user, hasRole } = useAuth();
  const { id } = useParams();
  const [rows, setRows] = useState(null);
  const [selectedNoticia, setSelectedNoticia] = useState(null);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ titulo: '', resumen: '', contenido: '', imagen: null, publicado: true });
  const [preview, setPreview] = useState(null);
  const [editing, setEditing] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [liked, setLiked] = useState(false);
  const [loadingComments, setLoadingComments] = useState(false);

  const load = () => {
    const request = !publicView && hasRole('admin') ? dataService.noticiasAdmin() : dataService.noticias();
    request
      .then((data) => {
        setRows(data);
        if (id) {
          const noticia = data.find(n => n.id === id);
          if (noticia) {
            setSelectedNoticia(noticia);
            loadComments(noticia.id);
          }
        }
      })
      .catch(() => {
        setError('No se pudieron cargar las noticias. Revisa que el backend y Supabase estén conectados.');
        setRows([]);
      });
  };

  const loadComments = (noticiaId) => {
    if (!noticiaId) return;
    setLoadingComments(true);
    dataService.getNoticiaComments(noticiaId)
      .then((data) => setComments(data || []))
      .catch(() => setComments([]))
      .finally(() => setLoadingComments(false));
  };

  const handleAddComment = async () => {
    if (!newComment.trim() || !selectedNoticia) return;
    try {
      const created = await dataService.createNoticiaComment(selectedNoticia.id, newComment);
      if (created) {
        created.usuarios = { nombre: user?.nombre || 'Tú' };
        setComments([...comments, created]);
      }
      setNewComment('');
    } catch (e) {
      console.error('Error al comentar:', e);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Eliminar este comentario?')) return;
    try {
      await dataService.deleteNoticiaComment(commentId);
      setComments(comments.filter(c => c.id !== commentId));
    } catch (e) {
      console.error('Error al eliminar:', e);
    }
  };

  const canDeleteComment = (comment) => {
    if (!user) return false;
    if (hasRole('admin') || hasRole('directiva')) return true;
    return comment.usuario_id === user.id;
  };

  useEffect(() => { load(); }, [id]);

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

  if (selectedNoticia) {
    return (
      <main className="min-h-screen bg-neighbor-mist p-6">
        <div className="mx-auto max-w-4xl">
          <button onClick={() => setSelectedNoticia(null)} className="mb-6 flex items-center gap-2 text-neighbor-blue hover:text-neighbor-green transition font-bold">
            <ArrowLeft className="h-4 w-4" />
            Volver a noticias
          </button>

          <article className="rounded-3xl border border-slate-200 bg-white overflow-hidden shadow-lg">
            {selectedNoticia.imagen_url && (
              <div className="h-80 overflow-hidden bg-gradient-to-br from-neighbor-blue/10 to-emerald-100 md:h-96">
                <img src={mediaUrl(selectedNoticia.imagen_url)} alt={selectedNoticia.titulo} className="h-full w-full object-cover" />
              </div>
            )}
            <div className="p-8 md:p-12">
              <div className="flex items-center justify-between mb-4">
                <span className="inline-flex items-center gap-2 rounded-full bg-neighbor-mist px-3 py-1 text-xs font-bold text-neighbor-blue">
                  Noticia del barrio
                </span>
                <span className="text-xs text-slate-500">
                  {new Date(selectedNoticia.created_at || Date.now()).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>
              <h1 className="text-4xl font-black text-neighbor-navy mb-6">{selectedNoticia.titulo}</h1>
              
              <div className="prose prose-sm max-w-none mb-8">
                <p className="text-lg text-slate-700 leading-relaxed whitespace-pre-wrap">{selectedNoticia.contenido || selectedNoticia.resumen}</p>
              </div>

              <div className="flex items-center gap-4 py-6 border-y border-slate-100">
                <button 
                  onClick={() => setLiked(!liked)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${liked ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                >
                  <Heart className={`h-5 w-5 ${liked ? 'fill-current' : ''}`} />
                  {liked ? 'Te gusta' : 'Me gusta'}
                </button>
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-600 rounded-lg">
                  <MessageCircle className="h-5 w-5" />
                  {comments.length} comentarios
                </div>
              </div>

              <div className="mt-8">
                <h3 className="text-2xl font-black text-neighbor-navy mb-6">Comentarios ({comments.length})</h3>
                
                {user && (
                  <div className="bg-slate-50 rounded-2xl p-6 mb-8">
                    <h4 className="font-bold text-neighbor-navy mb-4">Comparte tu opinión</h4>
                    <div className="flex gap-4">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                        {(user?.nombre || 'U').charAt(0)}
                      </div>
                      <div className="flex-1">
                        <textarea
                          value={newComment}
                          onChange={(e) => setNewComment(e.target.value)}
                          placeholder="Escribe tu comentario aquí..."
                          className="w-full p-4 border border-slate-200 rounded-lg text-sm resize-none focus:border-neighbor-blue focus:outline-none"
                          rows="3"
                        />
                        <div className="flex justify-end gap-2 mt-3">
                          <button
                            onClick={() => setNewComment('')}
                            className="px-4 py-2 text-slate-700 text-sm font-semibold rounded-lg hover:bg-slate-200 transition"
                          >
                            Cancelar
                          </button>
                          <button
                            onClick={handleAddComment}
                            disabled={!newComment.trim()}
                            className="px-6 py-2 bg-neighbor-blue text-white text-sm font-semibold rounded-lg hover:bg-neighbor-green transition disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Comentar
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="space-y-6">
                  {loadingComments ? (
                    <div className="text-center py-8">
                      <Spinner label="Cargando comentarios..." />
                    </div>
                  ) : comments.length > 0 ? comments.map((comment) => (
                    <div key={comment.id} className="flex gap-4">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                        {((comment.usuarios?.nombre) || 'U').charAt(0)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-neighbor-navy">{comment.usuarios?.nombre || 'Usuario'}</span>
                          <span className="text-xs text-slate-500">
                            {new Date(comment.created_at || comment.fecha || Date.now()).toLocaleDateString('es-ES', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                          {canDeleteComment(comment) && (
                            <button
                              onClick={() => handleDeleteComment(comment.id)}
                              className="ml-auto text-slate-400 hover:text-red-500 transition"
                              title="Eliminar comentario"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                        <p className="text-slate-600 leading-relaxed">{comment.contenido || comment.comentario}</p>
                      </div>
                    </div>
                  )) : (
                    <p className="text-center text-slate-500">No hay comentarios aún. ¡Sé el primero en comentar!</p>
                  )}
                </div>
              </div>
            </div>
          </article>
        </div>
      </main>
    );
  }

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
            <article 
              key={row.id} 
              className="card overflow-hidden cursor-pointer hover:shadow-lg hover:border-neighbor-blue/40 transition"
              onClick={() => { setSelectedNoticia(row); loadComments(row.id); }}
            >
              {row.imagen_url && (
                <div className="h-52 w-full overflow-hidden bg-gradient-to-br from-neighbor-mist to-slate-100 md:h-56">
                  <img className="h-full w-full object-cover hover:scale-105 transition" src={mediaUrl(row.imagen_url)} alt={row.titulo} />
                </div>
              )}
              <div className="p-5">
                <h3 className="font-bold text-neighbor-navy">{row.titulo}</h3>
                <p className="mt-2 text-sm text-slate-600">{row.resumen}</p>
                {!publicView && hasRole('admin') && (
                  <div className="mt-4 flex gap-2" onClick={(e) => e.stopPropagation()}>
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
