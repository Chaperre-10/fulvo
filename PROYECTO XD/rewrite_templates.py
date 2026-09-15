# Genera o actualiza las plantillas HTML a partir de contenido definido en este archivo.
from pathlib import Path

# Diccionario con el contenido de cada plantilla que se escribirá en templates/.
content = {
    'admin.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Panel Admin{% endblock %}

{% block extra_head %}
    <style>
        body {
            background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("{{ url_for('static', filename='IMG/07.png') }}");
            background-size: cover;
            background-position: center;
            min-height: 100vh;
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
        }
        .page-content { padding: 40px 20px; }
        .table-dark { background: rgba(20,20,20,0.9); }
        .services-section { background: rgba(30,30,30,0.9); border: 1px solid #00ff88; border-radius: 12px; padding: 20px; margin-bottom: 30px; }
        .service-btn { width: 100%; text-align: left; padding: 12px; font-weight: 500; margin-bottom: 8px; }
    </style>
{% endblock %}

{% block content %}
<main class="page-content">
<div class="container">
    <h1 class="mb-4" style="color: #00ff88;">Panel de administración</h1>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} py-2">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <div class="services-section">
        <h5 style="color: #00ff88; margin-bottom: 15px;">Servicios disponibles</h5>
        <div class="row">
            <div class="col-md-6">
                <a href="{{ url_for('players') }}" class="btn btn-outline-success service-btn">👥 Ver jugadores</a>
                <a href="{{ url_for('clubs') }}" class="btn btn-outline-success service-btn">🏟️ Ver clubes</a>
            </div>
            <div class="col-md-6">
                <a href="{{ url_for('tournaments') }}" class="btn btn-outline-success service-btn">🏆 Ver torneos</a>
            </div>
        </div>
    </div>

    <h3 style="color: #00ff88; margin-top: 40px; margin-bottom: 20px;">Gestión de usuarios</h3>
    <table class="table table-dark table-striped align-middle">
        <thead>
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Correo</th>
                <th>Usuario</th>
                <th>Rol</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for user in users %}
            <tr>
                <td>{{ user.id }}</td>
                <td>{{ user.nombre }}</td>
                <td>{{ user.correo }}</td>
                <td>{{ user.usuario }}</td>
                <td>{% if user.is_admin %}Admin{% else %}Usuario{% endif %}</td>
                <td>
                    {% if not user.is_admin %}
                    <button class="btn btn-sm btn-outline-warning me-1" type="button" data-bs-toggle="modal" data-bs-target="#editUserModal" data-user-id="{{ user.id }}" data-user-name="{{ user.nombre }}" data-user-correo="{{ user.correo }}" data-user-usuario="{{ user.usuario }}">Editar</button>
                    <button class="btn btn-sm btn-outline-danger" type="button" data-bs-toggle="modal" data-bs-target="#confirmDeleteModal" data-user-id="{{ user.id }}" data-user-name="{{ user.nombre }}">Eliminar</button>
                    {% else %}
                    <span class="text-muted">No editable</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <a href="{{ url_for('profile') }}" class="btn btn-outline-light">Volver al perfil</a>
</div>
</main>
{% endblock %}

{% block extra_js %}
<script>
    document.addEventListener('DOMContentLoaded', function () {
        var confirmModal = document.getElementById('confirmDeleteModal');
        confirmModal.addEventListener('show.bs.modal', function (event) {
            var button = event.relatedTarget;
            var userId = button.getAttribute('data-user-id');
            var userName = button.getAttribute('data-user-name');
            var confirmText = document.getElementById('confirmDeleteText');
            confirmText.textContent = '¿Seguro que quieres eliminar a "' + userName + '"? Esta acción no se puede deshacer.';
            var form = document.getElementById('deleteForm');
            form.action = '/admin/delete/' + userId;
        });
        var editModal = document.getElementById('editUserModal');
        editModal.addEventListener('show.bs.modal', function (event) {
            var button = event.relatedTarget;
            var userId = button.getAttribute('data-user-id');
            var userName = button.getAttribute('data-user-name');
            var userCorreo = button.getAttribute('data-user-correo');
            var userUsuario = button.getAttribute('data-user-usuario');
            document.getElementById('edit_nombre').value = userName || '';
            document.getElementById('edit_correo').value = userCorreo || '';
            document.getElementById('edit_usuario').value = userUsuario || '';
            document.getElementById('edit_password').value = '';
            document.getElementById('edit_confirmar').value = '';
            var editForm = document.getElementById('editUserForm');
            editForm.action = '/admin/edit/' + userId;
        });
    });
