"""
analitica.py — Puente Lógico SAS BIC
======================================
Transforma los datos crudos de la base de datos en métricas y
estructuras listas para visualizar en el dashboard del profesor.

Responsabilidades:
  1. Construir DataFrames de Pandas para los gráficos de Plotly.
  2. Calcular métricas de clase (promedio, distribución, tendencias).
  3. Generar datos de ejemplo (modo demo) cuando la DB está vacía.

Por qué separar la analítica del dashboard:
  La lógica de transformación de datos no debe estar mezclada con el
  código de visualización. Si en el futuro se cambia Streamlit por
  otro framework, esta capa no cambia.
"""

import random
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd

from config import CASOS_FACTORIZACION, GRADOS_COLOMBIA
from estudiantes import (
    obtener_resumen_clase,
    obtener_rendimiento_por_caso,
    obtener_progreso_temporal,
    listar_estudiantes,
)
from motor_riesgo import evaluar_clase, evaluar_riesgo


# ---------------------------------------------------------------------------
# DATOS DE DEMO
# Cuando no hay estudiantes reales, el dashboard muestra datos ficticios
# para que el profesor entienda qué verá con datos reales.
# ---------------------------------------------------------------------------

_NOMBRES_DEMO = [
    "Valentina Torres", "Santiago Gómez", "Camila Rodríguez",
    "Andrés Martínez", "Isabella López", "Sebastián García",
    "Mariana Hernández", "Felipe Castro", "Daniela Vargas",
    "Julián Moreno", "Laura Jiménez", "Tomás Díaz",
]


def _generar_resumen_demo(n: int = 12) -> list[dict]:
    """
    Genera una lista de n estudiantes ficticios con métricas variadas,
    incluyendo algunos con señales de riesgo alto para que el demo
    muestre el sistema de alertas funcionando.
    """
    random.seed(42)   # Seed fijo para que el demo sea reproducible
    estudiantes = []

    for i, nombre in enumerate(_NOMBRES_DEMO[:n]):
        # Simular perfiles variados: bueno, regular, en riesgo
        if i < 4:
            # Buen rendimiento
            precision  = random.uniform(75, 95)
            dias_inact = random.randint(0, 3)
            pistas     = random.uniform(0.2, 0.8)
            tiempo     = random.uniform(20, 50)
        elif i < 8:
            # Rendimiento regular
            precision  = random.uniform(50, 74)
            dias_inact = random.randint(2, 7)
            pistas     = random.uniform(1.0, 2.0)
            tiempo     = random.uniform(50, 90)
        else:
            # En riesgo
            precision  = random.uniform(20, 49)
            dias_inact = random.randint(6, 15)
            pistas     = random.uniform(2.0, 3.0)
            tiempo     = random.uniform(90, 150)

        ultima_act = (
            datetime.now() - timedelta(days=dias_inact)
        ).isoformat()

        total       = random.randint(8, 30)
        correctas   = int(total * precision / 100)
        puntos      = correctas * 15 + random.randint(0, 50)

        estudiantes.append({
            "estudiante_id":   i + 1,
            "nombre":          nombre,
            "grado":           random.choice([7, 8, 9]),
            "ultima_actividad": ultima_act,
            "total_respuestas": total,
            "correctas":       correctas,
            "precision_pct":   round(precision, 1),
            "pistas_promedio": round(pistas, 2),
            "tiempo_promedio": round(tiempo, 1),
            "puntos_totales":  puntos,
        })

    return estudiantes


def _generar_rendimiento_casos_demo() -> list[dict]:
    """Datos demo de rendimiento por caso para toda la clase."""
    random.seed(7)
    return [
        {
            "caso_id":        cid,
            "intentos":       random.randint(20, 80),
            "correctos":      random.randint(10, 60),
            "precision_pct":  round(random.uniform(30, 90), 1),
            "tiempo_promedio": round(random.uniform(25, 120), 1),
            "pistas_promedio": round(random.uniform(0.3, 2.5), 2),
        }
        for cid in CASOS_FACTORIZACION
    ]


def _generar_progreso_demo(n: int = 20) -> list[dict]:
    """Curva de aprendizaje demo para un estudiante."""
    random.seed(13)
    base = 40
    registros = []
    for i in range(n):
        # La precisión mejora gradualmente con algo de ruido
        correcta = random.random() < min(0.9, base / 100 + i * 0.02)
        base    += 2 if correcta else -1
        registros.append({
            "fue_correcta":   int(correcta),
            "puntos_ganados": random.randint(5, 50) if correcta else 0,
            "caso_id":        random.choice(list(CASOS_FACTORIZACION.keys())),
            "respondida_en":  (datetime.now() - timedelta(hours=n - i)).isoformat(),
        })
    return registros


# ---------------------------------------------------------------------------
# FUNCIONES PÚBLICAS DE ANALÍTICA
# ---------------------------------------------------------------------------

