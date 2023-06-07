import pandas as pd
import datetime as dt

def generate_plot_data(df):
    # Convertir la columna 'Fecha' al tipo de dato datetime
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Agrupar por mes y producto, y sumar las ventas
    ventas_mensuales = (
        df[df["Ventas"] > 0]
        .groupby([pd.Grouper(key="Fecha", freq="M"), "Producto"])
        .agg({"Ventas": "sum"})
        .unstack(fill_value=0)
    )

    # Reset index to convert the DataFrame into a list of dictionaries
    ventas_mensuales = ventas_mensuales.reset_index()

    # Convert the DataFrame to a list of dictionaries
    data = ventas_mensuales.to_dict(orient="records")

    # Convert the list of dictionaries to the desired output format
    output_data = []
    for record in data:
        record_dict = {"Fecha": record[("Fecha", "")]}
        for key, value in record.items():
            if isinstance(key, tuple) and key[0] == "Ventas":
                record_dict[key[1]] = value
        output_data.append(record_dict)

    return output_data

def venta_mensual(df):
    # Asegúrate de que la columna 'Fecha' es de tipo datetime
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Agrupa los datos por mes y suma las ventas para cada mes
    totales_mensuales = df.groupby(pd.Grouper(key="Fecha", freq="M"))["Ventas"].sum().reset_index()

    # Eliminar los registros con ventas igual a 0 para fechas futuras
    hoy = pd.Timestamp(dt.date.today())
    totales_mensuales = totales_mensuales[totales_mensuales["Fecha"] <= hoy]

    # Asegurarse de que la fecha se convierta al formato correcto para la API de Shimoku
    totales_mensuales["Fecha"] = totales_mensuales["Fecha"].dt.strftime("%Y-%m-%d")

    data = totales_mensuales.to_dict("records")

    return data

def acumulado_mensual(df):
    # Suponiendo que 'df' es tu DataFrame
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Obtener la fecha mínima en el DataFrame como fecha inicial
    fecha_inicial = df["Fecha"].min()

    df_meses = df[(df["Fecha"] >= fecha_inicial)]

    # Filtrar filas con ventas mayores a 0 para evitar la acumulación de ceros en el futuro
    df_meses = df_meses[df_meses["Ventas"] > 0]

    # Agrupar los datos por mes y sumar las ventas para cada mes
    df_meses = df_meses.groupby(pd.Grouper(key="Fecha", freq="M")).agg({"Ventas": "sum"}).reset_index()

    # Calcular la columna de ventas acumuladas
    df_meses["acumulado"] = df_meses["Ventas"].cumsum()

    # Asegurarse de que la fecha se convierta al formato correcto para la API de Shimoku
    df_meses["Fecha"] = df_meses["Fecha"].dt.strftime("%Y-%m-%d")

    # Creamos el diccionario
    dict_list = [{"Fecha": row["Fecha"], "acumulado": row["acumulado"]} for _, row in df_meses.iterrows()]

    return dict_list