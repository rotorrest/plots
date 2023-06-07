import pandas as pd
import datetime
from collections import defaultdict

from typing import Dict, Any, List, Union, Tuple


def calculate_weeks(df):
    # Use current date
    today = pd.to_datetime("today")

    # Calculate the start date of the current week (Monday)
    start_date_this_week = today - pd.DateOffset(days=today.weekday())

    # Calculate the end date of the current week (Sunday)
    end_date_this_week = start_date_this_week + pd.DateOffset(days=6)

    # Calculate the end date of the last week
    end_date_last_week = start_date_this_week - pd.DateOffset(days=1)

    # Calculate the start date of the last week
    start_date_last_week = end_date_last_week - pd.DateOffset(days=6)

    # Create masks for the current week and last week
    mask_this_week = (df["Fecha"] >= start_date_this_week) & (df["Fecha"] <= end_date_this_week)
    mask_last_week = (df["Fecha"] >= start_date_last_week) & (df["Fecha"] <= end_date_last_week)

    return (
        mask_this_week,
        mask_last_week,
        start_date_this_week,
        end_date_this_week,
        start_date_last_week,
        end_date_last_week,
    )


# Main functions
def calculate_sales_by_day_of_the_week(sales_df: pd.DataFrame):
    """
    Calculate sales data by day of the week for the given DataFrame.

    Args:
        sales_df (pd.DataFrame): The pandas DataFrame containing sales data.

    Returns:
        dict: A dictionary containing sales data by day of the week along with
              start and end dates of this week and last week.
    """
    # Assuming the dataset is stored in a pandas DataFrame called 'sales_df'
    
    # Calculate the masks and weeks as you've done in the calculate_weeks function.
    mask_this_week, mask_last_week, start_date, end_date, start_date_last_week, end_date_last_week = calculate_weeks(sales_df)

    # List to store the output for each day of the week
    output_list = []

    # Define the days of the week
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Print the tail of the sales_df DataFrame to inspect the last 100 rows

    for day in days_of_week:
        # Filter data for this week and last week
        filter_this_week = mask_this_week & (sales_df['Fecha'].dt.strftime('%A') == day)
        filter_last_week = mask_last_week & (sales_df['Fecha'].dt.strftime('%A') == day)
        
        df_this_week = sales_df.loc[filter_this_week]
        df_last_week = sales_df.loc[filter_last_week]

        # Calculate sales and predictions for this week and last week
        sales_this_week = df_this_week['Ventas'].sum()
        prediction_this_week = df_this_week['Prediccion'].sum()
        sales_last_week = df_last_week['Ventas'].sum()
        prediction_last_week = df_last_week['Prediccion'].sum()

        # Create the dictionary for this day and append to the output list
        day_data = {
            'Day_of_Week': day,
            'Sales this week': sales_this_week,
            'Prediction this week': prediction_this_week,
            'Sales last week': sales_last_week,
            'Prediction last week': prediction_last_week
        }
        output_list.append(day_data)

    return {
        "days_data": output_list,
        "start_date": start_date.strftime("%d%m%Y"),
        "end_date": end_date.strftime("%d%m%Y"),
        "start_date_last_week": start_date_last_week.strftime("%d-%m-%Y"),
        "end_date_last_week": end_date_last_week.strftime("%d-%m-%Y")
    }


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

def calculate_sales_by_month(sales_df: pd.DataFrame) -> List[Dict[str, Union[str, float]]]:
    """
    Calculate the total sales for each product by month.

    Args:
        sales_df (pd.DataFrame): The pandas DataFrame containing sales data.

    Returns:
        List[Dict[str, Union[str, float]]]: A list of dictionaries, each containing
            'Fecha' (date in 'YYYY-MM' format) and sales data for each product.
    """
    # Group by 'Producto' and 'Fecha' and sum the 'Ventas' column
    monthly_sum = sales_df.groupby(['Producto', sales_df['Fecha'].dt.to_period('M')])['Ventas'].sum().reset_index()

    # Convert the Period object to string in 'YYYY-MM' format
    monthly_sum['Fecha'] = monthly_sum['Fecha'].astype(str)
    monthly_sum['Fecha'] = pd.to_datetime(monthly_sum['Fecha'])
    monthly_sum["Fecha"] = monthly_sum["Fecha"].dt.date

    # Pivot the DataFrame to have Producto as columns and Fecha as rows, with Ventas as values
    pivot_table = monthly_sum.pivot_table(index='Fecha', columns='Producto', values='Ventas', fill_value=0)

    # Convert the pivot table to a list of dictionaries with the desired format
    return pivot_table.reset_index().to_dict(orient='records')

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


