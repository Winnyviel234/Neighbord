import { useState } from 'react';
import { CreditCard, ExternalLink, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Badge } from '../components/common';
import { dataService } from '../services/api';
import { money } from '../lib/utils';

export default function ProjectContributionPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    concepto: 'Aporte a proyectos comunitarios',
    monto: '50.00',
    fecha_pago: new Date().toISOString().slice(0, 10)
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!form.monto || Number(form.monto) <= 0) {
      setError('Ingresa un monto válido para tu aporte.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const response = await dataService.checkoutProjectContribution({
        concepto: form.concepto,
        monto: Number(form.monto),
        fecha_pago: form.fecha_pago
      });
      setResult(response);
    } catch (err) {
      setError(err?.response?.data?.detail || 'No se pudo iniciar el pago. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="page-title">Aporte a proyectos</h1>
          <p className="mt-2 max-w-3xl text-sm font-semibold leading-6 text-slate-600">
            Realiza una contribución económica segura a iniciativas comunitarias y apoya el trabajo conjunto del barrio.
          </p>
        </div>
        <Badge>Pago Strike</Badge>
      </div>

      {error && (
        <div className="mt-6 rounded-xl bg-red-50 p-4 text-sm font-semibold text-red-700">{error}</div>
      )}

      {result ? (
        <div className="card mt-6 p-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-neighbor-green">Pago iniciado</p>
              <h2 className="mt-3 text-3xl font-black text-neighbor-navy">Gracias por tu aporte</h2>
              <p className="mt-2 text-sm text-slate-600">Tu contribución está lista para completarse con el enlace de pago de Strike.</p>
            </div>
            <Zap className="h-12 w-12 text-neighbor-blue" />
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Concepto</p>
              <p className="mt-2 text-base font-bold text-neighbor-navy">{result.description}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Monto</p>
              <p className="mt-2 text-3xl font-black text-neighbor-navy">{money(result.amount)}</p>
            </div>
          </div>

          {result.lnurl ? (
            <a
              href={result.lnurl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 mt-6 rounded-full bg-neighbor-blue px-5 py-3 text-sm font-bold text-white shadow-lg shadow-neighbor-blue/20 hover:bg-neighbor-navy transition"
            >
              <ExternalLink className="h-4 w-4" /> Ir a Strike para pagar
            </a>
          ) : null}

          <div className="mt-6 rounded-3xl border border-slate-200 bg-white p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Código de pago</p>
            <textarea
              readOnly
              value={result.payment_request}
              className="input mt-3 min-h-[120px] w-full resize-none bg-slate-50 text-sm"
            />
            <p className="mt-2 text-sm text-slate-500">Copia este código y utilízalo en tu app de Strike o compatible con Lightning.</p>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button className="btn-primary" onClick={() => navigate('/app')}>Volver al panel</button>
            <button className="btn-secondary" onClick={() => setResult(null)}>Crear otro aporte</button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="card mt-6 grid gap-4 p-6 md:grid-cols-2">
          <div className="md:col-span-2">
            <h2 className="font-bold text-neighbor-navy">Registro de aporte</h2>
            <p className="mt-1 text-sm text-slate-500">Crea una factura de pago para apoyar proyectos comunitarios con Strike.</p>
          </div>

          <label className="block">
            <span className="text-sm font-semibold text-slate-700">Concepto</span>
            <input
              className="input mt-2 w-full"
              value={form.concepto}
              onChange={(e) => setForm({ ...form, concepto: e.target.value })}
              required
            />
          </label>

          <label className="block">
            <span className="text-sm font-semibold text-slate-700">Monto (USD)</span>
            <input
              className="input mt-2 w-full"
              type="number"
              min="1"
              step="0.01"
              value={form.monto}
              onChange={(e) => setForm({ ...form, monto: e.target.value })}
              required
            />
          </label>

          <label className="block md:col-span-2">
            <span className="text-sm font-semibold text-slate-700">Fecha de aporte</span>
            <input
              className="input mt-2 w-full"
              type="date"
              value={form.fecha_pago}
              onChange={(e) => setForm({ ...form, fecha_pago: e.target.value })}
              required
            />
          </label>

          <div className="md:col-span-2 flex flex-wrap gap-3">
            <button type="submit" className="btn-primary inline-flex items-center gap-2" disabled={loading}>
              {loading ? 'Generando pago...' : 'Generar pago'}
              <CreditCard className="h-4 w-4" />
            </button>
            <button type="button" className="btn-secondary" onClick={() => navigate('/app')} disabled={loading}>
              Cancelar
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
