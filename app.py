import pandas as pd
import streamlit as st

# 1. Cargar los datos limpios desde el CSV
df = pd.read_csv("data/datos_limpios.csv")

st.title("Análisis de Libros - Books to Scrape")
st.write("Dashboard interactivo para explorar precios, géneros y valoraciones.")

# 2. Filtros interactivos en la barra lateral
st.sidebar.header("Filtros")

lista_generos = sorted(df["genero"].unique())
generos_elegidos = st.sidebar.multiselect("Géneros:", lista_generos, default=lista_generos)

precio_min = float(df["precio_gbp"].min())
precio_max = float(df["precio_gbp"].max())
rango_precio = st.sidebar.slider("Rango de precio (£):", precio_min, precio_max, (precio_min, precio_max))

rating_min = st.sidebar.slider("Valoración mínima (estrellas):", 1, 5, 1)

# 3. Filtrar el DataFrame según lo que elija el usuario
df_filtrado = df[
    (df["genero"].isin(generos_elegidos)) &
    (df["precio_gbp"] >= rango_precio[0]) &
    (df["precio_gbp"] <= rango_precio[1]) &
    (df["rating"] >= rating_min)
]

# Comprobamos si hay resultados antes de mostrar métricas y gráficos
if df_filtrado.empty:
    st.warning("No hay libros con esos filtros. Prueba a cambiar las opciones de la izquierda.")
else:
    # 4. Métricas resumen
    col1, col2, col3 = st.columns(3)
    col1.metric("Libros encontrados", len(df_filtrado))
    col2.metric("Precio medio", f"{df_filtrado['precio_gbp'].mean():.2f} £")
    col3.metric("Valoración media", f"{df_filtrado['rating'].mean():.2f} / 5")

    st.divider()

    # 5. Gráfico 1: Precio medio por género
    st.subheader("1. ¿Qué géneros tienen el precio medio más alto?")
    precio_genero = df_filtrado.groupby("genero")["precio_gbp"].mean().sort_values(ascending=False)
    st.bar_chart(precio_genero)

    genero_mas_caro = precio_genero.index[0]
    genero_mas_barato = precio_genero.index[-1]
    st.info(
        f"Conclusión: El género más caro de media es {genero_mas_caro} ({precio_genero.iloc[0]:.2f} £) "
        f"y el más barato es {genero_mas_barato} ({precio_genero.iloc[-1]:.2f} £)."
    )

    # 6. Gráfico 2: Cantidad de libros por estrellas
    st.subheader("2. Distribución de valoraciones (estrellas)")
    conteo_estrellas = df_filtrado["rating"].value_counts().sort_index()
    st.bar_chart(conteo_estrellas)

    # 7. Gráfico 3: Relación entre estrellas y precio medio
    st.subheader("3. ¿Influye el precio en la valoración?")
    precio_estrellas = df_filtrado.groupby("rating")["precio_gbp"].mean()
    st.line_chart(precio_estrellas)
    st.info("Conclusión: Un precio más alto no significa mejor puntuación; la media se mantiene parecida en todas las estrellas.")

    st.divider()

    # 8. Tabla interactiva con los datos filtrados
    st.subheader("Tabla de libros filtrados")
    st.dataframe(df_filtrado)