#Activar entorno virtual .\venv\Scripts\activate
# correr código  py .\booking_scraper.py

from playwright.sync_api import sync_playwright
import pandas as pd
import os.path
from datetime import date
import time
"""
This script will scrape the following information from booking.com:
- Hotel name
- Price
- Score
- Average review
- Total number of reviews
- Link to hotel page
- Check-in date
- Check-out date
- Destination
- Number of adults
- Number of rooms
- Number of children
- Number of days
- Date of the search
"""
inicio = time.time()
today = date.today()

# Lee el archivo de ingreso de municipios y lo convierte en un diccionario, 
# con valor= nombre_columna y clave= valores_columna
def municipios():
    municipios = pd.read_csv(r"C:\Users\DELL\Esteban\Web Scraping\booking_scraper\municipios_2.csv") # --> Cambio a municipios_2 para ensayo
    df = pd.DataFrame(municipios)
    Lista = {col: df[col].dropna().tolist() for col in df.columns}
    return Lista


def main():


    
    Lista = municipios()

    for i in range(len(Lista['Nombre Municipio'])):
        print (Lista["Nombre Municipio"][i])

    
        with sync_playwright() as p:
            
            # IMPORTANT: Change dates to future dates, otherwise it won't work
            checkin_date = '2023-11-17' #Cambio de fechas --> Esto quizás podría hacerse con búsqueda flexible
            checkout_date = '2023-11-18'
            destination = (Lista["Nombre Municipio"][i]) #La posición especifica cuál municipio se va a cargar,
            #                                             Esto es lo que se debería automatizar
            destination = destination
            adult = 2
            room = 1
            children = 0

            lista = [offset for offset in range(0,2000, 25)] # Corresponde a los resultados a consultar,  ej 
                                                                #(0,200,25) serían 200 valores con 25 resultados por página 

            # Esto anterior se podría detener cuando no encuentre más resultados, para ser más eficiente
            # También se podría buscar la forma de saber cuántos resultados se entregan por búsqueda y poner
            # algo así: range(1000,num_resultados,25), con num_resultados como variable que dependa de la búsqueda

            for  offset  in lista:

                page_url = f'https://www.booking.com/searchresults.es.html?checkin={checkin_date}&checkout={checkout_date}&selected_currency=COP&ss={destination}&ssne={destination}&ssne_untouched={destination}&lang=es&sb=1&src_elem=sb&src=searchresults&dest_type=city&group_adults={adult}&no_rooms={room}&group_children={children}&sb_travel_purpose=leisure&offset={offset}'

                browser = p.chromium.launch(headless=True) # headless= False permite que se muestre la interfaz gráfica, en True, sería en 2° plano
                #                                             CONVIENE CAMBIAR A TRUE PARA QUE SEA MÁS EFICIENTE, SE PUEDE REEMPLAZAR CON PRINTS                                                        
                ua = (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/69.0.3497.100 Safari/537.36"
                )
                # context = browser.new_context()
                # page = context.new_page()
                page = browser.new_page(user_agent=ua) #puede usarse la línea anterior y en esta context en vez de browser para que se abran como pestañas
                page.goto(page_url, timeout=60000) #Espera 60.000 ms (60 s) antes de decir que el navegador falló

                hotels = page.locator('//div[@data-testid="property-card"]').all()

                if len(hotels) == 0: # ------------------> Líneas nuevas
                    print(f" En la página {int((offset/25)+1)} hay cero hoteles, se interrumpe la búsqueda en {destination}")
                    break
                print(f'There are: {len(hotels)} hotels in {destination}.') # --> Aquí tal vez podría limitarse, 
                #                                           si len(hotels) es menor que 25, break
                
                # Con la línea de la variable hotels, podrían limitarse los resultados fuera del sitio de búsqueda (OJO con los que salen igual en el sitio)
                # Es probable que la mejor solución sea eliminar en la limpieza los no dicen centro
                """
                ------------------------------------------------------------------------------------------------------------------------------------
                Para filtrar los resultados y excluir los hoteles que aparecen después del aviso "Alojamientos en los alrededores de 'lugar'", puedes utilizar XPath para seleccionar únicamente los elementos que estén antes de ese aviso. La estructura exacta del aviso y de los elementos puede variar en el sitio web de Booking, así que es posible que necesites ajustar el XPath según la estructura específica de la página.

    A continuación, te proporciono un ejemplo general de cómo podrías adaptar el código para excluir los hoteles que aparecen después del aviso:

    ```python
    hotels_before_warning = page.locator('//div[@data-testid="property-card" and not(ancestor::div[contains(text(), "Alojamientos en los alrededores")])]').all()
    ```

    En este XPath, estamos seleccionando todos los elementos `<div>` con el atributo `data-testid` igual a "property-card" que no tienen un ancestro `<div>` que contiene el texto "Alojamientos en los alrededores". Esto debería ayudar a excluir los hoteles que aparecen después de ese aviso.

    Recuerda que la estructura exacta del sitio web de Booking puede cambiar, y es posible que necesites ajustar el XPath según la estructura HTML específica de la página en la que estás trabajando. Puedes inspeccionar el código fuente de la página para comprender mejor la estructura y ajustar el XPath en consecuencia.
                -----------------------------------------------------------------------------------------------------------------------------------            

                """


                hotels_list = []
                for hotel in hotels:
                    hotel_dict = {}
                    hotel_dict['hotel'] = hotel.locator('//div[@data-testid="title"]').inner_text()
                    hotel_dict['price'] = hotel.locator('//span[@data-testid="price-and-discounted-price"]').inner_text()
                    hotel_dict['score'] = hotel.locator('//div[@data-testid="review-score"]/div[1]').all_inner_texts()
                    hotel_dict['avg review'] = hotel.locator('//div[@data-testid="review-score"]/div[2]/div[1]').all_inner_texts()
                    hotel_dict['reviews count'] = hotel.locator('//div[@data-testid="review-score"]/div[2]/div[2]').all_inner_texts()
                    hotel_dict['comfort'] = hotel.locator('//a[@data-testid="secondary-review-score-link"]').all_inner_texts()
                    hotel_dict['distancia del centro'] = hotel.locator('//span[@data-testid="distance"]').all_inner_texts()
                    hotel_dict['nivel de sostenibilidad'] = hotel.locator('//span[@data-testid="badge-sustainability"]').all_inner_texts()
                    hotel_dict['información habitación'] = hotel.locator('//div[@class="ccbf515d6e c07a747311"]//div[@role="link"]').all_inner_texts()
                    hotel_dict['Desayuno incluido'] = hotel.locator('//div[@class="ccbf515d6e c07a747311"]//span').all_inner_texts()
                    hotel_dict['Cancelación incluida'] = hotel.locator('//div[@class="ccbf515d6e c07a747311"]//strong').all_inner_texts()
                    
                
                    

                    hotels_list.append(hotel_dict)
                
        
                df = pd.DataFrame(hotels_list)
                df["Municipio"]= destination
                df["url"]= page_url
                df["fecha_consulta"]= today
                rute =r"C:\Users\DELL\Esteban\Web Scraping\booking_scraper\BORRAR_hotels_list_ensayo.xlsx" # --------> Se modifica para ensayo
                if os.path.exists(rute):
                    df1 = pd.read_excel(rute)
                    pd.concat([df1, df]).to_excel(rute, index=False)

                    # if destination in df1['Municipio'].values: # ------------> Condicional agregado para no repetir valores (no sirve porque está dentro del loop)
                    #     print("El municipio está repetido, por lo tanto no se agregará")
                    # else:
                    #     pd.concat([df1, df]).to_excel(rute, index=False)
                    
                else:
                    df.to_excel(rute, index=False)

                #df = pd.DataFrame(hotels_list)
                #df.to_excel(excel_writer='hotels_list5.xlsx', index=False)
                #df.to_excel('hotels_list.xlsx', index=False) 
                df.to_csv('BORRAR_hotels_list_ensayo.csv', index=False) # ------> Modificado para ensayo
                browser.close()

            
            
            # browser.close()
            
