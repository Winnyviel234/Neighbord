import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useState } from 'react';
import { authService } from '../services/api';

export default function ResetPasswordPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    setMessage('');
    setError('');
    if (!token) {
      setError('El enlace no tiene token de recuperación.');
      return;
    }
    if (password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres.');
      return;
    }
    if (password !== confirm) {
      setError('Las contraseñas no coinciden.');
      return;
    }

    setLoading(true);
    try {
      const result = await authService.confirmPasswordReset({ token, password_nueva: password });
      setMessage(result.message || 'Contraseña actualizada.');
      setTimeout(() => navigate('/login'), 1800);
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo cambiar la contraseña.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-neighbor-mist px-4">
      <form onSubmit={onSubmit} className="card w-full max-w-md p-7">
        <div className="text-center">
          <img src="/neighbor-logo.png" alt="Neighbord" className="mx-auto h-20 w-20 object-contain" />
          <h1 className="mt-3 text-2xl font-black text-neighbor-navy">Crear nueva contraseña</h1>
          <p className="mt-2 text-sm font-semibold text-slate-500">Usa una clave privada y diferente a la anterior.</p>
        </div>
        {message && <p className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">{message}</p>}
        {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}
        <div className="mt-5 space-y-4">
          <input className="input" type="password" placeholder="Nueva contraseña" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
          <input className="input" type="password" placeholder="Confirmar contraseña" value={confirm} onChange={(e) => setConfirm(e.target.value)} required minLength={6} />
          <button className="btn-primary w-full" disabled={loading || !token}>{loading ? 'Guardando...' : 'Actualizar contraseña'}</button>
        </div>
        <p className="mt-5 text-center text-sm text-slate-600"><Link className="font-bold text-neighbor-blue" to="/login">Volver al inicio de sesión</Link></p>
      </form>
    </main>
  );
}
