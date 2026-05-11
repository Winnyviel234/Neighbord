# 🚀 Neighbord - Inicio Rápido para Presentaciones

## ⚡ Inicio Automático (Recomendado)

**Doble click en `start_system.bat`** - Inicia todo automáticamente

## 🔧 Inicio Manual (Si es necesario)

### 1. Inicializar Sistema
```bash
cd backend
python initialize_system.py
```

### 2. Verificar Todo
```bash
cd backend
python pre_presentation_check.py
```

### 3. Iniciar Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 4. Iniciar Frontend (Nueva terminal)
```bash
cd frontend
npm run dev
```

## 🌐 Acceder al Sistema

- **Frontend**: http://localhost:5177
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## 🔐 Credenciales de Prueba

- **Email**: test@neighbord.com
- **Password**: test123

*(Usuario creado específicamente para presentaciones)*

## ✅ Checklist Pre-Presentación

- [ ] Ejecutar `start_system.bat`
- [ ] Verificar que ambos servidores estén corriendo
- [ ] Probar login con usuario demo
- [ ] Verificar que las páginas carguen correctamente
- [ ] Probar registro de nuevo usuario

## 🛠️ Solución de Problemas

### Si el backend no inicia:
```bash
cd backend
pip install -r requirements.txt
python initialize_system.py
```

### Si el frontend no inicia:
```bash
cd frontend
npm install
npm run dev
```

### Si hay errores de CORS:
- El sistema está configurado para permitir cualquier puerto localhost
- Si cambias de puerto, reinicia el backend

### Si hay errores de base de datos:
- El sistema funciona incluso sin tablas `roles` y `sectors`
- Ejecuta `python initialize_system.py` para crear datos de respaldo

## 🎯 Características Robustas

- ✅ **Sin dependencias de base de datos**: Funciona sin tablas `roles`/`sectors`
- ✅ **Auto-recuperación**: Manejo de errores graceful
- ✅ **CORS flexible**: Permite cualquier puerto localhost
- ✅ **Usuario demo**: Siempre disponible para pruebas
- ✅ **Verificación automática**: Script de pre-presentación

## 📞 Soporte

Si algo falla durante la presentación:
1. Cerrar todas las terminales
2. Ejecutar `start_system.bat` nuevamente
3. El sistema se auto-recuperará