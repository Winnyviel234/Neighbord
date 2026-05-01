import { useEffect, useMemo, useState } from 'react';
import { CreditCard, ReceiptText } from 'lucide-react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { money, shortDate } from '../lib/utils';
import { dataService, mediaUrl } from '../services/api';

export default function PagosPage() {
  const [data, setData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({ monto: '', fecha_pago: new Date().toISOString().slice(0, 10), metodo: 'transferencia', referencia: '', comprobante: null });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const load = () => dataService.misPagos().then(setData).catch(() => {
    setData({ cuotas: [], pagos: [] });
    setError('No se pudieron cargar pagos reales. Revisa que el backend este conectado.');
  });

  useEffect(() => { load(); }, []);

  const pagosByCuota = useMemo(() => {
    const map = new Map();
    (data?.pagos || []).forEach((pago) => map.set(pago.cuota_id, pago));
    return map;
  }, [data]);

  function startPayment(cuota) {
    setSelected(cuota);
    setForm({ monto: cuota.monto ?? '', fecha_pago: new Date().toISOString().slice(0, 10), metodo: 'transferencia', referencia: '', comprobante: null });
    setMessage('');
    setError('');
  }

  async function submit(event) {
    event.preventDefault();
    try {
      await dataService.pagarMiCuota(selected.id, {
        ...form,
        monto: Number(form.monto),
        referencia: form.referencia || null
      });
      setSelected(null);
      event.target.reset();
      setMessage('Pago registrado con comprobante. La directiva podra verificarlo en Finanzas.');
      setError('');
      load();
    } catch {
      setError('No se pudo registrar el pago. Revisa los datos e intenta nuevamente.');
    }
  }

  if (!data) return <Spinner label="Cargando pagos..." />;

  return (
    <section>
      <h1 className="page-title">Pagos</h1>
      <p className="mt-2 max-w-3xl text-sm font-semibold leading-6 text-slate-600">
        Aqui registras el pago de tus cuotas. Usa transferencia, efectivo u otro metodo y guarda la referencia para que administracion pueda verificarlo.
      </p>

      {message && <p className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">{message}</p>}
      {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}

      {selected && (
        <form onSubmit={submit} className="card mt-6 grid gap-4 p-5 md:grid-cols-2">
          <div className="md:col-span-2">
            <h2 className="font-bold text-neighbor-navy">Registrar pago: {selected.titulo}</h2>
            <p className="mt-1 text-sm text-slate-500">Monto sugerido: {money(selected.monto)}</p>
          </div>
          <input className="input" type="number" min="0" step="0.01" placeholder="Monto pagado" value={form.monto} onChange={(e) => setForm({ ...form, monto: e.target.value })} required />
          <input className="input" type="date" value={form.fecha_pago} onChange={(e) => setForm({ ...form, fecha_pago: e.target.value })} required />
          <select className="input" value={form.metodo} onChange={(e) => setForm({ ...form, metodo: e.target.value })}>
            <option value="transferencia">Transferencia</option>
            <option value="efectivo">Efectivo</option>
            <option value="deposito">Deposito</option>
            <option value="otro">Otro</option>
          </select>
          <input className="input" placeholder="Referencia, comprobante o nota" value={form.referencia} onChange={(e) => setForm({ ...form, referencia: e.target.value })} />
          <div className="md:col-span-2">
            <label className="label">Comprobante real del pago</label>
            <input className="input mt-1" type="file" accept="image/*,.pdf" onChange={(e) => setForm({ ...form, comprobante: e.target.files[0] || null })} />
            <p className="mt-1 text-xs font-semibold text-slate-500">Sube captura, foto o PDF de transferencia/deposito/recibo.</p>
          </div>
          <div className="flex gap-2 md:col-span-2">
            <button className="btn-primary"><CreditCard className="h-4 w-4" /> Registrar pago</button>
            <button type="button" className="btn-secondary" onClick={() => setSelected(null)}>Cancelar</button>
          </div>
        </form>
      )}

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {data.cuotas.length ? data.cuotas.map((cuota) => {
          const pago = pagosByCuota.get(cuota.id);
          return (
            <article key={cuota.id} className="card p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-black text-neighbor-navy">{cuota.titulo}</h2>
                  <p className="mt-1 text-sm text-slate-500">Vence: {shortDate(cuota.fecha_vencimiento)}</p>
                </div>
                <Badge>{pago ? pago.estado || 'pendiente' : cuota.estado}</Badge>
              </div>
              <p className="mt-4 text-3xl font-black text-neighbor-navy">{money(cuota.monto)}</p>
              {cuota.descripcion && <p className="mt-2 text-sm leading-6 text-slate-600">{cuota.descripcion}</p>}
              {pago ? (
                <div className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">
                  <ReceiptText className="mr-2 inline h-4 w-4" />
                  Pago registrado el {shortDate(pago.fecha_pago)} por {money(pago.monto)}
                  {pago.comprobante_url && (
                    <a href={mediaUrl(pago.comprobante_url)} target="_blank" rel="noreferrer" className="ml-2 underline">
                      Ver comprobante
                    </a>
                  )}
                </div>
              ) : (
                <button className="btn-primary mt-5" onClick={() => startPayment(cuota)}>Pagar cuota</button>
              )}
            </article>
          );
        }) : <EmptyState title="No hay cuotas disponibles" />}
      </div>
    </section>
  );
}
