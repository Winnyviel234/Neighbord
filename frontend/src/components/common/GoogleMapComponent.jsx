import { useEffect, useRef, useState } from 'react';
import { loadGoogleMaps, createMap, addMarker, createInfoWindow, getGoogleMaps } from '../../services/googleMaps';

export default function GoogleMapComponent({ 
  center = { lat: -16.5, lng: -68.15 }, 
  zoom = 16, 
  markers = [],
  onMapReady = null,
  onMarkerClick = null,
  onCenterChange = null,
  className = 'h-[680px]',
  mapTypeControl = true,
  streetViewControl = true,
  fullscreenControl = true,
  children
}) {
  const mapElement = useRef(null);
  const mapRef = useRef(null);
  const markersRef = useRef([]);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(null);

  // Cargar Google Maps
  useEffect(() => {
    loadGoogleMaps()
      .then(() => {
        setIsLoaded(true);
        setError(null);
      })
      .catch(err => {
        setError(err.message);
        console.error('Error loading Google Maps:', err);
      });
  }, []);

  // Inicializar mapa
  useEffect(() => {
    if (!isLoaded || !mapElement.current) return;

    const map = createMap(mapElement.current, {
      center,
      zoom,
      mapTypeControl,
      streetViewControl,
      fullscreenControl
    });

    if (map) {
      mapRef.current = map;
      if (onMapReady) onMapReady(map);

      // Escuchar cambios de centro del mapa
      map.addListener('center_changed', () => {
        const newCenter = map.getCenter();
        if (onCenterChange) {
          onCenterChange({
            lat: newCenter.lat(),
            lng: newCenter.lng(),
            zoom: map.getZoom()
          });
        }
      });

      map.addListener('zoom_changed', () => {
        const newCenter = map.getCenter();
        if (onCenterChange) {
          onCenterChange({
            lat: newCenter.lat(),
            lng: newCenter.lng(),
            zoom: map.getZoom()
          });
        }
      });
    }
  }, [isLoaded, center, zoom, mapTypeControl, streetViewControl, fullscreenControl, onMapReady, onCenterChange]);

  // Actualizar marcadores
  useEffect(() => {
    if (!mapRef.current || !isLoaded) return;

    // Limpiar marcadores anteriores
    markersRef.current.forEach(marker => marker.setMap(null));
    markersRef.current = [];

    // Agregar nuevos marcadores
    const google = getGoogleMaps();
    if (!google) return;

    markers.forEach((markerData, index) => {
      const marker = addMarker(mapRef.current, {
        position: { lat: markerData.lat, lng: markerData.lng },
        title: markerData.title,
        draggable: markerData.draggable || false
      });

      if (marker) {
        markersRef.current.push(marker);

        if (markerData.infoWindow) {
          const infoWindow = createInfoWindow(markerData.infoWindow);
          
          marker.addListener('click', () => {
            // Cerrar otras ventanas de información
            markersRef.current.forEach((m, i) => {
              if (m.infoWindow && i !== index) {
                m.infoWindow.close();
              }
            });

            infoWindow.open({
              anchor: marker,
              map: mapRef.current
            });
            marker.infoWindow = infoWindow;

            if (onMarkerClick) {
              onMarkerClick(markerData, marker, index);
            }
          });
        } else if (onMarkerClick) {
          marker.addListener('click', () => {
            onMarkerClick(markerData, marker, index);
          });
        }

        if (markerData.draggable) {
          marker.addListener('dragend', () => {
            const pos = marker.getPosition();
            markerData.onDragEnd?.({
              lat: pos.lat(),
              lng: pos.lng()
            });
          });
        }
      }
    });
  }, [markers, isLoaded, onMarkerClick]);

  if (error) {
    return (
      <div className={`${className} flex items-center justify-center bg-slate-100`}>
        <div className="text-center">
          <p className="text-red-500 font-semibold">Error cargando el mapa</p>
          <p className="text-sm text-slate-500">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={className} ref={mapElement}>
      {!isLoaded && (
        <div className="flex items-center justify-center h-full bg-slate-100">
          <p className="text-slate-500">Cargando mapa...</p>
        </div>
      )}
      {children}
    </div>
  );
}
