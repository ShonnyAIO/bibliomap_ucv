import os
import duckdb
from datetime import datetime
import json
from typing import Optional

DB_PATH = "data/processed/bibliomap.db"

def get_connection():
    """Returns a connection to the persistent DuckDB database."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return duckdb.connect(DB_PATH)

def initialize_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_connection()
    try:
        # Create sequences for auto-increment IDs
        conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_usuarios_id START 1;")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_intereses_id START 1;")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_preferencias_id START 1;")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_historial_id START 1;")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_cola_id START 1;")

        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_usuarios_id'),
                nombre VARCHAR,
                email VARCHAR UNIQUE,
                telefono VARCHAR,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS intereses (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_intereses_id'),
                usuario_id INTEGER,
                palabra_clave VARCHAR,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS preferencias_canal (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_preferencias_id'),
                usuario_id INTEGER,
                canal VARCHAR, -- 'SMTP', 'TELEGRAM', 'WHATSAPP'
                activo BOOLEAN DEFAULT FALSE,
                configuracion_adicional VARCHAR, -- JSON string (e.g. {"chat_id": "1234"})
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS historial_notificaciones (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_historial_id'),
                usuario_id INTEGER,
                titulo_articulo VARCHAR,
                canal_enviado VARCHAR,
                enviado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado VARCHAR, -- 'EXITOSO', 'FALLIDO'
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS cola_notificaciones (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_cola_id'),
                usuario_id INTEGER,
                titulo_articulo VARCHAR,
                mensaje VARCHAR,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                enviado BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        """)
        
        # Check if we need to insert a default demo user if the table is empty
        res = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()
        if res and res[0] == 0:
            # Insert a demo user
            conn.execute("""
                INSERT INTO usuarios (nombre, email, telefono)
                VALUES ('Usuario Demo', 'demo@bibliomap.ucv.ve', '+584120000000');
            """)
            user_id = conn.execute("SELECT currval('seq_usuarios_id')").fetchone()[0]
            
            # Default preferences
            conn.execute(f"INSERT INTO preferencias_canal (usuario_id, canal, activo, configuracion_adicional) VALUES ({user_id}, 'SMTP', false, '{{}}');")
            conn.execute(f"INSERT INTO preferencias_canal (usuario_id, canal, activo, configuracion_adicional) VALUES ({user_id}, 'TELEGRAM', false, '{{\"chat_id\": \"\"}}');")
            conn.execute(f"INSERT INTO preferencias_canal (usuario_id, canal, activo, configuracion_adicional) VALUES ({user_id}, 'WHATSAPP', false, '{{}}');")
            
            # Default interests
            conn.execute(f"INSERT INTO intereses (usuario_id, palabra_clave) VALUES ({user_id}, 'inteligencia artificial');")
            conn.execute(f"INSERT INTO intereses (usuario_id, palabra_clave) VALUES ({user_id}, 'bibliometria');")
            
        conn.commit()
    finally:
        conn.close()

def create_user(nombre: str, email: str, telefono: str):
    """Creates a new user and sets up default preferences."""
    conn = get_connection()
    try:
        # Check if email exists
        exists = conn.execute("SELECT id FROM usuarios WHERE email = ?", [email]).fetchone()
        if exists:
            return exists[0]
            
        conn.execute("""
            INSERT INTO usuarios (nombre, email, telefono)
            VALUES (?, ?, ?);
        """, [nombre, email, telefono])
        user_id = conn.execute("SELECT currval('seq_usuarios_id')").fetchone()[0]

        # Create default preferences
        conn.execute("INSERT INTO preferencias_canal (usuario_id, canal, activo, configuracion_adicional) VALUES (?, 'SMTP', false, '{}')", [user_id])
        conn.execute("INSERT INTO preferencias_canal (usuario_id, canal, activo, configuracion_adicional) VALUES (?, 'TELEGRAM', false, '{\"chat_id\": \"\"}')", [user_id])
        conn.execute("INSERT INTO preferencias_canal (usuario_id, canal, activo, configuracion_adicional) VALUES (?, 'WHATSAPP', false, '{}')", [user_id])
        
        conn.commit()
        return user_id
    finally:
        conn.close()

