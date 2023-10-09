import folium
import socket
import requests
import xml.etree.ElementTree as ET
import mysql.connector

#Diseño de Codigo
#1-obtener Datos
#2-verificar datos(coordenadas y url)
#3-imprimir mapa

# Configura la conexión a la base de datos
host = "localhost"  # URL o IP interna de la base de datos
database = "qqra"       # Nombre de la base de datos
user = "qqra"                 # Usuario de la base de datos
password = "qqra"           # Contraseña de la base de datos


# Inicializa diccionarios para almacenar los datos
datos = {"nombre":{}, "domicilio": {}, "latitud": {}, "longitud": {}, "url": {}, "estado":{}}
emisoras = []

######----1 OBTENER DATOS
def traer_datos():
    try:
        # Establece la conexión a la base de datos MySQL
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()

                # Consulta SQL
            query = """SELECT
                            a.Emisoras_Id,
                            c.EmisorasItems_Id,
                            a.Emisoras_Sigla,
                            b.EmisorasDatos_Dato,
                            c.EmisorasItems_Item
                        FROM
                            LRA1e_Emisoras AS a
                        JOIN
                            LRA1e_Emisoras_Datos AS b ON a.Emisoras_Id = b.EmisorasDatos_Emisora_Id
                        JOIN
                            LRA1e_Emisoras_Items AS c ON b.EmisorasDatos_Item_Id = c.EmisorasItems_Id
                        WHERE
                            c.EmisorasItems_Id IN (1, 3, 5, 19)
                        ORDER BY a.Emisoras_Id, c.EmisorasItems_Item;"""

        cursor.execute(query)
        # Recupera los resultados de la consulta
        results = cursor.fetchall()
        
        return(results)

    except mysql.connector.Error as error:
        print(f"Error: {error}")

    finally:
    #if connection.is_connected():
        cursor.close()
        connection.close()

######----2 VERIFICAR DATOS

# def obtener_ips_desde_dns(nombre_de_host):
#     try:
#         ips = socket.gethostbyname_ex(nombre_de_host)
#         print("ips:", str(ips))
#         #return ips[2]  # Devuelve una lista de direcciones IP
#     except socket.gaierror:
#         return [socket.error]


def verificar_sitios(url):
    #for sitio in emisoras:
        try:
            status='white'
            #web=sitio["url"]
            # print(web)
            # ips = obtener_ips_desde_dns(web)
            # print (web,ips)
            # print("Resultado:", str(ips))
            # if ips:
            if url:
                #for ip in ips:
                    # Intenta realizar una solicitud a la IP en lugar de la URL
                    #url = f"{ip}"
                response = requests.get(url)
                if response.status_code == 200:
                    #print(f"{url}")
                    #sitio["estado"]='green';
                    status='green'
                else:
                    #print(f"{sitio} ({ip}) - ({sitio}["estado"]:'red'))
                    #sitio["estado"]='red';
                    status='red'
            else:
                #print(f"No se tiene direccion")
                #sitio["estado"]='white';
                status='orange'
        except requests.RequestException as ex:
#            print(f"{sitio} - {ip} - {ex.response.status_code}")
            print(f"{url} - Error: {ex}")
            #sitio["estado"]='orange';
            status='blue'
        #print(status)
        return(status)

def modelar_datos(info):
        
        for row in info:
            emisoras_id, emisoras_items_id, emisoras_sigla, emisoras_datos_dato, emisoras_items_item = row

            # Verifica si el EmisorasItems_Id es 1, 3, 5 o 19 y almacena los valores en el diccionario por sigla correspondiente
            if emisoras_sigla not in datos:
                datos[emisoras_sigla] = {}
            if emisoras_items_id == 1:
                datos[emisoras_sigla]["domicilio"] = emisoras_datos_dato
            elif emisoras_items_id == 3:
                datos[emisoras_sigla]["latitud"] = emisoras_datos_dato
            elif emisoras_items_id == 5:
                datos[emisoras_sigla]["longitud"] = emisoras_datos_dato
            elif emisoras_items_id == 19:
                datos[emisoras_sigla]["url"] = emisoras_datos_dato
            #print(row)
            
        for sigla, datos_emisora in datos.items():
            # if datos[emisoras_sigla]["Latitud"] != {} and datos[emisoras_sigla]["Latitud"] !=  {} and datos[emisoras_sigla]["Latitud"] !=  {}:
            #     emisora = {"nombre": sigla, **datos_emisora, "estado": "white"}
            #     emisoras.append(emisora)

            if datos_emisora.get("latitud") and datos_emisora.get("longitud"):
                emisora = {"nombre": sigla, **datos_emisora, "estado": "white"}
                emisoras.append(emisora)
        # Ahora, la lista 'emisoras' contiene los datos de cada emisora
        # Puedes imprimir la lista o acceder a los datos de cada emisora según sea necesario.

        return(emisoras)

def verificador(emisoras):
    for emisora in emisoras:
        web = emisora.get('url', '')
     
        # Llama a la función para validar la URL
        std= verificar_sitios(web)
        #print (std)
        emisora['estado'] = std
    return emisoras

######----3 GENERACION DE MAPA
def mapadraw(emisoras):    
    ## Crear un objeto de mapa centrado en una ubicación inicial
    m = folium.Map(location=[emisoras[0]["latitud"], emisoras[0]["longitud"]], zoom_start=6, tiles="https://tiles.openstreetmap.org.ar/{z}/{x}/{y}.png")

    # Agregar marcadores al mapa
    for ubicacion in emisoras:
        folium.Marker(
            location=[ubicacion["latitud"], ubicacion["longitud"]],
            popup=ubicacion["nombre"],
            icon=folium.Icon(ubicacion["estado"])
        ).add_to(m)
    
        # Guardar el mapa en un archivo HTML
    m.save("mapa.html")


###FUNCIONES PRINCIPALES
resultados = traer_datos()
datosemisoras =  modelar_datos(resultados)
infoestado=verificador(datosemisoras)
mapadraw(infoestado)




######----IMPRESION DATOS VERIFICADOR
# emisoras = traer_datos()
# if emisoras:
#     for each in emisoras:
#         print(each)


######----IMPRESION DATOS VERIFICADOR