if __name__ == '__main__':
    main()


import numpy as np
import pandas as pd
import re
import unidecode

# Se importan los DataFrames y se combinan
df = pd.read_excel(r"C:\Users\DELL\Esteban\Web Scraping\booking_scraper\BORRAR_hotels_list_ensayo.xlsx")#("C:/Users/DELL/Esteban/Web Scraping/booking_scraper/python/hotels_list.xlsx")
df_coord = pd.read_excel("C:/Users/DELL/Esteban/Web Scraping/booking_scraper/python/coordenadas.xlsx")
df = df.merge(df_coord[['Código','Municipio','Subregión',"Latitud","Longitud"]],on = 'Municipio', how = 'left')

# FUNCIONES

def desayuno(texto):
    """
    Identifica si un hotel incluye desayuno y lo convierte en 1 o de lo contrario en 0.

    Parameters:
        texto (str): El texto en el que se busca la presencia de "Desayuno" o "desayuno".

    Returns:
        int: Devuelve 1 si "Desayuno" o "desayuno" está presente en el texto, de lo contrario, devuelve 0.
    """
    if "Desayuno" in texto or "desayuno" in texto:
        return 1
    else:
        return 0
    
    
def extraer_numeros(valor):
    """
    Extrae un número decimal de un texto que contiene una etiqueta y un número.

    Parameters:
        valor (str): El texto que contiene la etiqueta y el número.

    Returns:
        float o None: El número decimal extraído del texto. Retorna None si no se encuentra un número válido.
    """
    # Utiliza una expresión regular para buscar números en el valor
    numeros = re.findall(r'\d+[,.]?\d*', valor)
    
    # Si se encuentran números, toma el primer número
    if numeros:
        # Reemplaza la coma por un punto para que Python lo reconozca como decimal
        numero = numeros[0].replace(',', '.')
        return float(numero)
    else:
        return None
    
