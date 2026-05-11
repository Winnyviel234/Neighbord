# Manual del Usuario - Sistema Comunitario Neighbord

## Información General del Sistema

**Versión del Manual:** 2.0  
**Fecha de Actualización:** Mayo 2026  
**Sistema:** Neighbord - Plataforma de Gestión Comunitaria  
**Versión del Sistema:** 2.0.0  
**Desarrollado por:** Equipo de Desarrollo Neighbord  

---

## Tabla de contenido

- [Información General del Sistema](#información-general-del-sistema)
- [1. Introducción al Sistema](#1-introducción-al-sistema)
- [2. Primeros Pasos](#2-primeros-pasos)
- [3. Navegación e Interfaz de Usuario](#3-navegación-e-interfaz-de-usuario)
- [4. Módulo de Votaciones](#4-módulo-de-votaciones)
- [5. Módulo de Noticias y Comunicados](#5-módulo-de-noticias-y-comunicados)
- [6. Módulo de Reuniones y Asambleas](#6-módulo-de-reuniones-y-asambleas)
- [7. Módulo Financiero](#7-módulo-financiero)
- [8. Módulo de Solicitudes y Reclamos](#8-módulo-de-solicitudes-y-reclamos)
- [9. Módulo de Directiva](#9-módulo-de-directiva)
- [10. Configuración y Preferencias](#10-configuración-y-preferencias)
- [11. Funcionalidades Avanzadas](#11-funcionalidades-avanzadas)
- [12. Solución de Problemas](#12-solución-de-problemas)
- [13. Preguntas Frecuentes (FAQ)](#13-preguntas-frecuentes-faq)
- [14. Glosario de Términos](#14-glosario-de-términos)
- [15. Información de Contacto y Soporte](#15-información-de-contacto-y-soporte)
- [6. Perfil de usuario](#6-perfil-de-usuario)
- [7. Módulo de vecinos](#7-módulo-de-vecinos)
- [8. Reuniones](#8-reuniones)
- [9. Votaciones](#9-votaciones)
- [10. Solicitudes, quejas y reclamos](#10-solicitudes-quejas-y-reclamos)
- [11. Comunicados](#11-comunicados)
- [12. Noticias](#12-noticias)
- [13. Pagos](#13-pagos)
- [14. Finanzas](#14-finanzas)
- [15. Reportes](#15-reportes)
- [16. Notificaciones](#16-notificaciones)
- [17. Mapa y comunidad](#17-mapa-y-comunidad)
- [18. Permisos por rol](#18-permisos-por-rol)
- [19. Cierre de sesión](#19-cierre-de-sesión)
- [20. Problemas frecuentes](#20-problemas-frecuentes)
- [21. Recomendaciones de seguridad para usuarios](#21-recomendaciones-de-seguridad-para-usuarios)
- [22. Recomendaciones para administradores](#22-recomendaciones-para-administradores)
- [23. Flujo completo recomendado](#23-flujo-completo-recomendado)
- [24. Glosario](#24-glosario)
- [25. Soporte](#25-soporte)
- [26. Procedimientos por rol](#26-procedimientos-por-rol)
- [27. Matriz de responsabilidades](#27-matriz-de-responsabilidades)
- [28. Uso correcto de estados](#28-uso-correcto-de-estados)
- [29. Reglas de redacción profesional](#29-reglas-de-redacción-profesional)
- [30. Flujo recomendado para reuniones](#30-flujo-recomendado-para-reuniones)
- [31. Flujo recomendado para decisiones comunitarias](#31-flujo-recomendado-para-decisiones-comunitarias)
- [32. Buenas prácticas de transparencia](#32-buenas-prácticas-de-transparencia)
- [33. Escenarios de uso](#33-escenarios-de-uso)
- [34. Criterios de calidad para información ingresada](#34-criterios-de-calidad-para-información-ingresada)
- [35. Privacidad y convivencia digital](#35-privacidad-y-convivencia-digital)
- [36. Checklist mensual para directiva](#36-checklist-mensual-para-directiva)
- [37. Checklist mensual para tesorería](#37-checklist-mensual-para-tesorería)
- [38. Checklist mensual para administración](#38-checklist-mensual-para-administración)
- [39. Indicadores que debes vigilar](#39-indicadores-que-debes-vigilar)
- [40. Cierre](#40-cierre)
---

## 1. Introducción al Sistema

### 1.1 ¿Qué es Neighbord?

Neighbord es una plataforma integral de gestión comunitaria diseñada específicamente para juntas de vecinos, comunidades residenciales y asociaciones vecinales. El sistema centraliza todas las operaciones administrativas, comunicativas y financieras de una comunidad en una única interfaz web accesible desde cualquier dispositivo con conexión a internet.

**Características principales:**
- **Gestión Democrática:** Sistema de votaciones transparentes y participativas
- **Comunicación Efectiva:** Plataforma unificada para noticias, comunicados y anuncios
- **Administración Financiera:** Control completo de cuotas, pagos e ingresos comunitarios
- **Organización de Eventos:** Calendario integrado para reuniones y asambleas
- **Gestión de Solicitudes:** Sistema estructurado para reclamos y peticiones
- **Control de Acceso:** Seguridad avanzada con roles y permisos granulares

### 1.2 Beneficios para la Comunidad

**Para Residentes:**
- Acceso inmediato a toda la información comunitaria
- Participación activa en decisiones colectivas
- Gestión simplificada de pagos y cuotas
- Comunicación directa con la directiva
- Transparencia total en gastos e ingresos

**Para la Directiva:**
- Herramientas eficientes de gestión administrativa
- Automatización de procesos repetitivos
- Reportes detallados de actividad comunitaria
- Comunicación centralizada con residentes
- Control financiero avanzado

**Para la Comunidad en General:**
- Mayor transparencia y accountability
- Reducción de costos administrativos
- Mejora en la comunicación interna
- Fortalecimiento de la participación ciudadana
- Digitalización completa de procesos tradicionales

### 1.3 Arquitectura del Sistema

Neighbord está construido sobre una arquitectura moderna de tres capas:

**Capa de Presentación (Frontend):**
- Framework: React.js con Vite
- Estilos: Tailwind CSS
- Componentes: Biblioteca de componentes reutilizables
- Responsive: Diseño adaptativo para móviles y desktop

**Capa de Aplicación (Backend):**
- Framework: FastAPI (Python)
- Base de Datos: Supabase (PostgreSQL)
- Autenticación: JWT con OAuth2
- API RESTful: Endpoints documentados con OpenAPI

**Capa de Datos:**
- Base de Datos Principal: PostgreSQL vía Supabase
- Almacenamiento de Archivos: Supabase Storage
- Caché: Sistema integrado para optimización de rendimiento
- Backup: Estrategias automáticas de respaldo

### 1.4 Tipos de Usuarios y Roles

El sistema implementa un modelo de roles jerárquico con permisos granulares:

#### 1.4.1 Usuario Vecino
**Descripción:** Residente aprobado de la comunidad con acceso estándar.

**Permisos:**
- Lectura de noticias y comunicados
- Participación en votaciones activas
- Registro de asistencia a reuniones
- Creación y seguimiento de solicitudes
- Gestión de pagos personales
- Acceso a información pública

**Limitaciones:**
- No puede publicar contenido oficial
- No puede gestionar cuentas de otros usuarios
- No puede acceder a información financiera global

#### 1.4.2 Usuario Vice Presidenta
**Descripción:** Responsable de la coordinación ejecutiva y la definición de decisiones comunitarias.

**Permisos Adicionales:**
- Publicación de noticias y comunicados
- Creación y gestión de votaciones
- Organización de reuniones y eventos
- Revisión y resolución de solicitudes
- Acceso a reportes de actividad
- Gestión de miembros de la junta ejecutiva

#### 1.4.3 Usuario Vocero
**Descripción:** Encargado de la comunicación formal entre la directiva y la comunidad.

**Permisos Adicionales:**
- Publicación de comunicados oficiales
- Gestión de reuniones y anuncios públicos
- Coordinación de mensajería interna
- Acceso a reportes de actividad

#### 1.4.4 Usuario Secretaria
**Descripción:** Encargada del registro y la documentación de la gestión comunitaria.

**Permisos Adicionales:**
- Organización de actas y reuniones
- Gestión documental y archivos
- Acceso a reportes de actividad
- Apoyo en coordinación de comités

#### 1.4.5 Usuario Tesorero
**Descripción:** Responsable de la gestión financiera comunitaria.

**Permisos Adicionales:**
- Creación y gestión de cuotas
- Procesamiento de pagos
- Generación de reportes financieros
- Acceso completo a transacciones
- Configuración de métodos de pago
- Auditoría financiera

#### 1.4.4 Usuario Administrador
**Descripción:** Control total del sistema con capacidades de configuración.

**Permisos Adicionales:**
- Aprobación de cuentas de usuario
- Gestión de roles y permisos
- Configuración del sistema
- Acceso a logs y auditoría
- Gestión de sectores y zonas
- Configuración de políticas de seguridad

---

## 2. Primeros Pasos

### 2.1 Requisitos del Sistema

Para utilizar Neighbord de manera óptima, asegúrese de cumplir con los siguientes requisitos:

#### 2.1.1 Requisitos Técnicos Mínimos
- **Navegador Web:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Conexión a Internet:** Mínimo 1 Mbps estable
- **Resolución de Pantalla:** 1024x768 píxeles mínimo
- **JavaScript:** Habilitado (requerido para funcionalidad completa)

#### 2.1.2 Requisitos Recomendados
- **Navegador Web:** Última versión de Chrome o Firefox
- **Conexión a Internet:** 5 Mbps o superior
- **Resolución de Pantalla:** 1920x1080 o superior
- **Dispositivo:** Computadora, tablet o smartphone moderno

#### 2.1.3 Requisitos de Usuario
- **Correo Electrónico:** Dirección válida y activa
- **Información Personal:** Nombre completo, dirección, teléfono
- **Pertenencia Comunitaria:** Residencia verificada en el sector
- **Aceptación de Políticas:** Conformidad con términos de uso

### 2.2 Acceso a la Plataforma

#### 2.2.1 URL de Acceso
La plataforma está disponible en la URL proporcionada por su administrador comunitario. Generalmente sigue el formato:
```
https://[nombre-comunidad].neighbord.app
```

#### 2.2.2 Página de Inicio Pública
Al acceder a la URL principal, encontrará:
- **Información General:** Descripción de la comunidad y servicios
- **Noticias Destacadas:** Últimas publicaciones comunitarias
- **Votaciones Activas:** Consultas abiertas a la participación
- **Eventos Próximos:** Calendario de reuniones y asambleas
- **Enlaces de Acceso:** Botones para registro e inicio de sesión

#### 2.2.3 Navegación Inicial
- **Botón "Empezar":** Redirige al formulario de registro
- **Botón "Acceso":** Redirige al formulario de inicio de sesión
- **Botón "Ver Demo":** Muestra funcionalidades sin registro

### 2.3 Registro de Nueva Cuenta

#### 2.3.1 Paso 1: Acceso al Formulario
1. Desde la página principal, haga clic en "Empezar" o "Crear cuenta"
2. Será redirigido al formulario de registro
3. Verifique que se encuentra en una conexión segura (HTTPS)

#### 2.3.2 Paso 2: Información Personal
Complete los siguientes campos obligatorios:

**Información Básica:**
- **Nombre Completo:** Su nombre y apellidos tal como aparecen en documentos oficiales
- **Correo Electrónico:** Dirección de email válida y de uso frecuente
- **Teléfono:** Número de contacto con código de área
- **Fecha de Nacimiento:** Para verificación de edad (opcional en algunos casos)

**Información Residencial:**
- **Dirección Completa:** Calle, número, departamento, comuna
- **Sector/Barrio:** Seleccione de la lista desplegable
- **Número de Casa/Departamento:** Identificador específico
- **Tiempo de Residencia:** Años viviendo en la comunidad

#### 2.3.3 Paso 3: Credenciales de Acceso
- **Contraseña:** Mínimo 8 caracteres, combinación de letras, números y símbolos
- **Confirmar Contraseña:** Repita la contraseña para verificación
- **Pregunta de Seguridad:** Seleccione y responda una pregunta de recuperación

#### 2.3.4 Paso 4: Aceptación de Términos
- **Términos de Uso:** Lea y acepte las condiciones de servicio
- **Política de Privacidad:** Acepte el tratamiento de datos personales
- **Código de Ética Comunitaria:** Acepte las normas de convivencia

#### 2.3.5 Paso 5: Verificación y Envío
1. Revise todos los datos introducidos
2. Corrija cualquier error antes de enviar
3. Haga clic en "Crear Cuenta"
4. Recibirá confirmación de envío exitoso

### 2.4 Proceso de Aprobación

#### 2.4.1 Estado Inicial: Pendiente
Después del registro exitoso:
- Su cuenta queda en estado "Pendiente de Aprobación"
- Recibe un email de confirmación
- No puede acceder al dashboard completo
- Aparece mensaje informativo en pantalla de login

#### 2.4.2 Proceso de Verificación
La directiva o administrador realiza verificación:

**Verificaciones Automáticas:**
- Formato de email válido
- Unicidad de dirección de correo
- Coherencia de datos personales

**Verificaciones Manuales:**
- Confirmación de residencia en el sector
- Validación de identidad
- Verificación de no duplicidad
- Aprobación por directiva autorizada

#### 2.4.3 Tiempo de Aprobación
- **Tiempo Estimado:** 24-48 horas hábiles
- **Notificación:** Email automático al aprobarse
- **Acceso Inmediato:** Una vez aprobado, puede iniciar sesión

#### 2.4.4 Rechazo de Solicitud
En caso de rechazo:
- Recibe email explicando motivos
- Puede contactar a la directiva para aclaraciones
- Posibilidad de corregir y reenviar solicitud

### 2.5 Inicio de Sesión

#### 2.5.1 Acceso al Formulario
1. Desde página principal, clic en "Acceso" o "Iniciar Sesión"
2. Aparece formulario de login
3. Campos requeridos: email y contraseña

#### 2.5.2 Proceso de Autenticación
1. **Introduzca Email:** Use la dirección registrada
2. **Introduzca Contraseña:** Case-sensitive
3. **Haga Clic en "Entrar":** Inicia proceso de verificación

#### 2.5.3 Estados Posibles Post-Login

**Login Exitoso:**
- Redirección automática al dashboard
- Carga de preferencias de usuario
- Sincronización de notificaciones pendientes

**Cuenta Pendiente:**
- Mensaje: "Su cuenta está pendiente de aprobación"
- Sugerencia: "Contacte a la directiva para más información"

**Credenciales Incorrectas:**
- Mensaje: "Email o contraseña incorrectos"
- Opción: "Recuperar contraseña"

**Cuenta Inactiva:**
- Mensaje: "Cuenta temporalmente inactiva"
- Contacto sugerido con administración

### 2.6 Recuperación de Contraseña

#### 2.6.1 Inicio del Proceso
1. En pantalla de login, clic en "¿Olvidó su contraseña?"
2. Aparece formulario de recuperación
3. Introduzca email registrado

#### 2.6.2 Verificación de Seguridad
- Sistema envía código de verificación al email
- Código válido por 15 minutos
- Opción de reenvío limitado

#### 2.6.3 Cambio de Contraseña
1. Introduzca código recibido
2. Cree nueva contraseña segura
3. Confirme nueva contraseña
4. Sistema valida y actualiza

#### 2.6.4 Consideraciones de Seguridad
- Nueva contraseña debe ser diferente a anteriores
- Notificación automática de cambio exitoso
- Revisión de sesiones activas recomendada

---

## 3. Navegación e Interfaz de Usuario

### 3.1 Dashboard Principal

#### 3.1.1 Información General
El dashboard es la página principal después del login, mostrando:
- **Resumen Ejecutivo:** Estadísticas clave de la comunidad
- **Actividad Reciente:** Últimas noticias y eventos
- **Votaciones Activas:** Consultas abiertas
- **Recordatorios:** Eventos próximos y tareas pendientes

#### 3.1.2 Widgets Personalizables
- **Estadísticas de Comunidad:** Vecinos activos, votaciones, documentos
- **Calendario de Eventos:** Reuniones y asambleas programadas
- **Estado Financiero:** Resumen de cuotas y pagos
- **Notificaciones:** Mensajes del sistema y directiva

#### 3.1.3 Navegación Rápida
- **Accesos Directos:** Botones a módulos principales
- **Búsqueda Global:** Campo para buscar contenido
- **Menú de Usuario:** Configuración y logout

### 3.2 Barra de Navegación Superior

#### 3.2.1 Logo y Marca
- **Logo de Neighbord:** Enlace a dashboard
- **Nombre de Comunidad:** Configurable por administración
- **Indicador de Estado:** Online/offline

#### 3.2.2 Menú Principal
- **Dashboard:** Página principal
- **Noticias:** Sección de información comunitaria
- **Votaciones:** Participación democrática
- **Reuniones:** Calendario de eventos
- **Finanzas:** Gestión económica
- **Solicitudes:** Reclamos y peticiones

#### 3.2.3 Menú de Usuario
- **Perfil:** Información personal
- **Notificaciones:** Centro de mensajes
- **Configuración:** Preferencias de usuario
- **Cerrar Sesión:** Logout seguro

### 3.3 Menú Lateral

#### 3.3.1 Navegación por Módulos
Organizado por categorías principales:

**Información:**
- Noticias
- Comunicados
- Documentos

**Participación:**
- Votaciones
- Reuniones
- Asambleas

**Gestión:**
- Solicitudes
- Finanzas
- Directiva

#### 3.3.2 Indicadores Visuales
- **Números de Notificaciones:** En cada módulo
- **Estados de Actividad:** Colores indicadores
- **Accesos Rápidos:** Funciones frecuentes

### 3.4 Notificaciones del Sistema

#### 3.4.1 Tipos de Notificaciones
- **Sistema:** Actualizaciones y mantenimiento
- **Comunitarias:** Anuncios oficiales
- **Personales:** Mensajes directos
- **Recordatorios:** Eventos próximos

#### 3.4.2 Gestión de Notificaciones
- **Centro de Notificaciones:** Panel dedicado
- **Marcado como Leído:** Interfaz intuitiva
- **Configuración:** Preferencias por tipo
- **Historial:** Registro completo

### 3.5 Configuración de Perfil

#### 3.5.1 Información Personal
- **Datos Básicos:** Nombre, email, teléfono
- **Información Residencial:** Dirección, sector
- **Foto de Perfil:** Imagen personal
- **Información Adicional:** Campos personalizables

#### 3.5.2 Preferencias de Comunicación
- **Notificaciones por Email:** Selección granular
- **Frecuencia de Resúmenes:** Diaria, semanal, mensual
- **Canales de Comunicación:** Email, SMS, push
- **Zona Horaria:** Configuración regional

---

## 4. Módulo de Votaciones

### 4.1 Introducción a las Votaciones

Las votaciones en Neighbord permiten la participación democrática directa de todos los residentes en decisiones comunitarias importantes.

#### 4.1.1 Tipos de Votaciones
- **Votaciones Simples:** Sí/No o selección única
- **Votaciones Múltiples:** Selección de múltiples opciones
- **Votaciones de Prioridad:** Ordenamiento de preferencias
- **Votaciones de Presupuesto:** Asignación de recursos

#### 4.1.2 Estados de Votación
- **Borrador:** En preparación por directiva
- **Publicada:** Visible para votación
- **Activa:** Abierta para participación
- **Cerrada:** Finalizada, resultados disponibles
- **Archivada:** Histórica, solo consulta

### 4.2 Visualización de Votaciones Activas

#### 4.2.1 Lista de Votaciones
- **Vista General:** Todas las votaciones activas
- **Filtros Disponibles:** Por estado, fecha, categoría
- **Ordenamiento:** Por fecha de cierre, participación
- **Búsqueda:** Por palabras clave en título o descripción

#### 4.2.2 Detalle de Votación
- **Información Completa:** Título, descripción, contexto
- **Opciones de Voto:** Lista clara de alternativas
- **Fechas Importantes:** Inicio, cierre, resultados
- **Participación Actual:** Número de votos, porcentaje

### 4.3 Participación en Votaciones

#### 4.3.1 Proceso de Votación
1. **Selección de Opción:** Elija su preferencia
2. **Confirmación:** Revise selección antes de enviar
3. **Envío Seguro:** Transacción encriptada
4. **Confirmación:** Recibo de voto registrado

#### 4.3.2 Seguridad en Votaciones
- **Anonimato:** Sistema de votación secreta
- **No Repetición:** Un voto por usuario por consulta
- **Verificación:** Confirmación de registro exitoso
- **Auditoría:** Traza completa de participación

#### 4.3.3 Restricciones de Votación
- **Edad Mínima:** Verificación automática
- **Residencia:** Confirmación de pertenencia
- **Estado de Cuenta:** Usuario activo aprobado
- **Tiempo Límite:** Dentro del período activo

### 4.4 Historial de Votos

#### 4.4.1 Registro Personal
- **Votos Emitidos:** Historial completo
- **Fechas y Horarios:** Registro temporal preciso
- **Opciones Seleccionadas:** Detalle de decisiones
- **Resultados Finales:** Comparación con resultados globales

#### 4.4.2 Privacidad del Historial
- **Acceso Personal:** Solo el propio usuario
- **No Modificable:** Registro inmutable
- **Auditable:** Verificación de integridad
- **Exportable:** Descarga personal permitida

### 4.5 Creación de Votaciones (Directiva)

#### 4.5.1 Planificación de Votación
1. **Definición del Tema:** Objetivo claro y específico
2. **Análisis de Impacto:** Evaluación de consecuencias
3. **Consulta Preliminar:** Sondeo de opinión inicial
4. **Definición de Alcance:** Quiénes pueden votar

#### 4.5.2 Configuración Técnica
- **Título:** Claro y descriptivo
- **Descripción:** Contexto completo y objetivo
- **Opciones:** Número y claridad de alternativas
- **Fechas:** Inicio y cierre de votación
- **Tipo:** Simple, múltiple, ranking

#### 4.5.3 Publicación y Comunicación
- **Revisión Final:** Verificación de configuración
- **Publicación:** Activación de votación
- **Notificación:** Comunicación a comunidad
- **Seguimiento:** Monitoreo de participación

### 4.6 Gestión de Resultados

#### 4.6.1 Visualización de Resultados
- **Gráficos Interactivos:** Barras, pastel, tendencias
- **Estadísticas Detalladas:** Porcentajes, totales, distribución
- **Análisis Demográfico:** Por sector, edad, tiempo de residencia
- **Comparaciones Históricas:** Tendencias temporales

#### 4.6.2 Interpretación de Datos
- **Análisis de Participación:** Tasa de respuesta
- **Distribución de Votos:** Preferencias por opción
- **Factores Influyentes:** Correlaciones demográficas
- **Recomendaciones:** Sugerencias basadas en datos

#### 4.6.3 Acciones Post-Votación
- **Implementación:** Ejecución de decisión mayoritaria
- **Comunicación:** Informe de resultados a comunidad
- **Documentación:** Archivo oficial de votación
- **Lecciones Aprendidas:** Mejora de procesos futuros

---

## 5. Módulo de Noticias y Comunicados

### 5.1 Lectura de Noticias

#### 5.1.1 Página Principal de Noticias
- **Vista General:** Artículos destacados y recientes
- **Categorización:** Por temas y relevancia
- **Búsqueda Avanzada:** Filtros por fecha, autor, categoría
- **Vista Previa:** Resúmenes y miniaturas

#### 5.1.2 Lectura de Artículo Completo
- **Contenido Expandido:** Texto completo con formato
- **Multimedia Integrada:** Imágenes, videos, documentos
- **Información del Autor:** Perfil del publicador
- **Metadatos:** Fecha, categoría, etiquetas

### 5.2 Sistema de Comentarios

#### 5.2.1 Participación en Comentarios
- **Comentarios Públicos:** Diálogo comunitario
- **Respuestas Anidadas:** Conversaciones estructuradas
- **Moderación Automática:** Filtros de contenido
- **Notificaciones:** Alertas de respuestas

#### 5.2.2 Gestión Personal
- **Edición de Comentarios:** Modificación propia
- **Eliminación:** Retiro de contenido propio
- **Reportes:** Denuncia de contenido inapropiado
- **Historial:** Registro de participación

### 5.3 Publicación de Noticias (Directiva)

#### 5.3.1 Creación de Contenido
1. **Planificación:** Definición de tema y objetivo
2. **Investigación:** Recopilación de información
3. **Redacción:** Contenido claro y objetivo
4. **Revisión:** Verificación de hechos y ortografía

#### 5.3.2 Herramientas de Edición
- **Editor Visual:** Interfaz intuitiva de formato
- **Multimedia:** Integración de imágenes y documentos
- **Etiquetas:** Categorización y palabras clave
- **Programación:** Publicación inmediata o diferida

#### 5.3.3 Estrategia de Comunicación
- **Segmentación:** Audiencia objetivo
- **Canales:** Notificaciones push y email
- **Frecuencia:** Calendario editorial
- **Medición:** Análisis de engagement

### 5.4 Gestión de Comunicados Oficiales

#### 5.4.1 Tipos de Comunicados
- **Anuncios Generales:** Información para toda la comunidad
- **Comunicados Urgentes:** Avisos de importancia inmediata
- **Actualizaciones Administrativas:** Cambios en políticas
- **Convocatorias:** Llamados a reuniones especiales

#### 5.4.2 Protocolo de Publicación
- **Aprobación:** Revisión por directiva autorizada
- **Priorización:** Nivel de importancia y urgencia
- **Distribución:** Canales apropiados por tipo
- **Confirmación:** Verificación de recepción

### 5.5 Archivos Adjuntos y Multimedia

#### 5.5.1 Gestión de Archivos
- **Tipos Soportados:** PDF, DOC, XLS, imágenes, videos
- **Límites de Tamaño:** Restricciones por tipo de archivo
- **Organización:** Estructura de carpetas lógica
- **Acceso Seguro:** Control de permisos de descarga

#### 5.5.2 Optimización Multimedia
- **Compresión Automática:** Reducción de tamaño sin pérdida de calidad
- **Formatos Adaptativos:** Compatibilidad multiplataforma
- **Carga Progresiva:** Mejora de experiencia de usuario
- **Almacenamiento Eficiente:** Gestión inteligente de recursos

---

## 6. Módulo de Reuniones y Asambleas

### 6.1 Calendario de Eventos

#### 6.1.1 Vista de Calendario
- **Vista Mensual:** Eventos del mes completo
- **Vista Semanal:** Detalle por días
- **Vista Diaria:** Agenda detallada
- **Filtros:** Por tipo, sector, importancia

#### 6.1.2 Información de Eventos
- **Detalles Completos:** Hora, lugar, duración
- **Descripción:** Agenda y objetivos
- **Participantes:** Confirmados y pendientes
- **Documentos:** Actas y materiales previos

### 6.2 Registro de Asistencia

#### 6.2.1 Confirmación de Participación
- **Registro Previo:** Confirmación de asistencia
- **Check-in Digital:** Validación de presencia
- **Registro Tardío:** Justificación de llegada posterior
- **Ausencias:** Notificación de no participación

#### 6.2.2 Seguimiento de Asistencia
- **Estadísticas:** Tasa de participación por evento
- **Patrones:** Análisis de asistencia histórica
- **Recordatorios:** Notificaciones automáticas
- **Reportes:** Documentación oficial

### 6.3 Creación de Reuniones (Directiva)

#### 6.3.1 Planificación Estratégica
1. **Necesidad:** Justificación del evento
2. **Objetivos:** Resultados esperados claros
3. **Agenda:** Estructura detallada del encuentro
4. **Recursos:** Materiales y logística necesarios

#### 6.3.2 Configuración Técnica
- **Información Básica:** Título, descripción, fecha, hora
- **Ubicación:** Dirección física o virtual
- **Tipo de Evento:** Reunión, asamblea, taller
- **Invitados:** Lista de participantes requeridos

#### 6.3.3 Comunicación y Seguimiento
- **Convocatoria:** Invitaciones formales
- **Confirmaciones:** Seguimiento de RSVPs
- **Recordatorios:** Notificaciones previas
- **Documentación:** Minutas y actas post-evento

### 6.4 Actas y Minutas

#### 6.4.1 Creación de Actas
- **Plantillas Estandarizadas:** Formatos oficiales
- **Grabación Automática:** Notas durante el evento
- **Participantes:** Lista oficial de asistentes
- **Decisiones:** Registro de acuerdos y resoluciones

#### 6.4.2 Aprobación y Publicación
- **Revisión:** Verificación por directiva
- **Aprobación:** Firma digital autorizada
- **Publicación:** Disponibilización comunitaria
- **Archivo:** Conservación histórica

### 6.5 Notificaciones de Eventos

#### 6.5.1 Sistema de Alertas
- **Recordatorios Automáticos:** 24h, 1h antes
- **Cambios de Última Hora:** Notificaciones inmediatas
- **Confirmaciones:** Actualizaciones de estado
- **Actualizaciones:** Modificaciones en agenda

#### 6.5.2 Personalización
- **Preferencias Individuales:** Configuración personal
- **Canales Múltiples:** Email, SMS, app
- **Frecuencia Configurable:** Según preferencias
- **Opt-out:** Posibilidad de desactivar

---

## 7. Módulo Financiero

### 7.1 Dashboard Financiero

#### 7.1.1 Resumen Ejecutivo
- **Estado General:** Balance actual de la comunidad
- **Ingresos vs Egresos:** Comparativa mensual/anual
- **Deudas Pendientes:** Morosidad y cobros
- **Proyecciones:** Estimaciones futuras

#### 7.1.2 Indicadores Clave
- **Liquidez:** Disponibilidad inmediata
- **Rentabilidad:** Retorno de inversiones
- **Eficiencia:** Costos operativos
- **Sostenibilidad:** Capacidad de pago

### 7.2 Gestión de Cuotas y Pagos

#### 7.2.1 Configuración de Cuotas
- **Tipos de Cuota:** Fija, variable, extraordinaria
- **Periodicidad:** Mensual, trimestral, anual
- **Montos:** Por vivienda o porcentaje
- **Exenciones:** Casos especiales

#### 7.2.2 Proceso de Pago
1. **Generación:** Creación automática de cuotas
2. **Notificación:** Aviso a residentes
3. **Pago:** Múltiples métodos disponibles
4. **Confirmación:** Verificación y registro

### 7.3 Historial de Transacciones

#### 7.3.1 Registro Completo
- **Transacciones Individuales:** Detalle completo
- **Categorización:** Ingresos, egresos, transferencias
- **Períodos:** Filtros por fecha y tipo
- **Búsqueda:** Localización rápida

#### 7.3.2 Exportación de Datos
- **Formatos Disponibles:** PDF, Excel, CSV
- **Períodos Personalizables:** Rangos específicos
- **Filtros Aplicados:** Según criterios seleccionados
- **Programación:** Reportes automáticos

### 7.4 Reportes Financieros

#### 7.4.1 Tipos de Reportes
- **Balance General:** Estado patrimonial completo
- **Estado de Resultados:** P&L mensual/anual
- **Flujo de Caja:** Movimientos de efectivo
- **Análisis de Morosidad:** Deudas pendientes

#### 7.4.2 Generación Automática
- **Frecuencia:** Diaria, semanal, mensual
- **Distribución:** Email automático a directiva
- **Personalización:** Filtros y agrupaciones
- **Histórico:** Conservación de versiones anteriores

### 7.5 Métodos de Pago

#### 7.5.1 Opciones Disponibles
- **Transferencia Bancaria:** Datos completos
- **Pago en Línea:** Integración con plataformas
- **Pago Presencial:** En oficina administrativa
- **Domiciliación:** Cargo automático mensual

#### 7.5.2 Seguridad de Pagos
- **Encriptación:** Protección de datos sensibles
- **Verificación:** Confirmación de transacciones
- **Recibos Digitales:** Comprobantes automáticos
- **Soporte:** Asistencia en problemas de pago

---

## 8. Módulo de Solicitudes y Reclamos

### 8.1 Creación de Solicitudes

#### 8.1.1 Tipos de Solicitudes
- **Mantenimiento:** Reparaciones y mejoras
- **Seguridad:** Problemas de seguridad comunitaria
- **Administrativas:** Cambios en información personal
- **Sugerencias:** Propuestas de mejora

#### 8.1.2 Formulario Estructurado
- **Categorización:** Selección de tipo específico
- **Prioridad:** Urgente, normal, baja
- **Descripción Detallada:** Información completa del problema
- **Evidencia:** Fotos, documentos adjuntos

### 8.2 Seguimiento de Estado

#### 8.2.1 Estados de Solicitud
- **Recibida:** Registro inicial
- **En Revisión:** Evaluación por directiva
- **En Progreso:** Trabajo en solución
- **Resuelta:** Solución implementada
- **Cerrada:** Archivo final

#### 8.2.2 Comunicación Continua
- **Actualizaciones Automáticas:** Cambio de estado
- **Comentarios del Equipo:** Explicaciones detalladas
- **Solicitud de Información:** Datos adicionales requeridos
- **Confirmación Final:** Verificación de satisfacción

### 8.3 Categorización de Solicitudes

#### 8.3.1 Sistema de Etiquetas
- **Área Afectada:** Infraestructura, servicios, administración
- **Urgencia:** Crítica, alta, media, baja
- **Recursos Necesarios:** Humanos, materiales, presupuesto
- **Tiempo Estimado:** Inmediato, días, semanas, meses

#### 8.3.2 Reportes Estadísticos
- **Tendencias:** Problemas recurrentes
- **Eficiencia:** Tiempo de resolución promedio
- **Satisfacción:** Nivel de resolución exitosa
- **Mejoras:** Áreas de optimización

### 8.4 Resolución por Directiva

#### 8.4.1 Proceso de Evaluación
1. **Análisis Inicial:** Comprensión del problema
2. **Priorización:** Según urgencia e impacto
3. **Asignación:** Responsable específico
4. **Planificación:** Estrategia de solución

#### 8.4.2 Implementación y Seguimiento
- **Ejecución:** Desarrollo de la solución
- **Comunicación:** Actualizaciones al solicitante
- **Verificación:** Confirmación de resolución
- **Documentación:** Registro para futuras referencias

---

## 9. Módulo de Directiva

### 9.1 Gestión de Miembros

#### 9.1.1 Directorio de la Junta Ejecutiva
- **Perfiles Completos:** Información de cada miembro
- **Roles y Responsabilidades:** Funciones específicas para Vice Presidenta, Vocero, Secretaria y Tesorero
- **Contacto Directo:** Información de comunicación
- **Historial:** Trayectoria en la gestión comunitaria

#### 9.1.2 Administración de Roles
- **Asignación de Cargos:** Vice Presidenta, Vocero, Secretaria, Tesorero
- **Permisos Granulares:** Control de acceso según función
- **Rotación de Cargos:** Cambios periódicos
- **Capacitación:** Formación continua

### 9.2 Roles y Permisos

#### 9.2.1 Matriz de Permisos
- **Lectura:** Acceso a información
- **Escritura:** Creación y modificación
- **Aprobación:** Validación de acciones
- **Administración:** Control total de módulos

#### 9.2.2 Control de Acceso
- **Autenticación Multifactor:** Seguridad adicional
- **Logs de Actividad:** Auditoría completa
- **Restricciones Temporales:** Acceso limitado por horario
- **Alertas de Seguridad:** Detección de actividades sospechosas

### 9.3 Comunicación Interna

#### 9.3.1 Canales Privados
- **Mensajería Directa:** Comunicación entre miembros
- **Grupos de Trabajo:** Equipos específicos
- **Documentos Compartidos:** Colaboración en tiempo real
- **Videoconferencias:** Reuniones virtuales

#### 9.3.4 Protocolos de Comunicación
- **Cadena de Comando:** Jerarquía de decisiones
- **Escalamiento:** Procedimientos para situaciones críticas
- **Documentación:** Registro de comunicaciones importantes
- **Confidencialidad:** Protección de información sensible

### 9.4 Reportes de Actividad

#### 9.4.1 Dashboard Ejecutivo
- **Métricas Clave:** KPIs de gestión comunitaria
- **Tendencias:** Evolución temporal de indicadores
- **Alertas:** Situaciones que requieren atención
- **Comparativas:** Benchmarking interno

#### 9.4.2 Reportes Periódicos
- **Mensual:** Resumen ejecutivo completo
- **Trimestral:** Análisis detallado de tendencias
- **Anual:** Evaluación completa del período
- **Especiales:** Reportes por solicitud específica

---

## 10. Configuración y Preferencias

### 10.1 Perfil de Usuario

#### 10.1.1 Información Personal
- **Datos Básicos:** Nombre, email, teléfono, fecha nacimiento
- **Información Residencial:** Dirección completa, sector, tiempo residencia
- **Foto de Perfil:** Imagen personal personalizable
- **Información Adicional:** Campos configurables por comunidad

#### 10.1.2 Verificación de Datos
- **Validación Automática:** Formato y coherencia
- **Confirmación Manual:** Verificación por directiva
- **Actualización Segura:** Cambio controlado de información
- **Historial de Cambios:** Registro de modificaciones

### 10.2 Preferencias de Notificación

#### 10.2.1 Configuración por Módulo
- **Noticias:** Frecuencia de resúmenes
- **Votaciones:** Alertas de nuevas consultas
- **Reuniones:** Recordatorios de eventos
- **Finanzas:** Notificaciones de pagos

#### 10.2.2 Canales de Comunicación
- **Email:** Notificaciones por correo electrónico
- **SMS:** Mensajes de texto para urgencias
- **Push:** Notificaciones en aplicación móvil
- **Dashboard:** Alertas en plataforma web

### 10.3 Cambio de Contraseña

#### 10.3.1 Proceso Seguro
1. **Verificación de Identidad:** Confirmación actual contraseña
2. **Nueva Contraseña:** Creación de contraseña segura
3. **Confirmación:** Verificación de nueva contraseña
4. **Actualización:** Cambio inmediato en sistema

#### 10.3.2 Políticas de Seguridad
- **Complejidad:** Requisitos mínimos de fortaleza
- **Historial:** No reutilización de contraseñas anteriores
- **Expiración:** Cambio periódico recomendado
- **Recuperación:** Opciones de restablecimiento seguras

### 10.4 Configuración de Privacidad

#### 10.4.1 Control de Visibilidad
- **Información Pública:** Datos visibles para comunidad
- **Información Privada:** Datos solo para directiva
- **Participación Anónima:** Opciones de privacidad en votaciones
- **Historial Oculto:** Control de visibilidad de actividad

#### 10.4.2 Gestión de Datos
- **Exportación:** Descarga de datos personales
- **Eliminación:** Solicitud de borrado de cuenta
- **Portabilidad:** Transferencia de datos a otros sistemas
- **Consentimiento:** Control de uso de información

---

## 11. Funcionalidades Avanzadas

### 11.1 Búsqueda Global

#### 11.1.1 Motor de Búsqueda
- **Búsqueda por Texto:** Palabras clave en todo el contenido
- **Filtros Avanzados:** Por fecha, autor, categoría, módulo
- **Búsqueda por Voz:** Entrada por comandos de voz
- **Sugerencias Inteligentes:** Autocompletado y recomendaciones

#### 11.1.2 Resultados Organizados
- **Categorización:** Agrupación por tipo de contenido
- **Relevancia:** Ordenamiento por importancia
- **Previsualización:** Vista rápida de resultados
- **Navegación:** Paginación y filtros aplicados

### 11.2 Exportación de Datos

#### 11.2.1 Formatos Disponibles
- **PDF:** Documentos formateados para impresión
- **Excel:** Hojas de cálculo para análisis
- **CSV:** Datos planos para importación
- **JSON:** Formato estructurado para desarrolladores

#### 11.2.2 Alcance de Exportación
- **Datos Personales:** Información del propio usuario
- **Historial de Actividad:** Registros de participación
- **Reportes Financieros:** Transacciones y estados
- **Documentos Comunitarios:** Actas y comunicados

### 11.3 API Pública

#### 11.3.1 Endpoints Disponibles
- **Lectura de Información:** Acceso a datos públicos
- **Integración Externa:** Conexión con otros sistemas
- **Webhooks:** Notificaciones automáticas
- **Autenticación:** Tokens de acceso seguro

#### 11.3.2 Casos de Uso
- **Aplicaciones Móviles:** Desarrollo de apps complementarias
- **Integraciones Empresariales:** Conexión con sistemas externos
- **Automatización:** Procesos automatizados
- **Analytics:** Análisis de datos avanzado

### 11.4 Integraciones Externas

#### 11.4.1 Servicios Conectados
- **Pasarelas de Pago:** Procesamiento de transacciones
- **Servicios de Email:** Envío de notificaciones
- **Almacenamiento Cloud:** Backup y archivos
- **Herramientas de Comunicación:** Videoconferencias

#### 11.4.2 Configuración
- **Autenticación:** Credenciales de servicios externos
- **Permisos:** Control de acceso a integraciones
- **Monitoreo:** Estado de conexiones
- **Soporte:** Asistencia técnica especializada

---

## 12. Solución de Problemas

### 12.1 Problemas Comunes

#### 12.1.1 Problemas de Acceso
- **No puedo iniciar sesión:** Verificar email y contraseña
- **Cuenta pendiente:** Esperar aprobación de directiva
- **Contraseña olvidada:** Usar recuperación de contraseña
- **Cuenta bloqueada:** Contactar a administración

#### 12.1.2 Problemas de Rendimiento
- **Carga lenta:** Verificar conexión a internet
- **Página no responde:** Recargar navegador
- **Funciones no disponibles:** Actualizar navegador
- **Archivos no se cargan:** Verificar tamaño y formato

### 12.2 Mensajes de Error

#### 12.2.1 Errores de Validación
- **Campo requerido:** Completar información obligatoria
- **Formato inválido:** Corregir formato de datos
- **Duplicado:** Verificar información única
- **Permisos insuficientes:** Contactar a directiva

#### 12.2.2 Errores del Sistema
- **Error 500:** Problema interno, intentar más tarde
- **Error 403:** Acceso denegado, verificar permisos
- **Error 404:** Página no encontrada, verificar URL
- **Error 429:** Demasiadas solicitudes, esperar un momento

### 12.3 Contacto con Soporte

#### 12.3.1 Canales de Soporte
- **Email de Soporte:** soporte@neighbord.app
- **Chat en Vivo:** Disponible en horario laboral
- **Foro Comunitario:** Preguntas y respuestas entre usuarios
- **Base de Conocimiento:** Artículos de ayuda detallados

#### 12.3.2 Información a Proporcionar
- **Descripción del Problema:** Pasos para reproducir
- **Capturas de Pantalla:** Imágenes del error
- **Información del Navegador:** Versión y sistema operativo
- **Logs de Consola:** Errores técnicos si aplicable

### 12.4 Procedimientos de Recuperación

#### 12.4.1 Recuperación de Datos
- **Backup Automático:** Restauración de información
- **Exportación Manual:** Descarga de datos importantes
- **Sincronización:** Recuperación desde otros dispositivos
- **Asistencia Técnica:** Ayuda especializada para casos complejos

#### 12.4.2 Recuperación de Acceso
- **Reset de Contraseña:** Proceso seguro de recuperación
- **Verificación de Identidad:** Confirmación de propiedad de cuenta
- **Acceso Temporal:** Credenciales provisionales
- **Restauración de Permisos:** Recuperación de acceso perdido

---

## 13. Preguntas Frecuentes (FAQ)

### 13.1 Preguntas Generales

**¿Qué es Neighbord?**
Neighbord es una plataforma integral de gestión comunitaria que centraliza todas las operaciones administrativas, comunicativas y financieras de juntas de vecinos y comunidades residenciales.

**¿Es gratuito?**
El uso básico de la plataforma es gratuito para comunidades. Funcionalidades avanzadas pueden tener costos adicionales según el plan contratado.

**¿Necesito conocimientos técnicos?**
No, la plataforma está diseñada para ser intuitiva y no requiere conocimientos técnicos avanzados. La interfaz es similar a redes sociales comunes.

### 13.2 Problemas de Acceso

**¿Por qué mi cuenta está pendiente?**
Todas las cuentas nuevas requieren aprobación de la directiva para garantizar la seguridad de la comunidad. Este proceso normalmente toma 24-48 horas.

**¿Qué hago si olvidé mi contraseña?**
Use la opción "¿Olvidó su contraseña?" en la pantalla de inicio de sesión. Recibirá instrucciones por email para restablecerla.

**¿Puedo tener múltiples cuentas?**
No, cada residente debe tener una sola cuenta. Si necesita acceso adicional, contacte a la directiva.

### 13.3 Funcionalidades Específicas

**¿Cómo participo en votaciones?**
Una vez aprobado, puede acceder al módulo de votaciones desde el menú principal. Seleccione la votación deseada y siga las instrucciones en pantalla.

**¿Dónde veo las noticias?**
Las noticias están disponibles en el módulo "Noticias" del menú principal. Puede filtrar por fecha, categoría o buscar por palabras clave.

**¿Cómo pago mis cuotas?**
Acceda al módulo "Finanzas" donde encontrará sus cuotas pendientes. Seleccione el método de pago preferido y siga las instrucciones.

---

## 14. Glosario de Términos

**API (Application Programming Interface):** Interfaz de programación que permite la comunicación entre diferentes sistemas informáticos.

**Dashboard:** Panel principal de control que muestra información resumida y accesos rápidos a funciones principales.

**Directiva:** Órgano de gobierno de la comunidad, compuesto por presidente, secretario, tesorero y vocales.

**JWT (JSON Web Token):** Estándar para la creación de tokens de acceso que permite la autenticación segura.

**Morosidad:** Situación de deuda pendiente en el pago de cuotas comunitarias.

**Notificación Push:** Mensaje enviado automáticamente a dispositivos móviles o navegadores.

**Rol:** Conjunto de permisos y responsabilidades asignadas a un usuario dentro del sistema.

**Sector:** División geográfica o administrativa dentro de la comunidad (barrio, manzana, edificio).

**Token:** Cadena de caracteres que representa la autorización de acceso a recursos protegidos.

**Webhook:** Notificación automática enviada a una URL específica cuando ocurre un evento determinado.

**Widget:** Componente de interfaz que muestra información específica o proporciona funcionalidad particular.

---

## 15. Información de Contacto y Soporte

### 15.1 Soporte Técnico
- **Email Principal:** soporte@neighbord.app
- **Teléfono:** +56 2 1234 5678 (Lunes a Viernes, 9:00 - 18:00)
- **Chat en Vivo:** Disponible en la plataforma (horario laboral)
- **Tiempo de Respuesta:** 24 horas hábiles para consultas generales

### 15.2 Soporte Comunitario
- **Directiva Local:** Contacte a su presidente o secretario
- **Foro de Usuarios:** Comunidad de ayuda entre residentes
- **Documentación:** Base de conocimiento actualizada
- **Webinars:** Sesiones de capacitación mensuales

### 15.3 Información Legal
- **Política de Privacidad:** Disponible en [enlace]
- **Términos de Servicio:** Disponible en [enlace]
- **Código de Ética:** Normas de convivencia comunitaria

### 15.4 Actualizaciones y Novedades
- **Newsletter:** Suscripción mensual con actualizaciones
- **Blog:** Artículos sobre mejores prácticas comunitarias
- **Redes Sociales:** @NeighbordApp en todas las plataformas
- **Release Notes:** Historial de versiones y mejoras

---

**Fin del Manual**

Este manual se actualiza regularmente. Para la versión más reciente, visite la documentación en línea o contacte al soporte técnico.

*Neighbord - Más unión, mejor comunidad*

El dashboard es la primera pantalla después de iniciar sesión. Resume información útil para el día a día:

- Solicitudes recientes.
- Pagos o cuotas.
- Reuniones próximas.
- Votaciones activas.
- Comunicados destacados.
- Indicadores generales según el rol.

Un vecino ve información enfocada en su participación. Un directivo, tesorero o administrador puede ver además datos de gestión y seguimiento.

Si el dashboard no carga, revisa:

- Que tu sesión siga activa.
- Que tu cuenta esté aprobada.
- Que el backend esté funcionando.
- Que la conexión a internet no se haya interrumpido.

## 6. Perfil de usuario

El perfil muestra tus datos personales registrados en la plataforma. Desde esta sección puedes revisar información como:

- Nombre.
- Correo.
- Teléfono.
- Dirección.
- Sector.
- Rol.
- Estado de la cuenta.

Cuando el sistema permite edición, actualiza solo datos reales y verificables. Mantener teléfono y dirección correctos ayuda a la directiva a contactarte en casos importantes.

## 7. Módulo de vecinos

El módulo de vecinos funciona como padrón comunitario. Según tu rol, podrás consultar o administrar registros.

### 7.1 Para vecinos

Un vecino normalmente puede ver información limitada o pública de la comunidad, según las reglas definidas por la directiva. No debe poder editar datos de otros usuarios ni aprobar cuentas.

### 7.2 Para administración

Usuarios `admin`, `directiva` o `tesorero` pueden tener acceso a funciones de gestión:

- Listar vecinos.
- Filtrar por estado.
- Revisar cuentas pendientes.
- Aprobar registros.
- Editar datos básicos.
- Marcar estados administrativos.

### 7.3 Aprobar un vecino

Para aprobar una cuenta:

1. Entra al módulo `Vecinos`.
2. Busca el usuario con estado `pendiente`.
3. Verifica nombre, correo, dirección y sector.
4. Presiona la acción de aprobación.
5. Confirma que el estado cambió a `aprobado`.

Después de esto, el vecino podrá iniciar sesión. No es necesario entregar una contraseña nueva; usará la que creó durante el registro.

### 7.4 Buenas prácticas al aprobar cuentas

- No apruebes correos desconocidos.
- Evita aprobar registros sin dirección clara.
- Revisa duplicados antes de aprobar.
- Si tienes dudas, contacta al vecino por un canal oficial.
- No compartas capturas con datos personales en grupos públicos.

## 8. Reuniones

El módulo de reuniones permite consultar asambleas, sesiones de directiva, actividades comunitarias o encuentros programados.

Una reunión puede incluir:

- Título.
- Fecha.
- Hora.
- Lugar.
- Descripción.
- Estado.
- Lista de asistencia, si está habilitada.

Como vecino, úsalo para saber cuándo participar y qué temas se tratarán. Como directiva, úsalo para publicar convocatorias y mantener un historial organizado.

## 9. Votaciones

El módulo de votaciones permite participar en decisiones comunitarias de forma digital.

### 9.1 Antes de votar

Lee con calma:

- El título de la votación.
- La descripción de la propuesta.
- Las opciones disponibles.
- La fecha de cierre.
- Cualquier regla publicada por la directiva.

### 9.2 Emitir voto

1. Entra a `Votaciones`.
2. Abre la votación activa.
3. Selecciona tu opción.
4. Confirma tu voto.

Normalmente el sistema permite un voto por usuario. Una vez emitido, puede no ser editable, dependiendo de la configuración.

### 9.3 Resultados

Los resultados pueden mostrarse:

- En tiempo real.
- Al cerrar la votación.
- Solo para directiva.
- Públicamente para todos los vecinos.

La modalidad depende de las reglas comunitarias.

## 10. Solicitudes, quejas y reclamos

El módulo de solicitudes sirve para reportar situaciones y darles seguimiento formal.

Ejemplos:

- Alumbrado dañado.
- Ruido fuera de horario.
- Problemas de seguridad.
- Mantenimiento de áreas comunes.
- Limpieza.
- Daños en infraestructura.
- Peticiones a la directiva.

### 10.1 Crear una solicitud

1. Entra a `Solicitudes`.
2. Presiona la opción para crear una nueva solicitud.
3. Escribe un título claro.
4. Describe el problema con detalles.
5. Selecciona categoría y prioridad si aparecen disponibles.
6. Envía el registro.

Un buen reporte responde: qué pasa, dónde pasa, desde cuándo pasa y qué evidencia existe.

### 10.2 Estados de una solicitud

| Estado | Uso recomendado |
|---|---|
| `pendiente` | Recibida, aún sin atender |
| `en proceso` | La directiva o responsable está gestionando |
| `resuelto` | El caso fue solucionado |
| `rechazado` | No aplica, está duplicado o no corresponde |

### 10.3 Seguimiento

Revisa tus solicitudes periódicamente. Si un administrador agrega comentarios o cambia el estado, el historial permite entender qué ocurrió.

## 11. Comunicados

Los comunicados son avisos oficiales. Deben usarse para información importante como:

- Cortes de agua o electricidad.
- Convocatorias.
- Cambios de reglas.
- Avisos de mantenimiento.
- Alertas de seguridad.
- Fechas límite de pago.

Los vecinos deben revisar este módulo con frecuencia, porque puede contener información más confiable que mensajes reenviados por canales informales.

## 12. Noticias

Noticias permite publicar contenido informativo de la comunidad:

- Actividades realizadas.
- Mejoras del sector.
- Campañas.
- Recordatorios.
- Eventos.
- Reconocimientos.

La diferencia principal es que un comunicado suele ser oficial y urgente, mientras una noticia puede ser más informativa o comunitaria.

## 13. Pagos

El módulo de pagos ayuda a revisar cuotas, registrar comprobantes y consultar historial.

### 13.1 Qué puede ver un vecino

Un vecino puede revisar:

- Cuotas asignadas.
- Estado de pagos.
- Conceptos cobrados.
- Montos.
- Fechas.
- Historial reciente.

### 13.2 Estados de pago

| Estado | Significado |
|---|---|
| `pendiente` | Falta pagar o falta verificación |
| `verificado` | Pago confirmado por tesorería |
| `rechazado` | Comprobante inválido, monto incorrecto o información incompleta |

### 13.3 Recomendaciones para registrar pagos

- Verifica el monto antes de pagar.
- Guarda el comprobante.
- Sube información legible si el sistema lo solicita.
- No dupliques pagos por el mismo concepto.
- Si cometiste un error, contacta a tesorería.

## 14. Finanzas

El módulo de finanzas está orientado a tesorería, directiva y administración. Permite controlar ingresos, egresos, balances y reportes.

Puede incluir:

- Registro de ingresos.
- Registro de egresos.
- Categorización de movimientos.
- Balance general.
- Pagos recientes.
- Comprobantes.
- Estados de verificación.

La información financiera debe manejarse con cuidado. Solo usuarios autorizados deben modificar datos.

## 15. Reportes

Reportes permite obtener resúmenes para análisis, rendición de cuentas o presentación en reuniones.

Ejemplos:

- Reporte de vecinos.
- Reporte de pagos.
- Reporte financiero.
- Reporte de solicitudes.
- Reporte de votaciones.
- Exportación en PDF.
- Exportación en CSV.

Antes de compartir un reporte, revisa si contiene datos personales. No todos los reportes deben circular de forma pública.

## 16. Notificaciones

El sistema puede incluir centro de notificaciones y preferencias.

Úsalo para:

- Revisar avisos recientes.
- Marcar notificaciones como leídas.
- Ajustar preferencias si están habilitadas.
- Consultar alertas de pagos, solicitudes o comunicados.

Si no recibes notificaciones externas por correo, revisa también la bandeja de spam.

## 17. Mapa y comunidad

Cuando está habilitado, el mapa permite visualizar puntos de interés del sector:

- Incidencias.
- Áreas comunes.
- Referencias.
- Zonas de atención.
- Elementos de infraestructura.

El módulo de comunidad puede reunir información general sobre organización, sectores, noticias o datos vecinales relevantes.

## 18. Permisos por rol

| Módulo | vecino | tesorero | directiva | admin |
|---|---:|---:|---:|---:|
| Dashboard | Sí | Sí | Sí | Sí |
| Perfil | Sí | Sí | Sí | Sí |
| Vecinos | Limitado | Sí | Sí | Sí |
| Reuniones | Sí | Sí | Sí | Sí |
| Votaciones | Sí | Sí | Sí | Sí |
| Solicitudes | Sí | Sí | Sí | Sí |
| Comunicados | Sí | Sí | Sí | Sí |
| Noticias | Sí | Sí | Sí | Sí |
| Pagos | Sí | Sí | Sí | Sí |
| Finanzas | No | Sí | Sí | Sí |
| Directiva | No | Sí | Sí | Sí |
| Reportes | No | Sí | Sí | Sí |
| Administración total | No | No | Parcial | Sí |

Los permisos pueden ajustarse según la configuración técnica y las decisiones de la comunidad.

## 19. Cierre de sesión

Cuando termines, especialmente en una computadora compartida:

1. Abre el menú de usuario o la opción de salida.
2. Presiona `Cerrar sesión`.
3. Confirma que vuelves a la pantalla pública o de login.

No dejes tu sesión abierta en dispositivos que otras personas puedan usar.

## 20. Problemas frecuentes

### 20.1 Mi cuenta está pendiente

Es normal después del registro. Debes esperar aprobación. No podrás entrar al dashboard hasta que un administrador cambie tu cuenta a `aprobado`.

### 20.2 El sistema dice credenciales inválidas

Revisa:

- Que el correo esté escrito correctamente.
- Que no haya espacios al inicio o al final.
- Que la contraseña sea la correcta.
- Que estés usando el correo registrado.

### 20.3 Registré mi cuenta pero no me deja entrar

Si ves un mensaje de aprobación pendiente, la cuenta existe pero aún no fue aprobada. Contacta a la directiva si pasó mucho tiempo.

### 20.4 No veo un módulo

Puede ser por permisos. Por ejemplo, un vecino no debe ver administración financiera completa ni paneles internos.

### 20.5 Un dato mío está mal

Corrígelo desde perfil si el sistema lo permite. Si no puedes editarlo, contacta a administración.

### 20.6 El dashboard se queda cargando

Intenta:

- Recargar la página.
- Cerrar sesión e iniciar nuevamente.
- Verificar la conexión.
- Avisar al administrador si el problema continúa.

## 21. Recomendaciones de seguridad para usuarios

- No compartas tu contraseña.
- No uses la misma contraseña de otros servicios importantes.
- Cierra sesión en equipos compartidos.
- No publiques datos personales de otros vecinos fuera del sistema.
- Verifica que estás entrando al enlace correcto.
- Reporta actividades extrañas a la administración.

## 22. Recomendaciones para administradores

- Revisa cuentas pendientes con frecuencia.
- Aprueba solo usuarios verificados.
- Mantén roles mínimos necesarios.
- Corrige datos duplicados.
- Genera reportes antes de reuniones importantes.
- Mantén respaldo de información crítica.
- Evita compartir claves o accesos administrativos.

## 23. Flujo completo recomendado

1. El vecino abre la página.
2. Completa el registro.
3. El sistema crea la cuenta como `pendiente`.
4. El vecino ve un mensaje de espera y no entra al dashboard.
5. Administración revisa el registro.
6. Administración aprueba la cuenta.
7. El vecino inicia sesión.
8. El sistema valida credenciales y estado.
9. Si está `aprobado` o `activo`, entra al dashboard.
10. Desde el dashboard usa los módulos según su rol.

Este flujo garantiza orden, seguridad y control comunitario.

## 24. Glosario

- `Dashboard`: pantalla principal con resumen de información.
- `Rol`: nivel de permiso del usuario.
- `Estado`: situación administrativa de la cuenta.
- `Pendiente`: cuenta creada pero sin aprobación.
- `Aprobado`: cuenta autorizada para entrar.
- `Solicitud`: reporte, queja o petición.
- `Comunicado`: aviso oficial.
- `Cuota`: monto asignado a un vecino.
- `Reporte`: documento o resumen exportable.

## 25. Soporte

Si necesitas ayuda, reúne esta información antes de contactar al administrador:

- Correo usado para la cuenta.
- Pantalla donde ocurrió el problema.
- Mensaje exacto de error.
- Fecha y hora aproximada.
- Acción que intentabas realizar.

Con esos datos, el equipo técnico o administrativo podrá resolver el caso más rápido.

## 26. Procedimientos por rol

Esta sección describe cómo debe trabajar cada tipo de usuario para que la información del sistema se mantenga ordenada, confiable y útil para la comunidad.

### 26.1 Vecino

El vecino debe usar la plataforma como canal formal para consultar información y reportar necesidades. Su rutina recomendada es:

1. Iniciar sesión con su cuenta aprobada.
2. Revisar el dashboard para ver avisos, reuniones y votaciones.
3. Consultar comunicados antes de preguntar por canales informales.
4. Verificar cuotas o pagos pendientes.
5. Registrar solicitudes con una descripción completa.
6. Participar en votaciones activas dentro del plazo.
7. Cerrar sesión si usa un equipo compartido.

El vecino no debe crear cuentas duplicadas, compartir su contraseña ni usar solicitudes para temas que no correspondan a la comunidad.

### 26.2 Directiva

La directiva debe usar Neighbor como registro institucional. Sus tareas habituales son:

1. Revisar solicitudes nuevas.
2. Publicar comunicados oficiales.
3. Crear reuniones y convocatorias.
4. Dar seguimiento a acuerdos.
5. Consultar reportes antes de asambleas.
6. Coordinar con tesorería si una solicitud implica gasto.
7. Revisar cuentas pendientes cuando tenga autorización.

La directiva debe escribir comunicados claros, con fecha, alcance y responsable. Esto evita confusiones y reduce mensajes repetidos.

### 26.3 Tesorero

Tesorería debe mantener información financiera verificable. Su rutina recomendada es:

1. Revisar pagos registrados.
2. Validar comprobantes.
3. Cambiar estados de pago solo después de verificar.
4. Registrar ingresos y egresos con descripción clara.
5. Revisar balances antes de reuniones.
6. Descargar reportes para rendición de cuentas.
7. Marcar observaciones cuando un pago sea rechazado o incompleto.

El tesorero debe evitar editar datos financieros sin respaldo. Cada movimiento debe poder explicarse.

### 26.4 Administrador

El administrador es responsable del funcionamiento general. Sus tareas incluyen:

1. Aprobar o rechazar cuentas.
2. Mantener roles correctos.
3. Revisar el panel administrativo.
4. Detectar usuarios pendientes o inactivos.
5. Supervisar módulos críticos.
6. Apoyar recuperación operativa si un usuario no puede entrar.
7. Coordinar con el equipo técnico cuando haya fallos.

El administrador debe tener especial cuidado con permisos. No todos los usuarios necesitan acceso administrativo.

## 27. Matriz de responsabilidades

| Actividad | Vecino | Directiva | Tesorero | Admin |
|---|---:|---:|---:|---:|
| Registrarse | Responsable | Apoya | Apoya | Supervisa |
| Aprobar cuenta | No | Según permiso | Según permiso | Responsable |
| Publicar comunicado | Consulta | Responsable | Puede apoyar | Supervisa |
| Crear solicitud | Responsable | Puede crear | Puede crear | Puede crear |
| Atender solicitud | Consulta | Responsable | Apoya si hay gasto | Supervisa |
| Registrar pago | Responsable si aplica | Consulta | Responsable | Supervisa |
| Validar pago | No | Consulta | Responsable | Puede validar |
| Crear votación | Participa | Responsable | Apoya | Supervisa |
| Descargar reportes | No | Responsable | Responsable | Responsable |
| Cambiar roles | No | No | No | Responsable |

Esta matriz puede adaptarse a las reglas internas de la comunidad.

## 28. Uso correcto de estados

Los estados permiten que todos entiendan en qué punto está cada proceso.

### 28.1 Estados de usuarios

- Usa `pendiente` únicamente para registros sin revisar.
- Usa `aprobado` cuando ya se validó que la persona pertenece a la comunidad.
- Usa `activo` si la comunidad distingue entre aprobado y usuario operativo.
- Usa `inactivo` para cuentas que deben suspenderse temporalmente.
- Usa `rechazado` para registros que no cumplen los requisitos.
- Usa `moroso` solo si la política local permite reflejar deuda en estado de usuario.

No uses estados como castigo informal. Un cambio de estado debe tener una razón administrativa.

### 28.2 Estados de pagos

- `pendiente`: pago registrado o esperado, pero no confirmado.
- `verificado`: tesorería confirmó el pago.
- `rechazado`: el pago no pudo validarse.

Antes de rechazar, revisa si el comprobante está incompleto, si el monto no coincide o si corresponde a otro concepto.

### 28.3 Estados de solicitudes

- `pendiente`: solicitud recibida.
- `en revisión`: alguien debe evaluarla.
- `en proceso`: ya se está gestionando.
- `resuelto`: se solucionó.
- `rechazado`: no corresponde, está duplicada o no procede.

Cambiar estados con disciplina ayuda a que los vecinos confíen en el sistema.

## 29. Reglas de redacción profesional

Para mantener una comunicación institucional, usa estas recomendaciones:

- Escribe títulos cortos y específicos.
- Evita mensajes ambiguos como "problema urgente" sin detalle.
- Incluye fecha, hora y lugar cuando corresponda.
- Indica quién es responsable de la acción.
- No uses mayúsculas sostenidas.
- No publiques acusaciones personales.
- Evita compartir datos sensibles sin necesidad.
- Revisa ortografía antes de publicar comunicados.

Ejemplo poco claro:

```text
Hay problemas con la luz, arreglar urgente.
```

Ejemplo recomendado:

```text
Falla de luminaria en acceso norte
Desde el martes 5 de mayo, la luminaria frente al acceso norte se apaga de forma intermitente. Se solicita revisión eléctrica antes del fin de semana.
```

## 30. Flujo recomendado para reuniones

1. La directiva crea la reunión.
2. Se define fecha, hora, lugar y objetivo.
3. Se publica comunicado si la reunión requiere convocatoria formal.
4. Los vecinos revisan la agenda.
5. Durante la reunión se registran acuerdos.
6. Después de la reunión se publican resultados o acta.
7. Las tareas resultantes se convierten en solicitudes, proyectos o comunicados.

Este flujo transforma conversaciones en seguimiento real.

## 31. Flujo recomendado para decisiones comunitarias

1. La directiva identifica una decisión pendiente.
2. Se redacta una propuesta clara.
3. Se definen opciones de votación.
4. Se informa el plazo.
5. Los vecinos votan.
6. Se revisa el resultado.
7. Se publica la decisión.
8. Se ejecuta la acción acordada.

Una votación debe ser simple. Si el tema es complejo, conviene explicarlo primero en una reunión o comunicado.

## 32. Buenas prácticas de transparencia

Neighbor ayuda a ordenar la transparencia comunitaria, pero depende de cómo se use. Recomendaciones:

- Publicar reportes financieros periódicos.
- Mantener solicitudes actualizadas.
- Evitar cambios de estado sin explicación.
- Registrar reuniones importantes.
- No borrar información relevante sin respaldo.
- Usar reportes para rendición de cuentas.
- Separar opiniones personales de comunicados oficiales.

La transparencia no significa publicar todo sin filtro; significa que la información importante esté disponible para quien corresponde.

## 33. Escenarios de uso

### 33.1 Nuevo vecino

1. El vecino se registra.
2. El sistema lo deja pendiente.
3. El administrador revisa los datos.
4. El administrador aprueba la cuenta.
5. El vecino entra y completa su perfil.
6. El vecino consulta comunicados y pagos.

### 33.2 Pago mensual

1. Tesorería crea o revisa la cuota.
2. El vecino realiza el pago.
3. El vecino registra el comprobante si aplica.
4. Tesorería verifica el pago.
5. El estado cambia a `verificado`.
6. El pago aparece en reportes.

### 33.3 Solicitud de mantenimiento

1. El vecino crea la solicitud.
2. La directiva la revisa.
3. Se clasifica por prioridad.
4. Se asigna una acción.
5. Se actualiza el estado.
6. Al resolverse, se cierra.

### 33.4 Asamblea comunitaria

1. La directiva programa reunión.
2. Publica comunicado.
3. Los vecinos revisan detalles.
4. Se realiza asamblea.
5. Se registran acuerdos.
6. Se generan reportes o votaciones si hace falta.

## 34. Criterios de calidad para información ingresada

Un registro de buena calidad debe ser:

- Completo.
- Claro.
- Verificable.
- Respetuoso.
- Actualizado.
- Relacionado con la comunidad.

Evita datos incompletos como "mi casa", "lo de siempre" o "ya saben". El sistema funciona mejor cuando la información puede entenderla alguien que no estuvo en la conversación original.

## 35. Privacidad y convivencia digital

La plataforma contiene información comunitaria. Para proteger la convivencia:

- No uses datos de otros vecinos para fines personales.
- No compartas capturas de pantallas privadas.
- No publiques teléfonos o direcciones fuera del sistema.
- No uses solicitudes para conflictos personales sin base comunitaria.
- Mantén tono respetuoso.
- Reporta errores sin culpar públicamente a otros usuarios.

La tecnología organiza procesos, pero la buena convivencia depende de los usuarios.

## 36. Checklist mensual para directiva

- Revisar cuentas pendientes.
- Revisar solicitudes abiertas.
- Publicar resumen de actividades.
- Verificar reuniones próximas.
- Revisar votaciones activas o pendientes.
- Coordinar con tesorería el estado de pagos.
- Descargar reportes necesarios.
- Revisar datos de vecinos desactualizados.
- Comunicar decisiones relevantes.

## 37. Checklist mensual para tesorería

- Revisar pagos pendientes.
- Validar comprobantes.
- Registrar ingresos.
- Registrar egresos.
- Revisar balance.
- Preparar reporte financiero.
- Informar cuotas vencidas.
- Confirmar que los montos sean correctos.
- Guardar respaldo de reportes.

## 38. Checklist mensual para administración

- Revisar usuarios pendientes.
- Revisar roles asignados.
- Verificar que no haya accesos innecesarios.
- Confirmar que el panel admin cargue correctamente.
- Revisar módulos críticos.
- Coordinar respaldo con soporte técnico.
- Actualizar manuales si hubo cambios de proceso.

## 39. Indicadores que debes vigilar

| Indicador | Qué significa | Acción recomendada |
|---|---|---|
| Muchas cuentas pendientes | Hay vecinos esperando acceso | Revisar aprobaciones |
| Muchos pagos pendientes | Tesorería tiene validaciones atrasadas | Verificar comprobantes |
| Muchas solicitudes abiertas | Hay problemas sin seguimiento | Priorizar casos |
| Pocas votaciones activas | Puede faltar participación formal | Evaluar si hay decisiones pendientes |
| Reportes desactualizados | La información puede no reflejar la realidad | Generar nuevos reportes |

## 40. Cierre

Neighbor debe usarse como herramienta institucional de la comunidad. Mientras más constantes sean los usuarios al registrar información, actualizar estados y consultar módulos oficiales, más útil será para tomar decisiones, rendir cuentas y mejorar la convivencia.
