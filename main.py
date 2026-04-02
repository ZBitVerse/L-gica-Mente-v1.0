"""
main.py — Puente Lógico SAS BIC
================================
Punto de entrada de la aplicación.
Ejecutar con:  streamlit run main.py
"""

import streamlit as st
import time
import logging

from config import (
    NOMBRE_APP, COLORES, CASOS_FACTORIZACION,
    NIVELES_JUGADOR, PUNTOS_BONUS, GRADOS_COLOMBIA, VERSION,
    GRADO_INICIO_RECOMENDADO,
)
from generador_algebra import (
    generar_problema, validar_respuesta,
    generar_pistas, generar_pasos_solucion,
)
from estudiantes import (
    crear_o_recuperar_estudiante, iniciar_sesion, 
    guardar_respuesta, cerrar_sesion, Respuesta
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Lógicamente",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS — Diseño moderno para estudiantes
# ---------------------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

:root {
    --primary: #007AFF;
    --accent: #FFD700;
    --success: #34C759;
    --error: #FF3B30;
    --glass: rgba(255, 255, 255, 0.08);
    --glass-border: rgba(255, 255, 255, 0.15);
    --grad-dark: linear-gradient(180deg, #000000, #0F172A, #1E293B);
}

/* ── Reset y base ── */
html, body, .stApp {
    font-family: 'Nunito', sans-serif !important;
    scroll-behavior: smooth; /* Desplazamiento suave */
}

.stApp {
    background: var(--grad-dark);
    min-height: 100vh;
}

/* ── Animaciones de Entrada (Scroll Reveal) ── */
.st-scroll-reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}
.st-scroll-reveal.st-is-visible {
    opacity: 1;
    transform: translateY(0);
}
/* Retrasos para elementos consecutivos */
.st-scroll-reveal:nth-child(2) { transition-delay: 0.1s; }
.st-scroll-reveal:nth-child(3) { transition-delay: 0.2s; }
.st-scroll-reveal:nth-child(4) { transition-delay: 0.3s; }
.st-scroll-reveal:nth-child(5) { transition-delay: 0.4s; }

/* ── UI Elements ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

/* ── HERO de bienvenida ── */
.hero {
    text-align: center;
    padding: 40px 20px 20px;
}
.hero-logo {
    font-size: 5rem;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-10px); }
}
.hero h1 {
    font-size: 3.5rem;
    font-weight: 900;
    background: linear-gradient(180deg, #FFFFFF 0%, #FFD700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 8px 0 4px;
}
.hero p {
    color: rgba(255,255,255,0.75);
    font-size: 1.1rem;
    margin: 0;
}

/* ── Tarjeta glass ── */
.glass {
    background: var(--glass);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px); /* Para compatibilidad con Safari */
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 32px;
    margin: 12px 0;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); /* Sombra más pronunciada */
    transition: border 0.3s ease; /* Transición suave para el borde */
}
.glass:hover {
    border: 1px solid rgba(243, 156, 18, 0.4); /* Borde dorado al pasar el mouse */
}

/* ── Tarjeta de caso en bienvenida ── */
.caso-card {
    background: rgba(255,255,255,0.03); /* Fondo más sutil */
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 20px 16px;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Animación más elástica */
    height: 100%;
}
.caso-card:hover {
    background: rgba(255,255,255,0.12);
    transform: translateY(-4px);
}
.caso-card .emoji { font-size: 2.2rem; }
.caso-card h4 { color: var(--accent); font-size: 0.95rem; margin: 8px 0 4px; }
.caso-card .formula {
    font-family: 'Courier New', monospace;
    color: rgba(255,255,255,0.6);
    font-size: 0.78rem;
    background: rgba(0,0,0,0.3);
    padding: 4px 8px;
    border-radius: 6px;
    display: inline-block;
    margin: 4px 0;
}
.caso-card .ejemplo { color: rgba(255,255,255,0.5); font-size: 0.78rem; }

/* ── Panel de jugador (header del juego) ── */
.player-bar {
    background: rgba(255,255,255,0.08);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}
