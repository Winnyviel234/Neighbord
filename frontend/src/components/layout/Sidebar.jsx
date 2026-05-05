import { Link, NavLink } from 'react-router-dom';
import { BarChart3, Bell, FileText, Home, Landmark, LogOut, Mail, Map, MessageCircle, Newspaper, UserRound, Users, Vote, WalletCards } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { roleLabel } from '../../lib/utils';

const items = [
  { to: '/app', label: 'Dashboard', icon: Home, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/admin-dashboard', label: 'Dashboard Admin', icon: BarChart3, roles: ['admin', 'directiva', 'tesorero'] },
  { to: '/app/perfil', label: 'Perfil', icon: UserRound, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/vecinos', label: 'Vecinos', icon: Users, roles: ['admin', 'directiva', 'tesorero'] },
  { to: '/app/reuniones', label: 'Reuniones', icon: Bell, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/votaciones', label: 'Votaciones', icon: Vote, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/mapa', label: 'Mapa del sector', icon: Map, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/comunidad', label: 'Comunidad en vivo', icon: MessageCircle, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/solicitudes', label: 'Solicitudes', icon: FileText, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/comunicados', label: 'Comunicados', icon: Newspaper, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/noticias', label: 'Noticias', icon: Newspaper, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/pagos', label: 'Pagos', icon: WalletCards, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/finanzas', label: 'Finanzas', icon: WalletCards, roles: ['admin', 'directiva', 'tesorero'] },
  { to: '/app/directiva', label: 'Directiva', icon: Landmark, roles: ['admin', 'directiva', 'tesorero'] },
  { to: '/app/reportes', label: 'Reportes', icon: BarChart3, roles: ['admin', 'directiva', 'tesorero'] },
  { to: '/app/notificaciones', label: 'Notificaciones', icon: Bell, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/preferencias-notificaciones', label: 'Preferencias', icon: Bell, roles: ['admin', 'directiva', 'tesorero', 'vecino'] },
  { to: '/app/admin', label: 'Publicaciones', icon: Mail, roles: ['admin', 'directiva'] }
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  return (
    <aside className="flex h-screen w-72 flex-col border-r border-slate-200 bg-white">
      <Link to="/" className="flex items-center gap-3 border-b border-slate-200 p-5">
        <img src="/neighbor-logo.png" alt="Neighbord" className="h-14 w-14 rounded-lg object-contain" />
        <div>
          <p className="text-xl font-black text-neighbor-navy">Neighbord</p>
          <p className="text-xs font-semibold text-neighbor-green">Más unión, mejor comunidad</p>
        </div>
      </Link>
      <nav className="flex-1 space-y-1 overflow-y-auto p-4">
        {items.filter((item) => item.roles.includes(user?.rol)).map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/app'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold transition ${
                isActive ? 'bg-neighbor-blue text-white' : 'text-slate-700 hover:bg-neighbor-mist hover:text-neighbor-navy'
              }`
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-slate-200 p-4">
        <p className="text-sm font-bold text-neighbor-navy">{user?.nombre}</p>
        <p className="text-xs text-slate-500">{roleLabel[user?.rol] || user?.rol}</p>
        <button onClick={logout} className="mt-4 flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100">
          <LogOut className="h-4 w-4" /> Salir
        </button>
      </div>
    </aside>
  );
}
