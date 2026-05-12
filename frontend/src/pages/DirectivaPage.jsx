import { useEffect, useMemo, useRef, useState } from 'react';
import { Badge, EmptyState, Spinner } from '../components/common';
import { dateTime } from '../lib/utils';
import { dataService, mediaUrl, directivaSocketUrl } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { MessageCircle, Send, Users, Lock } from 'lucide-react';

const avatarFor = (name = 'V') => name.trim().slice(0, 2).toUpperCase();

export default function DirectivaPage() {
  const { user, hasRole } = useAuth();
  const [directiva, setDirectiva] = useState(null);
  const [reuniones, setReuniones] = useState(null);
  const [form, setForm] = useState({ titulo: '', descripcion: '', fecha: '', lugar: '', tipo: 'directiva', estado: 'programada', imagen: null });
  const [preview, setPreview] = useState(null);
  
  const isDirectivaMember = hasRole('admin') || hasRole('directiva') || hasRole('tesorero') || hasRole('vocero') || hasRole('secretaria');
  const [chat, setChat] = useState([]);
  const [presence, setPresence] = useState([]);
  const [typingUsers, setTypingUsers] = useState([]);
  const [chatText, setChatText] = useState('');
  const [queuedMessages, setQueuedMessages] = useState([]);
  const [status, setStatus] = useState('desconectado');
  
  const socketRef = useRef(null);
  const typingTimer = useRef(null);
  const messagesRef = useRef(null);
  const queuedMessagesRef = useRef([]);

  const load = () => {
    dataService.directiva().then(setDirectiva);
    dataService.reunionesDirectiva().then(setReuniones);
  };

  useEffect(() => {
    load();
    if (isDirectivaMember) {
      dataService.getDirectivaChatHistory().then((data) => {
        setChat(data.messages || []);
      }).catch(() => {});
    }
  }, [isDirectivaMember]);

  useEffect(() => {
    if (!isDirectivaMember) return;

    let reconnectTimer;
    let closedByPage = false;

    const sendJoin = (socket) => {
      socket.send(JSON.stringify({
        type: 'presence:join',
        user_id: user?.id,
        nombre: user?.nombre || 'Directivo'
      }));
    };

    const connect = () => {
      const socket = new WebSocket(directivaSocketUrl());
      socketRef.current = socket;
      setStatus('conectando');

      socket.onopen = () => {
        setStatus('en vivo');
        sendJoin(socket);
        const socketOpen = socketRef.current;
        if (socketOpen?.readyState === WebSocket.OPEN && queuedMessagesRef.current.length > 0) {
          queuedMessagesRef.current.forEach(msg => socketOpen.send(JSON.stringify(msg)));
          queuedMessagesRef.current = [];
          setQueuedMessages([]);
        }
      };

      socket.onclose = () => {
        setStatus('reconectando');
        if (!closedByPage) reconnectTimer = setTimeout(connect, 1800);
      };

      socket.onerror = () => setStatus('reconectando');

      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        if (payload.type === 'snapshot') {
          setChat((prev) => {
            const existingIds = new Set(prev.map(m => m.id));
            const newMessages = (payload.messages || []).filter(m => !existingIds.has(m.id));
            return [...prev, ...newMessages];
          });
          setPresence(payload.presence || []);
        }
        if (payload.type === 'presence:update') setPresence(payload.presence || []);
        if (payload.type === 'chat:new') {
          setChat((items) => [...(items || []), payload.message]);
          setTypingUsers((items) => items.filter((item) => item.autor !== payload.message.autor));
        }
        if (payload.type === 'chat:typing' && payload.autor !== user?.nombre) {
          setTypingUsers((items) => {
            const withoutCurrent = items.filter((item) => item.autor !== payload.autor);
            return payload.isTyping ? [...withoutCurrent, { autor: payload.autor }] : withoutCurrent;
          });
        }
      };
    };

    connect();
    return () => {
      closedByPage = true;
      clearTimeout(reconnectTimer);
      clearTimeout(typingTimer.current);
      socketRef.current?.close();
    };
  }, [isDirectivaMember, user]);

  useEffect(() => {
    messagesRef.current?.scrollTo({ top: messagesRef.current.scrollHeight, behavior: 'smooth' });
  }, [chat, typingUsers]);

  function handleImageChange(e) {
    const file = e.target.files[0];
    if (file) {
      setForm({ ...form, imagen: file });
      setPreview(URL.createObjectURL(file));
    }
  }

  function sendSocket(payload) {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload));
      return true;
    } else {
      if (payload.type === 'chat:send') {
        queuedMessagesRef.current = [...queuedMessagesRef.current, payload];
        setQueuedMessages([...queuedMessagesRef.current]);
      }
      return false;
    }
  }

  function onChatChange(value) {
    setChatText(value);
    if (status === 'en vivo') {
      sendSocket({ type: 'chat:typing', autor: user?.nombre || 'Directivo', isTyping: Boolean(value.trim()) });
      clearTimeout(typingTimer.current);
      typingTimer.current = setTimeout(() => {
        sendSocket({ type: 'chat:typing', autor: user?.nombre || 'Directivo', isTyping: false });
      }, 1100);
    }
  }

  function sendChat(event) {
    event.preventDefault();
    if (!chatText.trim()) return;
    const payload = { type: 'chat:send', mensaje: chatText.trim() };
    sendSocket(payload);
    setChatText('');
    sendSocket({ type: 'chat:typing', autor: user?.nombre || 'Directivo', isTyping: false });
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

  async function removeMember(item) {
    if (!window.confirm(`Eliminar a "${item.nombre}" de la directiva?`)) return;
    await dataService.eliminarDirectivo(item.id);
    load();
  }

  const isLive = status === 'en vivo';

  if (!directiva || !reuniones) return <Spinner />;

  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="page-title">Directiva</h1>
          {isDirectivaMember && (
            <p className="mt-1 text-sm font-semibold text-slate-500">Chat privado para miembros de la directiva.</p>
          )}
        </div>
        {isDirectivaMember && (
          <div className="flex gap-2">
            <Badge>{presence.length} en línea</Badge>
            {queuedMessages.length > 0 && (
              <Badge className="bg-yellow-50 text-yellow-700">{queuedMessages.length} en cola</Badge>
            )}
            <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-black ${isLive ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'}`}>
              <span className={`h-2 w-2 rounded-full ${isLive ? 'bg-green-500' : 'bg-yellow-500'}`} /> {status}
            </span>
          </div>
        )}
      </div>

      {isDirectivaMember ? (
        <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_380px]">
          <section className="card flex h-[520px] flex-col overflow-hidden">
            <div className="border-b border-slate-200 bg-white p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-neighbor-blue text-white">
                  <MessageCircle className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="font-black text-neighbor-navy">Chat de la Directiva</h2>
                  <p className="text-sm font-semibold text-slate-500">{chat.length} mensajes - Solo para miembros</p>
                </div>
              </div>
              {presence.length > 0 && (
                <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
                  {presence.map((item) => (
                    <span key={item.id} className="inline-flex shrink-0 items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-bold text-slate-600">
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-neighbor-mist text-[10px] font-black text-neighbor-blue">{avatarFor(item.nombre)}</span>
                      {item.nombre}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div ref={messagesRef} className="flex-1 space-y-4 overflow-y-auto bg-[#eef7fb] p-5">
              {!chat.length && (
                <div className="flex h-full items-center justify-center text-center">
                  <div>
                    <MessageCircle className="mx-auto h-10 w-10 text-neighbor-blue" />
                    <p className="mt-3 font-black text-neighbor-navy">Chat privado de la directiva</p>
                    <p className="mt-1 text-sm font-semibold text-slate-500">Escribe el primer mensaje.</p>
                  </div>
                </div>
              )}
              {chat.map((item) => {
                const mine = item.usuario_id === user?.id || item.autor === user?.nombre;
                return (
                  <article key={item.id} className={`flex gap-3 ${mine ? 'justify-end' : 'justify-start'}`}>
                    {!mine && <Avatar name={item.autor} />}
                    <div className={`max-w-[78%] rounded-2xl px-4 py-3 shadow-sm ${mine ? 'rounded-br-md bg-neighbor-blue text-white' : 'rounded-bl-md bg-white text-slate-700'}`}>
                      <div className="flex items-center justify-between gap-4">
                        <p className={`text-xs font-black ${mine ? 'text-white/80' : 'text-neighbor-green'}`}>{item.autor}</p>
                        <p className={`text-[11px] font-semibold ${mine ? 'text-white/60' : 'text-slate-400'}`}>{dateTime(item.fecha)}</p>
                      </div>
                      <p className="mt-2 whitespace-pre-wrap text-sm leading-6">{item.mensaje}</p>
                    </div>
                    {mine && <Avatar name={item.autor} mine />}
                  </article>
                );
              })}
              {typingUsers.length > 0 && (
                <div className="flex items-center gap-3 text-sm font-semibold text-slate-500">
                  <div className="rounded-2xl rounded-bl-md bg-white px-4 py-3 shadow-sm">
                    {typingUsers.join(', ')} escribiendo<span className="animate-pulse">...</span>
                  </div>
                </div>
              )}
            </div>

            <form onSubmit={sendChat} className="border-t border-slate-200 bg-white p-4">
              <div className="flex gap-2 rounded-lg border border-slate-200 bg-slate-50 p-2">
                <textarea
                  className="min-h-12 flex-1 resize-none bg-transparent px-2 py-2 text-sm outline-none"
                  placeholder="Escribe un mensaje para la directiva..."
                  value={chatText}
                  onChange={(e) => onChatChange(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendChat(e);
                    }
                  }}
                />
                <button className="btn-primary self-end px-3" title="Enviar mensaje" disabled={!chatText.trim()}>
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </form>
          </section>

          <aside className="space-y-6">
            <section className="card overflow-hidden">
              <h2 className="border-b border-slate-200 p-4 font-black text-neighbor-navy">Miembros de la directiva</h2>
              <div className="max-h-[260px] divide-y divide-slate-100 overflow-y-auto">
                {directiva.length ? directiva.map((item) => (
                  <article key={item.id} className="flex gap-3 p-4">
                    {item.imagen_url ? (
                      <img src={mediaUrl(item.imagen_url)} alt={item.nombre} className="h-10 w-10 rounded-full object-cover" />
                    ) : (
                      <Avatar name={item.nombre} />
                    )}
                    <div className="min-w-0">
                      <p className="font-bold text-neighbor-navy truncate">{item.nombre}</p>
                      <p className="text-xs text-slate-500">{cargoLabel(item.cargo)}</p>
                    </div>
                  </article>
                )) : (
                  <p className="p-4 text-center text-sm text-slate-500">Sin miembros registrados</p>
                )}
              </div>
            </section>

            <section className="card overflow-hidden">
              <h2 className="border-b border-slate-200 p-4 font-black text-neighbor-navy">Próximas reuniones</h2>
              <div className="max-h-[220px] divide-y divide-slate-100 overflow-y-auto">
                {reuniones.length ? reuniones.slice(0, 5).map((item) => (
                  <article key={item.id} className="p-4">
                    <p className="font-bold text-neighbor-navy">{item.titulo}</p>
                    <p className="mt-1 text-xs text-slate-500">{item.lugar} - {dateTime(item.fecha)}</p>
                  </article>
                )) : (
                  <p className="p-4 text-center text-sm text-slate-500">Sin reuniones programadas</p>
                )}
              </div>
            </section>
          </aside>
        </div>
      ) : (
        <div className="mt-8 card p-12 text-center">
          <Lock className="mx-auto h-16 w-16 text-slate-400" />
          <h2 className="mt-4 text-xl font-black text-neighbor-navy">Acceso Restringido</h2>
          <p className="mt-2 text-sm text-slate-500">Esta sección es solo para miembros de la directiva.</p>
        </div>
      )}

      {hasRole('admin') && (
        <form onSubmit={createMeeting} className="card mt-8 grid gap-4 p-5 md:grid-cols-2">
          <h2 className="font-bold text-neighbor-navy md:col-span-2">Nueva reunión directiva</h2>
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

      <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {directiva.length ? directiva.map((item) => (
          <article key={item.id} className="card p-5">
            {item.imagen_url && <img src={mediaUrl(item.imagen_url)} alt={item.nombre} className="mb-3 h-32 w-full rounded-md object-cover" />}
            <Badge>{cargoLabel(item.cargo)}</Badge>
            <h2 className="mt-3 font-black text-neighbor-navy">{item.nombre}</h2>
            <p className="mt-1 text-sm text-slate-600">{item.periodo}</p>
            <p className="mt-2 text-sm font-semibold text-neighbor-blue">{item.email}</p>
            {hasRole('admin') && <div className="mt-4 flex gap-2"><button className="btn border border-red-200 text-red-600 hover:bg-red-50" onClick={() => removeMember(item)}>Eliminar</button></div>}
          </article>
        )) : <EmptyState title="Directiva sin registrar" />}
      </div>

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

function Avatar({ name, mine = false }) {
  return (
    <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xs font-black ${mine ? 'bg-neighbor-navy text-white' : 'bg-white text-neighbor-blue shadow-sm'}`}>
      {avatarFor(name)}
    </div>
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
