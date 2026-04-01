"""
estudiantes.py — Puente Lógico SAS BIC
=======================================
Capa de persistencia: almacena estudiantes, sesiones y respuestas
en una base de datos SQLite local (un solo archivo .db).

Por qué SQLite y no un servidor:
  - No requiere infraestructura externa para el MVP.
  - El archivo puente_logico.db se puede mover o respaldar fácilmente.
  - Soporta múltiples lecturas concurrentes sin configuración.

Tablas:
  estudiantes   — perfil de cada estudiante
  sesiones      — cada vez que un estudiante entra al juego
  respuestas    — cada pregunta respondida (o saltada) en una sesión
"""

import sqlite3
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE LA BASE DE DATOS
# ---------------------------------------------------------------------------

# El archivo .db se guarda en la misma carpeta que este módulo
DB_PATH = os.path.join(os.path.dirname(__file__), "puente_logico.db")


def _conectar() -> sqlite3.Connection:
    """Abre (o crea) la conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # Permite acceder a columnas por nombre
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_db():
    """
    Crea las tablas si no existen.
    Se llama una vez al iniciar la aplicación (idempotente).
    """
    with _conectar() as conn:
        conn.executescript("""
        -- Tabla de estudiantes
        CREATE TABLE IF NOT EXISTS estudiantes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT    NOT NULL,
            grado       INTEGER NOT NULL,
            creado_en   TEXT    NOT NULL DEFAULT (datetime('now')),
            ultima_vez  TEXT
        );

        -- Tabla de sesiones (una sesión = una vez que el estudiante juega)
        CREATE TABLE IF NOT EXISTS sesiones (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id   INTEGER NOT NULL REFERENCES estudiantes(id),
            iniciada_en     TEXT    NOT NULL DEFAULT (datetime('now')),
            terminada_en    TEXT,
            puntos_sesion   INTEGER DEFAULT 0,
            racha_max       INTEGER DEFAULT 0
        );

        -- Tabla de respuestas (cada pregunta respondida)
        CREATE TABLE IF NOT EXISTS respuestas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            sesion_id       INTEGER NOT NULL REFERENCES sesiones(id),
            estudiante_id   INTEGER NOT NULL REFERENCES estudiantes(id),
            caso_id         TEXT    NOT NULL,
            expresion       TEXT    NOT NULL,
            respuesta_dada  TEXT,
            fue_correcta    INTEGER NOT NULL DEFAULT 0,  -- 0=no, 1=si
            pistas_usadas   INTEGER DEFAULT 0,
            tiempo_segundos REAL    DEFAULT 0,
            puntos_ganados  INTEGER DEFAULT 0,
            respondida_en   TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        """)


# ---------------------------------------------------------------------------
# MODELO DE DATOS
# ---------------------------------------------------------------------------

@dataclass
class Estudiante:
    """
    Representa un estudiante registrado en el sistema.

    Atributos:
        id:         Clave primaria (None si aún no está guardado en DB).
        nombre:     Nombre del estudiante.
        grado:      Grado escolar (6-11).
        creado_en:  Fecha y hora de registro.
        ultima_vez: Última sesión activa (None si nunca ha jugado).
    """
    nombre:     str
    grado:      int
    id:         Optional[int] = None
    creado_en:  Optional[str] = None
    ultima_vez: Optional[str] = None


@dataclass
class Sesion:
    """Una sesión de juego de un estudiante."""
    estudiante_id:  int
    id:             Optional[int] = None
    iniciada_en:    Optional[str] = None
    terminada_en:   Optional[str] = None
    puntos_sesion:  int = 0
    racha_max:      int = 0


@dataclass
class Respuesta:
    """
    Registro de una respuesta individual durante una sesión.

    fue_correcta es bool guardado como 0/1 en SQLite.
    """
    sesion_id:       int
    estudiante_id:   int
    caso_id:         str
    expresion:       str
    fue_correcta:    bool
    respuesta_dada:  Optional[str] = None
    pistas_usadas:   int = 0
    tiempo_segundos: float = 0.0
    puntos_ganados:  int = 0
    id:              Optional[int] = None


# ---------------------------------------------------------------------------
# OPERACIONES CON ESTUDIANTES
# ---------------------------------------------------------------------------

def crear_o_recuperar_estudiante(nombre: str, grado: int) -> Estudiante:
    """
    Busca un estudiante por nombre y grado.
    Si no existe, lo crea.

    Por qué esta estrategia: simplifica el flujo del juego — el estudiante
    no necesita recordar contraseñas ni IDs, solo su nombre y grado.

    Retorna:
        Estudiante con su id asignado.
    """
    with _conectar() as conn:
        fila = conn.execute(
            "SELECT * FROM estudiantes WHERE nombre = ? AND grado = ?",
            (nombre, grado)
        ).fetchone()

        if fila:
            return Estudiante(
                id=fila["id"],
                nombre=fila["nombre"],
                grado=fila["grado"],
                creado_en=fila["creado_en"],
                ultima_vez=fila["ultima_vez"],
            )

        # No existe → crear
        cursor = conn.execute(
            "INSERT INTO estudiantes (nombre, grado, creado_en) VALUES (?, ?, ?)",
            (nombre, grado, datetime.now().isoformat())
        )
        return Estudiante(id=cursor.lastrowid, nombre=nombre, grado=grado)


def listar_estudiantes(grado: Optional[int] = None) -> list[Estudiante]:
    """
    Retorna todos los estudiantes, opcionalmente filtrados por grado.

    Parámetros:
        grado: Si se indica, filtra solo ese grado. None = todos.
    """
    with _conectar() as conn:
        if grado:
            filas = conn.execute(
                "SELECT * FROM estudiantes WHERE grado = ? ORDER BY nombre",
                (grado,)
            ).fetchall()
        else:
            filas = conn.execute(
                "SELECT * FROM estudiantes ORDER BY grado, nombre"
            ).fetchall()

        return [
            Estudiante(
                id=f["id"], nombre=f["nombre"], grado=f["grado"],
                creado_en=f["creado_en"], ultima_vez=f["ultima_vez"]
            )
            for f in filas
        ]


# ---------------------------------------------------------------------------
# OPERACIONES CON SESIONES
# ---------------------------------------------------------------------------

def iniciar_sesion(estudiante_id: int) -> Sesion:
    """Crea un nuevo registro de sesión y retorna su id."""
    with _conectar() as conn:
        cursor = conn.execute(
            "INSERT INTO sesiones (estudiante_id, iniciada_en) VALUES (?, ?)",
            (estudiante_id, datetime.now().isoformat())
        )
        # Actualiza ultima_vez del estudiante
        conn.execute(
            "UPDATE estudiantes SET ultima_vez = ? WHERE id = ?",
            (datetime.now().isoformat(), estudiante_id)
        )
        return Sesion(id=cursor.lastrowid, estudiante_id=estudiante_id)


def cerrar_sesion(sesion_id: int, puntos: int, racha_max: int):
    """Marca la sesión como terminada con sus estadísticas finales."""
    with _conectar() as conn:
        conn.execute(
            """UPDATE sesiones
               SET terminada_en = ?, puntos_sesion = ?, racha_max = ?
               WHERE id = ?""",
            (datetime.now().isoformat(), puntos, racha_max, sesion_id)
        )


# ---------------------------------------------------------------------------
# OPERACIONES CON RESPUESTAS
# ---------------------------------------------------------------------------

def guardar_respuesta(respuesta: Respuesta):
    """Persiste una respuesta individual en la base de datos."""
    with _conectar() as conn:
        conn.execute(
            """INSERT INTO respuestas
               (sesion_id, estudiante_id, caso_id, expresion, respuesta_dada,
                fue_correcta, pistas_usadas, tiempo_segundos, puntos_ganados, respondida_en)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                respuesta.sesion_id,
                respuesta.estudiante_id,
                respuesta.caso_id,
                respuesta.expresion,
                respuesta.respuesta_dada,
                int(respuesta.fue_correcta),
                respuesta.pistas_usadas,
                respuesta.tiempo_segundos,
                respuesta.puntos_ganados,
                datetime.now().isoformat(),
            )
        )


