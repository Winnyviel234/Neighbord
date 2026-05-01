import { useEffect, useState } from 'react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { dateTime } from '../lib/utils';
import { dataService, mediaUrl } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function DirectivaPage() {
  const { hasRole } = useAuth();
  const [directiva, setDirectiva] = useState(null);
  const [reuniones, setReuniones] = useState(null);
  const [form, setForm] = useState({ titulo: '', descripcion: '', fecha: '', lugar: '', tipo: 'directiva', estado: 'programada', imagen: null });
  const [preview, setPreview] = useState(null);
  const [member, setMember] = useState({ nombre: '', email: '', telefono: '', cargo: 'presidente', periodo: '2026-2027', activo: true, imagen: null });
  const [memberPreview, setMemberPreview] = useState(null);
  const [editingMember, setEditingMember] = useState(null);

  const load = () => {
    dataService.directiva().then(setDirectiva);
    dataService.reunionesDirectiva().then(setReuniones);
  };

  useEffect(() => { load(); }, []);

  function handleImageChange(e) {
    const file = e.target.files[0];
    if (file) {
      setForm({ ...form, imagen: file });
      setPreview(URL.createObjectURL(file));
    }
  }

  function handleMemberImageChange(e) {
    const file = e.target.files[0];
    if (file) {
      setMember({ ...member, imagen: file });
      setMemberPreview(URL.createObjectURL(file));
    }
  }

  async function createMeeting(event) {
    event.preventDefault();
    if (!form.fecha || !form.titulo || !form.lugar) {
      alert('Por favor completa todos los campos requeridos');
      return;
    }
    
    let fechaISO;
    try {
      const fecha = new Date(form.fecha);
      if (isNaN(fecha.getTime())) {
        throw new Error('Invalid date');
      }
      fechaISO = fecha.toISOString();
    } catch {
      alert('Formato de fecha inválido');
      return;
    }
    
    const payload = { ...form, fecha: fechaISO, imagen: form.imagen };
    await dataService.crearReunion(payload);
    setForm({ titulo: '', descripcion: '', fecha: '', lugar: '', tipo: 'directiva', estado: 'programada', imagen: null });
    setPreview(null);
    load();
  }

  async function createMember(event) {
    event.preventDefault();
    const payload = {
      ...member,
      email: member.email || null,
      telefono: member.telefono || null,
      imagen: member.imagen
    };
    if (editingMember) await dataService.actualizarDirectivo(editingMember.id, payload);
    else await dataService.crearDirectivo(payload);
    setEditingMember(null);
    setMember({ nombre: '', email: '', telefono: '', cargo: 'presidente', periodo: '2026-2027', activo: true, imagen: null });
    setMemberPreview(null);
    load();
  }

  function editMember(item) {
    setEditingMember(item);
    setMember({ nombre: item.nombre || '', email: item.email || '', telefono: item.telefono || '', cargo: item.cargo || 'presidente', periodo: item.periodo || '2026-2027', activo: item.activo ?? true, imagen: null });
    setMemberPreview(mediaUrl(item.imagen_url) || null);
  }

  async function removeMember(item) {
    if (!window.confirm(`Eliminar a "${item.nombre}" de la directiva?`)) return;
    await dataService.eliminarDirectivo(item.id);
    load();
  }

  if (!directiva || !reuniones) return <Spinner />;

  return (
    <section>
      <h1 className="page-title">Directiva</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {directiva.length ? directiva.map((item) => (
          <article key={item.id} className="card p-5">
            {item.imagen_url && <img src={mediaUrl(item.imagen_url)} alt={item.nombre} className="mb-3 h-32 w-full rounded-md object-cover" />}
            <Badge>{cargoLabel(item.cargo)}</Badge>
            <h2 className="mt-3 font-black text-neighbor-navy">{item.nombre}</h2>
            <p className="mt-1 text-sm text-slate-600">{item.periodo}</p>
            <p className="mt-2 text-sm font-semibold text-neighbor-blue">{item.email}</p>
            {hasRole('admin') && <div className="mt-4 flex gap-2"><button className="btn-secondary" onClick={() => editMember(item)}>Editar</button><button className="btn border border-red-200 text-red-600 hover:bg-red-50" onClick={() => removeMember(item)}>Eliminar</button></div>}
          </article>
        )) : <EmptyState title="Directiva sin registrar" />}
      </div>

      {hasRole('admin') && (
        <form onSubmit={createMember} className="card mt-8 grid gap-4 p-5 md:grid-cols-2">
          <h2 className="font-bold text-neighbor-navy md:col-span-2">{editingMember ? 'Editar miembro de directiva' : 'Registrar miembro de directiva'}</h2>
          <input className="input" placeholder="Nombre" value={member.nombre} onChange={(e) => setMember({ ...member, nombre: e.target.value })} required />
          <select className="input" value={member.cargo} onChange={(e) => setMember({ ...member, cargo: e.target.value })}>
            <option value="presidente">Presidente</option>
            <option value="vice_presidente">Vice presidente</option>
            <option value="secretario">Secretaria / Secretario</option>
            <option value="tesorero">Tesorero</option>
            <option value="vocal">Vocal</option>
          </select>
          <input className="input" type="email" placeholder="Correo" value={member.email} onChange={(e) => setMember({ ...member, email: e.target.value })} />
          <input className="input" placeholder="Telefono" value={member.telefono} onChange={(e) => setMember({ ...member, telefono: e.target.value })} />
          <input className="input" placeholder="Periodo" value={member.periodo} onChange={(e) => setMember({ ...member, periodo: e.target.value })} required />
          <div className="md:col-span-2">
            <label className="label">Imagen (opcional)</label>
            <input type="file" accept="image/*" onChange={handleMemberImageChange} className="input" />
            {memberPreview && <img src={memberPreview} alt="Preview" className="mt-2 h-32 w-auto rounded-md object-cover" />}
          </div>
          <div className="flex gap-2">
            <button className="btn-primary w-fit">{editingMember ? 'Guardar cambios' : 'Guardar miembro'}</button>
            {editingMember && <button type="button" className="btn-secondary" onClick={() => { setEditingMember(null); setMember({ nombre: '', email: '', telefono: '', cargo: 'presidente', periodo: '2026-2027', activo: true, imagen: null }); setMemberPreview(null); }}>Cancelar</button>}
          </div>
        </form>
      )}

      {hasRole('admin', 'directiva') && (
        <form onSubmit={createMeeting} className="card mt-8 grid gap-4 p-5 md:grid-cols-2">
          <h2 className="font-bold text-neighbor-navy md:col-span-2">Nueva reunion de directiva</h2>
          <input className="input" placeholder="Titulo" value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} required />
          <input className="input" placeholder="Lugar" value={form.lugar} onChange={(e) => setForm({ ...form, lugar: e.target.value })} required />
          <input className="input" type="datetime-local" value={form.fecha} onChange={(e) => setForm({ ...form, fecha: e.target.value })} required />
          <textarea className="input min-h-24 md:col-span-2" placeholder="Descripcion" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          <div className="md:col-span-2">
            <label className="label">Imagen (opcional)</label>
            <input type="file" accept="image/*" onChange={handleImageChange} className="input" />
            {preview && <img src={preview} alt="Preview" className="mt-2 h-32 w-auto rounded-md object-cover" />}
          </div>
          <button className="btn-primary w-fit">Crear reunion</button>
        </form>
      )}

      <div className="mt-8">
        <h2 className="text-xl font-black text-neighbor-navy">Reuniones internas</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {reuniones.length ? reuniones.map((item) => (
            <article key={item.id} className="card p-5">
              {item.imagen_url && <img src={mediaUrl(item.imagen_url)} alt={item.titulo} className="mb-3 h-32 w-full rounded-md object-cover" />}
              <h3 className="font-bold text-neighbor-navy">{item.titulo}</h3>
              <p className="mt-2 text-sm text-slate-600">{item.lugar} - {dateTime(item.fecha)}</p>
              <p className="mt-2 text-sm text-slate-600">{item.descripcion}</p>
            </article>
          )) : <EmptyState title="Sin reuniones internas" />}
        </div>
      </div>
    </section>
  );
}

function cargoLabel(cargo) {
  return {
    presidente: 'Presidente',
    vice_presidente: 'Vice presidente',
    secretario: 'Secretaria / Secretario',
    tesorero: 'Tesorero',
    vocal: 'Vocal'
  }[cargo] || cargo;
}
