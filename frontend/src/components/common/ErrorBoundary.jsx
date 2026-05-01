import React from 'react';
import { Link } from 'react-router-dom';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('Error renderizando la aplicacion:', error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <main className="flex min-h-screen items-center justify-center bg-[#f7fbfd] p-6">
          <section className="w-full max-w-lg rounded-lg border border-red-100 bg-white p-6 shadow-sm">
            <p className="text-sm font-black uppercase text-red-600">Error de interfaz</p>
            <h1 className="mt-2 text-2xl font-black text-neighbor-navy">La pagina no pudo cargarse</h1>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Recarga la pagina. Si el problema continua, revisa la consola del navegador para ver el detalle tecnico.
            </p>
            <pre className="mt-4 max-h-40 overflow-auto rounded-md bg-slate-950 p-3 text-xs text-white">
              {this.state.error.message}
            </pre>
            <Link to="/" className="btn-primary mt-5 inline-flex">
              Volver al inicio
            </Link>
          </section>
        </main>
      );
    }

    return this.props.children;
  }
}
