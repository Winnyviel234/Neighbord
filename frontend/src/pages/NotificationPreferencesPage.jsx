import { Bell, Mail, AlertCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { notificationService } from '../services/api';

export default function NotificationPreferencesPage() {
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const data = await notificationService.getPreferences();
      setPreferences(data || getDefaultPreferences());
    } catch (err) {
      setPreferences(getDefaultPreferences());
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getDefaultPreferences = () => ({
    votaciones: true,
    reuniones: true,
    pagos: true,
    solicitudes: true,
    comunicados: true,
    directiva: true,
    chat: true,
    email_votaciones: false,
    email_reuniones: false,
    email_pagos: false,
    email_solicitudes: false,
    email_comunicados: false,
    email_directiva: false,
    email_chat: false
  });

  const handleSave = async () => {
    if (!preferences) return;

    try {
      setSaving(true);
      setError('');
      setSuccess('');

      await notificationService.updatePreferences(preferences);
      setSuccess('Preferencias guardadas correctamente');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Error al guardar preferencias');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const togglePreference = (key) => {
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  if (loading) {
    return (
      <section>
        <h1 className="page-title">Preferencias de Notificaciones</h1>
        <div className="mt-6 flex items-center justify-center">
          <p className="text-slate-500">Cargando preferencias...</p>
        </div>
      </section>
    );
  }

  return (
    <section>
      <div>
        <h1 className="page-title">Preferencias de Notificaciones</h1>
        <p className="mt-1 text-sm font-semibold text-slate-500">
          Personaliza cómo deseas recibir notificaciones de la comunidad
        </p>
      </div>

      {error && (
        <div className="mt-6 rounded-lg bg-red-50 p-4 border border-red-200 flex gap-3">
          <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {success && (
        <div className="mt-6 rounded-lg bg-green-50 p-4 border border-green-200">
          <p className="text-sm text-green-700">✓ {success}</p>
        </div>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        {/* Notificaciones en app */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Bell className="h-6 w-6 text-neighbor-blue" />
            <h2 className="text-lg font-bold text-neighbor-navy">Notificaciones en la App</h2>
          </div>

          <div className="space-y-4">
            {[
              { key: 'votaciones', label: 'Votaciones' },
              { key: 'reuniones', label: 'Reuniones' },
              { key: 'pagos', label: 'Pagos' },
              { key: 'solicitudes', label: 'Solicitudes' },
              { key: 'comunicados', label: 'Comunicados' },
              { key: 'directiva', label: 'Directiva' },
              { key: 'chat', label: 'Chat' }
            ].map(item => (
              <label key={item.key} className="flex items-center gap-3 cursor-pointer p-2 hover:bg-slate-50 rounded">
                <input
                  type="checkbox"
                  checked={preferences[item.key] || false}
                  onChange={() => togglePreference(item.key)}
                  className="w-4 h-4 rounded border-slate-300"
                />
                <span className="text-sm font-medium text-slate-700">{item.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Notificaciones por email */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Mail className="h-6 w-6 text-neighbor-green" />
            <h2 className="text-lg font-bold text-neighbor-navy">Notificaciones por Email</h2>
          </div>

          <div className="space-y-4">
            {[
              { key: 'email_votaciones', label: 'Votaciones' },
              { key: 'email_reuniones', label: 'Reuniones' },
              { key: 'email_pagos', label: 'Pagos' },
              { key: 'email_solicitudes', label: 'Solicitudes' },
              { key: 'email_comunicados', label: 'Comunicados' },
              { key: 'email_directiva', label: 'Directiva' },
              { key: 'email_chat', label: 'Chat' }
            ].map(item => (
              <label key={item.key} className="flex items-center gap-3 cursor-pointer p-2 hover:bg-slate-50 rounded">
                <input
                  type="checkbox"
                  checked={preferences[item.key] || false}
                  onChange={() => togglePreference(item.key)}
                  className="w-4 h-4 rounded border-slate-300"
                />
                <span className="text-sm font-medium text-slate-700">{item.label}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Información */}
      <div className="mt-6 rounded-lg bg-blue-50 p-4 border border-blue-200">
        <p className="text-sm text-blue-700">
          <strong>💡 Nota:</strong> Puedes desactivar notificaciones sin que afecte tu acceso a la aplicación. 
          Las notificaciones por email requieren que hayas compartido tu dirección de correo en tu perfil.
        </p>
      </div>

      <div className="mt-6 flex gap-3">
        <button onClick={loadPreferences} disabled={loading || saving} className="btn-secondary">
          Cancelar
        </button>
        <button onClick={handleSave} disabled={saving || loading} className="btn-primary">
          {saving ? 'Guardando...' : 'Guardar cambios'}
        </button>
      </div>
    </section>
  );
}
