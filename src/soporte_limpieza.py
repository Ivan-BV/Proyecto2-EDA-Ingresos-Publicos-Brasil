import pandas as pd
from src.soporte_variables import cambio_nombre_columnas

def funcion(n):
    """hola

    Args:
        n (int): numero
    """
    return n

def nombrecolumnas(dataframe, cambio_nombre_columnas):
    return pd.DataFrame(dataframe).rename(columns = cambio_nombre_columnas, inplace = True)