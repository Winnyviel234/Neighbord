import { BellRing, CheckCircle2, MessageCircle, Radio, Send, Users } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Badge, Spinner } from '../components/common';
import { dateTime } from '../lib/utils';
import { dataService, liveSocketUrl } from '../services/api';
import { useAuth } from '../context/AuthContext';

const avatarFor = (name = 'V') => name.trim().slice(0, 2).toUpperCase();

export default function ComunidadPage() {
  const { user } = useAuth();
  const socketRef = useRef(null);
  const typingTimer = useRef(null);
  const messagesRef = useRef(null);
  const [status, setStatus] = useState('conectando');
  const [notifications, setNotifications] = useState(null);
  const [chat, setChat] = useState(null);
  const [presence, setPresence] = useState([]);
  const [typingUsers, setTypingUsers] = useState([]);
  const [directivaMessages, setDirectivaMessages] = useState(null);
  const [chatText, setChatText] = useState('');
  const [queuedMessages, setQueuedMessages] = useState([]);
  const [directivaForm, setDirectivaForm] = useState({ asunto: '', mensaje: '' });

  useEffect(() => {
    Promise.all([
      dataService.notificacionesTiempoReal(),
      dataService.chatVecinal(),
      dataService.mensajesDirectiva()
    ]).then(([noti, chatRows, messages]) => {
      setNotifications(noti);
      setChat(chatRows);
      setDirectivaMessages(messages);
    });
  }, []);

  useEffect(() => {
    let reconnectTimer;
    let closedByPage = false;

    const sendJoin = (socket) => {
      socket.send(JSON.stringify({
        type: 'presence:join',
        user_id: user?.id || user?.email || user?.nombre || 'visitante',
        nombre: user?.nombre || 'Vecino'
      }));
    };

    const connect = () => {
      const socket = new WebSocket(liveSocketUrl());
      socketRef.current = socket;
      setStatus('conectando');

socket.onopen = () => {
  setStatus('en vivo');
  sendJoin(socket);
  if (queuedMessages.length > 0) {
    const socket = socketRef.current;
    if (socket?.readyState === WebSocket.OPEN) {
      queuedMessages.forEach(msg => socket.send(JSON.stringify(msg)));
      setQueuedMessages([]);
    }
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
          setChat(payload.chat || []);
          setDirectivaMessages(payload.directiva || []);
          setNotifications(payload.notifications || []);
          setPresence(payload.presence || []);
        }
        if (payload.type === 'presence:update') setPresence(payload.presence || []);
        if (payload.type === 'chat:new') {
          setChat((items) => [...(items || []), payload.message]);
          setTypingUsers((items) => items.filter((name) => name !== payload.message.autor));
        }
        if (payload.type === 'chat:typing' && payload.autor !== user?.nombre) {
          setTypingUsers((items) => {
            const next = new Set(items);
            if (payload.isTyping) next.add(payload.autor);
            else next.delete(payload.autor);
            return [...next];
          });
        }
        if (payload.type === 'directiva:new') setDirectivaMessages((items) => [payload.message, ...(items || [])]);
        if (payload.type === 'notification:new') setNotifications((items) => [payload.notification, ...(items || [])].slice(0, 12));
      };
    };

    connect();
    return () => {
      closedByPage = true;
      clearTimeout(reconnectTimer);
      clearTimeout(typingTimer.current);
      socketRef.current?.close();
    };
  }, [user]);

  useEffect(() => {
    messagesRef.current?.scrollTo({ top: messagesRef.current.scrollHeight, behavior: 'smooth' });
  }, [chat, typingUsers]);

  const unread = useMemo(() => notifications?.filter((item) => item.estado === 'nuevo').length || 0, [notifications]);
  const isLive = status === 'en vivo';

function sendSocket(payload) {
  if (socketRef.current?.readyState === WebSocket.OPEN) {
    socketRef.current.send(JSON.stringify(payload));
    return true;
  } else {
    if (payload.type === 'chat:send' || payload.type === 'directiva:send') {
      setQueuedMessages(prev => [...prev, payload]);
    }
    return false;
  }
}

function onChatChange(value) {
  setChatText(value);
  if (isLive) {
    sendSocket({ type: 'chat:typing', autor: user?.nombre || 'Vecino', isTyping: Boolean(value.trim()) });
    clearTimeout(typingTimer.current);
    typingTimer.current = setTimeout(() => {
      sendSocket({ type: 'chat:typing', autor: user?.nombre || 'Vecino', isTyping: false });
    }, 1100);
  }
}

function sendChat(event) {
  event.preventDefault();
  if (!chatText.trim()) return;
  const payload = { type: 'chat:send', autor: user?.nombre || 'Vecino', mensaje: chatText.trim() };
  sendSocket(payload);
  setChatText('');
  sendSocket({ type: 'chat:typing', autor: user?.nombre || 'Vecino', isTyping: false });
}

function sendDirectiva(event) {
  event.preventDefault();
  if (!directivaForm.asunto.trim() || !directivaForm.mensaje.trim()) return;
  const payload = { type: 'directiva:send', asunto: directivaForm.asunto, mensaje: directivaForm.mensaje };
  sendSocket(payload);
  setDirectivaForm({ asunto: '', mensaje: '' });
}

  if (!notifications || !chat || !directivaMessages) return <Spinner />;

  return (
    <section>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="page-title">Comunidad en vivo</h1>
          <p className="mt-1 text-sm font-semibold text-slate-500">Chat real por WebSocket, presencia vecinal y mensajes a la directiva.</p>
        </div>
<div className="flex gap-2">
  <Badge>{presence.length} conectados</Badge>
  <Badge>{unread} nuevas</Badge>
  {queuedMessages.length > 0 && (
    <Badge className="bg-yellow-50 text-yellow-700">{queuedMessages.length} en cola</Badge>
  )}
</div>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_340px]">
        <section className="card flex h-[560px] flex-col overflow-hidden">
          <div className="border-b border-slate-200 bg-white p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-neighbor-blue text-white">
                  <MessageCircle className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="font-black text-neighbor-navy">Chat entre vecinos</h2>
                  <p className="text-sm font-semibold text-slate-500">{chat.length} mensajes compartidos</p>
                </div>
              </div>
              <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-black ${isLive ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'}`}>
                <span className={`h-2 w-2 rounded-full ${isLive ? 'bg-green-500' : 'bg-yellow-500'}`} /> {status}
              </span>
            </div>
            <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
              {presence.map((item) => (
                <span key={item.id} className="inline-flex shrink-0 items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-bold text-slate-600">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-neighbor-mist text-[10px] font-black text-neighbor-blue">{avatarFor(item.nombre)}</span>
                  {item.nombre}
                </span>
              ))}
            </div>
          </div>

          <div ref={messagesRef} className="flex-1 space-y-4 overflow-y-auto bg-[#eef7fb] p-5">
            {!chat.length && (
              <div className="flex h-full items-center justify-center text-center">
                <div>
                  <MessageCircle className="mx-auto h-10 w-10 text-neighbor-blue" />
                  <p className="mt-3 font-black text-neighbor-navy">Todavia no hay mensajes</p>
                  <p className="mt-1 text-sm font-semibold text-slate-500">Escribe el primero; aqui solo responden vecinos conectados.</p>
                </div>
              </div>
            )}
            {chat.map((item) => {
              const mine = item.autor === user?.nombre;
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
                placeholder="Escribe un mensaje en vivo para tus vecinos"
                value={chatText}
                onChange={(e) => onChatChange(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendChat(e);
                  }
                }}
              />
              <button className="btn-primary self-end px-3" title="Enviar mensaje" disabled={!chatText.trim()}><Send className="h-4 w-4" /></button>
            </div>
          </form>
        </section>

        <aside className="space-y-6">
          <section className="card overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-200 p-4">
              <h2 className="flex items-center gap-2 font-black text-neighbor-navy"><Radio className="h-5 w-5 text-neighbor-green" /> Alertas</h2>
              <Badge>{unread}</Badge>
            </div>
            <div className="max-h-[240px] divide-y divide-slate-100 overflow-y-auto">
              {notifications.map((item) => (
                <article key={item.id} className="flex gap-3 p-4">
                  <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-neighbor-mist text-neighbor-blue">
                    <BellRing className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="font-bold text-neighbor-navy">{item.titulo}</p>
                      <Badge>{item.tipo}</Badge>
                    </div>
                    <p className="mt-1 text-sm text-slate-600">{item.mensaje}</p>
                    <p className="mt-2 text-xs font-semibold text-slate-400">{dateTime(item.fecha)}</p>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <form onSubmit={sendDirectiva} className="card grid gap-4 p-5">
            <h2 className="flex items-center gap-2 font-black text-neighbor-navy"><Users className="h-5 w-5 text-neighbor-green" /> Mensajes a la directiva</h2>
            <input className="input" placeholder="Asunto" value={directivaForm.asunto} onChange={(e) => setDirectivaForm({ ...directivaForm, asunto: e.target.value })} required />
            <textarea className="input min-h-24" placeholder="Mensaje" value={directivaForm.mensaje} onChange={(e) => setDirectivaForm({ ...directivaForm, mensaje: e.target.value })} required />
            <button className="btn-primary w-fit" disabled={!directivaForm.asunto.trim() || !directivaForm.mensaje.trim()}><Send className="h-4 w-4" /> Enviar</button>
          </form>

          <section className="card overflow-hidden">
            <h2 className="border-b border-slate-200 p-4 font-black text-neighbor-navy">Historial con directiva</h2>
            <div className="max-h-[220px] divide-y divide-slate-100 overflow-y-auto">
              {directivaMessages.map((item) => (
                <article key={item.id} className="p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="font-bold text-neighbor-navy">{item.asunto}</p>
                    <span className="inline-flex items-center gap-2 text-xs font-black text-green-700"><CheckCircle2 className="h-4 w-4" /> {item.estado}</span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{item.mensaje}</p>
                  <p className="mt-2 text-xs font-semibold text-slate-400">{dateTime(item.fecha)}</p>
                </article>
              ))}
            </div>
          </section>
        </aside>
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
