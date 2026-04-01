"""
motor_riesgo.py — Puente Lógico SAS BIC
=========================================
Detecta estudiantes en riesgo de deserción escolar basándose en
su comportamiento dentro del juego.

Fundamento pedagógico:
  Investigación del MEN y ICFES muestra que el abandono escolar en
  matemáticas tiene señales tempranas detectables semanas antes del
  abandono formal: bajo rendimiento sostenido, ausentismo creciente,
  frustración visible (muchas pistas, tiempos largos, respuestas en blanco).

  Este motor traduce esas señales a un puntaje de riesgo numérico (0-100)
  que el profesor puede consultar en tiempo real.

Niveles de riesgo:
  BAJO     (0-39):  Estudiante estable, sigue el ritmo esperado.
  MEDIO    (40-69): Señales de dificultad. Requiere atención preventiva.
  ALTO     (70-100): Riesgo real de abandono. Intervención urgente.
"""

from datetime import datetime, timedelta
from typing import Optional
from config import RIESGO_DESERCION


# ---------------------------------------------------------------------------
# MODELO DEL RESULTADO DE RIESGO
# ---------------------------------------------------------------------------

class ResultadoRiesgo:
    """
    Encapsula el análisis de riesgo de un estudiante.

    Atributos:
        puntaje:    0-100. Mayor = más riesgo.
        nivel:      "BAJO", "MEDIO" o "ALTO"
        color:      Color para mostrar en la UI (#hex)
        factores:   Lista de factores que contribuyen al riesgo (para el profesor)
        recomendacion: Acción sugerida para el profesor
    """

    # Umbrales para clasificar el nivel
    UMBRAL_MEDIO = 40
    UMBRAL_ALTO  = 70

    # Colores asociados a cada nivel
    COLORES = {
        "BAJO":  "#27AE60",   # verde
        "MEDIO": "#F39C12",   # amarillo
        "ALTO":  "#E74C3C",   # rojo
    }

    def __init__(self, puntaje: float, factores: list[str]):
        self.puntaje      = round(min(100, max(0, puntaje)), 1)
        self.factores     = factores

        # Clasificar nivel según puntaje
        if self.puntaje >= self.UMBRAL_ALTO:
            self.nivel = "ALTO"
            self.recomendacion = (
                "Contactar al estudiante y su acudiente esta semana. "
                "Considerar sesión de apoyo individualizado."
            )
        elif self.puntaje >= self.UMBRAL_MEDIO:
            self.nivel = "MEDIO"
            self.recomendacion = (
                "Revisar los casos donde tiene más dificultad. "
                "Ofrecer ejercicios adicionales de práctica."
            )
        else:
            self.nivel = "BAJO"
            self.recomendacion = "Seguimiento regular. El estudiante está progresando bien."

        self.color = self.COLORES[self.nivel]

    def __repr__(self):
        return f"Riesgo({self.nivel}, {self.puntaje}/100)"


# ---------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL DE EVALUACIÓN
# ---------------------------------------------------------------------------