</script>
{% endblock %}
''',
    'clubs.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Clubes{% endblock %}

{% block extra_head %}
    <style>
        body {
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("{{ url_for('static', filename='IMG/euro2024.jpg') }}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            min-height: 100vh;
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
        }
        .page-content { padding: 40px 20px; }
        @keyframes slideInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        h1 { color: #00ff88; text-align: center; margin-bottom: 50px; text-shadow: 0 0 20px rgba(0,255,136,0.5); font-weight: 700; font-size: 3em; animation: slideInUp 0.6s ease-out; }
        .club-card { background: linear-gradient(135deg, rgba(30,30,30,0.95), rgba(20,20,20,0.95)); border: 2px solid #ffa500; border-radius: 16px; padding: 25px; margin-bottom: 25px; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); animation: slideInUp 0.6s ease-out; animation-fill-mode: both; }
        .club-card:nth-child(1) { animation-delay: 0.1s; border-color: #ffa500; }
        .club-card:nth-child(2) { animation-delay: 0.2s; border-color: #ff8c00; }
        .club-card:nth-child(3) { animation-delay: 0.3s; border-color: #ff7f50; }
        .club-card:hover { transform: translateY(-10px) scale(1.02); box-shadow: 0 20px 50px rgba(255, 165, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.2); }
        .club-name { color: #ffa500; font-weight: bold; font-size: 1.8em; margin-bottom: 15px; text-shadow: 0 0 10px rgba(255, 165, 0, 0.5); }
        .club-info { font-size: 1em; margin: 8px 0; }
        .info-label { color: #ffa500; font-weight: 700; text-transform: uppercase; font-size: 0.85em; }
        .container { max-width: 1100px; }
    </style>
{% endblock %}

{% block content %}
<main class="page-content">
<div class="container">
    <h1>🏟️ Clubes</h1>
    {% if clubs %}
        {% for club in clubs %}
        <div class="club-card">
            <div class="club-name">{{ club.nombre }}</div>
            <div class="club-info"><span class="info-label">País:</span> {{ club.pais }}</div>
            <div class="club-info"><span class="info-label">Ciudad:</span> {{ club.ciudad }}</div>
            <div class="club-info"><span class="info-label">Estadio:</span> {{ club.estadio }}</div>
            <div class="club-info"><span class="info-label">Año de fundación:</span> {{ club.ano_fundacion }}</div>
            <div class="club-info" style="margin-top: 15px; color: #ddd;">{{ club.descripcion }}</div>
        </div>
        {% endfor %}
    {% else %}
        <div class="alert alert-info text-center">No hay clubes registrados.</div>
    {% endif %}
    <div style="margin-top: 30px;">
        <a href="{{ url_for('profile') }}" class="btn btn-outline-light">← Volver al perfil</a>
        <a href="{{ url_for('tournaments') }}" class="btn btn-outline-success">🏆 Ver torneos</a>
    </div>
</div>
</main>
{% endblock %}
''',
    'edit_profile.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Editar perfil{% endblock %}

{% block extra_head %}
    <style>
        body {
            background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("{{ url_for('static', filename='IMG/07.png') }}");
            background-size: cover;
            background-position: center;
            min-height: 100vh;
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
        }
        .page-content { padding: 40px 20px; }
        .card-box { background: rgba(20,20,20,0.9); border: 1px solid #00ff88; border-radius: 16px; padding: 30px; max-width: 700px; margin: auto; }
    </style>
{% endblock %}

{% block content %}
<main class="page-content">
<div class="card-box">
    <h1 class="mb-4" style="color: #00ff88;">Editar perfil</h1>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} py-2">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="POST" action="{{ url_for('edit_profile') }}">
        <div class="mb-3">
            <label class="form-label">Nombre</label>
            <input type="text" name="nombre" class="form-control" value="{{ user.nombre }}" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Correo</label>
            <input type="email" name="correo" class="form-control" value="{{ user.correo }}" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Usuario</label>
            <input type="text" name="usuario" class="form-control" value="{{ user.usuario }}" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Nueva contraseña (opcional)</label>
            <input type="password" name="password" class="form-control">
        </div>
        <div class="mb-3">
            <label class="form-label">Confirmar contraseña</label>
            <input type="password" name="confirmar" class="form-control">
        </div>
        <div class="mt-3">
            <a href="{{ url_for('profile') }}" class="btn btn-secondary">Cancelar</a>
            <button type="submit" class="btn btn-warning">Guardar cambios</button>
        </div>
    </form>
