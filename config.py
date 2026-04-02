"""
config.py — Puente Lógico SAS BIC
===================================
Configuración central de la aplicación.

Aquí definimos todas las constantes del sistema: grados escolares colombianos,
niveles de dificultad, puntos por logro y parámetros del motor de riesgo.
Centralizar la configuración permite cambiar el comportamiento de la app
sin tocar la lógica de negocio.
"""

import os
from dotenv import load_dotenv

# Cargar variables desde archivo .env si existe (entorno DEV)
load_dotenv()

ENV = os.getenv("ENV", "DEV")  # Por defecto asume DEV si no hay variable

# ---------------------------------------------------------------------------
# IDENTIDAD DE LA EMPRESA
# ---------------------------------------------------------------------------
NOMBRE_APP = "Lógicamente"
SUBTITULO  = "Aprende matemáticas jugando — Colombia"
VERSION    = "1.1.0"

# ---------------------------------------------------------------------------
# CONTEXTO CURRICULAR COLOMBIANO
# MEN (Ministerio de Educación Nacional): el álgebra y la factorización
# aparecen formalmente en los grados 8-9 del bachillerato, pero las bases
# (operaciones con variables, monomios) se establecen desde grado 6.
# Fuente: Estándares Básicos de Competencias en Matemáticas, MEN 2006.
# ---------------------------------------------------------------------------
GRADOS_COLOMBIA = {
    # grado : {"nombre": ..., "edad_tipica": ..., "nivel_algebra": ...}
    6:  {"nombre": "Sexto",   "edad_tipica": 11, "nivel_algebra": "pre-algebra"},
    7:  {"nombre": "Séptimo", "edad_tipica": 12, "nivel_algebra": "monomios y polinomios"},
    8:  {"nombre": "Octavo",  "edad_tipica": 13, "nivel_algebra": "factorización básica"},
    9:  {"nombre": "Noveno",  "edad_tipica": 14, "nivel_algebra": "factorización avanzada"},
    10: {"nombre": "Décimo",  "edad_tipica": 15, "nivel_algebra": "ecuaciones cuadráticas"},
    11: {"nombre": "Undécimo","edad_tipica": 16, "nivel_algebra": "cálculo introductorio"},
}

# Grado mínimo recomendado para iniciar el juego de factorización
GRADO_INICIO_RECOMENDADO = 7   # 12 años — tienen bases de variables y polinomios
GRADO_FACTORIZACION_FORMAL = 8  # 13 años — currículo oficial del MEN

# ---------------------------------------------------------------------------
# CASOS DE FACTORIZACIÓN
# Cada caso tiene: nombre, descripción pedagógica, fórmula, grado sugerido,
# nivel de dificultad (1=fácil … 5=experto) y puntaje base al resolverlo.
# ---------------------------------------------------------------------------
CASOS_FACTORIZACION = {
    "factor_comun": {
        "id": "factor_comun",
        "nombre": "Factor Común",
        "emoji": "🔵",
        "descripcion": (
            "Cuando todos los términos de una expresión comparten un factor "
            "(número, variable o ambos), ese factor se 'saca' al frente."
        ),
        "formula": "ax + ay + az = a(x + y + z)",
        "ejemplo":  "6x² + 9x = 3x(2x + 3)",
        "pista_visual": "¿Hay un número o letra que aparezca en TODOS los términos?",
        "grado_sugerido": 7,
        "dificultad": 1,
        "puntos_base": 10,
    },
    "diferencia_cuadrados": {
        "id": "diferencia_cuadrados",
        "nombre": "Diferencia de Cuadrados",
        "emoji": "🟡",
        "descripcion": (
            "Si tenemos dos cuadrados perfectos restados entre sí, "
            "podemos factorizar usando la identidad a² − b² = (a+b)(a−b)."
        ),
        "formula": "a² − b² = (a + b)(a − b)",
        "ejemplo":  "x² − 9 = (x + 3)(x − 3)",
        "pista_visual": "¿Hay DOS términos que sean cuadrados perfectos separados por un SIGNO MENOS?",
        "grado_sugerido": 8,
        "dificultad": 2,
        "puntos_base": 20,
    },
    "cuadrado_perfecto": {
        "id": "cuadrado_perfecto",
        "nombre": "Trinomio Cuadrado Perfecto",
        "emoji": "🟠",
        "descripcion": (
            "Un trinomio es cuadrado perfecto cuando el primer y último término "
            "son cuadrados perfectos, y el término del medio es el doble del producto "
            "de sus raíces: a² ± 2ab + b² = (a ± b)²."
        ),
        "formula": "a² ± 2ab + b² = (a ± b)²",
        "ejemplo":  "x² + 6x + 9 = (x + 3)²",
        "pista_visual": "¿El primero y el último término son cuadrados perfectos? ¿El del medio es 2·√primero·√último?",
        "grado_sugerido": 8,
        "dificultad": 3,
        "puntos_base": 30,
    },
    "suma_cubos": {
        "id": "suma_cubos",
        "nombre": "Suma de Cubos",
        "emoji": "🔴",
        "descripcion": (
            "Cuando dos términos son cubos perfectos sumados, "
            "se factoriza con la fórmula a³ + b³ = (a + b)(a² − ab + b²)."
        ),
        "formula": "a³ + b³ = (a + b)(a² − ab + b²)",
        "ejemplo":  "x³ + 8 = (x + 2)(x² − 2x + 4)",
        "pista_visual": "¿Hay DOS términos positivos que sean cubos perfectos sumados?",
        "grado_sugerido": 9,
        "dificultad": 4,
        "puntos_base": 40,
    },
    "diferencia_cubos": {
        "id": "diferencia_cubos",
        "nombre": "Diferencia de Cubos",
        "emoji": "🟣",
        "descripcion": (
            "Cuando dos términos son cubos perfectos restados, "
            "se factoriza con a³ − b³ = (a − b)(a² + ab + b²)."
        ),
        "formula": "a³ − b³ = (a − b)(a² + ab + b²)",
        "ejemplo":  "x³ − 27 = (x − 3)(x² + 3x + 9)",
        "pista_visual": "¿Hay DOS términos que sean cubos perfectos con un SIGNO MENOS entre ellos?",
        "grado_sugerido": 9,
        "dificultad": 4,
        "puntos_base": 40,
    },
    "trinomio_simple": {
        "id": "trinomio_simple",
        "nombre": "Trinomio x² + bx + c",
        "emoji": "🟢",
        "descripcion": (
            "Un trinomio con coeficiente 1 en x² se factoriza buscando dos números "
            "que multiplicados den 'c' y sumados den 'b': x² + bx + c = (x + p)(x + q)."
        ),
        "formula": "x² + bx + c = (x + p)(x + q)  donde p·q=c y p+q=b",
        "ejemplo":  "x² + 5x + 6 = (x + 2)(x + 3)",
        "pista_visual": "¿Tienes 3 términos donde el primero es x²? Busca dos números que multiplicados den el último y sumados den el del medio.",
        "grado_sugerido": 8,
        "dificultad": 3,
        "puntos_base": 30,
    },
    "trinomio_complejo": {
        "id": "trinomio_complejo",
        "nombre": "Trinomio ax² + bx + c",
        "emoji": "⚫",
        "descripcion": (
            "Cuando el coeficiente de x² es distinto de 1, se usa el método de "
            "factorización por agrupación (método de la 'X' o 'aspa doble')."
        ),
        "formula": "ax² + bx + c  →  busca p·q = a·c  y  p+q = b",
        "ejemplo":  "2x² + 7x + 3 = (2x + 1)(x + 3)",
        "pista_visual": "¿El coeficiente de x² es mayor que 1? Multiplica 'a' por 'c' y busca dos números que den ese producto y sumen 'b'.",
        "grado_sugerido": 9,
        "dificultad": 5,
        "puntos_base": 50,
    },
}

