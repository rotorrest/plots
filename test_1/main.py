import shimoku_api_python as Shimoku

from dotenv import load_dotenv
from os import getenv
import pandas as pd 

from prueba_acceso import generar_datos_ventas
from utils import (
    calculate_sales_percentage_by_region,
    calculate_sales_per_month,
    calculate_current_and_previous_week_sales,
    calculate_sales_prediction,
    calculate_data_indicators,
    calculate_sale_by_region,
    calculate_this_last_week_sales_vs_prediction,
)

# Load environment variables
load_dotenv()

# # # Generate dummmy sales data
sales_df = generar_datos_ventas(1000)
sales_df = sales_df.fillna(0)

# # Initiate Shimoku API
access_token = getenv("SHIMOKU_TOKEN")
universe_id: str = getenv("UNIVERSE_ID")
workspace_id: str = getenv("WORKSPACE_ID")

s = Shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
)
s.set_workspace(uuid=workspace_id)
s.set_board("Rodrigo Torres")

# Genearate data

# Task 1.a
current_and_previous_week_sales = calculate_current_and_previous_week_sales(sales_df.copy())

# Task 1.b
data_indicators = calculate_data_indicators(sales_df.copy())

# Task 2
sales_per_region_percentage = calculate_sales_percentage_by_region(sales_df.copy())

# Task 3
sales_prediction = calculate_sales_prediction(sales_df.copy())

# Task 4
sales_per_month = calculate_sales_per_month(sales_df.copy())

# Plots

# Task 1
s.set_menu_path("Test-v1", "Current/Previus Week")

s.plt.html(
    html=("<h3>Difference between sales and prediction</h3>"),
    order=1,
    rows_size=1,
    cols_size=12,
)

# Task 1.b
s.plt.indicator(
    data=data_indicators,
    order=2,
    rows_size=1,
    cols_size=12,
)

s.plt.html(
    html=(f"<h5>{current_and_previous_week_sales['title']}</h3>"),
    order=6,
    rows_size=1,
    cols_size=12,
)

# Task 1.a
s.plt.bar(
    data=current_and_previous_week_sales["data"],
    order=7,
    x="Semana",
    y_axis_name="Ventas",
    padding="0,1,0,1",
)

# Task 2
s.set_menu_path("Test-v1", "Percetage by Region")
s.plt.pie(
    data=sales_per_region_percentage,
    names="Región",
    values="Percentage",
    order=0,
    title="Percentage of sales by region",
    rows_size=2,
    cols_size=12,
)


# Task 3
s.set_menu_path("Test-v1", "Sales Prediction")
s.plt.predictive_line(
    data=sales_prediction["data"],
    x="date",
    order=0,
    min_value_mark=len(sales_prediction["data"]) - 1 - sales_prediction["num_predicted_dates"],
    max_value_mark=len(sales_prediction["data"]) - 1,
    rows_size=3,
    cols_size=12,
)

# Task 4
s.set_menu_path("Test-v1", "Monthly Sales")
s.plt.stacked_bar(
    data=sales_per_month,
    x="Month",
    y=sales_per_month.columns[1:].tolist(),
    x_axis_name="Month of the Year",
    y_axis_name="Total Sales",
    title="Evolution of Total Annual Sales Over the Months of the Year",
    order=1,
)

# Non guided tasks
data = calculate_sale_by_region(sales_df.copy())
this_last_week_sales_vs_prediction = calculate_this_last_week_sales_vs_prediction(sales_df.copy())
sales_date_float = this_last_week_sales_vs_prediction['Región 1']['This week']['Ventas']
prediction_date_float = this_last_week_sales_vs_prediction['Región 1']['This week']['Percentage']
this_week_start_date = this_last_week_sales_vs_prediction["Start Date"].strftime("%d%m%Y")
this_week_end_date = this_last_week_sales_vs_prediction["End Date"].strftime("%d%m%Y")
last_week_start_date = this_last_week_sales_vs_prediction["Start Date Last Week"].strftime("%d%m%Y")
last_week_end_date = this_last_week_sales_vs_prediction["End Date Last Week"].strftime("%d%m%Y")


s.set_menu_path("Test-v1", "Filter by Region")

s.plt.set_tabs_index(('Tabs', 'Region 1'), order=0)