def calculate_sale_by_region_group_by_date(df):
    """
    Process the dataframe by region, filtering out future dates and storing the sales data.

    Args:
        df (pandas.DataFrame): Input dataframe containing sales data.

    Returns:
        list: List of dictionaries containing the processed sales data for each week.
    """

    data = []

    # Unique products in the dataframe
    unique_products = df["Producto"].unique()

    # Group the dataframe by region
    grouped_df = df.groupby("Región")

    # Get the current date
    current_date = datetime.date.today()

    region_data = {}

    # Iterate over the groups
    for region, group in grouped_df:
        # Iterate over the rows in the group
        for index, row in group.iterrows():
            date = row["Fecha"].strftime("%Y-%m-%d")
            ventas = float(row["Ventas"])

            # Check if the date is valid (before or equal to the current date)
            if datetime.datetime.strptime(date, "%Y-%m-%d").date() <= current_date:
                # Check if the data for the current week already exists in 'data' list
                week_start_date = pd.to_datetime(date).to_period("W").start_time.date()
                existing_data = next((d for d in data if d["start_date"] == week_start_date), None)

                if existing_data:
                    existing_data[row["Producto"]] = ventas
                else:
                    product_data = {
                        "start_date": week_start_date
                    }
                    for prod in unique_products:
                        product_data[prod] = 0 if prod != row["Producto"] else ventas
                    data.append(product_data)

        # Assign the region's data to the dictionary
        region_data[region] = data

    for i in region_data:
        # Create a dictionary to store the sum of sales for each product per week
        sum_sales_by_week = defaultdict(lambda: defaultdict(float))

        # Iterate through the data and sum the sales for each product per week
        for record in region_data[i]:
            start_date = record["start_date"]
            for product, sales in record.items():
                if product != "start_date":
                    sum_sales_by_week[start_date][product] += sales

        region_data[i] = [
            {"date": start_date, **sales_data}
            for start_date, sales_data in sum_sales_by_week.items()
        ]

    return region_data

def calculate_this_last_week_sales_vs_prediction(df):
    """
    Calculate sales and prediction data for this week and last week and their percentage difference.

    Parameters:
        df (pandas.DataFrame): The input DataFrame containing sales and prediction data.

    Returns:
        dict: A dictionary containing aggregated sales and prediction data for each region and product
              for this week and last week, along with their percentage difference. The dictionary is
              structured as follows:
              {
                region: {
                    'This week': {
                        'Ventas': Total sales for this week,
                        'Prediccion': Total prediction for this week,
                        'Percentage': Percentage difference between sales and prediction for this week
                    },
                    'Last week': {
                        'Ventas': Total sales for last week,
                        'Prediccion': Total prediction for last week,
                        'Percentage': Percentage difference between sales and prediction for last week
                    }
                },
                'Start Date': Start date of this week (datetime),
                'End Date': End date of this week (datetime),
                'Start Date Last Week': Start date of last week (datetime),
                'End Date Last Week': End date of last week (datetime)
              }

    This function takes a DataFrame containing sales and prediction data, filters it for the current week
    and the previous week, groups the data by 'Región' and 'Producto', and calculates the sum of 'Ventas'
    and 'Prediccion' for each combination. It then calculates the percentage difference between sales and
    prediction for each region and product for both this week and last week. The result is returned in a
    structure
    """

    # Applying the function to get the masks and dates
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    (
        mask_this_week,
        mask_last_week,
        start_date,
        end_date,
        start_date_last_week,
        end_date_last_week,
    ) = calculate_weeks(df)

    # Filter the data for this week and last week
    data_this_week = df[mask_this_week]
    data_last_week = df[mask_last_week]

    # Group the data by 'Región' and 'Producto' and calculate the sum of 'Ventas' and 'Prediccion' for each combination
    ventas_this_week_by_region = data_this_week.groupby(["Región", "Producto"])[
        "Ventas"
    ].sum()
    prediccion_this_week_by_region = data_this_week.groupby(["Región", "Producto"])[
        "Prediccion"
    ].sum()
    ventas_last_week_by_region = data_last_week.groupby(["Región", "Producto"])[
        "Ventas"
    ].sum()
    prediccion_last_week_by_region = data_last_week.groupby(["Región", "Producto"])[
        "Prediccion"
    ].sum()

    # Create dictionaries for each week with regions as keys
    this_week_data_by_region = {
        region: {
            "This week": {
                "Ventas": ventas_this_week_by_region.get((region, "Producto A"), 0),
                "Prediccion": prediccion_this_week_by_region.get(
                    (region, "Producto A"), 0
                ),
                "Percentage": 0.0,  # Initialize percentage to 0, we'll calculate it later
            },
            "Last week": {
                "Ventas": ventas_last_week_by_region.get((region, "Producto A"), 0),
                "Prediccion": prediccion_last_week_by_region.get(
                    (region, "Producto A"), 0
                ),
                "Percentage": 0.0,  # Initialize percentage to 0, we'll calculate it later
            },
        }
        for region in df["Región"].unique()
    }

    # Calculate percentage for each region's data for this week and last week
    for region in this_week_data_by_region:
        ventas_this_week = this_week_data_by_region[region]["This week"]["Ventas"]
        prediccion_this_week = this_week_data_by_region[region]["This week"][
            "Prediccion"
        ]
        if prediccion_this_week != 0:
            percentage_this_week = (ventas_this_week / prediccion_this_week) * 100
            this_week_data_by_region[region]["This week"]["Percentage"] = round(
                percentage_this_week, 2
            )

        ventas_last_week = this_week_data_by_region[region]["Last week"]["Ventas"]
        prediccion_last_week = this_week_data_by_region[region]["Last week"][
            "Prediccion"
        ]
        if prediccion_last_week != 0:
            percentage_last_week = (ventas_last_week / prediccion_last_week) * 100
            this_week_data_by_region[region]["Last week"]["Percentage"] = round(
                percentage_last_week, 2
            )

    this_week_data_by_region["Start Date"] = start_date
    this_week_data_by_region["End Date"] = end_date
    this_week_data_by_region["Start Date Last Week"] = start_date_last_week
    this_week_data_by_region["End Date Last Week"] = end_date_last_week

    return this_week_data_by_region
