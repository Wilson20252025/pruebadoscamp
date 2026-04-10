import streamlit as st
import pandas as pd
import io

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Cargador de Datos",
    page_icon="📊",
    layout="wide",
)

# ── Estilos personalizados ───────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    .stApp {
        background-color: #0d0d0d;
        color: #f0f0f0;
    }

    .titulo-hero {
        font-family: 'Syne', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #f0f0f0;
        letter-spacing: -1px;
        line-height: 1.1;
    }

    .titulo-hero span {
        color: #00ff99;
    }

    .subtitulo {
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.3rem;
        letter-spacing: 1px;
    }

    .metric-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-left: 3px solid #00ff99;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        text-align: center;
    }

    .metric-card .valor {
        font-family: 'Space Mono', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: #00ff99;
    }

    .metric-card .label {
        font-size: 0.75rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }

    .col-badge {
        display: inline-block;
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 4px;
        padding: 3px 10px;
        margin: 3px;
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        color: #ccc;
    }

    .col-badge.num { border-color: #00ff99; color: #00ff99; }
    .col-badge.obj { border-color: #ff9900; color: #ff9900; }
    .col-badge.dat { border-color: #00aaff; color: #00aaff; }

    [data-testid="stFileUploader"] {
        background: #111;
        border: 2px dashed #333;
        border-radius: 8px;
        padding: 1rem;
    }

    [data-testid="stSidebar"] {
        background: #111;
        border-right: 1px solid #1e1e1e;
    }

    hr { border-color: #1e1e1e; }

    .stDownloadButton > button {
        background: #00ff99 !important;
        color: #000 !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.4rem 1.2rem !important;
    }

    .stSelectbox label, .stMultiSelect label, .stSlider label, .stTextInput label {
        color: #aaa !important;
        font-size: 0.8rem !important;
        font-family: 'Space Mono', monospace !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Función de carga ─────────────────────────────────────────────────────────
@st.cache_data
def cargar_archivo(archivo_bytes, nombre, sheet_name=0):
    if nombre.endswith(".csv"):
        contenido = archivo_bytes.decode("utf-8", errors="replace")
        sep = ";" if contenido.count(";") > contenido.count(",") else ","
        df = pd.read_csv(io.StringIO(contenido), sep=sep)
    elif nombre.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(archivo_bytes), sheet_name=sheet_name)
    else:
        return None
    return df


def tipo_badge(dtype):
    d = str(dtype)
    if "int" in d or "float" in d:
        return "num"
    elif "datetime" in d:
        return "dat"
    else:
        return "obj"


# ── Encabezado ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 2rem;">
  <div class="titulo-hero">Cargador de <span>Datos</span></div>
  <div class="subtitulo">CSV · XLSX · XLS → DataFrame de Pandas</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Opciones")
    filas_mostrar = st.slider("Filas a mostrar", 5, 100, 20, step=5)
    mostrar_nulos = st.checkbox("Resaltar valores nulos", value=True)
    mostrar_dtypes = st.checkbox("Mostrar tipos de columnas", value=True)
    mostrar_stats = st.checkbox("Estadísticas descriptivas", value=False)
    st.markdown("---")
    st.markdown("""
    <div style='font-family: Space Mono, monospace; font-size: 0.7rem; color: #555; line-height: 1.8;'>
    FORMATOS SOPORTADOS<br>
    ▸ .csv (sep , o ;)<br>
    ▸ .xlsx<br>
    ▸ .xls<br><br>
    ENCODING<br>
    ▸ UTF-8 auto-detectado
    </div>
    """, unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
archivo = st.file_uploader(
    "Arrastra tu archivo aquí o haz clic para seleccionar",
    type=["csv", "xlsx", "xls"],
    label_visibility="visible",
)

if archivo is None:
    st.markdown("""
    <div style='text-align:center; padding: 3rem 0; color: #444;
                font-family: Space Mono, monospace; font-size: 0.8rem;'>
        ↑  Sube un archivo para comenzar
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Leer bytes una sola vez ───────────────────────────────────────────────────
archivo_bytes = archivo.read()
nombre = archivo.name.lower()

# ── Selección de hoja (solo Excel) ───────────────────────────────────────────
sheet_name = 0
if nombre.endswith((".xlsx", ".xls")):
    xf = pd.ExcelFile(io.BytesIO(archivo_bytes))
    hojas = xf.sheet_names
    if len(hojas) > 1:
        sheet_name = st.selectbox("Selecciona la hoja", hojas)
    else:
        sheet_name = hojas[0]
        st.info(f"Hoja única detectada: **{sheet_name}**")

# ── Carga ─────────────────────────────────────────────────────────────────────
df = cargar_archivo(archivo_bytes, nombre, sheet_name=sheet_name)

if df is None:
    st.error("No se pudo leer el archivo.")
    st.stop()

# ── Métricas rápidas ──────────────────────────────────────────────────────────
nulos_total = int(df.isnull().sum().sum())
col_num = sum(1 for d in df.dtypes if "int" in str(d) or "float" in str(d))

m1, m2, m3, m4, m5 = st.columns(5)
for col_st, valor, label in zip(
    [m1, m2, m3, m4, m5],
    [df.shape[0], df.shape[1], col_num, df.shape[1] - col_num, nulos_total],
    ["FILAS", "COLUMNAS", "NUMÉRICAS", "TEXTO / FECHA", "VALORES NULOS"]
):
    with col_st:
        st.markdown(f"""
        <div class="metric-card">
          <div class="valor">{valor:,}</div>
          <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tipos de columnas ─────────────────────────────────────────────────────────
if mostrar_dtypes:
    badges = "".join(
        f'<span class="col-badge {tipo_badge(df[c].dtype)}">{c}<br>'
        f'<small style="opacity:0.6">{df[c].dtype}</small></span>'
        for c in df.columns
    )
    st.markdown(f"**Columnas y tipos**<br>{badges}", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Filtro rápido de columnas ─────────────────────────────────────────────────
with st.expander("🔎 Filtrar columnas a mostrar", expanded=False):
    cols_sel = st.multiselect(
        "Columnas", df.columns.tolist(), default=df.columns.tolist()
    )

# Fix: fuera del with, sin else
df_vista = df[cols_sel] if cols_sel else df

# ── DataFrame principal ───────────────────────────────────────────────────────
st.markdown("#### 📋 DataFrame")

if mostrar_nulos and nulos_total > 0:
    st.dataframe(
        df_vista.head(filas_mostrar).style.highlight_null(color="#3a1a1a"),
        use_container_width=True,
        height=420,
    )
else:
    st.dataframe(df_vista.head(filas_mostrar), use_container_width=True, height=420)

# ── Estadísticas ──────────────────────────────────────────────────────────────
if mostrar_stats:
    st.markdown("#### 📈 Estadísticas descriptivas")
    st.dataframe(df_vista.describe(include="all"), use_container_width=True)

# ── Descarga ──────────────────────────────────────────────────────────────────
st.markdown("---")
c1, c2, _ = st.columns([1, 1, 4])

with c1:
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Descargar CSV", csv_bytes, "datos.csv", "text/csv")

with c2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    st.download_button(
        "⬇ Descargar Excel",
        buffer.getvalue(),
        "datos.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