def obtener_respuestas_estudiante(estudiante_id: int) -> list[dict]:
    """
    Retorna todas las respuestas de un estudiante como lista de dicts.
    Útil para el motor de riesgo y la analítica.
    """
    with _conectar() as conn:
        filas = conn.execute(
            """SELECT * FROM respuestas
               WHERE estudiante_id = ?
               ORDER BY respondida_en DESC""",
            (estudiante_id,)
        ).fetchall()
        return [dict(f) for f in filas]


def obtener_resumen_clase(grado: Optional[int] = None) -> list[dict]:
    """
    Consulta agregada: para cada estudiante retorna sus métricas clave.
    Usada por el dashboard del profesor.

    Retorna lista de dicts con:
        nombre, grado, total_respuestas, correctas, precision_pct,
        pistas_promedio, tiempo_promedio, ultima_actividad, puntos_totales
    """
    filtro_grado = "WHERE e.grado = :grado" if grado else ""
    params = {"grado": grado} if grado else {}

    with _conectar() as conn:
        filas = conn.execute(f"""
            SELECT
                e.id            AS estudiante_id,
                e.nombre,
                e.grado,
                e.ultima_vez    AS ultima_actividad,
                COUNT(r.id)                         AS total_respuestas,
                SUM(r.fue_correcta)                 AS correctas,
                ROUND(100.0 * SUM(r.fue_correcta) / NULLIF(COUNT(r.id), 0), 1)
                                                    AS precision_pct,
                ROUND(AVG(r.pistas_usadas), 2)      AS pistas_promedio,
                ROUND(AVG(r.tiempo_segundos), 1)    AS tiempo_promedio,
                SUM(r.puntos_ganados)               AS puntos_totales
            FROM estudiantes e
            LEFT JOIN respuestas r ON r.estudiante_id = e.id
            {filtro_grado}
            GROUP BY e.id
            ORDER BY e.grado, e.nombre
        """, params).fetchall()

        return [dict(f) for f in filas]


