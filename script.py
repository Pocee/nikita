from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

url = "https://boss-spawns.pages.dev/"

# Configurar el navegador en modo headless
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

driver = webdriver.Chrome(options=options)

try:
    driver.get(url)
    
    # Esperar a que el contenido cargue
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "font-medium")))
    
    # Esperar un poco más para asegurar que todo cargue
    time.sleep(3)
    
    # Obtener el HTML completo después de que JavaScript haya cargado
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    
    # Buscar todas las secciones de mapas
    map_sections = soup.find_all('section', class_='rounded-xl')
    
    # Diccionario para agrupar por mapas
    maps_data = {}
    
    for section in map_sections:
        # Obtener el nombre del mapa del botón
        map_button = section.find('button', class_='w-full')
        if map_button:
            map_name_span = map_button.find('span', class_='text-base')
            if not map_name_span:
                map_name_span = map_button.find('span', class_='text-lg')
            
            if map_name_span:
                map_name = map_name_span.get_text(strip=True)
                
                # Inicializar la lista de bosses para este mapa
                if map_name not in maps_data:
                    maps_data[map_name] = []
                
                # Buscar el contenedor de datos (div con p-3 o p-4)
                data_container = section.find('div', class_='mt-2')
                if data_container:
                    # Buscar todas las filas de bosses
                    boss_rows = data_container.find_all('div', recursive=False)
                    
                    for row in boss_rows:
                        # Verificar que sea una fila de datos válida
                        if 'grid' in row.get('class', []) and 'grid-cols-12' in row.get('class', []):
                            # Buscar las 3 columnas principales
                            columns = row.find_all('div', recursive=False)
                            
                            if len(columns) >= 3:
                                # Columna 1: Nombre del boss
                                boss_name = None
                                boss_col = columns[0]
                                boss_span = boss_col.find('span', class_='font-medium')
                                if boss_span:
                                    boss_name = boss_span.get_text(strip=True)
                                
                                # Columna 2: Porcentaje de spawn
                                spawn_percentage = None
                                spawn_col = columns[1]
                                # Buscar el div que contiene el porcentaje
                                percent_div = spawn_col.find('div', class_='text-slate-100')
                                if not percent_div:
                                    percent_div = spawn_col.find('div', string=lambda text: text and '%' in text)
                                if percent_div:
                                    spawn_percentage = percent_div.get_text(strip=True)
                                
                                # Columna 3: Locaciones
                                locations = []
                                loc_col = columns[2]
                                location_spans = loc_col.find_all('span', class_='px-2')
                                for loc_span in location_spans:
                                    loc_text = loc_span.get_text(strip=True)
                                    locations.append(loc_text)
                                
                                # Solo agregar si encontramos al menos el nombre del boss
                                if boss_name:
                                    boss_info = {
                                        'boss': boss_name,
                                        'spawn_chance': spawn_percentage if spawn_percentage else 'N/A',
                                        'locations': locations if locations else []
                                    }
                                    maps_data[map_name].append(boss_info)
    
    # Crear el JSON final
    result = {
        'maps': maps_data,
        'total_maps': len(maps_data),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Guardar en archivo JSON
    with open('tarkov_boss_spawns.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen en consola
    print("=" * 80)
    print("DATOS DE SPAWN DE BOSSES EN TARKOV - GUARDADOS EN JSON")
    print("=" * 80)
    print(f"\nArchivo generado: tarkov_boss_spawns.json")
    print(f"Total de mapas: {result['total_maps']}")
    print(f"Timestamp: {result['timestamp']}")
    print("\nResumen por mapa:")
    for map_name, bosses in maps_data.items():
        print(f"  {map_name}: {len(bosses)} boss(es)")
    
    # Mostrar también el JSON en consola
    print("\n" + "=" * 80)
    print("CONTENIDO DEL JSON:")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
        
finally:
    driver.quit()
