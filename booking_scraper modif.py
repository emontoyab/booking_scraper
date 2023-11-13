#Activar entorno virtual .\venv\Scripts\activate
# correr código  py .\booking_scraper.py

from playwright.sync_api import sync_playwright
import pandas as pd
import os.path
from datetime import date
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
    
    with sync_playwright() as p:
        
        # IMPORTANT: Change dates to future dates, otherwise it won't work
        checkin_date = '2023-11-17' #Cambio de fechas --> Esto quizás podría hacerse con búsqueda flexible
        checkout_date = '2023-11-18'
        destination = (Lista["Nombre Municipio"][0]) #La posición especifica cuál municipio se va a cargar,
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

            #Analizar mejor estos parámetros (headless, timeout)
            browser = p.chromium.launch(headless=False) # headless= False permite que se muestre la interfaz gráfica, en True, sería en 2° plano
            #                                             CONVIENE CAMBIAR A TRUE PARA QUE SEA MÁS EFICIENTE, SE PUEDE REEMPLAZAR CON PRINTS                                                        
            #context = browser.new_context()
            page = browser.new_page() #puede usarse la línea anterior y en esta context en vez de browser para que se abran como pestañas
            page.goto(page_url, timeout=60000) #Espera 60.000 ms (60 s) antes de decir que el navegador falló
                                    
            hotels = page.locator('//div[@data-testid="property-card"]').all()

            if len(hotels) == 0: # ------------------> Líneas nuevas
                print(f" En la página {offset/25} hay cero hoteles, se interrumpe la búsqueda en {destination}")
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
            rute =r"C:\Users\DELL\Esteban\Web Scraping\booking_scraper\hotels_list_ensayo.xlsx" # --------> Se modifica para ensayo
            if os.path.exists(rute):
                df1 = pd.read_excel(rute)
                if destination in df1['Municipio'].values: # ------------> Condicional agregado para no repetir valores
                    print("El municipio está repetido, por lo tanto no se agregará")
                else:
                    pd.concat([df1, df]).to_excel(rute, index=False)
                
            else:
                df.to_excel(rute, index=False)

            #df = pd.DataFrame(hotels_list)
            #df.to_excel(excel_writer='hotels_list5.xlsx', index=False)
            #df.to_excel('hotels_list.xlsx', index=False) 
            df.to_csv('hotels_list_ensayo.csv', index=False) # ------> Modificado para ensayo

        
        
        browser.close()
            
if __name__ == '__main__':
    main()


