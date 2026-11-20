import time
from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"

# Cabecera para identificarnos y respetar buenas prácticas
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ProyectoAcademico/1.0"
}

# Diccionario para pasar las estrellas de texto a número
MAPA_RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def obtener_sopa(url):
    respuesta = requests.get(url, headers=HEADERS)
    respuesta.encoding = "utf-8"  # Evita que el símbolo £ salga corrupto como 'Â£'
    return BeautifulSoup(respuesta.text, "html.parser")


def extraer_libros():
    sopa_inicio = obtener_sopa(BASE_URL)
    enlaces_generos = sopa_inicio.select("ul.nav-list ul li a")
    datos_libros = []

    # Recorremos los primeros 12 géneros
    for enlace in enlaces_generos[:12]:
        genero = enlace.text.strip()
        url_genero = urljoin(BASE_URL, enlace["href"])
        print(f"Extrayendo género: {genero}...")

        sopa_genero = obtener_sopa(url_genero)
        libros = sopa_genero.select("article.product_pod")

        for libro in libros:
            # 1. Título completo desde el atributo 'title'
            titulo = libro.h3.a["title"].strip()

            # 2. Quitamos el símbolo £ y convertimos a número decimal (float)
            precio_texto = libro.select_one("p.price_color").text
            precio = float(precio_texto.replace("£", "").strip())

            # 3. Convertimos la palabra de estrellas ('Three') a número (3)
            clases_rating = libro.select_one("p.star-rating")["class"]
            rating = MAPA_RATING[clases_rating[1]]

            # 4. Convertimos la ruta relativa de la imagen en URL completa
            src_relativo = libro.select_one("div.image_container img")["src"]
            enlace_portada = urljoin(url_genero, src_relativo)

            datos_libros.append({
                "titulo": titulo,
                "genero": genero,
                "precio_gbp": precio,
                "rating": rating,
                "enlace_portada": enlace_portada,
            })

        # Pausa de 1 segundo entre categorías para no saturar el servidor
        time.sleep(1)

    return pd.DataFrame(datos_libros)


df_libros = extraer_libros()
df_libros.to_csv("data/datos_limpios.csv", index=False, encoding="utf-8")
print(f"Proceso finalizado. Se han guardado {len(df_libros)} libros.")