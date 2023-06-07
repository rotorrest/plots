import shimoku_api_python as Shimoku

from dotenv import load_dotenv
from os import getenv
import pandas as pd

from prueba_acceso import generar_datos_ventas
from utils import (
    calculate_sales_percentage_by_region,
    calculate_sales_per_month,
    calculate_sales_by_month,
    calculate_data_indicators,
    calculate_sale_by_region_group_by_date,
    calculate_this_last_week_sales_vs_prediction,
    calculate_sales_by_day_of_the_week,
)

# Load environment variables
load_dotenv()

# Generate dummmy sales data
sales_df = generar_datos_ventas(1000)
sales_df = sales_df.fillna(0)

# Initiate Shimoku API
access_token = getenv("SHIMOKU_TOKEN")
universe_id: str = getenv("UNIVERSE_ID")
workspace_id: str = getenv("WORKSPACE_ID")

s = Shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
)
s.set_workspace(uuid=workspace_id)
s.set_board("Rodrigo Torres")

# Guided Tasks

# Task 1.a
sales_by_day_of_the_week = calculate_sales_by_day_of_the_week(sales_df.copy())

# Task 1.b
data_indicators = calculate_data_indicators(sales_df.copy())

# Task 2
sales_per_region_percentage = calculate_sales_percentage_by_region(sales_df.copy())

# Task 3
sales_per_month_agrupation = calculate_sales_by_month(sales_df.copy())

# Task 4
sales_per_month = calculate_sales_per_month(sales_df.copy())

# Plots

# Task 1
s.set_menu_path("Prueba-1", "Weekly Sales Performance 1")

# Task 1.a
s.plt.line(
    data=sales_by_day_of_the_week["days_data"],
    x="Day_of_Week",
    x_axis_name="Day of the week",
    y_axis_name="Total Sales ($)",
    title="Sales Performance: This Week vs. Last Week and Future Projections",
    order=0,
    padding="0,1,0,1",
)

print(data_indicators)
# Task 1.b
s.plt.indicator(
    data=data_indicators,
    order=1,
    rows_size=1,
    cols_size=12,)

# Task 2
s.set_menu_path("Prueba-1", "Regional Sales Distribution")
s.plt.pie(
    data=sales_per_region_percentage,
    names="Región",
    values="Percentage",
    order=0,
    title="Percentage of Sales by Region",
    rows_size=2,
    cols_size=12,
    padding="0,1,0,1",
)

# Task 3
s.set_menu_path("Prueba-1", "Monthly Sales Overview")
s.plt.line(
    data=sales_per_month_agrupation,
    x="Fecha",
    order=0,
    rows_size=3,
    cols_size=12,
    title="Total Monthly Sales of all products",
    option_modifications={"dataZoom": {"show": True}, "toolbox": {"show": True}},
)

# Task 4
s.set_menu_path("Prueba-1", "Monthly Sales")
s.plt.stacked_bar(
    data=sales_per_month,
    x="Month",
    y=sales_per_month.columns[1:].tolist(),
    x_axis_name="Month of the Year",
    y_axis_name="Total Sales ($)",
    title="Monthly sales of all products",
    order=1,
)

# Non guided tasks
data = calculate_sale_by_region_group_by_date(sales_df.copy())
this_last_week_sales_vs_prediction = calculate_this_last_week_sales_vs_prediction(sales_df.copy())
sales_date_float = this_last_week_sales_vs_prediction["Región 1"]["This week"]["Ventas"]
prediction_date_float = this_last_week_sales_vs_prediction["Región 1"]["This week"]["Percentage"]
this_week_start_date = this_last_week_sales_vs_prediction["Start Date"].strftime("%d/%m/%Y")
this_week_end_date = this_last_week_sales_vs_prediction["End Date"].strftime("%d/%m/%Y")
last_week_start_date = this_last_week_sales_vs_prediction["Start Date Last Week"].strftime("%d/%m/%Y")
last_week_end_date = this_last_week_sales_vs_prediction["End Date Last Week"].strftime("%d/%m/%Y")

# Create a list of region names
regions = list(this_last_week_sales_vs_prediction.keys())

# Remove non region names and sort by alphabetical order
regions.remove("Start Date")
regions.remove("End Date")
regions.remove("Start Date Last Week")
regions.remove("End Date Last Week")
regions.sort()


s.set_menu_path("Prueba-1", "Filter by Region")
# Loop through each region
for region_name in regions:
    # Set menu path and tabs index
    s.plt.set_tabs_index(("Tabs", region_name), order=0)

    # Get percentage values
    this_week_percentage = this_last_week_sales_vs_prediction[region_name]["This week"]["Percentage"]
    last_week_percentage = this_last_week_sales_vs_prediction[region_name]["Last week"]["Percentage"]

    # Plot gauge indicators
    s.plt.gauge_indicator(
        value=last_week_percentage,
        order=0,
        rows_size=1,
        cols_size=6,
        title="Last Week Sales vs Last Prediction",
        description=f"Sales from {last_week_start_date} to {last_week_end_date}",
        color="success" if last_week_percentage >= 100 else "error",
    )

    s.plt.gauge_indicator(
        value=this_week_percentage,
        order=2,
        rows_size=1,
        cols_size=6,
        title="This Week Sales vs Last Prediction",
        description=f"Sales from {this_week_start_date} to {this_week_end_date}",
        color="success" if this_week_percentage >= 100 else "error",
    )

    print(data[region_name])
    # Plot stacked bar chart
    s.plt.stacked_bar(
        x="date",
        order=6,
        title="Total Weekly Sales by Product (USD)",
        data=data[region_name],
        option_modifications={"dataZoom": {"show": True}, "toolbox": {"show": True}},
    )

# Pop out of tabs group
s.plt.pop_out_of_tabs_group()