</div>
</main>
{% endblock %}
''',
    'news.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Foro de Noticias{% endblock %}

{% block extra_head %}
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
                        url("{{ url_for('static', filename='IMG/vozi.jpg') }}");
            background-size: cover;
            background-position: center;
            margin: 0;
        }
        .container-news { padding-top: 50px; text-align: center; }
        .title-neon { color: #00ff88; text-transform: uppercase; font-weight: 800; letter-spacing: 2px; }
        .carousel { border-radius: 20px; overflow: hidden; margin: 30px auto; box-shadow: 0 10px 40px rgba(0, 255, 136, 0.2); max-width: 900px; }
        .carousel-item img { height: 500px; object-fit: cover; filter: brightness(0.7); }
        .news-badge { background-color: #00ff88; color: #000; padding: 5px 15px; border-radius: 50px; font-weight: bold; font-size: 0.8rem; margin-bottom: 10px; display: inline-block; }
        .form-news { background: rgba(17, 17, 17, 0.9); padding: 20px; border-radius: 15px; border: 1px solid #00ff88; margin: 25px auto; max-width: 900px; text-align: left; }
        .news-card { background: rgba(17, 17, 17, 0.9); border: 1px solid #2c2c2c; border-radius: 12px; overflow: hidden; color: #fff; margin-bottom: 20px; }
        .news-card img { height: 320px; object-fit: cover; object-position: center center; width: 100%; display: block; }
    </style>
{% endblock %}

{% block content %}
<div class="container container-news">
    <span class="news-badge">Actualizado hace 5 minutos</span>
    <h1 class="title-neon">Foro de Noticias</h1>
    <h2 class="h5 text-secondary">Última hora del fútbol mundial</h2>

    <div id="carouselExample" class="carousel slide shadow-lg" data-bs-ride="carousel">
      <div class="carousel-inner">
        <div class="carousel-item active">
          <img src="{{ url_for('static', filename='IMG/luchoo.webp') }}" class="d-block w-100" alt="Noticia 1">
          <div class="carousel-caption d-none d-md-block">
            <h5 class="fw-bold">Partido hoy</h5>
            <p>La seleccón Colombia se mide ante Suiza</p>
          </div>
        </div>
        <div class="carousel-item">
          <img src="{{ url_for('static', filename='IMG/worldcup.jpg') }}" class="d-block w-100" alt="Noticia 2">
          <div class="carousel-caption d-none d-md-block">
            <h5 class="fw-bold">El mundial empieza!</h5>
            <p>Análisis previo a los partidos del torneo.</p>
          </div>
        </div>
        <div class="carousel-item">
          <img src="{{ url_for('static', filename='IMG/cr777') }}" class="d-block w-100" alt="Noticia 3">
          <div class="carousel-caption d-none d-md-block">
            <h5 class="fw-bold">Eliminado</h5>
            <p>El último baile del astro Portugues.</p>
          </div>
        </div>
      </div>
      <button class="carousel-control-prev" type="button" data-bs-target="#carouselExample" data-bs-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Anterior</span>
      </button>
      <button class="carousel-control-next" type="button" data-bs-target="#carouselExample" data-bs-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Siguiente</span>
      </button>
    </div>

    <div class="form-news">
        <h3 class="h5 mb-3" style="color: #00ff88;">Agregar una noticia</h3>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} py-2">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST" action="{{ url_for('news') }}">
            <div class="mb-3">
                <label class="form-label">Título</label>
                <input type="text" class="form-control" name="titulo" placeholder="Ej: Nuevo partido de la selección" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Resumen</label>
                <textarea class="form-control" name="resumen" rows="3" placeholder="Escribe un resumen breve de la noticia" required></textarea>
            </div>
            <div class="mb-3">
                <label class="form-label">Enlace (opcional)</label>
                <input type="url" class="form-control" name="enlace" placeholder="https://ejemplo.com">
            </div>
            <div class="mb-3">
                <label class="form-label">Imagen (opcional)</label>
                <input type="text" class="form-control" name="imagen" placeholder="Ej: IMG/01.jpg">
            </div>
            <button type="submit" class="btn btn-outline-success">Publicar noticia</button>
        </form>
    </div>

    <div class="mt-4">
        <h3 class="h5 mb-3" style="color: #00ff88;">Noticias agregadas</h3>
        {% for noticia in noticias %}
        <div class="news-card text-start">
            <img src="{{ url_for('static', filename=noticia.imagen) }}" alt="{{ noticia.titulo }}">
            <div class="p-3">
                <h4 class="h6 fw-bold">{{ noticia.titulo }}</h4>
                <p class="mb-2 text-secondary">{{ noticia.resumen }}</p>
                <a href="{{ noticia.enlace }}" target="_blank" class="btn btn-sm btn-outline-success">Leer más</a>
            </div>
        </div>
        {% endfor %}
    </div>

    <div class="mt-4">
        <a href="{{ url_for('index') }}" class="btn btn-outline-light btn-sm">Volver al inicio</a>
    </div>
</div>
{% endblock %}
''',
    'players.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Jugadores{% endblock %}

