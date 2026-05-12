import { Link, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/api';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_MIN_DIGITS = 8;
const PHONE_MAX_DIGITS = 15;

const cleanInput = (value) => (typeof value === 'string' ? value.trim().replace(/<[^>]*>/g, '') : '');
const phoneDigits = (value) => String(value || '').replace(/\D/g, '');
const normalizePhoneInput = (value) => {
  const raw = String(value || '').trim();
  const hasPlus = raw.startsWith('+');
  const digits = phoneDigits(raw).slice(0, PHONE_MAX_DIGITS);
  if (!digits) return hasPlus ? '+' : '';
  return `${hasPlus ? '+' : ''}${digits}`;
};
const getPhoneError = (value) => {
  const trimmed = String(value || '').trim();
  if (!trimmed) return '';
  const digits = phoneDigits(trimmed);
  if (trimmed.includes('+') && !trimmed.startsWith('+')) return 'El signo + solo puede ir al inicio.';
  if (digits.length < PHONE_MIN_DIGITS) return `Faltan ${PHONE_MIN_DIGITS - digits.length} digitos.`;
  if (digits.length > PHONE_MAX_DIGITS) return `Maximo ${PHONE_MAX_DIGITS} digitos.`;
  return '';
};

export default function RegisterPage() {
  const { register, user } = useAuth();
  const navigate = useNavigate();
  const [sectors, setSectors] = useState([]);
  const [form, setForm] = useState({ nombre: '', email: '', password: '', telefono: '', direccion: '', documento: '', sector: '' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const telefonoDigits = phoneDigits(form.telefono).length;
  const telefonoError = getPhoneError(form.telefono);

  useEffect(() => {
    if (user && ['aprobado', 'activo'].includes(user.estado)) {
      navigate('/app');
    }
  }, [user, navigate]);

  useEffect(() => {
    authService.getSectors()
      .then((data) => setSectors(Array.isArray(data) ? data : []))
      .catch(() => setSectors([]));
  }, []);

  async function onSubmit(event) {
    event.preventDefault();
    setError('');
    setMessage('');

    const payload = {
      nombre: cleanInput(form.nombre),
      email: cleanInput(form.email).toLowerCase(),
      password: form.password,
      telefono: cleanInput(form.telefono),
      direccion: cleanInput(form.direccion),
      documento: cleanInput(form.documento),
      sector: cleanInput(form.sector)
    };

    if (!payload.nombre || !payload.email || !payload.password || !payload.direccion || !payload.sector) {
      setError('Completa todos los campos obligatorios antes de continuar.');
      return;
    }

    if (!EMAIL_REGEX.test(payload.email)) {
      setError('Ingresa una direccion de correo valida.');
      return;
    }

    if (payload.password.length < 6) {
      setError('La contrasena debe tener al menos 6 caracteres.');
      return;
    }

    const phoneValidationError = getPhoneError(payload.telefono);
    if (phoneValidationError) {
      setError(`Telefono invalido: ${phoneValidationError}`);
      return;
    }

    try {
      const response = await register(payload);
      setMessage(response.message || 'Registro enviado. Espera a que un administrador apruebe tu cuenta antes de iniciar sesión.');
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo registrar. Revisa los datos e intenta nuevamente.');
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-neighbor-mist px-4 py-8">
      <form onSubmit={onSubmit} className="card w-full max-w-2xl p-7">
        <div className="flex items-center gap-4">
          <img src="/neighbor-logo.png" alt="Neighbord" className="h-20 w-20 object-contain" />
          <div>
            <h1 className="text-2xl font-black text-neighbor-navy">Registro vecinal</h1>
            <p className="text-sm text-slate-600">Tu registro fue recibido correctamente. Te notificaremos cuando tu cuenta esté lista para usar.</p>
          </div>
        </div>

        {message && <p className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">{message}</p>}
        {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          {[
            ['nombre', 'Nombre completo'],
            ['email', 'Correo'],
            ['password', 'Contrasena'],
            ['telefono', 'Telefono'],
            ['direccion', 'Direccion'],
            ['documento', 'Documento de identidad']
          ].map(([key, label]) => (
            <label key={key} className="block">
              <span className="label">{label}</span>
              <input
                className={`input mt-1 ${key === 'telefono' && telefonoError ? 'border-red-300 focus:border-red-500' : ''}`}
                type={key === 'password' ? 'password' : key === 'email' ? 'email' : key === 'telefono' ? 'tel' : 'text'}
                inputMode={key === 'telefono' ? 'tel' : undefined}
                placeholder={key === 'documento' ? 'Cédula, DNI o pasaporte' : undefined}
                value={form[key]}
                onChange={(e) => setForm({ ...form, [key]: key === 'telefono' ? normalizePhoneInput(e.target.value) : e.target.value })}
                required={['nombre', 'email', 'password', 'direccion'].includes(key)}
              />
              {key === 'documento' && (
                <span className="mt-1 block text-xs text-slate-500">
                  Ingresa tu número de identidad oficial (cédula, DNI o pasaporte).
                </span>
              )}
              {key === 'telefono' && (
                <span className={`mt-1 block text-xs font-semibold ${telefonoError ? 'text-red-600' : 'text-slate-500'}`}>
                  {telefonoError || `${telefonoDigits}/${PHONE_MAX_DIGITS} digitos`}
                </span>
              )}
            </label>
          ))}

          <label className="block">
            <span className="label">Sector</span>
            {sectors.length > 0 ? (
              <select
                className="input mt-1"
                value={form.sector}
                onChange={(e) => setForm({ ...form, sector: e.target.value })}
                required
              >
                <option value="">Selecciona un sector</option>
                {sectors.map((sector) => (
                  <option key={sector.id} value={sector.id}>{sector.name}</option>
                ))}
              </select>
            ) : (
              <input
                className="input mt-1"
                value={form.sector}
                onChange={(e) => setForm({ ...form, sector: e.target.value })}
                required
              />
            )}
          </label>
        </div>

        <button className="btn-primary mt-6 w-full" disabled={Boolean(telefonoError)}>Enviar registro</button>
        <p className="mt-5 text-center text-sm text-slate-600">
          <Link className="font-bold text-neighbor-blue" to="/login">Volver al login</Link>
        </p>
      </form>
    </main>
  );
}
