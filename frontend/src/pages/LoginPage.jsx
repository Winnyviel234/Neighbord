import { Link, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      navigate('/app');
    }
  }, [user, navigate]);

  async function onSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await login(form);
      navigate('/app');
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo iniciar sesion');
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-neighbor-mist px-4">
      <form onSubmit={onSubmit} className="card w-full max-w-md p-7">
        <div className="text-center">
          <img src="/neighbor-logo.png" alt="Neighbord" className="mx-auto h-24 w-24 object-contain" />
          <h1 className="mt-3 text-2xl font-black text-neighbor-navy">Iniciar sesion</h1>
        </div>
        {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}
        <div className="mt-5 space-y-4">
          <label className="block">
            <span className="label">Correo</span>
            <input className="input mt-1" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          </label>
          <label className="block">
            <span className="label">Contrasena</span>
            <input className="input mt-1" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          </label>
          <div className="flex justify-end">
            <Link className="text-sm font-bold text-neighbor-blue hover:text-neighbor-navy" to="/recuperar-contrasena">
              ¿Has olvidado la contraseña?
            </Link>
          </div>
          <button className="btn-primary w-full">Entrar</button>
        </div>
        <p className="mt-5 text-center text-sm text-slate-600">No tienes cuenta? <Link className="font-bold text-neighbor-blue" to="/registro">Registrate</Link></p>
      </form>
    </main>
  );
}
