import streamlit as st
import pandas as pd

st.set_page_config(page_title="Resultados ONPE 2021", layout="wide")

# Título principal de la aplicación [cite: 106]
st.title("Resultados Electorales ONPE 2021")
st.markdown("Sistema de análisis y visualización de datos públicos oficiales.")

# Cargar el dataset en la aplicación [cite: 111]
archivo_subido = st.file_uploader("Sube tu archivo CSV de resultados (ONPE u otra fuente)", type=["csv"])

if archivo_subido is not None:
    try:
        # Lectura inteligente del CSV
        df = pd.read_csv(archivo_subido, encoding="latin1", sep=None, engine="python")
        
        # Limpiar datos básicos si es necesario (valores nulos o formatos inconsistentes) 
        # Rellenamos cualquier casilla vacía con 0 para que las sumas no fallen
        df = df.fillna(0)
        
        st.success(f"¡Base de datos cargada y limpia! Se procesaron {df.shape[0]} registros.")
        
        st.markdown("---")
        st.header("📌 Identificación y Descripción de los Datos")
        
        col1, col2 = st.columns(2)
        
        # 1. Número de mesas [cite: 113]
        num_mesas = df['MESA_DE_VOTACION'].nunique() if 'MESA_DE_VOTACION' in df.columns else len(df)
        col1.metric("Número de mesas únicas", f"{num_mesas:,}")
        
        # 2. Ubigeo [cite: 114]
        num_ubigeos = df['UBIGEO'].nunique() if 'UBIGEO' in df.columns else "No detectado"
        col2.metric("Cantidad de Ubigeos", num_ubigeos)
        
        st.markdown("### 🗳️ Distribución de Votos Generales")
        
        # 3. Votos válidos, nulos y en blanco [cite: 116]
        # El sistema busca partes de la palabra para no equivocarse si el CSV dice "VOTOS_NULOS" o solo "NULOS"
        votos_blanco = df[[col for col in df.columns if 'BLANCO' in col.upper()]].sum().sum()
        votos_nulos = df[[col for col in df.columns if 'NULO' in col.upper()]].sum().sum()
        
        # Para los válidos, buscamos columnas de "válidos" explícitos. 
        # Si no existe, se calculará sumando los votos de los candidatos más abajo.
        col_validos = [col for col in df.columns if 'VALIDO' in col.upper()]
        votos_validos = df[col_validos].sum().sum() if col_validos else 0
        
        col_v1, col_v2, col_v3 = st.columns(3)
        col_v2.metric("Votos en Blanco", f"{int(votos_blanco):,}")
        col_v3.metric("Votos Nulos", f"{int(votos_nulos):,}")

        st.markdown("### 👥 Votos por Candidato (Partidos Políticos)")
        # 4. Votos por candidato [cite: 115]
        # Filtramos las columnas que sabemos que son texto o metadatos para quedarnos solo con los partidos
        columnas_ignoradas = ['UBIGEO', 'DEPARTAMENTO', 'PROVINCIA', 'DISTRITO', 'TIPO_ELECCION', 'MESA_DE_VOTACION', 'DESCRIP_ESTADO_ACTA', 'TIPO_OBSERVACION', 'NULOS', 'BLANCO', 'BLANCOS', 'VOTOS_BLANCOS', 'VOTOS_NULOS', 'VOTOS_VALIDOS']
        
        # Nos quedamos solo con las columnas que tienen números y no están en la lista de ignoradas
        columnas_candidatos = [col for col in df.columns if col.upper() not in columnas_ignoradas and pd.api.types.is_numeric_dtype(df[col])]
        
        if columnas_candidatos:
            # Sumamos los votos de cada partido
            votos_por_candidato = df[columnas_candidatos].sum().sort_values(ascending=False)
            
            # Si no había columna explícita de válidos, la calculamos sumando los votos de todos los candidatos
            if votos_validos == 0:
                votos_validos = votos_por_candidato.sum()
            col_v1.metric("Votos Válidos (Estimado)", f"{int(votos_validos):,}")
            
            # Mostramos una tabla bonita con los candidatos [cite: 115]
            st.dataframe(votos_por_candidato.reset_index().rename(columns={'index': 'Candidato/Partido', 0: 'Total Votos'}), use_container_width=True)
            
        else:
            st.warning("No pude detectar automáticamente las columnas de los candidatos.")

    except Exception as e:
        st.error(f"Hubo un error al intentar leer el archivo: {e}")
        
else:
    st.info("👆 Por favor, carga tu dataset oficial en formato CSV para comenzar la evaluación.")