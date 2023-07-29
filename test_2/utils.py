import pandas as pd
import datetime as dt


def generate_plot_data(df):
    # Convertir la columna 'Fecha' al tipo de dato datetime
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Usar una tabla pivot para agrupar por 'Fecha' y 'Producto', y sumar las ventas
    ventas_diarias = (
        df[df["Ventas"] > 0]
        .pivot_table(
            index="Fecha",
            columns="Producto",
            values="Ventas",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )

    # Convertir el resultado a una lista de diccionarios
    data = ventas_diarias.to_dict("records")

    return data


def totales_diarios(df):
    # Asegúrate de que la columna 'Fecha' es de tipo datetime
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Agrupa los datos por fecha y suma las ventas para cada día
    totales_diarios = df.groupby("Fecha")["Ventas"].sum().reset_index()
    # Asegurarse de que la fecha se convierta al formato correcto para la API de Shimoku

    data = totales_diarios.to_dict("records")

    return data


def total_semanal(df):
    # Suponiendo que 'df' es tu DataFrame
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Fecha actual y fecha de inicio (hace 10 semanas)
    hoy = pd.Timestamp(dt.date.today())  # Ahora es del tipo datetime64[ns]
    fecha_inicial = hoy - pd.DateOffset(
        weeks=10
    )  # Fecha inicial hace 10 semanas, también datetime64[ns]

    df_10_semanas = df[(df["Fecha"] >= fecha_inicial) & (df["Fecha"] <= hoy)]

    # Calculamos las ventas acumuladas
    df_10_semanas = df_10_semanas.sort_values(by="Fecha")
    df_10_semanas["acumulado"] = df_10_semanas["Ventas"].cumsum()

    # Creamos el diccionario
    dict_list = [
        {"Fecha": row["Fecha"], "acumulado": row["acumulado"]}
        for index, row in df_10_semanas.iterrows()
    ]

    # Verifica tu salida
    return dict_list