.player-name { color: white; font-weight: 800; font-size: 1.05rem; } /* Ya usa Nunito */
.player-level { color: #F39C12; font-size: 0.85rem; font-weight: 600; }

/* ── Barra de XP ── */
.xp-bar-container {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 10px 16px;
    margin: 8px 0 16px;
}
.xp-label {
    display: flex;
    justify-content: space-between;
    color: rgba(255,255,255,0.6);
    font-size: 0.78rem;
    margin-bottom: 6px;
}
.xp-track {
    background: rgba(255,255,255,0.1);
    border-radius: 99px;
    height: 10px;
    overflow: hidden;
}
.xp-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #F39C12, #f7c948);
    transition: width 0.5s ease;
}

/* ── Tarjeta del ejercicio ── */
.ejercicio-card {
    background: rgba(255,255,255,0.98); /* Fondo casi blanco para contraste */
    border-radius: 24px;
    padding: 32px 28px;
    box-shadow: 0 20px 80px rgba(0,0,0,0.5); /* Sombra más dramática */
    margin: 15px 0 25px; /* Más espacio */
    text-align: center;
}
.ejercicio-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1B4F72, #2980b9);
    color: white;
    padding: 5px 16px;
    border-radius: 99px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.ejercicio-dificultad {
    color: #888;
    font-size: 0.85rem;
    margin: 4px 0 16px;
}
.ejercicio-expresion {
    font-size: 2.8rem;
    font-weight: 900;
    color: var(--primary);
    font-family: 'Courier New', monospace;
    padding: 16px 8px;
    letter-spacing: 3px;
    line-height: 1.2;
}
.ejercicio-instruccion {
    color: #999;
    font-size: 0.88rem;
    margin-top: 8px;
}

/* ── Racha ── */
.racha-badge {
    background: linear-gradient(135deg, #e67e22, #f39c12);
    color: white;
    border-radius: 12px;
    padding: 8px 14px;
    font-weight: 800;
    font-size: 1.2rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(243,156,18,0.4);
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 4px 15px rgba(243,156,18,0.4); }
    50%       { box-shadow: 0 4px 25px rgba(243,156,18,0.8); }
}

/* ── Puntos ── */
/* .puntos-badge ya está bien */
    background: linear-gradient(135deg, #1B4F72, #2471a3);
    color: white;
    border-radius: 12px;
    padding: 8px 14px;
    font-weight: 800;
    font-size: 1.1rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(27,79,114,0.4);
}

