import sys
import requests
import pandas as pd
import json

class GooglePlacesAPI:
    def __init__(self,keyword, radius, location):
        '''
        Init donde pongo los parametros que voy modificando asi la api
        no devuelve los mismos resultados
        '''
        self.location = location
        self.radius = radius
        self.keyword = keyword
        self.places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        self.params = {
            "location": location,
            "radius": self.radius,
            "key": "AIzaSyB2v7bruAooTsZ1Xj_B022vn9I4F3SeDMQ",
            "fields": "place_id",
            "keyword": self.keyword,
        }
        self.session = requests.Session()

    def search_places(self):
        '''
        Esta funcion nos devuelve una lista con distitos place_id
        '''
        response = self.session.get(self.places_url, params=self.params, headers={'cache-control': 'no-cache'})
        if response.status_code == 200:
            results = response.json()["results"]
            place_ids = []
            for result in results:
                place_ids.append(result["place_id"])
            return place_ids

    def get_place_details(self, place_id):
        '''
        Funcion que se utiliza para obtener mas data de cada place_id que le coloques como 
        parámetro retorna en formato datadrame de pandas.
        '''
        params = {
            "place_id": place_id,
            "region": "NY",
            "key": "AIzaSyB2v7bruAooTsZ1Xj_B022vn9I4F3SeDMQ",
            "fields": "name,geometry,rating,adr_address,types,place_id,url,delivery,takeout,serves_breakfast,serves_dinner,serves_lunch",
            "keyword": "restaurant",
        }
        response = requests.get(self.details_url, params=params, headers={'cache-control': 'no-cache'})
        data = response.json()["result"]

        if "rating" in data:
            avg_rating = data["rating"]
        else:
            avg_rating = None

        df_dict = {                           # Diccionario con la data que preciso extraer
            "name": data["name"],
            "coordenada": f'{data["geometry"]["location"]["lat"]}, {data["geometry"]["location"]["lng"]}',
            "category": ", ".join(data["types"]),
            "gmap_id": data["place_id"],
            "address": data["adr_address"],
            "avg_rating": avg_rating,            
            "url": f"https://www.google.com/maps/place/?q=place_id:{data['place_id']}",
            "delivery": str(data.get("delivery", False)),
            "takeout": str(data.get("takeout", False)),
            "serves_breakfast": str(data.get("serves_breakfast", False)),
            "serves_lunch": str(data.get("serves_lunch", False)),
            "serves_dinner": str(data.get("serves_dinner", False))
        }
        df = pd.DataFrame(df_dict, index=[0])
        return df

    def search_and_fetch_data(self):
        '''
        Funcion para ejecutar las demas funciones en secuencia.
        '''
        place_ids = self.search_places()
        df_final = None
        for place_id in place_ids:
            df = self.get_place_details(place_id)
            if df_final is None:
                df_final = df
            else:
                df_final = pd.concat([df_final, df])
        return df_final