{% block extra_head %}
    <style>
        body {
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("{{ url_for('static', filename='IMG/euro2024.jpg') }}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            min-height: 100vh;
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
        }
        .page-content { padding: 40px 20px; }
        @keyframes slideInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        h1 { color: #00ff88; text-align: center; margin-bottom: 50px; text-shadow: 0 0 20px rgba(0,255,136,0.5); font-weight: 700; font-size: 3em; animation: slideInUp 0.6s ease-out; }
        .player-card { background: linear-gradient(135deg, rgba(30,30,30,0.95), rgba(20,20,20,0.95)); border: 2px solid #00ff88; border-radius: 16px; padding: 25px; margin-bottom: 25px; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); animation: slideInUp 0.6s ease-out; animation-fill-mode: both; }
        .player-card:nth-child(1) { animation-delay: 0.1s; }
        .player-card:nth-child(2) { animation-delay: 0.2s; }
        .player-card:nth-child(3) { animation-delay: 0.3s; }
        .player-card:hover { transform: translateY(-10px) scale(1.02); border-color: #00ff88; box-shadow: 0 20px 50px rgba(0,255,136,0.4), inset 0 1px 0 rgba(255,255,255,0.2); }
        .player-name { color: #00ff88; font-weight: bold; font-size: 1.8em; margin-bottom: 15px; text-shadow: 0 0 10px rgba(0,255,136,0.5); }
        .player-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid rgba(0,255,136,0.3); }
        .position-badge { background: linear-gradient(135deg, #00ff88, #00cc6f); color: #000; padding: 8px 16px; border-radius: 20px; font-weight: 600; font-size: 0.9em; }
        .player-info { font-size: 1em; margin: 8px 0; color: #ddd; }
        .info-label { color: #00ff88; font-weight: 700; text-transform: uppercase; font-size: 0.85em; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin: 20px 0; padding: 15px; background: rgba(0,255,136,0.05); border-radius: 12px; border-left: 4px solid #00ff88; }
        .stat-item { text-align: center; padding: 12px; background: rgba(20,20,20,0.6); border-radius: 8px; border: 1px solid rgba(0,255,136,0.2); }
        .stat-value { color: #00ff88; font-weight: 700; font-size: 1.5em; display: block; }
        .stat-label { color: #aaa; font-size: 0.75em; text-transform: uppercase; margin-top: 5px; }
        .logros-section { margin-top: 20px; padding: 15px; background: rgba(255, 215, 0, 0.05); border-left: 4px solid #ffd700; border-radius: 8px; }
        .logros-title { color: #ffd700; font-weight: 700; font-size: 1.1em; margin-bottom: 10px; }
        .logros-text { color: #ddd; font-size: 0.95em; line-height: 1.6; }
        .container { max-width: 1100px; }
        .btn-outline-light:hover { background-color: #00ff88; color: #000; border-color: #00ff88; }
    </style>
{% endblock %}

{% block content %}
<main class="page-content">
<div class="container">
    <h1>👥 Jugadores Elite</h1>
    {% if players %}
        {% for player in players %}
        <div class="player-card">
            <div class="player-header">
                <div class="player-name">{{ player.nombre }}</div>
                <div class="position-badge">{{ player.posicion }}</div>
            </div>
            <div class="player-info"><span class="info-label">🌍 Nacionalidad:</span> {{ player.nacionalidad }}</div>
            <div class="player-info"><span class="info-label">⚽ Club:</span> {{ player.club }}</div>
            <div class="player-info"><span class="info-label">📅 Nacimiento:</span> {{ player.fecha_nacimiento }}</div>
            <div class="player-info"><span class="info-label">👕 Camiseta:</span> #{{ player.numero_camiseta }} | <span class="info-label">📏 Altura:</span> {{ player.altura }} | <span class="info-label">⚖️ Peso:</span> {{ player.peso }}</div>
            <div class="player-info" style="margin-top: 15px; color: #ccc; font-style: italic;">{{ player.descripcion }}</div>
            <div class="stats-grid">
                <div class="stat-item"><span class="stat-value">{{ player.goles }}</span><span class="stat-label">Goles</span></div>
                <div class="stat-item"><span class="stat-value">{{ player.asistencias }}</span><span class="stat-label">Asistencias</span></div>
                <div class="stat-item"><span class="stat-value">{{ player.partidos_jugados }}</span><span class="stat-label">Partidos</span></div>
                <div class="stat-item"><span class="stat-value">{{ player.velocidad }}</span><span class="stat-label">Velocidad</span></div>
                <div class="stat-item"><span class="stat-value">{{ player.resistencia }}</span><span class="stat-label">Resistencia</span></div>
                <div class="stat-item"><span class="stat-value">{{ player.defensa }}</span><span class="stat-label">Defensa</span></div>
            </div>
            {% if player.logros %}
            <div class="logros-section">
                <div class="logros-title">🏆 Logros y Reconocimientos</div>
                <div class="logros-text">{{ player.logros }}</div>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    {% else %}
        <div class="alert alert-info text-center">No hay jugadores registrados.</div>
    {% endif %}
    <div style="margin-top: 40px; text-align: center;">
        <a href="{{ url_for('profile') }}" class="btn btn-outline-light me-2">← Volver al perfil</a>
        <a href="{{ url_for('clubs') }}" class="btn btn-outline-success">🏟️ Ver clubes</a>
    </div>
</div>
</main>
{% endblock %}
''',
    'profile.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Perfil{% endblock %}

{% block extra_head %}
    <style>
        body {
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("{{ url_for('static', filename='IMG/euro2024.jpg') }}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            min-height: 100vh;
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
        }
        .page-content { padding: 40px 20px; }
        @keyframes fadeInDown { from { opacity: 0; transform: translateY(-30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .card-box { background: linear-gradient(135deg, rgba(30,30,30,0.95), rgba(20,20,20,0.95)); border: 2px solid #00ff88; border-radius: 20px; padding: 40px; max-width: 700px; margin: auto; animation: fadeInDown 0.6s ease-out; box-shadow: 0 0 30px rgba(0,255,136,0.2), inset 0 1px 0 rgba(255,255,255,0.1); }
        h1 { color: #00ff88; text-shadow: 0 0 20px rgba(0,255,136,0.5); font-weight: 700; font-size: 2.5em; margin-bottom: 30px; }
        .profile-info { background: rgba(0,255,136,0.05); border-left: 4px solid #00ff88; padding: 20px; border-radius: 12px; margin-bottom: 25px; animation: slideInUp 0.6s ease-out 0.1s backwards; }
        .profile-info p { margin: 12px 0; font-size: 1.1em; }
        .profile-info strong { color: #00ff88; font-weight: 700; text-transform: uppercase; font-size: 0.85em; }
        .services-section { background: linear-gradient(135deg, rgba(0,255,136,0.05), rgba(0,200,100,0.05)); border: 2px solid #00ff88; border-radius: 16px; padding: 25px; margin-top: 35px; animation: slideInUp 0.6s ease-out 0.2s backwards; }
        .services-section h5 { color: #00ff88; font-weight: 700; text-transform: uppercase; font-size: 1.3em; margin-bottom: 20px; text-shadow: 0 0 10px rgba(0,255,136,0.3); }
        .service-btn { width: 100%; margin-bottom: 12px; text-align: left; padding: 15px; font-weight: 600; border: 2px solid #00ff88; color: #00ff88; background: transparent; border-radius: 10px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); font-size: 1.05em; }
        .service-btn:hover { background: linear-gradient(135deg, #00ff88, #00cc6f); color: #000; transform: translateX(10px); box-shadow: 0 10px 30px rgba(0,255,136,0.4); }
        .action-buttons { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 30px; animation: slideInUp 0.6s ease-out 0.3s backwards; }
        .action-buttons .btn { flex: 1; min-width: 140px; padding: 12px 20px; font-weight: 600; border-radius: 10px; transition: all 0.3s; text-transform: uppercase; font-size: 0.95em; }
        .btn-outline-light { border-color: #fff; color: #fff; }
        .btn-outline-light:hover { background-color: #fff; color: #000; }
        .btn-warning { background: linear-gradient(135deg, #ffc107, #ff9800); border: none; color: #fff; }
        .btn-warning:hover { background: linear-gradient(135deg, #ff9800, #f57c00); transform: translateY(-3px); box-shadow: 0 10px 30px rgba(255, 152, 0, 0.4); }
        .btn-outline-success { border-color: #00ff88; color: #00ff88; }
        .btn-outline-success:hover { background-color: #00ff88; color: #000; transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,255,136,0.4); }
    </style>
{% endblock %}

{% block content %}
<main class="page-content">
<div class="card-box">
    <h1 class="mb-4">Perfil de usuario</h1>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} py-2">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <div class="profile-info">
        <p><strong>👤 Nombre:</strong> {{ user.nombre }}</p>
        <p><strong>✉️ Correo:</strong> {{ user.correo }}</p>
        <p><strong>👥 Usuario:</strong> {{ user.usuario }}</p>
        <p><strong>🔐 Rol:</strong> {% if user.is_admin %}<span style="color: #ffc107;">Administrador</span>{% else %}Usuario{% endif %}</p>
    </div>
    <div class="services-section">
        <h5>⚽ Servicios disponibles</h5>
        <a href="{{ url_for('players') }}" class="btn btn-outline-success service-btn">👥 Ver jugadores</a>
        <a href="{{ url_for('clubs') }}" class="btn btn-outline-success service-btn">🏟️ Ver clubes</a>
        <a href="{{ url_for('tournaments') }}" class="btn btn-outline-success service-btn">🏆 Ver torneos</a>
    </div>
    <div class="action-buttons">
        <a href="{{ url_for('index') }}" class="btn btn-outline-light">🏠 Inicio</a>
        <a href="{{ url_for('edit_profile') }}" class="btn btn-warning">✏️ Editar</a>
        <a href="{{ url_for('logout') }}" class="btn btn-outline-success">🚪 Salir</a>
        {% if user.is_admin %}
        <a href="{{ url_for('admin') }}" class="btn btn-success">⚙️ Admin</a>
        {% endif %}
    </div>
</div>
</main>
{% endblock %}
''',
    'search_players.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Buscar Jugadores{% endblock %}

{% block extra_head %}
    <style>
        body {
            background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("{{ url_for('static', filename='IMG/07.png') }}");
            background-size: cover;
            background-position: center;
            min-height: 100vh;
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
        }
        .page-content { padding: 40px 20px; }
        .search-container { background: rgba(30,30,30,0.9); border: 2px solid #00ff88; border-radius: 12px; padding: 30px; margin-bottom: 30px; max-width: 600px; margin-left: auto; margin-right: auto; }
        .search-input { background: rgba(20,20,20,0.9); border: 1px solid #00ff88; color: #fff; padding: 12px; border-radius: 8px; }
        .search-btn { background: linear-gradient(135deg, #00ff88, #00cc6f); border: none; color: #000; font-weight: bold; padding: 12px 30px; border-radius: 8px; transition: transform 0.2s; }
        .search-btn:hover { transform: scale(1.05); background: linear-gradient(135deg, #00cc6f, #00ff88); color: #000; }
        .player-card { background: rgba(30,30,30,0.9); border: 2px solid #00ff88; border-radius: 12px; padding: 20px; margin-bottom: 20px; transition: transform 0.3s; }
        .player-card:hover { transform: translateY(-5px); border-color: #00ff88; box-shadow: 0 0 20px rgba(0,255,136,0.3); }
        .player-name { color: #00ff88; font-weight: bold; font-size: 1.3em; margin-bottom: 10px; }
        .player-info { font-size: 0.95em; margin: 5px 0; }
        .info-label { color: #00ff88; font-weight: 600; }
        .container { max-width: 1000px; }
        h1 { color: #00ff88; text-align: center; margin-bottom: 40px; text-shadow: 0 0 10px rgba(0,255,136,0.5); }
        .popular-searches { background: rgba(30,30,30,0.9); border: 1px solid #00ff88; border-radius: 8px; padding: 15px; margin-top: 20px; text-align: center; }
        .popular-searches h6 { color: #00ff88; margin-bottom: 10px; }
        .search-tag { display: inline-block; background: rgba(0,255,136,0.2); border: 1px solid #00ff88; color: #00ff88; padding: 5px 12px; border-radius: 20px; margin: 5px; cursor: pointer; font-size: 0.9em; transition: all 0.2s; }
        .search-tag:hover { background: rgba(0,255,136,0.4); text-decoration: none; color: #00ff88; }
    </style>
{% endblock %}

{% block content %}
<main class="page-content">
<div class="container">
    <h1>🔍 Buscar Jugadores</h1>
    <div class="search-container">
        <form method="POST" action="{{ url_for('search_players') }}">
            <div class="input-group mb-3">
                <input type="text" name="search_query" class="form-control search-input" placeholder="Busca un jugador por nombre..." value="{{ search_query }}" required>
                <button class="btn search-btn" type="submit">Buscar</button>
            </div>
        </form>
        <div class="popular-searches">
            <h6>Jugadores populares:</h6>
            <form method="POST" action="{{ url_for('search_players') }}" style="display: inline;"><input type="hidden" name="search_query" value="Cristiano Ronaldo"><button type="submit" class="search-tag">Cristiano Ronaldo</button></form>
            <form method="POST" action="{{ url_for('search_players') }}" style="display: inline;"><input type="hidden" name="search_query" value="Kylian Mbappé"><button type="submit" class="search-tag">Kylian Mbappé</button></form>
            <form method="POST" action="{{ url_for('search_players') }}" style="display: inline;"><input type="hidden" name="search_query" value="Voz Inha"><button type="submit" class="search-tag">Voz Inha</button></form>
        </div>
    </div>
    {% if search_query %}
        {% if players %}
            <h3 style="color: #00ff88; margin: 30px 0 20px 0;">Resultados para: "{{ search_query }}"</h3>
            {% for player in players %}
            <div class="player-card">
                <div class="player-name">{{ player.nombre }}</div>
                <div class="player-info"><span class="info-label">Nacionalidad:</span> {{ player.nacionalidad }}</div>
                <div class="player-info"><span class="info-label">Posición:</span> {{ player.posicion }}</div>
                <div class="player-info"><span class="info-label">Club:</span> {{ player.club }}</div>
                <div class="player-info"><span class="info-label">Número de camiseta:</span> {{ player.numero_camiseta }}</div>
                <div class="player-info"><span class="info-label">Altura:</span> {{ player.altura }}</div>
                <div class="player-info"><span class="info-label">Peso:</span> {{ player.peso }}</div>
                <div class="player-info" style="margin-top: 15px; color: #ddd;">{{ player.descripcion }}</div>
            </div>
            {% endfor %}
        {% endif %}
    {% else %}
        <div class="alert alert-info text-center" style="margin-top: 30px;">💡 Usa la barra de búsqueda arriba para buscar jugadores, o haz clic en uno de los nombres populares.</div>
    {% endif %}
    <div style="margin-top: 30px;">
        <a href="{{ url_for('profile') }}" class="btn btn-outline-light">← Volver al perfil</a>
        <a href="{{ url_for('players') }}" class="btn btn-outline-success">👥 Ver todos los jugadores</a>
    </div>
</div>
</main>
{% endblock %}
''',
    'search_results.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Resultados de Búsqueda{% endblock %}

{% block extra_head %}
    <style>
        body {
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("{{ url_for('static', filename='IMG/euro2024.jpg') }}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            min-height: 100vh;
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
        }
        .page-content { padding: 40px 20px; }
        .container { max-width: 1000px; }
        h1 { color: #00ff88; text-align: center; margin-bottom: 10px; text-shadow: 0 0 10px rgba(0,255,136,0.5); }
        .search-term { text-align: center; color: #aaa; margin-bottom: 40px; font-size: 1.1em; }
        .result-category { color: #00ff88; font-weight: bold; font-size: 1.2em; margin-top: 30px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #00ff88; }
        .result-card { background: rgba(30,30,30,0.9); border: 2px solid #00ff88; border-radius: 12px; padding: 20px; margin-bottom: 15px; transition: transform 0.3s; }
        .result-card:hover { transform: translateY(-5px); box-shadow: 0 0 20px rgba(0,255,136,0.3); }
        .result-title { color: #00ff88; font-weight: bold; font-size: 1.2em; margin-bottom: 10px; }
        .result-info { font-size: 0.95em; margin: 5px 0; color: #ddd; }
        .info-label { color: #00ff88; font-weight: 600; }
        .player-badge { display: inline-block; background: rgba(0,100,255,0.3); border: 1px solid #0064ff; color: #00a8ff; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 10px; }
        .club-badge { display: inline-block; background: rgba(255,165,0,0.3); border: 1px solid #ffa500; color: #ffb84d; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 10px; }
        .tournament-badge { display: inline-block; background: rgba(255,215,0,0.3); border: 1px solid #ffd700; color: #ffeb3b; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 10px; }
        .no-results { background: rgba(30,30,30,0.9); border: 1px solid #ff6b6b; border-radius: 12px; padding: 30px; text-align: center; margin-top: 30px; }
    </style>
{% endblock %}

{% block content %}
<main class="page-content">
<div class="container">
    <h1>🔍 Resultados de Búsqueda</h1>
    <div class="search-term">Búsqueda: <strong>"{{ query }}"</strong></div>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} py-2">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    {% set players = results | selectattr('type', 'equalto', 'player') | list %}
    {% set clubs_list = results | selectattr('type', 'equalto', 'club') | list %}
    {% set tournaments_list = results | selectattr('type', 'equalto', 'tournament') | list %}
    {% if results %}
        {% if players %}
            <div class="result-category">👥 Jugadores ({{ players | length }})</div>
            {% for player in players %}
            <div class="result-card">
                <div>
                    <span class="player-badge">JUGADOR</span>
                    <span class="result-title">{{ player.nombre }}</span>
                </div>
                <div class="result-info"><span class="info-label">Nacionalidad:</span> {{ player.nacionalidad }}</div>
                <div class="result-info"><span class="info-label">Posición:</span> {{ player.posicion }}</div>
                <div class="result-info"><span class="info-label">Club:</span> {{ player.club }}</div>
            </div>
            {% endfor %}
        {% endif %}
        {% if clubs_list %}
            <div class="result-category">🏟️ Clubes ({{ clubs_list | length }})</div>
            {% for club in clubs_list %}
            <div class="result-card">
                <div>
                    <span class="club-badge">CLUB</span>
                    <span class="result-title">{{ club.nombre }}</span>
                </div>
                <div class="result-info"><span class="info-label">País:</span> {{ club.pais }}</div>
                <div class="result-info"><span class="info-label">Ciudad:</span> {{ club.ciudad }}</div>
                <div class="result-info"><span class="info-label">Estadio:</span> {{ club.estadio }}</div>
            </div>
            {% endfor %}
        {% endif %}
        {% if tournaments_list %}
            <div class="result-category">🏆 Torneos ({{ tournaments_list | length }})</div>
            {% for tournament in tournaments_list %}
            <div class="result-card">
                <div>
                    <span class="tournament-badge">TORNEO</span>
                    <span class="result-title">{{ tournament.nombre }}</span>
                </div>
                <div class="result-info"><span class="info-label">Año:</span> {{ tournament.ano }}</div>
                <div class="result-info"><span class="info-label">País sede:</span> {{ tournament.pais_sede }}</div>
                <div class="result-info"><span class="info-label">Ganador:</span> {{ tournament.ganador }}</div>
            </div>
            {% endfor %}
        {% endif %}
    {% else %}
        <div class="no-results">
            <h4 style="color: #ff6b6b; margin-bottom: 15px;">❌ Sin resultados</h4>
            <p>No se encontraron jugadores, clubes o torneos que coincidan con "<strong>{{ query }}</strong>"</p>
            <p style="color: #888; font-size: 0.9em; margin-top: 15px;">Intenta con otro término de búsqueda</p>
        </div>
    {% endif %}
    <div style="margin-top: 40px;">
        <a href="{{ url_for('profile') }}" class="btn btn-outline-light">← Volver al perfil</a>
        <a href="{{ url_for('index') }}" class="btn btn-outline-success">🏠 Ir al inicio</a>
    </div>
</div>
</main>
{% endblock %}
''',
    'tournaments.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Torneos{% endblock %}

{% block extra_head %}
    <style>
        body {
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("{{ url_for('static', filename='IMG/euro2024.jpg') }}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            min-height: 100vh;
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
        }
        .page-content { padding: 40px 20px; }
        @keyframes slideInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        h1 { color: #ffd700; text-align: center; margin-bottom: 50px; text-shadow: 0 0 20px rgba(255, 215, 0, 0.6); font-weight: 700; font-size: 3em; animation: slideInUp 0.6s ease-out; }
        .tournament-card { background: linear-gradient(135deg, rgba(30,30,30,0.95), rgba(20,20,20,0.95)); border: 2px solid #ffd700; border-radius: 16px; padding: 25px; margin-bottom: 25px; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); animation: slideInUp 0.6s ease-out; animation-fill-mode: both; position: relative; overflow: hidden; }
        .tournament-card::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.1), transparent); transition: left 0.5s; }
        .tournament-card:hover::before { left: 100%; }
        .tournament-card:nth-child(1) { animation-delay: 0.1s; }
        .tournament-card:nth-child(2) { animation-delay: 0.2s; }
        .tournament-card:nth-child(3) { animation-delay: 0.3s; }
        .tournament-card:hover { transform: translateY(-10px) scale(1.02); box-shadow: 0 20px 50px rgba(255, 215, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.2); }
        .tournament-name { color: #ffd700; font-weight: bold; font-size: 1.8em; margin-bottom: 15px; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }
        .tournament-info { font-size: 1em; margin: 8px 0; }
        .info-label { color: #ffd700; font-weight: 700; text-transform: uppercase; font-size: 0.85em; }
        .winner-badge { background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; padding: 8px 16px; border-radius: 20px; font-weight: bold; display: inline-block; margin-top: 10px; animation: pulse 2s infinite; }
        .container { max-width: 1100px; }
    </style>
{% endblock %}

{% block content %}
<main class="page-content">
<div class="container">
    <h1>🏆 Torneos</h1>
    {% if tournaments %}
        {% for tournament in tournaments %}
        <div class="tournament-card">
            <div class="tournament-name">{{ tournament.nombre }}</div>
            <div class="tournament-info"><span class="info-label">Tipo:</span> {{ tournament.tipo }}</div>
            <div class="tournament-info"><span class="info-label">País sede:</span> {{ tournament.pais_sede }}</div>
            <div class="tournament-info"><span class="info-label">Año:</span> {{ tournament.ano }}</div>
            <div class="tournament-info"><span class="info-label">Ganador:</span> <span class="winner-badge">{{ tournament.ganador }}</span></div>
            <div class="tournament-info" style="margin-top: 15px; color: #ddd;">{{ tournament.descripcion }}</div>
        </div>
        {% endfor %}
    {% else %}
        <div class="alert alert-info text-center">No hay torneos registrados.</div>
    {% endif %}
    <div style="margin-top: 30px;">
        <a href="{{ url_for('profile') }}" class="btn btn-outline-light">← Volver al perfil</a>
        <a href="{{ url_for('clubs') }}" class="btn btn-outline-success">🏟️ Ver clubes</a>
    </div>
</div>
</main>
{% endblock %}
''',
    'user.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Usuarios{% endblock %}

{% block extra_head %}
    <style>
        body {
            background-color: #0d1117;
            color: white;
            font-family: Arial, sans-serif;
            margin: 0;
        }
        .page-content { padding: 30px; }
        h1 { text-align: center; color: #00aaff; margin-bottom: 30px; text-shadow: 0 0 10px #00aaff; }
        .users-table { width: 100%; max-width: 1100px; margin: auto; border-collapse: collapse; background-color: #161b22; box-shadow: 0 0 15px rgba(0, 170, 255, 0.4); border-radius: 10px; overflow: hidden; }
        .users-table th { background-color: #0077cc; color: white; padding: 15px; text-align: center; font-size: 18px; }
        .users-table td { padding: 12px; text-align: center; border-bottom: 1px solid #30363d; }
        .users-table tr:hover { background-color: #1f2937; }
        .btn-action, .btn-delete { background-color: #00aaff; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        .btn-action:hover, .btn-delete:hover { background-color: #0077cc; transform: scale(1.05); }
        .btn-delete { background-color: #ff3333; }
        .btn-delete:hover { background-color: #cc0000; }
        .container { width: 95%; margin: auto; }
        @media (max-width: 768px) { .users-table { width: 100%; font-size: 14px; } h1 { font-size: 28px; } }
    </style>
{% endblock %}

{% block content %}
<main class="page-content">
    <div class="container">
        <h1>Usuarios Registrados</h1>
        <table class="users-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Email</th>
                    <th>Usuario</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for usuario in usuarios %}
                <tr>
                    <td>{{ usuario.id }}</td>
                    <td>{{ usuario.nombre }}</td>
                    <td>{{ usuario.correo }}</td>
                    <td>{{ usuario.usuario }}</td>
                    <td>
                        <form action="{{ url_for('actualizar_usuario', id=usuario.id) }}" method="get" style="display:inline;">
                            <button type="submit" class="btn-action">Actualizar</button>
                        </form>
                        <form action="{{ url_for('eliminar_usuario', id=usuario.id) }}" method="post" style="display:inline;">
                            <button type="submit" class="btn-delete" onclick="return confirm('Estas seguro que quieres eliminar este usuario?');">Eliminar</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</main>
{% endblock %}
''',
    'actuser.html': '''{% extends "base.html" %}

{% block title %}MyDeport | Actualizar Usuario{% endblock %}

{% block extra_head %}
    <style>
        body { margin: 0; background-color: #0d1117; color: white; font-family: Arial, sans-serif; }
        .page-content { padding: 40px 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; color: #00aaff; margin-bottom: 30px; text-shadow: 0 0 10px #00aaff; }
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; margin-bottom: 8px; color: #00aaff; }
        .form-control { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #00aaff; background: #161b22; color: white; }
        .btn { background-color: #00aaff; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; }
        .btn:hover { background-color: #0077cc; }
        .button-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px; }
        .button-row .btn-secondary { background-color: #555; }
    </style>
{% endblock %}

{% block content %}
<main class="page-content">
    <div class="container">
        <h1>Actualizar Usuario</h1>
        <form action="{{ url_for('newuser', id=id) }}" method="post">
            <div class="form-group">
                <label for="nuevo_nombre" class="form-label">Nuevo nombre:</label>
                <input type="text" id="nuevo_nombre" name="nuevo_nombre" value="{{ nombre }}" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="nuevo_email" class="form-label">Nuevo Email:</label>
                <input type="email" id="nuevo_email" name="nuevo_email" value="{{ email }}" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="nuevo_contraseña" class="form-label">Nueva Contraseña:</label>
                <input type="password" id="nuevo_contraseña" name="nuevo_contraseña" class="form-control" required>
            </div>
            <div class="button-row">
                <button type="submit" class="btn">Actualizar</button>
                <a href="{{ url_for('newuser', id=id) }}" class="btn btn-secondary" style="display: inline-flex; align-items: center; justify-content: center;">Volver</a>
            </div>
        </form>
    </div>
</main>
{% endblock %}
''',
}

base = Path('templates')
for filename, text in content.items():
    path = base / filename
    path.write_text(text, encoding='utf-8')
    print(f'Updated {path}')