def distancia_metros(valor):
    """
    Extrae de un texto un número con unidad (m o km) y lo convierte a m.

    Parameters:
        valor (str): El texto que contiene el número con unidad.

    Returns:
        float o None: Número correspondiente a la distancia en m.
        Retorna None si no se encuentra un número con unidad válido.
    """
    # Utiliza una expresión regular para buscar números con unidad en el valor
    matches = re.findall(r'(\d+[,.]?\d*)\s*(km|m)', valor, re.IGNORECASE)

    if matches:
        numero, unidad = matches[0]
        # Reemplaza la coma por un punto en el número para que Python lo reconozca como decimal
        numero = numero.replace(',', '.')
        numero = float(numero)
        if unidad == 'km':
            numero *= 1000
        return numero
    else:
        return None   
    
def acomodacion(texto):

    """
    Extrae de un texto el tipo de acomodación y lo clasifica en dos
    columnas según su tipo y característica.

    Parameters:
        texto (str): Corresponde al texto de información de la habitación.

    Returns:
        tuple: Tupla correspondiente al tipo de acomodación y su característica.
    """

    apto = re.findall(r'\A(apartamento|casa|estudio|loft)', texto ,re.IGNORECASE)
    otro = re.findall(r'\A(bungalow|chalet|tienda|villa|cabaña)', texto ,re.IGNORECASE)
    hab = re.findall(r'(doble|compartida|cu.druple|deluxe|est.ndar|familiar|suite|triple)', texto ,re.IGNORECASE)

    if re.findall(r'\A(habitaci.n|suite|camarote|cama)|room', texto ,re.IGNORECASE):
        if hab:
            return ("habitacion",unidecode.unidecode(hab[0].lower()))
        else:
            return ("habitacion","estandar")

    elif apto:
        if apto[0] == 'Apartamento':
            return("apartamento","estandar")
        else:
            return ("apartamento",apto[0].lower())
    elif otro:
        return ("otro", otro[0].lower())
    elif texto == "":
        return (np.nan,np.nan)
    else:
        # return texto
        return ("otro", "otro")
    
def baño(texto):

    """
    Extrae de un texto si se especifica baño compartido o privado y retorna un valor
    de 0 para el primero y de 1 para el segundo.

    Parameters:
        texto (str): Corresponde al texto de información de la habitación.

    Returns:
        int o nan: Retorna 0 en caso de especificar baño compartido, 1 para baño privado
                   y nan para valores sin información de baño.
    """

    if re.search(r'baño', texto, re.IGNORECASE):
        if re.search(r'compartido', texto, re.IGNORECASE):
            return 0
        else: 
            return 1
    else:
        return np.nan

def dormitorios(texto):

    """
    Extrae de un texto si se especifica la palabra dormitorio o dormitorios y retorna 
    el número de estos o el valor nan en caso de no especificarse.

    Parameters:
        texto (str): Corresponde al texto de información de la habitación.

    Returns:
        list: Retorna una lista con el número de dormitorios en caso de especificar o de lo contrario
        retorna nan.
    """

    if re.findall(r'(dormitorio|dormitorios)', texto, re.IGNORECASE):
        return re.findall(r'\d', texto, re.IGNORECASE)
    else:
        return ([np.nan])
    


# LIMPIEZA INICIAL

    # Se eliminan los caracteres comunes "['']" en las columnas que los incluyen

cols = ['score','avg review','reviews count','comfort','distancia del centro',
        'nivel de sostenibilidad','información habitación','Desayuno incluido',
        'Cancelación incluida']
for col in cols:
    df[col] = (df[col].str.replace(r"['\[\]]", '', regex=True))


# Se eliminan los "." como separadores de decimales

cols = ['price','score','reviews count']
for col in cols:
    df[col] = (df[col].str.replace(".","",regex=False))