# ---------------------------------------------------------------------------
# GAMIFICACIÓN — Sistema de puntos y niveles
# ---------------------------------------------------------------------------
NIVELES_JUGADOR = {
    1: {"nombre": "Explorador",    "emoji": "🌱", "puntos_min": 0,    "puntos_max": 99},
    2: {"nombre": "Aprendiz",      "emoji": "📚", "puntos_min": 100,  "puntos_max": 299},
    3: {"nombre": "Calculista",    "emoji": "🔢", "puntos_min": 300,  "puntos_max": 599},
    4: {"nombre": "Algebraísta",   "emoji": "🧮", "puntos_min": 600,  "puntos_max": 999},
    5: {"nombre": "Maestro Lógico","emoji": "🏆", "puntos_min": 1000, "puntos_max": 99999},
}

PUNTOS_BONUS = {
    "racha_3":     15,   # 3 respuestas correctas seguidas
    "racha_5":     30,   # 5 respuestas correctas seguidas
    "racha_10":    75,   # 10 respuestas correctas seguidas
    "sin_pistas":  10,   # Respondió sin usar pistas
    "velocidad":   5,    # Respondió en menos de 30 segundos
    "primer_intento": 5, # Correcto al primer intento
}

# ---------------------------------------------------------------------------
# MOTOR DE RIESGO DE DESERCIÓN
# Umbrales basados en investigación del MEN y ICFES sobre factores de deserción.
# Un estudiante entra en "zona de riesgo" si acumula múltiples señales negativas.
# ---------------------------------------------------------------------------
RIESGO_DESERCION = {
    # Si el porcentaje de aciertos baja de este umbral → alerta temprana
    "umbral_aciertos_critico":   40,   # % de respuestas correctas
    "umbral_aciertos_advertencia": 60, # % de respuestas correctas
    # Si lleva más de estos días sin actividad → alerta de abandono
    "dias_sin_actividad_alerta": 5,
    "dias_sin_actividad_critico": 10,
    # Si el tiempo promedio por pregunta supera esto → posible frustración
    "tiempo_maximo_segundos":    120,
    # Máximo de pistas permitidas por sesión antes de alertar al profesor
    "pistas_excesivas_por_sesion": 5,
}

# ---------------------------------------------------------------------------
# COLORES DE LA MARCA — Puente Lógico
# Paleta inspirada en los colores de Colombia + modernidad EdTech
# ---------------------------------------------------------------------------
COLORES = {
    "primario":    "#007AFF",  # Azul Eléctrico (Apple Style) — Acción y tecnología
    "secundario":  "#FFD700",  # Dorado Sunlight — Claridad y logros
    "acento":      "#34C759",  # Verde Esmeralda — Éxito vibrante
    "error":       "#FF3B30",  # Rojo Coral — Alerta clara
    "neutro":      "#ECF0F1",  # Gris claro — fondos
    "texto":       "#2C3E50",  # Azul oscuro — texto principal
}
