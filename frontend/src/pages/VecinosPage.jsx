import { CheckCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { dataService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { roleLabel } from '../lib/utils';

export default function VecinosPage() {
  const { hasRole } = useAuth();
  const [rows, setRows] = useState(null);
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ nombre: '', email: '', telefono: '', direccion: '', documento: '', estado: 'pendiente' });
  const load = () => dataService.vecinos().then(setRows);

  useEffect(() => { load(); }, []);

  async function submit(event) {
    event.preventDefault();
    await dataService.actualizarVecino(editing.id, { ...form, email: form.email || null, telefono: form.telefono || null, documento: form.documento || null });
    setEditing(null);
    load();
  }

  function edit(row) {
    setEditing(row);
    setForm({ nombre: row.nombre || '', email: row.email || '', telefono: row.telefono || '', direccion: row.direccion || '', documento: row.documento || '', estado: row.estado || 'pendiente' });
  }

  async function remove(row) {
    if (!window.confirm(`Dar de baja a "${row.nombre}"?`)) return;
    try {
      await dataService.eliminarVecino(row.id);
      setError('');
      load();
    } catch {
      setError('No se pudo eliminar. Verifica que tu usuario sea admin y que el backend este reiniciado.');
    }
  }

  if (!rows) return <Spinner />;
  return (
    <section>
      <h1 className="page-title">Padron de vecinos</h1>
      {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}
      {hasRole('admin') && editing && (
        <form onSubmit={submit} className="card mt-6 grid gap-4 p-5 md:grid-cols-2">
          <h2 className="font-bold text-neighbor-navy md:col-span-2">Editar vecino</h2>
          <input className="input" placeholder="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required />
          <input className="input" type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="input" placeholder="Telefono" value={form.telefono} onChange={(e) => setForm({ ...form, telefono: e.target.value })} />
          <input className="input" placeholder="Direccion" value={form.direccion} onChange={(e) => setForm({ ...form, direccion: e.target.value })} required />
          <input className="input" placeholder="Documento" value={form.documento} onChange={(e) => setForm({ ...form, documento: e.target.value })} />
          <select className="input" value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })}>
            <option value="pendiente">Pendiente</option>
            <option value="aprobado">Aprobado</option>
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
            <option value="rechazado">Rechazado</option>
            <option value="moroso">Moroso</option>
          </select>
          <div className="flex gap-2">
            <button className="btn-primary">Guardar cambios</button>
            <button type="button" className="btn-secondary" onClick={() => setEditing(null)}>Cancelar</button>
          </div>
        </form>
      )}
      <div className="card mt-6 overflow-hidden">
        {rows.length === 0 ? <EmptyState /> : (
          <table className="w-full text-left text-sm">
            <thead className="bg-neighbor-mist text-neighbor-navy">
              <tr><th className="p-3">Nombre</th><th>Email</th><th>Direccion</th><th>Rol</th><th>Estado</th><th></th></tr>
            </thead>
            <tbody>{rows.map((row) => (
              <tr key={row.id} className="border-t border-slate-100">
                <td className="p-3 font-semibold">{row.nombre}</td><td>{row.email}</td><td>{row.direccion}</td><td>{roleLabel[row.rol] || row.rol}</td><td>{row.rol === 'admin' ? <Badge>Administrador</Badge> : <Badge>{row.estado}</Badge>}</td>
                <td className="p-3">
                  <div className="flex flex-wrap gap-2">
                    {row.estado === 'pendiente' && row.rol !== 'admin' && <button className="btn-secondary" onClick={() => dataService.aprobarVecino(row.id).then(load)}><CheckCircle className="h-4 w-4" /> Aprobar</button>}
                    {hasRole('admin') && row.rol !== 'admin' && (
                      <>
                        <select className="input w-36" value={row.rol} onChange={(e) => dataService.cambiarRolVecino(row.id, e.target.value).then(load)}>
                          <option value="vecino">Vecino</option>
                          <option value="directiva">Vice Presidente</option>
                          <option value="tesorero">Tesorero</option>
                          <option value="vocero">Vocero</option>
                          <option value="secretaria">Secretaria</option>
                        </select>
                        <button className="btn-secondary" onClick={() => edit(row)}>Editar</button>
                        <button className="btn border border-red-200 text-red-600 hover:bg-red-50" onClick={() => remove(row)}>Eliminar</button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}</tbody>
          </table>
        )}
      </div>
    </section>
  );
}
