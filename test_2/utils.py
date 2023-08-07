import pandas as pd
import datetime as dt


def calculate_generate_plot_data(df: pd.DataFrame) -> list:
    """
    Create a dictionary to store the sum of sales for each product per month.

    Parameters:
        df (pd.DataFrame): DataFrame containing sales data, with columns 'Fecha' (Date) and 'Ventas' (Sales).

    Returns:
        list: A list of dictionaries containing the sum of sales for each product per month, in the format:
              [{'Fecha': 'YYYY-MM', 'Product1': sum_sales1, 'Product2': sum_sales2, ...}, ...]
    """
    # Convert the 'Fecha' column to datetime data type
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Group by month and product, and sum the sales
    monthly_sales = (
        df[df["Ventas"] > 0]
        .groupby([pd.Grouper(key="Fecha", freq="M"), "Producto"])
        .agg({"Ventas": "sum"})
        .unstack(fill_value=0)
    )

    # Reset index to convert the DataFrame into a list of dictionaries
    monthly_sales = monthly_sales.reset_index()

    # Convert the DataFrame to a list of dictionaries
    data = monthly_sales.to_dict(orient="records")

    # Convert the list of dictionaries to the desired output format
    output_data = []
    for record in data:
        record_dict = {"Fecha": record[("Fecha", "")]}
        for key, value in record.items():
            if isinstance(key, tuple) and key[0] == "Ventas":
                record_dict[key[1]] = value
        output_data.append(record_dict)

    return output_data


def calculate_monthly_sales(df: pd.DataFrame) -> list:
    """
    Calculate monthly sales and return the data in a list of dictionaries.

    Parameters:
        df (pd.DataFrame): DataFrame with sales data, containing a 'Date' column and a 'Sales' column.

    Returns:
        list: A list of dictionaries with the total monthly sales and dates in 'YYYY-MM-DD' format.
    """
    # Ensure 'Date' is of type datetime
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Group the data by month and sum the sales for each month
    monthly_totals = (
        df.groupby(pd.Grouper(key="Fecha", freq="M"))["Ventas"].sum().reset_index()
    )

    # Remove records with zero sales for future dates
    today = pd.Timestamp(dt.date.today())
    monthly_totals = monthly_totals[monthly_totals["Fecha"] <= today]

    data = monthly_totals.to_dict("records")

    return data


def calculate_cumulative_monthly_sales(df: pd.DataFrame) -> list:
    """
    Calculate cumulative monthly sales and return the data in a list of dictionaries.

    Parameters:
        df (pd.DataFrame): DataFrame with sales data, containing a 'Date' column and a 'Sales' column.

    Returns:
        list: A list of dictionaries with the cumulative monthly sales and dates in 'YYYY-MM-DD' format.
    """
    df["Date"] = pd.to_datetime(df["Fecha"])

    # Get the minimum date in the DataFrame as the initial date
    initial_date = df["Date"].min()

    df_months = df[df["Date"] >= initial_date]

    # Filter rows with sales greater than 0 to avoid zero accumulation in the future
    df_months = df_months[df_months["Ventas"] > 0]

    # Group the data by month and sum the sales for each month
    df_months = (
        df_months.groupby(pd.Grouper(key="Fecha", freq="M"))
        .agg({"Ventas": "sum"})
        .reset_index()
    )

    # Calculate the cumulative sales column
    df_months["cumulative"] = df_months["Ventas"].cumsum()

    # Make sure the date is converted to the correct format for the Shimoku API
    df_months["Date"] = df_months["Fecha"].dt.strftime("%Y-%m-%d")

    # Create the dictionary
    dict_list = [
        {"Fecha": row["Date"], "cumulative": row["cumulative"]}
        for _, row in df_months.iterrows()
    ]
    return dict_list
