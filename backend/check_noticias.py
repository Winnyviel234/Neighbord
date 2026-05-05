#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.core.supabase import table

noticias = table('noticias').select('*').eq('publicado', True).order('created_at', desc=True).limit(6).execute().data
print('Noticias encontradas:', len(noticias))
for n in noticias:
    print(f'- {n["titulo"]}')