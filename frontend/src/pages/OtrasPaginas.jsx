import { Map, MessageCircle, Settings, Shield, UsersRound } from 'lucide-react';

const modules = [
  [Map, 'Mapa comunitario', 'Espacio preparado para integrar mapas de sectores, calles y puntos importantes.'],
  [MessageCircle, 'Chat vecinal', 'Módulo listo para conectar mensajería interna o canales por grupos.'],
  [UsersRound, 'Directiva', 'Registro público de cargos, responsables y periodos de gestión.'],
  [Shield, 'Auditoría', 'Historial de acciones administrativas sensibles.'],
  [Settings, 'Configuración', 'Preferencias del sistema, roles y parámetros comunitarios.']
];

export default function OtrasPaginas() {
  return (
    <section>
      <h1 className="page-title">Otros módulos</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {modules.map(([Icon, title, text]) => (
          <article key={title} className="card p-5">
            <Icon className="h-7 w-7 text-neighbor-green" />
            <h2 className="mt-3 font-bold text-neighbor-navy">{title}</h2>
            <p className="mt-2 text-sm text-slate-600">{text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