def get_users():
    """Returns a list of all users as dicts."""
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT id, nombre, email, telefono, creado_en FROM usuarios ORDER BY nombre ASC")
        rows = cursor.fetchall()
        return [
            {
                "id": r[0],
                "nombre": r[1],
                "email": r[2],
                "telefono": r[3],
                "creado_en": r[4]
            }
            for r in rows
        ]
    finally:
        conn.close()

def get_user_by_id(user_id: int):
    """Returns a user by ID."""
    conn = get_connection()
    try:
        r = conn.execute("SELECT id, nombre, email, telefono, creado_en FROM usuarios WHERE id = ?", [user_id]).fetchone()
        if r:
            return {
                "id": r[0],
                "nombre": r[1],
                "email": r[2],
                "telefono": r[3],
                "creado_en": r[4]
            }
        return None
    finally:
        conn.close()

def update_user(user_id: int, nombre: str, email: str, telefono: str):
    """Updates user information."""
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE usuarios
            SET nombre = ?, email = ?, telefono = ?
            WHERE id = ?;
        """, [nombre, email, telefono, user_id])
        conn.commit()
    finally:
        conn.close()

def delete_user(user_id: int):
    """Deletes a user and all cascade relationships."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM intereses WHERE usuario_id = ?", [user_id])
        conn.execute("DELETE FROM preferencias_canal WHERE usuario_id = ?", [user_id])
        conn.execute("DELETE FROM historial_notificaciones WHERE usuario_id = ?", [user_id])
        conn.execute("DELETE FROM cola_notificaciones WHERE usuario_id = ?", [user_id])
        conn.execute("DELETE FROM usuarios WHERE id = ?", [user_id])
        conn.commit()
    finally:
        conn.close()

def get_user_interests(user_id: int):
    """Returns a list of keywords for a user."""
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT palabra_clave FROM intereses WHERE usuario_id = ? ORDER BY creado_en DESC", [user_id])
        return [r[0] for r in cursor.fetchall()]
    finally:
        conn.close()

def add_user_interest(user_id: int, palabra_clave: str):
    """Adds a new interest keyword for a user if it doesn't already exist."""
    conn = get_connection()
    try:
        palabra = palabra_clave.strip().lower()
        exists = conn.execute("SELECT id FROM intereses WHERE usuario_id = ? AND LOWER(palabra_clave) = ?", [user_id, palabra]).fetchone()
        if not exists and palabra:
            conn.execute("INSERT INTO intereses (usuario_id, palabra_clave) VALUES (?, ?)", [user_id, palabra_clave.strip()])
            conn.commit()
            return True
        return False
    finally:
        conn.close()

def remove_user_interest(user_id: int, palabra_clave: str):
    """Removes an interest keyword for a user."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM intereses WHERE usuario_id = ? AND LOWER(palabra_clave) = ?", [user_id, palabra_clave.strip().lower()])
        conn.commit()
    finally:
        conn.close()

def get_user_preferences(user_id: int):
    """Returns a dictionary of channel preferences for a user."""
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT canal, activo, configuracion_adicional FROM preferencias_canal WHERE usuario_id = ?", [user_id])
        rows = cursor.fetchall()
        prefs = {}
        for r in rows:
            canal = r[0]
            activo = r[1]
            try:
                config = json.loads(r[2]) if r[2] else {}
            except Exception:
                config = {}
            prefs[canal] = {
                "activo": activo,
                "config": config
            }
        return prefs
    finally:
        conn.close()

def update_user_preference(user_id: int, canal: str, activo: bool, configuracion_adicional: dict):
    """Updates preferences for a specific channel of a user."""
    conn = get_connection()
    try:
        config_str = json.dumps(configuracion_adicional)
        # Check if preference exists
        exists = conn.execute("SELECT id FROM preferencias_canal WHERE usuario_id = ? AND canal = ?", [user_id, canal]).fetchone()
        if exists:
            conn.execute("""
                UPDATE preferencias_canal
                SET activo = ?, configuracion_adicional = ?
                WHERE usuario_id = ? AND canal = ?;
            """, [activo, config_str, user_id, canal])
        else:
            conn.execute("""
                INSERT INTO preferencias_canal (usuario_id, canal, activo, configuracion_adicional)
                VALUES (?, ?, ?, ?);
            """, [user_id, canal, activo, config_str])
        conn.commit()
    finally:
        conn.close()

def add_notification_history(user_id: int, titulo_articulo: str, canal_enviado: str, estado: str):
    """Logs a sent notification in the history."""
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO historial_notificaciones (usuario_id, titulo_articulo, canal_enviado, estado)
            VALUES (?, ?, ?, ?);
        """, [user_id, titulo_articulo, canal_enviado, estado])
        conn.commit()
    finally:
        conn.close()

