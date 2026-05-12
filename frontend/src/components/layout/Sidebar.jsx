import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { BarChart3, Bell, FileText, Landmark, LogOut, Map, MessageCircle, Menu, Newspaper, UserRound, Users, Vote, WalletCards, Zap } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { roleLabel } from '../../lib/utils';

const items = [
  { to: '/app', label: 'Dashboard', icon: BarChart3, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'], exact: true },
  { to: '/app/perfil', label: 'Perfil', icon: UserRound, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/vecinos', label: 'Vecinos', icon: Users, roles: ['admin', 'directiva', 'tesorero'] },
  { to: '/app/reuniones', label: 'Reuniones', icon: Bell, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/votaciones', label: 'Votaciones', icon: Vote, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/admin-dashboard', label: 'Panel admin', icon: BarChart3, roles: ['admin', 'directiva', 'tesorero'] },
  { to: '/app/mapa', label: 'Mapa del sector', icon: Map, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/comunidad', label: 'Comunidad en vivo', icon: MessageCircle, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/solicitudes', label: 'Solicitudes', icon: FileText, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/comunicados', label: 'Comunicados', icon: Newspaper, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/noticias', label: 'Noticias', icon: Newspaper, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/pagos', label: 'Pagos', icon: WalletCards, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/proyectos', label: 'Proyectos', icon: Zap, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/finanzas', label: 'Finanzas', icon: WalletCards, roles: ['admin', 'directiva', 'tesorero'] },
  { to: '/app/directiva', label: 'Directiva', icon: Landmark, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria'] },
  { to: '/app/reportes', label: 'Reportes', icon: BarChart3, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria'] },
  { to: '/app/notificaciones', label: 'Notificaciones', icon: Bell, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/preferencias-notificaciones', label: 'Preferencias', icon: Bell, roles: ['admin', 'directiva', 'tesorero', 'vocero', 'secretaria', 'vecino'] },
  { to: '/app/admin', label: 'Publicaciones', icon: Map, roles: ['admin', 'directiva'] }
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(() => {
    if (typeof window === 'undefined') return false;
    try {
      return JSON.parse(localStorage.getItem('neighbor_sidebar_collapsed') || 'false');
    } catch {
      return false;
    }
  });

  const toggleCollapsed = () => {
    const next = !collapsed;
    setCollapsed(next);
    localStorage.setItem('neighbor_sidebar_collapsed', JSON.stringify(next));
  };

  return (
     <aside className={`sticky top-0 flex h-screen flex-col border-r border-white/70 bg-white/80 shadow-[16px_0_50px_rgba(15,35,64,0.08)] backdrop-blur-xl transition-all duration-300 ${collapsed ? 'w-28' : 'w-72'}`}>
       <Link to="/" className={`flex items-center gap-3 border-b border-slate-200/70 p-5 ${collapsed ? 'justify-center' : ''}`}>
         <img src="/neighbor-logo.png" alt="Neighbord" className={`rounded-2xl object-contain shadow-sm ${collapsed ? 'h-14 w-14' : 'h-16 w-16'}`} />
        {!collapsed && (
          <div>
            <p className="text-xl font-black text-neighbor-navy">Neighbord</p>
            <p className="text-xs font-bold text-neighbor-green">Mas union, mejor comunidad</p>
          </div>
        )}
      </Link>

       <nav className="flex-1 space-y-1 overflow-y-auto p-4">
         {items.filter((item) => item.roles.includes(user?.rol)).map(({ to, label, icon: Icon, exact }) => (
           <NavLink
             key={to}
             to={to}
             end={exact}
             title={label}
             className={({ isActive }) =>
               `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-bold transition ${
                 isActive
                   ? 'bg-neighbor-navy text-white shadow-lg shadow-neighbor-navy/15'
                   : 'text-slate-600 hover:bg-white hover:text-neighbor-navy hover:shadow-sm'
               } ${collapsed ? 'justify-center' : ''}`
             }
           >
              <Icon className={`${collapsed ? 'h-8 w-8' : 'h-5 w-5'}`} />
             {!collapsed && <span>{label}</span>}
           </NavLink>
         ))}
       </nav>

      <div className="border-t border-slate-200/70 p-4">
        <button
          type="button"
          onClick={toggleCollapsed}
          className="mb-4 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-white transition"
        >
           <Menu className={`${collapsed ? 'h-8 w-8' : 'h-5 w-5'}`} />
          {!collapsed && <span>{collapsed ? 'Abrir barra' : 'Colapsar barra'}</span>}
        </button>
        {!collapsed ? (
          <>
            <p className="text-sm font-bold text-neighbor-navy">{user?.nombre}</p>
            <p className="text-xs text-slate-500">{roleLabel[user?.rol] || user?.rol}</p>
          </>
        ) : null}
        <button
          onClick={logout}
          className={`mt-4 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-white hover:text-neighbor-navy ${collapsed ? 'justify-center' : ''}`}
        >
           <LogOut className={`${collapsed ? 'h-8 w-8' : 'h-5 w-5'}`} />
          {!collapsed && 'Salir'}
        </button>
      </div>
    </aside>
  );
}

