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

def municipios():
    municipios = pd.read_csv(r"C:\Users\DELL\Esteban\Web Scraping\booking_scraper\municipios.csv")
    df = pd.DataFrame(municipios)
    Lista = {col: df[col].dropna().tolist() for col in df.columns}
    return Lista


def main():


    
    Lista = municipios()
    
    with sync_playwright() as p:
        
        # IMPORTANT: Change dates to future dates, otherwise it won't work
        checkin_date = '2023-11-17' #Cambio de fechas
        checkout_date = '2023-11-18'
        destination = (Lista["Nombre Municipio"][0])
        destination = destination
        adult = 2
        room = 1
        children = 0

        lista = [offset for offset in range(500,525, 25)]


        for  offset  in lista:

            page_url = f'https://www.booking.com/searchresults.es.html?checkin={checkin_date}&checkout={checkout_date}&selected_currency=COP&ss={destination}&ssne={destination}&ssne_untouched={destination}&lang=es&sb=1&src_elem=sb&src=searchresults&dest_type=city&group_adults={adult}&no_rooms={room}&group_children={children}&sb_travel_purpose=leisure&offset={offset}'

            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(page_url, timeout=60000)
                        
            hotels = page.locator('//div[@data-testid="property-card"]').all()
            print(f'There are: {len(hotels)} hotels.')

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
            rute =r"C:\Users\DELL\Esteban\Web Scraping\booking_scraper\hotels_list.xlsx"
            if os.path.exists(rute):
                df1 = pd.read_excel(rute)
                pd.concat([df1, df]).to_excel(rute, index=False)
                
            else:
                df.to_excel(rute, index=False)

            #df = pd.DataFrame(hotels_list)
            #df.to_excel(excel_writer='hotels_list5.xlsx', index=False)
            #df.to_excel('hotels_list.xlsx', index=False) 
            df.to_csv('hotels_list.csv', index=False)

        
        
        browser.close()
            
if __name__ == '__main__':
    main()


