import pandas as pd
import datetime

from pandas.tseries.offsets import DateOffset
from typing import Dict, Any, List

# Auxiliary function

def calculate_weeks(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    """
    Calculate the masks for the current week and last week in the dataframe based on 'Fecha' column.
    
    The function determines the start and end dates of the current week and the previous week. 
    Then it creates boolean masks for the records belonging to the current week and the last week.
    
    Args:
        df (pd.DataFrame): Input dataframe. It should contain a 'Fecha' column with datetime type.
        
    Returns:
        tuple: A tuple containing six elements:
            - mask_this_week (pd.Series): A boolean Series for the records in the current week.
            - mask_last_week (pd.Series): A boolean Series for the records in the last week.
            - start_date (pd.Timestamp): The start date of the current week.
            - end_date (pd.Timestamp): The end date of the current week.
            - start_date_last_week (pd.Timestamp): The start date of the last week.
            - end_date_last_week (pd.Timestamp): The end date of the last week.
    """
    # Use current date
    end_date = pd.to_datetime("today")

    # Calculate the start date of the current week
    start_date = end_date - pd.DateOffset(days=end_date.weekday())

    # Calculate the end date of the last week
    end_date_last_week = start_date - pd.DateOffset(days=1)

    # Calculate the start date of the last week
    start_date_last_week = end_date_last_week - pd.DateOffset(days=6)

    # Create masks for the current week and last week
    mask_this_week = (df["Fecha"] >= start_date) & (df["Fecha"] <= end_date)
    mask_last_week = (df["Fecha"] >= start_date_last_week) & (df["Fecha"] <= end_date_last_week)

    return mask_this_week, mask_last_week, start_date, end_date, start_date_last_week, end_date_last_week



# Main functions

def calculate_current_and_previous_week_sales(sales_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Task 1.a: Bar Chart: Visualize the total sales for the current week and the previous week using a bar chart.
    """
    # Filter out rows where 'Ventas' is 0
    sales_df = sales_df[sales_df["Ventas"] != 0]

    (
        mask_this_week,
        mask_last_week,
        start_date,
        end_date,
        start_date_last_week,
        end_date_last_week,
    ) = calculate_weeks(sales_df)

    # Calculate the total sales for each week
    sales_this_week = sales_df.loc[mask_this_week, "Ventas"].sum()
    sales_last_week = sales_df.loc[mask_last_week, "Ventas"].sum()

    # Define date format
    date_format = "%d/%m/%Y"

    # Prepare data for bar plot
    data: List[Dict[str, Any]] = [
        {
            "Semana": f"Semana Pasada \n {start_date_last_week.strftime(date_format)} - {end_date_last_week.strftime(date_format)}",
            "Ventas": sales_last_week,
        },
        {
            "Semana": f"Semana Actual \n {start_date.strftime(date_format)} - {end_date.strftime(date_format)}",
            "Ventas": sales_this_week,
        },
    ]

    # Prepare title with date range information
    title = f"Ventas totales hasta {end_date.strftime(date_format)}"

    return {"data": data, "title": title}


def calculate_data_indicators(df):
    """
    Task 1.b: Indicators: Visualize the total sales for the current week using indicators.
    """
    # Preprocessing
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Replace the sales of 0 by the prediction on future dates
    mask_future_dates_and_zero_sales = (df["Fecha"] > pd.to_datetime("today")) & (
        df["Ventas"] == 0
    )
    df.loc[mask_future_dates_and_zero_sales, "Ventas"] = df.loc[
        mask_future_dates_and_zero_sales, "Prediccion"
    ]

    # Calculate the mask for this week
    mask_this_week, _, _, _, _, _ = calculate_weeks(df)

    # Calculate the sales and predictions per product for the current week
    sales_this_week_per_product = (
        df.loc[mask_this_week].groupby("Producto")["Ventas"].sum()
    )
    predictions_this_week_per_product = (
        df.loc[mask_this_week].groupby("Producto")["Prediccion"].sum()
    )

    # Combine the data into a single DataFrame
    sales_comparison = pd.concat(
        [sales_this_week_per_product, predictions_this_week_per_product], axis=1
    )
    sales_comparison.columns = ["Ventas Semana Actual", "Prediccion Semana Actual"]

    # Reset the index to make 'Producto' a column
    sales_comparison = sales_comparison.reset_index()
    sales_comparison = sales_comparison.fillna(0)

    # Create the list of indicators for visualization
    data_indicator = []

    for idx, row in sales_comparison.iterrows():
        indicator = {}
        indicator["description"] = row["Producto"]
        indicator["title"] = "Ventas semanales"
        indicator["value"] = (
            row["Ventas Semana Actual"] - row["Prediccion Semana Actual"]
        )

        if row["Ventas Semana Actual"] < row["Prediccion Semana Actual"]:
            indicator[
                "color"
            ] = "error"  # Red if actual sales are less than predictions
        else:
            indicator[
                "color"
            ] = "success"  # Green if actual sales are equal to or greater than predictions
        data_indicator.append(indicator)

    return data_indicator


def calculate_sales_percentage_by_region(sales_df: pd.DataFrame) -> list:
    """
    Task 2: Pie Chart: Visualize the percentage of sales by region.

    Args:
        sales_df (pd.DataFrame): Dataframe with sales data. It must have 'Región' and 'Ventas' columns.

    Returns:
        list: A list of dictionaries where each dictionary represents a region
              and its corresponding sales percentage.
    """
    # Calculate the total sales by region
    sales_by_region = sales_df.groupby("Región")["Ventas"].sum().reset_index()

    # Calculate total sales
    total_sales = sales_df["Ventas"].sum()

    # Calculate the percentage for each region
    sales_by_region["Percentage"] = (
        sales_by_region["Ventas"] / total_sales * 100
    ).round(3)

    # Only return the region and the percentage
    return sales_by_region[["Región", "Percentage"]].to_dict("records")


def calculate_sales_prediction(sales_df: pd.DataFrame) -> dict:
    # Use a boolean mask to replace 'Ventas' values with 'Prediccion' values where 'Ventas' is 0
    mask_zero_before = sales_df["Ventas"] == 0.0
    sales_df.loc[mask_zero_before, "Ventas"] = sales_df.loc[
        mask_zero_before, "Prediccion"
    ]

    # Reshape the dataframe so that each product is a column, and fill any null values with 0s
    sales_df_pivot = (
        sales_df.pivot_table(
            index="Fecha", columns="Producto", values="Ventas", aggfunc="sum"
        )
        .fillna(0)
        .astype(int)
    )

    # Convert the reshaped dataframe to a list of dictionaries
    sales_list = [
        {"date": k.to_pydatetime().date(), **v}
        for k, v in sales_df_pivot.to_dict("index").items()
    ]

    # Calculate the difference in points (number of records) between the current date and the latest date in data
    current_date = datetime.date.today()
    nearest_past_date = max(
        date for date in [item["date"] for item in sales_list] if date <= current_date
    )

    try:
        nearest_past_date_index = next(
            i for i, item in enumerate(sales_list) if item["date"] == nearest_past_date
        )
        num_predicted_dates = len(sales_list) - nearest_past_date_index - 1
    except StopIteration:
        num_predicted_dates = 0  # Default value if no date found in sales_list

    return {"data": sales_list, "num_predicted_dates": num_predicted_dates}


def calculate_sales_per_month(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Task 4: Line Chart: Visualize the evolution of total annual sales over the months of the year
    (from January to December) using a line chart. That is, the chart's legend will be the years and the 'x' axis
    will be the names of the months.

    Args:
        sales_df (pd.DataFrame): Dataframe with sales data. It must have 'Fecha' and 'Ventas' columns.

    Returns:
        pd.DataFrame: A pivot dataframe that represents total sales per month for each year.
    """
    # Ensure that 'Fecha' is datetime
    sales_df["Fecha"] = pd.to_datetime(sales_df["Fecha"])

    # Extract year and month from 'Fecha'
    sales_df["Year"] = sales_df["Fecha"].dt.year
    sales_df["Month"] = sales_df["Fecha"].dt.month_name()

    # Group by year and month, sum the sales
    sales_per_month = sales_df.groupby(["Year", "Month"])["Ventas"].sum().reset_index()

    # Create a pivot table
    pivot_sales = sales_per_month.pivot(index="Month", columns="Year", values="Ventas")

    # Sort the index to make sure months are in correct order
    month_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    pivot_sales = pivot_sales.reindex(month_order)

    # Replace NaN values with 0
    pivot_sales = pivot_sales.fillna(0)

    # Get the current year
    current_year = datetime.datetime.now().year

    # Drop the columns that are greater than the current year
    pivot_sales = pivot_sales.loc[:, pivot_sales.columns <= current_year]

    # Reset the index to move "Month" from index to a column
    pivot_sales = pivot_sales.reset_index()

    # Convert all column names to strings
    pivot_sales.columns = pivot_sales.columns.astype(str)

    return pivot_sales
