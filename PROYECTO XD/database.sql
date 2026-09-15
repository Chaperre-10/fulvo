-- ============================================================================
-- MyDeport: esquema completo de producción
-- ============================================================================
-- Este archivo se ejecuta dentro de una base de datos MySQL ya seleccionada.
-- No borra bases ni tablas existentes, por lo que es seguro para importaciones.
--
-- Importación local:
--   CREATE DATABASE my_deport_ CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
--   mysql -u root -p my_deport_ < database.sql
--
-- Importación en PythonAnywhere:
--   mysql -u TU_USUARIO -h TU_USUARIO.mysql.pythonanywhere-services.com \
--     -p TU_USUARIO$my_deport_ < database.sql
-- ============================================================================

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- Usuarios, autenticación, roles y recuperación de contraseña.
CREATE TABLE IF NOT EXISTS users (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(100) NOT NULL,
	correo VARCHAR(255) NOT NULL,
	usuario VARCHAR(50) NOT NULL,
	password VARCHAR(255) NOT NULL,
	is_admin TINYINT(1) NOT NULL DEFAULT 0,
	reset_token VARCHAR(255) NULL,
	reset_token_expires DATETIME NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uq_users_correo (correo),
	UNIQUE KEY uq_users_usuario (usuario),
	KEY idx_users_admin (is_admin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Jugadores que se muestran en el catálogo y en las búsquedas.
CREATE TABLE IF NOT EXISTS players (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(100) NOT NULL,
	nacionalidad VARCHAR(100) NULL,
	posicion VARCHAR(100) NULL,
	club VARCHAR(100) NULL,
	numero_camiseta INT NULL,
	altura VARCHAR(20) NULL,
	peso VARCHAR(20) NULL,
	fecha_nacimiento DATE NULL,
	descripcion TEXT NULL,
	goles INT NOT NULL DEFAULT 0,
	asistencias INT NOT NULL DEFAULT 0,
	partidos_jugados INT NOT NULL DEFAULT 0,
	tarjetas_amarillas INT NOT NULL DEFAULT 0,
	tarjetas_rojas INT NOT NULL DEFAULT 0,
	velocidad INT NOT NULL DEFAULT 0,
	resistencia INT NOT NULL DEFAULT 0,
	defensa INT NOT NULL DEFAULT 0,
	logros TEXT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uq_players_nombre (nombre),
	KEY idx_players_club (club),
	KEY idx_players_nacionalidad (nacionalidad)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Copia de jugadores recibidos desde la fuente externa de datos deportivos.
CREATE TABLE IF NOT EXISTS players_external (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(200) NULL,
	nacionalidad VARCHAR(100) NULL,
	posicion VARCHAR(100) NULL,
	club VARCHAR(200) NULL,
	numero_camiseta INT NULL,
	altura VARCHAR(50) NULL,
	peso VARCHAR(50) NULL,
	fecha_nacimiento DATE NULL,
	descripcion TEXT NULL,
	goles INT NOT NULL DEFAULT 0,
	asistencias INT NOT NULL DEFAULT 0,
	partidos_jugados INT NOT NULL DEFAULT 0,
	tarjetas_amarillas INT NOT NULL DEFAULT 0,
	tarjetas_rojas INT NOT NULL DEFAULT 0,
	velocidad INT NOT NULL DEFAULT 0,
	resistencia INT NOT NULL DEFAULT 0,
	defensa INT NOT NULL DEFAULT 0,
	logros TEXT NULL,
	PRIMARY KEY (id),
	KEY idx_players_external_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Clubes disponibles para el catálogo y el buscador global.
CREATE TABLE IF NOT EXISTS clubs (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(100) NOT NULL,
	pais VARCHAR(100) NULL,
	ciudad VARCHAR(100) NULL,
	estadio VARCHAR(150) NULL,
	ano_fundacion SMALLINT NULL,
	descripcion TEXT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uq_clubs_nombre (nombre),
	KEY idx_clubs_pais (pais)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Torneos y competiciones disponibles para consulta.
CREATE TABLE IF NOT EXISTS tournaments (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(150) NOT NULL,
	tipo VARCHAR(80) NULL,
	pais_sede VARCHAR(150) NULL,
	ano SMALLINT NULL,
	ganador VARCHAR(150) NULL,
	descripcion TEXT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uq_tournaments_nombre (nombre),
	KEY idx_tournaments_ano (ano)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Partidos sincronizados, usados por la página de partidos y su API.
CREATE TABLE IF NOT EXISTS matches (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	league_name VARCHAR(200) NOT NULL,
	country VARCHAR(100) NULL,
	kickoff DATETIME NULL,
	home_team VARCHAR(200) NOT NULL,
	away_team VARCHAR(200) NOT NULL,
	home_odd VARCHAR(30) NULL,
	draw_odd VARCHAR(30) NULL,
	away_odd VARCHAR(30) NULL,
	stadium VARCHAR(200) NULL,
	home_badge VARCHAR(500) NULL,
	away_badge VARCHAR(500) NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	KEY idx_matches_kickoff (kickoff),
	KEY idx_matches_league (league_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Predicciones únicas por usuario y partido.
CREATE TABLE IF NOT EXISTS predictions (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	user_id INT UNSIGNED NOT NULL,
	league_name VARCHAR(200) NULL,
	home_team VARCHAR(200) NULL,
	away_team VARCHAR(200) NULL,
	kickoff DATETIME NULL,
	prediction VARCHAR(100) NOT NULL,
	match_key VARCHAR(255) NOT NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uq_predictions_user_match (user_id, match_key),
	KEY idx_predictions_created (created_at),
	CONSTRAINT fk_predictions_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Noticias publicadas por usuarios.
CREATE TABLE IF NOT EXISTS noticias (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	usuario_id INT UNSIGNED NOT NULL,
	titulo VARCHAR(255) NOT NULL,
	resumen TEXT NOT NULL,
	enlace VARCHAR(500) NULL,
	imagen VARCHAR(500) NULL,
	fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	fecha_modificacion DATETIME NULL,
	PRIMARY KEY (id),
	KEY idx_noticias_fecha (fecha_creacion),
	CONSTRAINT fk_noticias_usuario FOREIGN KEY (usuario_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Comentarios del foro de opiniones.
CREATE TABLE IF NOT EXISTS comentarios (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	usuario_id INT UNSIGNED NOT NULL,
	comentario TEXT NOT NULL,
	fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	fecha_modificacion DATETIME NULL,
	PRIMARY KEY (id),
	KEY idx_comentarios_fecha (fecha_creacion),
	CONSTRAINT fk_comentarios_usuario FOREIGN KEY (usuario_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Mensajes enviados desde la página de Contáctenos.
CREATE TABLE IF NOT EXISTS contact_messages (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(100) NOT NULL,
	correo VARCHAR(255) NOT NULL,
	asunto VARCHAR(255) NOT NULL,
	mensaje TEXT NOT NULL,
	estado ENUM('nuevo', 'leido', 'respondido') NOT NULL DEFAULT 'nuevo',
	usuario_id INT UNSIGNED NULL,
	fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	fecha_modificacion DATETIME NULL,
	PRIMARY KEY (id),
	KEY idx_contact_messages_fecha (fecha_creacion),
	KEY idx_contact_messages_estado (estado),
	CONSTRAINT fk_contact_messages_usuario FOREIGN KEY (usuario_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos iniciales del catálogo. INSERT IGNORE permite importar el archivo varias veces.
INSERT IGNORE INTO players
	(nombre, nacionalidad, posicion, club, numero_camiseta, altura, peso, fecha_nacimiento, descripcion, goles, asistencias, partidos_jugados, tarjetas_amarillas, tarjetas_rojas, velocidad, resistencia, defensa, logros)
VALUES
	('Vozinha (Josimar Évora Dias)', 'Cabo Verde', 'Arquero', 'Colo-Colo', 1, '1.85m', '82kg', '1990-07-22', 'Arquero caboverdiano destacado por su seguridad bajo los palos.', 0, 0, 371, 12, 0, 78, 85, 88, 'Referente de la selección de Cabo Verde'),
	('Cristiano Ronaldo', 'Portugal', 'Extremo/Delantero', 'Al Nassr', 7, '1.87m', '84kg', '1985-02-05', 'Leyenda del fútbol con cifras históricas en clubes y selecciones.', 923, 96, 1261, 162, 12, 94, 92, 35, 'Figura histórica del fútbol moderno'),
	('Kylian Mbappé', 'Francia', 'Delantero', 'Real Madrid', 9, '1.78m', '80kg', '1998-12-20', 'Estrella internacional con velocidad y gran capacidad goleadora.', 357, 116, 465, 48, 2, 97, 90, 40, 'Referente ofensivo de su generación');

INSERT IGNORE INTO clubs (nombre, pais, ciudad, estadio, ano_fundacion, descripcion)
VALUES
	('Real Madrid', 'España', 'Madrid', 'Santiago Bernabéu', 1902, 'Club histórico de LaLiga y competiciones europeas.'),
	('FC Barcelona', 'España', 'Barcelona', 'Camp Nou', 1899, 'Club español con una amplia trayectoria internacional.'),
	('Manchester United', 'Inglaterra', 'Manchester', 'Old Trafford', 1878, 'Club histórico de la Premier League.');

INSERT IGNORE INTO tournaments (nombre, tipo, pais_sede, ano, ganador, descripcion)
VALUES
	('Champions League 2025/2026', 'Clubes', 'Hungría (Budapest)', 2026, 'Paris Saint-Germain', 'Final disputada en Budapest.'),
	('La Liga 2025/2026', 'Liga', 'España', 2026, 'FC Barcelona', 'Temporada 2025/2026.'),
	('Mundial 2026', 'Internacional', 'Estados Unidos, México y Canadá', 2026, 'España', 'Copa del Mundo disputada en Norteamérica.');

-- Partidos de demostración para que la API tenga información antes de sincronizar.
INSERT INTO matches (league_name, country, kickoff, home_team, away_team, home_odd, draw_odd, away_odd, stadium)
SELECT 'La Liga', 'España', '2026-09-08 18:00:00', 'Real Madrid', 'Barcelona', '2.05', '3.50', '3.15', 'Santiago Bernabéu'
WHERE NOT EXISTS (
	SELECT 1 FROM matches WHERE league_name = 'La Liga' AND home_team = 'Real Madrid' AND away_team = 'Barcelona'
);

-- La aplicación crea automáticamente el administrador, noticias y comentarios
-- usando los valores configurados en app.py al iniciar por primera vez.
