import { Loader2 } from 'lucide-react';

export function Spinner({ label = 'Cargando...' }) {
  return (
    <div className="flex min-h-40 items-center justify-center gap-3 text-neighbor-navy">
      <Loader2 className="h-5 w-5 animate-spin" />
      <span className="text-sm font-medium">{label}</span>
    </div>
  );
}

export function StatCard({ icon: Icon, label, value, tone = 'blue' }) {
  const tones = {
    blue: 'bg-neighbor-blue/10 text-neighbor-blue',
    green: 'bg-neighbor-green/10 text-neighbor-green',
    sky: 'bg-neighbor-sky/10 text-neighbor-sky',
    navy: 'bg-neighbor-navy/10 text-neighbor-navy'
  };
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-bold text-neighbor-navy">{value}</p>
        </div>
        {Icon && <div className={`rounded-lg p-3 ${tones[tone]}`}><Icon className="h-6 w-6" /></div>}
      </div>
    </div>
  );
}

export function EmptyState({ title = 'Sin datos', text = 'Cuando existan registros aparecerán aquí.' }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center">
      <p className="font-semibold text-neighbor-navy">{title}</p>
      <p className="mt-1 text-sm text-slate-500">{text}</p>
    </div>
  );
}

export function Badge({ children, className = '' }) {
  return <span className={`rounded-full bg-neighbor-mist px-3 py-1 text-xs font-bold text-neighbor-navy ${className}`}>{children}</span>;
}
