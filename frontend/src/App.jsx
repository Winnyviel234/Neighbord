import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/layout/Layout';
import { Spinner } from './components/common';
import LandingPage from './pages/LandingPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import ForgotPasswordPage from './pages/ForgotPasswordPage.jsx';
import ResetPasswordPage from './pages/ResetPasswordPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import VecinosPage from './pages/VecinosPage.jsx';
import ReunionesPage from './pages/ReunionesPage.jsx';
import VotacionesPage from './pages/VotacionesPage.jsx';
import SolicitudesPage from './pages/SolicitudesPage.jsx';
import ComunicadosPage from './pages/ComunicadosPage.jsx';
import NoticiasPage from './pages/NoticiasPage.jsx';
import PagosPage from './pages/PagosPage.jsx';
import ProjectContributionPage from './pages/ProjectContributionPage.jsx';
import PerfilPage from './pages/PerfilPage.jsx';
import FinanzasPage from './pages/FinanzasPage.jsx';
import ReportesPage from './pages/ReportesPage.jsx';
import AdminPublicacionesPage from './pages/AdminPublicacionesPage.jsx';
import OtrasPaginas from './pages/OtrasPaginas.jsx';
import DirectivaPage from './pages/DirectivaPage.jsx';
import MapaSectorPage from './pages/MapaSectorPage.jsx';
import ExplorerMapPage from './pages/ExplorerMapPage.jsx';
import ComunidadPage from './pages/ComunidadPage.jsx';
import NotificationCenterPage from './pages/NotificationCenterPage.jsx';
import NotificationPreferencesPage from './pages/NotificationPreferencesPage.jsx';
import AdminDashboardPage from './pages/AdminDashboardPage.jsx';

const APPROVED_STATES = ['aprobado', 'activo'];

function Protected({ children, roles }) {
  const auth = useAuth();
  const { user, loading } = auth || { user: null, loading: false };
  if (loading) return <Spinner />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.rol !== 'admin' && !APPROVED_STATES.includes(user.estado)) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.rol)) return <Navigate to="/app" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/recuperar-contrasena" element={<ForgotPasswordPage />} />
      <Route path="/restablecer-contrasena" element={<ResetPasswordPage />} />
      <Route path="/registro" element={<RegisterPage />} />
      <Route path="/noticias" element={<NoticiasPage publicView />} />
      <Route path="/app" element={<Protected><Layout /></Protected>}>
        <Route index element={<DashboardPage />} />
        <Route path="perfil" element={<PerfilPage />} />
        <Route path="vecinos" element={<Protected roles={['admin', 'directiva', 'tesorero']}><VecinosPage /></Protected>} />
        <Route path="reuniones" element={<ReunionesPage />} />
        <Route path="votaciones" element={<VotacionesPage />} />
        <Route path="mapa" element={<MapaSectorPage />} />
        <Route path="mapa-explorer" element={<ExplorerMapPage />} />
        <Route path="comunidad" element={<ComunidadPage />} />
        <Route path="solicitudes" element={<SolicitudesPage />} />
        <Route path="comunicados" element={<ComunicadosPage />} />
        <Route path="noticias" element={<NoticiasPage />} />
        <Route path="pagos" element={<PagosPage />} />
        <Route path="finanzas" element={<Protected roles={['admin', 'directiva', 'tesorero']}><FinanzasPage /></Protected>} />
        <Route path="proyectos" element={<ProjectContributionPage />} />
        <Route path="directiva" element={<Protected roles={['admin', 'directiva', 'tesorero', 'vocero', 'secretaria']}><DirectivaPage /></Protected>} />
        <Route path="reportes" element={<Protected roles={['admin', 'directiva', 'tesorero', 'vocero', 'secretaria']}><ReportesPage /></Protected>} />
        <Route path="admin" element={<Protected roles={['admin']}><AdminPublicacionesPage /></Protected>} />
        <Route path="admin-dashboard" element={<Protected roles={['admin', 'directiva', 'tesorero']}><AdminDashboardPage /></Protected>} />
        <Route path="notificaciones" element={<NotificationCenterPage />} />
        <Route path="preferencias-notificaciones" element={<NotificationPreferencesPage />} />
        <Route path="otros" element={<OtrasPaginas />} />
      </Route>
    </Routes>
  );
}