# Se hacen los cambios necesarios para terminar de limpiar los valores de las columnas

df['price'] = pd.to_numeric(df['price'].str.replace('COP','').str.strip())
df['score'] = pd.to_numeric(df['score'].str.replace(",","."))
df['reviews count'] = pd.to_numeric(df['reviews count'].str.replace(r'\b(comentario|comentarios)\b', '', regex=True))
df['nivel de sostenibilidad'] = df['nivel de sostenibilidad'].str.replace("Travel Sustainable Nivel ","")
df['Desayuno incluido'] = df['Desayuno incluido'].apply(desayuno)
df['comfort'] = (df['comfort'].apply(extraer_numeros))
df['Cancelación incluida'] = df['Cancelación incluida'].map({
                                                            'Cancelación gratis, Sin pago por adelantado': 2,
                                                            'Cancelación gratis': 1,'': 0})



# COLUMNAS NUEVAS

# Las siguientes columna se crea con el fin de tener una referencia para eliminar los duplicados

df["Origen_ref"] = df["distancia del centro"].apply(lambda x: x.split()[-1])

df['distancia origen m'] = df['distancia del centro'].apply(distancia_metros)

df['origen'] = np.where(df['Origen_ref'] == 'centro', 0, 1)

# Se crean columnas para tipo de acomodación y características

df["acomodacion"] = (df["información habitación"].apply(acomodacion)).apply(lambda x: x[0])
df["caracteristica"] = (df["información habitación"].apply(acomodacion)).apply(lambda x: x[1])

# Columna para especificar baño privado (1) o baño compartido (0)

df['baño'] = df['información habitación'].apply(baño)

#Columna con número de dormitorios

df['dormitorios'] = df['información habitación'].apply(dormitorios).apply(lambda x: x[0])

# Se reorganizan las columnas
df = df.iloc[:,[0,1,2,3,4,5,6,19,18,20,11,7,8,21,22,23,24,9,10,12,13,14,15,16,17]]

# FILAS DUPLICADAS

# Se genera referencia de shape antes de la limpieza
shape_df_pre = df.shape
shape_df_pre

"""
Primero se eliminan las filas donde se repite el nombre del hotel y el municipio. 
Se usan estos parámetros ya que los duplicados ocasionalmente varían en url y esto
impide que se identifiquen correctamente los duplicados por municipio. 
"""

df.drop_duplicates(subset = ('hotel','Municipio'), inplace = True)

# Para los hoteles que tiene "distancia al centro", se conserva esta fila y se eliminan las demás

#Primero, se encuentran los hoteles duplicados que incluyen el valor 'distancia al centro'
a = df[df['hotel'].duplicated(keep = False)]
con_centro = a.groupby('hotel')['origen'].apply(lambda x: 0 in x.values)
con_centro = con_centro[con_centro].index.tolist()

# Luego, Con los nombres de estos hoteles, se seleccionan los que no corresponden a centro (1) y se eliminan, conservando los que sí (0).
duplicados_centro = df[df['hotel'].isin(con_centro)].sort_values(by = 'origen').duplicated(subset='hotel')
duplicados_centro = duplicados_centro[duplicados_centro].index
df.drop(duplicados_centro, inplace = True)

"""
__________________________________________________________________________________________________________________
Esto se podría borrar
"""
# Se elimina el resto de duplicados con respecto a la distancia al origen
duplicados_otros = df.loc[df.duplicated(subset='hotel')].sort_values(by=['hotel','distancia origen m']).index
df.drop(duplicados_otros,inplace = True)

"""
___________________________________________________________________________________________________________________
"""
print(f"Se eliminaron en total {shape_df_pre[0]-df.shape[0]} filas")

# Se reinician los índices
df.reset_index(drop=True,inplace=True)

# BORRAR COLUMNAS INNECESARIAS

# Se borran las columnas que ya no se necesitan

df.columns
df.drop(['distancia del centro','Origen_ref','origen','información habitación','fecha_consulta'],axis=1, inplace=True)

# SEPARACIÓN DATASETS

# Se generan dos datasets, uno para Medellín y el otro para el resto de municipios
df_med = df.loc[df['Municipio'] == 'MEDELLIN'].reset_index(drop=True)
df_ant = df.loc[df['Municipio'] != 'MEDELLIN']

# EXPORT

# Se exportan ambos datasets como un libro de excel con dos hojas
with pd.ExcelWriter('booking_clean.xlsx') as writer:
    df_ant.to_excel(writer, sheet_name='Antioquia')
    df_med.to_excel(writer, sheet_name='Medellin')

fin = time.time()
print(f"Tiempo ejecución: {fin-inicio} segundos")