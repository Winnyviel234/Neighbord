import React, { Suspense, ComponentType } from 'react';
import { Loader2 } from 'lucide-react';

// Componente de carga por defecto
const DefaultLoader = () => (
  <div className="flex items-center justify-center p-8">
    <Loader2 className="h-8 w-8 animate-spin text-neighbor-blue" />
    <span className="ml-2 text-gray-600">Cargando...</span>
  </div>
);

// Componente de carga para páginas
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-neighbor-mist">
    <div className="text-center">
      <Loader2 className="h-12 w-12 animate-spin text-neighbor-blue mx-auto mb-4" />
      <p className="text-lg text-neighbor-navy font-medium">Cargando página...</p>
    </div>
  </div>
);

// Componente de carga para secciones
const SectionLoader = ({ message = "Cargando contenido..." }) => (
  <div className="flex flex-col items-center justify-center p-12 bg-white rounded-lg shadow-soft">
    <Loader2 className="h-6 w-6 animate-spin text-neighbor-blue mb-2" />
    <p className="text-sm text-gray-600">{message}</p>
  </div>
);

// Componente de carga para botones/cards pequeños
const InlineLoader = ({ size = "sm" }) => {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8"
  };

  return (
    <Loader2 className={`animate-spin text-neighbor-blue ${sizeClasses[size]}`} />
  );
};

// Hook personalizado para lazy loading
export const useLazyImport = <T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
) => {
  return React.lazy(importFunc);
};

// Componente LazyLoader principal
interface LazyLoaderProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  errorFallback?: React.ReactNode;
}

export const LazyLoader: React.FC<LazyLoaderProps> = ({
  children,
  fallback = <DefaultLoader />,
  errorFallback
}) => {
  const [hasError, setHasError] = React.useState(false);

  if (hasError && errorFallback) {
    return <>{errorFallback}</>;
  }

  return (
    <Suspense
      fallback={fallback}
      onError={() => setHasError(true)}
    >
      {children}
    </Suspense>
  );
};

// Lazy loading para páginas completas
export const lazyPage = <T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
) => {
  const LazyComponent = React.lazy(importFunc);

  return (props: React.ComponentProps<T>) => (
    <LazyLoader fallback={<PageLoader />}>
      <LazyComponent {...props} />
    </LazyLoader>
  );
};

// Lazy loading para componentes de sección
export const lazySection = <T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  loadingMessage?: string
) => {
  const LazyComponent = React.lazy(importFunc);

  return (props: React.ComponentProps<T>) => (
    <LazyLoader fallback={<SectionLoader message={loadingMessage} />}>
      <LazyComponent {...props} />
    </LazyLoader>
  );
};

// Lazy loading para componentes pequeños
export const lazyComponent = <T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
) => {
  const LazyComponent = React.lazy(importFunc);

  return (props: React.ComponentProps<T>) => (
    <LazyLoader fallback={<InlineLoader />}>
      <LazyComponent {...props} />
    </LazyLoader>
  );
};

// Error boundary para lazy loading
interface LazyErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export class LazyErrorBoundary extends React.Component<
  LazyErrorBoundaryProps,
  { hasError: boolean }
> {
  constructor(props: LazyErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Lazy loading error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-8 text-center bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-medium">Error al cargar el componente</p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Reintentar
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export {
  DefaultLoader,
  PageLoader,
  SectionLoader,
  InlineLoader
};