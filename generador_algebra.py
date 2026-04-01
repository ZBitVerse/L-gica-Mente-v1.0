"""
generador_algebra.py — Puente Lógico SAS BIC
==============================================
Motor central de factorización algebraica.

RESPONSABILIDADES:
  1. Generar expresiones algebraicas para cada caso de factorización.
  2. Identificar automáticamente qué caso aplica a una expresión dada.
  3. Proporcionar el proceso de solución paso a paso.
  4. Generar pistas visuales progresivas (sin revelar la respuesta directamente).
  5. Validar si la respuesta de un estudiante es algebraicamente correcta.

DISEÑO:
  Usamos SymPy (librería de matemáticas simbólicas en Python) para garantizar
  que la validación sea matemáticamente correcta, no solo una comparación de texto.
  Esto significa que "(x+3)(x-3)" y "(x-3)(x+3)" se consideran la misma respuesta.

AUTOR: Puente Lógico SAS BIC
"""

import random
from dataclasses import dataclass, field
from typing import Optional
import sympy as sp
from config import CASOS_FACTORIZACION


# ---------------------------------------------------------------------------
# ESTRUCTURAS DE DATOS
# Usamos dataclasses para representar problemas y soluciones de forma clara.
# ---------------------------------------------------------------------------

@dataclass
class ProblemaFactorizacion:
    """
    Representa un problema de factorización listo para mostrar al estudiante.

    Atributos:
        caso_id:       Clave del tipo de factorización (ej: "diferencia_cuadrados")
        expresion_str: La expresión como texto (ej: "x**2 - 9")
        expresion_sp:  La expresión como objeto SymPy (para validación matemática)
        solucion_str:  La solución factorizada en texto (ej: "(x + 3)*(x - 3)")
        solucion_sp:   La solución como objeto SymPy
        dificultad:    Nivel 1-5
        puntos_base:   Puntos que vale este problema
    """
    caso_id:       str
    expresion_str: str
    expresion_sp:  sp.Expr
    solucion_str:  str
    solucion_sp:   sp.Expr
    dificultad:    int
    puntos_base:   int


@dataclass
class PistasProgresivas:
    """
    Sistema de pistas por niveles para un problema dado.
    El estudiante puede pedir hasta 3 pistas, cada una más reveladora.
    Revelar más pistas reduce el puntaje que puede ganar.

    Atributos:
        pista_1: Orienta sobre el tipo de caso (no da la respuesta)
        pista_2: Muestra la estructura/patrón a identificar
        pista_3: Muestra el primer paso concreto de la solución
        penalizacion_pista: Puntos que se descuentan por cada pista usada
    """
    pista_1:            str
    pista_2:            str
    pista_3:            str
    penalizacion_pista: int = 5


@dataclass
class PasoSolucion:
    """Un paso individual dentro del proceso de solución."""
    numero:      int
    descripcion: str   # Explicación en lenguaje natural
    expresion:   str   # Cómo queda la expresión en este paso


# ---------------------------------------------------------------------------
# GENERADORES DE PROBLEMAS POR CASO
# Cada función genera UN problema aleatorio de su tipo con parámetros
# que garantizan que el resultado sea "limpio" (sin fracciones complicadas).
# ---------------------------------------------------------------------------

