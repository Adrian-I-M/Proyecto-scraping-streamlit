import time
from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"

# Identificación mediante User-Agent para cumplir buenas prácticas de scraping
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ProyectoAcademicoScraping/1.0"
}

# Diccionario para convertir la clase CSS de estrellas en un valor numérico
MAPA_RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def obtener_sopa(url: str) -> BeautifulSoup:
    """Realiza la petición HTTP, fuerza codificación UTF-8 y devuelve el árbol HTML."""
    respuesta = requests.get(url, headers=HEADERS, timeout=10)
    respuesta.raise_for_status()
    respuesta.encoding = "utf-8"  # Evita caracteres corruptos como 'Â£' en los precios
    return BeautifulSoup(respuesta.text, "html.parser")


def extraer_libros() -> pd.DataFrame:
    """Recorre las categorías de la web y extrae los datos limpios de cada libro."""
    sopa_inicio = obtener_sopa(BASE_URL)
    
    # Seleccionamos los enlaces de géneros del menú lateral (excluyendo el enlace padre 'Books')
    enlaces_generos = sopa_inicio.select("ul.nav-list ul li a")
    datos_libros = []

    # Recorremos los primeros 12 géneros para obtener una muestra amplia sin saturar el servidor
    for enlace in enlaces_generos[:12]:
        genero = enlace.text.strip()
        url_genero = urljoin(BASE_URL, enlace["href"])
        print(f"Extrayendo género: {genero}...")

        sopa_genero = obtener_sopa(url_genero)
        libros = sopa_genero.select("article.product_pod")

        for libro in libros:
            # 1. Título completo desde el atributo 'title' (el texto visible aparece recortado con '...')
            titulo = libro.h3.a["title"].strip()

            # 2. Precio limpio convertido directamente a float
            precio_texto = libro.select_one("p.price_color").text
            precio = float(precio_texto.replace("£", "").strip())

            # 3. Rating convertido de texto ('Three') a entero (3)
            clases_rating = libro.select_one("p.star-rating")["class"]
            rating = MAPA_RATING.get(clases_rating[1], 0)

            # 4. Enlace absoluto de la portada
            src_relativo = libro.select_one("div.image_container img")["src"]
            enlace_portada = urljoin(url_genero, src_relativo)

            datos_libros.append({
                "titulo": titulo,
                "genero": genero,
                "precio_gbp": precio,
                "rating": rating,
                "enlace_portada": enlace_portada,
            })

        # Pausa ética entre peticiones para no sobrecargar el servidor
        time.sleep(1)

    return pd.DataFrame(datos_libros)


if __name__ == "__main__":
    df_libros = extraer_libros()
    ruta_salida = "data/datos_limpios.csv"
    df_libros.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"\nProceso finalizado. Se han guardado {len(df_libros)} libros en '{ruta_salida}'.")