/* ── Pistas ── */
.pista-card {
    background: rgba(243,156,18,0.12); /* Color de acento */
    border: 1px solid rgba(243,156,18,0.3);
    border-radius: 14px;
    padding: 14px 16px;
    color: white;
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 4px 0;
}
.pista-card strong { color: #F39C12; }

/* ── Resultado correcto ── */
.resultado-correcto {
    background: linear-gradient(135deg, var(--success), #2ecc71); /* Usar variable */
    border-radius: 18px;
    padding: 24px;
    text-align: center;
    color: white;
    margin: 12px 0;
    box-shadow: 0 8px 30px rgba(39,174,96,0.4);
    animation: celebrate 0.5s ease;
}
@keyframes celebrate {
    0%   { transform: scale(0.95); opacity: 0; }
    60%  { transform: scale(1.02); }
    100% { transform: scale(1);    opacity: 1; }
}
.resultado-correcto .titulo { font-size: 1.6rem; font-weight: 900; }
.resultado-correcto .puntos { font-size: 2.2rem; font-weight: 900; margin: 8px 0; }
.resultado-correcto .detalle { font-size: 0.88rem; opacity: 0.85; }

/* ── Resultado incorrecto ── */
.resultado-incorrecto {
    background: linear-gradient(135deg, var(--error), #e74c3c); /* Usar variable */
    border-radius: 18px;
    padding: 20px 24px;
    color: white;
    margin: 12px 0;
    box-shadow: 0 8px 30px rgba(192,57,43,0.3);
}
.resultado-incorrecto .titulo { font-size: 1.2rem; font-weight: 800; }
.resultado-incorrecto .mensaje { font-size: 0.9rem; opacity: 0.9; margin-top: 6px; }

/* ── Pasos de solución ── */
.paso {
    background: rgba(255,255,255,0.06);
    border-left: 4px solid var(--accent); /* Usar variable */
    border-radius: 0 12px 12px 0;
    padding: 12px 16px;
    margin: 6px 0;
    color: white;
}
.paso .num { color: var(--accent); font-weight: 800; }
.paso .desc { font-size: 0.9rem; opacity: 0.9; } /* Ya usa Nunito */
.paso .expr {
    font-family: 'Courier New', monospace;
    background: rgba(0,0,0,0.3);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.85rem;
    color: #f7c948;
    display: inline-block;
    margin-top: 4px;
}

/* ── Pantalla de resultado final ── */
.resultado-final {
    text-align: center;
    padding: 20px;
}
.resultado-final .trofeo { font-size: 5rem; animation: float 2s ease-in-out infinite; } /* Ya tiene animación */
.resultado-final h1 { color: #F39C12; font-size: 2.5rem; font-weight: 900; margin: 8px 0; }
.resultado-final p { color: rgba(255,255,255,0.8); font-size: 1.1rem; }

.stat-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
}
.stat-card .valor { font-size: 2.4rem; font-weight: 900; color: var(--accent); } /* Usar variable */
.stat-card .etiqueta { color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-top: 4px; }

/* ── Inputs y botones ── */
.stTextInput > div > div > input {
    background: rgba(0, 0, 0, 0.4) !important; /* Fondo oscuro para máximo contraste */
    border: 2px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
    color: white !important;
    font-size: 1.1rem !important;
    padding: 12px 16px !important;
    font-family: 'Courier New', monospace !important;
}
div.stTextInput > div > div > input:focus { /* Más específico */
    border-color: #F39C12 !important;
    box-shadow: 0 0 0 3px rgba(243,156,18,0.2) !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.35) !important; }

div.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 10px 20px !important;
    width: 100% !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important; /* Transición más suave */
}
div.stButton > button:hover { transform: translateY(-2px) !important; }
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #F39C12, #f7c948) !important;
    color: #1a1a1a !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(243,156,18,0.4) !important;
}

/* Selectbox y labels */
.stSelectbox label, .stTextInput label {
    color: rgba(255,255,255,0.85) !important;
    font-weight: 600 !important;
}
div[data-baseweb="select"] > div {
    background: rgba(0, 0, 0, 0.4) !important; /* Fondo oscuro para máximo contraste */
    border: 2px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
}
/* Asegura que el texto seleccionado sea visible */
div[data-baseweb="select"] div {
    color: white !important;
}

/* Tabs y Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* Sidebar */
/* Custom Checkbox y Radio simulation */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: transparent;
}
.stTabs [data-baseweb="tab"] {
    background-color: var(--glass);
    border-radius: 10px 10px 0 0;
    color: white;
}
.stTabs [aria-selected="true"] {
    background-color: var(--accent) !important;
    color: var(--primary) !important;
}
.css-1d391kg, [data-testid="stSidebar"] {
    background: rgba(15,32,39,0.95) !important;
}
[data-testid="stSidebar"] * { color: white !important; }

/* Separador */
hr { border-color: rgba(255,255,255,0.1) !important; }

/* Mensaje de instrucción */
.instruccion-input {
    color: rgba(255,255,255,0.5);
    font-size: 0.82rem;
    text-align: center;
    margin: -8px 0 10px;
}

/* Secciones de la Landing */
.landing-section {
    padding: 60px 0;
    color: white;
}
.section-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #F39C12;
    margin-bottom: 20px;
}

