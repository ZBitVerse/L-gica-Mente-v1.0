"""
main.py — Puente Lógico SAS BIC
================================
Punto de entrada de la aplicación.
Ejecutar con:  streamlit run main.py

Estructura de pantallas:
  1. Bienvenida / registro del estudiante
  2. Juego de factorización  ← pantalla principal
  3. Resultado de la sesión
"""

import streamlit as st
import time

from config import (
    NOMBRE_APP, SUBTITULO, COLORES, CASOS_FACTORIZACION,
    NIVELES_JUGADOR, PUNTOS_BONUS, GRADOS_COLOMBIA,
    GRADO_INICIO_RECOMENDADO,
)
from generador_algebra import (
    generar_problema, validar_respuesta,
    generar_pistas, generar_pasos_solucion,
)

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title=NOMBRE_APP,
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# ESTILOS CSS — Paleta Puente Lógico
# ---------------------------------------------------------------------------

st.markdown(f"""
<style>
  /* Fondo general */
  .stApp {{
      background-color: {COLORES['neutro']};
  }}

  /* Tarjeta principal del ejercicio */
  .card-ejercicio {{
      background: white;
      border-radius: 16px;
      padding: 32px;
      box-shadow: 0 4px 20px rgba(27,79,114,0.12);
      border-left: 6px solid {COLORES['primario']};
      margin: 12px 0;
  }}

  /* Expresión algebraica grande */
  .expresion-grande {{
      font-size: 2.4rem;
      font-weight: 700;
      color: {COLORES['primario']};
      text-align: center;
      padding: 20px 0;
      font-family: 'Courier New', monospace;
      letter-spacing: 2px;
  }}

  /* Badge del caso */
  .badge-caso {{
      display: inline-block;
      background: {COLORES['primario']};
      color: white;
      padding: 4px 14px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 8px;
  }}

  /* Tarjeta de pista */
  .card-pista {{
      background: #FEF9E7;
      border: 1px solid {COLORES['secundario']};
      border-radius: 10px;
      padding: 14px 18px;
      margin: 8px 0;
      font-size: 0.95rem;
  }}

  /* Respuesta correcta */
  .resultado-correcto {{
      background: #EAFAF1;
      border: 2px solid {COLORES['acento']};
      border-radius: 12px;
      padding: 18px 24px;
      text-align: center;
      font-size: 1.1rem;
      font-weight: 600;
      color: #1E8449;
      margin: 12px 0;
  }}

  /* Respuesta incorrecta */
  .resultado-incorrecto {{
      background: #FDEDEC;
      border: 2px solid {COLORES['error']};
      border-radius: 12px;
      padding: 18px 24px;
      font-size: 1rem;
      color: #922B21;
      margin: 12px 0;
  }}

  /* Panel de puntaje */
  .panel-puntos {{
      background: {COLORES['primario']};
      color: white;
      border-radius: 12px;
      padding: 14px 20px;
      text-align: center;
  }}

  /* Paso de solución */
  .paso-solucion {{
      background: #EBF5FB;
      border-left: 4px solid {COLORES['primario']};
      border-radius: 0 8px 8px 0;
      padding: 10px 16px;
      margin: 6px 0;
      font-size: 0.92rem;
  }}

  /* Botón personalizado (override Streamlit) */
  div.stButton > button {{
      width: 100%;
      border-radius: 10px;
      font-weight: 600;
      padding: 10px;
  }}

  /* Header de la app */
  .app-header {{
      text-align: center;
      padding: 8px 0 16px 0;
  }}
  .app-header h1 {{
      color: {COLORES['primario']};
      font-size: 2rem;
      margin: 0;
  }}
  .app-header p {{
      color: #666;
      margin: 4px 0 0 0;
      font-size: 0.95rem;
  }}

  /* Racha de respuestas */
  .racha {{
      font-size: 1.4rem;
      font-weight: 700;
      color: {COLORES['secundario']};
  }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# INICIALIZACIÓN DEL ESTADO DE SESIÓN
# st.session_state persiste variables entre interacciones del usuario
# sin perder datos al hacer clic en botones.
# ---------------------------------------------------------------------------

def _init_estado():
    """Inicializa todas las variables de sesión si no existen."""
    defaults = {
        # Pantalla activa: "bienvenida", "juego", "resultado"
        "pantalla": "bienvenida",

        # Datos del estudiante
        "nombre": "",
        "grado": 8,

        # Problema actual
        "problema": None,
        "pistas_obj": None,
        "pistas_usadas": 0,
        "ya_respondio": False,
        "resultado_actual": None,

        # Estadísticas de la sesión
        "puntos": 0,
        "racha": 0,
        "racha_max": 0,
        "ejercicios_resueltos": 0,
        "respuestas_correctas": 0,
        "tiempo_inicio": None,

        # Dificultad actual (sube automáticamente con los aciertos)
        "dificultad": 1,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_estado()


# ---------------------------------------------------------------------------
# FUNCIONES DE NAVEGACIÓN
# ---------------------------------------------------------------------------

def ir_a_juego():
    """Genera el primer problema y cambia a la pantalla de juego."""
    st.session_state.pantalla = "juego"
    _nuevo_problema()


def _nuevo_problema():
    """Genera un nuevo problema y resetea el estado del turno."""
    # La dificultad sube cada 5 respuestas correctas, máximo 5
    dif = min(5, 1 + st.session_state.respuestas_correctas // 5)
    st.session_state.dificultad = dif

    problema = generar_problema(dificultad=dif)
    st.session_state.problema       = problema
    st.session_state.pistas_obj     = generar_pistas(problema)
    st.session_state.pistas_usadas  = 0
    st.session_state.ya_respondio   = False
    st.session_state.resultado_actual = None
    st.session_state.tiempo_inicio  = time.time()


def _calcular_nivel(puntos: int) -> dict:
    """Devuelve el nivel del jugador según sus puntos."""
    for nivel in sorted(NIVELES_JUGADOR.keys(), reverse=True):
        if puntos >= NIVELES_JUGADOR[nivel]["puntos_min"]:
            return NIVELES_JUGADOR[nivel]
    return NIVELES_JUGADOR[1]


# ---------------------------------------------------------------------------
# PANTALLA 1: BIENVENIDA / REGISTRO
# ---------------------------------------------------------------------------

def pantalla_bienvenida():
    st.markdown("""
    <div class="app-header">
        <h1>🧮 Puente Lógico</h1>
        <p>Aprende factorización algebraica jugando</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Columnas para centrar el formulario
    col_izq, col_centro, col_der = st.columns([1, 2, 1])

    with col_centro:
        st.markdown("### Antes de empezar...")

        nombre = st.text_input(
            "Tu nombre",
            placeholder="Escribe tu nombre aquí",
            max_chars=40,
        )

        grado = st.selectbox(
            "¿En qué grado estás?",
            options=list(GRADOS_COLOMBIA.keys()),
            format_func=lambda g: f"Grado {GRADOS_COLOMBIA[g]['nombre']} ({GRADOS_COLOMBIA[g]['edad_tipica']} años)",
            index=2,  # Grado 8 por defecto
        )

        st.markdown("")  # Espacio

        # Aviso si el grado es muy bajo
        if grado < GRADO_INICIO_RECOMENDADO:
            st.info(
                f"Este juego está diseñado principalmente para grados 7° en adelante. "
                f"¡Pero puedes intentarlo si ya conoces las variables y los polinomios!"
            )

        # Mostrar descripción del nivel algebraico del grado elegido
        nivel_algebra = GRADOS_COLOMBIA[grado]["nivel_algebra"]
        st.caption(f"📚 Nivel esperado en grado {grado}: *{nivel_algebra}*")

        st.markdown("")

        if st.button("🚀 ¡Empezar a jugar!", type="primary"):
            if nombre.strip():
                st.session_state.nombre = nombre.strip()
                st.session_state.grado  = grado
                ir_a_juego()
                st.rerun()
            else:
                st.error("Escribe tu nombre para continuar.")

    # Sección informativa debajo
    st.markdown("---")
    st.markdown("#### ¿Qué aprenderás en este juego?")

    cols = st.columns(3)
    casos_a_mostrar = ["factor_comun", "diferencia_cuadrados", "cuadrado_perfecto"]
    for i, caso_id in enumerate(casos_a_mostrar):
        caso = CASOS_FACTORIZACION[caso_id]
        with cols[i]:
            st.markdown(f"""
            **{caso['emoji']} {caso['nombre']}**

            `{caso['formula']}`

            *Ej: {caso['ejemplo']}*
            """)


# ---------------------------------------------------------------------------
# PANTALLA 2: JUEGO
# ---------------------------------------------------------------------------

def pantalla_juego():
    problema = st.session_state.problema
    if problema is None:
        _nuevo_problema()
        st.rerun()
        return

    caso_cfg = CASOS_FACTORIZACION.get(problema.caso_id, {})

    # ── ENCABEZADO: nombre + puntos + nivel ──────────────────────────────
    col_nombre, col_puntos, col_racha = st.columns([3, 2, 1])

    with col_nombre:
        nivel = _calcular_nivel(st.session_state.puntos)
        st.markdown(
            f"**{nivel['emoji']} {st.session_state.nombre}** "
            f"— Grado {st.session_state.grado}  \n"
            f"*Nivel: {nivel['nombre']}*"
        )

    with col_puntos:
        st.markdown(
            f'<div class="panel-puntos">'
            f'⭐ <strong>{st.session_state.puntos}</strong> puntos'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_racha:
        if st.session_state.racha >= 3:
            st.markdown(
                f'<div class="racha" title="Racha de respuestas correctas">'
                f'🔥 {st.session_state.racha}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── TARJETA DEL EJERCICIO ─────────────────────────────────────────────
    st.markdown(
        f'<div class="card-ejercicio">'
        f'<span class="badge-caso">{caso_cfg.get("emoji","📐")} {caso_cfg.get("nombre","Factorización")}</span>'
        f'<p style="color:#555; font-size:0.9rem; margin:4px 0 0 0;">'
        f'Dificultad: {"⭐" * problema.dificultad}{"☆" * (5 - problema.dificultad)}'
        f' &nbsp;|&nbsp; Vale {problema.puntos_base} puntos</p>'
        f'<div class="expresion-grande">{_formato_expresion(problema.expresion_str)}</div>'
        f'<p style="text-align:center; color:#888; font-size:0.9rem;">Factoriza esta expresión</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── PISTAS ────────────────────────────────────────────────────────────
    pistas = st.session_state.pistas_obj
    pistas_usadas = st.session_state.pistas_usadas

    if not st.session_state.ya_respondio:
        col_p1, col_p2, col_p3 = st.columns(3)

        with col_p1:
            if pistas_usadas < 1:
                if st.button("💡 Pista 1 (-5 pts)", disabled=False):
                    st.session_state.pistas_usadas = 1
                    st.rerun()
            else:
                st.markdown(
                    f'<div class="card-pista">💡 <strong>Pista 1:</strong><br>{pistas.pista_1}</div>',
                    unsafe_allow_html=True,
                )

        with col_p2:
            if pistas_usadas < 2:
                if st.button("💡 Pista 2 (-5 pts)", disabled=(pistas_usadas < 1)):
                    st.session_state.pistas_usadas = 2
                    st.rerun()
            else:
                st.markdown(
                    f'<div class="card-pista">💡 <strong>Pista 2:</strong><br>{pistas.pista_2}</div>',
                    unsafe_allow_html=True,
                )

        with col_p3:
            if pistas_usadas < 3:
                if st.button("💡 Pista 3 (-5 pts)", disabled=(pistas_usadas < 2)):
                    st.session_state.pistas_usadas = 3
                    st.rerun()
            else:
                st.markdown(
                    f'<div class="card-pista">💡 <strong>Pista 3:</strong><br>{pistas.pista_3}</div>',
                    unsafe_allow_html=True,
                )

    # ── FORMULARIO DE RESPUESTA ───────────────────────────────────────────
    if not st.session_state.ya_respondio:
        st.markdown("")
        st.markdown("#### ✏️ Tu respuesta")
        st.caption(
            "Escribe la expresión factorizada. "
            "Usa `**` para potencias y `*` para multiplicar. "
            "Ejemplo: `(x+3)*(x-3)` o `3*(2*x+1)`"
        )

        with st.form("form_respuesta", clear_on_submit=True):
            respuesta_input = st.text_input(
                "Tu respuesta:",
                placeholder="Ej: (x + 3)*(x - 3)",
                label_visibility="collapsed",
            )
            col_enviar, col_saltar = st.columns([3, 1])
            with col_enviar:
                enviado = st.form_submit_button("Verificar respuesta ✅", type="primary")
            with col_saltar:
                saltado = st.form_submit_button("Saltar ⏭️")

        if enviado and respuesta_input.strip():
            _procesar_respuesta(respuesta_input.strip(), problema)
            st.rerun()

        if saltado:
            # Saltar cuenta como incorrecto, rompe la racha
            st.session_state.racha = 0
            st.session_state.ejercicios_resueltos += 1
            st.session_state.resultado_actual = {
                "correcto": False,
                "mensaje": f"Saltaste este ejercicio. La respuesta correcta era: {problema.solucion_str}",
                "puntos_ganados": 0,
            }
            st.session_state.ya_respondio = True
            st.rerun()

    # ── RESULTADO ─────────────────────────────────────────────────────────
    else:
        resultado = st.session_state.resultado_actual

        if resultado["correcto"]:
            st.markdown(
                f'<div class="resultado-correcto">'
                f'✅ {resultado["mensaje"]}<br>'
                f'<span style="font-size:1.5rem;">+{resultado.get("puntos_ganados", 0)} puntos</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="resultado-incorrecto">'
                f'❌ {resultado["mensaje"]}'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Mostrar solución paso a paso
        with st.expander("📖 Ver solución paso a paso", expanded=resultado["correcto"]):
            pasos = generar_pasos_solucion(problema)
            for paso in pasos:
                st.markdown(
                    f'<div class="paso-solucion">'
                    f'<strong>Paso {paso.numero}:</strong> {paso.descripcion}<br>'
                    f'<code>{paso.expresion}</code>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"**Respuesta oficial:** `{problema.solucion_str}`"
            )

        # Botón para continuar
        st.markdown("")
        col_sig, col_menu = st.columns([3, 1])
        with col_sig:
            if st.button("➡️ Siguiente ejercicio", type="primary"):
                _nuevo_problema()
                st.rerun()
        with col_menu:
            if st.button("🏠 Menú"):
                st.session_state.pantalla = "resultado"
                st.rerun()

    # ── BARRA LATERAL: estadísticas de sesión ─────────────────────────────
    with st.sidebar:
        st.markdown(f"### 📊 Mi sesión")
        st.metric("Ejercicios", st.session_state.ejercicios_resueltos)
        st.metric("Correctas", st.session_state.respuestas_correctas)
        if st.session_state.ejercicios_resueltos > 0:
            pct = int(100 * st.session_state.respuestas_correctas / st.session_state.ejercicios_resueltos)
            st.metric("Precisión", f"{pct}%")
        st.metric("Racha máx.", st.session_state.racha_max)
        st.markdown("---")
        st.markdown("**Casos disponibles:**")
        for cid, cfg in CASOS_FACTORIZACION.items():
            st.markdown(f"{cfg['emoji']} {cfg['nombre']}")


# ---------------------------------------------------------------------------
# PANTALLA 3: RESULTADO FINAL DE LA SESIÓN
# ---------------------------------------------------------------------------

def pantalla_resultado():
    nivel = _calcular_nivel(st.session_state.puntos)

    st.markdown(f"""
    <div class="app-header">
        <h1>{nivel['emoji']} Sesión terminada</h1>
        <p>¡Buen trabajo, {st.session_state.nombre}!</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⭐ Puntos totales", st.session_state.puntos)
    with col2:
        st.metric("✅ Ejercicios correctos", st.session_state.respuestas_correctas)
    with col3:
        st.metric("🔥 Racha máxima", st.session_state.racha_max)

    st.markdown("")
    st.success(f"**Nivel alcanzado: {nivel['emoji']} {nivel['nombre']}**")

    st.markdown("---")

    col_reiniciar, col_nuevo = st.columns(2)

    with col_reiniciar:
        if st.button("🔄 Jugar de nuevo (mismo jugador)"):
            # Conserva nombre y grado, reinicia estadísticas
            st.session_state.puntos = 0
            st.session_state.racha = 0
            st.session_state.racha_max = 0
            st.session_state.ejercicios_resueltos = 0
            st.session_state.respuestas_correctas = 0
            st.session_state.dificultad = 1
            ir_a_juego()
            st.rerun()

    with col_nuevo:
        if st.button("👤 Nuevo jugador"):
            # Reinicia todo
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            _init_estado()
            st.rerun()


# ---------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------

def _formato_expresion(expr_str: str) -> str:
    """
    Convierte la notación Python de SymPy a una forma más legible.
    Ejemplo: "x**2 - 9"  →  "x² - 9"
    """
    return (
        expr_str
        .replace("**2", "²")
        .replace("**3", "³")
        .replace("**4", "⁴")
        .replace("*", "·")
    )


def _procesar_respuesta(respuesta: str, problema):
    """
    Evalúa la respuesta del estudiante y actualiza puntos, racha
    y estadísticas de la sesión.
    """
    tiempo_usado = time.time() - (st.session_state.tiempo_inicio or time.time())
    resultado = validar_respuesta(respuesta, problema)

    puntos_ganados = 0

    if resultado["correcto"]:
        # Puntos base, menos penalización por pistas
        penalizacion = st.session_state.pistas_usadas * 5
        puntos_ganados = max(0, problema.puntos_base - penalizacion)

        # Bonus por velocidad (menos de 30 segundos)
        if tiempo_usado < 30:
            puntos_ganados += PUNTOS_BONUS["velocidad"]

        # Bonus por no usar pistas
        if st.session_state.pistas_usadas == 0:
            puntos_ganados += PUNTOS_BONUS["sin_pistas"]

        # Actualizar racha
        st.session_state.racha += 1
        if st.session_state.racha == 3:
            puntos_ganados += PUNTOS_BONUS["racha_3"]
        elif st.session_state.racha == 5:
            puntos_ganados += PUNTOS_BONUS["racha_5"]
        elif st.session_state.racha == 10:
            puntos_ganados += PUNTOS_BONUS["racha_10"]

        st.session_state.racha_max = max(
            st.session_state.racha_max, st.session_state.racha
        )
        st.session_state.respuestas_correctas += 1

    else:
        st.session_state.racha = 0  # Rompe la racha

    st.session_state.puntos += puntos_ganados
    st.session_state.ejercicios_resueltos += 1
    st.session_state.ya_respondio = True
    st.session_state.resultado_actual = {**resultado, "puntos_ganados": puntos_ganados}


# ---------------------------------------------------------------------------
# ENRUTADOR PRINCIPAL
# ---------------------------------------------------------------------------

pantalla = st.session_state.pantalla

if pantalla == "bienvenida":
    pantalla_bienvenida()
elif pantalla == "juego":
    pantalla_juego()
elif pantalla == "resultado":
    pantalla_resultado()
