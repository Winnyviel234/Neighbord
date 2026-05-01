import { Link } from 'react-router-dom';
import { ArrowRight, Bell, CalendarDays, CheckCircle2, Landmark, Mail, MapPin, Menu, MessageCircle, Newspaper, Phone, Vote } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { dataService, mediaUrl } from '../services/api';
import { demoLanding } from '../services/demoData';
import { dateTime } from '../lib/utils';
import { useAuth } from '../context/AuthContext';

const empty = { comunicados: [], noticias: [], votaciones: [], asambleas: [], directiva: [] };
const withDemo = (payload) => ({
  comunicados: payload?.comunicados?.length ? payload.comunicados : demoLanding.comunicados,
  noticias: payload?.noticias?.length ? payload.noticias : demoLanding.noticias,
  votaciones: payload?.votaciones?.length ? payload.votaciones : demoLanding.votaciones,
  asambleas: payload?.asambleas?.length ? payload.asambleas : demoLanding.asambleas,
  directiva: payload?.directiva?.length ? payload.directiva : demoLanding.directiva
});

export default function LandingPage() {
  const { user } = useAuth();
  const [data, setData] = useState(withDemo(empty));
  const [voting, setVoting] = useState({});
  const [voteMessage, setVoteMessage] = useState('');

  const handleVote = async (votacionId, opcion) => {
    if (!user) {
      setVoteMessage('Debes iniciar sesión para votar');
      return;
    }
    try {
      setVoting({ ...voting, [votacionId]: true });
      await dataService.votar(votacionId, opcion);
      setVoteMessage('Voto registrado exitosamente');
      setTimeout(() => setVoteMessage(''), 3000);
      // Recargar datos
      dataService.landing().then((payload) => setData(withDemo(payload))).catch(() => setData(withDemo(empty)));
    } catch (err) {
      setVoteMessage(err.response?.data?.detail || 'Error al votar');
    } finally {
      setVoting({ ...voting, [votacionId]: false });
    }
  };

  useEffect(() => {
    dataService.landing().then((payload) => setData(withDemo(payload))).catch(() => setData(withDemo(empty)));
  }, []);

  const featuredPosts = [
    ...data.noticias.map((item) => ({ ...item, type: 'Noticia vecinal', title: item.titulo, text: item.resumen })),
    ...data.comunicados.map((item) => ({ ...item, type: item.categoria || 'Comunicado', title: item.titulo, text: item.contenido }))
  ].slice(0, 4);

  const recentItems = [
    ...data.votaciones.map((item) => ({ ...item, label: 'Votacion', title: item.titulo })),
    ...data.asambleas.map((item) => ({ ...item, label: dateTime(item.fecha), title: item.titulo })),
    ...data.noticias.map((item) => ({ ...item, label: 'Noticia', title: item.titulo }))
  ].slice(0, 5);

  const votingStats = useMemo(() => {
    if (!data.votaciones?.length) return null;
    const totalVotos = data.votaciones.reduce((sum, v) => sum + (v.total_votos || 0), 0);
    return {
      total: data.votaciones.length,
      totalVotos,
      withStats: data.votaciones.filter(v => v.opciones_stats?.length > 0).length
    };
  }, [data.votaciones]);

  return (
    <main className="min-h-screen bg-[#f7fbfd] text-slate-900">
      <section className="bg-white">
        <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <Link to="/" className="flex items-center gap-3">
            <img src="/neighbor-logo.png" alt="Neighbord" className="h-14 w-14 object-contain" />
            <div>
              <p className="text-2xl font-black text-neighbor-navy">Neighbord</p>
              <p className="text-xs font-bold text-neighbor-green">Mas union, mejor comunidad</p>
            </div>
          </Link>
          <nav className="hidden items-center gap-8 text-sm font-bold text-slate-600 lg:flex">
            <a href="#junta" className="hover:text-neighbor-blue">Junta de vecinos</a>
            <a href="#actividad" className="hover:text-neighbor-blue">Actividad</a>
            <a href="#contacto" className="hover:text-neighbor-blue">Contacto</a>
          </nav>
          <div className="flex items-center gap-3">
            <Link to="/login" className="hidden rounded-md border border-neighbor-blue px-4 py-2 text-sm font-bold text-neighbor-blue transition hover:bg-neighbor-mist sm:inline-flex">Acceso</Link>
            <Link to="/registro" className="btn-primary">Empezar</Link>
            <button className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 text-neighbor-navy lg:hidden" aria-label="Abrir menu">
              <Menu className="h-5 w-5" />
            </button>
          </div>
        </header>
      </section>

      <section className="overflow-hidden bg-neighbor-mist">
        <div className="mx-auto grid min-h-[72vh] max-w-7xl items-center gap-12 px-6 py-14 lg:grid-cols-[0.95fr_1.05fr]">
          <div className="order-2 lg:order-1">
            <p className="text-sm font-black uppercase tracking-[0.24em] text-neighbor-green">Sistema comunitario real</p>
            <h1 className="mt-4 max-w-2xl text-5xl font-black leading-[1.02] text-neighbor-navy md:text-7xl">Junta de vecinos organizada en un solo lugar</h1>
            <p className="mt-6 max-w-2xl text-lg font-semibold leading-8 text-slate-700">
              Neighbord conecta asambleas, votaciones, comunicados, noticias, cuotas, finanzas y directiva con datos reales para que la comunidad funcione con claridad.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/registro" className="btn-primary px-5 py-3">Crear cuenta <ArrowRight className="h-4 w-4" /></Link>
              <a href="#actividad" className="btn-secondary px-5 py-3">Ver actividad</a>
            </div>
            <div className="mt-10 grid max-w-xl gap-3 sm:grid-cols-3">
              {[
                ['Votaciones', 'Participacion clara'],
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
      </section>

      <section id="junta" className="border-y border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="text-sm font-bold text-slate-500">
            <Link to="/" className="text-neighbor-blue">Inicio</Link>
            <span className="mx-2">/</span>
            <span>Junta de vecinos</span>
          </div>
          <div className="mt-6 grid gap-8 lg:grid-cols-[1fr_340px]">
            <div>
              <p className="text-sm font-black uppercase tracking-[0.22em] text-neighbor-green">Categoria</p>
              <h2 className="mt-2 text-4xl font-black text-neighbor-navy">Junta de vecinos</h2>
              <p className="mt-4 max-w-3xl text-lg font-semibold leading-8 text-slate-600">
                Un espacio publico para revisar lo que esta pasando en el barrio: publicaciones, acuerdos, reuniones y decisiones que sostienen la convivencia.
              </p>
            </div>
            <div className="rounded-lg border border-neighbor-blue/20 bg-neighbor-mist p-6">
              <p className="font-black text-neighbor-navy">Acceso para residentes</p>
              <p className="mt-2 text-sm leading-6 text-slate-600">Ingresa para votar, revisar cuotas, enviar solicitudes y seguir los acuerdos de la directiva.</p>
              <Link to="/login" className="mt-5 inline-flex items-center gap-2 text-sm font-black text-neighbor-blue">Entrar al sistema <ArrowRight className="h-4 w-4" /></Link>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white">
        <div className="mx-auto grid max-w-7xl gap-4 px-6 py-10 md:grid-cols-4">
          {[
            [Vote, 'Votaciones abiertas', 'Decisiones visibles para todos los vecinos.'],
            [Bell, 'Avisos oficiales', 'Comunicados destacados y recordatorios.'],
            [MapPin, 'Mapa del sector', 'Puntos clave, accesos e incidencias.'],
            [MessageCircle, 'Comunidad activa', 'Chat y mensajes directos a la directiva.']
          ].map(([Icon, title, text]) => (
            <article key={title} className="rounded-lg border border-slate-200 bg-[#f7fbfd] p-5">
              <div className="flex h-11 w-11 items-center justify-center rounded-md bg-neighbor-mist text-neighbor-blue">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="mt-4 font-black text-neighbor-navy">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="actividad" className="mx-auto grid max-w-7xl gap-8 px-6 py-12 lg:grid-cols-[1fr_340px]">
        <div className="grid gap-5">
          {featuredPosts.length ? featuredPosts.map((item, index) => (
            <ArticlePreview key={`${item.type}-${item.id || index}`} item={item} />
          )) : (
            <ArticlePreview item={{ type: 'Neighbord', title: 'Actividad comunitaria en tiempo real', text: 'Cuando existan noticias o comunicados publicados, apareceran aqui con el formato de categoria publica.' }} />
          )}
        </div>

        <aside className="space-y-6">
          <SidebarBlock title="Post recientes">
            <div className="space-y-4">
              {recentItems.length ? recentItems.map((item, index) => (
                <div key={`${item.label}-${item.id || index}`} className="border-b border-slate-200 pb-4 last:border-0 last:pb-0">
                  <p className="text-xs font-black uppercase text-neighbor-green">{item.label}</p>
                  <p className="mt-1 font-bold leading-5 text-neighbor-navy">{item.title}</p>
                </div>
              )) : (
                <p className="text-sm font-semibold text-slate-500">Aun no hay publicaciones recientes.</p>
              )}
            </div>
          </SidebarBlock>

          <SidebarBlock title="Categorias">
            <div className="grid gap-2 text-sm font-bold text-slate-600">
              {['Administracion', 'Junta de vecinos', 'Residentes', 'Sistema'].map((item) => (
                <span key={item} className="flex items-center justify-between border-b border-slate-100 pb-2">
                  {item}
                  <CheckCircle2 className="h-4 w-4 text-neighbor-green" />
                </span>
              ))}
            </div>
          </SidebarBlock>

          <SidebarBlock title="Etiquetas">
            <div className="flex flex-wrap gap-2">
              {['asambleas', 'votaciones', 'cuotas', 'comunicados', 'directiva', 'residentes'].map((tag) => (
                <span key={tag} className="rounded-md bg-neighbor-mist px-3 py-2 text-xs font-black text-neighbor-blue">{tag}</span>
              ))}
            </div>
          </SidebarBlock>
        </aside>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Vote className="h-7 w-7 text-neighbor-green" />
            <h2 className="text-2xl font-black text-neighbor-navy">Votaciones activas</h2>
          </div>
          {votingStats && (
            <div className="flex gap-2">
              <span className="rounded-full bg-neighbor-mist px-3 py-1 text-xs font-black text-neighbor-blue">{data.votaciones.length} activas</span>
              {votingStats.totalVotos > 0 && (
                <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-black text-green-700">{votingStats.totalVotos} votos</span>
              )}
            </div>
          )}
        </div>

        {voteMessage && (
          <p className="mt-4 rounded-md bg-green-50 p-3 text-sm font-semibold text-green-700">{voteMessage}</p>
        )}

        {data.votaciones.length > 0 ? (
          <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {data.votaciones.slice(0, 3).map((item) => (
              <article key={item.id} className="card overflow-hidden p-0">
                {item.imagen_url && (
                  <div className="aspect-video w-full overflow-hidden bg-gradient-to-br from-neighbor-mist to-slate-100">
                    <img src={mediaUrl(item.imagen_url)} alt={item.titulo} className="h-full w-full object-cover" />
                  </div>
                )}
                <div className="border-b border-slate-100 bg-neighbor-mist p-4">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="font-bold text-neighbor-navy">{item.titulo}</h3>
                    <span className="rounded-full bg-green-50 px-2 py-1 text-xs font-bold text-green-700">Activa</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-600">{item.descripcion || 'Disponible para votar'}</p>
                </div>

                {item.opciones_stats && item.opciones_stats.length > 0 && (
                  <div className="space-y-3 p-4">
                    <p className="text-xs font-bold text-slate-500">RESULTADOS EN VIVO ({item.total_votos || 0} votos)</p>
                    {item.opciones_stats.map((stat) => (
                      <div key={stat.opcion} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="font-semibold text-slate-700">{optionLabel(stat.opcion)}</span>
                          <span className="font-bold text-neighbor-blue">{stat.count} votos ({stat.percentage}%)</span>
                        </div>
                        <button
                          onClick={() => handleVote(item.id, stat.opcion)}
                          disabled={voting[item.id]}
                          className="h-2 w-full overflow-hidden rounded-full bg-slate-100 transition hover:opacity-80 disabled:opacity-50"
                        >
                          <div className="h-full rounded-full bg-neighbor-blue" style={{ width: `${stat.percentage}%` }} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                <div className="border-t border-slate-100 bg-white p-3">
                  {user ? (
                    <button
                      onClick={() => window.location.href = '/votaciones'}
                      className="text-xs font-bold text-neighbor-blue hover:text-neighbor-navy"
                    >
                      Ver todas las opciones →
                    </button>
                  ) : (
                    <Link to="/login" className="text-xs font-bold text-neighbor-blue hover:text-neighbor-navy">
                      Inicia sesión para votar →
                    </Link>
                  )}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="mt-5 rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm font-semibold text-slate-500">No hay votaciones activas.</p>
        )}
      </section>

      <PublicSection icon={Bell} title="Comunicados recientes" items={data.comunicados} emptyText="No hay comunicados publicados.">
        {(item) => <Card eyebrow={item.categoria} title={item.titulo} text={item.contenido} />}
      </PublicSection>

      <PublicSection icon={CalendarDays} title="Asambleas" items={data.asambleas} emptyText="No hay asambleas programadas.">
        {(item) => <Card eyebrow={dateTime(item.fecha)} title={item.titulo} text={`${item.lugar}${item.descripcion ? ` - ${item.descripcion}` : ''}`} />}
      </PublicSection>

      <PublicSection icon={Landmark} title="Directiva" items={data.directiva} emptyText="La directiva aun no ha sido registrada.">
        {(item) => <Card eyebrow={cargoLabel(item.cargo)} title={item.nombre} text={`${item.periodo}${item.email ? ` - ${item.email}` : ''}`} />}
      </PublicSection>

      <PublicSection icon={Newspaper} title="Noticias del barrio" items={data.noticias} emptyText="No hay noticias publicadas.">
        {(item) => <Card eyebrow="Noticia vecinal" title={item.titulo} text={item.resumen} />}
      </PublicSection>

      <footer id="contacto" className="mt-8 bg-neighbor-navy text-white">
        <div className="mx-auto grid max-w-7xl gap-8 px-6 py-10 md:grid-cols-[1.2fr_0.8fr_0.8fr]">
          <div>
            <div className="flex items-center gap-3">
              <img src="/neighbor-logo.png" alt="Neighbord" className="h-12 w-12 rounded-md bg-white object-contain" />
              <div>
                <p className="text-xl font-black">Neighbord</p>
                <p className="text-xs font-bold text-neighbor-leaf">Mas union, mejor comunidad</p>
              </div>
            </div>
            <p className="mt-4 max-w-md text-sm leading-6 text-white/75">Plataforma para organizar la gestion residencial, transparentar acuerdos y mantener informada a la comunidad.</p>
          </div>
          <div>
            <h3 className="font-black">Enlaces rapidos</h3>
            <div className="mt-4 grid gap-2 text-sm font-semibold text-white/75">
              <Link to="/login">Acceso</Link>
              <Link to="/registro">Registrate</Link>
              <Link to="/noticias">Noticias</Link>
            </div>
          </div>
          <div>
            <h3 className="font-black">Servicios</h3>
            <div className="mt-4 grid gap-2 text-sm font-semibold text-white/75">
              <span>Administracion</span>
              <span>Junta de vecinos</span>
              <span>Residentes</span>
            </div>
          </div>
          <div className="md:col-span-3">
            <div className="flex flex-wrap gap-x-8 gap-y-3 border-t border-white/10 pt-6 text-sm font-semibold text-white/75">
              <span className="inline-flex items-center gap-2"><MapPin className="h-4 w-4" /> Comunidad conectada</span>
              <span className="inline-flex items-center gap-2"><Mail className="h-4 w-4" /> comunicados@Neighbord.local</span>
              <span className="inline-flex items-center gap-2"><Phone className="h-4 w-4" /> Soporte vecinal</span>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}

function ArticlePreview({ item }) {
  return (
    <article className="grid overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm md:grid-cols-[220px_1fr]">
      <div className="flex min-h-44 items-center justify-center bg-neighbor-mist p-6">
        {item.imagen_url ? (
          <img src={mediaUrl(item.imagen_url)} alt={item.title} className="h-full w-full object-cover" />
        ) : (
          <img src="/neighbor-logo.png" alt="" className="h-28 w-28 object-contain opacity-90" />
        )}
      </div>
      <div className="p-6">
        <p className="text-xs font-black uppercase tracking-wide text-neighbor-green">{item.type}</p>
        <h3 className="mt-2 text-2xl font-black leading-tight text-neighbor-navy">{item.title}</h3>
        <p className="mt-3 line-clamp-3 text-sm leading-6 text-slate-600">{item.text}</p>
        <div className="mt-5 border-t border-slate-100 pt-4 text-xs font-bold text-slate-500">
          admin <span className="mx-2">/</span> Comunidad Neighbord
        </div>
      </div>
    </article>
  );
}

function SidebarBlock({ title, children }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-black text-neighbor-navy">{title}</h3>
      <div className="mt-4">{children}</div>
    </section>
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
