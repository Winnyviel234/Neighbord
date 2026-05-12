import { Link } from 'react-router-dom';
import { useState } from 'react';
import { authService } from '../services/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    setMessage('');
    setError('');
    setLoading(true);
    try {
      const result = await authService.requestPasswordReset({ email });
      setMessage(result.message || 'Revisa tu correo para continuar.');
      if (result.email_configured === false) {
        setError(result.detail || 'El correo SMTP no esta configurado.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo procesar la solicitud.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-neighbor-mist px-4">
      <form onSubmit={onSubmit} className="card w-full max-w-md p-7">
        <div className="text-center">
          <img src="/neighbor-logo.png" alt="Neighbord" className="mx-auto h-20 w-20 object-contain" />
          <h1 className="mt-3 text-2xl font-black text-neighbor-navy">Recuperar contrasena</h1>
          <p className="mt-2 text-sm font-semibold text-slate-500">Te enviaremos un enlace seguro que vence en 30 minutos.</p>
        </div>
        {message && <p className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">{message}</p>}
        {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}
        <div className="mt-5 space-y-4">
          <label className="block">
            <span className="label">Correo registrado</span>
            <input className="input mt-1" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <button className="btn-primary w-full" disabled={loading}>{loading ? 'Enviando...' : 'Enviar enlace'}</button>
        </div>
        <p className="mt-5 text-center text-sm text-slate-600"><Link className="font-bold text-neighbor-blue" to="/login">Volver al inicio de sesion</Link></p>
      </form>
    </main>
  );
}
