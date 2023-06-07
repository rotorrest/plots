import shimoku_api_python as Shimoku

from dotenv import load_dotenv
from os import getenv

from prueba_acceso import generar_datos_ventas
from utils import (
    generate_plot_data,
    venta_mensual,
    acumulado_mensual,
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


# data = generate_plot_data(df.copy())

data_t2 = venta_mensual(df.copy())

data_t3 = acumulado_mensual(df.copy())


# # Task 1
# s.set_menu_path("Prueba-2", "Daily Sales2")
# s.plt.html(
#     html=(f"<h1>The following plots contain the same information</h1>"),
#     order=0,
# )
# s.plt.html(
#     html=(f"<h3>Monthly Sales</h3>"),
#     order=1,
# )
# s.plt.bar(data=data, order=2, x="Fecha")
# s.plt.line(data=data, order=3, x="Fecha", rows_size=3, cols_size=6)
# s.plt.stacked_bar(data=data, order=4, x="Fecha", rows_size=3, cols_size=6)

# Task 2
s.set_menu_path("Prueba-3", "Sales Accumulated")

s.plt.set_tabs_index(("Charts", "Montly Sales"), order=0)
s.plt.bar(data=data_t2,
          order=0,
          x="Fecha",
          y_axis_name="Sales ($)",
)

s.plt.change_current_tab("Montly Accumulated Sales")
s.plt.bar(x="Fecha",
        order=0,
        data=data_t3,
        y_axis_name="Sales ($)",
)
s.plt.pop_out_of_tabs_group()
