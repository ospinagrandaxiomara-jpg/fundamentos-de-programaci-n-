import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración general de la página
st.set_page_config(
    page_title="Dashboard Estudiantes - Colmayor",
    page_icon="🎓",
    layout="wide"
)

# Paleta de colores: https://colorhunt.co/palette/774d78af8eb1b7d0ccf1e3c4
PALETA = ["#774D78", "#AF8EB1", "#B7D0CC", "#F1E3C4"]
COLOR_PRIMARIO = "#774D78"
COLOR_SECUNDARIO = "#AF8EB1"
COLOR_ACENTO = "#B7D0CC"
COLOR_FONDO_CALIDO = "#F1E3C4"
COLOR_TEXTO = "#2E1D2F"

# Estilos CSS personalizados para un acabado ejecutivo de dashboard
st.markdown(f"""
    <style>
        /* Tarjetas de métricas */
        div[data-testid="stMetric"] {{
            background-color: {COLOR_FONDO_CALIDO}45;
            border-left: 5px solid {COLOR_PRIMARIO};
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }}
        div[data-testid="stMetric"] label {{
            color: {COLOR_PRIMARIO};
            font-weight: 600;
        }}
        /* Estilo de las pestañas */
        button[data-baseweb="tab"] {{
            font-size: 16px;
            font-weight: 600;
            color: {COLOR_TEXTO};
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {COLOR_PRIMARIO} !important;
            border-bottom-color: {COLOR_PRIMARIO} !important;
        }}
    </style>
""", unsafe_allow_html=True)

st.title("Dashboard de Estudiantes Matriculados")
st.markdown(f"<span style='color:{COLOR_PRIMARIO}; font-size:18px; font-weight:500;'>Institución Universitaria Colegio Mayor de Antioquia</span>", unsafe_allow_html=True)

# 1. Carga y limpieza de datos con caché
@st.cache_data
def cargar_datos():
    ruta = r"Database\Estudiantes_Matriculados_en_Programas_Académicos_-_Institución_Universitaria_Colegio_Mayor_de_Antioquia_20261126.csv"
    df = pd.read_csv(ruta)
    
    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.upper()
    
    # Limpiar espacios en blanco de columnas de texto
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("NO REGISTRA").astype(str).str.strip()
        
    return df

df = cargar_datos()

def buscar_columna(posibles_nombres):
    for nombre in posibles_nombres:
        if nombre in df.columns:
            return nombre
    return None

COL_INSCRIPCION = buscar_columna(["TIPO INSCRIPCION", "TIPO DE INSCRIPCION", "TIPO_INSCRIPCION"])
COL_PROGRAMA = buscar_columna(["PROGRAMA", "PROGRAMA ACADEMICO", "NOMBRE PROGRAMA"])
COL_SEXO = buscar_columna(["SEXO BIOLOGICO", "SEXO", "GENERO", "SEXO_BIOLOGICO"])

# 2. Filtros entrelazados en la barra lateral (sin Municipios ni Semestres)
st.sidebar.header("Filtros de Búsqueda")
st.sidebar.caption("Las opciones se actualizan dinámicamente según tu selección.")

df_filtrado = df.copy()

def aplicar_filtro_cascada(dataframe, col_name, label):
    if col_name and col_name in dataframe.columns:
        opciones = sorted(dataframe[col_name].unique())
        seleccion = st.sidebar.multiselect(label, options=opciones, default=[])
        if seleccion:
            return dataframe[dataframe[col_name].isin(seleccion)]
    return dataframe

df_filtrado = aplicar_filtro_cascada(df_filtrado, COL_INSCRIPCION, "1. Tipo de Inscripción")
df_filtrado = aplicar_filtro_cascada(df_filtrado, COL_PROGRAMA, "2. Programa Académico")
df_filtrado = aplicar_filtro_cascada(df_filtrado, COL_SEXO, "3. Sexo Biológico")

# KPIs superiores
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric(label="Total Estudiantes Matriculados", value=f"{len(df_filtrado):,}")
with kpi2:
    total_programas = df_filtrado[COL_PROGRAMA].nunique() if COL_PROGRAMA else 0
    st.metric(label="Programas Activos", value=total_programas)
with kpi3:
    total_inscripciones = df_filtrado[COL_INSCRIPCION].nunique() if COL_INSCRIPCION else 0
    st.metric(label="Modalidades de Inscripción", value=total_inscripciones)

st.write("")

