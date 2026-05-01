import { Download, FileUp, Mail } from 'lucide-react';
import { useEffect, useState } from 'react';
import { EmptyState } from '../components/common';
import { dataService, mediaUrl } from '../services/api';

const reports = [
  ['vecinos', 'Reporte de vecinos'],
  ['financiero', 'Reporte financiero'],
  ['solicitudes', 'Reporte de solicitudes'],
  ['actas', 'Actas de reuniones'],
  ['cronograma', 'Cronograma']
];

export default function ReportesPage() {
  const [email, setEmail] = useState({ destinatarios: '', asunto: '', mensaje: '' });
  const [documentos, setDocumentos] = useState(null);
  const [documento, setDocumento] = useState({ titulo: '', descripcion: '', archivo: null });
  const [message, setMessage] = useState('');

  const loadDocuments = () => dataService.documentos().then(setDocumentos).catch(() => setDocumentos([]));

  useEffect(() => { loadDocuments(); }, []);

  async function downloadReport(type, format) {
    const blob = await dataService.descargarReporte(type, format);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${type}.${format === 'pdf' ? 'pdf' : 'csv'}`;
    link.click();
    URL.revokeObjectURL(url);
  }

  async function send(e) {
    e.preventDefault();
    const payload = { ...email, destinatarios: email.destinatarios.split(',').map((x) => x.trim()).filter(Boolean) };
    const response = await dataService.enviarEmail(payload);
    setMessage(response.sent ? 'Correo enviado correctamente.' : response.detail);
  }

  async function uploadDocument(e) {
    e.preventDefault();
    if (!documento.archivo) return;
    await dataService.subirDocumento(documento);
    setDocumento({ titulo: '', descripcion: '', archivo: null });
    e.target.reset();
    setMessage('Documento subido correctamente.');
    loadDocuments();
  }

  return (
    <section>
      <h1 className="page-title">Reportes y correos</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {reports.map(([type, label]) => (
          <article key={type} className="card p-5">
            <h3 className="font-bold text-neighbor-navy">{label}</h3>
            <div className="mt-4 flex gap-2">
              <button type="button" className="btn-primary" onClick={() => downloadReport(type, 'pdf')}><Download className="h-4 w-4" /> PDF</button>
              <button type="button" className="btn-secondary" onClick={() => downloadReport(type, 'csv')}><Download className="h-4 w-4" /> Excel</button>
            </div>
          </article>
        ))}
      </div>

      <div className="mt-6 grid items-start gap-6 lg:grid-cols-[420px_minmax(0,1fr)]">
        <div className="grid gap-6">
          <form onSubmit={uploadDocument} className="card p-5">
            <h2 className="flex items-center gap-2 font-bold text-neighbor-navy"><FileUp className="h-5 w-5" /> Subir documento</h2>
            <div className="mt-4 grid gap-4">
              <input className="input" placeholder="Titulo del documento" value={documento.titulo} onChange={(e) => setDocumento({ ...documento, titulo: e.target.value })} required />
              <textarea className="input min-h-24" placeholder="Descripcion opcional" value={documento.descripcion} onChange={(e) => setDocumento({ ...documento, descripcion: e.target.value })} />
              <input className="input" type="file" onChange={(e) => setDocumento({ ...documento, archivo: e.target.files[0] || null })} required />
              <button className="btn-primary w-fit">Subir archivo</button>
            </div>
          </form>

          <form onSubmit={send} className="card p-5">
            <h2 className="flex items-center gap-2 font-bold text-neighbor-navy"><Mail className="h-5 w-5" /> Enviar correo personalizado</h2>
            {message && <p className="mt-3 rounded-md bg-neighbor-mist p-3 text-sm font-semibold text-neighbor-navy">{message}</p>}
            <div className="mt-4 grid gap-4">
              <input className="input" placeholder="destino1@gmail.com, destino2@gmail.com" value={email.destinatarios} onChange={(e) => setEmail({ ...email, destinatarios: e.target.value })} required />
              <input className="input" placeholder="Asunto" value={email.asunto} onChange={(e) => setEmail({ ...email, asunto: e.target.value })} required />
              <textarea className="input min-h-32" placeholder="Mensaje" value={email.mensaje} onChange={(e) => setEmail({ ...email, mensaje: e.target.value })} required />
              <button className="btn-primary w-fit">Enviar correo</button>
            </div>
          </form>
        </div>

        <section className="card p-5 lg:sticky lg:top-6">
          <h2 className="font-bold text-neighbor-navy">Documentos subidos</h2>
          <div className="mt-4 grid max-h-[640px] gap-3 overflow-y-auto pr-1">
            {documentos?.length ? documentos.map((item) => (
              <article key={item.id || item.archivo_url} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-slate-200 p-3">
                <div>
                  <p className="font-bold text-neighbor-navy">{item.titulo || item.nombre_archivo}</p>
                  <p className="text-sm text-slate-500">{item.descripcion || item.nombre_archivo || item.tipo}</p>
                </div>
                <a className="btn-secondary" href={mediaUrl(item.archivo_url)} target="_blank" rel="noreferrer">
                  <Download className="h-4 w-4" /> Abrir
                </a>
              </article>
            )) : <EmptyState title="Sin documentos subidos" />}
          </div>
        </section>
      </div>
    </section>
  );
}
