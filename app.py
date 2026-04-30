import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(
    page_title="Resultados ONPE 2021",
    layout="wide",
    page_icon="🗳️"
)

# ==========================================
# PARTE 8 - TÍTULO INSTITUCIONAL
# ==========================================
col_logo1, col_titulo, col_logo2 = st.columns([1, 4, 1])
with col_titulo:
    st.markdown("""
        <div style='text-align: center; padding: 10px 0;'>
            <h1 style='color: #c0392b; font-size: 2.2rem; margin-bottom: 0;'>🗳️ ONPE</h1>
            <h2 style='color: #2c3e50; font-size: 1.5rem; margin-top: 4px;'>Oficina Nacional de Procesos Electorales</h2>
            <p style='color: #7f8c8d; font-size: 1rem;'>Sistema Oficial de Resultados Electorales — Elecciones Generales 2021</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 2px solid #c0392b;'>", unsafe_allow_html=True)

# ==========================================
# PARTE 2 - CARGA DE DATOS
# ==========================================
archivo_subido = st.file_uploader(
    "📂 Sube tu archivo CSV de resultados (ONPE u otra fuente oficial)",
    type=["csv"]
)

if archivo_subido is not None:
    try:
        df = pd.read_csv(archivo_subido, encoding="latin1", sep=None, engine="python")
        df = df.fillna(0)

        st.success(f"✅ Dataset cargado con éxito — {df.shape[0]:,} registros detectados.")
        st.markdown("<hr>", unsafe_allow_html=True)

        # Columnas de candidatos
        columnas_no_candidatos = [
            'UBIGEO', 'DEPARTAMENTO', 'PROVINCIA', 'DISTRITO', 'TIPO_ELECCION',
            'MESA_DE_VOTACION', 'DESCRIP_ESTADO_ACTA', 'TIPO_OBSERVACION',
            'NULOS', 'BLANCO', 'BLANCOS', 'VOTOS_BLANCOS', 'VOTOS_NULOS',
            'VOTOS_VALIDOS', 'TOTAL_VOTOS_MESA', 'N_CVAS', 'TOTAL_MUESTRA'
        ]
        columnas_candidatos = [
            col for col in df.columns
            if col.upper() not in columnas_no_candidatos
            and pd.api.types.is_numeric_dtype(df[col])
        ]

        # ==========================================
        # PARTE 8 - USER FLOW: PASO 1 — SELECCIÓN DE REGIÓN
        # ==========================================
        st.header("🔍 Paso 1: Selección de Región y Candidato")
        st.markdown("Utiliza los filtros para explorar los resultados por zona geográfica o candidato/partido.")

        col_f1, col_f2, col_f3 = st.columns(3)

        # Filtro por Departamento
        with col_f1:
            if 'DEPARTAMENTO' in df.columns:
                departamentos = ["Todos"] + sorted(df['DEPARTAMENTO'].dropna().unique().tolist())
                depto_sel = st.selectbox("🌎 Filtrar por Departamento", departamentos)
            else:
                depto_sel = "Todos"
                st.info("Columna DEPARTAMENTO no disponible.")

        # Filtro por Provincia
        with col_f2:
            if 'PROVINCIA' in df.columns:
                if depto_sel != "Todos":
                    provincias_disponibles = df[df['DEPARTAMENTO'] == depto_sel]['PROVINCIA'].dropna().unique().tolist()
                else:
                    provincias_disponibles = df['PROVINCIA'].dropna().unique().tolist()
                provincias = ["Todas"] + sorted(provincias_disponibles)
                prov_sel = st.selectbox("🏙️ Filtrar por Provincia", provincias)
            else:
                prov_sel = "Todas"
                st.info("Columna PROVINCIA no disponible.")

        # Filtro por Candidato
        with col_f3:
            if columnas_candidatos:
                candidato_sel = st.selectbox("👤 Filtrar por Candidato/Partido", ["Todos"] + columnas_candidatos)
            else:
                candidato_sel = "Todos"
                st.info("No se detectaron columnas de candidatos.")

        # Aplicar filtros al DataFrame
        df_filtrado = df.copy()
        if depto_sel != "Todos" and 'DEPARTAMENTO' in df.columns:
            df_filtrado = df_filtrado[df_filtrado['DEPARTAMENTO'] == depto_sel]
        if prov_sel != "Todas" and 'PROVINCIA' in df.columns:
            df_filtrado = df_filtrado[df_filtrado['PROVINCIA'] == prov_sel]

        st.caption(f"📋 Mostrando {df_filtrado.shape[0]:,} registros con los filtros aplicados.")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ==========================================
        # PARTE 2 - DESCRIPCIÓN DE LA DATA
        # ==========================================
        st.header("📌 Descripción de la Data Electoral")

        col_m1, col_m2 = st.columns(2)
        num_mesas = df_filtrado['MESA_DE_VOTACION'].nunique() if 'MESA_DE_VOTACION' in df_filtrado.columns else len(df_filtrado)
        num_ubigeos = df_filtrado['UBIGEO'].nunique() if 'UBIGEO' in df_filtrado.columns else "N/D"
        col_m1.metric("Total de Mesas Únicas", f"{num_mesas:,}")
        col_m2.metric("Total de Ubigeos Identificados", num_ubigeos)

        st.markdown("### 🗳️ Resumen de Votación")
        votos_blanco = df_filtrado[[col for col in df_filtrado.columns if 'BLANCO' in col.upper()]].sum().sum()
        votos_nulos  = df_filtrado[[col for col in df_filtrado.columns if 'NULO' in col.upper()]].sum().sum()
        votos_validos = df_filtrado[columnas_candidatos].sum().sum() if columnas_candidatos else 0

        cv1, cv2, cv3 = st.columns(3)
        cv1.metric("Votos Válidos", f"{int(votos_validos):,}")
        cv2.metric("Votos en Blanco", f"{int(votos_blanco):,}")
        cv3.metric("Votos Nulos", f"{int(votos_nulos):,}")

        if columnas_candidatos:
            resumen_candidatos = df_filtrado[columnas_candidatos].sum().sort_values(ascending=False)

            # Si hay filtro por candidato, mostramos solo ese
            if candidato_sel != "Todos":
                resumen_candidatos = resumen_candidatos[[candidato_sel]] if candidato_sel in resumen_candidatos.index else resumen_candidatos

            st.subheader("👥 Detalle de Votos por Candidato/Partido")
            st.dataframe(
                resumen_candidatos.reset_index().rename(
                    columns={'index': 'Candidato / Partido', 0: 'Total de Votos'}
                ),
                use_container_width=True
            )

            st.markdown("<hr>", unsafe_allow_html=True)

            # ==========================================
            # PARTE 8 - USER FLOW: PASO 2 — VISUALIZACIÓN DE RESULTADOS
            # ==========================================
            st.header("📊 Paso 2: Visualización de Resultados")

            tab1, tab2, tab3 = st.tabs(["🏆 Por Candidato", "🌎 Por Región", "📈 Top 5"])

            with tab1:
                st.subheader("Votos por Candidato/Partido")
                st.bar_chart(resumen_candidatos)

            with tab2:
                if 'DEPARTAMENTO' in df_filtrado.columns:
                    st.subheader("Distribución Electoral por Departamento")
                    df_filtrado['TOTAL_MUESTRA'] = df_filtrado[columnas_candidatos].sum(axis=1)
                    votos_region = df_filtrado.groupby('DEPARTAMENTO')['TOTAL_MUESTRA'].sum().sort_values(ascending=False)
                    st.bar_chart(votos_region)
                else:
                    st.info("No hay columna DEPARTAMENTO disponible para esta visualización.")

            with tab3:
                st.subheader("Top 5 Candidatos con Mayor Votación")
                st.area_chart(resumen_candidatos.head(5))

            st.markdown("<hr>", unsafe_allow_html=True)

            # ==========================================
            # PARTE 8 - USER FLOW: PASO 3 — INTERPRETACIÓN
            # ==========================================
            st.header("💡 Paso 3: Interpretación de Resultados")

            lider = resumen_candidatos.idxmax()
            votos_lider = int(resumen_candidatos.max())
            total_votos = int(resumen_candidatos.sum())
            porcentaje_lider = (votos_lider / total_votos * 100) if total_votos > 0 else 0

            col_i1, col_i2 = st.columns(2)
            with col_i1:
                st.success(f"🥇 **Candidato/Partido líder:** {lider}")
                st.metric("Votos obtenidos", f"{votos_lider:,}", f"{porcentaje_lider:.1f}% del total")

            with col_i2:
                st.info(f"📊 **Total de votos analizados:** {total_votos:,}")
                st.metric("Candidatos/Partidos en competencia", len(resumen_candidatos))

            filtro_activo = []
            if depto_sel != "Todos":
                filtro_activo.append(f"Departamento: **{depto_sel}**")
            if prov_sel != "Todas":
                filtro_activo.append(f"Provincia: **{prov_sel}**")
            if candidato_sel != "Todos":
                filtro_activo.append(f"Candidato: **{candidato_sel}**")

            contexto = f" (Filtros aplicados: {', '.join(filtro_activo)})" if filtro_activo else " (Vista nacional — sin filtros activos)"

            st.markdown("### 📝 Análisis Automático")
            st.info(f"""
**Análisis de resultados{contexto}**

El análisis de los datos cargados muestra que **{lider}** lidera la contienda electoral 
con **{votos_lider:,} votos**, representando el **{porcentaje_lider:.1f}%** del total de votos válidos registrados en la selección actual.

Se observa una participación de **{len(resumen_candidatos)} candidatos o partidos** en la muestra analizada. 
La distribución de votos permite identificar las preferencias ciudadanas según la región seleccionada, 
siendo este tipo de análisis fundamental para comprender el comportamiento electoral a nivel nacional y regional.

Los votos en blanco (**{int(votos_blanco):,}**) y nulos (**{int(votos_nulos):,}**) representan 
información clave para evaluar la representatividad efectiva del proceso electoral.
            """)

    except Exception as error:
        st.error(f"⚠️ Error al procesar el archivo: {error}")

else:
    # ==========================================
    # PARTE 8 - ESTADO INICIAL (User Flow - Bienvenida)
    # ==========================================
    st.markdown("""
        <div style='text-align: center; padding: 60px 20px;'>
            <h2 style='color: #2c3e50;'>👋 Bienvenido al Sistema de Resultados ONPE 2021</h2>
            <p style='font-size: 1.1rem; color: #7f8c8d;'>
                Para iniciar el análisis, cargue un archivo CSV oficial en el panel superior.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Paso 1**\n\n🌎 Selecciona tu región o candidato usando los filtros disponibles.")
    with col2:
        st.info("**Paso 2**\n\n📊 Visualiza los resultados en gráficas interactivas por candidato y región.")
    with col3:
        st.info("**Paso 3**\n\n💡 Lee la interpretación automática generada a partir de los datos.")