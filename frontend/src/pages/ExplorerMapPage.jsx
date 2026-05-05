import { MapPin, Navigation, Search, AlertCircle } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { GoogleMapComponent } from '../components/common';
import { loadGoogleMaps, searchPlace, getCoordsFromAddress } from '../services/googleMaps';

export default function ExplorerMapPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState({
    lat: -16.5,
    lng: -68.15,
    zoom: 14,
    name: 'Centro de búsqueda'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [markers, setMarkers] = useState([
    {
      lat: -16.5,
      lng: -68.15,
      title: 'Centro',
      infoWindow: '<div style="font-family: Arial; padding: 8px;"><h3 style="margin: 0;">Centro de búsqueda</h3></div>'
    }
  ]);

  // Cargar Google Maps
  useEffect(() => {
    loadGoogleMaps();
  }, []);

  // Manejar búsqueda
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setError('Por favor ingresa un lugar o dirección');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await getCoordsFromAddress(searchQuery);
      const newLocation = {
        lat: result.lat,
        lng: result.lng,
        zoom: 15,
        name: result.address
      };
      
      setSelectedLocation(newLocation);
      setMarkers([
        {
          lat: result.lat,
          lng: result.lng,
          title: result.address,
          infoWindow: `
            <div style="font-family: Arial; padding: 8px;">
              <h3 style="margin: 0; font-weight: bold;">${result.address}</h3>
              <p style="margin: 4px 0; font-size: 12px; color: #666;">
                ${result.lat.toFixed(6)}, ${result.lng.toFixed(6)}
              </p>
            </div>
          `
        }
      ]);
      setSearchResults([result]);
    } catch (err) {
      setError(`No se encontró el lugar: ${err.message}`);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectResult = (result) => {
    const newLocation = {
      lat: result.lat,
      lng: result.lng,
      zoom: 16,
      name: result.address
    };
    
    setSelectedLocation(newLocation);
    setMarkers([
      {
        lat: result.lat,
        lng: result.lng,
        title: result.address,
        infoWindow: `
          <div style="font-family: Arial; padding: 8px;">
            <h3 style="margin: 0; font-weight: bold;">${result.address}</h3>
            <p style="margin: 4px 0; font-size: 12px; color: #666;">
              ${result.lat.toFixed(6)}, ${result.lng.toFixed(6)}
            </p>
          </div>
        `
      }
    ]);
  };

  return (
    <section>
      <div className="mb-6">
        <h1 className="page-title">Explorador de Mapa</h1>
        <p className="mt-1 text-sm font-semibold text-slate-500">Busca lugares y explora el mapa interactivamente.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="card overflow-hidden">
          <GoogleMapComponent
            center={{ lat: selectedLocation.lat, lng: selectedLocation.lng }}
            zoom={selectedLocation.zoom}
            markers={markers}
            className="h-[600px]"
          />
        </div>

        <aside className="space-y-4">
          <div className="card p-5">
            <h2 className="flex items-center gap-2 font-black text-neighbor-navy mb-4">
              <Search className="h-5 w-5 text-neighbor-green" /> Buscar lugar
            </h2>

            <form onSubmit={handleSearch} className="space-y-3">
              <input
                type="text"
                placeholder="Busca una dirección o lugar..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input w-full"
              />
              <button 
                type="submit" 
                disabled={loading}
                className="btn-primary w-full disabled:opacity-50"
              >
                {loading ? 'Buscando...' : 'Buscar'}
              </button>
            </form>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-2">
                <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {searchResults.length > 0 && (
              <div className="mt-4 space-y-2">
                <p className="text-sm font-semibold text-slate-600">Resultados:</p>
                {searchResults.map((result, index) => (
                  <button
                    key={index}
                    onClick={() => handleSelectResult(result)}
                    className="w-full text-left p-3 bg-neighbor-mist hover:bg-neighbor-blue/20 rounded-lg transition"
                  >
                    <div className="flex items-start gap-2">
                      <MapPin className="h-4 w-4 text-neighbor-blue mt-0.5 flex-shrink-0" />
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-neighbor-navy truncate">
                          {result.address}
                        </p>
                        <p className="text-xs text-slate-500">
                          {result.lat.toFixed(4)}, {result.lng.toFixed(4)}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="card p-5">
            <h3 className="flex items-center gap-2 font-black text-neighbor-navy mb-3">
              <Navigation className="h-5 w-5 text-neighbor-green" /> Ubicación actual
            </h3>
            <div className="space-y-2 text-sm">
              <p>
                <span className="font-semibold text-slate-700">Lugar:</span>
                <span className="text-slate-600 ml-2 block truncate">{selectedLocation.name}</span>
              </p>
              <p>
                <span className="font-semibold text-slate-700">Latitud:</span>
                <span className="text-slate-600 ml-2">{selectedLocation.lat.toFixed(6)}</span>
              </p>
              <p>
                <span className="font-semibold text-slate-700">Longitud:</span>
                <span className="text-slate-600 ml-2">{selectedLocation.lng.toFixed(6)}</span>
              </p>
              <p>
                <span className="font-semibold text-slate-700">Zoom:</span>
                <span className="text-slate-600 ml-2">{selectedLocation.zoom}</span>
              </p>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
