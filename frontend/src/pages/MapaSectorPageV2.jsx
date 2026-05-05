import { Crosshair, ExternalLink, LocateFixed, MapPin, Navigation, Radio } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { Badge, GoogleMapComponent } from '../components/common';
import { liveSocketUrl } from '../services/api';
import { getCurrentLocation, getAddressFromCoords, loadGoogleMaps, isGoogleMapsLoaded } from '../services/googleMaps';

const defaultCenter = {
  lat: Number(import.meta.env.VITE_MAP_LAT || -16.5),
  lng: Number(import.meta.env.VITE_MAP_LNG || -68.15),
  zoom: Number(import.meta.env.VITE_MAP_ZOOM || 16),
  name: import.meta.env.VITE_MAP_NAME || 'Sector comunitario'
};

const savedCenter = (() => {
  try {
    const value = JSON.parse(localStorage.getItem('neighbor_map_center_v2') || 'null');
    return value?.lat && value?.lng ? value : defaultCenter;
  } catch {
    return defaultCenter;
  }
})();

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

export default function MapaSectorPageV2() {
  const socketRef = useRef(null);
  const [status, setStatus] = useState('conectando');
  const [center, setCenter] = useState(savedCenter);
  const [address, setAddress] = useState('');
  const [loadingAddress, setLoadingAddress] = useState(false);
  const [form, setForm] = useState({
    lat: String(savedCenter.lat),
    lng: String(savedCenter.lng),
    zoom: String(savedCenter.zoom),
    name: savedCenter.name
  });
  const [markers, setMarkers] = useState([
    {
      lat: center.lat,
      lng: center.lng,
      title: center.name,
      infoWindow: `
        <div style="font-family: Arial, sans-serif; padding: 8px;">
          <h3 style="margin: 0; font-weight: bold; color: #003366;">${center.name}</h3>
          <p style="margin: 4px 0; font-size: 12px; color: #666;">
            ${center.lat.toFixed(6)}, ${center.lng.toFixed(6)}
          </p>
        </div>
      `,
      draggable: true,
      onDragEnd: (coords) => {
        const newCenter = { ...center, ...coords };
        broadcastCenter(newCenter);
      }
    }
  ]);

  // Sincronizar estado en vivo
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

  // Obtener dirección del centro
  useEffect(() => {
    if (!isGoogleMapsLoaded() || !center.lat || !center.lng) return;

    setLoadingAddress(true);
    getAddressFromCoords(center.lat, center.lng)
      .then(addr => {
        setAddress(addr);
        setLoadingAddress(false);
      })
      .catch(err => {
        console.error('Error getting address:', err);
        setAddress('Dirección no disponible');
        setLoadingAddress(false);
      });
  }, [center.lat, center.lng]);

  // Actualizar marcadores
  useEffect(() => {
    setMarkers([
      {
        lat: center.lat,
        lng: center.lng,
        title: center.name,
        infoWindow: `
          <div style="font-family: Arial, sans-serif; padding: 8px;">
            <h3 style="margin: 0; font-weight: bold; color: #003366;">${center.name}</h3>
            <p style="margin: 4px 0; font-size: 12px; color: #666;">
              ${center.lat.toFixed(6)}, ${center.lng.toFixed(6)}
            </p>
            <p style="margin: 4px 0; font-size: 11px; color: #999;">
              ${address || 'Cargando dirección...'}
            </p>
          </div>
        `,
        draggable: true,
        onDragEnd: (coords) => {
          const newCenter = { ...center, ...coords };
          broadcastCenter(newCenter);
        }
      }
    ]);
  }, [center, address]);

  function broadcastCenter(next) {
    setCenter(next);
    setForm({ lat: String(next.lat), lng: String(next.lng), zoom: String(next.zoom), name: next.name });
    localStorage.setItem('neighbor_map_center_v2', JSON.stringify(next));
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

  async function useCurrentLocation() {
    try {
      const location = await getCurrentLocation();
      broadcastCenter({
        lat: location.lat,
        lng: location.lng,
        zoom: 17,
        name: 'Mi ubicación actual'
      });
    } catch (error) {
      console.error('Error getting location:', error);
      alert('No se pudo obtener la ubicación. Asegúrate de que el navegador tiene permiso de geolocalización.');
    }
  }

  const handleCenterChange = (newCenter) => {
    setCenter(prev => ({
      ...prev,
      zoom: newCenter.zoom
    }));
  };

  const handleMapReady = (map) => {
    // El mapa está listo
    console.log('Google Map loaded');
  };

  return (
    <section>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="page-title">Mapa del sector (Mejorado)</h1>
          <p className="mt-1 text-sm font-semibold text-slate-500">Mapa interactivo con Google Maps con geolocalización avanzada.</p>
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
                <p className="text-sm font-semibold text-slate-500">
                  {center.lat.toFixed(6)}, {center.lng.toFixed(6)}
                </p>
                {address && (
                  <p className="text-xs text-slate-400 mt-1">{address}</p>
                )}
              </div>
            </div>
          </div>

          <GoogleMapComponent
            center={{ lat: center.lat, lng: center.lng }}
            zoom={center.zoom}
            markers={markers}
            onMapReady={handleMapReady}
            onCenterChange={handleCenterChange}
            className="h-[680px]"
          />
        </section>

        <aside className="space-y-4">
          <section className="card p-5">
            <div className="flex items-center gap-2">
              <Radio className="h-5 w-5 text-neighbor-green" />
              <h2 className="font-black text-neighbor-navy">Ubicación real</h2>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Configura las coordenadas reales de tu junta de vecinos. El cambio se sincroniza en vivo con otras pestañas conectadas.
            </p>

            <button type="button" onClick={useCurrentLocation} className="btn-primary mt-4 w-full">
              <LocateFixed className="h-4 w-4" /> Usar mi ubicación actual
            </button>
          </section>

          <form onSubmit={submitCoords} className="card grid gap-4 p-5">
            <h2 className="flex items-center gap-2 font-black text-neighbor-navy">
              <Crosshair className="h-5 w-5 text-neighbor-green" /> Coordenadas
            </h2>
            <label className="label">
              Nombre del sector
              <input 
                className="input mt-1" 
                value={form.name} 
                onChange={(e) => setForm({ ...form, name: e.target.value })} 
              />
            </label>
            <label className="label">
              Latitud
              <input 
                className="input mt-1" 
                type="number" 
                step="0.000001" 
                value={form.lat} 
                onChange={(e) => setForm({ ...form, lat: e.target.value })} 
                required 
              />
            </label>
            <label className="label">
              Longitud
              <input 
                className="input mt-1" 
                type="number" 
                step="0.000001" 
                value={form.lng} 
                onChange={(e) => setForm({ ...form, lng: e.target.value })} 
                required 
              />
            </label>
            <label className="label">
              Zoom
              <input 
                className="input mt-1" 
                type="number" 
                min="3" 
                max="19" 
                value={form.zoom} 
                onChange={(e) => setForm({ ...form, zoom: e.target.value })} 
              />
            </label>

            <button type="submit" className="btn-primary w-full">
              <Navigation className="h-4 w-4" /> Actualizar ubicación
            </button>
          </form>
        </aside>
      </div>
    </section>
  );
}
