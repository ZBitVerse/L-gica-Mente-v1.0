"""
pages/01_profesor.py — Puente Lógico SAS BIC
=============================================
Dashboard del profesor.

Acceso: http://localhost:8501/profesor  (Streamlit multi-page)

Secciones:
  1. Tarjetas de resumen: total estudiantes, en riesgo, precisión promedio
  2. Tabla de clase: todos los estudiantes con nivel de riesgo y métricas
  3. Alertas: estudiantes con riesgo ALTO, con detalle de factores
  4. Rendimiento por caso: qué tipos de factorización le cuestan más a la clase
  5. Detalle individual: curva de aprendizaje de un estudiante seleccionado
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from config import COLORES, CASOS_FACTORIZACION, NOMBRE_APP
from analitica import (
    cargar_resumen_clase,
    cargar_rendimiento_casos,
    cargar_progreso_estudiante,
    metricas_globales,
)

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title=f"Profesor — {NOMBRE_APP}",
    page_icon="👨‍🏫",
    layout="wide",
)

# ---------------------------------------------------------------------------
# ESTILOS
# ---------------------------------------------------------------------------

st.markdown(f"""
<style>
  .stApp {{ background-color: {COLORES['neutro']}; }}

  .metric-card {{
      background: white;
      border-radius: 14px;
      padding: 20px 24px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08);
      text-align: center;
  }}
  .metric-card .valor {{
      font-size: 2.4rem;
      font-weight: 800;
      line-height: 1.1;
  }}
  .metric-card .etiqueta {{
      font-size: 0.88rem;
      color: #666;
      margin-top: 4px;
  }}

  .alerta-card {{
      background: white;
      border-left: 5px solid {COLORES['error']};
      border-radius: 0 12px 12px 0;
      padding: 14px 18px;
      margin: 8px 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .alerta-card.medio {{
      border-left-color: {COLORES['secundario']};
  }}

  .seccion-titulo {{
      color: {COLORES['primario']};
      font-size: 1.2rem;
      font-weight: 700;
      margin: 24px 0 10px 0;
      padding-bottom: 6px;
      border-bottom: 2px solid {COLORES['primario']}33;
  }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------------------------

col_tit, col_modo = st.columns([4, 1])

with col_tit:
    st.markdown(f"""
    # 👨‍🏫 Dashboard del Profesor
    **{NOMBRE_APP}** — Panel de seguimiento estudiantil
    """)

with col_modo:
    modo_demo = st.toggle("Modo demo", value=True, help="Activa datos de ejemplo para explorar el dashboard")

if modo_demo:
    st.info("📊 **Modo demo activo** — Estás viendo datos de ejemplo. Desactívalo para ver datos reales de tus estudiantes.")

# ---------------------------------------------------------------------------
# FILTROS
# ---------------------------------------------------------------------------

col_grado, col_riesgo, _ = st.columns([2, 2, 4])

with col_grado:
    grado_filtro = st.selectbox(
        "Filtrar por grado",
        options=[None, 7, 8, 9, 10, 11],
        format_func=lambda g: "Todos los grados" if g is None else f"Grado {g}",
    )

with col_riesgo:
    nivel_filtro = st.selectbox(
        "Filtrar por riesgo",
        options=[None, "ALTO", "MEDIO", "BAJO"],
        format_func=lambda n: "Todos los niveles" if n is None else n,
    )

# ---------------------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------------------

df_clase   = cargar_resumen_clase(grado=grado_filtro, demo=modo_demo)
df_casos   = cargar_rendimiento_casos(demo=modo_demo)
metricas   = metricas_globales(df_clase)

# Aplicar filtro de nivel de riesgo
if nivel_filtro and not df_clase.empty:
    df_clase = df_clase[df_clase["riesgo_nivel"] == nivel_filtro]

# ---------------------------------------------------------------------------
# SECCIÓN 1: TARJETAS DE MÉTRICAS GLOBALES
# ---------------------------------------------------------------------------

st.markdown('<p class="seccion-titulo">📊 Resumen de la clase</p>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

tarjetas = [
    (c1, metricas["total_estudiantes"], "Estudiantes",         COLORES["primario"]),
    (c2, f'{metricas["precision_promedio"]}%', "Precisión promedio", COLORES["acento"]),
    (c3, metricas["en_riesgo_alto"],    "En riesgo ALTO",      COLORES["error"]),
    (c4, metricas["en_riesgo_medio"],   "En riesgo MEDIO",     COLORES["secundario"]),
    (c5, metricas["activos_hoy"],       "Activos hoy",         COLORES["primario"]),
]

for col, valor, etiqueta, color in tarjetas:
    with col:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="valor" style="color:{color}">{valor}</div>'
            f'<div class="etiqueta">{etiqueta}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# SECCIÓN 2: TABLA COMPLETA DE ESTUDIANTES
# ---------------------------------------------------------------------------

st.markdown('<p class="seccion-titulo">👥 Listado de estudiantes</p>', unsafe_allow_html=True)

if df_clase.empty:
    st.warning("No hay estudiantes registrados aún. Activa el modo demo para explorar el dashboard.")
else:
    # Preparar tabla para mostrar (columnas seleccionadas y renombradas)
    df_tabla = df_clase[[
        "nombre", "grado", "total_respuestas", "precision_pct",
        "pistas_promedio", "tiempo_promedio", "puntos_totales",
        "riesgo_nivel", "riesgo_puntaje",
    ]].copy()

    df_tabla.columns = [
        "Nombre", "Grado", "Ejercicios", "Precisión (%)",
        "Pistas/ej.", "Tiempo prom. (s)", "Puntos",
        "Nivel de riesgo", "Puntaje riesgo",
    ]

    # Colorear la columna de riesgo
    def _color_riesgo(val):
        colores = {"ALTO": "#FDEDEC", "MEDIO": "#FEF9E7", "BAJO": "#EAFAF1"}
        return f"background-color: {colores.get(val, 'white')}"

    st.dataframe(
        df_tabla.style.applymap(_color_riesgo, subset=["Nivel de riesgo"]),
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------------------------------------------------------
# SECCIÓN 3: ALERTAS DE RIESGO
# ---------------------------------------------------------------------------

st.markdown('<p class="seccion-titulo">🚨 Alertas de riesgo</p>', unsafe_allow_html=True)

if not df_clase.empty:
    en_riesgo = df_clase[df_clase["riesgo_nivel"].isin(["ALTO", "MEDIO"])]

    if en_riesgo.empty:
        st.success("✅ Ningún estudiante presenta señales de riesgo en este momento.")
    else:
        for _, row in en_riesgo.iterrows():
            clase_css = "alerta-card" if row["riesgo_nivel"] == "ALTO" else "alerta-card medio"
            emoji     = "🔴" if row["riesgo_nivel"] == "ALTO" else "🟡"

            factores_html = "".join(
                f"<li>{f}</li>" for f in row["riesgo_factores"]
            )

            st.markdown(
                f'<div class="{clase_css}">'
                f'<strong>{emoji} {row["nombre"]}</strong> — Grado {row["grado"]} '
                f'| Riesgo: <strong>{row["riesgo_nivel"]}</strong> ({row["riesgo_puntaje"]}/100)<br>'
                f'<ul style="margin:6px 0 4px 0; font-size:0.9rem; color:#444">{factores_html}</ul>'
                f'<em style="font-size:0.88rem; color:#555">💡 {row["recomendacion"]}</em>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------------------
# SECCIÓN 4: RENDIMIENTO POR CASO DE FACTORIZACIÓN
# ---------------------------------------------------------------------------

st.markdown('<p class="seccion-titulo">📐 Rendimiento por caso de factorización</p>', unsafe_allow_html=True)

if not df_casos.empty:
    col_bar, col_radar = st.columns(2)

    with col_bar:
        fig_bar = px.bar(
            df_casos.sort_values("precision_pct"),
            x="precision_pct",
            y="nombre_caso",
            orientation="h",
            color="precision_pct",
            color_continuous_scale=["#E74C3C", "#F39C12", "#27AE60"],
            range_color=[0, 100],
            labels={"precision_pct": "Precisión (%)", "nombre_caso": ""},
            title="Precisión por tipo de caso",
            text="precision_pct",
        )
        fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_bar.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=350,
            margin=dict(l=10, r=30, t=40, b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_radar:
        # Gráfico de pistas promedio — muestra dónde hay más frustración
        fig_pistas = px.bar(
            df_casos.sort_values("pistas_promedio", ascending=False),
            x="nombre_caso",
            y="pistas_promedio",
            color="pistas_promedio",
            color_continuous_scale=["#27AE60", "#F39C12", "#E74C3C"],
            labels={"pistas_promedio": "Pistas promedio", "nombre_caso": ""},
            title="Pistas usadas por caso (mayor = más dificultad)",
        )
        fig_pistas.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=350,
            xaxis_tickangle=-30,
            margin=dict(l=10, r=10, t=40, b=60),
        )
        st.plotly_chart(fig_pistas, use_container_width=True)

# ---------------------------------------------------------------------------
# SECCIÓN 5: DETALLE INDIVIDUAL
# ---------------------------------------------------------------------------

st.markdown('<p class="seccion-titulo">🔍 Detalle individual</p>', unsafe_allow_html=True)

if not df_clase.empty:
    nombres_opciones = df_clase["nombre"].tolist()
    nombre_sel = st.selectbox("Selecciona un estudiante", options=nombres_opciones)

    fila_sel = df_clase[df_clase["nombre"] == nombre_sel].iloc[0]
    eid_sel  = fila_sel.get("estudiante_id")

    # Métricas del estudiante seleccionado
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Precisión", f'{fila_sel["precision_pct"]}%')
    col_m2.metric("Ejercicios", int(fila_sel["total_respuestas"]))
    col_m3.metric("Puntos", int(fila_sel["puntos_totales"]))
    col_m4.metric("Nivel de riesgo", fila_sel["riesgo_nivel"])

    # Curva de aprendizaje
    df_prog = cargar_progreso_estudiante(eid_sel, demo=modo_demo)

    if not df_prog.empty:
        fig_prog = go.Figure()

        # Línea de puntos acumulados
        fig_prog.add_trace(go.Scatter(
            x=df_prog["numero"],
            y=df_prog["puntos_acumulados"],
            mode="lines+markers",
            name="Puntos acumulados",
            line=dict(color=COLORES["primario"], width=2),
            marker=dict(
                color=[COLORES["acento"] if c else COLORES["error"]
                       for c in df_prog["fue_correcta"]],
                size=8,
            ),
        ))

        fig_prog.update_layout(
            title=f"Curva de aprendizaje — {nombre_sel}",
            xaxis_title="Ejercicio N°",
            yaxis_title="Puntos acumulados",
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=320,
            legend=dict(orientation="h", y=-0.2),
            margin=dict(l=10, r=10, t=40, b=10),
        )

        # Anotación de colores
        fig_prog.add_annotation(
            text="● Verde = correcto  ● Rojo = incorrecto",
            xref="paper", yref="paper",
            x=0.01, y=1.08, showarrow=False,
            font=dict(size=11, color="#666"),
        )

        st.plotly_chart(fig_prog, use_container_width=True)

    # Factores de riesgo del estudiante
    if fila_sel["riesgo_nivel"] != "BAJO":
        with st.expander(f"🔎 Factores de riesgo detectados para {nombre_sel}"):
            for factor in fila_sel["riesgo_factores"]:
                st.markdown(f"- {factor}")
            st.markdown(f"**Recomendación:** {fila_sel['recomendacion']}")

# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------

st.markdown("---")
st.caption(
    f"**{NOMBRE_APP}** — Dashboard del Profesor  |  "
    "Datos actualizados en tiempo real  |  "
    "Puente Lógico SAS BIC © 2026"
)