list_rest = ['Coffee shop', 'Cafe', 'Fast food restaurant', 'Chinese restaurant', 'Pizza restaurant', 'Auto repair shop', 'Nail salon','Barber shop', 'Gas station', 'Beauty salon', 'Hair salon', 'Auto body shop', 'Tattoo shop', 'Bakery','Restaurant']
list_location = ['40.7047,-74.0122',
                '40.7192,-73.9864',
                '40.7251,-73.9924',
                '40.7418,-73.9893',
                '40.7614,-73.9776',
                '40.7777,-73.9522',
                '40.7862,-73.9750',
                '40.8044,-73.9364',
                '40.8076,-73.9635',
                '40.8150,-73.9512',
                '40.8283,-73.9438',
                '40.8425,-73.9382',
                '40.8526,-73.9307',
                '40.8583,-73.8693',
                '40.8645,-73.8256',
                '40.8626,-73.7872',
                '40.8599,-73.7589',
                '40.8467,-73.7427',
                '40.8257,-73.7359',
                '40.8064,-73.7474',
                '40.7874,-73.7697',
                '40.7709,-73.7899',
                '40.7533,-73.8072',
                '40.7326,-73.8072',
                '40.7206,-73.8244',
                '40.7047,-73.8272',
                '40.6874,-73.8121',
                '40.6672,-73.8046',
                '40.6456,-73.7927',
                '40.6338,-73.7776',
                '40.6136,-73.7614',
                '40.5974,-73.7564',
                '40.5852,-73.7495',
                '40.5741,-73.7323',
                '40.5641,-73.7159',
                '40.5557,-73.6980',
                '40.5500,-73.6738',
                '40.5411,-73.6486',
                '40.5316,-73.6286',
                '40.5216,-73.6149',
                '40.5088,-73.5949',
                '40.5023,-73.5671',
                '40.4905,-73.5471',
                '40.4843,-73.5229',
                '40.4763,-73.5003',
                '40.4708,-73.4767',
                '40.4637,-73.4509',
                '40.4546,-73.4267',
                '40.4441,-73.4104',
                '40.4341,-73.3941',
                '40.4219,-73.3749',
                '40.4128,-73.3576',
                '40.4006,-73.3404',
                '40.3939,-73.3204']

dataframes = {} # Crear un diccionario vacío

for index1, category in enumerate(list_rest):
    for index2, location in enumerate(list_location):
        api_result = GooglePlacesAPI(category, 5000, location).search_and_fetch_data()
        df_name = f"df_{index1}-{index2}" # Crear un nombre para el dataframe basado en el índice
        dataframes[df_name] = api_result # Agregar el dataframe al diccionario

df = pd.concat(dataframes.values(), axis=0)

# ETL

df.drop_duplicates(subset=['gmap_id'], inplace=True)

df = df.reset_index(drop=True)

# Divide la columna "coordenada" en dos columnas
df[['latitud', 'longitud']] = df['coordenada'].str.split(',', expand=True)

# Convierte las columnas "latitud" y "longitud" a tipo numérico
df['latitude'] = pd.to_numeric(df['latitud'])
df['longitude'] = pd.to_numeric(df['longitud'])

df = df[['gmap_id','name', 'address','longitude', 'latitude', 'avg_rating', 'category', 'delivery', 'takeout', 'serves_breakfast', 'serves_lunch', 'serves_dinner']]

df = df.dropna(subset=['avg_rating'])

# Convierte a float32 para que sea el mismo float de athena
df['latitude'] = df['latitude'].astype('float32')
df['longitude'] = df['longitude'].astype('float32')
df['avg_rating'] = df['avg_rating'].astype('float32')

import re

# Define una función que utiliza expresiones regulares para extraer la información necesaria
def clean_address(address):
    address = re.sub('<.*?>', '', address) # Elimina las etiquetas HTML
    address = re.sub('\s+', ' ', address) # Elimina los espacios en blanco adicionales
    address = address.strip() # Elimina los espacios en blanco al principio y al final
    return address

# Aplica la función a la columna "address" del DataFrame
df['address'] = df['address'].apply(clean_address)

import boto3

def name_file():
    # Definimos el nombre del bucket S3 y la ruta a la carpeta que deseamos listar
    bucket_name = 'stagedata-bucket00'
    folder_path = 'metadata/metada_newyork/'

    # Creamos el cliente de S3 y listamos los archivos en la ruta especificada
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)

    # Extraemos el nombre del último archivo existente en la ruta
    last_file_name = response['Contents'][-2]['Key']
    if 'part-' not in last_file_name:
        archivo = last_file_name.split("/")[-1]  # Selecciona el anteultimo elemento de la lista
        numero = archivo[-11:-8]
        new_file_num = int(numero) + 1
        print(new_file_num)
    
        # Creamos el nombre del nuevo archivo
        new_file_name = f"s3://stagedata-bucket00/{folder_path}metadata00{new_file_num}.parquet"
    else:
        new_file_name = f"s3://stagedata-bucket00/{folder_path}metadata001.parquet"
    return new_file_name
    
file_name = name_file()   

df.to_parquet(file_name)