def get_notification_history(user_id: Optional[int] = None):
    """Returns the notification history, optionally filtered by user."""
    conn = get_connection()
    try:
        if user_id is not None:
            cursor = conn.execute("""
                SELECT h.id, u.nombre, h.titulo_articulo, h.canal_enviado, h.enviado_en, h.estado
                FROM historial_notificaciones h
                JOIN usuarios u ON h.usuario_id = u.id
                WHERE h.usuario_id = ?
                ORDER BY h.enviado_en DESC
                LIMIT 50
            """, [user_id])
        else:
            cursor = conn.execute("""
                SELECT h.id, u.nombre, h.titulo_articulo, h.canal_enviado, h.enviado_en, h.estado
                FROM historial_notificaciones h
                JOIN usuarios u ON h.usuario_id = u.id
                ORDER BY h.enviado_en DESC
                LIMIT 50
            """)
        rows = cursor.fetchall()
        return [
            {
                "id": r[0],
                "usuario": r[1],
                "titulo_articulo": r[2],
                "canal": r[3],
                "enviado_en": r[4],
                "estado": r[5]
            }
            for r in rows
        ]
    finally:
        conn.close()

def get_last_whatsapp_sent_time(telefono: str) -> Optional[datetime]:
    """Returns the timestamp of the last WhatsApp notification sent to a specific user's telephone number."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT h.enviado_en 
            FROM historial_notificaciones h
            JOIN usuarios u ON h.usuario_id = u.id
            WHERE u.telefono = ? AND h.canal_enviado = 'WHATSAPP' AND h.estado = 'EXITOSO'
            ORDER BY h.enviado_en DESC
            LIMIT 1
        """, [telefono])
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()

def queue_notification(user_id: int, titulo_articulo: str, mensaje: str):
    """Queues a notification for background sending."""
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO cola_notificaciones (usuario_id, titulo_articulo, mensaje, enviado)
            VALUES (?, ?, ?, false);
        """, [user_id, titulo_articulo, mensaje])
        conn.commit()
    finally:
        conn.close()

def get_pending_notifications():
    """Returns a list of queued, unsent notifications."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT id, usuario_id, titulo_articulo, mensaje, creado_en
            FROM cola_notificaciones
            WHERE enviado = false
            ORDER BY creado_en ASC
        """)
        rows = cursor.fetchall()
        return [
            {
                "id": r[0],
                "usuario_id": r[1],
                "titulo_articulo": r[2],
                "mensaje": r[3],
                "creado_en": r[4]
            }
            for r in rows
        ]
    finally:
        conn.close()

def mark_notification_sent(cola_id: int):
    """Marks a queued notification as sent."""
    conn = get_connection()
    try:
        conn.execute("UPDATE cola_notificaciones SET enviado = true WHERE id = ?", [cola_id])
        conn.commit()
    finally:
        conn.close()

def has_user_been_notified(user_id: int, title: str) -> bool:
    """Checks if a user has already been notified about a specific article title."""
    conn = get_connection()
    try:
        r = conn.execute("SELECT id FROM historial_notificaciones WHERE usuario_id = ? AND titulo_articulo = ?", [user_id, title]).fetchone()
        return r is not None
    finally:
        conn.close()
