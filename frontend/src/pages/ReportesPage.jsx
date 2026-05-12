import {
  BarChart3,
  Trash2,
  Download,
  FileSpreadsheet,
  FileText,
  FileUp,
  Mail,
  PieChart,
  RefreshCw,
  Send,
  UploadCloud,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { dataService, mediaUrl } from '../services/api';

const reports = [
  { type: 'vecinos', label: 'Reporte de vecinos', text: 'Padrón, estados y datos de contacto.', icon: FileText, tone: 'blue' },
  { type: 'financiero', label: 'Reporte financiero', text: 'Resumen de ingresos, egresos y balances.', icon: PieChart, tone: 'green' },
  { type: 'solicitudes', label: 'Reporte de solicitudes', text: 'Casos abiertos, resueltos y pendientes.', icon: BarChart3, tone: 'amber' },
  { type: 'actas', label: 'Actas de reuniones', text: 'Documentos formales y acuerdos.', icon: FileSpreadsheet, tone: 'violet' },
  { type: 'cronograma', label: 'Cronograma', text: 'Reuniones, eventos y fechas importantes.', icon: FileText, tone: 'slate' },
];

const moneyFormatter = new Intl.NumberFormat('es-BO', {
  style: 'currency',
  currency: 'BOB',
  maximumFractionDigits: 2,
});

const numberFormatter = new Intl.NumberFormat('es-BO');

const formatNumber = (value) => numberFormatter.format(Number(value || 0));
const formatMoney = (value) => moneyFormatter.format(Number(value || 0));
const sum = (items = []) => items.reduce((total, value) => total + Number(value || 0), 0);

function ToneIcon({ icon: Icon, tone = 'blue' }) {
  const tones = {
    blue: 'border-blue-100 bg-blue-50 text-blue-700',
    green: 'border-emerald-100 bg-emerald-50 text-emerald-700',
    amber: 'border-amber-100 bg-amber-50 text-amber-700',
    violet: 'border-violet-100 bg-violet-50 text-violet-700',
    slate: 'border-slate-200 bg-slate-50 text-slate-700',
  };

  return (
    <div className={`inline-flex h-11 w-11 items-center justify-center rounded-lg border ${tones[tone] || tones.blue}`}>
      <Icon className="h-5 w-5" />
    </div>
  );
}

function MetricCard({ label, value, detail, icon: Icon, tone }) {
  return (
    <article className="card p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-black text-neighbor-navy">{value}</p>
          {detail && <p className="mt-1 text-sm text-slate-500">{detail}</p>}
        </div>
        <ToneIcon icon={Icon} tone={tone} />
      </div>
    </article>
  );
}

function ReportCard({ report, onDownload }) {
  const { type, label, text, icon, tone } = report;

  return (
    <article className="card flex min-h-[190px] flex-col justify-between p-5 transition hover:border-neighbor-blue/40 hover:shadow-lg">
      <div>
        <div className="flex items-start justify-between gap-4">
          <ToneIcon icon={icon} tone={tone} />
          <Badge>{type}</Badge>
        </div>
        <h3 className="mt-4 font-black text-neighbor-navy">{label}</h3>
        <p className="mt-2 text-sm leading-6 text-slate-500">{text}</p>
      </div>
      <div className="mt-5 grid grid-cols-2 gap-2">
        <button type="button" className="btn-primary px-3" onClick={() => onDownload(type, 'pdf')}>
          <Download className="h-4 w-4" /> PDF
        </button>
        <button type="button" className="btn-secondary px-3" onClick={() => onDownload(type, 'xlsx')}>
          <FileSpreadsheet className="h-4 w-4" /> Excel
        </button>
      </div>
    </article>
  );
}

function TrendPanel({ analytics }) {
  const trends = analytics?.payment_trends || {};
  const months = trends.months || [];
  const amounts = trends.amounts || [];
  const maxAmount = Math.max(...amounts.map((value) => Number(value || 0)), 1);
  const categories = analytics?.complaint_trends?.categories || {};

  return (
    <section className="card overflow-hidden">
      <div className="border-b border-slate-100 bg-slate-50/70 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-black text-neighbor-navy">Análisis avanzado</h2>
            <p className="mt-1 text-sm text-slate-500">Lectura rápida para preparar reuniones y rendición de cuentas.</p>
          </div>
          <Badge>{months.length || 0} periodos</Badge>
        </div>
      </div>
      <div className="grid gap-5 p-5 lg:grid-cols-[1.5fr_1fr]">
        <div className="rounded-lg border border-slate-200 p-4">
          <p className="font-bold text-neighbor-navy">Tendencia de pagos</p>
          <div className="mt-4 space-y-3">
            {months.length ? months.map((month, index) => {
              const amount = Number(amounts[index] || 0);
              return (
                <div key={month} className="space-y-1.5">
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <span className="font-semibold text-slate-600">{month}</span>
                    <span className="font-bold text-neighbor-navy">{formatMoney(amount)}</span>
                  </div>
                  <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                    <div className="h-full rounded-full bg-neighbor-blue" style={{ width: `${Math.max(4, Math.min(100, (amount / maxAmount) * 100))}%` }} />
                  </div>
                </div>
              );
            }) : (
              <p className="rounded-md border border-dashed border-slate-200 p-4 text-sm text-slate-500">No hay tendencia de pagos disponible.</p>
            )}
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 p-4">
          <p className="font-bold text-neighbor-navy">Categorías de solicitudes</p>
          <div className="mt-4 space-y-2">
            {Object.entries(categories).length ? Object.entries(categories).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2 text-sm">
                <span className="font-semibold capitalize text-slate-600">{category}</span>
                <span className="font-black text-neighbor-navy">{formatNumber(count)}</span>
              </div>
            )) : (
              <p className="rounded-md border border-dashed border-slate-200 p-4 text-sm text-slate-500">No hay datos de categorías disponibles.</p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

export default function ReportesPage() {
  const [email, setEmail] = useState({ destinatarios: '', asunto: '', mensaje: '' });
  const [documentos, setDocumentos] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [documento, setDocumento] = useState({ titulo: '', descripcion: '', archivo: null });
  const [message, setMessage] = useState('');
  const [loadingAnalytics, setLoadingAnalytics] = useState(true);
  const [sending, setSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const loadDocuments = () => dataService.documentos().then(setDocumentos).catch(() => setDocumentos([]));
  const loadAnalytics = async () => {
    try {
      setLoadingAnalytics(true);
      setAnalytics(await dataService.getAnalytics());
    } catch {
      setAnalytics(null);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  useEffect(() => {
    loadDocuments();
    loadAnalytics();
  }, []);

  const metrics = useMemo(() => {
    const dashboard = analytics?.dashboard || {};
    const payments = dashboard.payments || {};
    const complaints = dashboard.complaints || {};
    const votings = dashboard.votings || {};

    return [
      {
        label: 'Pagos recientes',
        value: formatNumber(payments.recent_payments_30d),
        detail: 'Registrados en 30 días',
        icon: BarChart3,
        tone: 'blue',
      },
      {
        label: 'Monto total',
        value: formatMoney(payments.total_amount),
        detail: `${formatNumber(payments.total_payments)} pagos registrados`,
        icon: PieChart,
        tone: 'green',
      },
      {
        label: 'Solicitudes',
        value: formatNumber(complaints.total_complaints),
        detail: 'Casos para seguimiento',
        icon: FileText,
        tone: 'amber',
      },
      {
        label: 'Participación',
        value: formatNumber(votings.total_votes),
        detail: `${formatNumber(votings.active_votings)} votaciones activas`,
        icon: FileSpreadsheet,
        tone: 'violet',
      },
    ];
  }, [analytics]);

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
    try {
      setSending(true);
      const payload = {
        ...email,
        destinatarios: email.destinatarios.split(',').map((x) => x.trim()).filter(Boolean),
      };
      const response = await dataService.enviarEmail(payload);
      setMessage(response.sent ? 'Correo enviado correctamente.' : response.detail);
    } catch (err) {
      setMessage(err.response?.data?.detail || 'No se pudo enviar el correo.');
    } finally {
      setSending(false);
    }
  }

  async function uploadDocument(e) {
    e.preventDefault();
    if (!documento.archivo) return;
    try {
      setUploading(true);
      await dataService.subirDocumento(documento);
      setDocumento({ titulo: '', descripcion: '', archivo: null });
      e.target.reset();
      setMessage('Documento subido correctamente.');
      loadDocuments();
    } catch (err) {
      setMessage(err.response?.data?.detail || 'No se pudo subir el documento.');
    } finally {
      setUploading(false);
    }
  }

  async function deleteDocument(item) {
    const id = item.id || item.nombre_archivo;
    if (!id) return;
    const confirmed = window.confirm(`¿Eliminar "${item.titulo || item.nombre_archivo || 'documento'}"?`);
    if (!confirmed) return;
    try {
      setDeletingId(id);
      await dataService.eliminarDocumento(id);
      setMessage('Documento eliminado correctamente.');
      loadDocuments();
    } catch (err) {
      setMessage(err.response?.data?.detail || 'No se pudo eliminar el documento.');
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-lg border border-neighbor-blue/10 bg-[linear-gradient(135deg,#eef7fb_0%,#ffffff_55%,#ecf8ef_100%)] p-6 shadow-soft">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-black uppercase tracking-[0.2em] text-neighbor-green">Centro documental</p>
            <h1 className="mt-2 text-3xl font-black text-neighbor-navy">Reportes y correos</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
              Genera documentos, revisa indicadores, sube respaldos y envía comunicaciones formales desde un solo lugar.
            </p>
          </div>
          <button type="button" className="btn-secondary" onClick={loadAnalytics} disabled={loadingAnalytics}>
            <RefreshCw className={`h-4 w-4 ${loadingAnalytics ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
        </div>
      </div>

      {loadingAnalytics ? (
        <div className="card">
          <Spinner label="Cargando análisis de reportes..." />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => <MetricCard key={metric.label} {...metric} />)}
        </div>
      )}

      <section>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-black text-neighbor-navy">Descargas rápidas</h2>
            <p className="mt-1 text-sm text-slate-500">Exporta cada módulo en PDF o Excel/CSV.</p>
          </div>
          <Badge>{reports.length} reportes</Badge>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          {reports.map((report) => (
            <ReportCard key={report.type} report={report} onDownload={downloadReport} />
          ))}
        </div>
      </section>

      {analytics && <TrendPanel analytics={analytics} />}

      <div className="grid items-start gap-6 lg:grid-cols-[420px_minmax(0,1fr)]">
        <div className="grid gap-6">
          <form onSubmit={uploadDocument} className="card overflow-hidden">
            <div className="border-b border-slate-100 bg-slate-50/70 p-5">
              <h2 className="flex items-center gap-2 font-black text-neighbor-navy">
                <FileUp className="h-5 w-5 text-neighbor-green" /> Subir documento
              </h2>
              <p className="mt-1 text-sm text-slate-500">Guarda actas, respaldos o archivos importantes.</p>
            </div>
            <div className="grid gap-4 p-5">
              <input className="input" placeholder="Título del documento" value={documento.titulo} onChange={(e) => setDocumento({ ...documento, titulo: e.target.value })} required />
              <textarea className="input min-h-24" placeholder="Descripción opcional" value={documento.descripcion} onChange={(e) => setDocumento({ ...documento, descripcion: e.target.value })} />
              <label className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600">
                <span className="flex items-center gap-2 font-bold text-neighbor-navy"><UploadCloud className="h-4 w-4 text-neighbor-blue" /> Seleccionar archivo</span>
                <input className="mt-3 block w-full text-sm" type="file" onChange={(e) => setDocumento({ ...documento, archivo: e.target.files[0] || null })} required />
              </label>
              <button className="btn-primary w-fit" disabled={uploading}>
                <UploadCloud className="h-4 w-4" /> {uploading ? 'Subiendo...' : 'Subir archivo'}
              </button>
            </div>
          </form>

          <form onSubmit={send} className="card overflow-hidden">
            <div className="border-b border-slate-100 bg-slate-50/70 p-5">
              <h2 className="flex items-center gap-2 font-black text-neighbor-navy">
                <Mail className="h-5 w-5 text-neighbor-green" /> Enviar correo personalizado
              </h2>
              <p className="mt-1 text-sm text-slate-500">Comunicación formal para vecinos o directiva.</p>
            </div>
            <div className="grid gap-4 p-5">
              {message && <p className="rounded-md bg-neighbor-mist p-3 text-sm font-semibold text-neighbor-navy">{message}</p>}
              <input className="input" placeholder="destino1@gmail.com, destino2@gmail.com" value={email.destinatarios} onChange={(e) => setEmail({ ...email, destinatarios: e.target.value })} required />
              <input className="input" placeholder="Asunto" value={email.asunto} onChange={(e) => setEmail({ ...email, asunto: e.target.value })} required />
              <textarea className="input min-h-32" placeholder="Mensaje" value={email.mensaje} onChange={(e) => setEmail({ ...email, mensaje: e.target.value })} required />
              <button className="btn-primary w-fit" disabled={sending}>
                <Send className="h-4 w-4" /> {sending ? 'Enviando...' : 'Enviar correo'}
              </button>
            </div>
          </form>
        </div>

        <section className="card overflow-hidden lg:sticky lg:top-6">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 bg-slate-50/70 p-5">
            <div>
              <h2 className="font-black text-neighbor-navy">Documentos subidos</h2>
              <p className="mt-1 text-sm text-slate-500">Biblioteca interna de respaldos.</p>
            </div>
            <Badge>{formatNumber(documentos?.length || 0)}</Badge>
          </div>
          <div className="grid max-h-[640px] gap-3 overflow-y-auto p-5">
            {documentos === null ? (
              <Spinner label="Cargando documentos..." />
            ) : documentos.length ? documentos.map((item) => (
              <article key={item.id || item.archivo_url} className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-4 transition hover:border-neighbor-blue/40 hover:shadow-soft">
                <div className="min-w-0">
                  <p className="font-bold text-neighbor-navy">{item.titulo || item.nombre_archivo}</p>
                  <p className="mt-1 max-w-xl truncate text-sm text-slate-500">{item.descripcion || item.nombre_archivo || item.tipo}</p>
                </div>
                <a className="btn-secondary" href={mediaUrl(item.archivo_url)} target="_blank" rel="noreferrer">
                  <Download className="h-4 w-4" /> Abrir
                </a>
                <button
                  type="button"
                  className="btn border border-red-200 text-red-600 hover:bg-red-50"
                  onClick={() => deleteDocument(item)}
                  disabled={deletingId === (item.id || item.nombre_archivo)}
                >
                  <Trash2 className="h-4 w-4" />
                  {deletingId === (item.id || item.nombre_archivo) ? 'Eliminando...' : 'Eliminar'}
                </button>
              </article>
            )) : (
              <EmptyState title="Sin documentos subidos" text="Cuando subas actas o respaldos aparecerán aquí." />
            )}
          </div>
        </section>
      </div>
    </section>
  );
}
