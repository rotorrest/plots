import pandas as pd
import datetime
from collections import defaultdict

from typing import Dict, Any, List, Union, Tuple

# Auxiliary function
def calculate_weeks(
    df: pd.DataFrame,
) -> Tuple[
    pd.Series, pd.Series, pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp
]:
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
    mask_last_week = (df["Fecha"] >= start_date_last_week) & (
        df["Fecha"] <= end_date_last_week
    )

    return (
        mask_this_week,
        mask_last_week,
        start_date,
        end_date,
        start_date_last_week,
        end_date_last_week,
    )


# Main functions
def calculate_current_and_previous_week_sales(sales_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates total sales for the current week and the previous week.

    The function uses the data from the input dataframe to calculate the total sales
    for the current week and the previous week, then prepares the data for visualization
    in a bar chart.

    Args:
        sales_df (pd.DataFrame): The input dataframe, containing the sales data.

    Returns
        dict:
            A dictionary containing two keys: 'data' and 'title'.
            'data' holds a list of dictionaries with sales data for the current and previous weeks.
            'title' is a string for the title of the chart with date range information.
    """

    # Filter out rows where 'Ventas' is 0
    sales_df = sales_df[sales_df["Ventas"] != 0]

    # Use calculate_weeks() function to get masks for current and previous week,
    # and their start and end dates
    (
        mask_this_week,
        mask_last_week,
        start_date,
        end_date,
        start_date_last_week,
        end_date_last_week,
    ) = calculate_weeks(sales_df)

    # Calculate the total sales for each week using the boolean masks
    sales_this_week = sales_df.loc[mask_this_week, "Ventas"].sum()
    sales_last_week = sales_df.loc[mask_last_week, "Ventas"].sum()

    # Define date format for the chart
    date_format = "%d/%m/%Y"

    # Prepare data for bar plot, including week labels and sales data
    data: List[Dict[str, Any]] = [
        {
            "Semana": f"Previous week \n {start_date_last_week.strftime(date_format)} - {end_date_last_week.strftime(date_format)}",
            "Ventas": sales_last_week,
        },
        {
            "Semana": f"Current week \n {start_date.strftime(date_format)} - {end_date.strftime(date_format)}",
            "Ventas": sales_this_week,
        },
    ]

    # Prepare title with date range information for the chart
    title = f"Total sales up to {end_date.strftime(date_format)}"

    return {"data": data, "title": title}


def calculate_data_indicators(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Calculate and visualize the total sales for the current week using indicators.

    The function preprocesses the input dataframe, replaces sales of zero by the
    predicted sales on future dates, calculates the sales and predictions per product
    for the current week, and prepares the data for visualization.

    Args:
        df (pd.DataFrame): The input dataframe, which should include 'Fecha', 'Ventas',
                           'Prediccion', and 'Producto' columns. 'Fecha' should be of datetime type.

    Returns:
        list: A list of dictionaries, each containing the data for one indicator.
    """

    # Convert 'Fecha' column to datetime type
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
        indicator["title"] = "Diferente to match prediccion"
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


def calculate_sales_percentage_by_region(
    sales_df: pd.DataFrame,
) -> List[Dict[str, Union[str, float]]]:
    """
    Calculate and visualize the percentage of sales by region as a pie chart.

    This function takes a sales data DataFrame, groups the data by region, and calculates
    the percentage of total sales for each region. The result is returned as a list of
    dictionaries suitable for visualization.

    Args:
        sales_df (pd.DataFrame): The sales data DataFrame. It should have 'Región' and 'Ventas' columns.

    Returns:
        list: A list of dictionaries, where each dictionary has two keys: 'Región' representing
              the region name, and 'Percentage' representing the percentage of total sales
              for that region.
    """
    # Group the sales data by region and calculate the total sales for each region
    sales_by_region = sales_df.groupby("Región")["Ventas"].sum().reset_index()

    # Calculate the total sales across all regions
    total_sales = sales_df["Ventas"].sum()

    # Calculate the percentage of total sales for each region and add it to the DataFrame as a new column
    sales_by_region["Percentage"] = (
        sales_by_region["Ventas"] / total_sales * 100
    ).round(3)

    # Convert the DataFrame to a list of dictionaries, including only the region and the percentage
    # Each dictionary corresponds to a data entry for visualization
    return sales_by_region[["Región", "Percentage"]].to_dict("records")


def calculate_sales_prediction(
    sales_df: pd.DataFrame,
) -> Dict[str, Union[List[Dict], int]]:
    """
    Calculate sales predictions based on the provided DataFrame.

    This function replaces zero 'Ventas' values with corresponding 'Prediccion' values,
    reshapes the DataFrame to map each product to a column, fills any null values with 0,
    and finally computes the number of predicted dates by finding the difference in
    records between the current date and the latest date in the data.

    Args:
        sales_df (pd.DataFrame): The input sales DataFrame. It should contain 'Ventas',
                                 'Prediccion', 'Fecha', and 'Producto' columns.

    Returns:
        dict: A dictionary containing two keys: 'data' (a list of dictionaries where each
              dictionary represents sales data for a specific date) and 'num_predicted_dates'
              (an integer representing the number of predicted dates).
    """

    # Replace 'Ventas' values with 'Prediccion' values where 'Ventas' is 0
    mask_zero_before = sales_df["Ventas"] == 0.0
    sales_df.loc[mask_zero_before, "Ventas"] = sales_df.loc[
        mask_zero_before, "Prediccion"
    ]

    # Pivot the DataFrame using 'Fecha' as index, 'Producto' as columns and 'Ventas' as values,
    # fill null values with 0 and convert to int
    sales_df_pivot = (
        sales_df.pivot_table(
            index="Fecha", columns="Producto", values="Ventas", aggfunc="sum"
        )
        .fillna(0)
        .astype(int)
    )

    # Convert the reshaped DataFrame to a list of dictionaries
    sales_list = [
        {"date": k.to_pydatetime().date(), **v}
        for k, v in sales_df_pivot.to_dict("index").items()
    ]

    # Define the current date
    current_date = datetime.date.today()

    # Get the most recent past date in the sales list
    nearest_past_date = max(
        date for date in [item["date"] for item in sales_list] if date <= current_date
    )

    # Compute the number of predicted dates by calculating the difference
    # in records between the current date and the latest date in the data
    try:
        nearest_past_date_index = next(
            i for i, item in enumerate(sales_list) if item["date"] == nearest_past_date
        )
        num_predicted_dates = len(sales_list) - nearest_past_date_index - 1
    except StopIteration:
        num_predicted_dates = 0  # Default to 0 if no date found in sales_list

    # Return a dictionary containing the sales list and the number of predicted dates
    return {"data": sales_list, "num_predicted_dates": num_predicted_dates}


def calculate_sales_per_month(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total sales per month for each year.

    This function transforms the input DataFrame to a format where each column represents a year,
    each row represents a month, and cell values represent total sales for the corresponding year and month.
    This transformation facilitates the visualization of annual sales over the months of the year.

    Args:
        sales_df (pd.DataFrame): The input sales DataFrame. It should contain 'Fecha' and 'Ventas' columns.

    Returns:
        pd.DataFrame: A pivot DataFrame where index is 'Month', columns are 'Year',
                      and cell values are the total sales for the corresponding month and year.
    """
    # Ensure 'Fecha' is of datetime type
    sales_df["Fecha"] = pd.to_datetime(sales_df["Fecha"])

    # Extract year and month from 'Fecha'
    sales_df["Year"] = sales_df["Fecha"].dt.year
    sales_df["Month"] = sales_df["Fecha"].dt.month_name()

    # Group data by year and month, calculate total sales
    sales_per_month = sales_df.groupby(["Year", "Month"])["Ventas"].sum().reset_index()

    # Pivot the DataFrame: months as index, years as columns, and sales as values
    pivot_sales = sales_per_month.pivot(index="Month", columns="Year", values="Ventas")

    # Define a list for the correct month order
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

    # Reindex the pivot DataFrame to get months in the correct order
    pivot_sales = pivot_sales.reindex(month_order)

    # Replace NaN values with 0
    pivot_sales = pivot_sales.fillna(0)

    # Get the current year
    current_year = datetime.datetime.now().year

    # Drop the columns that are greater than the current year
    pivot_sales = pivot_sales.loc[:, pivot_sales.columns <= current_year]

    # Reset the index to move 'Month' from index to a column
    pivot_sales = pivot_sales.reset_index()

    # Convert all column names to strings
    pivot_sales.columns = pivot_sales.columns.astype(str)

    return pivot_sales

def calculate_sale_by_region(df):
    """
    Process the dataframe by region, filtering out future dates and storing the sales data.

    Args:
        df (pandas.DataFrame): Input dataframe containing sales data.

    Returns:
        list: List of dictionaries containing the processed sales data for each date.
    """

    data = []

    # Unique products in the dataframe
    unique_products = df['Producto'].unique()

    # Group the dataframe by region
    grouped_df = df.groupby('Región')

    # Get the current date
    current_date = datetime.date.today()

    region_data = {}

    # Iterate over the groups
    for region, group in grouped_df:
        # Iterate over the rows in the group
        for index, row in group.iterrows():
            date = row['Fecha'].strftime('%Y-%m-%d')
            ventas = float(row['Ventas'])

            # Check if the date is valid (before or equal to the current date)
            if datetime.datetime.strptime(date, '%Y-%m-%d').date() <= current_date:
                # Check if the data for the current date already exists in 'data' list
                existing_data = next((d for d in data if d['date'] == date), None)

                if existing_data:
                    existing_data[row['Producto']] = ventas
                else:
                    product_data = {'date': datetime.datetime.strptime(date, '%Y-%m-%d').date()}
                    for prod in unique_products:
                        product_data[prod] = 0 if prod != row['Producto'] else ventas
                    data.append(product_data)

        # Assign the region's data to the dictionary
        region_data[region] = data

    for i in region_data:
        # Create a dictionary to store the sum of sales for each product per date
        sum_sales_by_date = defaultdict(lambda: defaultdict(float))

        # Iterate through the data and sum the sales for each product per date
        for record in region_data[i]:
            date = record['date']
            for product, sales in record.items():
                if product != 'date':
                    sum_sales_by_date[date][product] += sales

        region_data[i] = [{'date': date, **sales_data} for date, sales_data in sum_sales_by_date.items()]

    return region_data