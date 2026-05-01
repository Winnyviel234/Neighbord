import { useEffect, useState } from 'react';
import { KeyRound, ReceiptText, UserRound, Vote } from 'lucide-react';
import { EmptyState, Spinner } from '../components/common';
import { useAuth } from '../context/AuthContext';
import { dataService } from '../services/api';
import { money, shortDate } from '../lib/utils';

export default function PerfilPage() {
  const { user, updateProfile, changePassword } = useAuth();
  const [history, setHistory] = useState(null);
  const [profile, setProfile] = useState({ nombre: user?.nombre || '', telefono: user?.telefono || '', direccion: user?.direccion || '', documento: user?.documento || '' });
  const [password, setPassword] = useState({ password_actual: '', password_nueva: '' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    dataService.dashboard().then(setHistory).catch(() => setHistory({ reportes_recientes: [], pagos_recientes: [], votaciones_activas: [] }));
  }, []);

  async function saveProfile(event) {
    event.preventDefault();
    try {
      await updateProfile(profile);
      setMessage('Perfil actualizado.');
      setError('');
    } catch {
      setError('No se pudo actualizar el perfil.');
    }
  }

  async function savePassword(event) {
    event.preventDefault();
    try {
      await changePassword(password);
      setPassword({ password_actual: '', password_nueva: '' });
      setMessage('Contrasena actualizada.');
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo cambiar la contrasena.');
    }
  }

  if (!history) return <Spinner label="Cargando perfil..." />;

  return (
    <section>
      <h1 className="page-title">Perfil de usuario</h1>
      {message && <p className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">{message}</p>}
      {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <form onSubmit={saveProfile} className="card grid gap-4 p-5">
          <h2 className="flex items-center gap-2 font-black text-neighbor-navy"><UserRound className="h-5 w-5 text-neighbor-green" /> Datos personales</h2>
          <input className="input" placeholder="Nombre" value={profile.nombre} onChange={(e) => setProfile({ ...profile, nombre: e.target.value })} required />
          <input className="input" placeholder="Telefono" value={profile.telefono} onChange={(e) => setProfile({ ...profile, telefono: e.target.value })} />
          <input className="input" placeholder="Direccion" value={profile.direccion} onChange={(e) => setProfile({ ...profile, direccion: e.target.value })} />
          <input className="input" placeholder="Documento" value={profile.documento} onChange={(e) => setProfile({ ...profile, documento: e.target.value })} />
          <button className="btn-primary w-fit">Guardar datos</button>
        </form>

        <form onSubmit={savePassword} className="card grid gap-4 p-5">
          <h2 className="flex items-center gap-2 font-black text-neighbor-navy"><KeyRound className="h-5 w-5 text-neighbor-green" /> Cambiar contrasena</h2>
          <input className="input" type="password" placeholder="Contrasena actual" value={password.password_actual} onChange={(e) => setPassword({ ...password, password_actual: e.target.value })} required />
          <input className="input" type="password" placeholder="Nueva contrasena" value={password.password_nueva} onChange={(e) => setPassword({ ...password, password_nueva: e.target.value })} minLength={6} required />
          <button className="btn-primary w-fit">Actualizar contrasena</button>
        </form>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <History title="Mis reportes" items={history.reportes_recientes} render={(item) => `${item.estado || 'abierta'} - ${item.descripcion}`} />
        <History title="Mis pagos" items={history.pagos_recientes} icon={ReceiptText} render={(item) => `${money(item.monto)} - ${shortDate(item.fecha_pago)}`} />
        <History title="Votaciones disponibles" items={history.votaciones_activas} icon={Vote} render={(item) => item.descripcion || 'Activa'} />
      </div>
    </section>
  );
}

function History({ title, items, render }) {
  return (
    <section className="card p-5">
      <h2 className="font-black text-neighbor-navy">{title}</h2>
      <div className="mt-4 space-y-3">
        {items?.length ? items.map((item) => (
          <article key={item.id} className="rounded-md border border-slate-100 p-3">
            <p className="font-bold text-neighbor-navy">{item.titulo || item.concepto || item.id}</p>
            <p className="mt-1 text-sm text-slate-600">{render(item)}</p>
          </article>
        )) : <EmptyState />}
      </div>
    </section>
  );
}
