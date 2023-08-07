import shimoku_api_python as Shimoku

from dotenv import load_dotenv
from os import getenv

from prueba_acceso import generar_datos_ventas
from utils import (
    calculate_generate_plot_data,
    calculate_monthly_sales,
    calculate_cumulative_monthly_sales,
)

# Load environment variables
load_dotenv()

# Generate dummmy sales data
df = generar_datos_ventas(1000)
df = df.fillna(0)

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


plot1_data = calculate_generate_plot_data(df.copy())
monthly_sales = calculate_monthly_sales(df.copy())
cumulative_monthly_sales = calculate_cumulative_monthly_sales(df.copy())


# Task 1
s.set_menu_path("Prueba-v2", "Daily Sales")
s.plt.html(
    html=(f"<h1>The following plots contain the same information</h1>"),
    order=0,
)
s.plt.html(
    html=(f"<h3>Product sales by month</h3>"),
    order=1,
)
s.plt.bar(data=plot1_data, order=2, x="Fecha", y_axis_name="Sales ($)")
s.plt.line(
    data=plot1_data,
    order=3,
    x="Fecha",
    rows_size=3,
    cols_size=6,
    y_axis_name="Sales ($)",
)
s.plt.stacked_bar(
    data=plot1_data,
    order=4,
    x="Fecha",
    rows_size=3,
    cols_size=6,
    y_axis_name="Sales ($)",
)

# Task 2
s.set_menu_path("Prueba-v2", "Sales")

s.plt.set_tabs_index(("Charts", "Montly"), order=0)
s.plt.bar(
    data=monthly_sales,
    order=0,
    x="Fecha",
    y_axis_name="Sales ($)",
)

s.plt.change_current_tab("Accumulated")
s.plt.bar(
    x="Fecha",
    order=0,
    data=cumulative_monthly_sales,
    y_axis_name="Sales ($)",
)
s.plt.pop_out_of_tabs_group()
