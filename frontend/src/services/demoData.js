const now = new Date();
const day = 24 * 60 * 60 * 1000;

const isoIn = (days, hour = 10) => {
  const date = new Date(now.getTime() + days * day);
  date.setHours(hour, 0, 0, 0);
  return date.toISOString();
};

export const demoData = {
  vecinos: [
    { id: 'demo-vecino-1', nombre: 'Ana Morales', email: 'ana.morales@neighbor.local', telefono: '+591 700-11223', direccion: 'Pasaje Los Robles 124', documento: 'CI-102334', rol: 'admin', estado: 'activo' },
    { id: 'demo-vecino-2', nombre: 'Carlos Rojas', email: 'carlos.rojas@neighbor.local', telefono: '+591 700-22441', direccion: 'Calle Jardin 58', documento: 'CI-284901', rol: 'tesorero', estado: 'activo' },
    { id: 'demo-vecino-3', nombre: 'Mariela Quispe', email: 'mariela.quispe@neighbor.local', telefono: '+591 700-99871', direccion: 'Av. Comunidad 310', documento: 'CI-771204', rol: 'directiva', estado: 'activo' },
    { id: 'demo-vecino-4', nombre: 'Jorge Salvatierra', email: 'jorge.salvatierra@neighbor.local', telefono: '+591 700-55390', direccion: 'Manzano B, Casa 17', documento: 'CI-552719', rol: 'vecino', estado: 'pendiente' },
    { id: 'demo-vecino-5', nombre: 'Lucia Fernandez', email: 'lucia.fernandez@neighbor.local', telefono: '+591 700-41802', direccion: 'Calle Las Flores 44', documento: 'CI-430981', rol: 'vecino', estado: 'moroso' }
  ],
  reuniones: [
    { id: 'demo-reunion-1', titulo: 'Asamblea ordinaria de mayo', descripcion: 'Revision de cuotas, seguridad y mantenimiento de areas comunes.', fecha: isoIn(6, 19), lugar: 'Sede vecinal', tipo: 'general', estado: 'programada' },
    { id: 'demo-reunion-2', titulo: 'Mesa de trabajo de seguridad', descripcion: 'Coordinacion con vecinos por sectores y rondas informativas.', fecha: isoIn(10, 18), lugar: 'Salon comunitario', tipo: 'general', estado: 'programada' },
    { id: 'demo-reunion-3', titulo: 'Reunion de directiva', descripcion: 'Preparacion de presupuestos y seguimiento de solicitudes abiertas.', fecha: isoIn(3, 20), lugar: 'Oficina de administracion', tipo: 'directiva', estado: 'programada' }
  ],
  votaciones: [
    { id: 'demo-votacion-1', titulo: 'Prioridad de mejoras del trimestre', descripcion: 'Elige la obra que deberia recibir prioridad presupuestaria.', fecha_inicio: isoIn(-1, 8), fecha_fin: isoIn(8, 22), opciones: ['Iluminacion publica', 'Camaras de seguridad', 'Jardin central'], estado: 'activa', total_votos: 23, opciones_stats: [{ opcion: 'Iluminacion publica', count: 12, percentage: 52.2 }, { opcion: 'Camaras de seguridad', count: 8, percentage: 34.8 }, { opcion: 'Jardin central', count: 3, percentage: 13.0 }] },
    { id: 'demo-votacion-2', titulo: 'Horario para la feria vecinal', descripcion: 'Definicion del horario mas conveniente para actividades de domingo.', fecha_inicio: isoIn(0, 8), fecha_fin: isoIn(5, 21), opciones: ['09:00 a 13:00', '10:00 a 14:00', '15:00 a 18:00'], estado: 'activa', total_votos: 18, opciones_stats: [{ opcion: '09:00 a 13:00', count: 5, percentage: 27.8 }, { opcion: '10:00 a 14:00', count: 11, percentage: 61.1 }, { opcion: '15:00 a 18:00', count: 2, percentage: 11.1 }] },
    { id: 'demo-votacion-3', titulo: 'Eleccion de nuevo tesorero', descripcion: 'Selecciona al vecino que sera tesorero para el proximo periodo.', fecha_inicio: isoIn(-3, 10), fecha_fin: isoIn(2, 18), opciones: ['election|role=tesorero|user=demo-vecino-2|name=Carlos Rojas', 'election|role=tesorero|user=demo-vecino-4|name=Jorge Salvatierra'], estado: 'activa', total_votos: 35, opciones_stats: [{ opcion: 'election|role=tesorero|user=demo-vecino-2|name=Carlos Rojas', count: 20, percentage: 65.0 }, { opcion: 'election|role=tesorero|user=demo-vecino-4|name=Jorge Salvatierra', count: 11, percentage: 35.0 }] },
    { id: 'demo-votacion-4', titulo: 'Mejoras en el parque infantil', descripcion: 'Elige la nueva instalacion para el area de juegos.', fecha_inicio: isoIn(-2, 9), fecha_fin: isoIn(6, 18), opciones: ['Columpios nuevos', 'Pista de patinaje', 'Jardin tematico'], estado: 'activa', total_votos: 42, opciones_stats: [{ opcion: 'Columpios nuevos', count: 21, percentage: 50.0 }, { opcion: 'Pista de patinaje', count: 13, percentage: 31.0 }, { opcion: 'Jardin tematico', count: 8, percentage: 19.0 }] },
    { id: 'demo-votacion-5', titulo: 'Fondo de seguridad', descripcion: 'Decide si aumentamos el presupuesto de vigilancia nocturna.', fecha_inicio: isoIn(-4, 10), fecha_fin: isoIn(4, 20), opciones: ['Aumentar 10%', 'Mantener igual', 'Reducir 5%'], estado: 'activa', total_votos: 31, opciones_stats: [{ opcion: 'Aumentar 10%', count: 16, percentage: 51.6 }, { opcion: 'Mantener igual', count: 11, percentage: 35.5 }, { opcion: 'Reducir 5%', count: 4, percentage: 12.9 }] },
    { id: 'demo-votacion-6', titulo: 'Calendario de limpieza', descripcion: 'Elige el mejor dia para las jornadas de limpieza comunitaria.', fecha_inicio: isoIn(-1, 9), fecha_fin: isoIn(7, 19), opciones: ['Sabado', 'Domingo', 'Viernes'], estado: 'activa', total_votos: 26, opciones_stats: [{ opcion: 'Sabado', count: 14, percentage: 53.8 }, { opcion: 'Domingo', count: 9, percentage: 34.6 }, { opcion: 'Viernes', count: 3, percentage: 11.6 }] },
    { id: 'demo-votacion-7', titulo: 'Instalacion de camaras', descripcion: 'Selecciona los sectores prioritarios para camaras de seguridad.', fecha_inicio: isoIn(-3, 8), fecha_fin: isoIn(3, 21), opciones: ['Entrada principal', 'Parque infantil', 'Calle central'], estado: 'activa', total_votos: 29, opciones_stats: [{ opcion: 'Entrada principal', count: 12, percentage: 41.4 }, { opcion: 'Parque infantil', count: 10, percentage: 34.5 }, { opcion: 'Calle central', count: 7, percentage: 24.1 }] },
    { id: 'demo-votacion-8', titulo: 'Taller de reciclaje', descripcion: 'Elige el tema principal para el proximo taller ambiental.', fecha_inicio: isoIn(-2, 10), fecha_fin: isoIn(5, 18), opciones: ['Compostaje', 'Señalizacion', 'Reciclaje creativo'], estado: 'activa', total_votos: 22, opciones_stats: [{ opcion: 'Compostaje', count: 9, percentage: 40.9 }, { opcion: 'Señalizacion', count: 8, percentage: 36.4 }, { opcion: 'Reciclaje creativo', count: 5, percentage: 22.7 }] },
    { id: 'demo-votacion-9', titulo: 'Horario del gimnasio comunitario', descripcion: 'Define las franjas mas utiles para el uso de la sala deportiva.', fecha_inicio: isoIn(-1, 8), fecha_fin: isoIn(6, 20), opciones: ['6-9 am', '4-7 pm', '7-9 pm'], estado: 'activa', total_votos: 34, opciones_stats: [{ opcion: '6-9 am', count: 10, percentage: 29.4 }, { opcion: '4-7 pm', count: 16, percentage: 47.1 }, { opcion: '7-9 pm', count: 8, percentage: 23.5 }] },
    { id: 'demo-votacion-10', titulo: 'Equipo de primeros auxilios', descripcion: 'Elige el material de seguridad que se comprara para la sede.', fecha_inicio: isoIn(-3, 7), fecha_fin: isoIn(4, 22), opciones: ['Botiquin completo', 'Defibrilador', 'Kits portatiles'], estado: 'activa', total_votos: 19, opciones_stats: [{ opcion: 'Botiquin completo', count: 9, percentage: 47.4 }, { opcion: 'Defibrilador', count: 6, percentage: 31.6 }, { opcion: 'Kits portatiles', count: 4, percentage: 21.0 }] },
    { id: 'demo-votacion-11', titulo: 'Decoracion de la plaza', descripcion: 'Selecciona la propuesta para paisajismo del espacio comun.', fecha_inicio: isoIn(-2, 9), fecha_fin: isoIn(6, 20), opciones: ['Arbustos nativos', 'Jardin colorido', 'Fuente central'], estado: 'activa', total_votos: 28, opciones_stats: [{ opcion: 'Arbustos nativos', count: 13, percentage: 46.4 }, { opcion: 'Jardin colorido', count: 10, percentage: 35.7 }, { opcion: 'Fuente central', count: 5, percentage: 17.9 }] },
    { id: 'demo-votacion-12', titulo: 'Noche cultural comunitaria', descripcion: 'Decide el tipo de eventos que gustaria tener en la plaza.', fecha_inicio: isoIn(-1, 10), fecha_fin: isoIn(4, 19), opciones: ['Musica en vivo', 'Talleres', 'Proyeccion de peliculas'], estado: 'activa', total_votos: 32, opciones_stats: [{ opcion: 'Musica en vivo', count: 15, percentage: 46.9 }, { opcion: 'Talleres', count: 10, percentage: 31.3 }, { opcion: 'Proyeccion de peliculas', count: 7, percentage: 21.8 }] }
  ],
  solicitudes: [
    { id: 'demo-solicitud-1', titulo: 'Luminaria con falla', descripcion: 'Poste principal de la esquina norte se apaga por intervalos.', categoria: 'infraestructura', prioridad: 'alta', estado: 'en revision' },
    { id: 'demo-solicitud-2', titulo: 'Poda de arboles', descripcion: 'Ramas invaden el cableado del pasaje Los Robles.', categoria: 'mantenimiento', prioridad: 'media', estado: 'abierta' },
    { id: 'demo-solicitud-3', titulo: 'Ruido fuera de horario', descripcion: 'Reporte preventivo para reforzar convivencia durante fines de semana.', categoria: 'convivencia', prioridad: 'media', estado: 'pendiente' }
  ],
  comunicados: [
    { id: 'demo-comunicado-1', titulo: 'Corte programado de agua', contenido: 'El mantenimiento de la red interna se realizara el sabado entre 08:00 y 12:00.', categoria: 'Servicios', publicado: true },
    { id: 'demo-comunicado-2', titulo: 'Campana de limpieza comunitaria', contenido: 'Se invita a residentes a participar por sectores con apoyo de la directiva.', categoria: 'Comunidad', publicado: true },
    { id: 'demo-comunicado-3', titulo: 'Actualizacion de cuotas', contenido: 'La tesoreria publicara el resumen mensual y recibira consultas esta semana.', categoria: 'Finanzas', publicado: true },
    { id: 'demo-comunicado-4', titulo: 'Inspeccion de seguridad', contenido: 'Rondas de vigilancia reforzadas los fines de semana a partir del proximo mes.', categoria: 'Seguridad', publicado: true },
    { id: 'demo-comunicado-5', titulo: 'Mantenimiento de areas verdes', contenido: 'Poda de arboles y jardineria en el jardin central durante la proxima semana.', categoria: 'Mantenimiento', publicado: true },
    { id: 'demo-comunicado-6', titulo: 'Reunion de vecinos', contenido: 'Convocatoria para la asamblea vecinal del proximo sabado en la sede.', categoria: 'Reunion', publicado: true },
    { id: 'demo-comunicado-7', titulo: 'Control de acceso', contenido: 'Se reforzaran las entradas principales con tarjetas de acceso nuevas.', categoria: 'Seguridad', publicado: true },
    { id: 'demo-comunicado-8', titulo: 'Nueva zona de reciclaje', contenido: 'Se habilito una segunda area de reciclaje junto al parque central.', categoria: 'Servicios', publicado: true },
    { id: 'demo-comunicado-9', titulo: 'Reparacion de banquetas', contenido: 'Iniciara la reparacion de veredas en la calle principal la proxima semana.', categoria: 'Infraestructura', publicado: true }
  ],
  noticias: [
    { id: 'demo-noticia-1', titulo: 'Nuevo punto de reciclaje vecinal', resumen: 'La comunidad habilito contenedores clasificados junto a la sede vecinal.', contenido: 'La comunidad habilito contenedores clasificados junto a la sede vecinal.', publicado: true },
    { id: 'demo-noticia-2', titulo: 'Vecinos coordinan mejoras de iluminacion', resumen: 'La directiva presento alternativas para reforzar seguridad en accesos principales.', contenido: 'La directiva presento alternativas para reforzar seguridad en accesos principales.', publicado: true },
    { id: 'demo-noticia-3', titulo: 'Exitoso evento deportivo comunitario', resumen: 'Participacion masiva en el torneo amistoso de futbol organizado por el sector norte.', contenido: 'Participacion masiva en el torneo amistoso de futbol organizado por el sector norte.', publicado: true },
    { id: 'demo-noticia-4', titulo: 'Capacitacion sobre primeros auxilios', resumen: 'Instructores certificados brindaron taller gratuito para vecinos interesados.', contenido: 'Instructores certificados brindaron taller gratuito para vecinos interesados.', publicado: true },
    { id: 'demo-noticia-5', titulo: 'Tarde de cine al aire libre', resumen: 'La plaza central recibira proyecciones gratuitas para familias el viernes.', contenido: 'La plaza central recibira proyecciones gratuitas para familias el viernes.', publicado: true },
    { id: 'demo-noticia-6', titulo: 'Jornada de salud gratuita', resumen: 'Se ofrecera control medico basico y vacunacion en la sede comunitaria.', contenido: 'Se ofrecera control medico basico y vacunacion en la sede comunitaria.', publicado: true },
    { id: 'demo-noticia-7', titulo: 'Plaza renovada', resumen: 'Se inauguro el area de descanso con bancos nuevos y plantas nativas.', contenido: 'Se inauguro el area de descanso con bancos nuevos y plantas nativas.', publicado: true },
    { id: 'demo-noticia-8', titulo: 'Taller de compostaje', resumen: 'Vecinos aprendieron a convertir residuos organicos en abono.', contenido: 'Vecinos aprendieron a convertir residuos organicos en abono.', publicado: true }
  ],
  directiva: [
    { id: 'demo-directiva-1', nombre: 'Ana Morales', email: 'ana.morales@neighbor.local', telefono: '+591 700-11223', cargo: 'presidente', periodo: '2026-2027', activo: true },
    { id: 'demo-directiva-2', nombre: 'Mariela Quispe', email: 'mariela.quispe@neighbor.local', telefono: '+591 700-99871', cargo: 'secretario', periodo: '2026-2027', activo: true },
    { id: 'demo-directiva-3', nombre: 'Carlos Rojas', email: 'carlos.rojas@neighbor.local', telefono: '+591 700-22441', cargo: 'tesorero', periodo: '2026-2027', activo: true },
    { id: 'demo-directiva-4', nombre: 'Nicolas Vargas', email: 'nicolas.vargas@neighbor.local', telefono: '+591 700-66102', cargo: 'vocal', periodo: '2026-2027', activo: true }
  ],
  cuotas: [
    { id: 'demo-cuota-1', titulo: 'Cuota mensual mayo', descripcion: 'Aporte ordinario para mantenimiento y seguridad.', monto: 80, fecha_vencimiento: isoIn(12, 23), estado: 'activa' },
    { id: 'demo-cuota-2', titulo: 'Fondo de iluminacion', descripcion: 'Compra e instalacion de luminarias LED.', monto: 45, fecha_vencimiento: isoIn(20, 23), estado: 'activa' }
  ],
  pagos: [
    { id: 'demo-pago-1', concepto: 'Cuota mensual abril', monto: 80, fecha_pago: isoIn(-6, 11), usuarios: { nombre: 'Ana Morales', email: 'ana.morales@neighbor.local' } },
    { id: 'demo-pago-2', concepto: 'Fondo de seguridad', monto: 55, fecha_pago: isoIn(-4, 15), usuarios: { nombre: 'Mariela Quispe', email: 'mariela.quispe@neighbor.local' } },
    { id: 'demo-pago-3', concepto: 'Cuota mensual mayo', monto: 80, fecha_pago: isoIn(-1, 10), usuarios: { nombre: 'Carlos Rojas', email: 'carlos.rojas@neighbor.local' } }
  ],
  transacciones: [
    { id: 'demo-transaccion-1', tipo: 'ingreso', categoria: 'Cuotas', monto: 4280, fecha: isoIn(-2, 9), descripcion: 'Recaudacion parcial de cuotas mensuales' },
    { id: 'demo-transaccion-2', tipo: 'ingreso', categoria: 'Aportes especiales', monto: 1350, fecha: isoIn(-9, 14), descripcion: 'Fondo de iluminacion comunitaria' },
    { id: 'demo-transaccion-3', tipo: 'egreso', categoria: 'Mantenimiento', monto: 980, fecha: isoIn(-5, 16), descripcion: 'Reparacion de luminarias y pintura de senaletica' },
    { id: 'demo-transaccion-4', tipo: 'egreso', categoria: 'Seguridad', monto: 720, fecha: isoIn(-12, 12), descripcion: 'Insumos para rondas vecinales' }
  ],
  notificacionesTiempoReal: [
    { id: 'demo-notificacion-1', tipo: 'Seguridad', titulo: 'Ronda vecinal iniciada', mensaje: 'Sector norte confirma recorrido preventivo.', fecha: isoIn(0, 20), estado: 'nuevo' },
    { id: 'demo-notificacion-2', tipo: 'Finanzas', titulo: 'Nuevo pago registrado', mensaje: 'Tesoreria actualizo el resumen de cuotas.', fecha: isoIn(0, 11), estado: 'visto' },
    { id: 'demo-notificacion-3', tipo: 'Directiva', titulo: 'Acta disponible', mensaje: 'Ya se puede revisar el resumen de la ultima reunion.', fecha: isoIn(-1, 18), estado: 'visto' }
  ],
  chatVecinal: [
    { id: 'demo-chat-1', autor: 'Ana Morales', mensaje: 'Buenas tardes, manana se revisa el jardin central a las 9.', fecha: isoIn(-1, 17) },
    { id: 'demo-chat-2', autor: 'Carlos Rojas', mensaje: 'Gracias Ana. Tambien llevo el resumen de gastos de abril.', fecha: isoIn(-1, 17) },
    { id: 'demo-chat-3', autor: 'Mariela Quispe', mensaje: 'Perfecto, avisare a los vecinos del pasaje Los Robles.', fecha: isoIn(0, 8) }
  ],
  mensajesDirectiva: [
    { id: 'demo-directiva-msg-1', asunto: 'Consulta por luminaria', mensaje: 'Solicito revisar el poste frente a la sede vecinal.', estado: 'recibido', fecha: isoIn(-2, 10) },
    { id: 'demo-directiva-msg-2', asunto: 'Propuesta de taller', mensaje: 'Podriamos organizar una charla de reciclaje para ninos.', estado: 'en revision', fecha: isoIn(-1, 16) }
  ],
  mapaSector: [
    { id: 'demo-punto-1', nombre: 'Sede vecinal', tipo: 'Administracion', estado: 'activo', x: 44, y: 48, descripcion: 'Lugar de reuniones, votaciones presenciales y atencion vecinal.' },
    { id: 'demo-punto-2', nombre: 'Jardin central', tipo: 'Area verde', estado: 'mantenimiento', x: 58, y: 34, descripcion: 'Area comun priorizada para poda, riego e iluminacion.' },
    { id: 'demo-punto-3', nombre: 'Acceso norte', tipo: 'Seguridad', estado: 'observacion', x: 28, y: 18, descripcion: 'Punto de rondas vecinales y control de iluminacion.' },
    { id: 'demo-punto-4', nombre: 'Punto de reciclaje', tipo: 'Servicios', estado: 'activo', x: 70, y: 68, descripcion: 'Contenedores clasificados para reciclaje comunitario.' },
    { id: 'demo-punto-5', nombre: 'Luminaria reportada', tipo: 'Incidencia', estado: 'pendiente', x: 35, y: 74, descripcion: 'Solicitud abierta para reparacion electrica.' }
  ]
};