percentage_value = this_last_week_sales_vs_prediction['Región 1']['This week']['Percentage']

s.plt.gauge_indicator(
    value=percentage_value,
    order=0,
    rows_size=1, cols_size=6,
    title="Last week sales vs prediction",
    description = f"Sales from {this_week_start_date} to {this_week_end_date}",
    color = "success" if percentage_value >= 100 else "error",
)

percentage_value = this_last_week_sales_vs_prediction['Región 1']['Last week']['Percentage']

s.plt.gauge_indicator(
    value=percentage_value,
    order=2,
    rows_size=1, cols_size=6,
    title="Last week sales vs prediction",
    description = f"Sales from {last_week_start_date} to {last_week_end_date}",
    color = "success" if percentage_value >= 100 else "error",
)


s.plt.stacked_bar(
        x='date',
        order=6,
        data=data["Región 1"],
        option_modifications={
            'dataZoom': {
                'show': True
                }, 
                'toolbox': {
                    'show': True
                    }
        },
    )

s.plt.change_current_tab('Region 2')

percentage_value = this_last_week_sales_vs_prediction['Región 2']['This week']['Percentage']
s.plt.gauge_indicator(
    value=percentage_value,
    order=0,
    rows_size=1, cols_size=6,
    title="Last week sales vs prediction",
    description = f"Sales from {this_week_start_date} to {this_week_end_date}",
    color = "success" if percentage_value >= 100 else "error",
)

percentage_value = this_last_week_sales_vs_prediction['Región 2']['Last week']['Percentage']
s.plt.gauge_indicator(
    value=percentage_value,
    order=2,
    rows_size=1, cols_size=6,
    title="Last week sales vs prediction",
    description = f"Sales from {last_week_start_date} to {last_week_end_date}",
    color = "success" if percentage_value >= 100 else "error",
)

s.plt.stacked_bar(
        x='date',
        order=6,
        data=data["Región 2"],
        option_modifications={
            'dataZoom': {
                'show': True
                }, 
                'toolbox': {
                    'show': True
                    }
        },
    )


s.plt.change_current_tab('Region 3')
percentage_value = this_last_week_sales_vs_prediction['Región 3']['This week']['Percentage']
s.plt.gauge_indicator(
    value=percentage_value,
    order=0,
    rows_size=1, cols_size=6,
    title="Last week sales vs prediction",
    description = f"Sales from {this_week_start_date} to {this_week_end_date}",
    color = "success" if percentage_value >= 100 else "error",
)

percentage_value = this_last_week_sales_vs_prediction['Región 3']['Last week']['Percentage']
s.plt.gauge_indicator(
    value=percentage_value,
    order=2,
    rows_size=1, cols_size=6,
    title="Last week sales vs prediction",
    description = f"Sales from {last_week_start_date} to {last_week_end_date}",
    color = "success" if percentage_value >= 100 else "error",
)


s.plt.stacked_bar(
        x='date',
        order=6,
        data=data["Región 3"],
        option_modifications={
            'dataZoom': {
                'show': True
                }, 
                'toolbox': {
                    'show': True
                    }
        },
    )

s.plt.change_current_tab('Region 4')
percentage_value = this_last_week_sales_vs_prediction['Región 4']['This week']['Percentage']
s.plt.gauge_indicator(
    value=percentage_value,
    order=0,
    rows_size=1, cols_size=6,
    title="Last week sales vs prediction",
    description = f"Sales from {this_week_start_date} to {this_week_end_date}",
    color = "success" if percentage_value >= 100 else "error",
)

percentage_value = this_last_week_sales_vs_prediction['Región 4']['Last week']['Percentage']
s.plt.gauge_indicator(
    value=percentage_value,
    order=2,
    rows_size=1, cols_size=6,
    title="Last week sales vs prediction",
    description = f"Sales from {last_week_start_date} to {last_week_end_date}",
    color = "success" if percentage_value >= 100 else "error",
)

s.plt.stacked_bar(
        x='date',
        order=6,
        data=data["Región 4"],
        option_modifications={
            'dataZoom': {
                'show': True
                }, 
                'toolbox': {
                    'show': True
                    }
        },
    )

s.plt.pop_out_of_tabs_group()