/* Toast/Notificación flotante */
.st-toast-container {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.st-toast {
    background-color: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    margin-top: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    opacity: 0;
    animation: fadeInOut 3s forwards;
}
@keyframes fadeInOut {
    0%, 100% { opacity: 0; }
    10%, 90% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# ESTADO DE SESIÓN
# ---------------------------------------------------------------------------

def _init_estado():
    defaults = {
        "pantalla":             "bienvenida",
        "nombre":               "",
        "autenticado":          False,
        "rol":                  "estudiante",
        "estudiante_id":        None,
        "sesion_id":            None,
        "grado":                8,
        "problema":             None,
        "pistas_obj":           None,
        "pistas_usadas":        0,
        "ya_respondio":         False,
        "resultado_actual":     None,
        "puntos":               0,
        "racha":                0,
        "racha_max":            0,
        "ejercicios_resueltos": 0,
        "respuestas_correctas": 0,
        "tiempo_inicio":        None,
        "dificultad":           1,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_estado()


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _calcular_nivel(puntos: int) -> dict:
    for n in sorted(NIVELES_JUGADOR.keys(), reverse=True):
        if puntos >= NIVELES_JUGADOR[n]["puntos_min"]:
            return NIVELES_JUGADOR[n]
    return NIVELES_JUGADOR[1]


def _xp_progreso(puntos: int) -> tuple[int, int, int]:
    """Retorna (xp_actual_en_nivel, xp_necesario, pct) para la barra de progreso."""
    nivel_actual = _calcular_nivel(puntos)
    nid = [k for k, v in NIVELES_JUGADOR.items() if v["nombre"] == nivel_actual["nombre"]][0]
    xp_min = nivel_actual["puntos_min"]
    xp_max = nivel_actual["puntos_max"]
    if xp_max >= 99999:
        return puntos - xp_min, 1, 100
    rango    = xp_max - xp_min
    actual   = puntos - xp_min
    pct      = min(100, int(100 * actual / rango))
    return actual, rango, pct


def _formato_expr(expr_str: str) -> str:
    """Convierte notación SymPy a notación legible."""
    return (
        expr_str
        .replace("**2", "²")
        .replace("**3", "³")
        .replace("**4", "⁴")
        .replace("*", " · ")
    )


def _nuevo_problema():
    dif = min(5, 1 + st.session_state.respuestas_correctas // 5)
    st.session_state.dificultad     = dif
    problema                         = generar_problema(dificultad=dif)
    st.session_state.problema        = problema
    st.session_state.pistas_obj      = generar_pistas(problema)
    st.session_state.pistas_usadas   = 0
    st.session_state.ya_respondio    = False
    st.session_state.resultado_actual = None
    st.session_state.tiempo_inicio   = time.time()


def _procesar_respuesta(respuesta: str, problema):
    tiempo = time.time() - (st.session_state.tiempo_inicio or time.time())
    res    = validar_respuesta(respuesta, problema)
    pts    = 0

    if res["correcto"]:
        pts = max(0, problema.puntos_base - st.session_state.pistas_usadas * 5)
        if tiempo < 30:               pts += PUNTOS_BONUS["velocidad"]
        if st.session_state.pistas_usadas == 0: pts += PUNTOS_BONUS["sin_pistas"]

        st.session_state.racha += 1
        if st.session_state.racha == 3:  pts += PUNTOS_BONUS["racha_3"]
        elif st.session_state.racha == 5: pts += PUNTOS_BONUS["racha_5"]
        elif st.session_state.racha == 10: pts += PUNTOS_BONUS["racha_10"]

        st.session_state.racha_max = max(st.session_state.racha_max, st.session_state.racha)
        st.session_state.respuestas_correctas += 1
    else:
        st.session_state.racha = 0

    # Guardar en Base de Datos
    if st.session_state.sesion_id:
        reg_resp = Respuesta(
            sesion_id=st.session_state.sesion_id,
            estudiante_id=st.session_state.estudiante_id,
            caso_id=problema.caso_id,
            expresion=problema.expresion_str,
            fue_correcta=res["correcto"],
            respuesta_dada=respuesta,
            pistas_usadas=st.session_state.pistas_usadas,
            tiempo_segundos=round(tiempo, 2),
            puntos_ganados=pts
        )
        guardar_respuesta(reg_resp)

    if not res["correcto"]:
        st.session_state.racha = 0

    st.session_state.puntos               += pts
    st.session_state.ejercicios_resueltos += 1
    st.session_state.ya_respondio          = True
    st.session_state.resultado_actual      = {**res, "puntos_ganados": pts}


# ---------------------------------------------------------------------------
# PANTALLA 1: BIENVENIDA
# ---------------------------------------------------------------------------

def pantalla_bienvenida():
    # ── HERO SECTION ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero st-scroll-reveal">
        <div class="hero-logo">🧮</div>
        <h1>Lógicamente</h1>
        <p style="font-size: 1.4rem; color: #f7c948;">Transformando el miedo a las matemáticas en éxito escolar</p>
        <p style="max-width: 700px; margin: 20px auto; opacity: 0.8;">
            Una plataforma interactiva diseñada para reducir la deserción escolar en Colombia 
            mediante el dominio del álgebra con tecnología de vanguardia.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── LOGIN / REGISTRO ────────────────────────────────────────────────
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="glass st-scroll-reveal" style="animation-delay: 0.2s">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "✨ Registrarse"])
        
        with tab1:
            l_nombre = st.text_input("Nombre de usuario", key="l_user")
            l_grado  = st.selectbox("Grado", list(GRADOS_COLOMBIA.keys()), key="l_grade")
            l_pass   = st.text_input("Contraseña", type="password", key="l_pass")
            if st.button("Entrar a jugar", type="primary", use_container_width=True):
                from estudiantes import verificar_usuario
                u = verificar_usuario(l_nombre, l_grado, l_pass)
                if u:
                    _login_usuario(u)
                else:
                    logger.warning(f"Intento de login fallido para: {l_nombre}")
                    st.error("Credenciales incorrectas")

        with tab2:
            r_nombre = st.text_input("¿Cómo quieres llamarte?", key="r_user")
            r_grado  = st.selectbox("Grado escolar", list(GRADOS_COLOMBIA.keys()), key="r_grade", index=2)
            r_pass   = st.text_input("Crea una contraseña", type="password", key="r_pass")
            if st.button("Crear mi cuenta", use_container_width=True):
                if r_nombre and r_pass:
                    u = crear_o_recuperar_estudiante(r_nombre, r_grado, r_pass)
                    _login_usuario(u)
                else:
                    st.warning("Completa todos los campos")

        st.markdown('</div>', unsafe_allow_html=True)

def _login_usuario(u):
    """Helper para centralizar la lógica de inicio de sesión."""
    ses = iniciar_sesion(u.id)
    st.session_state.nombre = u.nombre
    st.session_state.estudiante_id = u.id
    st.session_state.sesion_id = ses.id
    st.session_state.grado = u.grado
    st.session_state.rol = u.rol
    st.session_state.autenticado = True
    
    if u.rol == "profesor":
        st.switch_page("pages/01_profesor.py")
    else:
        st.session_state.pantalla = "juego"
        _nuevo_problema()
    st.rerun()

    # ── SECCIÓN: EL PROBLEMA ─────────────────────────────────────────────
    st.markdown("""
    <div class="landing-section st-scroll-reveal" style="text-align:center; animation-delay: 0.4s">
        <h2 class="section-title">¿Por qué Puente Lógico?</h2>
        <div style="display:flex; justify-content:center; gap:30px; flex-wrap:wrap;">
            <div class="glass st-scroll-reveal" style="width:300px; animation-delay:0.5s">
                <h3>📉 5%</h3>
                <p>Tasa de deserción escolar en secundaria en Colombia.</p>
            </div>
            <div class="glass st-scroll-reveal" style="width:300px; animation-delay:0.6s">
                <h3>✖️ Álgebra</h3>
                <p>La principal barrera académica que causa abandono escolar.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECCIÓN: CARACTERÍSTICAS ─────────────────────────────────────────
    st.markdown('<h2 class="section-title st-scroll-reveal" style="text-align:center; animation-delay: 0.7s">Nuestra Tecnología</h2>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="caso-card">
            <div class="emoji">🧠</div>
            <h4>Motor Algebraico</h4>
            <p style="font-size:0.8rem; opacity:0.7;">Validación real con SymPy. No comparamos texto, entendemos matemáticas.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="caso-card">
            <div class="emoji">🚨</div>
            <h4>Motor de Riesgo</h4>
            <p style="font-size:0.8rem; opacity:0.7;">Alertas tempranas para profesores basadas en patrones de comportamiento.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="caso-card">
            <div class="emoji">🎮</div>
            <h4>Gamificación</h4>
            <p style="font-size:0.8rem; opacity:0.7;">Niveles, rachas y puntos para mantener el compromiso del estudiante.</p>
        </div>
        """, unsafe_allow_html=True)

    # Cards de casos
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown( # No le pongo scroll-reveal a este texto para que aparezca con las cards
        '<p style="text-align:center; color:rgba(255,255,255,0.5); font-size:0.9rem; margin-bottom:12px;">'
        'LO QUE APRENDERÁS</p>',
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    casos = list(CASOS_FACTORIZACION.items())[:4]
    for i, (_, caso) in enumerate(casos):
        with cols[i]: # Las cards individuales tendrán un delay para un efecto escalonado
            st.markdown(f"""
            <div class="caso-card">
                <div class="emoji">{caso['emoji']}</div>
                <h4>{caso['nombre']}</h4>
                <div class="formula">{caso['formula']}</div>
                <div class="ejemplo">Ej: {caso['ejemplo']}</div>
            </div>
            """, unsafe_allow_html=True)

    # JavaScript para el Scroll Reveal
    st.components.v1.html("""
    <script>
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('st-is-visible');
            } else {
                // Opcional: remover la clase si sale de la vista para re-animar
                // entry.target.classList.remove('st-is-visible');
            }
        });
    }, { threshold: 0.1 }); // El 10% del elemento debe ser visible

    document.querySelectorAll('.st-scroll-reveal').forEach(element => observer.observe(element));
    </script>
    """, height=0)


# ---------------------------------------------------------------------------
# PANTALLA 2: JUEGO
# ---------------------------------------------------------------------------

def pantalla_juego():
    problema = st.session_state.problema
    if not problema:
        _nuevo_problema()
        st.rerun()
        return

    caso_cfg = CASOS_FACTORIZACION.get(problema.caso_id, {})
    nivel    = _calcular_nivel(st.session_state.puntos)
    xp_act, xp_total, xp_pct = _xp_progreso(st.session_state.puntos)

    # ── BARRA DEL JUGADOR ────────────────────────────────────────────────
    col_info, col_pts, col_racha = st.columns([4, 2, 1])

    with col_info:
        st.markdown(
            f'<div style="color:white; font-weight:800; font-size:1.05rem;">'
            f'{nivel["emoji"]} {st.session_state.nombre}'
            f'</div>'
            f'<div style="color:#F39C12; font-size:0.82rem; font-weight:600;">'
            f'{nivel["nombre"]}  ·  Grado {st.session_state.grado}'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_pts:
        st.markdown(
            f'<div class="puntos-badge">⭐ {st.session_state.puntos} pts</div>',
            unsafe_allow_html=True,
        )

    with col_racha:
        if st.session_state.racha >= 3:
            st.markdown(
                f'<div class="racha-badge">🔥 {st.session_state.racha}</div>',
                unsafe_allow_html=True,
            )

    # ── BARRA DE XP ──────────────────────────────────────────────────────
    siguiente = _calcular_nivel(st.session_state.puntos + 1)
    st.markdown(f"""
    <div class="xp-bar-container">
        <div class="xp-label">
            <span>Progreso al nivel <strong>{siguiente['nombre']}</strong></span>
            <span>{xp_act} / {xp_total} XP</span>
        </div>
        <div class="xp-track">
            <div class="xp-fill" style="width:{xp_pct}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TARJETA DEL EJERCICIO ─────────────────────────────────────────────
    estrellas_llenas = "★" * problema.dificultad
    estrellas_vacias = "☆" * (5 - problema.dificultad)

    st.markdown(f"""
    <div class="ejercicio-card">
        <div>
            <span class="ejercicio-badge">
                {caso_cfg.get('emoji','📐')} {caso_cfg.get('nombre','Factorización')}
            </span>
        </div>
        <div class="ejercicio-dificultad">
            {estrellas_llenas}{estrellas_vacias} &nbsp;·&nbsp; Vale {problema.puntos_base} puntos
        </div>
        <div class="ejercicio-expresion">{_formato_expr(problema.expresion_str)}</div>
        <div class="ejercicio-instruccion">Escribe la forma factorizada de esta expresión</div>
    </div>
    """, unsafe_allow_html=True)

    # ── PISTAS ────────────────────────────────────────────────────────────
    pistas       = st.session_state.pistas_obj
    pistas_usadas = st.session_state.pistas_usadas

    if not st.session_state.ya_respondio:
        col_p1, col_p2, col_p3 = st.columns(3)

        for idx, (col, num, texto) in enumerate([
            (col_p1, 1, pistas.pista_1),
            (col_p2, 2, pistas.pista_2),
            (col_p3, 3, pistas.pista_3),
        ]):
            with col:
                if pistas_usadas < num:
                    st.button(
                        f"💡 Pista {num}  −5 pts",
                        key=f"pista_{num}",
                        disabled=(pistas_usadas < num - 1),
                        on_click=lambda n=num: setattr(st.session_state, 'pistas_usadas', n),
                    )
                else:
                    st.markdown(
                        f'<div class="pista-card">'
                        f'<strong>Pista {num}:</strong> {texto}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    # ── FORMULARIO DE RESPUESTA ───────────────────────────────────────────
    if not st.session_state.ya_respondio:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<p class="instruccion-input">'
            'Usa <code>**</code> para potencias y <code>*</code> para multiplicar &nbsp;·&nbsp;'
            'Ej: <code>(x+3)*(x-3)</code>'
            '</p>',
            unsafe_allow_html=True,
        )

        with st.form("form_respuesta", clear_on_submit=True):
            respuesta_input = st.text_input(
                "Respuesta",
                placeholder="Escribe tu respuesta aquí...",
                label_visibility="collapsed",
            )
            c1, c2 = st.columns([4, 1])
            with c1:
                enviado = st.form_submit_button("✅  Verificar respuesta", type="primary")
            with c2:
                saltado = st.form_submit_button("⏭️ Saltar")

        if enviado and respuesta_input.strip():
            _procesar_respuesta(respuesta_input.strip(), problema)
            st.rerun()

        if saltado:
            st.session_state.racha                = 0
            st.session_state.ejercicios_resueltos += 1
            st.session_state.resultado_actual      = {
                "correcto":       False,
                "mensaje":        f"Saltaste este ejercicio.",
                "puntos_ganados": 0,
            }
            st.session_state.ya_respondio = True
            st.rerun()

    # ── RESULTADO ─────────────────────────────────────────────────────────
    else:
        resultado = st.session_state.resultado_actual

        if resultado["correcto"]:
            pts = resultado.get("puntos_ganados", 0)
            bonos = []
            if st.session_state.pistas_usadas == 0: bonos.append("Sin pistas +10")
            if st.session_state.racha >= 3:          bonos.append(f"Racha x{st.session_state.racha} 🔥")
            bonos_html = " &nbsp;·&nbsp; ".join(bonos) if bonos else ""

            st.markdown(f"""
            <div class="resultado-correcto">
                <div class="titulo">¡Correcto! 🎉</div>
                <div class="puntos">+{pts} puntos</div>
                {f'<div class="detalle">{bonos_html}</div>' if bonos_html else ''}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="resultado-incorrecto">
                <div class="titulo">❌ Respuesta incorrecta</div>
                <div class="mensaje">{resultado.get('mensaje','')}</div>
            </div>
            """, unsafe_allow_html=True)

        # Solución paso a paso
        with st.expander("📖  Ver solución paso a paso"):
            pasos = generar_pasos_solucion(problema)
            for paso in pasos:
                st.markdown(f"""
                <div class="paso">
                    <span class="num">Paso {paso.numero}:</span>
                    <span class="desc"> {paso.descripcion}</span><br>
                    <span class="expr">{paso.expresion}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(
                f'<p style="color:#F39C12; font-weight:700; margin-top:12px;">'
                f'Respuesta: <code style="background:rgba(0,0,0,0.3); padding:2px 8px; border-radius:6px;">'
                f'{problema.solucion_str}</code></p>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button("➡️  Siguiente ejercicio", type="primary"):
                _nuevo_problema()
                st.rerun()
        with c2:
            if st.button("🏁 Terminar"):
                if st.session_state.sesion_id:
                    cerrar_sesion(
                        st.session_state.sesion_id, 
                        st.session_state.puntos, 
                        st.session_state.racha_max
                    )
                st.session_state.pantalla = "resultado"
                st.rerun()

    # ── SIDEBAR ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"## 📊 Mi sesión")
        st.markdown("---")
        st.metric("Ejercicios", st.session_state.ejercicios_resueltos)
        st.metric("Correctas",  st.session_state.respuestas_correctas)
        if st.session_state.ejercicios_resueltos > 0:
            pct = int(100 * st.session_state.respuestas_correctas / st.session_state.ejercicios_resueltos)
            st.metric("Precisión", f"{pct}%")
        st.metric("Racha máx.", st.session_state.racha_max)
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            cerrar_sesion_ui()
        st.markdown("**Casos del juego:**")
        for _, cfg in CASOS_FACTORIZACION.items():
            st.markdown(f"{cfg['emoji']} {cfg['nombre']}")


# ---------------------------------------------------------------------------
# PANTALLA 3: RESULTADO FINAL
# ---------------------------------------------------------------------------

def pantalla_resultado():
    nivel = _calcular_nivel(st.session_state.puntos)
    total = st.session_state.ejercicios_resueltos
    pct   = int(100 * st.session_state.respuestas_correctas / total) if total else 0

    # Trofeo y mensaje
    if pct >= 80:
        trofeo, mensaje = "🏆", "¡Rendimiento excelente!"
    elif pct >= 60:
        trofeo, mensaje = "🥈", "¡Muy buen trabajo!"
    else:
        trofeo, mensaje = "💪", "¡Sigue practicando!"

    st.markdown(f"""
    <div class="resultado-final">
        <div class="trofeo">{trofeo}</div>
        <h1>Sesión terminada</h1>
        <p>{mensaje} <strong>{st.session_state.nombre}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, str(st.session_state.puntos),               "Puntos totales"),
        (c2, str(st.session_state.respuestas_correctas),  "Correctas"),
        (c3, f"{pct}%",                                   "Precisión"),
        (c4, str(st.session_state.racha_max),             "Racha máxima"),
    ]
    for col, val, label in stats:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="valor">{val}</div>
                <div class="etiqueta">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="glass" style="text-align:center; color:white;">'
        f'Nivel alcanzado: <strong style="color:#F39C12; font-size:1.1rem;">'
        f'{nivel["emoji"]} {nivel["nombre"]}</strong>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄  Jugar de nuevo", type="primary"):
            for k in ["puntos","racha","racha_max","ejercicios_resueltos","respuestas_correctas","dificultad"]:
                st.session_state[k] = 0
            st.session_state.pantalla = "juego"
            _nuevo_problema()
            st.rerun()
    with c2:
        if st.button("👤  Cambiar jugador"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            _init_estado()
            st.rerun()


# ---------------------------------------------------------------------------
# ENRUTADOR
# ---------------------------------------------------------------------------

{
    "bienvenida": pantalla_bienvenida,
    "juego":      pantalla_juego,
    "resultado":  pantalla_resultado,
}.get(st.session_state.pantalla, pantalla_bienvenida)()
