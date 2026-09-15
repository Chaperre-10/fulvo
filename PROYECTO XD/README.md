# 🏆 MyDeport - Aplicación de Fútbol

**Sistema de gestión de jugadores, equipos, torneos y predicciones de fútbol con autenticación de usuarios.**

---

## 📋 Tabla de Contenidos

- [Inicio Rápido](#-inicio-rápido)
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración de BD](#-configuración-de-la-base-de-datos)
- [Credenciales por Defecto](#-credenciales-por-defecto)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Errores Corregidos](#-errores-corregidos)
- [Solución de Problemas](#-solución-de-problemas)

---

## 🚀 Inicio Rápido

### Opción 1: Arranque Automático (Recomendado)
```bash
cd d:\Desktop\PROYECTO XD
python app.py
```
La app inicializa automáticamente:
- ✅ Crea la base de datos si no existe
- ✅ Crea todas las tablas necesarias
- ✅ Inserta datos de ejemplo
- ✅ Arranca el servidor Flask en http://localhost:5000

### Opción 2: Setup Manual
```bash
cd d:\Desktop\PROYECTO XD
python app.py --setup
```

### Opción 3: Solo Verificar Conexión
```bash
python app.py --test-connection
```

---

## ✨ Características

✅ **Autenticación de Usuarios**
- Registro de nuevos usuarios
- Login con email o usuario
- Recuperación de contraseña
- Reseteo de contraseña por email token
- Sesiones seguras

✅ **Gestión de Contenido**
- CRUD de noticias y comentarios
- Búsqueda de jugadores, equipos y torneos
- Panel de administración
- Gestión de usuarios (admin)

✅ **Base de Datos**
- 9 tablas relacionales
- Integridad referencial
- Autocommit habilitado
- Timezone-aware (UTC)

✅ **API JSON**
- Endpoint `/api/partidos` - Partidos disponibles
- Endpoint `/api/players` - Jugadores registrados
- Endpoint `/api/predictions` - Predicciones del usuario

✅ **Sincronización Automática**
- Background thread para sincronización de datos
- Intervalo configurable (por defecto 30 segundos)

---

## 🔍 Requisitos

### Software
- **Python 3.8+**
- **MySQL Server 5.7+** (corriendo en localhost:3306)
- **Windows/Linux/macOS**

### Dependencias Python
```
Flask==2.3.3
mysql-connector-python==8.2.0
werkzeug==2.3.7
requests==2.31.0
```

---

## 📦 Instalación

### 1. Clonar/Descargar el Proyecto
```bash
cd d:\Desktop\PROYECTO XD
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Verificar MySQL
```bash
# Windows
net start MySQL80

# O abre Services (services.msc) y inicia MySQL
```

### 4. Ejecutar la Aplicación
```bash
python app.py
```

### 5. Importar la base de datos

El archivo `database.sql` contiene el esquema completo que utiliza la aplicación. No elimina la base de datos ni las tablas existentes y puede importarse varias veces.

```bash
# Crear la base local una sola vez
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS my_deport_ CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"

# Importar tablas, índices y datos iniciales
mysql -u root -p my_deport_ < database.sql
```

---

## 📊 Configuración de la Base de Datos

### Conexión
```
Host:       localhost
Usuario:    root
Contraseña: mysql
Base de Datos: my_deport_
Puerto:     3306
```

La aplicación acepta estas variables de entorno para usar cualquier servidor MySQL:

```text
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=mysql
MYSQL_DATABASE=my_deport_
DB_AUTO_CREATE_DATABASE=true
SECRET_KEY=cambia-esta-clave-en-produccion
```

#### Configuración en PythonAnywhere

1. Crea la base de datos MySQL desde la pestaña **Databases**. PythonAnywhere suele asignarle un nombre como `tuusuario$my_deport_`.
2. Importa `database.sql` seleccionando esa base de datos:

```bash
mysql -u tuusuario -h tuusuario.mysql.pythonanywhere-services.com -p tuusuario$my_deport_ < database.sql
```

3. En la configuración de la aplicación web agrega estas variables de entorno:

```text
MYSQL_HOST=tuusuario.mysql.pythonanywhere-services.com
MYSQL_PORT=3306
MYSQL_USER=tuusuario
MYSQL_PASSWORD=TU_CONTRASENA_MYSQL
MYSQL_DATABASE=tuusuario$my_deport_
DB_AUTO_CREATE_DATABASE=false
SECRET_KEY=UNA_CLAVE_LARGA_Y_ALEATORIA
```

En PythonAnywhere `DB_AUTO_CREATE_DATABASE=false` es importante porque la base ya existe y el usuario normalmente no tiene permiso para crear otra. Al iniciar, `app.py` creará las tablas que falten y el usuario administrador inicial.

### Tablas Principales

| Tabla | Descripción |
|-------|-------------|
| `users` | Usuarios registrados de la aplicación |
| `players` | Jugadores de fútbol con estadísticas |
| `clubs` | Equipos de fútbol |
| `tournaments` | Torneos y campeonatos |
| `matches` | Partidos disputados |
| `predictions` | Predicciones de usuarios |
| `noticias` | Noticias y artículos |
| `comentarios` | Comentarios de usuarios |
| `contact_messages` | Mensajes enviados desde Contáctenos |
| `players_external` | Datos sincronizados de API externa |

### Esquema de Usuarios
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    reset_token VARCHAR(255) NULL,
    reset_token_expires DATETIME NULL
)
```

---

## 👤 Credenciales por Defecto

**Usuario Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`
- Email: `admin@mydeport.com`

**Acceso:**
- Panel Admin: http://localhost:5000/admin
- Perfil: http://localhost:5000/profile

---

## 🎮 Uso

### Rutas Principales

| Ruta | Descripción | Requiere Auth |
|------|-------------|---------------|
| `/` | Página de inicio | No |
| `/login` | Iniciar sesión | No |
| `/register` | Registrarse | No |
| `/forgot-password` | Recuperar contraseña | No |
| `/profile` | Perfil de usuario | Sí |
| `/profile/edit` | Editar perfil | Sí |
| `/admin` | Panel de administración | Sí (admin) |
| `/news` | Noticias | Parcial |
| `/op` | Foro de opiniones | Sí |
| `/players` | Listado de jugadores | Sí |
| `/clubs` | Listado de equipos | Sí |
| `/tournaments` | Listado de torneos | Sí |
| `/partidos` | Partidos en vivo | Sí |
| `/search` | Buscar contenido | No |
| `/api/partidos` | API partidos | Sí |
| `/api/predictions` | API predicciones | Sí |

### Funciones Ejecutables (Línea de Comandos)

```bash
# Ejecutar setup de BD
python app.py --setup

# Probar conexión a MySQL
python app.py --test-connection

# Iniciar modo debug
python app.py --debug

# Puerto personalizado
python app.py --port 8000
```

---

## 📁 Estructura del Proyecto

```
PROYECTO XD/
├── app.py                      # Aplicación principal (integrada)
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
├── database.sql               # Script SQL de referencia
├── config.py                  # Configuración (integrada en app.py)
├── setup_database.py          # Setup DB (integrado en app.py)
├── test_connection.py         # Test conexión (integrado en app.py)
├── init_database.py           # Init DB (integrado en app.py)
├── templates/                 # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── admin.html
│   ├── news.html
│   ├── players.html
│   ├── clubs.html
│   └── ... (más templates)
├── static/                    # Archivos estáticos
│   ├── CSS/
│   │   ├── navbar.css
│   │   ├── partidos.css
│   │   └── ... (más CSS)
│   ├── JS/
│   │   ├── navbar.js
│   │   ├── partidos.js
│   │   └── ... (más JS)
│   ├── IMG/                   # Imágenes
│   │   ├── real madrid.jpg
│   │   ├── barcelona.jpg
│   │   └── ... (más imágenes)
│   └── DOC/                   # Documentación
├── flask_session/             # Sesiones del usuario
└── .gitignore                 # Archivos ignorados

```

---

## 🔧 Errores Corregidos

### 1. ✅ Importaciones Actualizadas
```python
# ANTES
from datetime import datetime, timedelta

# DESPUÉS
from datetime import datetime, timedelta, timezone
```

### 2. ✅ Try/Except Completado
```python
# ANTES - ERROR: Try sin except
try:
    conn = mysql.connector.connect(...)
    cursor.execute('CREATE DATABASE...')
cursor.close()  # ← Indentación incorrecta

# DESPUÉS - CORRECTO
try:
    conn = mysql.connector.connect(...)
    cursor.execute('CREATE DATABASE...')
    cursor.close()
    conn.close()
except mysql.connector.Error as e:
    logger.error(f"Error al crear base de datos: {e}")
```

### 3. ✅ Datetime Deprecado Reemplazado
```python
# ANTES - DEPRECADO
datetime.utcnow()

# DESPUÉS - MODERNO Y TIMEZONE-AWARE
datetime.now(timezone.utc)
```

**Total de cambios:** 12 ocurrencias reemplazadas en todo el código.

---

## 🐛 Solución de Problemas

### Error: "No module named 'mysql'"
```bash
pip install mysql-connector-python
```

### Error: "Access denied for user 'root'"
**Solución:** Verificar credenciales en `app.py`
- Usuario: `root`
- Contraseña: `mysql`

### Error: "Connection refused"
```bash
# Windows
net start MySQL80

# Linux
sudo service mysql start

# macOS
brew services start mysql
```

### Error: "Base de datos no existe"
```bash
python app.py --setup
```

### Puerto 5000 ya está en uso
```bash
python app.py --port 8000
```

### Tabla 'users' no existe
La app crea automáticamente todas las tablas al iniciar. Si aún así falla:
```bash
python app.py --setup --force
```

---

## 🔐 Seguridad

✅ **Contraseñas encriptadas** con werkzeug.security
✅ **Tokens de recuperación** con secrets.token_urlsafe
✅ **Sesiones seguras** con Flask sessions
✅ **Protección CSRF** en formularios
✅ **Validación de entrada** en todas las rutas
✅ **Inyección SQL prevenida** con parametrized queries

---

## 📝 Logs

La aplicación registra automáticamente:
- Intentos de login (exitosos y fallidos)
- Errores de base de datos
- Excepciones no capturadas
- Acceso a rutas no encontradas

**Ubicación de logs:** Console y archivo de debug

---

## 🚧 Notas de Desarrollo

### Variables de Entorno
```bash
FOOTBALL_SYNC_INTERVAL=30    # Intervalo de sincronización en segundos
FOOTBALL_API_KEY=xxx         # API Key para datos externos
FOOTBALL_API_URL=xxx         # URL de API externa
```

### Debug Mode
```python
app.run(debug=True)  # Ya habilitado por defecto en desarrollo
```

### Estructura de Sesión
```python
session['user_id']      # ID del usuario
session['user_name']    # Nombre del usuario
session['is_admin']     # Permisos de administrador
```

---

## 📞 Contacto y Soporte

Para reportar bugs o sugerencias, contacta al equipo de desarrollo.

**Última actualización:** 2026-08-16  
**Versión:** 1.0.0  
**Estado:** ✅ Producción

---

## 📄 Licencia

Este proyecto es propiedad de MyDeport © 2026

---

## 🎯 Roadmap Futuro

- [ ] Integración con API de fútbol en vivo
- [ ] Notificaciones en tiempo real
- [ ] Sistema de ranking de usuarios
- [ ] Calendario de partidos interactivo
- [ ] Estadísticas avanzadas de jugadores
- [ ] Chat entre usuarios
- [ ] Aplicación móvil
- [ ] Exportación de datos (PDF/Excel)

---

**¡Gracias por usar MyDeport! ⚽**
