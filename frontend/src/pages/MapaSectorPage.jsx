import { Crosshair, ExternalLink, LocateFixed, MapPin, Navigation, Radio } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Badge } from '../components/common';
import { liveSocketUrl } from '../services/api';

const defaultCenter = {
  lat: Number(import.meta.env.VITE_MAP_LAT || -16.5),
  lng: Number(import.meta.env.VITE_MAP_LNG || -68.15),
  zoom: Number(import.meta.env.VITE_MAP_ZOOM || 16),
  name: import.meta.env.VITE_MAP_NAME || 'Sector comunitario'
};
const savedCenter = (() => {
  try {
    const value = JSON.parse(localStorage.getItem('neighbor_map_center') || 'null');
    return value?.lat && value?.lng ? value : defaultCenter;
  } catch {
    return defaultCenter;
  }
})();

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

function mapUrls(center) {
  const delta = 0.018 / Math.max(center.zoom - 12, 1);
  const left = center.lng - delta;
  const right = center.lng + delta;
  const top = center.lat + delta;
  const bottom = center.lat - delta;
  const bbox = `${left},${bottom},${right},${top}`;

  return {
    embed: `https://www.openstreetmap.org/export/embed.html?bbox=${encodeURIComponent(bbox)}&layer=mapnik&marker=${center.lat},${center.lng}`,
    open: `https://www.openstreetmap.org/?mlat=${center.lat}&mlon=${center.lng}#map=${center.zoom}/${center.lat}/${center.lng}`
  };
}

export default function MapaSectorPage() {
  const socketRef = useRef(null);
  const [status, setStatus] = useState('conectando');
  const [center, setCenter] = useState(savedCenter);
  const [form, setForm] = useState({
    lat: String(savedCenter.lat),
    lng: String(savedCenter.lng),
    zoom: String(savedCenter.zoom),
    name: savedCenter.name
  });
  const urls = useMemo(() => mapUrls(center), [center]);

  useEffect(() => {
    let reconnectTimer;
    let closedByPage = false;

    const connect = () => {
      const socket = new WebSocket(liveSocketUrl());
      socketRef.current = socket;
      setStatus('conectando');

      socket.onopen = () => setStatus('en vivo');
      socket.onclose = () => {
        setStatus('reconectando');
        if (!closedByPage) reconnectTimer = setTimeout(connect, 1800);
      };
      socket.onerror = () => setStatus('reconectando');
      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        if (payload.type === 'snapshot' && payload.realMap) {
          const next = {
            lat: Number(payload.realMap.lat),
            lng: Number(payload.realMap.lng),
            zoom: Number(payload.realMap.zoom || center.zoom),
            name: payload.realMap.name || 'Sector comunitario'
          };
          setCenter(next);
          setForm({ lat: String(next.lat), lng: String(next.lng), zoom: String(next.zoom), name: next.name });
        }
        if (payload.type === 'map:real:update') {
          const next = {
            lat: Number(payload.center.lat),
            lng: Number(payload.center.lng),
            zoom: Number(payload.center.zoom || center.zoom),
            name: payload.center.name || 'Sector comunitario'
          };
          setCenter(next);
          setForm({ lat: String(next.lat), lng: String(next.lng), zoom: String(next.zoom), name: next.name });
        }
      };
    };

    connect();
    return () => {
      closedByPage = true;
      clearTimeout(reconnectTimer);
      socketRef.current?.close();
    };
  }, [center.zoom]);

  function broadcastCenter(next) {
    setCenter(next);
    setForm({ lat: String(next.lat), lng: String(next.lng), zoom: String(next.zoom), name: next.name });
    localStorage.setItem('neighbor_map_center', JSON.stringify(next));
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'map:real:update', center: next }));
    }
  }

  function submitCoords(event) {
    event.preventDefault();
    const lat = Number(form.lat);
    const lng = Number(form.lng);
    const zoom = clamp(Number(form.zoom || center.zoom), 3, 19);
    if (Number.isNaN(lat) || Number.isNaN(lng)) return;
    broadcastCenter({ lat, lng, zoom, name: form.name || 'Sector comunitario' });
  }

  function useCurrentLocation() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition((position) => {
      broadcastCenter({
        lat: Number(position.coords.latitude.toFixed(6)),
        lng: Number(position.coords.longitude.toFixed(6)),
        zoom: 17,
        name: 'Mi ubicacion actual'
      });
    });
  }

  return (
    <section>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="page-title">Mapa del sector</h1>
          <p className="mt-1 text-sm font-semibold text-slate-500">Mapa real con OpenStreetMap, no una maqueta simulada.</p>
        </div>
        <div className="flex gap-2">
          <Badge>{center.name}</Badge>
          <Badge>{status}</Badge>
        </div>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_360px]">
        <section className="card overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-md bg-neighbor-mist text-neighbor-blue">
                <MapPin className="h-5 w-5" />
              </div>
              <div>
                <p className="font-black text-neighbor-navy">{center.name}</p>
                <p className="text-sm font-semibold text-slate-500">{center.lat}, {center.lng}</p>
              </div>
            </div>
            <a href={urls.open} target="_blank" rel="noreferrer" className="btn-secondary">
              <ExternalLink className="h-4 w-4" /> Abrir en OSM
            </a>
          </div>

          <div className="h-[680px] bg-slate-100">
            <iframe
              key={`${center.lat}-${center.lng}-${center.zoom}`}
              title="Mapa real del sector"
              src={urls.embed}
              className="h-full w-full border-0"
              loading="lazy"
            />
          </div>
        </section>

        <aside className="space-y-4">
          <section className="card p-5">
            <div className="flex items-center gap-2">
              <Radio className="h-5 w-5 text-neighbor-green" />
              <h2 className="font-black text-neighbor-navy">Ubicacion real</h2>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Configura las coordenadas reales de tu junta de vecinos. El cambio se sincroniza en vivo con otras pestañas conectadas.
            </p>

            <button type="button" onClick={useCurrentLocation} className="btn-primary mt-4 w-full">
              <LocateFixed className="h-4 w-4" /> Usar mi ubicacion actual
            </button>
          </section>

          <form onSubmit={submitCoords} className="card grid gap-4 p-5">
            <h2 className="flex items-center gap-2 font-black text-neighbor-navy">
              <Crosshair className="h-5 w-5 text-neighbor-green" /> Coordenadas del sector
            </h2>
            <label className="label">
              Nombre del sector
              <input className="input mt-1" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </label>
            <label className="label">
              Latitud
              <input className="input mt-1" type="number" step="0.000001" value={form.lat} onChange={(e) => setForm({ ...form, lat: e.target.value })} required />
            </label>
            <label className="label">
              Longitud
              <input className="input mt-1" type="number" step="0.000001" value={form.lng} onChange={(e) => setForm({ ...form, lng: e.target.value })} required />
            </label>
            <label className="label">
              Zoom
              <input className="input mt-1" type="number" min="3" max="19" value={form.zoom} onChange={(e) => setForm({ ...form, zoom: e.target.value })} />
            </label>
            <button className="btn-primary">
              <Navigation className="h-4 w-4" /> Actualizar mapa real
            </button>
          </form>
        </aside>
      </div>
    </section>
  );
}
