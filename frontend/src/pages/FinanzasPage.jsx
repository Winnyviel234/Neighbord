import { useEffect, useState } from 'react';
import { CheckCircle, ExternalLink, Pencil, Trash2, X, XCircle } from 'lucide-react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { money, shortDate } from '../lib/utils';
import { dataService, mediaUrl } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function FinanzasPage() {
  const { hasRole } = useAuth();
  const [pagos, setPagos] = useState(null);
  const [transacciones, setTransacciones] = useState(null);
  const [cuotas, setCuotas] = useState(null);
  const [cuotaForm, setCuotaForm] = useState({ titulo: '', descripcion: '', monto: '', fecha_vencimiento: '', estado: 'activa' });
  const [editingCuota, setEditingCuota] = useState(null);
  const [message, setMessage] = useState('');
  const load = () => {
    dataService.pagos().then(setPagos);
    dataService.transacciones().then(setTransacciones);
    dataService.cuotas().then(setCuotas);
  };
  useEffect(() => {
    load();
  }, []);

  async function createCuota(event) {
    event.preventDefault();
    const payload = { ...cuotaForm, monto: Number(cuotaForm.monto) };
    if (editingCuota) {
      await dataService.actualizarCuota(editingCuota.id, payload);
      setMessage('Cuota actualizada.');
    } else {
      await dataService.crearCuota(payload);
      setMessage('Cuota creada.');
    }
    resetCuotaForm();
    load();
  }

  function editCuota(row) {
    setEditingCuota(row);
    setMessage('');
    setCuotaForm({
      titulo: row.titulo || '',
      descripcion: row.descripcion || '',
      monto: row.monto ?? '',
      fecha_vencimiento: row.fecha_vencimiento ? row.fecha_vencimiento.slice(0, 10) : '',
      estado: row.estado || 'activa'
    });
  }

  function resetCuotaForm() {
    setEditingCuota(null);
    setCuotaForm({ titulo: '', descripcion: '', monto: '', fecha_vencimiento: '', estado: 'activa' });
  }

  async function deleteCuota(row) {
    if (!window.confirm(`Eliminar la cuota "${row.titulo}"?`)) return;
    await dataService.eliminarCuota(row.id);
    if (editingCuota?.id === row.id) resetCuotaForm();
    setMessage('Cuota eliminada.');
    load();
  }

  async function changePaymentStatus(row, estado) {
    await dataService.cambiarEstadoPago(row.id, estado);
    setMessage(estado === 'verificado' ? 'Pago verificado.' : 'Pago rechazado.');
    load();
  }

  if (!pagos || !transacciones || !cuotas) return <Spinner />;
  const hasFinancialRows = transacciones.length > 0 || pagos.length > 0;
  const ingresos = transacciones.filter((t) => t.tipo === 'ingreso').reduce((sum, item) => sum + Number(item.monto || 0), 0);
  const egresos = transacciones.filter((t) => t.tipo === 'egreso').reduce((sum, item) => sum + Number(item.monto || 0), 0);
  return (
    <section>
      <h1 className="page-title">Finanzas</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <Box label="Ingresos" value={hasFinancialRows ? money(ingresos) : 'Sin pagos reales'} />
        <Box label="Egresos" value={transacciones.length ? money(egresos) : 'Sin egresos reales'} />
        <Box label="Balance" value={hasFinancialRows ? money(ingresos - egresos) : 'Sin balance real'} />
      </div>
      {hasRole('admin', 'tesorero') && (
        <form onSubmit={createCuota} className="card mt-6 grid gap-4 p-5 md:grid-cols-2">
          <div className="flex items-center justify-between gap-3 md:col-span-2">
            <h2 className="font-bold text-neighbor-navy">{editingCuota ? 'Editar cuota comunitaria' : 'Crear cuota comunitaria'}</h2>
            {editingCuota && (
              <button type="button" onClick={resetCuotaForm} className="btn-secondary">
                <X className="h-4 w-4" /> Cancelar
              </button>
            )}
          </div>
          {message && <p className="rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700 md:col-span-2">{message}</p>}
          <input className="input" placeholder="Titulo" value={cuotaForm.titulo} onChange={(e) => setCuotaForm({ ...cuotaForm, titulo: e.target.value })} required />
          <input className="input" type="number" min="0" step="0.01" placeholder="Monto" value={cuotaForm.monto} onChange={(e) => setCuotaForm({ ...cuotaForm, monto: e.target.value })} required />
          <input className="input" type="date" value={cuotaForm.fecha_vencimiento} onChange={(e) => setCuotaForm({ ...cuotaForm, fecha_vencimiento: e.target.value })} required />
          <input className="input" placeholder="Descripcion" value={cuotaForm.descripcion} onChange={(e) => setCuotaForm({ ...cuotaForm, descripcion: e.target.value })} />
          <select className="input" value={cuotaForm.estado} onChange={(e) => setCuotaForm({ ...cuotaForm, estado: e.target.value })}>
            <option value="activa">Activa</option>
            <option value="cerrada">Cerrada</option>
            <option value="cancelada">Cancelada</option>
          </select>
          <button className="btn-primary w-fit">{editingCuota ? 'Guardar cambios' : 'Crear cuota'}</button>
        </form>
      )}
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Table
          title="Cuotas"
          rows={cuotas}
          columns={['titulo', 'monto', 'fecha_vencimiento', 'estado']}
          actions={hasRole('admin') ? (row) => (
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => editCuota(row)} className="btn-secondary px-3" title="Editar cuota">
                <Pencil className="h-4 w-4" />
              </button>
              <button type="button" onClick={() => deleteCuota(row)} className="btn border border-red-200 text-red-600 hover:bg-red-50 px-3" title="Eliminar cuota">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ) : null}
        />
        <PaymentsTable rows={pagos} onStatusChange={hasRole('admin', 'tesorero') ? changePaymentStatus : null} />
        <Table title="Transacciones" rows={transacciones} columns={['tipo', 'categoria', 'monto', 'fecha']} />
      </div>
    </section>
  );
}