export const demoLanding = {
  comunicados: demoData.comunicados,
  noticias: demoData.noticias,
  votaciones: demoData.votaciones,
  pagos: demoData.pagos,
  asambleas: demoData.reuniones.filter((item) => item.tipo === 'general'),
  directiva: demoData.directiva
};

export const demoDashboard = {
  vecinos: demoData.vecinos.length,
  solicitudes: demoData.solicitudes.length,
  reuniones: demoData.reuniones.length,
  votaciones: demoData.votaciones.filter((item) => item.estado === 'activa').length,
  pagos: demoData.pagos.length,
  rol: 'admin',
  resumen: {
    comunidad: 'Sistema comunitario activo',
    estado: 'Mostrando datos demo para presentacion'
  },
  ultimos_anuncios: [...demoData.comunicados, ...demoData.noticias].slice(0, 5),
  reportes_recientes: demoData.solicitudes,
  eventos_proximos: demoData.reuniones,
  votaciones_activas: demoData.votaciones,
  cuotas_activas: demoData.cuotas,
  pagos_recientes: demoData.pagos,
  notificaciones: [
    { titulo: 'Presentacion lista', mensaje: 'La pagina usa datos demo cuando no hay registros reales.' },
    { titulo: 'Votaciones', mensaje: `${demoData.votaciones.length} votaciones activas de ejemplo.` },
    { titulo: 'Finanzas', mensaje: `${demoData.cuotas.length} cuotas activas para mostrar.` }
  ]
};

export function isEmptyPayload(payload) {
  if (Array.isArray(payload)) return payload.length === 0;
  if (!payload || typeof payload !== 'object') return !payload;
  const values = Object.values(payload);
  if (!values.length) return true;
  return values.every((value) => (Array.isArray(value) ? value.length === 0 : !value));
}
