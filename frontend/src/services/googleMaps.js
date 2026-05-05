/**
 * Google Maps Service
 * Gestiona la inicialización y uso de la API de Google Maps
 */

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

let googleMapsLoaded = false;
let googleMapsPromise = null;

export const loadGoogleMaps = () => {
  if (googleMapsLoaded) {
    return Promise.resolve();
  }

  if (googleMapsPromise) {
    return googleMapsPromise;
  }

  googleMapsPromise = new Promise((resolve, reject) => {
    if (!GOOGLE_MAPS_API_KEY) {
      console.warn('Google Maps API key not configured. Map features will be limited.');
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=places,geometry,marker`;
    script.async = true;
    script.defer = true;

    script.onload = () => {
      googleMapsLoaded = true;
      resolve();
    };

    script.onerror = () => {
      console.error('Failed to load Google Maps API');
      reject(new Error('Failed to load Google Maps'));
    };

    document.head.appendChild(script);
  });

  return googleMapsPromise;
};

export const getGoogleMaps = () => {
  if (!googleMapsLoaded) {
    console.error('Google Maps not loaded yet');
    return null;
  }
  return window.google?.maps;
};

export const isGoogleMapsLoaded = () => googleMapsLoaded;

/**
 * Crear un mapa de Google Maps
 */
export const createMap = (element, options = {}) => {
  const google = getGoogleMaps();
  if (!google) return null;

  const defaultOptions = {
    zoom: 16,
    center: { lat: -16.5, lng: -68.15 },
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapTypeControl: true,
    streetViewControl: true,
    fullscreenControl: true,
    zoomControl: true,
    ...options
  };

  return new google.maps.Map(element, defaultOptions);
};

/**
 * Agregar marcador al mapa
 */
export const addMarker = (map, options = {}) => {
  const google = getGoogleMaps();
  if (!google) return null;

  const defaultOptions = {
    position: { lat: -16.5, lng: -68.15 },
    map: map,
    draggable: false,
    ...options
  };

  return new google.maps.Marker(defaultOptions);
};

/**
 * Crear info window (popup de información)
 */
export const createInfoWindow = (content) => {
  const google = getGoogleMaps();
  if (!google) return null;

  return new google.maps.InfoWindow({
    content: content
  });
};

/**
 * Buscar lugar por nombre
 */
export const searchPlace = (query) => {
  return new Promise((resolve, reject) => {
    const google = getGoogleMaps();
    if (!google) {
      reject(new Error('Google Maps not loaded'));
      return;
    }

    const service = new google.maps.places.PlacesService(document.createElement('div'));
    
    service.findPlaceFromQuery(
      {
        query: query,
        fields: ['formatted_address', 'geometry', 'name', 'photos']
      },
      (results, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK && results?.[0]) {
          resolve({
            name: results[0].name,
            address: results[0].formatted_address,
            lat: results[0].geometry.location.lat(),
            lng: results[0].geometry.location.lng()
          });
        } else {
          reject(new Error(`Place search failed: ${status}`));
        }
      }
    );
  });
};

/**
 * Obtener ubicación actual usando Geolocation API
 */
export const getCurrentLocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: Number(position.coords.latitude.toFixed(6)),
          lng: Number(position.coords.longitude.toFixed(6)),
          accuracy: position.coords.accuracy
        });
      },
      (error) => {
        reject(new Error(`Geolocation error: ${error.message}`));
      }
    );
  });
};

/**
 * Calcular distancia entre dos puntos (en km)
 */
export const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const google = getGoogleMaps();
  if (!google) return null;

  const point1 = new google.maps.LatLng(lat1, lng1);
  const point2 = new google.maps.LatLng(lat2, lng2);

  return google.maps.geometry.spherical.computeDistanceBetween(point1, point2) / 1000; // en km
};

/**
 * Crear polígono en el mapa
 */
export const createPolygon = (map, paths, options = {}) => {
  const google = getGoogleMaps();
  if (!google) return null;

  const defaultOptions = {
    paths: paths,
    strokeColor: '#FF0000',
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: '#FF0000',
    fillOpacity: 0.35,
    map: map,
    ...options
  };

  return new google.maps.Polygon(defaultOptions);
};

/**
 * Crear círculo en el mapa
 */
export const createCircle = (map, center, radius, options = {}) => {
  const google = getGoogleMaps();
  if (!google) return null;

  const defaultOptions = {
    strokeColor: '#4285F4',
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: '#4285F4',
    fillOpacity: 0.35,
    map: map,
    center: center,
    radius: radius, // en metros
    ...options
  };

  return new google.maps.Circle(defaultOptions);
};

/**
 * Obtener dirección a partir de coordenadas (reverse geocoding)
 */
export const getAddressFromCoords = (lat, lng) => {
  return new Promise((resolve, reject) => {
    const google = getGoogleMaps();
    if (!google) {
      reject(new Error('Google Maps not loaded'));
      return;
    }

    const geocoder = new google.maps.Geocoder();
    
    geocoder.geocode({ location: { lat, lng } }, (results, status) => {
      if (status === 'OK' && results?.[0]) {
        resolve(results[0].formatted_address);
      } else {
        reject(new Error(`Geocoding failed: ${status}`));
      }
    });
  });
};

/**
 * Obtener coordenadas a partir de dirección (geocoding)
 */
export const getCoordsFromAddress = (address) => {
  return new Promise((resolve, reject) => {
    const google = getGoogleMaps();
    if (!google) {
      reject(new Error('Google Maps not loaded'));
      return;
    }

    const geocoder = new google.maps.Geocoder();
    
    geocoder.geocode({ address: address }, (results, status) => {
      if (status === 'OK' && results?.[0]) {
        const loc = results[0].geometry.location;
        resolve({
          lat: loc.lat(),
          lng: loc.lng(),
          address: results[0].formatted_address
        });
      } else {
        reject(new Error(`Geocoding failed: ${status}`));
      }
    });
  });
};
