import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  return (
    <div className="flex min-h-screen bg-[linear-gradient(135deg,#f8fafc_0%,#eef7fb_42%,#ecfdf5_100%)]">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-7xl px-6 py-7">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
