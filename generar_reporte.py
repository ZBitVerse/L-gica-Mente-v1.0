"""
generar_reporte.py — Puente Lógico SAS BIC
==========================================
Genera el documento PDF de resumen del proyecto.
Ejecutar con: python generar_reporte.py
"""

from fpdf import FPDF
from datetime import date
import os

AZUL_OSCURO = (27, 79, 114)
DORADO      = (243, 156, 18)
GRIS_TEXTO  = (44, 62, 80)
GRIS_SUAVE  = (236, 240, 241)
VERDE       = (39, 174, 96)
ROJO        = (231, 76, 60)
BLANCO      = (255, 255, 255)


class PDF(FPDF):

    def header(self):
        # Banda superior azul
        self.set_fill_color(*AZUL_OSCURO)
        self.rect(0, 0, 210, 14, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*BLANCO)
        self.set_xy(10, 3)
        self.cell(0, 8, "Puente Lógico SAS BIC  —  Documentación del Proyecto", align="L")
        self.set_xy(0, 3)
        self.cell(200, 8, f"Fecha: {date.today().strftime('%d/%m/%Y')}", align="R")
        self.ln(12)

    def footer(self):
        self.set_y(-13)
        self.set_fill_color(*AZUL_OSCURO)
        self.rect(0, 284, 210, 14, "F")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*BLANCO)
        self.cell(0, 10, f"Página {self.page_no()} | Confidencial — Puente Lógico SAS BIC © 2026", align="C")

    # ── Helpers de formato ───────────────────────────────────────────────

    def titulo_seccion(self, numero: str, texto: str):
        """Título principal de sección con banda de color."""
        self.ln(6)
        self.set_fill_color(*AZUL_OSCURO)
        self.set_text_color(*BLANCO)
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 10, f"  {numero}. {texto}", fill=True, ln=True)
        self.ln(3)
        self.set_text_color(*GRIS_TEXTO)

    def subtitulo(self, texto: str):
        """Subtítulo con línea dorada."""
        self.ln(4)
        self.set_draw_color(*DORADO)
        self.set_line_width(0.8)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*AZUL_OSCURO)
        self.cell(0, 7, texto, ln=True)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(3)
        self.set_text_color(*GRIS_TEXTO)
        self.set_line_width(0.2)

    def parrafo(self, texto: str):
        """Párrafo normal."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GRIS_TEXTO)
        self.multi_cell(0, 6, texto)
        self.ln(2)

    def bullet(self, texto: str, color=AZUL_OSCURO):
        """Ítem de lista con viñeta de color."""
        self.set_fill_color(*color)
        self.set_xy(self.get_x() + 6, self.get_y())
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*color)
        self.cell(6, 6, "•")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GRIS_TEXTO)
        self.multi_cell(174, 6, texto)

    def caja_info(self, titulo: str, contenido: str, color=GRIS_SUAVE, borde=AZUL_OSCURO):
        """Caja con fondo de color para destacar información."""
        self.ln(3)
        self.set_fill_color(*color)
        self.set_draw_color(*borde)
        self.set_line_width(0.5)
        x, y = self.get_x(), self.get_y()
        # Calcular altura del contenido
        self.set_font("Helvetica", "", 9)
        lines = self.multi_cell(176, 5, contenido, dry_run=True, output="LINES")
        alto = len(lines) * 5 + 14
        self.rect(10, y, 190, alto, "FD")
        self.set_xy(14, y + 4)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*borde)
        self.cell(0, 5, titulo, ln=True)
        self.set_xy(14, self.get_y())
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GRIS_TEXTO)
        self.multi_cell(176, 5, contenido)
        self.ln(4)

    def tabla_dos_col(self, filas: list[tuple], ancho1=60, ancho2=130):
        """Tabla sencilla de dos columnas."""
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*AZUL_OSCURO)
        self.set_text_color(*BLANCO)
        self.cell(ancho1, 7, filas[0][0], fill=True, border=1)
        self.cell(ancho2, 7, filas[0][1], fill=True, border=1, ln=True)
        for i, (col1, col2) in enumerate(filas[1:]):
            fill = i % 2 == 0
            self.set_fill_color(235, 242, 250) if fill else self.set_fill_color(*BLANCO)
            self.set_text_color(*GRIS_TEXTO)
            self.set_font("Helvetica", "", 9)
            self.cell(ancho1, 6, col1, fill=True, border=1)
            self.cell(ancho2, 6, col2, fill=True, border=1, ln=True)
        self.ln(4)

    def pagina_titulo(self):
        """Página de portada."""
        # Fondo azul superior
        self.set_fill_color(*AZUL_OSCURO)
        self.rect(0, 0, 210, 100, "F")

        # Acento dorado
        self.set_fill_color(*DORADO)
        self.rect(0, 100, 210, 4, "F")

        # Logo textual
        self.set_font("Helvetica", "B", 48)
        self.set_text_color(*DORADO)
        self.set_xy(0, 22)
        self.cell(210, 20, "🧮", align="C", ln=True)

        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*BLANCO)
        self.set_xy(0, 48)
        self.cell(210, 14, "PUENTE LÓGICO SAS BIC", align="C", ln=True)

        self.set_font("Helvetica", "", 13)
        self.set_text_color(180, 210, 240)
        self.set_xy(0, 64)
        self.cell(210, 8, "Tecnología educativa para reducir la deserción escolar", align="C", ln=True)
        self.set_xy(0, 74)
        self.cell(210, 8, "en matemáticas — Colombia", align="C", ln=True)

        # Subtítulo del documento
        self.set_fill_color(255, 255, 255)
        self.set_xy(30, 112)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*AZUL_OSCURO)
        self.cell(150, 12, "Documentación Técnica del Proyecto", align="C", ln=True)

        self.set_font("Helvetica", "", 11)
        self.set_text_color(100, 100, 100)
        self.set_xy(0, 130)
        self.cell(210, 8, f"Sesión de desarrollo: {date.today().strftime('%d de %B de %Y')}", align="C", ln=True)
        self.set_xy(0, 140)
        self.cell(210, 8, "Guía para principiantes — Paso a paso", align="C", ln=True)

        # Datos de contacto
        self.set_fill_color(*GRIS_SUAVE)
        self.rect(25, 180, 160, 55, "F")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*AZUL_OSCURO)
        self.set_xy(0, 185)
        self.cell(210, 8, "Información del Proyecto", align="C", ln=True)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GRIS_TEXTO)
        info = [
            ("Empresa",      "Puente Lógico SAS BIC"),
            ("GitHub",       "github.com/ZBitVerse/L-gica-Mente-v1.0"),
            ("App en vivo",  "puente-logico-app-gdd5od5pda-uc.a.run.app"),
            ("Cloud",        "Google Cloud Run — Proyecto: puente-logico-sas-bic"),
            ("Tecnologías",  "Python · Streamlit · SymPy · SQLite · Docker"),
        ]
        for label, valor in info:
            self.set_xy(35, self.get_y())
            self.set_font("Helvetica", "B", 9)
            self.cell(35, 7, label + ":", ln=False)
            self.set_font("Helvetica", "", 9)
            self.cell(0, 7, valor, ln=True)

        self.add_page()


# ============================================================================
# GENERACIÓN DEL DOCUMENTO
# ============================================================================

def generar():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(10, 18, 10)

    # ── PORTADA ──────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.pagina_titulo()

    # ── 1. EL PROBLEMA ───────────────────────────────────────────────────
    pdf.titulo_seccion("1", "El Problema: Deserción Escolar en Matemáticas")

    pdf.parrafo(
        "Colombia enfrenta un problema crítico: miles de estudiantes abandonan el colegio cada año, "
        "y las matemáticas son una de las principales causas. Cuando un estudiante no entiende álgebra "
        "en grado 8°, comienza a perder el hilo del curso, se frustra, y eventualmente deja de asistir."
    )

    pdf.subtitulo("¿Por qué es tan difícil la factorización?")
    pdf.parrafo(
        "La factorización algebraica aparece en grado 8° y requiere reconocer patrones abstractos. "
        "Sin práctica repetida y retroalimentación inmediata, el estudiante no logra automatizar "
        "el proceso. Los libros de texto no son suficientes porque:"
    )
    for item in [
        "No dan retroalimentación instantánea — el estudiante no sabe si está bien hasta el día siguiente.",
        "Son lineales — no se adaptan al ritmo de cada estudiante.",
        "No motivan — aprender de un libro no genera el mismo compromiso que un videojuego.",
    ]:
        pdf.bullet(item)

    pdf.caja_info(
        "Dato clave del MEN (Ministerio de Educación Nacional):",
        "La tasa de deserción escolar en Colombia en educación básica secundaria supera el 5% anual. "
        "Las áreas STEM (ciencias y matemáticas) concentran la mayor parte de las dificultades "
        "académicas reportadas por los estudiantes como razón para abandonar el estudio.",
        color=(235, 245, 255), borde=AZUL_OSCURO
    )

    # ── 2. LA SOLUCIÓN ───────────────────────────────────────────────────
    pdf.titulo_seccion("2", "La Solución: Puente Lógico")

    pdf.parrafo(
        "Puente Lógico es una aplicación web educativa que convierte el aprendizaje de la "
        "factorización algebraica en un juego. El estudiante resuelve ejercicios, gana puntos, "
        "sube de nivel y recibe retroalimentación inmediata. El profesor puede ver en tiempo real "
        "quién está progresando y quién necesita ayuda."
    )

    pdf.subtitulo("Público objetivo")
    pdf.tabla_dos_col([
        ("Quién",              "Rol en la aplicación"),
        ("Estudiantes grado 7°-9°  (12-15 años)", "Juegan, practican, suben de nivel"),
        ("Profesores de matemáticas",              "Monitorean progreso y reciben alertas de riesgo"),
        ("Colegios colombianos",                   "Implementan la herramienta como apoyo pedagógico"),
    ])

    pdf.subtitulo("Metodología pedagógica")
    for item in [
        "Aprendizaje Basado en Problemas (ABP): el estudiante ve el ejercicio primero, luego aprende el método.",
        "Scaffolding: pistas progresivas que guían sin dar la respuesta directa.",
        "Gamificación: puntos, rachas, niveles y bonos que mantienen la motivación.",
        "Retroalimentación inmediata: el sistema verifica algebraicamente, no por texto exacto.",
    ]:
        pdf.bullet(item, color=VERDE)

    # ── 3. ARQUITECTURA ──────────────────────────────────────────────────
    pdf.titulo_seccion("3", "Arquitectura del Proyecto (Los Archivos)")

    pdf.parrafo(
        "Piensa en el proyecto como una casa: cada archivo es una habitación con una función específica. "
        "Aquí están todos los archivos que creamos y qué hace cada uno:"
    )

    pdf.tabla_dos_col([
        ("Archivo",               "¿Qué hace?"),
        ("config.py",             "Configuración central: casos de factorización, puntos, colores, parámetros del MEN"),
        ("generador_algebra.py",  "Motor principal: genera ejercicios, valida respuestas, crea pistas paso a paso"),
        ("main.py",               "Interfaz del juego: pantallas de bienvenida, juego y resultado final"),
        ("estudiantes.py",        "Base de datos: guarda estudiantes, sesiones y respuestas en SQLite"),
        ("motor_riesgo.py",       "Inteligencia: calcula si un estudiante está en riesgo de deserción"),
        ("analitica.py",          "Analítica: transforma datos en gráficos y métricas para el profesor"),
        ("pages/01_profesor.py",  "Dashboard del profesor: alertas, gráficos y seguimiento individual"),
        ("requirements.txt",      "Lista de librerías Python que necesita el proyecto"),
        ("dockerfile",            "Instrucciones para empacar la app en un contenedor Docker"),
        ("cloudbuild.yaml",       "Pipeline de despliegue automático en Google Cloud"),
        (".gitignore",            "Le dice a Git qué archivos NO subir a GitHub"),
    ])

    # ── 4. EL MOTOR ALGEBRAICO ───────────────────────────────────────────
    pdf.titulo_seccion("4", "El Motor Algebraico (generador_algebra.py)")

    pdf.parrafo(
        "Este es el corazón del proyecto. Usa SymPy, una librería de matemáticas simbólicas para Python, "
        "que permite trabajar con álgebra exactamente como lo haría un humano — no con números aproximados."
    )

    pdf.subtitulo("Los 7 casos de factorización que cubre el motor")
    pdf.tabla_dos_col([
        ("Caso",                        "Fórmula"),
        ("1. Factor Común",              "ax + ay = a(x + y)"),
        ("2. Diferencia de Cuadrados",   "a² - b² = (a+b)(a-b)"),
        ("3. Trinomio Cuadrado Perfecto","a² ± 2ab + b² = (a ± b)²"),
        ("4. Trinomio Simple",           "x² + bx + c = (x+p)(x+q)"),
        ("5. Trinomio Complejo",         "ax² + bx + c  (método aspa doble)"),
        ("6. Suma de Cubos",             "a³ + b³ = (a+b)(a²-ab+b²)"),
        ("7. Diferencia de Cubos",       "a³ - b³ = (a-b)(a²+ab+b²)"),
    ])

    pdf.subtitulo("¿Cómo valida las respuestas?")
    pdf.parrafo(
        "En lugar de comparar texto (lo que sería muy limitado), el motor expande algebraicamente "
        "la respuesta del estudiante y la compara con la expresión original. Esto significa que:"
    )
    for item in [
        "(x+3)*(x-3)  y  (x-3)*(x+3)  se consideran IGUAL — el orden no importa.",
        "3*(2x+1)  y  (6x+3)  se consideran IGUAL — son equivalentes.",
        "El estudiante tiene libertad de escribir la respuesta a su manera.",
    ]:
        pdf.bullet(item, color=VERDE)

    pdf.subtitulo("Sistema de pistas progresivas")
    pdf.parrafo(
        "Cada ejercicio tiene 3 pistas. La filosofía es socrática: no dar la respuesta, "
        "sino guiar al estudiante a descubrirla. Cada pista usada descuenta 5 puntos."
    )
    pdf.tabla_dos_col([
        ("Pista",    "Qué revela"),
        ("Pista 1",  "Orientación general — qué buscar en la expresión"),
        ("Pista 2",  "El nombre del caso y su fórmula"),
        ("Pista 3",  "El primer paso concreto de la solución"),
    ], ancho1=40, ancho2=150)

    # ── 5. EL JUEGO ──────────────────────────────────────────────────────
    pdf.titulo_seccion("5", "La Interfaz del Juego (main.py)")

    pdf.parrafo(
        "La interfaz fue construida con Streamlit, un framework de Python que permite crear "
        "aplicaciones web sin necesidad de escribir HTML o JavaScript. El juego tiene 3 pantallas:"
    )

    pdf.subtitulo("Pantalla 1 — Bienvenida")
    for item in [
        "El estudiante escribe su nombre y selecciona su grado escolar.",
        "Se muestran los 4 tipos de factorización que aprenderá.",
        "Diseño oscuro con fondo degradado y logo animado.",
    ]:
        pdf.bullet(item)

    pdf.subtitulo("Pantalla 2 — Juego")
    for item in [
        "Barra de XP animada que muestra el progreso hacia el siguiente nivel.",
        "La expresión algebraica se muestra grande y legible (x² - 9, no x**2 - 9).",
        "Badge dorado con animación cuando el estudiante tiene racha de 3+ correctas.",
        "Sistema de pistas desbloqueable (3 niveles).",
        "Validación algebraica de la respuesta con retroalimentación inmediata.",
        "Solución paso a paso visible después de responder.",
    ]:
        pdf.bullet(item)

    pdf.subtitulo("Pantalla 3 — Resultado Final")
    for item in [
        "Trofeo según precisión: 🏆 (>80%), 🥈 (>60%), 💪 (menor).",
        "Estadísticas: puntos totales, correctas, precisión y racha máxima.",
        "Opción de jugar de nuevo o cambiar jugador.",
    ]:
        pdf.bullet(item)

    pdf.subtitulo("Sistema de puntos y niveles")
    pdf.tabla_dos_col([
        ("Nivel",           "Puntos requeridos"),
        ("🌱 Explorador",    "0 - 99 puntos"),
        ("📚 Aprendiz",      "100 - 299 puntos"),
        ("🔢 Calculista",    "300 - 599 puntos"),
        ("🧮 Algebraísta",   "600 - 999 puntos"),
        ("🏆 Maestro Lógico","1,000+ puntos"),
    ], ancho1=80, ancho2=110)

    pdf.caja_info(
        "Bonos adicionales de puntos:",
        "• Sin pistas: +10 pts     • Velocidad (< 30 seg): +5 pts\n"
        "• Racha de 3:  +15 pts    • Racha de 5: +30 pts    • Racha de 10: +75 pts",
        color=(240, 255, 240), borde=VERDE
    )

    # ── 6. BASE DE DATOS ─────────────────────────────────────────────────
    pdf.titulo_seccion("6", "La Base de Datos (estudiantes.py)")

    pdf.parrafo(
        "Usamos SQLite, una base de datos que funciona como un solo archivo en el disco. "
        "No requiere configurar ningún servidor — el archivo puente_logico.db se crea "
        "automáticamente la primera vez que se ejecuta la aplicación."
    )

    pdf.subtitulo("Las 3 tablas de la base de datos")

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*AZUL_OSCURO)
    pdf.cell(0, 7, "Tabla: estudiantes", ln=True)
    pdf.tabla_dos_col([
        ("Campo",        "¿Qué guarda?"),
        ("id",           "Número único del estudiante"),
        ("nombre",       "Nombre completo"),
        ("grado",        "Grado escolar (7, 8, 9...)"),
        ("ultima_vez",   "Cuándo jugó por última vez"),
    ], ancho1=50, ancho2=140)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*AZUL_OSCURO)
    pdf.cell(0, 7, "Tabla: sesiones", ln=True)
    pdf.tabla_dos_col([
        ("Campo",          "¿Qué guarda?"),
        ("estudiante_id",  "A qué estudiante pertenece"),
        ("iniciada_en",    "Cuándo empezó a jugar"),
        ("puntos_sesion",  "Puntos ganados en esa sesión"),
        ("racha_max",      "Mayor racha alcanzada"),
    ], ancho1=50, ancho2=140)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*AZUL_OSCURO)
    pdf.cell(0, 7, "Tabla: respuestas", ln=True)
    pdf.tabla_dos_col([
        ("Campo",            "¿Qué guarda?"),
        ("caso_id",          "Tipo de factorización (factor_comun, etc.)"),
        ("expresion",        "La expresión que se le mostró"),
        ("fue_correcta",     "Si respondió bien (1) o mal (0)"),
        ("pistas_usadas",    "Cuántas pistas pidió"),
        ("tiempo_segundos",  "Cuánto tardó en responder"),
        ("puntos_ganados",   "Puntos que ganó con esa respuesta"),
    ], ancho1=50, ancho2=140)

    # ── 7. MOTOR DE RIESGO ───────────────────────────────────────────────
    pdf.titulo_seccion("7", "Motor de Riesgo de Deserción (motor_riesgo.py)")

    pdf.parrafo(
        "Este módulo analiza el comportamiento del estudiante dentro del juego y calcula "
        "un puntaje de riesgo de 0 a 100. Está basado en señales que la investigación del MEN "
        "identifica como precursores del abandono escolar."
    )

    pdf.subtitulo("Los 4 factores de riesgo")
    pdf.tabla_dos_col([
        ("Factor",                    "Peso máximo  /  Cuándo se activa"),
        ("Precisión baja",            "40 pts  /  Menos del 40% de respuestas correctas"),
        ("Días sin actividad",        "30 pts  /  Más de 10 días sin jugar"),
        ("Uso excesivo de pistas",    "15 pts  /  Promedio de 2.5+ pistas por ejercicio"),
        ("Tiempo muy alto",           "15 pts  /  Más de 120 segundos por respuesta"),
    ])

    pdf.subtitulo("Niveles de riesgo")
    pdf.tabla_dos_col([
        ("Nivel",     "Puntaje  /  Acción recomendada"),
        ("BAJO",      "0-39    /  Seguimiento regular"),
        ("MEDIO",     "40-69   /  Ejercicios adicionales, atención preventiva"),
        ("ALTO",      "70-100  /  Contactar estudiante y acudiente esta semana"),
    ], ancho1=30, ancho2=160)

    # ── 8. DASHBOARD DEL PROFESOR ────────────────────────────────────────
    pdf.titulo_seccion("8", "Dashboard del Profesor (pages/01_profesor.py)")

    pdf.parrafo(
        "El profesor accede a una pantalla separada en la misma aplicación. "
        "Puede ver en tiempo real el estado de todos sus estudiantes sin necesidad de "
        "calificar manualmente ni esperar a un examen."
    )

    pdf.subtitulo("Secciones del dashboard")
    for item in [
        "Tarjetas de resumen: total de estudiantes, cuántos están en riesgo alto/medio, precisión promedio de la clase y activos hoy.",
        "Tabla completa: todos los estudiantes con su precisión, ejercicios, pistas usadas, tiempo promedio, puntos y nivel de riesgo (coloreado).",
        "Alertas: lista detallada de estudiantes en riesgo ALTO o MEDIO, con los factores exactos que generaron la alerta y una recomendación de acción.",
        "Rendimiento por caso: gráfico de barras que muestra en qué tipo de factorización tiene más dificultades la clase.",
        "Detalle individual: selecciona un estudiante y ve su curva de aprendizaje (puntos acumulados en el tiempo).",
        "Modo demo: datos de ejemplo precargados para presentar el sistema sin necesitar estudiantes reales.",
    ]:
        pdf.bullet(item)

    # ── 9. GOOGLE CLOUD ──────────────────────────────────────────────────
    pdf.titulo_seccion("9", "Despliegue en Google Cloud")

    pdf.parrafo(
        "La aplicación está desplegada en Google Cloud Run, un servicio que ejecuta "
        "la app dentro de un contenedor Docker y la pone disponible en internet. "
        "La gran ventaja es que escala a cero — si nadie está usando la app, no se paga nada."
    )

    pdf.subtitulo("El flujo de despliegue automático")
    pdf.parrafo(
        "1. El desarrollador hace cambios en el código.\n"
        "2. Ejecuta: git add . && git commit -m 'descripción' && git push\n"
        "3. GitHub recibe el push y notifica a Google Cloud Build.\n"
        "4. Cloud Build construye la imagen Docker con el nuevo código.\n"
        "5. Sube la imagen a Artifact Registry (bodega de imágenes).\n"
        "6. Despliega la nueva versión en Cloud Run sin tiempo de inactividad.\n"
        "7. La app está actualizada en menos de 5 minutos."
    )

    pdf.subtitulo("Componentes de GCP configurados")
    pdf.tabla_dos_col([
        ("Servicio GCP",         "Función"),
        ("Cloud Run",            "Ejecuta la app en internet — escala automáticamente"),
        ("Cloud Build",          "Pipeline CI/CD — construye y despliega en cada push a main"),
        ("Artifact Registry",    "Almacena las imágenes Docker del proyecto"),
        ("Cloud Storage",        "Guarda archivos temporales del proceso de build"),
    ])

    pdf.subtitulo("Costos estimados (fase MVP)")
    pdf.tabla_dos_col([
        ("Escenario",                          "Costo mensual"),
        ("MVP — 1 colegio (50-100 estudiantes)", "$ 0 — $ 2 USD"),
        ("Crecimiento — 5 colegios (500 est.)",  "$ 2 — $ 10 USD"),
        ("Escala — 50 colegios (5,000 est.)",    "$ 20 — $ 60 USD"),
    ])

    pdf.caja_info(
        "URL de la aplicación en producción:",
        "https://puente-logico-app-gdd5od5pda-uc.a.run.app\n"
        "Dashboard del profesor: /01_profesor",
        color=(235, 245, 255), borde=AZUL_OSCURO
    )

    # ── 10. GITHUB ───────────────────────────────────────────────────────
    pdf.titulo_seccion("10", "Control de Versiones con GitHub")

    pdf.parrafo(
        "GitHub es el sistema que guarda el historial completo del código. "
        "Cada vez que hacemos un cambio, queda registrado con fecha, autor y descripción. "
        "Si algo sale mal, podemos volver a una versión anterior en segundos."
    )

    pdf.subtitulo("Comandos básicos de Git (los que usamos)")
    pdf.tabla_dos_col([
        ("Comando",                      "¿Qué hace?"),
        ("git add .",                     "Prepara todos los archivos modificados para guardar"),
        ("git commit -m 'descripción'",   "Guarda los cambios con un mensaje explicativo"),
        ("git push",                      "Sube los cambios a GitHub (y activa el deploy)"),
        ("git status",                    "Muestra qué archivos cambiaron"),
        ("git log --oneline",             "Muestra el historial de cambios"),
    ])

    pdf.caja_info(
        "Repositorio del proyecto:",
        "https://github.com/ZBitVerse/L-gica-Mente-v1.0\n"
        "Rama principal: main  |  Trigger automático: activo",
        color=(235, 245, 255), borde=AZUL_OSCURO
    )

    # ── 11. PRÓXIMOS PASOS ───────────────────────────────────────────────
    pdf.titulo_seccion("11", "Próximos Pasos — Roadmap del Proyecto")

    pdf.subtitulo("Fase 2 — Escuela (próximos 3-4 meses)")
    for item in [
        "Migración de SQLite a Cloud SQL (PostgreSQL) para persistencia en producción.",
        "Sistema de login con roles: estudiante / profesor.",
        "Integración de la persistencia en el juego (guardar cada respuesta en la DB).",
        "Exportación de reportes en PDF para el docente.",
        "Alertas por correo al profesor cuando un estudiante entra en riesgo ALTO.",
    ]:
        pdf.bullet(item)

    pdf.subtitulo("Fase 3 — Escalabilidad (4-6 meses)")
    for item in [
        "API REST para conectar apps móviles (Android/iOS) en el futuro.",
        "Integración con plataformas del MEN y secretarías de educación.",
        "Panel administrativo para colegios (gestión de cursos y grupos).",
        "Análisis predictivo de deserción con machine learning.",
        "Dominio personalizado: app.puentelogico.co",
    ]:
        pdf.bullet(item)

    pdf.caja_info(
        "Configurar alerta de presupuesto en GCP:",
        "Ve a console.cloud.google.com → Facturación → Presupuestos y alertas → Crear presupuesto.\n"
        "Proyecto: puente-logico-sas-bic  |  Importe sugerido: $10 USD/mes\n"
        "Configura alertas al 50%, 90% y 100% del presupuesto.",
        color=(255, 248, 230), borde=DORADO
    )

    # ── 12. GLOSARIO ─────────────────────────────────────────────────────
    pdf.titulo_seccion("12", "Glosario de Términos Técnicos")

    terminos = [
        ("Python",         "Lenguaje de programación. Como el idioma en que está escrito el proyecto."),
        ("Streamlit",      "Herramienta que convierte código Python en una app web visual."),
        ("SymPy",          "Librería de matemáticas simbólicas para Python — hace álgebra real."),
        ("SQLite",         "Base de datos que funciona como un archivo .db en el disco."),
        ("Docker",         "Tecnología que empaca la app con todo lo que necesita para correr en cualquier lugar."),
        ("Git",            "Sistema que guarda el historial completo de cambios del código."),
        ("GitHub",         "Plataforma web donde se almacena el repositorio Git del proyecto."),
        ("Cloud Run",      "Servicio de Google que ejecuta la app en internet de forma automática."),
        ("Cloud Build",    "Servicio de Google que construye y despliega la app automáticamente."),
        ("CI/CD",          "Continuous Integration/Deployment: el deploy se hace solo en cada push."),
        ("Dockerfile",     "Archivo con instrucciones para construir la imagen Docker de la app."),
        ("API",            "Interfaz que permite que dos programas se comuniquen entre sí."),
        ("MVP",            "Minimum Viable Product: la versión mínima funcional del producto."),
        ("MEN",            "Ministerio de Educación Nacional de Colombia."),
    ]

    pdf.tabla_dos_col(
        [("Término", "Definición simple")] + terminos,
        ancho1=45, ancho2=145
    )

    # Guardar
    output = os.path.join(os.path.dirname(__file__), "Puente_Logico_Documentacion.pdf")
    pdf.output(output)
    print(f"PDF generado: {output}")
    return output


if __name__ == "__main__":
    generar()