def _generar_factor_comun(dificultad: int = 1) -> ProblemaFactorizacion:
    """
    Genera un problema de Factor Común.

    Estrategia:
      - Escoge un factor 'a' aleatorio (número × variable potencia).
      - Multiplica ese factor por 2 o 3 términos simples.
      - El problema es la expresión expandida; la solución es la factorizada.

    Ejemplo generado con a=3x, términos=[2x, 4, 1]:
      Expresión: 6x² + 12x + 3x → se simplifica a 6x² + 15x (incorrecto, ver código)
    """
    x = sp.Symbol('x')

    # El factor común será un número entre 2-9
    factor_num = random.randint(2, 9)

    # Generamos 2 o 3 términos que serán multiplicados por el factor
    if dificultad == 1:
        # Solo factor numérico: 6x + 9 = 3(2x + 3)
        t1 = random.randint(1, 6) * x
        t2 = sp.Integer(random.randint(1, 6))
        expresion = sp.expand(factor_num * t1 + factor_num * t2)
    else:
        # Factor numérico × variable: 6x² + 9x = 3x(2x + 3)
        factor_var = x  # factor también tiene variable
        t1 = random.randint(2, 5) * x**2
        t2 = random.randint(1, 5) * x
        expresion = sp.expand(factor_num * t1 + factor_num * t2)

    # SymPy puede factorizar automáticamente → solución verificada
    solucion = sp.factor(expresion)

    return ProblemaFactorizacion(
        caso_id       = "factor_comun",
        expresion_str = str(expresion),
        expresion_sp  = expresion,
        solucion_str  = str(solucion),
        solucion_sp   = solucion,
        dificultad    = dificultad,
        puntos_base   = CASOS_FACTORIZACION["factor_comun"]["puntos_base"],
    )


