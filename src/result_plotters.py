import os
from typing import Final

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

from time import sleep


class ResultPlotter:
    def __init__(self, fluid_name: str):
        self.fluid_name: Final[str] = fluid_name
        self.output_folder: Final[str] = "output/"

    def plot_fluid_and_cell_temperature_vs_time(self, metrics_and_temp_df: pd.DataFrame):
        fluid_temp_1 = metrics_and_temp_df["Channel 7 Ave. (C)"][0]
        cell_temp_1 = metrics_and_temp_df["Channel 3 Ave. (C)"][0]

        temp_offset: Final[
            float] = fluid_temp_1 - cell_temp_1 if fluid_temp_1 > cell_temp_1 else cell_temp_1 - fluid_temp_1

        fig = px.scatter(
            x=metrics_and_temp_df["time"],
            y=metrics_and_temp_df["Channel 7 Ave. (C)"]+temp_offset,
            title="Plot of Temperature of Fluid and PV Cell versus Time"
        )
        fig['data'][0]['showlegend'] = True
        fig['data'][0]['name'] = self.fluid_name

        fig.add_scatter(x=metrics_and_temp_df["time"], y=metrics_and_temp_df["Channel 3 Ave. (C)"], name="PV Cell")

        fig.update_layout(
            showlegend=True,
            xaxis_title="Time from Initialization",
            yaxis_title="Temperature (°C)",
            title={"x": 0.5, "xanchor": "center", "yanchor": "top"},
            plot_bgcolor="#FFF",
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="black"
            )
        )
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
            rangemode="tozero",
        )

        fig.show()
        output_path = os.path.join(self.output_folder, "phase")
        os.makedirs(output_path, exist_ok=True)
        fig.write_image(os.path.join(output_path, f"transmittances.pdf"))


    def plot_characteristics_vs_fluid_temperature(self, metrics_and_temp_df: pd.DataFrame, cell_area: float, is_cooling: bool) -> None:
        #NB: subtract initial cell temperature so they begin from same value
        fluid_temp_1 = metrics_and_temp_df["Channel 7 Ave. (C)"][0]
        cell_temp_1 = metrics_and_temp_df["Channel 3 Ave. (C)"][0]

        temp_offset: Final[float] = fluid_temp_1 - cell_temp_1 if fluid_temp_1 > cell_temp_1 else cell_temp_1 - fluid_temp_1

        fig = make_subplots(rows=2, cols=2, horizontal_spacing=0.2)

        I_sc = metrics_and_temp_df["Jsc (A.cm^-2)"] * cell_area

        fig.add_trace(
            go.Scatter(y=metrics_and_temp_df["Maximum Power (W)"], x=metrics_and_temp_df["Channel 7 Ave. (C)"] - temp_offset), row=1,
            col=1)
        fig.add_trace(go.Scatter(y=metrics_and_temp_df["Voc (V)"], x=metrics_and_temp_df["Channel 7 Ave. (C)"] - temp_offset), row=1,
                      col=2)
        fig.add_trace(go.Scatter(y=I_sc, x=metrics_and_temp_df["Channel 7 Ave. (C)"] + temp_offset), row=2,
                      col=1)
        fig.add_trace(go.Scatter(y=metrics_and_temp_df["FF (%)"], x=metrics_and_temp_df["Channel 7 Ave. (C)"] - temp_offset), row=2,
                      col=2)

        # fig["data"][0]["name"] = "prey"
        # fig["data"][1]["name"] = "predator"

        fig.update_xaxes(
            title_text="Fluid Temperature (°C)",
            row=1,
            col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_xaxes(
            title_text="Fluid Temperature (°C)",
            row=2,
            col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_xaxes(
            title_text="Fluid Temperature (°C)",
            row=1,
            col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_xaxes(
            title_text="Fluid Temperature (°C)",
            row=2,
            col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="Max. Power (W)",
            row=1, col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="$\\text{V}_{\\text{oc}}$ (V)",
            row=1, col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="$\\text{I}_{\\text{sc}}$ (A)",
            row=2, col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="FF (%)",
            row=2, col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )

        fig.update_layout(
            height=600,
            width=800,
            title_text=f"Plots of PV Characteristics versus Fluid Temperature<br> for Incident Light under {self.fluid_name.title()} Down-Shifting" if is_cooling == False
            else f"Plots of PV Characteristics versus Fluid Temperature<br> under {self.fluid_name.title()} Cooling",
            title={"x": 0.5, "xanchor": "center", "yanchor": "top"},
            showlegend=False,
            plot_bgcolor="#FFF",
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="black"
            )
        )

        fig.show()
        output_path = os.path.join(self.output_folder, f"characteristics_vs_fluid_temperature")
        os.makedirs(output_path, exist_ok=True)
        fig.write_image(os.path.join(output_path, f"{self.fluid_name}.pdf"))

    def plot_characteristics_vs_time(self, metrics_and_temp_df: pd.DataFrame, cell_area: float, is_cooling: bool) -> None:
        fig = make_subplots(rows=2, cols=2, horizontal_spacing=0.2, vertical_spacing=0.32)

        I_sc = metrics_and_temp_df["Jsc (A.cm^-2)"]*cell_area

        fig.add_trace(go.Scatter(y=metrics_and_temp_df["Maximum Power (W)"], x=metrics_and_temp_df["time"]), row=1, col=1)
        fig.add_trace(go.Scatter(y=metrics_and_temp_df["Voc (V)"], x=metrics_and_temp_df["time"]), row=1, col=2)
        fig.add_trace(go.Scatter(y=I_sc, x=metrics_and_temp_df["time"]), row=2,
                      col=1)
        fig.add_trace(go.Scatter(y=metrics_and_temp_df["FF (%)"], x=metrics_and_temp_df["time"]), row=2,
                      col=2)

        #fig["data"][0]["name"] = "prey"
        #fig["data"][1]["name"] = "predator"

        fig.update_xaxes(
            title_text="Time (T)",
            row=1,
            col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
            rangemode="tozero",
        )
        fig.update_xaxes(
            title_text="Time (T)",
            row=2,
            col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
            rangemode="tozero",
        )
        fig.update_xaxes(
            title_text="Time (T)",
            row=1,
            col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
            rangemode="tozero",
        )
        fig.update_xaxes(
            title_text="Time (T)",
            row=2,
            col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
            rangemode="tozero",
        )
        fig.update_yaxes(
            title_text="Max. Power (W)",
            row=1, col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="$\\text{V}_{\\text{oc}}$ (V)",
            row=1, col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="$\\text{I}_{\\text{sc}}$ (A)",
            row=2, col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="FF (%)",
            row=2, col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )

        fig.update_layout(
            height=600,
            width=800,
            title_text=f"Plots of PV Characteristics versus Time<br> for Incident Light" if is_cooling == False
            else f"Plots of PV Characteristics versus Time<br> under {self.fluid_name.title()} Cooling",
            title={"x": 0.5, "xanchor": "center", "yanchor": "top"},
            showlegend=False,
            plot_bgcolor="#FFF",
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="black"
            )
        )

        fig.show()
        output_path = os.path.join(self.output_folder, f"characteristics_vs_time")
        os.makedirs(output_path, exist_ok=True)
        fig.write_image(os.path.join(output_path, f"{self.fluid_name}.pdf"))

    def plot_characteristics_vs_cell_temperature(self, metrics_and_temp_df: pd.DataFrame, cell_area: float) -> None:
        fig = make_subplots(rows=2, cols=2, horizontal_spacing=0.2)

        I_sc = metrics_and_temp_df["Jsc (A.cm^-2)"]*cell_area

        fig.add_trace(go.Scatter(y=metrics_and_temp_df["Maximum Power (W)"], x=metrics_and_temp_df["Channel 3 Ave. (C)"]), row=1, col=1)
        fig.add_trace(go.Scatter(y=metrics_and_temp_df["Voc (V)"], x=metrics_and_temp_df["Channel 3 Ave. (C)"]), row=1, col=2)
        fig.add_trace(go.Scatter(y=I_sc, x=metrics_and_temp_df["Channel 3 Ave. (C)"]), row=2,
                      col=1)
        fig.add_trace(go.Scatter(y=metrics_and_temp_df["FF (%)"], x=metrics_and_temp_df["Channel 3 Ave. (C)"]), row=2,
                      col=2)

        #fig["data"][0]["name"] = "prey"
        #fig["data"][1]["name"] = "predator"

        fig.update_xaxes(
            title_text="PV Cell Temperature (°C)",
            row=1,
            col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_xaxes(
            title_text="PV Cell Temperature (°C)",
            row=2,
            col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_xaxes(
            title_text="PV Cell Temperature (°C)",
            row=1,
            col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_xaxes(
            title_text="PV Cell Temperature (°C)",
            row=2,
            col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="Max. Power (W)",
            row=1, col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="$\\text{V}_{\\text{oc}}$ (V)",
            row=1, col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="$\\text{I}_{\\text{sc}}$ (A)",
            row=2, col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )
        fig.update_yaxes(
            title_text="FF (%)",
            row=2, col=2,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
        )

        fig.update_layout(
            height=600,
            width=800,
            title_text=f"Plots of PV Characteristics versus Cell Temperature<br> for Incident Light under {self.fluid_name.title()} Down-Shifting",
            title={"x": 0.5, "xanchor": "center", "yanchor": "top"},
            showlegend=False,
            plot_bgcolor="#FFF",
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="black"
            )
        )

        fig.show()
        output_path = os.path.join(self.output_folder, f"characteristics_vs_cell_temperature")
        os.makedirs(output_path, exist_ok=True)
        fig.write_image(os.path.join(output_path, f"{self.fluid_name}.pdf"))

    """
    def plot_phase(self, simulated_populations: SimulatedPopulations):
        fig = px.scatter(
            x=simulated_populations.prey,
            y=simulated_populations.predator,
            title="Plot of predator count versus prey count",
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title="Prey count [arb. units]",
            yaxis_title="Predator count [arb. units]",
            title={"x": 0.5, "xanchor": "center", "yanchor": "top"},
            plot_bgcolor="#FFF",
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="black"
            )
        )
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            showline=True,
            linecolor="black",
            rangemode="tozero",
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            showline=True,
            linecolor="black",
            rangemode="tozero",
        )

        #fig.show()
        output_path = os.path.join(self.output_folder, "phase")
        os.makedirs(output_path, exist_ok=True)
        fig.write_image(os.path.join(output_path, f"{self.count}.pdf"))
    """

    @staticmethod
    def load_mathjax():
        """https://github.com/plotly/plotly.py/issues/3469"""
        os.makedirs("output", exist_ok=True)
        px.scatter(x=[0, 1], y=[0, 1]).write_image("output/random.pdf")
        sleep(1)
