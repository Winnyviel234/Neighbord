import { Link } from 'react-router-dom';
import { ArrowRight, Bell, CalendarDays, CheckCircle2, Landmark, Mail, MapPin, Menu, MessageCircle, Newspaper, Phone, Vote, Users, TrendingUp, Shield, Zap, FileText, PieChart, Heart } from 'lucide-react';
import { useEffect, useMemo, useState, useRef, useCallback } from 'react';
import { dataService, mediaUrl } from '../services/api';
import { demoLanding } from '../services/demoData';
import { dateTime } from '../lib/utils';
import { useAuth } from '../context/AuthContext';

const empty = { comunicados: [], noticias: [], votaciones: [], asambleas: [], directiva: [], pagos: [] };
const withDemo = (payload) => ({
  comunicados: payload?.comunicados?.length ? payload.comunicados : demoLanding.comunicados,
  noticias: payload?.noticias?.length ? payload.noticias : demoLanding.noticias,
  votaciones: payload?.votaciones?.length ? payload.votaciones : demoLanding.votaciones,
  pagos: payload?.pagos?.length ? payload.pagos : demoLanding.pagos,
  asambleas: payload?.asambleas?.length ? payload.asambleas : demoLanding.asambleas,
  directiva: payload?.directiva?.length ? payload.directiva : demoLanding.directiva
});

const isDemoId = (id) => String(id || '').startsWith('demo-');

// Hook personalizado para animaciones de entrada
function useIntersectionObserver(ref, options = {}) {
  const [isIntersecting, setIsIntersecting] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsIntersecting(true);
          observer.unobserve(element); // Solo animar una vez
        }
      },
      { threshold: 0.1, ...options }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [ref, options]);

  return isIntersecting;
}

// Hook para prefetching de rutas
function usePrefetch() {
  const prefetchRef = useRef(new Set());

  const prefetchRoute = useCallback((route) => {
    if (prefetchRef.current.has(route)) return;

    // Prefetch de módulos de rutas comunes
    const routeModules = {
      '/app': () => import('../pages/DashboardPage.jsx'),
      '/app/noticias': () => import('../pages/NoticiasPage.jsx'),
      '/app/votaciones': () => import('../pages/VotacionesPage.jsx'),
      '/app/reuniones': () => import('../pages/ReunionesPage.jsx'),
      '/app/directiva': () => import('../pages/DirectivaPage.jsx'),
    };

    if (routeModules[route]) {
      routeModules[route]().catch(() => {});
      prefetchRef.current.add(route);
    }
  }, []);

  return prefetchRoute;
}