def _generar_diferencia_cuadrados(dificultad: int = 2) -> ProblemaFactorizacion:
    """
    Genera un problema de Diferencia de Cuadrados: a² - b².

    Estrategia:
      - Escoge 'a' como variable con coeficiente (ej: x, 2x, 3x).
      - Escoge 'b' como número entero positivo.
      - Construye la expresión a² - b² directamente.

    Garantía: los valores b² serán cuadrados perfectos reconocibles (4, 9, 16, 25...).
    """
    x = sp.Symbol('x')

    # Cuadrados perfectos frecuentes en el currículo
    cuadrados_b = [1, 4, 9, 16, 25, 36, 49] if dificultad <= 2 else [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
    b_cuad = random.choice(cuadrados_b)
    b      = int(b_cuad ** 0.5)

    # Coeficiente de x según dificultad
    coef_a = 1 if dificultad <= 2 else random.choice([1, 2, 3])

    expresion = sp.expand((coef_a * x)**2 - b**2)
    solucion  = sp.factor(expresion)

    return ProblemaFactorizacion(
        caso_id       = "diferencia_cuadrados",
        expresion_str = str(expresion),
        expresion_sp  = expresion,
        solucion_str  = str(solucion),
        solucion_sp   = solucion,
        dificultad    = dificultad,
        puntos_base   = CASOS_FACTORIZACION["diferencia_cuadrados"]["puntos_base"],
    )


def _generar_cuadrado_perfecto(dificultad: int = 3) -> ProblemaFactorizacion:
    """
    Genera un trinomio cuadrado perfecto: (ax + b)².

    Estrategia:
      - Escoge 'a' y 'b' pequeños para que el resultado sea reconocible.
      - Expande (ax + b)² para obtener el trinomio.
      - La solución es volver a (ax + b)².

    La clave pedagógica: el término del medio SIEMPRE es 2ab.
    """
    x = sp.Symbol('x')

    a = 1 if dificultad <= 3 else random.randint(1, 3)
    b = random.randint(1, 7)
    signo = random.choice([1, -1])  # (ax + b)² o (ax - b)²

    expresion = sp.expand((a * x + signo * b)**2)
    solucion  = sp.factor(expresion)

    return ProblemaFactorizacion(
        caso_id       = "cuadrado_perfecto",
        expresion_str = str(expresion),
        expresion_sp  = expresion,
        solucion_str  = str(solucion),
        solucion_sp   = solucion,
        dificultad    = dificultad,
        puntos_base   = CASOS_FACTORIZACION["cuadrado_perfecto"]["puntos_base"],
    )


def _generar_trinomio_simple(dificultad: int = 3) -> ProblemaFactorizacion:
    """
    Genera un trinomio x² + bx + c donde el coeficiente de x² es 1.

    Estrategia:
      - Escoge dos números enteros p y q (pueden ser negativos en dificultad alta).
      - Construye (x + p)(x + q) y expande.
      - p y q se eligen para que b = p+q y c = p*q sean "bonitos".

    Por qué esta estrategia: garantiza que la factorización existe y es entera,
    evitando fracciones que confundirían al estudiante.
    """
    x = sp.Symbol('x')

    # Rango de raíces según dificultad
    if dificultad <= 3:
        rango = list(range(1, 8))  # Solo positivos
    else:
        rango = list(range(-8, 9)) # Positivos y negativos
        rango = [n for n in rango if n != 0]  # Excluye 0

    p = random.choice(rango)
    q = random.choice(rango)

    expresion = sp.expand((x + p) * (x + q))
    solucion  = sp.factor(expresion)

    return ProblemaFactorizacion(
        caso_id       = "trinomio_simple",
        expresion_str = str(expresion),
        expresion_sp  = expresion,
        solucion_str  = str(solucion),
        solucion_sp   = solucion,
        dificultad    = dificultad,
        puntos_base   = CASOS_FACTORIZACION["trinomio_simple"]["puntos_base"],
    )


def _generar_suma_cubos(dificultad: int = 4) -> ProblemaFactorizacion:
    """
    Genera un problema de Suma de Cubos: a³ + b³.

    Cubos perfectos usados: 1, 8, 27, 64, 125 (b = 1, 2, 3, 4, 5).
    """
    x  = sp.Symbol('x')
    bs = [1, 2, 3, 4, 5]
    b  = random.choice(bs)
    a  = 1 if dificultad <= 4 else random.choice([1, 2])

    expresion = (a * x)**3 + b**3
    solucion  = sp.factor(expresion)

    return ProblemaFactorizacion(
        caso_id       = "suma_cubos",
        expresion_str = str(sp.expand(expresion)),
        expresion_sp  = sp.expand(expresion),
        solucion_str  = str(solucion),
        solucion_sp   = solucion,
        dificultad    = dificultad,
        puntos_base   = CASOS_FACTORIZACION["suma_cubos"]["puntos_base"],
    )


def _generar_diferencia_cubos(dificultad: int = 4) -> ProblemaFactorizacion:
    """
    Genera un problema de Diferencia de Cubos: a³ - b³.

    Igual que suma de cubos pero con signo negativo.
    """
    x  = sp.Symbol('x')
    bs = [1, 2, 3, 4, 5]
    b  = random.choice(bs)
    a  = 1 if dificultad <= 4 else random.choice([1, 2])

    expresion = (a * x)**3 - b**3
    solucion  = sp.factor(expresion)

    return ProblemaFactorizacion(
        caso_id       = "diferencia_cubos",
        expresion_str = str(sp.expand(expresion)),
        expresion_sp  = sp.expand(expresion),
        solucion_str  = str(solucion),
        solucion_sp   = solucion,
        dificultad    = dificultad,
        puntos_base   = CASOS_FACTORIZACION["diferencia_cubos"]["puntos_base"],
    )


# Mapa: caso_id → función generadora
_GENERADORES = {
    "factor_comun":         _generar_factor_comun,
    "diferencia_cuadrados": _generar_diferencia_cuadrados,
    "cuadrado_perfecto":    _generar_cuadrado_perfecto,
    "trinomio_simple":      _generar_trinomio_simple,
    "suma_cubos":           _generar_suma_cubos,
    "diferencia_cubos":     _generar_diferencia_cubos,
}


# ---------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# Esta es la función que llama el resto de la aplicación.
# ---------------------------------------------------------------------------

def generar_problema(
    caso_id:    Optional[str] = None,
    dificultad: int = 1
) -> ProblemaFactorizacion:
    """
    Genera un problema de factorización.

    Parámetros:
        caso_id:    ID del caso a generar. Si es None, se elige aleatoriamente
                    entre los casos disponibles para la dificultad indicada.
        dificultad: Nivel 1-5. Determina la complejidad de los coeficientes.

    Retorna:
        ProblemaFactorizacion listo para mostrar al estudiante.

    Ejemplo de uso:
        >>> prob = generar_problema("diferencia_cuadrados", dificultad=2)
        >>> print(prob.expresion_str)   # "x**2 - 9"
        >>> print(prob.solucion_str)    # "(x - 3)*(x + 3)"
    """
    if caso_id is None:
        # Filtra casos según dificultad máxima disponible
        casos_disponibles = [
            cid for cid, cfg in CASOS_FACTORIZACION.items()
            if cfg["dificultad"] <= dificultad and cid in _GENERADORES
        ]
        caso_id = random.choice(casos_disponibles) if casos_disponibles else "factor_comun"

    generador = _GENERADORES.get(caso_id)
    if generador is None:
        raise ValueError(f"Caso '{caso_id}' no reconocido. Casos válidos: {list(_GENERADORES.keys())}")

    return generador(dificultad)


# ---------------------------------------------------------------------------
# IDENTIFICADOR AUTOMÁTICO DE CASOS
# Dada una expresión, determina qué caso de factorización aplica.
# Útil para el modo "identifica el caso" del juego.
# ---------------------------------------------------------------------------

def identificar_caso(expresion_str: str) -> Optional[str]:
    """
    Analiza una expresión algebraica e identifica qué caso de factorización aplica.

    Algoritmo:
      1. Parsea la expresión con SymPy.
      2. La factoriza y analiza la forma del resultado.
      3. Compara con los patrones conocidos.

    Parámetros:
        expresion_str: Expresión como string. Ej: "x**2 - 9" o "x^2 - 9"

    Retorna:
        caso_id (str) si lo identifica, o None si no reconoce el patrón.

    Limitaciones:
        - Solo maneja expresiones en una variable (x).
        - No identifica factorizaciones compuestas (ej: primero factor común y luego diferencia de cuadrados).
    """
    x = sp.Symbol('x')

    # Normalizamos el símbolo de potencia: ^ → ** (SymPy usa **)
    expresion_str = expresion_str.replace('^', '**')

    try:
        expr = sp.sympify(expresion_str)
    except Exception:
        return None  # Expresión inválida

    # Expandimos para trabajar con la forma estándar
    expr_expandida = sp.expand(expr)

    # Obtenemos el polinomio en x
    try:
        poly   = sp.Poly(expr_expandida, x)
        grado  = poly.degree()
        coefs  = poly.all_coeffs()  # De mayor a menor grado
    except Exception:
        return None

    # --- REGLA 1: Factor común ---
    # Si la expresión tiene más de un término y el MCD de sus coeficientes > 1,
    # o todos los términos tienen x como factor → factor común.
    # SymPy lo detecta si factor() produce algo con coeficiente fuera del paréntesis.
    factorizado = sp.factor(expr_expandida)
    args = factorizado.args if factorizado.func == sp.Mul else (factorizado,)
    tiene_factor_numerico = any(a.is_number and abs(a) > 1 for a in args)
    tiene_factor_variable = any(isinstance(a, sp.Symbol) or
                                (a.func == sp.Pow and a.args[0].is_symbol)
                                for a in args)

    # --- REGLA 2: Diferencia de cuadrados ---
    # Forma: ax² + 0x - c  (grado 2, sin término lineal, coeficiente independiente negativo)
    if (grado == 2
            and len(coefs) == 3
            and coefs[1] == 0         # Sin término lineal
            and coefs[2] < 0):        # Término independiente negativo
        a_sq = coefs[0]
        b_sq = -coefs[2]
        # Verificamos que a_sq y b_sq sean cuadrados perfectos
        sqrt_a = sp.sqrt(a_sq)
        sqrt_b = sp.sqrt(b_sq)
        if sqrt_a.is_integer and sqrt_b.is_integer:
            return "diferencia_cuadrados"

    # --- REGLA 3: Trinomio Cuadrado Perfecto ---
    # Forma: a² x² ± 2ab x + b²  → (ax ± b)²
    if grado == 2 and len(coefs) == 3:
        A, B, C = coefs[0], coefs[1], coefs[2]
        if C > 0:
            sqrt_A = sp.sqrt(A)
            sqrt_C = sp.sqrt(C)
            if sqrt_A.is_integer and sqrt_C.is_integer:
                # El término medio debe ser ±2·√A·√C
                if abs(B) == 2 * sqrt_A * sqrt_C:
                    return "cuadrado_perfecto"

    # --- REGLA 4: Trinomio simple (coef de x² = 1) ---
    if grado == 2 and len(coefs) == 3 and coefs[0] == 1:
        # Verificamos que la factorización de SymPy tiene raíces enteras
        raices = sp.solve(expr_expandida, x)
        if all(r.is_integer for r in raices):
            return "trinomio_simple"

    # --- REGLA 5: Trinomio complejo (coef de x² ≠ 1) ---
    if grado == 2 and len(coefs) == 3 and coefs[0] != 1:
        raices = sp.solve(expr_expandida, x)
        if all(r.is_rational for r in raices):
            return "trinomio_complejo"

    # --- REGLA 6 y 7: Suma o diferencia de cubos ---
    if grado == 3 and len(coefs) == 4:
        A, B, C, D = coefs[0], coefs[1], coefs[2], coefs[3]
        # Forma pura: Ax³ + D (sin términos x² ni x)
        if B == 0 and C == 0:
            sqrt3_A = round(A ** (1/3))
            sqrt3_D = round(abs(D) ** (1/3))
            if sqrt3_A**3 == A and abs(sqrt3_D**3) == abs(D):
                return "suma_cubos" if D > 0 else "diferencia_cubos"

    # --- REGLA 8: Factor común (fallback) ---
    # Si después de todas las reglas anteriores el MCD de coeficientes es > 1
    coefs_enteros = [int(c) for c in coefs if c.is_number]
    if len(coefs_enteros) > 1:
        from math import gcd
        from functools import reduce
        mcd = reduce(gcd, [abs(c) for c in coefs_enteros])
        if mcd > 1:
            return "factor_comun"

    return None  # No se reconoció el patrón


# ---------------------------------------------------------------------------
# GENERADOR DE PISTAS PROGRESIVAS
# ---------------------------------------------------------------------------

def generar_pistas(problema: ProblemaFactorizacion) -> PistasProgresivas:
    """
    Genera tres pistas progresivas para un problema dado.

    Nivel de pistas:
      Pista 1: ¿Qué buscar? (Orienta el razonamiento sin revelar el caso)
      Pista 2: ¿Cómo se llama el caso? (Revela el tipo de factorización)
      Pista 3: ¿Cuál es el primer paso? (Da el inicio de la solución)

    Diseño pedagógico: Las pistas siguen la metodología socrática — en lugar
    de dar la respuesta, guían al estudiante a descubrirla.
    """
    caso = CASOS_FACTORIZACION.get(problema.caso_id, {})
    x    = sp.Symbol('x')
    expr = problema.expresion_sp
    poly = sp.Poly(expr, x)

    pista_generica_1 = caso.get("pista_visual", "Observa la estructura de la expresión con cuidado.")
    pista_generica_2 = f"El tipo de factorización que aplica aquí es: **{caso.get('nombre', '?')}**\n\nFórmula: {caso.get('formula', '')}"

    # Pista 3 específica por caso: el primer paso concreto
    pistas_paso_1 = {
        "factor_comun": (
            f"Primer paso: identifica el máximo común divisor (MCD) de todos los coeficientes. "
            f"Luego saca ese factor fuera del paréntesis."
        ),
        "diferencia_cuadrados": (
            f"Primer paso: calcula la raíz cuadrada del primer término y del último término. "
            f"Esas dos raíces serán 'a' y 'b' en la fórmula (a+b)(a-b)."
        ),
        "cuadrado_perfecto": (
            f"Primer paso: calcula √(primer término) = a, y √(último término) = b. "
            f"Verifica que el término del medio sea exactamente 2·a·b."
        ),
        "trinomio_simple": (
            f"Primer paso: busca dos números que multiplicados den **{poly.all_coeffs()[-1]}** "
            f"y sumados den **{poly.all_coeffs()[-2] if len(poly.all_coeffs()) > 2 else '?'}**."
        ),
        "trinomio_complejo": (
            f"Primer paso: multiplica el coeficiente de x² por el término independiente. "
            f"Luego busca dos números que den ese producto y sumen el coeficiente de x."
        ),
        "suma_cubos": (
            f"Primer paso: calcula la raíz cúbica del primer término y del segundo término. "
            f"Esas raíces son 'a' y 'b'. Luego aplica: (a+b)(a²-ab+b²)."
        ),
        "diferencia_cubos": (
            f"Primer paso: calcula la raíz cúbica del primer término y del segundo término. "
            f"Esas raíces son 'a' y 'b'. Luego aplica: (a-b)(a²+ab+b²)."
        ),
    }

    return PistasProgresivas(
        pista_1            = pista_generica_1,
        pista_2            = pista_generica_2,
        pista_3            = pistas_paso_1.get(problema.caso_id, "Revisa la fórmula del caso y aplica paso a paso."),
        penalizacion_pista = 5,
    )


# ---------------------------------------------------------------------------
# GENERADOR DE PASOS DE SOLUCIÓN
# Muestra el proceso completo DESPUÉS de que el estudiante resolvió el problema.
# ---------------------------------------------------------------------------

def generar_pasos_solucion(problema: ProblemaFactorizacion) -> list[PasoSolucion]:
    """
    Genera el proceso de solución paso a paso para mostrar al estudiante
    DESPUÉS de que respondió (correcto o incorrecto).

    Esta función es clave para el aprendizaje: ver el proceso correcto
    refuerza el método, incluso cuando la respuesta fue correcta.

    Parámetros:
        problema: El ProblemaFactorizacion que acaba de resolver el estudiante.

    Retorna:
        Lista de PasoSolucion ordenados.
    """
    x    = sp.Symbol('x')
    expr = problema.expresion_sp
    poly = sp.Poly(expr, x)
    coefs = poly.all_coeffs()

    pasos = []

    if problema.caso_id == "factor_comun":
        from math import gcd
        from functools import reduce
        coefs_ent = [abs(int(c)) for c in coefs]
        mcd = reduce(gcd, coefs_ent)
        pasos = [
            PasoSolucion(1, "Identifica el Máximo Común Divisor (MCD) de todos los coeficientes.",
                         f"MCD{tuple(coefs_ent)} = {mcd}"),
            PasoSolucion(2, "Saca el MCD como factor fuera del paréntesis.",
                         f"{mcd} × ({sp.expand(expr / mcd)})"),
            PasoSolucion(3, "Verifica expandiendo: el resultado debe ser igual a la expresión original.",
                         f"{str(expr)} ✓"),
        ]

    elif problema.caso_id == "diferencia_cuadrados":
        A = coefs[0]
        C = -coefs[-1]  # c está negativo en la expresión
        a = int(sp.sqrt(A))
        b = int(sp.sqrt(C))
        pasos = [
            PasoSolucion(1, "Identifica la forma a² - b². Calcula las raíces cuadradas.",
                         f"√({A}x²) = {a}x   y   √({C}) = {b}"),
            PasoSolucion(2, "Aplica la fórmula: a² - b² = (a + b)(a - b).",
                         f"({a}x + {b})({a}x - {b})"),
            PasoSolucion(3, "Verifica multiplicando los factores.",
                         f"{str(sp.expand(sp.factor(expr)))} = {str(expr)} ✓"),
        ]

    elif problema.caso_id == "cuadrado_perfecto":
        A, B, C = coefs[0], coefs[1], coefs[2]
        a    = int(sp.sqrt(A))
        b    = int(sp.sqrt(abs(C)))
        signo = "+" if B > 0 else "-"
        pasos = [
            PasoSolucion(1, "Verifica que el primer y último término son cuadrados perfectos.",
                         f"√({A}x²) = {a}x   y   √({abs(C)}) = {b}"),
            PasoSolucion(2, "Verifica que el término del medio sea 2·a·b.",
                         f"2 × {a} × {b} = {2*a*b}   (término del medio = {abs(B)}) ✓"),
            PasoSolucion(3, "Escribe la solución: (ax ± b)².",
                         f"({a}x {signo} {b})²"),
        ]

    elif problema.caso_id in ("trinomio_simple", "trinomio_complejo"):
        raices = sp.solve(expr, x)
        r1, r2 = [int(r) for r in raices] if all(r.is_integer for r in raices) else raices
        pasos = [
            PasoSolucion(1, "Busca dos números que multiplicados den el término independiente y sumados den el coeficiente de x.",
                         f"p = {r1 if isinstance(r1, int) else r1}, q = {r2 if isinstance(r2, int) else r2}"),
            PasoSolucion(2, "Escribe los factores (x - p)(x - q).",
                         str(sp.factor(expr))),
            PasoSolucion(3, "Verifica expandiendo.",
                         f"{str(sp.expand(sp.factor(expr)))} = {str(expr)} ✓"),
        ]

    elif problema.caso_id in ("suma_cubos", "diferencia_cubos"):
        A = coefs[0]
        D = coefs[-1]
        a = round(abs(A) ** (1/3))
        b = round(abs(D) ** (1/3))
        signo_b = "+" if D > 0 else "-"
        signo_medio = "-" if D > 0 else "+"
        pasos = [
            PasoSolucion(1, "Identifica los cubos perfectos: calcula la raíz cúbica de cada término.",
                         f"∛({A}x³) = {a}x   y   ∛({abs(D)}) = {b}"),
            PasoSolucion(2, "Aplica la fórmula de cubos.",
                         f"({a}x {signo_b} {b})({a}²x² {signo_medio} {a}·{b}x + {b}²)"),
            PasoSolucion(3, "Simplifica los cuadrados.",
                         f"({a}x {signo_b} {b})({a**2}x² {signo_medio} {a*b}x + {b**2})"),
        ]

    return pasos


# ---------------------------------------------------------------------------
# VALIDADOR DE RESPUESTAS
# Compara la respuesta del estudiante con la solución, algebraicamente.
# ---------------------------------------------------------------------------

def validar_respuesta(respuesta_str: str, problema: ProblemaFactorizacion) -> dict:
    """
    Verifica si la respuesta del estudiante es algebraicamente equivalente
    a la solución correcta.

    Por qué usamos equivalencia algebraica y no comparación de texto:
      - "(x+3)(x-3)" y "(x-3)(x+3)" son ambas correctas.
      - "3(2x+1)" y "(6x+3)/1" son equivalentes aunque escritas diferente.
      - Esto evita frustración cuando el estudiante escribe la respuesta
        correcta de una forma diferente a la esperada.

    Parámetros:
        respuesta_str: Lo que escribió el estudiante. Ej: "(x+3)*(x-3)"
        problema:      El ProblemaFactorizacion con la solución correcta.

    Retorna:
        Diccionario con:
          - "correcto" (bool): ¿Es correcta la respuesta?
          - "mensaje"  (str):  Mensaje para mostrar al estudiante.
          - "diferencia" (str): Si es incorrecta, en qué difiere.
    """
    x = sp.Symbol('x')

    # Normalizamos el símbolo de potencia
    respuesta_str = respuesta_str.replace('^', '**').strip()

    try:
        respuesta_sp = sp.sympify(respuesta_str)
    except Exception:
        return {
            "correcto": False,
            "mensaje": "No pude leer tu respuesta. Revisa que esté bien escrita (usa ** para potencias, * para multiplicar).",
            "diferencia": "Expresión no válida",
        }

    # La diferencia algebraica debe ser 0 si son equivalentes
    diferencia = sp.simplify(sp.expand(respuesta_sp) - sp.expand(problema.expresion_sp))

    if diferencia == 0:
        return {
            "correcto": True,
            "mensaje": "¡Correcto! Tu respuesta es algebraicamente equivalente a la solución.",
            "diferencia": None,
        }
    else:
        return {
            "correcto": False,
            "mensaje": "Tu respuesta no es correcta. Expande los factores que escribiste y compara con la expresión original.",
            "diferencia": f"Tu respuesta expandida: {str(sp.expand(respuesta_sp))} — Original: {str(problema.expresion_sp)}",
        }