# 3. Tabla desplegable
with st.expander("📂 Ver tabla de datos detallados (Click para desplegar)"):
    st.dataframe(df_filtrado, use_container_width=True)

st.divider()

# 4. Función para crear gráficos estilizados
def crear_grafico_profesional(columna, titulo, tipo="bar"):
    if not columna or columna not in df_filtrado.columns:
        st.info(f"No se encontró la columna para: {titulo}")
        return
        
    conteo = df_filtrado[columna].value_counts().reset_index()
    conteo.columns = [columna, "Cantidad"]

    if tipo == "pie":
        fig = px.pie(
            conteo,
            names=columna,
            values="Cantidad",
            title=titulo,
            hole=0.52,
            color_discrete_sequence=PALETA
        )
        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#FFFFFF", width=2.5)),
            pull=[0.02] * len(conteo)
        )
    elif tipo == "hbar":
        conteo = conteo.sort_values(by="Cantidad", ascending=True)
        fig = px.bar(
            conteo,
            x="Cantidad",
            y=columna,
            orientation="h",
            title=titulo,
            text_auto=",",
            color="Cantidad",
            color_continuous_scale=[COLOR_ACENTO, COLOR_SECUNDARIO, COLOR_PRIMARIO]
        )
        fig.update_traces(
            textposition="outside",
            marker_line_width=0,
            cliponaxis=False
        )
        fig.update_coloraxes(showscale=False)
    else:
        fig = px.bar(
            conteo,
            x=columna,
            y="Cantidad",
            title=titulo,
            text_auto=",",
            color=columna,
            color_discrete_sequence=PALETA
        )
        fig.update_traces(
            textposition="outside",
            marker_line_width=0,
            cliponaxis=False
        )
        fig.update_layout(showlegend=False)

    # Estilización general del layout Plotly
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            font=dict(size=18, color=COLOR_PRIMARIO),
            x=0
        ),
        font=dict(family="sans-serif", size=12, color=COLOR_TEXTO),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(241, 227, 196, 0.15)",
        margin=dict(t=60, b=30, l=20, r=40),
        xaxis=dict(
            showgrid=True if tipo == "hbar" else False,
            gridcolor="rgba(119, 77, 120, 0.12)",
            zeroline=False,
            title=""
        ),
        yaxis=dict(
            showgrid=False if tipo == "hbar" else True,
            gridcolor="rgba(119, 77, 120, 0.12)",
            zeroline=False,
            title=""
        ),
        hoverlabel=dict(
            bgcolor=COLOR_PRIMARIO,
            font_size=13,
            font_color="white"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 5. Pestañas por categoría con texto descriptivo corto
st.subheader("Análisis por Categoría")

if df_filtrado.empty:
    st.warning("No hay datos que coincidan con la combinación de filtros seleccionada.")
else:
    tab1, tab2, tab3 = st.tabs([
        "📝 Tipo de Inscripción",
        "🎓 Programa Académico",
        "👥 Sexo Biológico"
    ])

    with tab1:
        st.markdown(
            f"<p style='color:{COLOR_TEXTO}; font-size:15px;'>"
            "Explora las diferentes modalidades de ingreso y vinculación académica bajo las cuales los estudiantes "
            "formalizaron su matrícula en la institución durante el periodo evaluado."
            "</p>",
            unsafe_allow_html=True
        )
        crear_grafico_profesional(COL_INSCRIPCION, "Distribución de Estudiantes por Tipo de Inscripción", tipo="bar")

    with tab2:
        st.markdown(
            f"<p style='color:{COLOR_TEXTO}; font-size:15px;'>"
            "Visualiza la concentración estudiantil a través de la oferta académica institucional, permitiendo identificar "
            "los programas profesionales y tecnológicos con mayor demanda."
            "</p>",
            unsafe_allow_html=True
        )
        crear_grafico_profesional(COL_PROGRAMA, "Estudiantes Matriculados por Programa Académico", tipo="hbar")

    with tab3:
        st.markdown(
            f"<p style='color:{COLOR_TEXTO}; font-size:15px;'>"
            "Analiza la composición demográfica de la población estudiantil según su sexo biológico registrado, "
            "facilitando el seguimiento de la participación y equidad en la comunidad universitaria."
            "</p>",
            unsafe_allow_html=True
        )
        crear_grafico_profesional(COL_SEXO, "Proporción de Estudiantes por Sexo Biológico", tipo="pie")