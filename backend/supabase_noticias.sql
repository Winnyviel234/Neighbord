create table if not exists noticias (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  resumen text not null,
  contenido text not null,
  imagen_url text,
  publicado boolean not null default true,
  autor_id uuid references usuarios(id),
  created_at timestamptz not null default now()
);

create index if not exists idx_noticias_publicado on noticias(publicado, created_at desc);

delete from comunicados
where titulo in ('Asamblea comunitaria', 'Jornada de limpieza');

delete from noticias
where titulo in ('Nuevo sistema comunitario', 'Participación vecinal');
