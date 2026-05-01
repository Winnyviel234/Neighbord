import { useState } from 'react';
import api from '../services/api';
import { dataService } from '../services/api';

export default function AdminPublicacionesPage() {
  const [comunicado, setComunicado] = useState({ titulo: '', contenido: '', categoria: 'general', publicado: true });
  const [noticia, setNoticia] = useState({ titulo: '', resumen: '', contenido: '', imagen: null, publicado: true });
  const [preview, setPreview] = useState(null);
  const [message, setMessage] = useState('');

  async function saveComunicado(e) {
    e.preventDefault();
    await api.post('/comunicados', comunicado);
    setMessage('Comunicado publicado.');
    setComunicado({ titulo: '', contenido: '', categoria: 'general', publicado: true });
  }

  async function saveNoticia(e) {
    e.preventDefault();
    await dataService.crearNoticia(noticia);
    setMessage('Noticia publicada.');
    setNoticia({ titulo: '', resumen: '', contenido: '', imagen: null, publicado: true });
    setPreview(null);
    e.target.reset();
  }

  return (
    <section>
      <h1 className="page-title">Publicaciones</h1>
      {message && <p className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">{message}</p>}
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <form onSubmit={saveComunicado} className="card space-y-4 p-5">
          <h2 className="font-bold text-neighbor-navy">Nuevo comunicado</h2>
          <input className="input" placeholder="Título" value={comunicado.titulo} onChange={(e) => setComunicado({ ...comunicado, titulo: e.target.value })} required />
          <input className="input" placeholder="Categoría" value={comunicado.categoria} onChange={(e) => setComunicado({ ...comunicado, categoria: e.target.value })} required />
          <textarea className="input min-h-36" placeholder="Contenido" value={comunicado.contenido} onChange={(e) => setComunicado({ ...comunicado, contenido: e.target.value })} required />
          <button className="btn-primary">Publicar comunicado</button>
        </form>
        <form onSubmit={saveNoticia} className="card space-y-4 p-5">
          <h2 className="font-bold text-neighbor-navy">Nueva noticia</h2>
          <input className="input" placeholder="Título" value={noticia.titulo} onChange={(e) => setNoticia({ ...noticia, titulo: e.target.value })} required />
          <input className="input" placeholder="Resumen" value={noticia.resumen} onChange={(e) => setNoticia({ ...noticia, resumen: e.target.value })} required />
          <div>
            <label className="label">Imagen relacionada</label>
            <input
              className="input"
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files[0] || null;
                setNoticia({ ...noticia, imagen: file });
                setPreview(file ? URL.createObjectURL(file) : null);
              }}
            />
            {preview && <img src={preview} alt="Preview" className="mt-2 h-32 w-auto rounded-md object-cover" />}
          </div>
          <textarea className="input min-h-36" placeholder="Contenido" value={noticia.contenido} onChange={(e) => setNoticia({ ...noticia, contenido: e.target.value })} required />
          <button className="btn-primary">Publicar noticia</button>
        </form>
      </div>
    </section>
  );
}
