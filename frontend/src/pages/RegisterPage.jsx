import { Link } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const { register } = useAuth();
  const [form, setForm] = useState({ nombre: '', email: '', password: '', telefono: '', direccion: '', documento: '' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  async function onSubmit(event) {
    event.preventDefault();
    setError('');
    setMessage('');
    try {
      const response = await register(form);
      setMessage(response.message);
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo registrar');
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-neighbor-mist px-4 py-8">
      <form onSubmit={onSubmit} className="card w-full max-w-2xl p-7">
        <div className="flex items-center gap-4">
          <img src="/neighbor-logo.png" alt="Neighbord" className="h-20 w-20 object-contain" />
          <div><h1 className="text-2xl font-black text-neighbor-navy">Registro vecinal</h1><p className="text-sm text-slate-600">Tu cuenta queda pendiente hasta aprobación.</p></div>
        </div>
        {message && <p className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">{message}</p>}
        {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          {[
            ['nombre', 'Nombre completo'],
            ['email', 'Correo'],
            ['password', 'Contraseña'],
            ['telefono', 'Teléfono'],
            ['direccion', 'Dirección'],
            ['documento', 'Documento']
          ].map(([key, label]) => (
            <label key={key} className="block">
              <span className="label">{label}</span>
              <input className="input mt-1" type={key === 'password' ? 'password' : key === 'email' ? 'email' : 'text'} value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} required={['nombre', 'email', 'password', 'direccion'].includes(key)} />
            </label>
          ))}
        </div>
        <button className="btn-primary mt-6 w-full">Enviar registro</button>
        <p className="mt-5 text-center text-sm text-slate-600"><Link className="font-bold text-neighbor-blue" to="/login">Volver al login</Link></p>
      </form>
    </main>
  );
}

