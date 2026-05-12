import { useEffect, useState } from 'react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { dataService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, MessageCircle, Trash2 } from 'lucide-react';

export default function ComunicadosPage() {
  const { user, hasRole } = useAuth();
  const [rows, setRows] = useState(null);
  const [selectedComunicado, setSelectedComunicado] = useState(null);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ titulo: '', contenido: '', categoria: 'general', publicado: true });
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loadingComments, setLoadingComments] = useState(false);

  const load = () => dataService.comunicados().then(setRows);
  useEffect(() => { load(); }, []);

  const loadComments = (comunicadoId) => {
    if (!comunicadoId) return;
    setLoadingComments(true);
    dataService.getComunicadoComments(comunicadoId)
      .then((data) => setComments(data || []))
      .catch(() => setComments([]))
      .finally(() => setLoadingComments(false));
  };

  const handleAddComment = async () => {
    if (!newComment.trim() || !selectedComunicado) return;
    try {
      const created = await dataService.createComunicadoComment(selectedComunicado.id, newComment);
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
      await dataService.deleteComunicadoComment(commentId);
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

  if (selectedComunicado) {
    return (
      <main className="min-h-screen bg-neighbor-mist p-6">
        <div className="mx-auto max-w-4xl">
          <button onClick={() => setSelectedComunicado(null)} className="mb-6 flex items-center gap-2 text-neighbor-blue hover:text-neighbor-green transition font-bold">
            <ArrowLeft className="h-4 w-4" />
            Volver a comunicados
          </button>

          <article className="rounded-3xl border border-slate-200 bg-white overflow-hidden shadow-lg">
            <div className="p-8 md:p-12">
              <div className="flex items-center justify-between mb-4">
                <Badge>{selectedComunicado.categoria}</Badge>
                <span className="text-xs text-slate-500">
                  {new Date(selectedComunicado.created_at || Date.now()).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>
              <h1 className="text-4xl font-black text-neighbor-navy mb-6">{selectedComunicado.titulo}</h1>
              
              <div className="prose prose-sm max-w-none mb-8">
                <p className="text-lg text-slate-700 leading-relaxed whitespace-pre-wrap">{selectedComunicado.contenido}</p>
              </div>

              <div className="flex items-center gap-4 py-6 border-y border-slate-100">
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-600 rounded-lg">
                  <MessageCircle className="h-5 w-5" />
                  {comments.length} comentarios
                </div>
              </div>

              <div className="mt-8">
                <h3 className="text-2xl font-black text-neighbor-navy mb-6">Comentarios ({comments.length})</h3>
                
                {user && (
                  <div className="bg-slate-50 rounded-2xl p-6 mb-8">
                    <h4 className="font-bold text-neighbor-navy mb-4">Comenta este comunicado</h4>
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
                            {new Date(comment.created_at || Date.now()).toLocaleDateString('es-ES', {
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
                        <p className="text-slate-600 leading-relaxed">{comment.contenido || ''}</p>
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
          <article 
            className="card p-5 cursor-pointer hover:shadow-lg hover:border-neighbor-blue/40 transition" 
            key={row.id}
            onClick={() => { setSelectedComunicado(row); loadComments(row.id); }}
          >
            <Badge>{row.categoria}</Badge>
            <h3 className="mt-3 font-bold text-neighbor-navy">{row.titulo}</h3>
            <p className="mt-2 text-sm text-slate-600">{row.contenido}</p>
            {hasRole('admin') && (
              <div className="mt-4 flex gap-2" onClick={(e) => e.stopPropagation()}>
                <button className="btn-secondary" onClick={() => edit(row)}>Editar</button>
                <button className="btn border border-red-200 text-red-600 hover:bg-red-50" onClick={() => remove(row)}>Eliminar</button>
              </div>
            )}
          </article>
        )) : <EmptyState />}
      </div>
    </section>
  );
}
