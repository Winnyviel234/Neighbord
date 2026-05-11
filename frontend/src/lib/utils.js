export const money = (value = 0) =>
  new Intl.NumberFormat('es-DO', { style: 'currency', currency: 'DOP' }).format(Number(value || 0));

export const dateTime = (value) => (value ? new Intl.DateTimeFormat('es-DO', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) : '-');

export const shortDate = (value) => (value ? new Intl.DateTimeFormat('es-DO', { dateStyle: 'medium' }).format(new Date(value)) : '-');

export const roleLabel = {
  admin: 'Administrador',
  directiva: 'Vice Presidente',
  tesorero: 'Tesorero',
  vecino: 'Vecino',
  vocero: 'Vocero',
  secretaria: 'Secretaria'
};

export const datetimeLocalToISO = (datetimeLocalString) => {
  if (!datetimeLocalString) return null;
  try {
    // Parsear formato YYYY-MM-DDTHH:mm
    const [datePart, timePart] = datetimeLocalString.split('T');
    const [year, month, day] = datePart.split('-').map(Number);
    const [hour, minute] = timePart.split(':').map(Number);
    
    // Crear fecha como hora local del usuario
    const fecha = new Date(year, month - 1, day, hour, minute, 0);
    
    // Validar que la fecha sea válida
    if (isNaN(fecha.getTime())) {
      throw new Error('Invalid date');
    }
    
    // Convertir a ISO string considerando la zona horaria local
    const offset = fecha.getTimezoneOffset() * 60000;
    const localDate = new Date(fecha.getTime() - offset);
    return localDate.toISOString();
  } catch {
    throw new Error('Formato de fecha inválido');
  }
};

