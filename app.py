import altair as alt
import pandas as pd
import streamlit as st

# Configuración general de la página
st.set_page_config(
    page_title="Análisis de Libros - Books to Scrape",
    page_icon="📚",
    layout="wide",
)


@st.cache_data
def cargar_datos(ruta: str) -> pd.DataFrame:
    """Carga el dataset limpio en caché para evitar lecturas repetidas del disco."""
    return pd.read_csv(ruta)


df = cargar_datos("data/datos_limpios.csv")

st.title("📚 Dashboard de Análisis de Catálogo Editorial")
st.markdown(
    "Exploración interactiva de **205 libros** extraídos mediante Web Scraping "
    "de *Books to Scrape* para analizar precios, géneros y valoraciones."
)

# --- BARRA LATERAL: FILTROS INTERACTIVOS ---
st.sidebar.header("Filtros de búsqueda")

generos_disponibles = sorted(df["genero"].unique())
generos_seleccionados = st.sidebar.multiselect(
    "Selecciona uno o varios géneros:",
    options=generos_disponibles,
    default=generos_disponibles,
)

precio_min = float(df["precio_gbp"].min())
precio_max = float(df["precio_gbp"].max())
rango_precio = st.sidebar.slider(
    "Rango de precio (£):",
    min_value=precio_min,
    max_value=precio_max,
    value=(precio_min, precio_max),
)

rating_minimo = st.sidebar.slider(
    "Valoración mínima (estrellas):",
    min_value=1,
    max_value=5,
    value=1,
)

# Aplicación combinada de filtros sobre el DataFrame
df_filtrado = df[
    (df["genero"].isin(generos_seleccionados))
    & (df["precio_gbp"].between(rango_precio[0], rango_precio[1]))
    & (df["rating"] >= rating_minimo)
]

# --- MÉTRICAS PRINCIPALES (KPIs) ---
col1, col2, col3 = st.columns(3)
col1.metric("Libros mostrados", len(df_filtrado))
col2.metric(
    "Precio medio (£)",
    f"{df_filtrado['precio_gbp'].mean():.2f} £" if not df_filtrado.empty else "0.00 £",
)
col3.metric(
    "Valoración media",
    f"{df_filtrado['rating'].mean():.2f} / 5" if not df_filtrado.empty else "0.00 / 5",
)

st.divider()

if df_filtrado.empty:
    st.warning("No hay libros que coincidan con los filtros seleccionados. Amplía el rango en la barra lateral.")
else:
    # --- SECCIÓN DE GRÁFICOS Y ANÁLISIS CRÍTICO ---
    st.subheader("1. ¿Qué géneros tienen el precio medio más alto?")
    precio_por_genero = (
        df_filtrado.groupby("genero", as_index=False)["precio_gbp"]
        .mean()
        .sort_values(by="precio_gbp", ascending=False)
    )

    grafico_precios = (
        alt.Chart(precio_por_genero)
        .mark_bar(color="#4C78A8")
        .encode(
            x=alt.X("precio_gbp:Q", title="Precio medio (£)"),
            y=alt.Y("genero:N", sort="-x", title="Género literario"),
            tooltip=["genero", alt.Tooltip("precio_gbp:Q", format=".2f", title="Precio medio (£)")],
        )
        .properties(height=350, title="Precio medio por género literario")
    )
    st.altair_chart(grafico_precios, use_container_width=True)

    genero_caro = precio_por_genero.iloc[0]
    genero_barato = precio_por_genero.iloc[-1]
    st.info(
        f"**Interpretación:** Dentro de la selección actual, **{genero_caro['genero']}** "
        f"presenta el precio medio más elevado ({genero_caro['precio_gbp']:.2f} £), mientras que "
        f"**{genero_barato['genero']}** es la categoría más económica ({genero_barato['precio_gbp']:.2f} £)."
    )

    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("2. Distribución de valoraciones")
        conteo_ratings = df_filtrado.groupby("rating", as_index=False).size()
        grafico_ratings = (
            alt.Chart(conteo_ratings)
            .mark_bar(color="#F58518")
            .encode(
                x=alt.X("rating:O", title="Puntuación (Estrellas)"),
                y=alt.Y("size:Q", title="Cantidad de libros"),
                tooltip=["rating", alt.Tooltip("size:Q", title="Total de libros")],
            )
            .properties(height=300, title="Cantidad de libros por puntuación")
        )
        st.altair_chart(grafico_ratings, use_container_width=True)

    with col_der:
        st.subheader("3. ¿Influye el precio en la valoración?")
        precio_por_rating = (
            df_filtrado.groupby("rating", as_index=False)["precio_gbp"].mean()
        )
        grafico_relacion = (
            alt.Chart(precio_por_rating)
            .mark_line(point=True, color="#54A24B")
            .encode(
                x=alt.X("rating:O", title="Puntuación (Estrellas)"),
                y=alt.Y("precio_gbp:Q", title="Precio medio (£)"),
                tooltip=["rating", alt.Tooltip("precio_gbp:Q", format=".2f", title="Precio medio (£)")],
            )
            .properties(height=300, title="Relación entre estrellas y precio medio")
        )
        st.altair_chart(grafico_relacion, use_container_width=True)

    st.info(
        "**Análisis de correlación:** Al comparar el precio medio según el número de estrellas, "
        "se observa que un precio más alto no garantiza una mejor valoración; los libros de 1 y 5 estrellas "
        "mantienen promedios de precio muy similares."
    )

    st.divider()

    # --- TABLA INTERACTIVA DE RESULTADOS ---
    st.subheader("Catálogo detallado (resultados filtrados)")
    st.dataframe(
        df_filtrado[["enlace_portada", "titulo", "genero", "precio_gbp", "rating"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "enlace_portada": st.column_config.ImageColumn("Portada", width="small"),
            "titulo": st.column_config.TextColumn("Título del libro"),
            "genero": st.column_config.TextColumn("Género"),
            "precio_gbp": st.column_config.NumberColumn("Precio (£)", format="£%.2f"),
            "rating": st.column_config.NumberColumn("Valoración", format="%d ⭐"),
        },
    )