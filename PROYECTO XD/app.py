from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import time
import os
import sys
import requests  # pyright: ignore[reportMissingModuleSource]
from datetime import datetime, timedelta, timezone
import logging
import secrets

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger('mydeport')


# Registra excepciones no controladas que ocurren en el hilo principal.
def global_excepthook(exc_type, exc_value, exc_traceback):
    # Log all uncaught exceptions; treat SystemExit specially so we can observe code
    if issubclass(exc_type, SystemExit):
        logger.warning(f'Uncaught SystemExit: code={exc_value.code if hasattr(exc_value, "code") else exc_value}')
    else:
        logger.exception('Uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))


# Install global excepthook to capture SystemExit from any thread that bubbles up
sys.excepthook = global_excepthook


# Registra excepciones no controladas producidas por hilos secundarios.
def thread_excepthook(args):
    # threading.ExceptHookArgs: .exc_type, .exc_value, .exc_traceback, .thread
    exc_type = getattr(args, 'exc_type', None)
    exc_value = getattr(args, 'exc_value', None)
    exc_tb = getattr(args, 'exc_traceback', None)
    if exc_type:
        if issubclass(exc_type, SystemExit):
            logger.warning(f'Uncaught SystemExit in thread {getattr(args, "thread", None)}: code={getattr(exc_value, "code", exc_value)}')
        else:
            logger.exception(f'Uncaught exception in thread {getattr(args, "thread", None)}', exc_info=(exc_type, exc_value, exc_tb))


# Install threading excepthook if available (Python 3.8+)
if hasattr(threading, 'excepthook'):
    threading.excepthook = thread_excepthook

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
app.secret_key = os.getenv('SECRET_KEY', 'mydeport-secret-key')

# Configuración de conexión: permite usar las credenciales locales o las de PythonAnywhere.
DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
DB_PORT = int(os.getenv('MYSQL_PORT', '3306'))
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', 'mysql')
DB_NAME = os.getenv('MYSQL_DATABASE', 'my_deport_')
DB_AUTO_CREATE_DATABASE = os.getenv('DB_AUTO_CREATE_DATABASE', 'true').lower() in ('1', 'true', 'yes', 'on')

# Datos de noticias iniciales que se muestran cuando todavía no hay contenido en la base de datos.
noticias = [
    {
        'titulo': 'La llegada de Cuadrado "El Panita" al futbol Colombiano en Millonarios',
        'resumen': 'Una imagen especial del legado y la pasión del volante colombiano en su regreso a la hinchada.',
        'enlace': 'https://www.fifa.com/es',
        'imagen': 'IMG/Cuadrado.jfif'
    },
    {
        'titulo': 'El Mundial causa impresión en todo el mundo',
        'resumen': 'Las grandes ligas y los fanáticos siguen atentos a cada jornada del torneo mundial.',
        'enlace': 'https://www.fifa.com/es',
        'imagen': 'IMG/affiche de la finale de la coupe du monde 1966 Angleterre Allemagne.jfif'
    }
]


def get_db_connection():
    """Obtiene conexión a la base de datos MySQL"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            use_unicode=True,
        )
        conn.autocommit = True
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Error de conexión a MySQL: {e}")
        raise


    # Crea la base de datos, las tablas y los registros iniciales necesarios para la aplicación.
def init_db():
    """Inicializa la base de datos si es necesario"""
    if DB_AUTO_CREATE_DATABASE:
        try:
            # En local se puede crear la base automáticamente; PythonAnywhere normalmente la crea antes.
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                charset='utf8mb4',
                use_unicode=True,
            )
            cursor = conn.cursor()
            cursor.execute(
                f'CREATE DATABASE IF NOT EXISTS `{DB_NAME}` '
                'CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
            )
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            logger.error(f"Error al crear base de datos: {e}")

    # Create external players table for synced player data
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players_external (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(200),
            nacionalidad VARCHAR(100),
            posicion VARCHAR(100),
            club VARCHAR(200),
            numero_camiseta INT,
            altura VARCHAR(50),
            peso VARCHAR(50),
            fecha_nacimiento DATE,
            descripcion TEXT,
            goles INT DEFAULT 0,
            asistencias INT DEFAULT 0,
            partidos_jugados INT DEFAULT 0,
            tarjetas_amarillas INT DEFAULT 0,
            tarjetas_rojas INT DEFAULT 0,
            velocidad INT DEFAULT 0,
            resistencia INT DEFAULT 0,
            defensa INT DEFAULT 0,
            logros TEXT
        )
    ''')
    cursor.close()
    conn.close()

    # Create matches table for synced match data
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            league_name VARCHAR(200),
            country VARCHAR(100),
            kickoff DATETIME,
            home_team VARCHAR(200),
            away_team VARCHAR(200),
            home_odd VARCHAR(30),
            draw_odd VARCHAR(30),
            away_odd VARCHAR(30),
            stadium VARCHAR(200)
        )
    ''')
    cursor.close()
    conn.close()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            correo VARCHAR(100) NOT NULL UNIQUE,
            usuario VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        )
    ''')
    cursor.execute("SHOW COLUMNS FROM users LIKE 'is_admin'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")

    cursor.execute("SHOW COLUMNS FROM users LIKE 'reset_token'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) NULL")

    cursor.execute("SHOW COLUMNS FROM users LIKE 'reset_token_expires'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires DATETIME NULL")
    cursor.close()

    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            league_name VARCHAR(200),
            home_team VARCHAR(200),
            away_team VARCHAR(200),
            kickoff DATETIME NULL,
            prediction VARCHAR(100) NOT NULL,
            match_key VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY uq_user_match (user_id, match_key)
        )
    ''')
    cursor.execute("SHOW COLUMNS FROM predictions LIKE 'prediction'")
    prediction_column = cursor.fetchone()
    if prediction_column and prediction_column[1].lower() not in ('varchar(100)', 'varchar(255)', 'text'):
        cursor.execute('ALTER TABLE predictions MODIFY prediction VARCHAR(100) NOT NULL')
    cursor.close()

    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS noticias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            titulo VARCHAR(255) NOT NULL,
            resumen TEXT NOT NULL,
            enlace VARCHAR(255) NULL,
            imagen VARCHAR(255) NULL,
            fecha_creacion DATETIME NOT NULL,
            fecha_modificacion DATETIME NULL,
            FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comentarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            comentario TEXT NOT NULL,
            fecha_creacion DATETIME NOT NULL,
            fecha_modificacion DATETIME NULL,
            FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            correo VARCHAR(255) NOT NULL,
            asunto VARCHAR(255) NOT NULL,
            mensaje TEXT NOT NULL,
            estado ENUM('nuevo', 'leido', 'respondido') NOT NULL DEFAULT 'nuevo',
            usuario_id INT NULL,
            fecha_creacion DATETIME NOT NULL,
            fecha_modificacion DATETIME NULL,
            FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_contact_messages_fecha (fecha_creacion),
            INDEX idx_contact_messages_estado (estado)
        )
    ''')
    cursor.close()

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE is_admin = TRUE LIMIT 1")
    if not cursor.fetchone():
        cursor.execute(
            'INSERT INTO users (nombre, correo, usuario, password, is_admin) VALUES (%s, %s, %s, %s, %s)',
            ('Administrador', 'admin@mydeport.com', 'admin', generate_password_hash('admin123'), True)
        )
    cursor.close()

    # Seed sample noticias and comentarios if empty
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE usuario = %s', ('admin',))
    admin_user = cursor.fetchone()
    admin_id = admin_user[0] if admin_user else None

    seed_noticias = [
        {
            'titulo': 'La llegada de Cuadrado "El Panita" al futbol Colombiano en Millonarios',
            'resumen': 'Una imagen especial del legado y la pasión del volante colombiano en su regreso a la hinchada.',
            'enlace': 'https://www.fifa.com/es',
            'imagen': 'IMG/Cuadrado.jfif'
        },
        {
            'titulo': 'El Mundial causa impresión en todo el mundo',
            'resumen': 'Las grandes ligas y los fanáticos siguen atentos a cada jornada del torneo mundial.',
            'enlace': 'https://www.fifa.com/es',
            'imagen': 'IMG/affiche de la finale de la coupe du monde 1966 Angleterre Allemagne.jfif'
        }
    ]

    if admin_id:
        for noticia in seed_noticias:
            cursor.execute('SELECT 1 FROM noticias WHERE titulo = %s LIMIT 1', (noticia['titulo'],))
            if cursor.fetchone() is None:
                cursor.execute(
                    'INSERT INTO noticias (usuario_id, titulo, resumen, enlace, imagen, fecha_creacion) VALUES (%s, %s, %s, %s, %s, %s)',
                    (admin_id, noticia['titulo'], noticia['resumen'], noticia['enlace'], noticia['imagen'], datetime.now(timezone.utc))
                )

    cursor.execute('SELECT 1 FROM comentarios WHERE comentario = %s LIMIT 1', ('Bienvenido al foro de opiniones. Aquí puedes compartir tu punto de vista y el administrador podrá gestionarlo.',))
    if cursor.fetchone() is None and admin_id:
        cursor.execute(
            'INSERT INTO comentarios (usuario_id, comentario, fecha_creacion) VALUES (%s, %s, %s)',
            (admin_id, 'Bienvenido al foro de opiniones. Aquí puedes compartir tu punto de vista y el administrador podrá gestionarlo.', datetime.now(timezone.utc))
        )
    cursor.close()
    conn.close()

    # Create players table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            nacionalidad VARCHAR(50),
            posicion VARCHAR(30),
            club VARCHAR(100),
            numero_camiseta INT,
            altura VARCHAR(10),
            peso VARCHAR(10),
            fecha_nacimiento DATE,
            descripcion TEXT,
            goles INT DEFAULT 0,
            asistencias INT DEFAULT 0,
            partidos_jugados INT DEFAULT 0,
            tarjetas_amarillas INT DEFAULT 0,
            tarjetas_rojas INT DEFAULT 0,
            velocidad INT DEFAULT 0,
            resistencia INT DEFAULT 0,
            defensa INT DEFAULT 0,
            logros TEXT
        )
    ''')
    cursor.close()

    # Ensure older database schemas get the columns used by the app
    cursor = conn.cursor()
    for column_name, column_definition in [
        ('goles', 'INT DEFAULT 0'),
        ('asistencias', 'INT DEFAULT 0'),
        ('partidos_jugados', 'INT DEFAULT 0'),
        ('tarjetas_amarillas', 'INT DEFAULT 0'),
        ('tarjetas_rojas', 'INT DEFAULT 0'),
        ('velocidad', 'INT DEFAULT 0'),
        ('resistencia', 'INT DEFAULT 0'),
        ('defensa', 'INT DEFAULT 0'),
        ('logros', 'TEXT')
    ]:
        cursor.execute("SHOW COLUMNS FROM players LIKE %s", (column_name,))
        if not cursor.fetchone():
            cursor.execute(f'ALTER TABLE players ADD COLUMN {column_name} {column_definition}')
    cursor.close()

    # Inserta los jugadores iniciales sin borrar datos añadidos posteriormente.
    cursor = conn.cursor()
    cursor.execute('''
        INSERT IGNORE INTO players (nombre, nacionalidad, posicion, club, numero_camiseta, altura, peso, fecha_nacimiento, descripcion, goles, asistencias, partidos_jugados, tarjetas_amarillas, tarjetas_rojas, velocidad, resistencia, defensa, logros)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s),
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s),
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        'Vozinha (Josimar Évora Dias)', 'Cabo Verde', 'Arquero', 'Colo-Colo', 1, '1.85m', '82kg', '1990-07-22', 'Arquero caboverdiano destacado por su seguridad bajo los palos y su historial de porterías invictas en el fútbol profesional.', 0, 0, 371, 12, 0, 78, 85, 88, '140 partidos sin recibir goles • Referente de la selección de Cabo Verde • Reconocido por su liderazgo y solidez defensiva',
        'Cristiano Ronaldo', 'Portugal', 'Extremo/Delantero', 'Al Nassr', 7, '1.87m', '84kg', '1985-02-05', 'Leyenda viva del fútbol con cifras históricas en clubes y selecciones, conocida por su profesionalismo, impacto goleador y presencia en las grandes competiciones.', 923, 96, 1261, 162, 12, 94, 92, 35, '1,261 partidos oficiales en clubes • 923 goles en clubes • 495 goles y 96 asistencias en las 5 grandes ligas europeas • Figura histórica del fútbol moderno',
        'Kylian Mbappé', 'Francia', 'Delantero', 'Real Madrid', 9, '1.78m', '80kg', '1998-12-20', 'Joven estrella internacional con un gran impacto ofensivo, velocidad y capacidad para decidir partidos en los grandes escenarios del fútbol.', 357, 116, 465, 48, 2, 97, 90, 40, '465 partidos oficiales en clubes • 357 goles • 116 asistencias • 247 goles y 75 asistencias en competiciones de máximo nivel • Referente ofensivo de su generación'
    ))
    cursor.close()
    conn.close()

    # Create clubs table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clubs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            pais VARCHAR(50),
            ciudad VARCHAR(50),
            estadio VARCHAR(100),
            ano_fundacion INT,
            descripcion TEXT
        )
    ''')
    cursor.close()

    # Inserta los clubes iniciales sin borrar datos añadidos posteriormente.
    cursor = conn.cursor()
    cursor.execute('''
        INSERT IGNORE INTO clubs (nombre, pais, ciudad, estadio, ano_fundacion, descripcion)
        VALUES 
        (%s, %s, %s, %s, %s, %s),
        (%s, %s, %s, %s, %s, %s),
        (%s, %s, %s, %s, %s, %s)
    ''', (
        'Real Madrid', 'España', 'Madrid', 'Santiago Bernabéu', 1902, 'Liga (LaLiga): Subcampeón, con 86 puntos. Champions League: Cuartos de final.',
        'FC Barcelona', 'España', 'Barcelona', 'Camp Nou', 1899, 'Liga (LaLiga): Campeón, con 94 puntos. Champions League: Cuartos de final.',
        'Manchester United', 'Inglaterra', 'Manchester', 'Old Trafford', 1878, 'Liga (Premier League): Tercer puesto, con 71 puntos.'
    ))
    cursor.close()
    conn.close()

    # Create tournaments table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tournaments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            tipo VARCHAR(50),
            pais_sede VARCHAR(50),
            ano INT,
            ganador VARCHAR(100),
            descripcion TEXT
        )
    ''')
    cursor.close()

    # Inserta los torneos iniciales sin borrar datos añadidos posteriormente.
    cursor = conn.cursor()
    cursor.execute('''
        INSERT IGNORE INTO tournaments (nombre, tipo, pais_sede, ano, ganador, descripcion)
        VALUES 
        (%s, %s, %s, %s, %s, %s),
        (%s, %s, %s, %s, %s, %s),
        (%s, %s, %s, %s, %s, %s)
    ''', (
        'Champions League 2025/2026', 'Clubes', 'Hungría (Budapest)', 2026, 'Paris Saint-Germain', 'Final disputada en Budapest y ganada por Paris Saint-Germain.',
        'La Liga 2025/2026', 'Liga', 'España', 2026, 'FC Barcelona', 'Temporada 2025/2026 con FC Barcelona como campeón y Real Madrid como subcampeón.',
        'Mundial 2026', 'Internacional', 'Estados Unidos, México y Canadá', 2026, 'España', 'Copa del Mundo disputada en Estados Unidos, México y Canadá, con España como ganador.'
    ))
    cursor.close()
    conn.close()


init_db()


# Restringe una función para que solo puedan ejecutarla usuarios autenticados.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'danger')
            return redirect(url_for('login', next=request.url))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM users WHERE id = %s', (session['user_id'],))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            session.clear()
            flash('Tu sesión expiró. Inicia sesión nuevamente.', 'warning')
            return redirect(url_for('login'))
        cursor.close()
        conn.close()

        return f(*args, **kwargs)
    return decorated_function


@app.before_request
# Configura la protección común aplicada antes de procesar las solicitudes.
def protect_routes():
    allowed_routes = {'index', 'login', 'register', 'logout', 'static', 'contact', 'search', 'news', 'api_players', 'api_partidos', 'forgot_password', 'reset_password'}
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a esta página.', 'danger')
        return redirect(url_for('login'))


@app.route('/')
# Página principal con el resumen de noticias y contenido deportivo destacado.
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT COUNT(*) AS total FROM players')
    total_players = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT COUNT(*) AS total FROM clubs')
    total_clubs = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT COUNT(*) AS total FROM tournaments')
    total_tournaments = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT COUNT(*) AS total FROM matches')
    total_matches = cursor.fetchone()['total'] or 0

    cursor.execute('''
        SELECT titulo, resumen, enlace, imagen, fecha_creacion
        FROM noticias
        ORDER BY fecha_creacion DESC
        LIMIT 3
    ''')
    latest_news = cursor.fetchall()

    cursor.execute('''
        SELECT league_name, home_team, away_team, kickoff
        FROM matches
        ORDER BY kickoff ASC
        LIMIT 3
    ''')
    upcoming_matches = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'index.html',
        user_name=session.get('user_name'),
        is_admin=session.get('is_admin', False),
        total_players=total_players,
        total_clubs=total_clubs,
        total_tournaments=total_tournaments,
        total_matches=total_matches,
        latest_news=latest_news,
        upcoming_matches=upcoming_matches,
    )


@app.route('/login', methods=['GET', 'POST'])
# Formulario y proceso de inicio de sesión de los usuarios.
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        login_input = request.form.get('login_input', '').strip()
        password = request.form.get('password', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE correo = %s OR usuario = %s', (login_input, login_input))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            session['is_admin'] = bool(user['is_admin'])
            flash('Inicio de sesión correcto.', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))

        flash('Correo, usuario o contraseña incorrectos.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
# Registro de una cuenta nueva y validación de sus datos.
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '')
        confirmar = request.form.get('confirmar', '')

        if not all([nombre, correo, usuario, password, confirmar]):
            flash('Completa todos los campos.', 'danger')
            return redirect(url_for('register'))

        if password != confirmar:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('register'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE correo = %s OR usuario = %s', (correo, usuario))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash('El correo o usuario ya está registrado.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (nombre, correo, usuario, password) VALUES (%s, %s, %s, %s)',
            (nombre, correo, usuario, hashed_password)
        )
        cursor.close()
        conn.close()

        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
# Solicitud de recuperación de contraseña mediante un token temporal.
def forgot_password():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email_or_user = request.form.get('email_or_user', '').strip()
        if not email_or_user:
            flash('Ingresa tu correo o usuario para recuperar la contraseña.', 'warning')
            return redirect(url_for('forgot_password'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, correo, usuario FROM users WHERE correo = %s OR usuario = %s', (email_or_user, email_or_user))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET reset_token=%s, reset_token_expires=%s WHERE id=%s',
                (token, expires_at, user['id'])
            )
            cursor.close()
            conn.close()
            reset_link = url_for('reset_password', token=token, _external=True)
            return render_template('forgot_password.html', reset_link=reset_link, token_generated=True)

        flash('Si existe una cuenta asociada, te mostraremos un enlace para restablecer la contraseña.', 'info')
        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html', reset_link=None, token_generated=False)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
# Validación del token y cambio de contraseña del usuario.
def reset_password(token):
    if 'user_id' in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT id FROM users WHERE reset_token = %s AND reset_token_expires > %s',
        (token, datetime.now(timezone.utc))
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        flash('El enlace de recuperación ha expirado o es inválido.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirmar = request.form.get('confirmar', '')

        if not password or not confirmar:
            flash('Completa ambos campos de contraseña.', 'warning')
            return redirect(url_for('reset_password', token=token))

        if password != confirmar:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('reset_password', token=token))

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET password=%s, reset_token=NULL, reset_token_expires=NULL WHERE id=%s',
            (hashed_password, user['id'])
        )
        cursor.close()
        conn.close()
        flash('Contraseña actualizada correctamente. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


@app.route('/success')
@login_required
# Página de confirmación después de completar una operación.
def success():
    return render_template('success.html')


@app.route('/logout')
# Cierra la sesión actual y elimina sus datos temporales.
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
# Consulta los datos del perfil del usuario autenticado.
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nombre, correo, usuario, is_admin FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile.html', user=user)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
# Muestra y guarda los cambios realizados en el perfil.
def edit_profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nombre, correo, usuario FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '')
        confirmar = request.form.get('confirmar', '')

        if not all([nombre, correo, usuario]):
            flash('Nombre, correo y usuario son obligatorios.', 'danger')
            return redirect(url_for('edit_profile'))

        # Check uniqueness for correo and usuario excluding current user
        check_cursor = conn.cursor()
        check_cursor.execute('SELECT id FROM users WHERE (correo = %s OR usuario = %s) AND id != %s', (correo, usuario, session['user_id']))
        if check_cursor.fetchone():
            check_cursor.close()
            flash('El correo o usuario ya está en uso por otro usuario.', 'danger')
            return redirect(url_for('edit_profile'))
        check_cursor.close()

        # Handle op
        # tional password change
        if password:
            if password != confirmar:
                flash('Las contraseñas no coinciden.', 'danger')
                return redirect(url_for('edit_profile'))
            hashed = generate_password_hash(password)
            upd_cursor = conn.cursor()
            upd_cursor.execute('UPDATE users SET nombre=%s, correo=%s, usuario=%s, password=%s WHERE id=%s', (nombre, correo, usuario, hashed, session['user_id']))
            upd_cursor.close()
        else:
            upd_cursor = conn.cursor()
            upd_cursor.execute('UPDATE users SET nombre=%s, correo=%s, usuario=%s WHERE id=%s', (nombre, correo, usuario, session['user_id']))
            upd_cursor.close()

        # Update session display name
        session['user_name'] = nombre
        flash('Datos actualizados correctamente. Usa tus nuevas credenciales para iniciar sesión si las cambiaste.', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('profile'))

    cursor.close()
    conn.close()
    return render_template('edit_profile.html', user=user)


@app.route('/admin')
@login_required
# Panel de administración con usuarios, noticias, comentarios y predicciones.
def admin():
    if not session.get('is_admin', False):
        flash('No tienes permisos para entrar al panel de administración.', 'danger')
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nombre, correo, usuario, is_admin FROM users ORDER BY id')
    users = cursor.fetchall()

    cursor.execute('''
        SELECT n.id, n.titulo, n.resumen, n.enlace, n.imagen, n.fecha_creacion, n.fecha_modificacion, u.nombre AS autor
        FROM noticias n
        LEFT JOIN users u ON u.id = n.usuario_id
        ORDER BY n.fecha_creacion DESC
    ''')
    noticias_admin = cursor.fetchall()

    cursor.execute('''
        SELECT c.id, c.comentario, c.fecha_creacion, c.fecha_modificacion, u.nombre AS autor
        FROM comentarios c
        LEFT JOIN users u ON u.id = c.usuario_id
        ORDER BY c.fecha_creacion DESC
    ''')
    comentarios_admin = cursor.fetchall()

    cursor.execute('''
        SELECT p.id, p.league_name, p.home_team, p.away_team, p.kickoff, p.prediction, p.created_at, u.nombre AS autor
        FROM predictions p
        LEFT JOIN users u ON u.id = p.user_id
        ORDER BY p.created_at DESC
    ''')
    predicciones_admin = cursor.fetchall()

    cursor.execute('''
        SELECT id, nombre, correo, asunto, mensaje, estado, fecha_creacion, fecha_modificacion
        FROM contact_messages
        ORDER BY fecha_creacion DESC
    ''')
    mensajes_contacto_admin = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template(
        'admin.html',
        users=users,
        noticias_admin=noticias_admin,
        comentarios_admin=comentarios_admin,
        predicciones_admin=predicciones_admin,
        mensajes_contacto_admin=mensajes_contacto_admin,
    )


@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
# Elimina un usuario desde el panel de administración.
def delete_user(user_id):
    if not session.get('is_admin', False):
        flash('No tienes permisos para eliminar usuarios.', 'danger')
        return redirect(url_for('profile'))

    if user_id == session['user_id']:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
    cursor.close()
    conn.close()
    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/edit/<int:user_id>', methods=['POST'])
@login_required
# Actualiza los datos de un usuario desde el panel administrativo.
def admin_edit_user(user_id):
    if not session.get('is_admin', False):
        flash('No tienes permisos para editar usuarios.', 'danger')
        return redirect(url_for('profile'))

    # Prevent admin from accidentally removing their own admin status via this form
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    usuario = request.form.get('usuario', '').strip()
    password = request.form.get('password', '')
    confirmar = request.form.get('confirmar', '')

    if not all([nombre, correo, usuario]):
        flash('Nombre, correo y usuario son obligatorios.', 'danger')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.cursor()
    # Check uniqueness excluding this user
    check_cursor = conn.cursor()
    check_cursor.execute('SELECT id FROM users WHERE (correo = %s OR usuario = %s) AND id != %s', (correo, usuario, user_id))
    if check_cursor.fetchone():
        check_cursor.close()
        flash('El correo o usuario ya está en uso por otro usuario.', 'danger')
        return redirect(url_for('admin'))
    check_cursor.close()

    if password:
        if password != confirmar:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('admin'))
        hashed = generate_password_hash(password)
        cursor.execute('UPDATE users SET nombre=%s, correo=%s, usuario=%s, password=%s WHERE id=%s', (nombre, correo, usuario, hashed, user_id))
    else:
        cursor.execute('UPDATE users SET nombre=%s, correo=%s, usuario=%s WHERE id=%s', (nombre, correo, usuario, user_id))

    cursor.close()
    conn.close()
    flash('Usuario actualizado correctamente.', 'success')
    return redirect(url_for('admin'))


@app.route('/users')
@login_required

# Lista los usuarios registrados para su gestión administrativa.
def users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nombre, correo, usuario FROM users ORDER BY id')
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('user.html', usuarios=usuarios)


@app.route('/admin/delete-news/<int:news_id>', methods=['POST'])
@login_required
# Elimina una noticia publicada por un usuario.
def admin_delete_news(news_id):
    if not session.get('is_admin', False):
        flash('No tienes permisos para eliminar noticias.', 'danger')
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM noticias WHERE id = %s', (news_id,))
    cursor.close()
    conn.close()
    flash('Noticia eliminada correctamente.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/edit-news/<int:news_id>', methods=['POST'])
@login_required
# Modifica el contenido de una noticia existente.
def admin_edit_news(news_id):
    if not session.get('is_admin', False):
        flash('No tienes permisos para editar noticias.', 'danger')
        return redirect(url_for('profile'))

    titulo = request.form.get('titulo', '').strip()
    resumen = request.form.get('resumen', '').strip()
    enlace = request.form.get('enlace', '').strip()
    imagen = request.form.get('imagen', '').strip()

    if not titulo or not resumen:
        flash('Título y resumen son obligatorios.', 'danger')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE noticias SET titulo=%s, resumen=%s, enlace=%s, imagen=%s, fecha_modificacion=%s WHERE id=%s',
        (titulo, resumen, enlace or None, imagen or None, datetime.now(timezone.utc), news_id)
    )
    cursor.close()
    conn.close()
    flash('Noticia actualizada correctamente.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/delete-comment/<int:comment_id>', methods=['POST'])
@login_required
# Elimina un comentario desde el panel administrativo.
def admin_delete_comment(comment_id):
    if not session.get('is_admin', False):
        flash('No tienes permisos para eliminar comentarios.', 'danger')
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM comentarios WHERE id = %s', (comment_id,))
    cursor.close()
    conn.close()
    flash('Comentario eliminado correctamente.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/delete-prediction/<int:prediction_id>', methods=['POST'])
@login_required
# Elimina una predicción guardada por un usuario.
def admin_delete_prediction(prediction_id):
    if not session.get('is_admin', False):
        flash('No tienes permisos para eliminar predicciones.', 'danger')
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions WHERE id = %s', (prediction_id,))
    cursor.close()
    conn.close()
    flash('Predicción eliminada correctamente.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/edit-prediction/<int:prediction_id>', methods=['POST'])
@login_required
# Edita el texto de una predicción existente.
def admin_edit_prediction(prediction_id):
    if not session.get('is_admin', False):
        flash('No tienes permisos para editar predicciones.', 'danger')
        return redirect(url_for('profile'))

    nueva_prediccion = request.form.get('prediction', '').strip()
    if not nueva_prediccion:
        flash('La predicción no puede estar vacía.', 'danger')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE predictions SET prediction=%s, updated_at=%s WHERE id=%s',
        (nueva_prediccion, datetime.now(timezone.utc), prediction_id)
    )
    cursor.close()
    conn.close()
    flash('Predicción actualizada correctamente.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/edit-comment/<int:comment_id>', methods=['POST'])
@login_required
# Edita un comentario desde la administración.
def admin_edit_comment(comment_id):
    if not session.get('is_admin', False):
        flash('No tienes permisos para editar comentarios.', 'danger')
        return redirect(url_for('profile'))

    comentario = request.form.get('comentario', '').strip()
    if not comentario:
        flash('El comentario no puede estar vacío.', 'danger')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE comentarios SET comentario=%s, fecha_modificacion=%s WHERE id=%s',
        (comentario, datetime.now(timezone.utc), comment_id)
    )
    cursor.close()
    conn.close()
    flash('Comentario actualizado correctamente.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/delete-contact/<int:message_id>', methods=['POST'])
@login_required
# Elimina un mensaje recibido mediante el formulario de contacto.
def admin_delete_contact(message_id):
    if not session.get('is_admin', False):
        flash('No tienes permisos para eliminar mensajes de contacto.', 'danger')
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contact_messages WHERE id = %s', (message_id,))
    cursor.close()
    conn.close()
    flash('Mensaje de contacto eliminado correctamente.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/edit-contact/<int:message_id>', methods=['POST'])
@login_required
# Actualiza los datos y el estado de un mensaje recibido por Contactenos.
def admin_edit_contact(message_id):
    if not session.get('is_admin', False):
        flash('No tienes permisos para editar mensajes de contacto.', 'danger')
        return redirect(url_for('profile'))

    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    asunto = request.form.get('asunto', '').strip()
    mensaje = request.form.get('mensaje', '').strip()
    estado = request.form.get('estado', 'nuevo').strip()

    if not all([nombre, correo, asunto, mensaje]) or estado not in {'nuevo', 'leido', 'respondido'}:
        flash('Completa correctamente todos los datos del mensaje.', 'danger')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE contact_messages
           SET nombre=%s, correo=%s, asunto=%s, mensaje=%s, estado=%s, fecha_modificacion=%s
           WHERE id=%s''',
        (nombre, correo, asunto, mensaje, estado, datetime.now(timezone.utc), message_id),
    )
    cursor.close()
    conn.close()
    flash('Mensaje de contacto actualizado correctamente.', 'success')
    return redirect(url_for('admin'))


@app.route('/actualizar/<int:id>')
# Carga los datos de un usuario antes de abrir su formulario de edición.
def actualizar_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT nombre, correo FROM users WHERE id = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('users'))

    return render_template(
        'actuser.html',
        id=id,
        nombre=user['nombre'],
        email=user['correo']
    )


@app.route('/newuser/<int:id>', methods=['GET', 'POST'])
# Guarda los cambios del formulario de actualización de usuarios.
def newuser(id):
    if request.method == 'POST':
        nombre = request.form.get('nuevo_nombre', '').strip()
        correo = request.form.get('nuevo_email', '').strip()
        password = request.form.get('nuevo_contraseña', '').strip()

        if not nombre or not correo:
            flash('Nombre y correo son obligatorios.', 'danger')
            return redirect(url_for('newuser', id=id))

        conn = get_db_connection()
        cursor = conn.cursor()
        if password:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                'UPDATE users SET nombre=%s, correo=%s, password=%s WHERE id=%s',
                (nombre, correo, hashed_password, id)
            )
        else:
            cursor.execute(
                'UPDATE users SET nombre=%s, correo=%s WHERE id=%s',
                (nombre, correo, id)
            )
        cursor.close()
        conn.close()

        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('users'))

    return redirect(url_for('actualizar_usuario', id=id))


@app.route('/contact', methods=['GET', 'POST'])
# Recibe mensajes enviados mediante el formulario de contacto.
def contact():
    try:
        if request.method == 'POST':
            nombre = request.form.get('nombre', '').strip()
            correo = request.form.get('correo', '').strip()
            asunto = request.form.get('asunto', '').strip()
            mensaje = request.form.get('mensaje', '').strip()

            if not nombre or not correo or not asunto or not mensaje:
                flash('Por favor completa todos los campos obligatorios.', 'danger')
                return render_template('contact.html', nombre=nombre, correo=correo, asunto=asunto, mensaje=mensaje)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO contact_messages
                   (nombre, correo, asunto, mensaje, estado, usuario_id, fecha_creacion)
                   VALUES (%s, %s, %s, %s, 'nuevo', %s, %s)''',
                (
                    nombre,
                    correo,
                    asunto,
                    mensaje,
                    session.get('user_id'),
                    datetime.now(timezone.utc),
                ),
            )
            cursor.close()
            conn.close()

            flash('Gracias por escribirnos. Tu mensaje ha sido recibido.', 'success')
            return redirect(url_for('contact'))

        return render_template('contact.html')
    except Exception as exc:
        logger.exception('Error en la ruta de contacto: %s', exc)
        return render_template('error.html', title='Error interno', message='Ocurrió un error interno al procesar tu solicitud. Por favor intenta más tarde.'), 500


@app.route('/news', methods=['GET', 'POST'])
# Muestra noticias y permite publicar nuevas noticias a usuarios autenticados.
def news():
    public_only = 'user_id' not in session
    if request.method == 'POST':
        if public_only:
            flash('Debes iniciar sesión para publicar noticias.', 'danger')
            return redirect(url_for('login'))

        titulo = request.form.get('titulo', '').strip()
        resumen = request.form.get('resumen', '').strip()
        enlace = request.form.get('enlace', '').strip()
        imagen = request.form.get('imagen', '').strip()

        if titulo and resumen:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE id = %s', (session['user_id'],))
            if cursor.fetchone() is None:
                cursor.close()
                conn.close()
                session.clear()
                flash('Tu sesión expiró. Inicia sesión nuevamente.', 'warning')
                return redirect(url_for('login'))

            cursor.execute(
                'INSERT INTO noticias (usuario_id, titulo, resumen, enlace, imagen, fecha_creacion) VALUES (%s, %s, %s, %s, %s, %s)',
                (session['user_id'], titulo, resumen, enlace or 'https://www.fifa.com/es', imagen or 'IMG/luchoo.webp', datetime.now(timezone.utc))
            )
            cursor.close()
            conn.close()
            flash('Noticia agregada correctamente.', 'success')
        else:
            flash('Completa al menos el título y el resumen.', 'danger')

        return redirect(url_for('news'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT COUNT(*) AS total FROM noticias')
    total_noticias = cursor.fetchone()['total']
    cursor.execute('''
        SELECT n.id, n.titulo, n.resumen, n.enlace, n.imagen, n.fecha_creacion, n.fecha_modificacion, u.nombre AS autor
        FROM noticias n
        LEFT JOIN users u ON u.id = n.usuario_id
        ORDER BY n.fecha_creacion DESC
    ''')
    todas_noticias = cursor.fetchall()
    cursor.close()
    conn.close()

    cuadrado_title = 'La llegada de Cuadrado "El Panita" al futbol Colombiano en Millonarios'
    mundial_title = 'El Mundial causa impresión en todo el mundo'

    cuadrado_data = {
        'titulo': cuadrado_title,
        'resumen': 'Una imagen especial del legado y la pasión del volante colombiano en su regreso a la hinchada.',
        'enlace': 'https://www.fifa.com/es',
        'imagen': 'IMG/Cuadrado.jfif'
    }

    mundial_data = {
        'titulo': mundial_title,
        'resumen': 'Las grandes ligas y los fanáticos siguen atentos a cada jornada del torneo mundial.',
        'enlace': 'https://www.fifa.com/es',
        'imagen': 'IMG/affiche de la finale de la coupe du monde 1966 Angleterre Allemagne.jfif'
    }

    noticias_filtradas = []
    seen_titles = set()

    for noticia in todas_noticias:
        titulo = noticia.get('titulo', '')
        if 'Cuadrado' in titulo or 'Millonarios' in titulo:
            noticia.update(cuadrado_data)
            if noticia['titulo'] not in seen_titles:
                noticias_filtradas.append(noticia)
                seen_titles.add(noticia['titulo'])
        elif 'Mundial' in titulo or 'mundo' in titulo.lower() and 'Mundial' in titulo:
            noticia.update(mundial_data)
            if noticia['titulo'] not in seen_titles:
                noticias_filtradas.append(noticia)
                seen_titles.add(noticia['titulo'])

    if cuadrado_title not in seen_titles:
        noticias_filtradas.insert(0, {
            'id': None,
            'titulo': cuadrado_title,
            'resumen': cuadrado_data['resumen'],
            'enlace': cuadrado_data['enlace'],
            'imagen': cuadrado_data['imagen'],
            'fecha_creacion': datetime.now(timezone.utc),
            'fecha_modificacion': None,
            'autor': 'Administrador'
        })
        seen_titles.add(cuadrado_title)

    if mundial_title not in seen_titles:
        noticias_filtradas.append({
            'id': None,
            'titulo': mundial_title,
            'resumen': mundial_data['resumen'],
            'enlace': mundial_data['enlace'],
            'imagen': mundial_data['imagen'],
            'fecha_creacion': datetime.now(timezone.utc),
            'fecha_modificacion': None,
            'autor': 'Administrador'
        })
        seen_titles.add(mundial_title)

    todas_noticias = noticias_filtradas[:2]
    visible_noticias = todas_noticias if public_only else todas_noticias
    return render_template('news.html', noticias=visible_noticias, public_only=public_only, total_noticias=len(todas_noticias))


@app.route('/op', methods=['GET', 'POST'])
@login_required
# Gestiona el foro de opiniones y sus comentarios.
def op():
    if request.method == 'POST':
        comentario = request.form.get('comentario', '').strip()
        if not comentario:
            flash('Escribe un comentario antes de publicar.', 'danger')
            return redirect(url_for('op'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM users WHERE id = %s', (session['user_id'],))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            session.clear()
            flash('Tu sesión expiró. Inicia sesión nuevamente.', 'warning')
            return redirect(url_for('login'))

        cursor.execute(
            'INSERT INTO comentarios (usuario_id, comentario, fecha_creacion) VALUES (%s, %s, %s)',
            (session['user_id'], comentario, datetime.now(timezone.utc))
        )
        cursor.close()
        conn.close()
        flash('Comentario publicado correctamente.', 'success')
        return redirect(url_for('op'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT c.id, c.comentario, c.fecha_creacion, c.fecha_modificacion, u.nombre AS autor
        FROM comentarios c
        LEFT JOIN users u ON u.id = c.usuario_id
        ORDER BY c.fecha_creacion DESC
    ''')
    comentarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('op.html', comentarios=comentarios)


@app.route('/players')
@login_required
# Muestra el catálogo de jugadores disponibles.
def players():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM players ORDER BY nombre')
    players_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('players.html', players=players_list)


@app.route('/clubs')
@login_required
# Muestra el catálogo de clubes deportivos.
def clubs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM clubs ORDER BY nombre')
    clubs_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clubs.html', clubs=clubs_list)


@app.route('/tournaments')
@login_required
# Muestra el catálogo de torneos.
def tournaments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tournaments ORDER BY ano DESC')
    tournaments_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tournaments.html', tournaments=tournaments_list)


@app.route('/search-players', methods=['GET', 'POST'])
@login_required
# Busca jugadores por nombre u otros datos introducidos por el usuario.
def search_players():
    players_found = []
    search_query = ''
    
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        
        if search_query:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM players WHERE nombre LIKE %s', (f'%{search_query}%',))
            players_found = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not players_found:
                flash(f'No se encontraron jugadores con "{search_query}"', 'info')
    
    return render_template('search_players.html', players=players_found, search_query=search_query)


@app.route('/partidos')
@login_required
# Página visual de partidos, ligas, cuotas y predicciones.
def partidos():
    return render_template('partidos.html')


# Convierte diferentes formatos de fecha de partidos a un valor comparable.
def parse_match_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    if not candidate:
        return None
    if candidate.endswith('Z'):
        candidate = candidate[:-1] + '+00:00'
    try:
        return datetime.fromisoformat(candidate)
    except ValueError:
        try:
            return datetime.strptime(candidate, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None


# Selecciona y ordena los partidos más relevantes para mostrarlos al usuario.
def pick_relevant_matches(matches, limit=80):
    if not matches:
        return []

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    important_leagues = {
        'Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'UEFA Champions League',
        'UEFA Europa League', 'CONMEBOL Libertadores', 'Liga BetPlay Dimayor', 'MLS',
        'Liga MX', 'Copa Libertadores', 'Liga Profesional', 'Brasileirão'
    }

    relevant = []
    for match in matches:
        kickoff = parse_match_datetime(match.get('kickoff'))
        if kickoff is None:
            continue

        if kickoff.tzinfo is None:
            kickoff = kickoff.replace(tzinfo=timezone.utc)

        league_name = (match.get('league_name') or '').strip()
        kickoff_date = kickoff.date()

        if kickoff < now - timedelta(days=2):
            continue
        if kickoff > now + timedelta(days=7):
            continue

        # Orden exacto pedido por el usuario:
        # 1) hoy
        # 2) mañana
        # 3) ya jugados hoy
        # 4) primeros partidos de temporada
        if kickoff_date == today_start.date() and kickoff >= now:
            priority = 0
        elif kickoff_date == tomorrow_start.date():
            priority = 1
        elif kickoff_date == today_start.date() and kickoff < now:
            priority = 2
        elif league_name in important_leagues and kickoff >= now and kickoff <= now + timedelta(days=7):
            priority = 3
        else:
            continue

        relevant.append((match, priority, kickoff))

    relevant.sort(key=lambda item: (item[1], item[2]))
    return [match for match, _, _ in relevant[:limit]]


@app.route('/api/partidos')
@login_required
# API que devuelve partidos sincronizados en formato JSON.
def api_partidos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM matches ORDER BY kickoff ASC LIMIT 200')
    matches = cursor.fetchall()
    cursor.close()
    conn.close()

    if not matches:
        fallback_data = fetch_external_data_example()
        sync_external_to_db(fallback_data)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM matches ORDER BY kickoff ASC LIMIT 200')
        matches = cursor.fetchall()
        cursor.close()
        conn.close()

    matches = pick_relevant_matches(matches)

    leagues = {}
    featured = []
    for m in sorted(matches, key=lambda item: ((item.get('league_name') or '').lower(), str(item.get('kickoff') or ''))):
        league = m.get('league_name') or 'Primera'
        entry = leagues.setdefault(league, {'name': league, 'country': m.get('country') or '', 'matches': []})
        kickoff = parse_match_datetime(m.get('kickoff'))
        kickoff_iso = kickoff.isoformat() if isinstance(kickoff, datetime) else str(m.get('kickoff') or '')
        home_team = (m.get('home_team') or '').strip() or 'Local'
        away_team = (m.get('away_team') or '').strip() or 'Visitante'
        stadium = (m.get('stadium') or '').strip() or 'Estadio'
        match_entry = {
            'time': kickoff_iso,
            'home': home_team,
            'away': away_team,
            'home_odd': m.get('home_odd') or '2.20',
            'draw_odd': m.get('draw_odd') or '3.20',
            'away_odd': m.get('away_odd') or '3.10',
            'stadium': stadium,
            'home_badge': m.get('home_badge') or get_team_badge_url(home_team),
            'away_badge': m.get('away_badge') or get_team_badge_url(away_team),
            'competition': league,
        }
        entry['matches'].append(match_entry)

    ordered_leagues = []
    for league_name in sorted(leagues.keys(), key=lambda name: name.lower()):
        league_entry = leagues[league_name]
        league_entry['matches'] = sorted(league_entry['matches'], key=lambda match: str(match.get('time') or ''))
        ordered_leagues.append(league_entry)

    for league_entry in ordered_leagues:
        for match in league_entry['matches'][:2]:
            featured.append({
                'competition': league_entry['name'],
                'home': match.get('home'),
                'away': match.get('away'),
                'kickoff': match.get('time'),
                'home_odd': match.get('home_odd'),
                'draw_odd': match.get('draw_odd'),
                'away_odd': match.get('away_odd'),
                'stadium': match.get('stadium'),
                'home_badge': match.get('home_badge'),
                'away_badge': match.get('away_badge'),
            })

    return jsonify({'last_update': datetime.now(timezone.utc).isoformat(), 'leagues': ordered_leagues, 'featured': featured[:8]})


@app.route('/api/predictions', methods=['GET', 'POST'])
@login_required
# API para consultar, crear y actualizar predicciones del usuario.
def api_predictions():
    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT id, league_name, home_team, away_team, kickoff, prediction, match_key, created_at FROM predictions WHERE user_id = %s ORDER BY created_at DESC',
            (session['user_id'],)
        )
        predictions = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'predictions': predictions})

    data = request.get_json(silent=True) or {}
    match_key = (data.get('match_key') or '').strip()
    prediction = (data.get('prediction') or '').strip()
    league_name = (data.get('league_name') or '').strip()
    home_team = (data.get('home_team') or '').strip()
    away_team = (data.get('away_team') or '').strip()
    kickoff = data.get('kickoff') or None

    if not match_key or not prediction:
        return jsonify({'error': 'Faltan datos para guardar la predicción.'}), 400

    if kickoff is not None:
        try:
            kickoff_dt = datetime.fromisoformat(str(kickoff).replace('Z', '+00:00'))
            kickoff = kickoff_dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            kickoff = None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM predictions WHERE user_id = %s AND match_key = %s', (session['user_id'], match_key))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            'UPDATE predictions SET league_name = %s, home_team = %s, away_team = %s, kickoff = %s, prediction = %s, updated_at = %s WHERE user_id = %s AND match_key = %s',
            (league_name, home_team, away_team, kickoff, prediction, datetime.now(timezone.utc), session['user_id'], match_key)
        )
    else:
        cursor.execute(
            'INSERT INTO predictions (user_id, league_name, home_team, away_team, kickoff, prediction, match_key, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (session['user_id'], league_name, home_team, away_team, kickoff, prediction, match_key, datetime.now(timezone.utc), datetime.now(timezone.utc))
        )
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'prediction': prediction})


# Obtiene la imagen adecuada para un jugador, club o torneo.
def get_entity_image(entity_type, record):
    if not record:
        return None

    label = ''
    if entity_type == 'player':
        label = (record.get('nombre') or '') + ' ' + (record.get('club') or '')
    elif entity_type == 'club':
        label = record.get('nombre') or ''
    elif entity_type == 'tournament':
        label = (record.get('nombre') or '') + ' ' + (record.get('ganador') or '')
    else:
        label = record.get('nombre') or ''

    normalized = label.lower().replace('é', 'e').replace('á', 'a').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')

    if 'cristiano ronaldo' in normalized or 'ronaldo' in normalized:
        return 'IMG/ronaldo.jpg'
    if 'kylian mbappe' in normalized or 'mbappe' in normalized:
        return 'IMG/mbappe.jpg'
    if 'vozinha' in normalized or 'josimar evora' in normalized:
        return 'IMG/Vozinha2026.jpg'
    if 'real madrid' in normalized:
        return 'IMG/Real Madrid.jpg'
    if 'barcelona' in normalized:
        return 'IMG/Barcelona.jpg'
    if 'manchester united' in normalized or 'manchesteru' in normalized:
        return 'IMG/ManchesterU.jpg'
    if 'champions league' in normalized:
        return 'IMG/UEFA Champions League.jpg'
    if 'mundial' in normalized or 'world cup' in normalized:
        return 'IMG/mundial2026.jpg'
    if 'la liga' in normalized or 'liga' in normalized:
        return 'IMG/liga.jpg'

    return None


# Busca coincidencias en las entidades disponibles de la aplicación.
def get_search_results(query):
    if not query or not query.strip():
        return []

    search_term = f'%{query.strip()}%'
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            '''
            SELECT 'player' as type, p.*
            FROM players p
            WHERE LOWER(p.nombre) LIKE LOWER(%s)
               OR LOWER(COALESCE(p.nacionalidad, '')) LIKE LOWER(%s)
               OR LOWER(COALESCE(p.posicion, '')) LIKE LOWER(%s)
               OR LOWER(COALESCE(p.club, '')) LIKE LOWER(%s)
               OR LOWER(COALESCE(p.descripcion, '')) LIKE LOWER(%s)
               OR LOWER(COALESCE(p.logros, '')) LIKE LOWER(%s)
            ORDER BY p.nombre ASC
            ''',
            (search_term, search_term, search_term, search_term, search_term, search_term),
        )
        players = cursor.fetchall()
        for player in players:
            player['image'] = get_entity_image('player', player)

        cursor.execute(
            '''
            SELECT 'club' as type, c.*
            FROM clubs c
            WHERE LOWER(c.nombre) LIKE LOWER(%s)
               OR LOWER(COALESCE(c.pais, '')) LIKE LOWER(%s)
               OR LOWER(COALESCE(c.ciudad, '')) LIKE LOWER(%s)
               OR LOWER(COALESCE(c.estadio, '')) LIKE LOWER(%s)
               OR LOWER(COALESCE(c.descripcion, '')) LIKE LOWER(%s)
            ORDER BY c.nombre ASC
            ''',
            (search_term, search_term, search_term, search_term, search_term),
        )
        clubs = cursor.fetchall()
        for club in clubs:
            club['image'] = get_entity_image('club', club)

        cursor.execute(
            '''
            SELECT 'tournament' as type, t.*
            FROM tournaments t
            WHERE LOWER(t.nombre) LIKE LOWER(%s)
               OR LOWER(COALESCE(t.tipo, '')) LIKE LOWER(%s)
               OR LOWER(COALESCE(t.pais_sede, '')) LIKE LOWER(%s)
               OR LOWER(COALESCE(t.ganador, '')) LIKE LOWER(%s)
               OR LOWER(COALESCE(t.descripcion, '')) LIKE LOWER(%s)
            ORDER BY t.ano DESC, t.nombre ASC
            ''',
            (search_term, search_term, search_term, search_term, search_term),
        )
        tournaments = cursor.fetchall()
        for tournament in tournaments:
            tournament['image'] = get_entity_image('tournament', tournament)
    finally:
        cursor.close()
        conn.close()

    return players + clubs + tournaments


@app.route('/autocomplete', methods=['GET'])
# API de sugerencias rápidas para el buscador global.
def autocomplete():
    try:
        query = request.args.get('q', '').strip()

        if not query or len(query) < 1:
            return jsonify([])

        search_term = f'%{query}%'
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            'SELECT nombre, "player" as type FROM players WHERE LOWER(nombre) LIKE LOWER(%s) LIMIT 8',
            (search_term,),
        )
        players = cursor.fetchall()

        cursor.execute(
            'SELECT nombre, "club" as type FROM clubs WHERE LOWER(nombre) LIKE LOWER(%s) LIMIT 8',
            (search_term,),
        )
        clubs = cursor.fetchall()

        cursor.execute(
            'SELECT nombre, "tournament" as type FROM tournaments WHERE LOWER(nombre) LIKE LOWER(%s) LIMIT 8',
            (search_term,),
        )
        tournaments = cursor.fetchall()

        cursor.close()
        conn.close()

        results = players + clubs + tournaments
        return jsonify(results)
    except SystemExit as se:
        logger.warning(f'autocomplete triggered SystemExit: {se}')
        return jsonify([])
    except Exception as ex:
        logger.exception('Error in autocomplete: %s', ex)
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        return jsonify([])


@app.route('/search', methods=['GET', 'POST'])
# Buscador global de jugadores, clubes, torneos y otros contenidos.
def search():
    # Allow anonymous users to search; results will be shown to everyone

    if request.method == 'GET':
        query = request.args.get('q', request.args.get('query', '')).strip()
    else:
        query = request.form.get('q', request.form.get('query', request.form.get('search_query', ''))).strip()

    if not query:
        flash('Por favor ingresa un término de búsqueda.', 'warning')
        return redirect(url_for('index'))

    results = get_search_results(query)

    if not results:
        flash(f'No se encontraron resultados para "{query}"', 'info')

    return render_template('search_results.html', results=results, query=query)


@app.route('/api/players')
# API que devuelve los jugadores almacenados en la base de datos.
def api_players():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM players_external ORDER BY nombre LIMIT 200')
    players = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'last_update': datetime.now(timezone.utc).isoformat(), 'players': players})


@app.errorhandler(404)
def handle_not_found_error(error):
    logger.warning('Page not found: %s', request.path)
    return render_template('error.html', title='Página no encontrada', message='No se encontró la página solicitada.'), 404


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    logger.exception('Unhandled exception during request: %s', error)
    if request.path.startswith('/api') or request.is_json or request.accept_mimetypes.accept_json:
        return jsonify({'error': 'internal_server_error'}), 500
    return render_template('error.html', title='Error interno', message='Ocurrió un error interno. Por favor intenta más tarde.'), 500


# Devuelve la URL del escudo correspondiente al nombre de un equipo.
def get_team_badge_url(team_name):
    if not team_name:
        return None
    n = team_name.strip().lower()
    mapping = {
        'real madrid': 'IMG/Real Madrid.jpg',
        'barcelona': 'IMG/Barcelona.jpg',
        'manchester united': 'IMG/ManchesterU.jpg',
        'bayern munich': 'IMG/UEFA Champions League.jpg',
        'psg': 'IMG/UEFA Champions League.jpg',
        'inter miami': 'IMG/IMG/Real Madrid.jpg',
        'la galaxy': 'IMG/Real Madrid.jpg',
        'inter': 'IMG/UEFA Champions League.jpg',
        'juventus': 'IMG/UEFA Champions League.jpg',
        'milan': 'IMG/UEFA Champions League.jpg',
        'napoli': 'IMG/UEFA Champions League.jpg',
        'roma': 'IMG/UEFA Champions League.jpg',
        'lazio': 'IMG/UEFA Champions League.jpg',
        'manchester city': 'IMG/ManchesterU.jpg',
        'arsenal': 'IMG/UEFA Champions League.jpg',
        'liverpool': 'IMG/UEFA Champions League.jpg',
        'chelsea': 'IMG/UEFA Champions League.jpg',
        'tottenham': 'IMG/UEFA Champions League.jpg',
        'atletico de madrid': 'IMG/Real Madrid.jpg',
        'valencia': 'IMG/UEFA Champions League.jpg',
        'sevilla': 'IMG/UEFA Champions League.jpg',
        'girona': 'IMG/UEFA Champions League.jpg',
        'millonarios': 'IMG/Real Madrid.jpg',
        'junior': 'IMG/UEFA Champions League.jpg',
        'atletico nacional': 'IMG/Real Madrid.jpg',
        'santa fe': 'IMG/UEFA Champions League.jpg',
        'pasto': 'IMG/UEFA Champions League.jpg',
        'tolima': 'IMG/UEFA Champions League.jpg',
    }
    return mapping.get(n)


# Consulta la fuente externa de datos deportivos y normaliza su respuesta.
def fetch_external_data_example():
    """Obtiene datos en tiempo real desde API de fútbol y usa fallback local si falla."""
    api_key = os.environ.get('FOOTBALL_API_KEY') or 'ffc5f91a37d5d902d8b3977d724ff5f7'
    api_url = os.environ.get('FOOTBALL_API_URL') or 'https://v3.football.api-sports.io'
    os.environ.setdefault('FOOTBALL_API_KEY', api_key)
    os.environ.setdefault('FOOTBALL_API_URL', api_url)

    headers = {'x-apisports-key': api_key, 'Accept': 'application/json'}

    def normalize_matches(raw_matches):
        normalized = []
        for item in raw_matches:
            fixture = item.get('fixture') or {}
            league = item.get('league') or {}
            teams = item.get('teams') or {}
            home_team = teams.get('home') or {}
            away_team = teams.get('away') or {}
            score = item.get('score') or {}
            halftime = score.get('halftime') or {}
            fulltime = score.get('fulltime') or {}
            current_score = fulltime if fulltime else halftime if halftime else {}
            normalized.append({
                'league_name': league.get('name') or 'Liga',
                'country': league.get('country') or '',
                'kickoff': fixture.get('date') or None,
                'home_team': home_team.get('name') or 'Local',
                'away_team': away_team.get('name') or 'Visitante',
                'home_odd': '',
                'draw_odd': '',
                'away_odd': '',
                'stadium': (fixture.get('venue') or {}).get('name') or '',
                'home_badge': home_team.get('logo'),
                'away_badge': away_team.get('logo'),
                'status': (fixture.get('status') or {}).get('short') or '',
                'home_goals': current_score.get('home'),
                'away_goals': current_score.get('away'),
            })
        return sorted(normalized, key=lambda match: ((match.get('league_name') or '').lower(), str(match.get('kickoff') or '')))

    try:
        now = datetime.now(timezone.utc)
        from_date = (now - timedelta(days=2)).strftime('%Y-%m-%d')
        to_date = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        live_resp = requests.get(
            f"{api_url}/fixtures?live=all&from={from_date}&to={to_date}&next=60",
            headers=headers,
            timeout=15,
        )
        live_resp.raise_for_status()
        live_payload = live_resp.json() or {}
        fixtures = live_payload.get('response') or []
        matches = normalize_matches(fixtures[:60])

        if matches:
            players = []
            try:
                players_resp = requests.get(f"{api_url}/players?league=39&season=2025", headers=headers, timeout=15)
                players_resp.raise_for_status()
                players_data = players_resp.json() or {}
                players = players_data.get('response') or []
                players = [
                    {
                        'nombre': p.get('player', {}).get('name'),
                        'nacionalidad': p.get('player', {}).get('nationality'),
                        'posicion': p.get('statistics', [{}])[0].get('games', {}).get('position') if p.get('statistics') else '',
                        'club': p.get('statistics', [{}])[0].get('team', {}).get('name') if p.get('statistics') else '',
                        'numero_camiseta': '',
                        'altura': '',
                        'peso': '',
                        'fecha_nacimiento': '',
                        'descripcion': '',
                        'goles': 0,
                        'asistencias': 0,
                        'partidos_jugados': 0,
                        'velocidad': 0,
                        'resistencia': 0,
                        'defensa': 0,
                        'logros': '',
                    }
                    for p in players[:10]
                ]
            except Exception:
                players = []
            return {'matches': matches, 'players': players}

    except Exception as e:
        logger.warning('API de fútbol no disponible, usando fallback local: %s', e)

    # Fallback sample data with multiple leagues and competitions, kept within a short real-time window.
    now = datetime.now(timezone.utc)
    def make_match(league_name, country, offset_days, hour, home_team, away_team, home_odd, draw_odd, away_odd, stadium):
        kickoff = (now + timedelta(days=offset_days)).replace(hour=hour, minute=0, second=0, microsecond=0)
        return {
            'league_name': league_name,
            'country': country,
            'kickoff': kickoff.isoformat(),
            'home_team': home_team,
            'away_team': away_team,
            'home_odd': home_odd,
            'draw_odd': draw_odd,
            'away_odd': away_odd,
            'stadium': stadium,
            'home_badge': None,
            'away_badge': None,
        }

    fallback_matches = [
        make_match('CONMEBOL Libertadores', 'Sudamérica', 0, 17, 'Mirassol SP', 'LDU Quito', '2.10', '3.25', '3.45', 'Estádio José Jorge Damous'),
        make_match('CONMEBOL Libertadores', 'Sudamérica', 1, 19, 'Rosario Central', 'Corinthians', '1.92', '3.35', '4.05', 'Estadio Gigante de Arroyito'),
        make_match('UEFA Europa League', 'Europa', -1, 12, 'CS U Craiova', 'Kuopion Palloseura', '2.30', '3.40', '2.75', 'Ion Oblemenco Stadium'),
        make_match('UEFA Europa League', 'Europa', 0, 12, 'AC Omonia Nicosia', 'Lincoln Red Imps FC', '1.95', '3.55', '3.60', 'New GSP Stadium'),
        make_match('La Liga', 'España', 0, 18, 'Real Madrid', 'Barcelona', '2.05', '3.50', '3.15', 'Santiago Bernabéu'),
        make_match('La Liga', 'España', 1, 21, 'Atlético de Madrid', 'Valencia', '1.80', '3.45', '4.25', 'Wanda Metropolitano'),
        make_match('Premier League', 'Inglaterra', 0, 15, 'Manchester City', 'Arsenal', '2.30', '3.40', '2.75', 'Etihad Stadium'),
        make_match('Premier League', 'Inglaterra', 1, 17, 'Liverpool', 'Chelsea', '1.85', '3.60', '4.20', 'Anfield'),
        make_match('Serie A', 'Italia', -1, 18, 'Juventus', 'Inter', '2.65', '3.20', '2.55', 'Allianz Stadium'),
        make_match('MLS', 'Estados Unidos', 2, 22, 'Inter Miami', 'LA Galaxy', '1.90', '3.50', '3.25', 'Chase Stadium')
    ]
    return {
        'matches': fallback_matches,
        'players': [
            {'nombre': 'Jugador Ejemplo', 'nacionalidad': 'Colombia', 'posicion': 'Delantero', 'club': 'Club X', 'numero_camiseta': 9, 'altura': '1.80m', 'peso': '75kg', 'fecha_nacimiento': '1995-05-10', 'descripcion': 'Delantero de ejemplo', 'goles': 5, 'asistencias': 2, 'partidos_jugados': 10, 'velocidad': 85, 'resistencia': 80, 'defensa': 30, 'logros': 'Jugador destacado'}
        ]
    }


# Guarda en MySQL los jugadores y partidos recibidos desde la fuente externa.
def sync_external_to_db(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        ordered_matches = sorted(data.get('matches', []), key=lambda match: ((match.get('league_name') or '').lower(), str(match.get('kickoff') or '')))
        cursor.execute('DELETE FROM matches')
        for m in ordered_matches:
            kickoff = m.get('kickoff')
            try:
                kickoff_dt = datetime.fromisoformat(kickoff) if kickoff else None
            except Exception:
                kickoff_dt = None
            cursor.execute('''INSERT INTO matches (league_name, country, kickoff, home_team, away_team, home_odd, draw_odd, away_odd, stadium)
                             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''', (
                m.get('league_name'), m.get('country'), kickoff_dt, m.get('home_team'), m.get('away_team'), m.get('home_odd'), m.get('draw_odd'), m.get('away_odd'), m.get('stadium')
            ))

        # Sync players_external
        cursor.execute('DELETE FROM players_external')
        for p in data.get('players', []):
            fecha = p.get('fecha_nacimiento')
            try:
                fecha_dt = datetime.fromisoformat(fecha).date() if fecha else None
            except Exception:
                fecha_dt = None
            cursor.execute(
                '''INSERT INTO players_external (nombre,nacionalidad,posicion,club,numero_camiseta,altura,peso,fecha_nacimiento,descripcion,goles,asistencias,partidos_jugados,tarjetas_amarillas,tarjetas_rojas,velocidad,resistencia,defensa,logros)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    p.get('nombre'), p.get('nacionalidad'), p.get('posicion'), p.get('club'), p.get('numero_camiseta'), p.get('altura'), p.get('peso'), fecha_dt, p.get('descripcion'), p.get('goles') or 0, p.get('asistencias') or 0, p.get('partidos_jugados') or 0, p.get('tarjetas_amarillas') or 0, p.get('tarjetas_rojas') or 0, p.get('velocidad') or 0, p.get('resistencia') or 0, p.get('defensa') or 0, p.get('logros') or ''
                )
            )
        cursor.close()
        conn.close()
        print('Sync external data: OK')
    except Exception as e:
        print('Error syncing external data to DB:', e)


# Ejecuta periódicamente la sincronización externa en un hilo independiente.
def background_sync_loop(interval=86400):
    while True:
        try:
            data = fetch_external_data_example()
            sync_external_to_db(data)
        except BaseException as e:
            # Catch BaseException to log SystemExit/KeyboardInterrupt as well
            logger.exception('Background sync error (caught BaseException): %s', e)
        time.sleep(interval)


# Inicia el hilo encargado de actualizar los datos deportivos automáticamente.
def start_background_sync(interval=86400):
    t = threading.Thread(target=background_sync_loop, args=(interval,), daemon=True)
    t.start()


# Seed the matches table with the default multi-league sample data when the app boots.
sync_external_to_db(fetch_external_data_example())


# ============================================================================
# FUNCIONES UTILITARIAS DE LÍNEA DE COMANDOS
# ============================================================================

# Comprueba manualmente que las credenciales y el servidor MySQL funcionan.
def test_mysql_connection():
    """Verifica la conexión a MySQL"""
    print("\n" + "=" * 60)
    print("   VERIFICADOR DE CONEXIÓN MYSQL")
    print("=" * 60 + "\n")
    
    try:
        print("🔄 Verificando conexión con MySQL...")
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            use_unicode=True,
        )
        conn.close()
        print("✅ Servidor MySQL está en línea\n")
        
        # Probar conexión a BD específica
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Base de datos 'my_deport_' accesible")
            print(f"✅ Total de tablas: {len(tables)}\n")
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   ✓ {table[0]}: {count} registros")
            
            cursor.close()
            conn.close()
            print("\n✅ CONEXIÓN EXITOSA\n")
            return True
        except Exception as e:
            print(f"❌ Error al acceder a BD: {e}\n")
            return False
            
    except Exception as e:
        print(f"❌ No se puede conectar a MySQL: {e}")
        print("   Asegúrate de que MySQL está corriendo:\n")
        print("   Windows: net start MySQL80")
        print("   Linux: sudo service mysql start")
        print("   macOS: brew services start mysql\n")
        return False


# Permite inicializar manualmente la estructura y los datos de la base de datos.
def setup_database_manual():
    """Setup manual de la base de datos"""
    print("\n" + "=" * 60)
    print("   INICIALIZADOR DE BASE DE DATOS MYDEPORT")
    print("=" * 60 + "\n")
    
    if not test_mysql_connection():
        print("❌ No se puede conectar a MySQL")
        return False
    
    print("🔄 Inicializando base de datos...")
    try:
        init_db()
        print("\n✅ INICIALIZACIÓN COMPLETADA CON ÉXITO\n")
        print("📝 Próximos pasos:")
        print("   1. Ejecuta: python app.py")
        print("   2. Accede a: http://localhost:5000")
        print("   3. Credenciales admin: admin / admin123\n")
        return True
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}\n")
        return False


# Punto de entrada: procesa argumentos, sincroniza datos y arranca el servidor Flask.
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MyDeport - Aplicación de Fútbol')
    parser.add_argument('--setup', action='store_true', help='Inicializar la base de datos')
    parser.add_argument('--test-connection', action='store_true', help='Verificar conexión a MySQL')
    parser.add_argument('--port', type=int, default=5000, help='Puerto para ejecutar la app (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Ejecutar en modo debug')
    
    args = parser.parse_args()
    
    if args.test_connection:
        test_mysql_connection()
    elif args.setup:
        setup_database_manual()
    else:
        # Start background sync thread (interval seconds configurable via FOOTBALL_SYNC_INTERVAL env var)
        try:
            interval = int(os.environ.get('FOOTBALL_SYNC_INTERVAL', '86400'))
        except Exception:
            interval = 86400
        try:
            start_background_sync(interval=interval)
            debug_mode = args.debug or True  # Debug por defecto en desarrollo
            print(f"\n🚀 Iniciando MyDeport en http://localhost:{args.port}")
            print(f"   Modo debug: {'Activado' if debug_mode else 'Desactivado'}\n")
            app.run(debug=debug_mode, use_reloader=False, port=args.port)
        except KeyboardInterrupt:
            logger.info('Aplicación interrumpida por el usuario')
            print("\n\n✋ Aplicación cerrada correctamente.")