function PaymentsTable({ rows, onStatusChange }) {
  return (
    <div className="card overflow-hidden">
      <h2 className="border-b border-slate-200 p-4 font-bold text-neighbor-navy">Pagos reales de cuotas</h2>
      {!rows.length ? <div className="p-4"><EmptyState title="Sin pagos registrados" /></div> : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <tbody>{rows.slice(0, 12).map((row) => (
              <tr key={row.id} className="border-t border-slate-100 align-top">
                <td className="p-3">
                  <p className="font-bold text-neighbor-navy">{row.cuota?.titulo || row.cuota_id}</p>
                  <p className="text-xs text-slate-500">{row.vecino?.nombre || row.vecino_id}</p>
                </td>
                <td className="p-3">{money(row.monto)}</td>
                <td className="p-3">{shortDate(row.fecha_pago)}</td>
                <td className="p-3"><Badge>{row.estado || 'pendiente'}</Badge></td>
                <td className="p-3">
                  {row.comprobante_url ? (
                    <a className="btn-secondary px-3" href={mediaUrl(row.comprobante_url)} target="_blank" rel="noreferrer">
                      <ExternalLink className="h-4 w-4" /> Comprobante
                    </a>
                  ) : <span className="text-xs font-semibold text-slate-400">Sin comprobante</span>}
                </td>
                {onStatusChange && (
                  <td className="p-3">
                    <div className="flex justify-end gap-2">
                      <button type="button" className="btn-secondary px-3 text-green-700" onClick={() => onStatusChange(row, 'verificado')} title="Verificar pago">
                        <CheckCircle className="h-4 w-4" />
                      </button>
                      <button type="button" className="btn border border-red-200 px-3 text-red-600 hover:bg-red-50" onClick={() => onStatusChange(row, 'rechazado')} title="Rechazar pago">
                        <XCircle className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                )}
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Box({ label, value }) {
  return <div className="card p-5"><p className="text-sm font-bold text-slate-500">{label}</p><p className="mt-2 text-3xl font-black text-neighbor-navy">{value}</p></div>;
}

function Table({ title, rows, columns, actions }) {
  return (
    <div className="card overflow-hidden">
      <h2 className="border-b border-slate-200 p-4 font-bold text-neighbor-navy">{title}</h2>
      {!rows.length ? <div className="p-4"><EmptyState /></div> : (
        <table className="w-full text-left text-sm">
          <tbody>{rows.slice(0, 10).map((row) => (
            <tr key={row.id} className="border-t border-slate-100">
              {columns.map((col) => <td key={col} className="p-3">{col.includes('monto') ? money(row[col]) : col.includes('fecha') ? shortDate(row[col]) : row[col]}</td>)}
              {actions && <td className="p-3">{actions(row)}</td>}
            </tr>
          ))}</tbody>
        </table>
      )}
    </div>
  );
}
