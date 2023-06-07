import shimoku_api_python as Shimoku

from dotenv import load_dotenv
from os import getenv

from prueba_acceso import generar_datos_ventas
from utils import (
    generate_plot_data,
    totales_diarios,
    total_semanal,
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


data = generate_plot_data(df.copy())
data = data[-100:]

data_t2 = totales_diarios(df.copy())
data_t2 = data_t2[-100:]

data_t3 = total_semanal(df.copy())
data_t3 = data_t3[-100:]

# Task 1
s.set_menu_path("Test-v2", "Daily Sales")
s.plt.html(
    html=(f"<h1>The following plots contain the same information</h1>"),
    order=0,
    rows_size=0,
    cols_size=12,
)
s.plt.bar(data=data, order=1, x="Fecha")
s.plt.line(data=data, order=2, x="Fecha", rows_size=3, cols_size=6)
s.plt.stacked_bar(data=data, order=3, x="Fecha", rows_size=3, cols_size=6)

# Task 2
s.set_menu_path("Test-v2", "Daily Sales & Weekly Accumulated Sales")

s.plt.set_tabs_index(("Charts", "Daily Sales"), order=0)
s.plt.bar(data=data_t2,
          order=0,
          x="Fecha",
          y_axis_name="Daily Sales ($)",
)

s.plt.change_current_tab("Weekly Accumulated Sales")
s.plt.bar(x="Fecha",
        order=0,
        data=data_t3,
        y_axis_name="Weekly Accumulated ($)",
)
s.plt.pop_out_of_tabs_group()