// Componente wrapper para secciones con animación de entrada
function SectionWrapper({ children, className = '', delay = 0 }) {
  const ref = useRef(null);
  const isVisible = useIntersectionObserver(ref, { rootMargin: '50px' });

  return (
    <section
      ref={ref}
      className={`transition-all duration-700 ease-out ${
        isVisible
          ? 'opacity-100 translate-y-0'
          : 'opacity-0 translate-y-8'
      } ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </section>
  );
}

function SkeletonCard({ className = '', type = 'default' }) {
  if (type === 'directiva') {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="bg-slate-200 rounded-t-2xl h-40"></div>
        <div className="p-6 space-y-3">
          <div className="bg-slate-200 rounded-full h-6 w-24 mx-auto"></div>
          <div className="bg-slate-200 rounded h-5 w-32 mx-auto"></div>
          <div className="bg-slate-200 rounded h-4 w-40 mx-auto"></div>
          <div className="bg-slate-200 rounded h-4 w-36 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`animate-pulse ${className}`}>
      <div className="bg-slate-200 rounded-lg h-48 mb-4"></div>
      <div className="space-y-3">
        <div className="bg-slate-200 rounded h-4 w-3/4"></div>
        <div className="bg-slate-200 rounded h-4 w-1/2"></div>
        <div className="bg-slate-200 rounded h-4 w-full"></div>
        <div className="bg-slate-200 rounded h-4 w-2/3"></div>
      </div>
    </div>
  );
}

function SkeletonGrid({ count = 3, className = '' }) {
  return (
    <div className={`grid gap-6 md:grid-cols-2 lg:grid-cols-3 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

function LazyImage({ src, alt, className = '', fallback: FallbackComponent, ...props }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  const handleLoad = () => setLoaded(true);
  const handleError = () => {
    setError(true);
    setLoaded(true);
  };

  if (error && FallbackComponent) {
    return <FallbackComponent className={className} {...props} />;
  }

  return (
    <div className={`relative ${className}`}>
      {!loaded && (
        <div className="absolute inset-0 bg-slate-200 animate-pulse rounded-lg flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-slate-300 border-t-slate-400 rounded-full animate-spin"></div>
        </div>
      )}
      <img
        src={src}
        alt={alt}
        loading="lazy"
        onLoad={handleLoad}
        onError={handleError}
        className={`transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'} ${className}`}
        {...props}
      />
    </div>
  );
}

export default function LandingPage() {
  const { user } = useAuth();
  const prefetchRoute = usePrefetch();
  const [data, setData] = useState(withDemo(empty));
  const [loading, setLoading] = useState(false);
  const [isRealData, setIsRealData] = useState(false);
  const [voting, setVoting] = useState({});
  const [voteMessage, setVoteMessage] = useState('');
  const [selectedOptions, setSelectedOptions] = useState({});

  const [paymentForm, setPaymentForm] = useState({
    concepto: 'Apoyo para ropa y ayuda comunitaria',
    monto: '',
    fecha_pago: new Date().toISOString().slice(0, 10),
    metodo: 'transferencia',
    referencia: ''
  });
  const [paymentMessage, setPaymentMessage] = useState('');
  const [paymentError, setPaymentError] = useState('');

  const isAuthenticated = Boolean(user);
  const greeting = user ? `Hola, ${user.nombre}` : null;
  const dataStatus = loading
    ? 'Cargando contenido de la comunidad...'
    : isRealData
      ? 'Contenido real cargado desde el sistema'
      : 'Mostrando contenido de demostración';

  const handleVote = async (votacionId, opcion) => {
    if (!user) {
      setVoteMessage('Debes iniciar sesión para votar');
      return;
    }
    if (isDemoId(votacionId)) {
      setVoteMessage('No se puede votar en datos de demostración.');
      return;
    }
    const selected = opcion || selectedOptions[votacionId];
    if (!selected) {
      setVoteMessage('Selecciona una opción para votar');
      return;
    }
    try {
      setVoting((prev) => ({ ...prev, [votacionId]: true }));
      await dataService.votar(votacionId, selected);
      setVoteMessage(`Voto registrado: ${optionLabel(selected)}`);
      setTimeout(() => setVoteMessage(''), 3000);
      await loadLanding();
    } catch (err) {
      setVoteMessage(err.response?.data?.detail || 'Error al votar');
      setTimeout(() => setVoteMessage(''), 3000);
    } finally {
      setVoting((prev) => ({ ...prev, [votacionId]: false }));
    }
  };

  const handlePaymentSubmit = async (event) => {
    event.preventDefault();
    if (!user) {
      setPaymentError('Debes iniciar sesión para registrar un pago.');
      return;
    }
    try {
      await dataService.crearPagoSolicitud({
        vecino_id: user.id,
        concepto: paymentForm.concepto,
        monto: Number(paymentForm.monto),
        fecha_pago: paymentForm.fecha_pago,
        metodo: paymentForm.metodo,
        referencia: paymentForm.referencia || null
      });
      setPaymentMessage('Pago registrado en la base de datos. Gracias por apoyar a la comunidad.');
      setPaymentError('');
      setPaymentForm({
        concepto: 'Apoyo para ropa y ayuda comunitaria',
        monto: '',
        fecha_pago: new Date().toISOString().slice(0, 10),
        metodo: 'transferencia',
        referencia: ''
      });
      await loadLanding();
      setTimeout(() => setPaymentMessage(''), 4000);
    } catch (err) {
      setPaymentError(err.response?.data?.detail || 'Error al registrar el pago, intenta nuevamente.');
      setPaymentMessage('');
      setTimeout(() => setPaymentError(''), 4000);
    }
  };

  const loadLanding = async () => {
    setLoading(true);
    try {
      const payload = await dataService.landing();
      const votacionesReales = (payload?.votaciones || []).filter((v) => !isDemoId(v.id));
      const hasRealData = ['comunicados', 'noticias', 'votaciones', 'pagos', 'asambleas', 'directiva']
        .some((key) => Array.isArray(payload?.[key]) && payload[key].some((item) => !isDemoId(item?.id)));
      setIsRealData(hasRealData);
      setData({
        comunicados: payload?.comunicados?.length ? payload.comunicados : demoLanding.comunicados,
        noticias: payload?.noticias?.length ? payload.noticias : demoLanding.noticias,
        votaciones: votacionesReales.length > 0 ? votacionesReales : demoLanding.votaciones,
        pagos: payload?.pagos?.length ? payload.pagos : demoLanding.pagos,
        asambleas: payload?.asambleas?.length ? payload.asambleas : demoLanding.asambleas,
        directiva: payload?.directiva?.length ? payload.directiva : demoLanding.directiva
      });
    } catch {
      setData(withDemo(empty));
      setIsRealData(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLanding();
    // Prefetch rutas comunes después de cargar datos
    setTimeout(() => {
      prefetchRoute('/app');
      prefetchRoute('/app/noticias');
      prefetchRoute('/app/votaciones');
    }, 2000);
  }, []);

  const realVotaciones = useMemo(() => {
    return (data.votaciones || []).slice(0, 6);
  }, [data.votaciones]);

  const votingStats = useMemo(() => {
    if (!realVotaciones?.length) return null;
    const totalVotos = realVotaciones.reduce((sum, v) => sum + (v.total_votos || 0), 0);
    return {
      total: realVotaciones.length,
      totalVotos,
      withStats: realVotaciones.filter(v => v.opciones_stats?.length > 0).length
    };
  }, [realVotaciones]);

  const stats = useMemo(() => {
    const votacionesActivas = realVotaciones.filter((item) => item.estado === 'activa').length;
    const documentosCount = data.comunicados.length + data.noticias.length;

    return [
      { icon: Users, value: '324', label: 'Vecinos activos', sub: 'Participantes conectados', color: 'from-blue-500 to-blue-600' },
      { icon: Vote, value: `${votacionesActivas}`, label: 'Votaciones activas', sub: 'Consultas abiertas del barrio', color: 'from-green-500 to-green-600' },
      { icon: FileText, value: `${documentosCount}`, label: 'Documentos', sub: 'Comunicados y noticias disponibles', color: 'from-purple-500 to-purple-600' },
      { icon: PieChart, value: '$125K', label: 'Fondos comunitarios', sub: 'Presupuesto estimado', color: 'from-orange-500 to-orange-600' }
    ];
  }, [data, realVotaciones]);

  return (
    <main className="min-h-screen bg-[#f7fbfd] text-slate-900">
      {/* Navbar */}
      <section className="sticky top-0 z-50 border-b border-white/60 bg-white/80 backdrop-blur-xl">
        <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="relative h-11 w-11 rounded-xl bg-gradient-to-br from-neighbor-blue to-neighbor-green p-2 shadow-md group-hover:shadow-lg transition">
              <img src="/neighbor-logo.png" alt="Neighbord" className="h-full w-full object-contain invert" />
            </div>
            <div>
              <p className="text-xl font-black text-neighbor-navy">Neighbord</p>
              <p className="text-[10px] font-bold text-neighbor-green -mt-1">Más unión, mejor comunidad</p>
            </div>
          </Link>
          <nav className="hidden items-center gap-8 text-sm font-bold text-slate-600 lg:flex">
            <a href="#caracteristicas" className="hover:text-neighbor-blue transition">Características</a>
            <a href="#actividad" className="hover:text-neighbor-blue transition">Actividad</a>
            <a href="#directiva" className="hover:text-neighbor-blue transition">Directiva</a>
            <a href="#contacto" className="hover:text-neighbor-blue transition">Contacto</a>
          </nav>
          <div className="flex items-center gap-3">
            <Link to="/login" className="hidden rounded-lg border border-neighbor-blue/30 px-4 py-2 text-sm font-bold text-neighbor-blue transition hover:bg-neighbor-mist hover:border-neighbor-blue sm:inline-flex">Acceso</Link>
            <Link to="/registro" className="btn-primary rounded-lg">Empezar →</Link>
            <button className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 text-neighbor-navy lg:hidden hover:bg-slate-100 transition" aria-label="Abrir menu">
              <Menu className="h-5 w-5" />
            </button>
          </div>
        </header>
      </section>

      {/* Hero Section */}
      <SectionWrapper className="overflow-hidden bg-neighbor-mist">
        <div className="mx-auto grid min-h-[72vh] max-w-7xl items-center gap-12 px-6 py-14 lg:grid-cols-[0.95fr_1.05fr]">
          <div>
            <p className="text-sm font-black uppercase tracking-[0.24em] text-neighbor-green">Sistema comunitario real</p>
            <h1 className="mt-4 max-w-2xl text-5xl font-black leading-[1.02] text-neighbor-navy md:text-7xl">Junta de vecinos organizada en un solo lugar</h1>
            <p className="mt-6 max-w-2xl text-lg font-semibold leading-8 text-slate-700">
              Neighbord conecta asambleas, votaciones, comunicados, noticias, cuotas, finanzas y directiva con datos reales para que la comunidad funcione con claridad.
            </p>
            <p className="mt-4 inline-flex items-center rounded-full bg-white/80 px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm">
              {loading ? 'Actualizando contenido comunitario...' : 'Información real y ejemplos demostrativos disponibles.'}
            </p>
            {isAuthenticated ? (
              <div className="mt-6 rounded-3xl border border-neighbor-blue/20 bg-neighbor-blue/5 p-5 text-sm text-neighbor-navy">
                <p className="font-semibold">{greeting}</p>
                <p className="mt-2">Accede al panel para gestionar tu sector, enviar solicitudes y participar en votaciones.</p>
              </div>
            ) : null}
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/registro" className="btn-primary px-5 py-3">Crear cuenta <ArrowRight className="h-4 w-4" /></Link>
              {isAuthenticated ? (
                <Link to="/app" className="btn-secondary px-5 py-3">Ir al panel</Link>
              ) : (
                <a href="#actividad" className="btn-secondary px-5 py-3">Ver actividad</a>
              )}
            </div>
            <div className="mt-10 grid max-w-xl gap-3 sm:grid-cols-3">
              {[
                ['Votaciones', 'Participación clara'],
                ['Comunicados', 'Avisos oficiales'],
                ['Finanzas', 'Cuentas visibles']
              ].map(([title, text]) => (
                <div key={title} className="border-l-4 border-neighbor-green bg-white px-4 py-3 shadow-sm">
                  <p className="font-black text-neighbor-navy">{title}</p>
                  <p className="mt-1 text-xs font-semibold text-slate-500">{text}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="order-1 flex justify-center lg:order-2">
            <div className="w-full max-w-xl bg-white p-8 shadow-soft">
              <img src="/neighbor-logo.png" alt="Logo Neighbord" className="mx-auto max-h-[460px] w-full object-contain" />
            </div>
          </div>
        </div>
      </SectionWrapper>

      {/* Statistics Section */}
      <SectionWrapper className="py-12 bg-white/30 backdrop-blur-sm" delay={200}>
        <div className="mx-auto max-w-7xl px-6">
          <div className="grid md:grid-cols-4 gap-6">
            {stats.map(({ icon: Icon, value, label, sub, color }) => (
              <div key={label} className="group bg-white/60 backdrop-blur-sm rounded-2xl border border-white/80 p-6 hover:border-neighbor-blue/40 hover:shadow-lg transition">
                <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${color} text-white shadow-lg`}>
                  <Icon className="h-6 w-6" />
                </div>
                <p className="mt-4 text-3xl font-black text-neighbor-navy">{value}</p>
                <p className="mt-1 text-sm font-semibold text-slate-600">{label}</p>
                <p className="mt-2 text-sm text-slate-500">{sub}</p>
              </div>
            ))}
          </div>
        </div>
      </SectionWrapper>

      {/* Features Section */}
      <SectionWrapper id="caracteristicas" className="py-20" delay={400}>
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-sm font-bold text-neighbor-green uppercase tracking-wider">características</p>
            <h2 className="mt-3 text-4xl font-black text-neighbor-navy">Todo lo que necesita tu comunidad</h2>
            <p className="mt-4 text-lg text-slate-600">Herramientas poderosas para organizar, comunicar y decidir juntos</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              [Vote, 'Votaciones Transparentes', 'Decisiones democráticas en tiempo real con resultados claros y participación segura.', 'from-blue-500 to-blue-600'],
              [Bell, 'Comunicados Efectivos', 'Avisos oficiales que llegan a todos, categorizados y organizados para fácil acceso.', 'from-indigo-500 to-indigo-600'],
              [PieChart, 'Finanzas Claras', 'Dashboard completo de ingresos, egresos, cuotas y reportes auditables.', 'from-purple-500 to-purple-600'],
              [Users, 'Directiva Conectada', 'Gestión de roles, perfiles y comunicación directa con la administración.', 'from-pink-500 to-pink-600'],
              [FileText, 'Documentos Centralizados', 'Biblioteca digital de actas, resoluciones y documentos importantes.', 'from-orange-500 to-orange-600'],
              [MapPin, 'Mapa Interactivo', 'Ubicación del sector, puntos clave e información de acceso.', 'from-green-500 to-green-600'],
            ].map(([Icon, title, text, color]) => (
              <div key={title} className="group bg-white/60 backdrop-blur-sm rounded-2xl border border-white/80 p-7 hover:border-neighbor-blue/40 hover:shadow-lg hover:-translate-y-1 transition">
                <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${color} text-white shadow-lg group-hover:scale-110 transition`}>
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="mt-4 text-lg font-black text-neighbor-navy">{title}</h3>
                <p className="mt-2 text-slate-600 leading-relaxed">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </SectionWrapper>

      {/* Votaciones Section */}
      <SectionWrapper className="py-20 bg-white/30 backdrop-blur-sm" delay={600}>
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-12">
            <div>
              <p className="text-sm font-bold text-neighbor-green uppercase tracking-wider">en votación</p>
              <h2 className="mt-2 text-4xl font-black text-neighbor-navy">Votaciones activas</h2>
            </div>
            {votingStats && (
              <div className="flex gap-2">
                <span className="inline-flex items-center gap-2 bg-white/80 rounded-full px-4 py-2 border border-neighbor-blue/20 text-sm font-bold text-neighbor-blue">
                  <Vote className="h-4 w-4" />
                  {realVotaciones.length} activas
                </span>
                {votingStats.totalVotos > 0 && (
                  <span className="inline-flex items-center gap-2 bg-green-50 rounded-full px-4 py-2 border border-green-200 text-sm font-bold text-green-700">
                    <TrendingUp className="h-4 w-4" />
                    {votingStats.totalVotos} votos
                  </span>
                )}
              </div>
            )}
          </div>

          {voteMessage && (
            <div className="mb-6 rounded-xl bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 p-4 text-sm font-semibold text-green-700 flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5" />
              {voteMessage}
            </div>
          )}

          {!realVotaciones.length && !loading && (
            <div className="mb-6 rounded-xl bg-white border border-slate-200 p-4 text-sm text-slate-600">
              No hay votaciones reales disponibles en este momento. Solo se muestran votaciones que pueden votarse de verdad.
            </div>
          )}

          {loading ? (
            <SkeletonGrid count={3} />
          ) : realVotaciones.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {realVotaciones.map((item) => {
                const voteOptions = item.opciones?.length ? item.opciones : item.opciones_stats?.map((stat) => stat.opcion) || [];
                return (
                  <div key={item.id} className="group bg-white/60 backdrop-blur-sm rounded-2xl border border-white/80 overflow-hidden hover:border-neighbor-blue/40 hover:shadow-xl transition">
                  {item.imagen_url && (
                    <div className="relative h-40 overflow-hidden bg-gradient-to-br from-neighbor-blue/10 to-emerald-100">
                      <LazyImage
                        src={mediaUrl(item.imagen_url)}
                        alt={item.titulo}
                        className="h-full w-full object-cover group-hover:scale-110 transition duration-300"
                        fallback={() => (
                          <div className="h-full w-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white">
                            <Vote className="h-12 w-12" />
                          </div>
                        )}
                      />
                      <div className="absolute top-3 right-3 inline-flex items-center gap-1 bg-green-500 text-white rounded-full px-3 py-1 text-xs font-bold shadow-lg">
                        <Zap className="h-3 w-3" />
                        En curso
                      </div>
                    </div>
                  )}
                  <div className="p-6 space-y-4">
                    <div>
                      <h3 className="font-black text-lg text-neighbor-navy line-clamp-2">{item.titulo}</h3>
                      <p className="mt-1 text-sm text-slate-600">{item.descripcion || 'Disponible para votar'}</p>
                    </div>

                    {item.opciones_stats && item.opciones_stats.length > 0 && (
                      <div className="space-y-3">
                        <p className="text-xs font-bold text-slate-500 uppercase">Resultados en vivo ({item.total_votos || 0} votos)</p>
                        <div className="space-y-2">
                          {item.opciones_stats.slice(0, 3).map((stat) => (
                            <div key={stat.opcion} className="space-y-1">
                              <div className="flex justify-between items-center text-xs">
                                <span className="font-semibold text-slate-700">{optionLabel(stat.opcion)}</span>
                                <span className="font-bold text-neighbor-blue bg-blue-50 px-2 py-0.5 rounded">{stat.percentage}%</span>
                              </div>
                              <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                                <div className="h-full rounded-full bg-gradient-to-r from-neighbor-blue to-neighbor-green transition-all duration-500" style={{ width: `${stat.percentage}%` }} />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {voteOptions.length > 0 && (
                      <div className="space-y-3">
                        <p className="text-xs font-bold text-slate-500 uppercase">Elige tu opción</p>
                        <div className="grid gap-2">
                          {voteOptions.map((opcion) => {
                            const label = optionLabel(opcion);
                            const selected = selectedOptions[item.id] === opcion;
                            return (
                              <button
                                key={opcion}
                                type="button"
                                onClick={() => setSelectedOptions((prev) => ({ ...prev, [item.id]: opcion }))}
                                disabled={isDemoId(item.id)}
                                className={`w-full rounded-2xl border px-3 py-2 text-left text-sm font-semibold transition ${selected ? 'border-neighbor-blue bg-neighbor-blue/10 text-neighbor-navy' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'} ${isDemoId(item.id) ? 'cursor-not-allowed opacity-70' : ''}`}
                              >
                                {label}
                              </button>
                            );
                          })}
                        </div>
                        {isDemoId(item.id) && (
                          <p className="text-xs text-slate-500">Esta votación es de demostración y no se puede enviar al servidor.</p>
                        )}
                      </div>
                    )}

                    <div className="flex gap-2">
                      {voteOptions.length > 0 && (
                        <button
                          onClick={() => handleVote(item.id)}
                          disabled={voting[item.id] || isDemoId(item.id)}
                          className="flex-1 px-3 py-2 text-xs font-bold rounded-lg bg-gradient-to-r from-neighbor-blue to-neighbor-green text-white hover:shadow-lg hover:scale-105 transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {voting[item.id] ? 'Votando...' : 'Votar'}
                        </button>
                      )}
                      <Link to="/app/votaciones" className="flex-1 px-3 py-2 text-xs font-bold rounded-lg border border-neighbor-blue/30 text-neighbor-blue hover:bg-neighbor-mist transition text-center">
                        Ver más
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
            </div>
          ) : (
            <div className="rounded-2xl border-2 border-dashed border-slate-300 p-12 text-center">
              <Vote className="h-12 w-12 text-slate-300 mx-auto mb-3" />
              <p className="text-slate-500 font-semibold">No hay votaciones activas en este momento</p>
            </div>
          )}
        </div>
      </SectionWrapper>

      {/* Comunicados Section */}
      <SectionWrapper className="py-20 bg-[#f8fbff]" delay={800}>
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-12">
            <div>
              <p className="text-sm font-bold text-neighbor-green uppercase tracking-wider">Comunicados</p>
              <h2 className="mt-3 text-4xl font-black text-neighbor-navy">Comunicados oficiales</h2>
              <p className="mt-4 max-w-2xl text-lg text-slate-600">Publicaciones oficiales de la comunidad, visibles y actualizadas.</p>
            </div>
            <Link to="/app/comunicados" className="btn-secondary px-5 py-3">Ver todos los comunicados</Link>
          </div>
          <div className="grid gap-6 lg:grid-cols-3">
            {data.comunicados.slice(0, 8).map((item) => (
              <div key={item.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-neighbor-green">{item.categoria}</p>
                <h3 className="mt-3 text-xl font-black text-neighbor-navy">{item.titulo}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{item.contenido}</p>
              </div>
            ))}
          </div>
        </div>
      </SectionWrapper>

      {/* Noticias Section */}
      <SectionWrapper className="py-20 bg-white" delay={1000}>
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-12">
            <div>
              <p className="text-sm font-bold text-neighbor-green uppercase tracking-wider">Noticias</p>
              <h2 className="mt-3 text-4xl font-black text-neighbor-navy">Últimas noticias</h2>
              <p className="mt-4 max-w-2xl text-lg text-slate-600">Mantente informado sobre las novedades y acontecimientos de la comunidad.</p>
            </div>
            <Link to="/app/noticias" className="btn-secondary px-5 py-3">Ver todas las noticias</Link>
          </div>
          <div className="grid gap-8 lg:grid-cols-2">
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} className="bg-white/60 backdrop-blur-sm rounded-2xl border border-white/80 p-6" />
              ))
            ) : (
              data.noticias.slice(0, 6).map((item) => (
                <NewsCard key={item.id} news={item} />
              ))
            )}
          </div>
        </div>
      </SectionWrapper>

      {/* Noticias Destacadas con Comentarios */}
      <section className="py-20 bg-[#f8fbff]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-12">
            <div>
              <p className="text-sm font-bold text-neighbor-green uppercase tracking-wider">Conversación</p>
              <h2 className="mt-3 text-4xl font-black text-neighbor-navy">Noticias destacadas con comentarios</h2>
              <p className="mt-4 max-w-2xl text-lg text-slate-600">Lee las noticias más importantes y participa en la conversación de la comunidad.</p>
            </div>
            <Link to="/app/noticias" className="btn-secondary px-5 py-3">Ver todas las noticias</Link>
          </div>
          <div className="grid gap-8">
            {loading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <SkeletonCard key={i} className="bg-white/60 backdrop-blur-sm rounded-2xl border border-white/80 p-6" />
              ))
            ) : (
              data.noticias.slice(0, 3).map((item) => (
                <NewsCardWithComments key={item.id} news={item} />
              ))
            )}
          </div>
        </div>
      </section>

      {/* Segunda sección de noticias con comentarios distintos */}
      <SectionWrapper className="py-20 bg-white" delay={1200}>
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-12">
            <div>
              <p className="text-sm font-bold text-neighbor-green uppercase tracking-wider">Opiniones</p>
              <h2 className="mt-3 text-4xl font-black text-neighbor-navy">Comentarios distintos en noticias recientes</h2>
              <p className="mt-4 max-w-2xl text-lg text-slate-600">Un segundo vistazo a las noticias con comentarios nuevos y más voces del barrio.</p>
            </div>
            <Link to="/app/noticias" className="btn-secondary px-5 py-3">Ver todas las noticias</Link>
          </div>
          <div className="grid gap-8 lg:grid-cols-2">
            {loading ? (
              Array.from({ length: 2 }).map((_, i) => (
                <SkeletonCard key={i} className="bg-white/60 backdrop-blur-sm rounded-2xl border border-white/80 p-6" />
              ))
            ) : (
              data.noticias.slice(1, 3).map((item) => (
                <NewsCardDiscussion key={item.id} news={item} />
              ))
            )}
          </div>
        </div>
      </SectionWrapper>

      {/* Avisos Section */}
      <SectionWrapper className="py-20" delay={1400}>
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-12">
            <div>
              <p className="text-sm font-bold text-neighbor-green uppercase tracking-wider">Avisos</p>
              <h2 className="mt-3 text-4xl font-black text-neighbor-navy">Avisos recientes</h2>
              <p className="mt-4 max-w-2xl text-lg text-slate-600">Noticias y alertas rápidas que mantienen a la comunidad informada.</p>
            </div>
            <Link to="/app/noticias" className="btn-secondary px-5 py-3">Ver todas las noticias</Link>
          </div>
          <div className="grid gap-6 lg:grid-cols-3">
            {data.noticias.slice(0, 6).map((item) => (
              <div key={item.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-neighbor-green">Aviso vecinal</p>
                <h3 className="mt-3 text-xl font-black text-neighbor-navy">{item.titulo}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{item.resumen}</p>
              </div>
            ))}
          </div>
        </div>
      </SectionWrapper>

      {/* Asambleas Section */}
      <section className="py-20 bg-[#f8fbff]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-12">
            <div>
              <p className="text-sm font-bold text-neighbor-green uppercase tracking-wider">Asambleas</p>
              <h2 className="mt-3 text-4xl font-black text-neighbor-navy">Asambleas y reuniones programadas</h2>
              <p className="mt-4 max-w-2xl text-lg text-slate-600">Fechas oficiales de reuniones y asambleas para la comunidad.</p>
            </div>
            <Link to="/app/reuniones" className="btn-secondary px-5 py-3">Ver todas las reuniones</Link>
          </div>
          <div className="grid gap-6 lg:grid-cols-3">
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm" />
              ))
            ) : (
              data.asambleas.slice(0, 6).map((item) => (
                <div key={item.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.24em] text-neighbor-green">
                    <CalendarDays className="h-4 w-4" />
                    {item.tipo === 'general' ? 'Asamblea' : 'Reunión'}
                  </div>
                  <h3 className="mt-3 text-xl font-black text-neighbor-navy">{item.titulo}</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{item.descripcion}</p>
                  <p className="mt-4 text-xs uppercase tracking-[0.18em] text-slate-500">{dateTime(item.fecha)}</p>
                  <p className="mt-2 text-xs text-slate-500">{item.lugar}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* Pagos Section */}
      <SectionWrapper className="py-20 bg-white/30 backdrop-blur-sm" delay={1600}>
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-12">
            <div>
              <p className="text-sm font-bold text-neighbor-green uppercase tracking-wider">Pagos comunitarios</p>
              <h2 className="mt-3 text-4xl font-black text-neighbor-navy">Aporte real para necesidades vecinales</h2>
              <p className="mt-4 max-w-2xl text-lg text-slate-600">Registra aquí un pago para una causa comunitaria y guarda el aporte en la base de datos.</p>
            </div>
            <Link to="/app/pagos" className="btn-secondary px-5 py-3">Ir a la gestión de pagos</Link>
          </div>

          {paymentMessage && <div className="mb-6 rounded-xl bg-green-50 border border-green-200 p-4 text-sm font-semibold text-green-700">{paymentMessage}</div>}
          {paymentError && <div className="mb-6 rounded-xl bg-red-50 border border-red-200 p-4 text-sm font-semibold text-red-700">{paymentError}</div>}

          <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <form onSubmit={handlePaymentSubmit} className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm space-y-4">
              <div>
                <label className="text-sm font-bold text-slate-700">Motivo del pago</label>
                <input
                  className="input mt-2 w-full"
                  placeholder="Ayuda para ropa, traslado, comida, etc."
                  value={paymentForm.concepto}
                  onChange={(e) => setPaymentForm({ ...paymentForm, concepto: e.target.value })}
                  required
                />
              </div>
              <div className="grid gap-4 lg:grid-cols-2">
                <div>
                  <label className="text-sm font-bold text-slate-700">Monto</label>
                  <input
                    className="input mt-2 w-full"
                    type="number"
                    min="0"
                    step="0.01"
                    value={paymentForm.monto}
                    onChange={(e) => setPaymentForm({ ...paymentForm, monto: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-700">Fecha</label>
                  <input
                    className="input mt-2 w-full"
                    type="date"
                    value={paymentForm.fecha_pago}
                    onChange={(e) => setPaymentForm({ ...paymentForm, fecha_pago: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="grid gap-4 lg:grid-cols-2">
                <div>
                  <label className="text-sm font-bold text-slate-700">Método</label>
                  <select
                    className="input mt-2 w-full"
                    value={paymentForm.metodo}
                    onChange={(e) => setPaymentForm({ ...paymentForm, metodo: e.target.value })}
                  >
                    <option value="transferencia">Transferencia</option>
                    <option value="efectivo">Efectivo</option>
                    <option value="deposito">Depósito</option>
                    <option value="otro">Otro</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-bold text-slate-700">Referencia</label>
                  <input
                    className="input mt-2 w-full"
                    placeholder="Número de operación o nota"
                    value={paymentForm.referencia}
                    onChange={(e) => setPaymentForm({ ...paymentForm, referencia: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row">
                <button className="btn-primary w-full py-3">Registrar aporte</button>
                {!user && (
                  <Link to="/login" className="btn-secondary w-full py-3 text-center">Iniciar sesión</Link>
                )}
              </div>
            </form>

            <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
              <p className="text-sm font-bold uppercase tracking-[0.24em] text-neighbor-green">Solicitudes recientes</p>
              <h3 className="mt-3 text-2xl font-black text-neighbor-navy">Pagos registrados</h3>
              <p className="mt-4 text-sm text-slate-600">Últimos aportes y solicitudes guardadas en la base.</p>
              <div className="mt-6 space-y-4">
                {data.pagos.slice(0, 6).map((pago) => (
                  <div key={pago.id} className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">{pago.metodo}</p>
                    <h4 className="mt-2 font-black text-neighbor-navy line-clamp-2">{pago.concepto}</h4>
                    <p className="mt-2 text-sm text-slate-600">RD$ {Number(pago.monto).toFixed(2)}</p>
                    <p className="mt-1 text-xs text-slate-500">{pago.fecha_pago}</p>
                  </div>
                ))}
                {!data.pagos.length && <p className="text-sm text-slate-500">No hay pagos registrados aún.</p>}
              </div>
            </div>
          </div>
        </div>
      </SectionWrapper>

      {/* Directiva Section */}
      <SectionWrapper id="directiva" className="py-20 bg-white/30 backdrop-blur-sm" delay={1800}>
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-sm font-bold text-neighbor-green uppercase tracking-wider">administración</p>
            <h2 className="mt-3 text-4xl font-black text-neighbor-navy">Junta directiva</h2>
            <p className="mt-3 text-lg text-slate-600">Los encargados de mantener organizada nuestra comunidad</p>
          </div>

          {loading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} type="directiva" className="group bg-white/80 backdrop-blur-sm rounded-2xl border border-white/80 overflow-hidden" />
              ))}
            </div>
          ) : data.directiva.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {data.directiva.slice(0, 6).map((item) => (
                <div key={item.id} className="group bg-white/80 backdrop-blur-sm rounded-2xl border border-white/80 overflow-hidden hover:border-neighbor-blue/40 hover:shadow-xl hover:-translate-y-1 transition">
                  <div className="h-40 bg-gradient-to-br from-neighbor-blue/20 to-emerald-100 flex items-center justify-center overflow-hidden">
                    {item.foto_url ? (
                      <LazyImage
                        src={mediaUrl(item.foto_url)}
                        alt={item.nombre}
                        className="h-full w-full object-cover group-hover:scale-110 transition duration-300"
                        fallback={() => (
                          <div className="h-full w-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white">
                            <Users className="h-16 w-16" />
                          </div>
                        )}
                      />
                    ) : (
                      <div className="h-full w-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white">
                        <Users className="h-16 w-16" />
                      </div>
                    )}
                  </div>
                  <div className="p-6 text-center">
                    <div className="inline-flex items-center gap-1 bg-gradient-to-r from-neighbor-green/20 to-emerald-100 border border-neighbor-green/30 rounded-full px-3 py-1 text-xs font-bold text-neighbor-green mb-3">
                      <Shield className="h-3 w-3" />
                      {cargoLabel(item.cargo)}
                    </div>
                    <h3 className="text-lg font-black text-neighbor-navy">{item.nombre}</h3>
                    {item.email && (
                      <p className="mt-2 text-sm text-slate-600 flex items-center justify-center gap-1">
                        <Mail className="h-3.5 w-3.5 text-neighbor-blue" />
                        {item.email}
                      </p>
                    )}
                    {item.telefono && (
                      <p className="mt-1 text-sm text-slate-600 flex items-center justify-center gap-1">
                        <Phone className="h-3.5 w-3.5 text-neighbor-blue" />
                        {item.telefono}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border-2 border-dashed border-slate-300 p-12 text-center">
              <Users className="h-12 w-12 text-slate-300 mx-auto mb-3" />
              <p className="text-slate-500 font-semibold">La directiva aún no ha sido registrada</p>
            </div>
          )}
        </div>
      </SectionWrapper>

      {/* CTA Section */}
      <SectionWrapper className="py-20" delay={2000}>
        <div className="mx-auto max-w-4xl px-6">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-neighbor-blue via-teal-500 to-neighbor-green p-12 md:p-16 shadow-2xl">
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 right-0 h-40 w-40 rounded-full bg-white blur-3xl" />
              <div className="absolute bottom-0 left-0 h-40 w-40 rounded-full bg-white blur-3xl" />
            </div>
            <div className="relative text-center space-y-6">
              <h2 className="text-4xl md:text-5xl font-black text-white">¿Listo para conectar tu comunidad?</h2>
              <p className="text-lg text-white/90 max-w-xl mx-auto">Únete a cientos de comunidades que ya están organizadas con Neighbord</p>
              <div className="flex flex-wrap gap-3 justify-center pt-4">
                <Link to="/registro" className="inline-flex items-center gap-2 bg-white text-neighbor-blue px-6 py-3 rounded-lg font-bold hover:scale-105 transition shadow-lg">
                  Crear cuenta gratis
                  <ArrowRight className="h-5 w-5" />
                </Link>
                <button className="inline-flex items-center gap-2 border-2 border-white text-white px-6 py-3 rounded-lg font-bold hover:bg-white/10 transition">
                  Ver demo
                </button>
              </div>
            </div>
          </div>
        </div>
      </SectionWrapper>

      {/* Footer */}
      <SectionWrapper id="contacto" className="border-t border-slate-200 bg-gradient-to-br from-neighbor-navy to-slate-900 text-white" delay={2200}>
        <div className="mx-auto max-w-7xl px-6 py-16">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2.5">
                <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-neighbor-blue to-neighbor-green p-2">
                  <img src="/neighbor-logo.png" alt="" className="h-full w-full invert" />
                </div>
                <div>
                  <p className="font-black text-lg">Neighbord</p>
                  <p className="text-xs font-bold text-neighbor-green">Más unión</p>
                </div>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-white/75">Plataforma de gestión comunitaria para juntas de vecinos modernas y transparentes.</p>
            </div>
            <div>
              <h3 className="font-black text-sm uppercase tracking-wider mb-4 text-white">Producto</h3>
              <div className="space-y-2.5 text-sm">
                <Link to="/app/noticias" className="text-white/75 hover:text-white transition">Noticias</Link>
                <Link to="/app/votaciones" className="text-white/75 hover:text-white transition block">Votaciones</Link>
                <Link to="/app/finanzas" className="text-white/75 hover:text-white transition block">Finanzas</Link>
              </div>
            </div>
            <div>
              <h3 className="font-black text-sm uppercase tracking-wider mb-4 text-white">Acceso</h3>
              <div className="space-y-2.5 text-sm">
                <Link to="/login" className="text-white/75 hover:text-white transition">Iniciar sesión</Link>
                <Link to="/registro" className="text-white/75 hover:text-white transition block">Registrarse</Link>
              </div>
            </div>
            <div>
              <h3 className="font-black text-sm uppercase tracking-wider mb-4 text-white">Contacto</h3>
              <div className="space-y-2.5 text-sm text-white/75">
                <p className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-neighbor-green" />
                  info@neighbord.local
                </p>
                <p className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-neighbor-green" />
                  Comunidad conectada
                </p>
              </div>
            </div>
          </div>
          <div className="border-t border-white/10 pt-8 text-center text-sm text-white/60">
            <p>© 2026 Neighbord. Todos los derechos reservados. Construido con ❤️ para comunidades.</p>
          </div>
        </div>
      </SectionWrapper>
    </main>
  );
}

function PublicSection({ icon: Icon, title, items, emptyText, children }) {
  return (
    <section className="mx-auto max-w-7xl px-6 py-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Icon className="h-7 w-7 text-neighbor-green" />
          <h2 className="text-2xl font-black text-neighbor-navy">{title}</h2>
        </div>
        <span className="rounded-full bg-neighbor-mist px-3 py-1 text-xs font-black text-neighbor-blue">{items.length} publicados</span>
      </div>
      <div className="mt-5 grid gap-4 md:grid-cols-3">
        {items.length ? items.slice(0, 3).map((item) => <div key={item.id}>{children(item)}</div>) : <p className="rounded-lg border border-dashed border-slate-300 p-6 text-sm font-semibold text-slate-500">{emptyText}</p>}
      </div>
    </section>
  );
}

function Card({ eyebrow, title, text }) {
  return (
    <article className="h-full rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-black uppercase text-neighbor-green">{eyebrow}</p>
      <h3 className="mt-2 font-black text-neighbor-navy">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{text}</p>
    </article>
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

function NewsCard({ news }) {
  const { user } = useAuth();
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState([
    { id: '1', autor: 'Ana Morales', comentario: '¡Excelente noticia! Me alegra mucho que la comunidad esté creciendo.', fecha: '2026-05-02T10:30:00Z' },
    { id: '2', autor: 'Carlos Rojas', comentario: '¿Cuándo será el próximo evento? Me gustaría participar.', fecha: '2026-05-02T11:15:00Z' },
    { id: '3', autor: 'María García', comentario: 'Felicitaciones al equipo organizador. ¡Sigan adelante!', fecha: '2026-05-02T12:45:00Z' }
  ]);
  const [newComment, setNewComment] = useState('');
  const userName = user?.nombre || 'Usuario Anónimo';

  const handleAddComment = () => {
    if (!newComment.trim()) return;
    const comment = {
      id: Date.now().toString(),
      autor: user.nombre,
      comentario: newComment,
      fecha: new Date().toISOString()
    };
    setComments([comment, ...comments]);
    setNewComment('');
  };

  return (
    <article className="rounded-3xl border border-slate-200 bg-white overflow-hidden shadow-sm hover:shadow-lg transition">
      {news.imagen_url && (
        <div className="aspect-video overflow-hidden bg-gradient-to-br from-neighbor-blue/10 to-emerald-100">
          <LazyImage
            src={mediaUrl(news.imagen_url)}
            alt={news.titulo}
            className="h-full w-full object-cover"
            fallback={() => (
              <div className="h-full w-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white">
                <Newspaper className="h-12 w-12" />
              </div>
            )}
          />
        </div>
      )}
      <div className="p-8">
        <div className="flex items-center justify-between mb-4">
          <span className="inline-flex items-center gap-2 rounded-full bg-neighbor-mist px-3 py-1 text-xs font-bold text-neighbor-blue">
            <Newspaper className="h-3 w-3" />
            Noticia
          </span>
          <span className="text-xs text-slate-500">
            {new Date(news.created_at || Date.now()).toLocaleDateString('es-ES', {
              year: 'numeric',
              month: 'short',
              day: 'numeric'
            })}
          </span>
        </div>
        <h3 className="text-2xl font-black text-neighbor-navy mb-3">{news.titulo}</h3>
        <p className="text-slate-600 leading-relaxed mb-4">{news.resumen || news.contenido}</p>
        
        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <button
            onClick={() => setShowComments(!showComments)}
            aria-expanded={showComments}
            className="flex items-center gap-2 text-sm font-semibold text-neighbor-blue hover:text-neighbor-green transition"
          >
            <MessageCircle className="h-4 w-4" />
            {showComments ? 'Ocultar comentarios' : `${comments.length} comentarios`}
          </button>
          <Link to={`/app/noticias/${news.id}`} className="text-sm font-semibold text-neighbor-blue hover:text-neighbor-green transition">
            Leer más →
          </Link>
        </div>

        {showComments && (
          <div className="mt-6 pt-6 border-t border-slate-100">
            <div className="space-y-4 mb-6 max-h-72 overflow-y-auto">
              {comments.map((comment) => (
                <div key={comment.id} className="flex gap-3">
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white text-xs font-bold">
                    {comment.autor.charAt(0)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="text-sm font-semibold text-neighbor-navy">{comment.autor}</span>
                      <span className="text-xs text-slate-500">
                        {new Date(comment.fecha).toLocaleDateString('es-ES', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600">{comment.comentario}</p>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white text-xs font-bold">
                {userName.charAt(0)}
              </div>
              <div className="flex-1">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Escribe un comentario..."
                  className="w-full p-3 border border-slate-200 rounded-lg text-sm resize-none focus:border-neighbor-blue focus:outline-none"
                  rows="2"
                />
                <div className="flex justify-end mt-2">
                  <button
                    onClick={handleAddComment}
                    disabled={!newComment.trim()}
                    className="px-4 py-2 bg-neighbor-blue text-white text-sm font-semibold rounded-lg hover:bg-neighbor-green transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Comentar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </article>
  );
}

function NewsCardWithComments({ news }) {
  const { user } = useAuth();
  const [comments, setComments] = useState(() => {
    const nombres = [
      'Ana Morales', 'Carlos Rojas', 'María García', 'Juan López', 'Rosa Martínez',
      'Pedro González', 'Luisa Fernández', 'Diego Rodríguez', 'Sofia Díaz', 'Miguel Torres',
      'Elena Castro', 'Roberto Sánchez', 'Victoria López', 'Andrés Ruiz', 'Catalina Méndez'
    ];

    const comentariosBase = [
      '¡Excelente noticia! Me alegra mucho que la comunidad esté creciendo.',
      '¿Cuándo será el próximo evento? Me gustaría participar.',
      'Felicitaciones al equipo organizador. ¡Sigan adelante!',
      'Espero poder asistir al próximo evento comunitario.',
      'Gracias por mantener a la comunidad informada. ¡Que sigan los logros!',
      'Esto es justo lo que necesitábamos en el barrio.',
      'Muy buen trabajo, sigan con esta energía positiva.',
      'Me encantaría contribuir en futuros eventos.',
      'La comunidad se ve cada vez más unida. ¡Qué bueno!',
      'Importante conocer sobre estas iniciativas vecinales.',
      'Apoyaré esta iniciativa sin dudarlo.',
      'Necesitábamos este tipo de conexión en el sector.',
      'Muchas gracias por el esfuerzo y la dedicación.',
      'Este es el camino para fortalecer nuestra comunidad.',
      'Información valiosa para todos nosotros.',
      'Ojalá se repita este tipo de eventos pronto.',
      'La organización ha mejorado significativamente.',
      'Definitivamente, la comunidad lo necesitaba.',
      'Seguiremos apoyando estas iniciativas comunitarias.',
      'Gracias por pensar en el bienestar de todos.'
    ];

    return Array.from({ length: 5 }, (_, index) => ({
      id: `${news.id}-comment-${index}`,
      autor: nombres[Math.floor(Math.random() * nombres.length)],
      comentario: comentariosBase[Math.floor(Math.random() * comentariosBase.length)],
      fecha: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
    }));
  });
  const [newComment, setNewComment] = useState('');
  const userName = user?.nombre || 'Tu nombre';

  const handleAddComment = () => {
    if (!newComment.trim()) return;
    const comment = {
      id: Date.now().toString(),
      autor: userName,
      comentario: newComment,
      fecha: new Date().toISOString()
    };
    setComments([comment, ...comments]);
    setNewComment('');
  };

  return (
    <article className="rounded-3xl border border-slate-200 bg-white overflow-hidden shadow-sm hover:shadow-lg transition">
      {news.imagen_url && (
        <div className="aspect-video overflow-hidden bg-gradient-to-br from-neighbor-blue/10 to-emerald-100">
          <LazyImage
            src={mediaUrl(news.imagen_url)}
            alt={news.titulo}
            className="h-full w-full object-cover"
            fallback={() => (
              <div className="h-full w-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white">
                <Newspaper className="h-12 w-12" />
              </div>
            )}
          />
        </div>
      )}
      <div className="p-8">
        <div className="flex items-center justify-between mb-4">
          <span className="inline-flex items-center gap-2 rounded-full bg-neighbor-mist px-3 py-1 text-xs font-bold text-neighbor-blue">
            <Newspaper className="h-3 w-3" />
            Noticia destacada
          </span>
          <span className="text-xs text-slate-500">
            {new Date(news.created_at || Date.now()).toLocaleDateString('es-ES', {
              year: 'numeric',
              month: 'short',
              day: 'numeric'
            })}
          </span>
        </div>
        <h3 className="text-2xl font-black text-neighbor-navy mb-3">{news.titulo}</h3>
        <p className="text-slate-600 leading-relaxed mb-6">{news.resumen || news.contenido}</p>
        
        {/* Comentarios Section */}
        <div className="pt-6 border-t border-slate-100">
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-6">
              <MessageCircle className="h-5 w-5 text-neighbor-blue" />
              <h4 className="text-lg font-black text-neighbor-navy">{comments.length} comentarios</h4>
            </div>
            
            {/* Comments List */}
            <div className="space-y-4 mb-8 max-h-96 overflow-y-auto">
              {comments.map((comment) => (
                <div key={comment.id} className="flex gap-3 pb-4 border-b border-slate-100 last:border-0">
                  <div className="h-9 w-9 rounded-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                    {comment.autor.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="text-sm font-semibold text-neighbor-navy">{comment.autor}</span>
                      <span className="text-xs text-slate-500">
                        {new Date(comment.fecha).toLocaleDateString('es-ES', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600">{comment.comentario}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Add Comment */}
            <div className="bg-slate-50 rounded-2xl p-4">
              <div className="flex gap-3 mb-3">
                <div className="h-9 w-9 rounded-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                  {userName.charAt(0)}
                </div>
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Comparte tu opinión con la comunidad..."
                  className="flex-1 p-3 border border-slate-200 rounded-lg text-sm resize-none focus:border-neighbor-blue focus:outline-none"
                  rows="2"
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setNewComment('')}
                  className="px-4 py-2 text-slate-700 text-sm font-semibold rounded-lg hover:bg-slate-200 transition"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleAddComment}
                  disabled={!newComment.trim()}
                  className="px-4 py-2 bg-neighbor-blue text-white text-sm font-semibold rounded-lg hover:bg-neighbor-green transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Comentar
                </button>
              </div>
            </div>
          </div>

          {/* Link to full article */}
          <div className="flex justify-end pt-4">
            <Link to={`/app/noticias/${news.id}`} className="text-sm font-semibold text-neighbor-blue hover:text-neighbor-green transition flex items-center gap-2">
              Ver noticia completa <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </div>
    </article>
  );
}

function NewsCardDiscussion({ news }) {
  const { user } = useAuth();
  const [comments, setComments] = useState(() => {
    const nombres = [
      'Lucía Pérez', 'Javier Torres', 'Natalia Suárez', 'Daniel Vega', 'Mariana Cruz',
      'Gabriel Ortiz', 'Clara Jiménez', 'Elias Medina', 'Laura Castillo', 'Ricardo Paredes'
    ];

    const comentariosBase = [
      'Este tipo de información nos mantiene más unidos como vecinos.',
      'Muy buena iniciativa, sería ideal que se comparta en la próxima asamblea.',
      'Quisiera saber cómo puedo colaborar con esta actividad.',
      'Es importante que todos estemos al tanto de estos avances.',
      'Aprecio la transparencia, esto da confianza a la comunidad.',
      'Espero que pronto tengamos más noticias como esta.',
      'La plaza del barrio se ve cada vez mejor gracias a estas acciones.',
      'Me gustaría proponer más eventos familiares para el sector.',
      'Este reporte comunitario es justo lo que necesitábamos.',
      'Gracias por mantener la comunicación activa entre vecinos.'
    ];

    return Array.from({ length: 4 }, (_, index) => ({
      id: `${news.id}-disc-${index}`,
      autor: nombres[Math.floor(Math.random() * nombres.length)],
      comentario: comentariosBase[Math.floor(Math.random() * comentariosBase.length)],
      fecha: new Date(Date.now() - Math.random() * 48 * 60 * 60 * 1000).toISOString()
    }));
  });
  const [newComment, setNewComment] = useState('');
  const userName = user?.nombre || 'Vecino';

  const handleAddComment = () => {
    if (!newComment.trim()) return;
    const comment = {
      id: Date.now().toString(),
      autor: userName,
      comentario: newComment,
      fecha: new Date().toISOString()
    };
    setComments([comment, ...comments]);
    setNewComment('');
  };

  return (
    <article className="rounded-3xl border border-slate-200 bg-white overflow-hidden shadow-sm hover:shadow-lg transition">
      {news.imagen_url && (
        <div className="aspect-video overflow-hidden bg-gradient-to-br from-neighbor-blue/10 to-emerald-100">
          <LazyImage
            src={mediaUrl(news.imagen_url)}
            alt={news.titulo}
            className="h-full w-full object-cover"
            fallback={() => (
              <div className="h-full w-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white">
                <Newspaper className="h-12 w-12" />
              </div>
            )}
          />
        </div>
      )}
      <div className="p-8">
        <div className="flex items-center justify-between mb-4">
          <span className="inline-flex items-center gap-2 rounded-full bg-neighbor-mist px-3 py-1 text-xs font-bold text-neighbor-blue">
            <Newspaper className="h-3 w-3" />
            Noticia comunitaria
          </span>
          <span className="text-xs text-slate-500">
            {new Date(news.created_at || Date.now()).toLocaleDateString('es-ES', {
              year: 'numeric',
              month: 'short',
              day: 'numeric'
            })}
          </span>
        </div>
        <h3 className="text-2xl font-black text-neighbor-navy mb-3">{news.titulo}</h3>
        <p className="text-slate-600 leading-relaxed mb-6">{news.resumen || news.contenido}</p>

        <div className="pt-6 border-t border-slate-100">
          <div className="flex items-center gap-2 mb-5">
            <MessageCircle className="h-5 w-5 text-neighbor-blue" />
            <h4 className="text-lg font-black text-neighbor-navy">Voces del barrio</h4>
          </div>
          <div className="space-y-4 mb-6">
            {comments.map((comment) => (
              <div key={comment.id} className="flex gap-3 pb-4 border-b border-slate-100 last:border-0">
                <div className="h-9 w-9 rounded-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                  {comment.autor.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="text-sm font-semibold text-neighbor-navy">{comment.autor}</span>
                    <span className="text-xs text-slate-500">
                      {new Date(comment.fecha).toLocaleDateString('es-ES', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600">{comment.comentario}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-slate-50 rounded-2xl p-4">
            <div className="flex gap-3 mb-3">
              <div className="h-9 w-9 rounded-full bg-gradient-to-br from-neighbor-blue to-neighbor-green flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                {userName.charAt(0)}
              </div>
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="¿Qué opinas de esta noticia?"
                className="flex-1 p-3 border border-slate-200 rounded-lg text-sm resize-none focus:border-neighbor-blue focus:outline-none"
                rows="2"
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setNewComment('')}
                className="px-4 py-2 text-slate-700 text-sm font-semibold rounded-lg hover:bg-slate-200 transition"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddComment}
                disabled={!newComment.trim()}
                className="px-4 py-2 bg-neighbor-blue text-white text-sm font-semibold rounded-lg hover:bg-neighbor-green transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Comentar
              </button>
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <Link to={`/app/noticias/${news.id}`} className="text-sm font-semibold text-neighbor-blue hover:text-neighbor-green transition flex items-center gap-2">
              Ver noticia completa <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </div>
    </article>
  );
}

function optionLabel(option) {
  if (!option) return '';
  if (typeof option === 'object') return option.opcion || '';
  if (option.startsWith('election|')) {
    const parts = option.split('|').slice(1);
    for (const part of parts) {
      const [key, value] = part.split('=');
      if (key === 'name') return decodeURIComponent(value || 'Candidato');
    }
    return 'Candidato';
  }
  return option;
}

function parseElectionOption(option) {
  if (!option?.startsWith('election|')) return null;
  return option.split('|').slice(1).reduce((acc, part) => {
    const [key, value] = part.split('=');
    acc[key] = value;
    return acc;
  }, {});
}
