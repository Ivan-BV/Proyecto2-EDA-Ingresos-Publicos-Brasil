import pandas as pd
import numpy as np

def nombrecolumnas(dataframe, cambio_nombre_columnas):
    return pd.DataFrame(dataframe).rename(columns = cambio_nombre_columnas)


def cambiar_tipo_columnas(df: pd.DataFrame, cambios: dict):
    """
    Cambia el tipo de dato de las columnas de un DataFrame según el diccionario de cambios dado. 
    Si las columnas contienen valores nulos, se rellenan automáticamente con un valor por defecto antes de la conversión.

    Valores por defecto para columnas con nulos:
    - 'int': se rellenan con -1.
    - 'float': se rellenan con -1.0.
    - 'anio_ejercicio': se rellena con el año extraído de la columna 'fecha_lanzamiento'.

    :param df: DataFrame de pandas a modificar.
    :param cambios: Diccionario con las columnas como llaves y los tipos de datos a convertir como valores. 
                    Ejemplo: {"columna1": "int", "columna2": "float", "columna3": "datetime"}.
    :return: DataFrame con los tipos de columnas actualizados y los nulos rellenados con valores por defecto.
    """
    
    df_copy = df.copy()

    # Primero intento extraer el año del dataframe apoyandome en la columna fecha_lanzamiento si es posible para saber en que df estamos trabajando
    if "fecha_lanzamiento" in df_copy.columns:
        fecha_col = df_copy["fecha_lanzamiento"].astype(str)
        
        # Trato de ver si la columna contiene / o - antes de obtener la fecha
        if fecha_col.str.contains("/").any():
            df_copy["fecha_lanzamiento"] = pd.to_datetime(df_copy["fecha_lanzamiento"], format="%d/%m/%Y")
        elif fecha_col.str.contains("-").any():
            df_copy["fecha_lanzamiento"] = pd.to_datetime(df_copy["fecha_lanzamiento"], format="%Y-%m-%d")
        else:
            df_copy["fecha_lanzamiento"] = pd.to_datetime(df_copy["fecha_lanzamiento"])

        if df_copy["fecha_lanzamiento"].notna().any():
            anio = df_copy["fecha_lanzamiento"].dt.year.mode()[0]  # Como no me funcionaba vi en stackoverflow que si utilizo la moda del valor que más se repite si que funciona
            anio = int(anio) # Tengo que estar haciendo cosas redundantes como esta porque si no me funciona (Igual tengo algo mal en mi vsc)
        else:
            anio = None
    else:
        anio = None

    for columna, nuevo_tipo in cambios.items():
        columna = str(columna)

        if columna in df_copy.columns:
            # Trato de reemplazar las comas por puntos y los strings nan por valor NaN para reemplazarlo posteriormente
            df_copy[columna] = df_copy[columna].astype(str).str.replace(",", ".", case=False, regex=False)
            df_copy[columna] = df_copy[columna].replace("nan", pd.NA)
            df_copy[columna] = df_copy[columna].replace(np.nan, pd.NA)

            if columna == "anio_ejercicio" and anio is not None:
                df_copy[columna].fillna(anio, inplace=True)
                df_copy[columna] = pd.to_numeric(df_copy[columna]).astype(int)

            try:
                if nuevo_tipo == "int":
                    df_copy[columna] = pd.to_numeric(df_copy[columna]).fillna(-1)
                    df_copy[columna] = df_copy[columna].astype(float).astype(int)
                elif nuevo_tipo == "float":
                    df_copy[columna] = pd.to_numeric(df_copy[columna]).fillna(-1.0).astype(float)
                elif nuevo_tipo == "str":
                    df_copy[columna] = df_copy[columna].fillna("Sem informação").astype(str)
                    df_copy[columna].replace("0", "Sem informação")
            except ValueError as error:
                print(f"Error al convertir la columna '{columna}' a {nuevo_tipo}: {error}")
        else:
            print(f"Advertencia: La columna '{columna}' no existe en el DataFrame.")
    
    return df_copy

def codigo_nombre(dataframe: pd.DataFrame, cod: str, nom: str):
    """
    Completa valores nulos en un DataFrame utilizando un mapeo entre dos columnas 
    especificadas (código y nombre). La función busca rellenar los valores faltantes 
    en una columna con los valores correspondientes de la otra columna basada en 
    las combinaciones de códigos y nombres.

    :param dataframe: DataFrame de pandas en el que se desea realizar el mapeo.
    :param cod: Nombre de la columna que contiene los códigos, debe ser una cadena.
    :param nom: Nombre de la columna que contiene los nombres, debe ser una cadena.
    
    :return: DataFrame con los valores nulos de las columnas 'cod' y 'nom' 
             completados según el mapeo.
             
    :raises ValueError: Si 'cod' o 'nom' no son cadenas.
    
    El comportamiento de la función es el siguiente:
    - Si ambos parámetros son cadenas, se crea un mapeo a partir de las combinaciones 
      únicas de códigos y nombres en el DataFrame.
    - Los valores nulos en la columna 'nom' se rellenan usando el mapeo de 'cod'.
    - Los valores nulos en la columna 'cod' se rellenan usando el mapeo de 'nom'.
    """
    if type(cod) == str and type(nom) == str:
        cols0y1 = dataframe[[cod,nom]].drop_duplicates().dropna().to_dict("records")
        mapping = {item[cod]: item[nom] for item in cols0y1}
        dataframe[nom] = dataframe[nom].fillna(dataframe[cod].map(mapping))
        mapping2 = {item[nom]: item[cod] for item in cols0y1}
        dataframe[cod] = dataframe[cod].fillna(dataframe[nom].map(mapping2))
        return dataframe
    else:
        print("Código y número no son strings")