def evaluar_riesgo(metricas: dict) -> ResultadoRiesgo:
    """
    Calcula el nivel de riesgo de deserción de un estudiante.

    Parámetros:
        metricas: Diccionario con estadísticas del estudiante.
                  Claves esperadas (todas opcionales, usa defaults seguros):
                    - precision_pct      (float): % de respuestas correctas
                    - total_respuestas   (int):   ejercicios completados
                    - pistas_promedio    (float): pistas usadas por ejercicio
                    - tiempo_promedio    (float): segundos por respuesta
                    - ultima_actividad   (str):   fecha ISO de última sesión
                    - dias_sin_actividad (int):   días desde la última sesión

    Retorna:
        ResultadoRiesgo con puntaje, nivel y factores detectados.

    Metodología:
        Cada factor de riesgo aporta un peso al puntaje total (0-100).
        Los pesos fueron calibrados con base en los umbrales del MEN.
    """
    factores = []
    puntaje  = 0.0

    # ── FACTOR 1: Precisión baja ──────────────────────────────────────────
    # Peso máximo: 40 puntos (el factor más importante)
    precision = metricas.get("precision_pct") or 0

    if precision < RIESGO_DESERCION["umbral_aciertos_critico"]:
        # Menos del 40% de aciertos → máxima alerta
        contribucion = 40.0
        factores.append(
            f"Precisión crítica: {precision}% de respuestas correctas "
            f"(mínimo esperado: {RIESGO_DESERCION['umbral_aciertos_critico']}%)"
        )
    elif precision < RIESGO_DESERCION["umbral_aciertos_advertencia"]:
        # Entre 40% y 60% → alerta moderada, proporcional
        contribucion = 40.0 * (
            (RIESGO_DESERCION["umbral_aciertos_advertencia"] - precision)
            / (RIESGO_DESERCION["umbral_aciertos_advertencia"] - RIESGO_DESERCION["umbral_aciertos_critico"])
        )
        factores.append(
            f"Precisión baja: {precision}% de respuestas correctas"
        )
    else:
        contribucion = 0.0

    puntaje += contribucion

    # ── FACTOR 2: Inactividad ─────────────────────────────────────────────
    # Peso máximo: 30 puntos
    dias = _calcular_dias_inactivo(metricas.get("ultima_actividad"))

    if dias is not None:
        if dias >= RIESGO_DESERCION["dias_sin_actividad_critico"]:
            contribucion = 30.0
            factores.append(
                f"Inactividad crítica: {dias} días sin jugar "
                f"(límite: {RIESGO_DESERCION['dias_sin_actividad_critico']} días)"
            )
        elif dias >= RIESGO_DESERCION["dias_sin_actividad_alerta"]:
            contribucion = 30.0 * (
                (dias - RIESGO_DESERCION["dias_sin_actividad_alerta"])
                / (RIESGO_DESERCION["dias_sin_actividad_critico"] - RIESGO_DESERCION["dias_sin_actividad_alerta"])
            )
            factores.append(f"Sin actividad reciente: {dias} días desde la última sesión")
        else:
            contribucion = 0.0
        puntaje += contribucion

    # ── FACTOR 3: Uso excesivo de pistas ─────────────────────────────────
    # Peso máximo: 15 puntos
    # Muchas pistas = frustración, no comprensión conceptual
    pistas_prom = metricas.get("pistas_promedio") or 0

    if pistas_prom >= 2.5:
        contribucion = 15.0
        factores.append(
            f"Dependencia de pistas: usa en promedio {pistas_prom:.1f} pistas por ejercicio"
        )
    elif pistas_prom >= 1.5:
        contribucion = 7.5
        factores.append(f"Uso frecuente de pistas: {pistas_prom:.1f} por ejercicio")
    else:
        contribucion = 0.0

    puntaje += contribucion

    # ── FACTOR 4: Tiempo excesivo por pregunta ────────────────────────────
    # Peso máximo: 15 puntos
    # Tiempo muy alto = bloqueo emocional o falta de comprensión
    tiempo_prom = metricas.get("tiempo_promedio") or 0

    if tiempo_prom > RIESGO_DESERCION["tiempo_maximo_segundos"]:
        contribucion = 15.0
        factores.append(
            f"Tiempo de respuesta muy alto: {tiempo_prom:.0f}s promedio "
            f"(máximo recomendado: {RIESGO_DESERCION['tiempo_maximo_segundos']}s)"
        )
    elif tiempo_prom > RIESGO_DESERCION["tiempo_maximo_segundos"] * 0.7:
        contribucion = 7.5
        factores.append(f"Tiempo de respuesta elevado: {tiempo_prom:.0f}s promedio")
    else:
        contribucion = 0.0

    puntaje += contribucion

    # Si no hay respuestas aún, no hay suficiente información
    if (metricas.get("total_respuestas") or 0) == 0:
        return ResultadoRiesgo(
            puntaje=0,
            factores=["Sin datos suficientes para evaluar riesgo (0 respuestas registradas)"]
        )

    return ResultadoRiesgo(puntaje=puntaje, factores=factores if factores else ["Sin señales de riesgo detectadas"])


# ---------------------------------------------------------------------------
# FUNCIÓN PARA EVALUAR TODA LA CLASE
# ---------------------------------------------------------------------------

def evaluar_clase(resumenes: list[dict]) -> list[dict]:
    """
    Evalúa el riesgo de todos los estudiantes de una clase.

    Parámetros:
        resumenes: Lista de dicts devueltos por estudiantes.obtener_resumen_clase()

    Retorna:
        Lista de dicts con los campos originales + campo "riesgo" (ResultadoRiesgo),
        ordenada de mayor a menor riesgo.
    """
    resultados = []

    for resumen in resumenes:
        riesgo = evaluar_riesgo(resumen)
        resultados.append({**resumen, "riesgo": riesgo})

    # Ordena de mayor riesgo a menor (más urgentes primero)
    return sorted(resultados, key=lambda r: r["riesgo"].puntaje, reverse=True)


# ---------------------------------------------------------------------------
# FUNCIÓN AUXILIAR
# ---------------------------------------------------------------------------

def _calcular_dias_inactivo(ultima_actividad: Optional[str]) -> Optional[int]:
    """
    Calcula cuántos días han pasado desde la última actividad.

    Parámetros:
        ultima_actividad: String ISO datetime o None si nunca ha jugado.

    Retorna:
        Número de días (int) o None si el dato no está disponible.
    """
    if not ultima_actividad:
        return None
    try:
        ultima = datetime.fromisoformat(ultima_actividad)
        delta  = datetime.now() - ultima
        return delta.days
    except (ValueError, TypeError):
        return None
