import pandas as pd
import random
from datetime import datetime, timedelta


def generar_datos_ventas(num_registros=1000):
    # Generar fechas diarias para un rango específico
    fecha_inicial = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=num_registros)
    fechas = [fecha_inicial + timedelta(days=i) for i in range(num_registros)]

    # Generar datos de ventas aleatorias por producto y día
    productos = ["Producto A", "Producto B", "Producto C", "Producto D"]
    regiones = ["Región 1", "Región 2", "Región 3", "Región 4"]
    ventas = []
    for fecha in fechas:
        for producto in productos:
            num_lineas = random.randint(
                1, 5
            )  # Generar un número aleatorio de líneas por producto y día
            for _ in range(num_lineas):
                venta = {
                    "Fecha": fecha,
                    "Producto": producto,
                    "Ventas": random.randint(100, 1000),
                    "Región": random.choice(regiones),
                    "Prediccion": random.randint(50, 900),  # Valor predicho ficticio
                }
                ventas.append(venta)

    # Generar datos de predicción para los próximos 6 meses
    fecha_actual = fechas[-1]
    for _ in range(6):
        fecha_actual += timedelta(days=30)  # Avanzar 30 días para el siguiente mes
        for producto in productos:
            for region in regiones:
                venta_prediccion = {
                    "Fecha": fecha_actual,
                    "Producto": producto,
                    "Ventas": None,  # Valor de ventas faltante (NaN)
                    "Región": region,
                    "Prediccion": random.randint(50, 900),  # Valor predicho ficticio
                }
                ventas.append(venta_prediccion)

    # Convertir los datos en un DataFrame de Pandas
    df_ventas = pd.DataFrame(ventas)
    return df_ventas