@st.cache_data(ttl=600)  # Caché por 10 minutos para ahorrar procesamiento
def cargar_resumen_clase(grado: int = None, demo: bool = False) -> pd.DataFrame:
    """
    Carga el resumen de todos los estudiantes con su nivel de riesgo.

    Parámetros:
        grado: Filtrar por grado (None = todos).
        demo:  Si True, usa datos ficticios (para presentaciones sin datos reales).

    Retorna:
        DataFrame con columnas:
          nombre, grado, precision_pct, total_respuestas, correctas,
          pistas_promedio, tiempo_promedio, ultima_actividad, puntos_totales,
          riesgo_puntaje, riesgo_nivel, riesgo_color
    """
    if demo:
        resumenes = _generar_resumen_demo()
    else:
        resumenes = obtener_resumen_clase(grado)

    # Evaluar riesgo de cada estudiante
    con_riesgo = evaluar_clase(resumenes)

    # Convertir a DataFrame
    filas = []
    for r in con_riesgo:
        riesgo = r["riesgo"]
        filas.append({
            "nombre":           r.get("nombre", "—"),
            "grado":            r.get("grado", "—"),
            "precision_pct":    r.get("precision_pct") or 0,
            "total_respuestas": r.get("total_respuestas") or 0,
            "correctas":        r.get("correctas") or 0,
            "pistas_promedio":  r.get("pistas_promedio") or 0,
            "tiempo_promedio":  r.get("tiempo_promedio") or 0,
            "ultima_actividad": r.get("ultima_actividad") or "Sin actividad",
            "puntos_totales":   r.get("puntos_totales") or 0,
            "riesgo_puntaje":   riesgo.puntaje,
            "riesgo_nivel":     riesgo.nivel,
            "riesgo_color":     riesgo.color,
            "riesgo_factores":  riesgo.factores,
            "recomendacion":    riesgo.recomendacion,
            "estudiante_id":    r.get("estudiante_id"),
        })

    return pd.DataFrame(filas)


@st.cache_data(ttl=600)
def cargar_rendimiento_casos(estudiante_id: int = None, demo: bool = False) -> pd.DataFrame:
    """
    Rendimiento por tipo de caso de factorización.

    Retorna DataFrame con: caso_id, nombre_caso, emoji, intentos,
    precision_pct, tiempo_promedio, pistas_promedio
    """
    if demo:
        datos = _generar_rendimiento_casos_demo()
    else:
        datos = obtener_rendimiento_por_caso(estudiante_id)

    filas = []
    for d in datos:
        cfg = CASOS_FACTORIZACION.get(d["caso_id"], {})
        filas.append({
            "caso_id":         d["caso_id"],
            "nombre_caso":     cfg.get("nombre", d["caso_id"]),
            "emoji":           cfg.get("emoji", "📐"),
            "intentos":        d.get("intentos", 0),
            "precision_pct":   d.get("precision_pct") or 0,
            "tiempo_promedio": d.get("tiempo_promedio") or 0,
            "pistas_promedio": d.get("pistas_promedio") or 0,
        })

    return pd.DataFrame(filas)


def cargar_progreso_estudiante(estudiante_id: int, demo: bool = False) -> pd.DataFrame:
    """
    Historial de respuestas de un estudiante para graficar su curva de aprendizaje.

    Retorna DataFrame con: numero, fue_correcta, puntos_acumulados, caso_id
    """
    if demo:
        datos = _generar_progreso_demo()
    else:
        datos = obtener_progreso_temporal(estudiante_id, ultimos_n=30)

    if not datos:
        return pd.DataFrame()

    df = pd.DataFrame(datos)
    df["numero"]           = range(1, len(df) + 1)
    df["puntos_acumulados"] = df["puntos_ganados"].cumsum()
    df["fue_correcta"]     = df["fue_correcta"].astype(int)
    return df


def metricas_globales(df_clase: pd.DataFrame) -> dict:
    """
    Calcula las métricas de resumen para las tarjetas del encabezado
    del dashboard.

    Retorna dict con:
        total_estudiantes, en_riesgo_alto, en_riesgo_medio,
        precision_promedio, activos_hoy
    """
    if df_clase.empty:
        return {
            "total_estudiantes": 0,
            "en_riesgo_alto":    0,
            "en_riesgo_medio":   0,
            "precision_promedio": 0,
            "activos_hoy":       0,
        }

    hoy = datetime.now().date()

    def _es_hoy(fecha_str):
        try:
            return datetime.fromisoformat(fecha_str).date() == hoy
        except Exception:
            return False

    return {
        "total_estudiantes":  len(df_clase),
        "en_riesgo_alto":     int((df_clase["riesgo_nivel"] == "ALTO").sum()),
        "en_riesgo_medio":    int((df_clase["riesgo_nivel"] == "MEDIO").sum()),
        "precision_promedio": round(df_clase["precision_pct"].mean(), 1),
        "activos_hoy":        int(df_clase["ultima_actividad"].apply(_es_hoy).sum()),
    }