def obtener_rendimiento_por_caso(estudiante_id: Optional[int] = None) -> list[dict]:
    """
    Rendimiento desglosado por tipo de caso de factorización.
    Si estudiante_id es None, agrega toda la clase.
    """
    filtro = "WHERE r.estudiante_id = :eid" if estudiante_id else ""
    params = {"eid": estudiante_id} if estudiante_id else {}

    with _conectar() as conn:
        filas = conn.execute(f"""
            SELECT
                r.caso_id,
                COUNT(r.id)                     AS intentos,
                SUM(r.fue_correcta)             AS correctos,
                ROUND(100.0 * SUM(r.fue_correcta) / NULLIF(COUNT(r.id), 0), 1)
                                                AS precision_pct,
                ROUND(AVG(r.tiempo_segundos), 1) AS tiempo_promedio,
                ROUND(AVG(r.pistas_usadas), 2)  AS pistas_promedio
            FROM respuestas r
            {filtro}
            GROUP BY r.caso_id
            ORDER BY precision_pct ASC
        """, params).fetchall()

        return [dict(f) for f in filas]


def obtener_progreso_temporal(estudiante_id: int, ultimos_n: int = 20) -> list[dict]:
    """
    Últimas N respuestas de un estudiante, ordenadas cronológicamente.
    Usado para graficar la curva de aprendizaje.
    """
    with _conectar() as conn:
        filas = conn.execute(
            """SELECT fue_correcta, puntos_ganados, caso_id, respondida_en
               FROM respuestas
               WHERE estudiante_id = ?
               ORDER BY respondida_en DESC
               LIMIT ?""",
            (estudiante_id, ultimos_n)
        ).fetchall()
        return list(reversed([dict(f) for f in filas]))


# Inicializar la DB al importar el módulo
inicializar_db()
