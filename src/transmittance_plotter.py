import os
import plotly.express as px
from typing import Final
import pandas as pd

class TransmittancePlotter:
    def __init__(self):
        self.output_folder: Final[str] = "output/"

    def plot_phase(self, spectral_intensities: pd.DataFrame) -> None:
        fig = px.scatter(
            x=spectral_intensities.index,
            y=spectral_intensities["air"]/spectral_intensities["air"],
            title="Plot of Wavelength versus Transmittance of Fluids"
        )
        fig['data'][0]['showlegend'] = True
        fig['data'][0]['name'] = 'air'

        fig.add_scatter(x=spectral_intensities.index, y=(spectral_intensities["water"]/spectral_intensities["air"]), name="water")
        fig.add_scatter(x=spectral_intensities.index,
                        y=(spectral_intensities["glycerol"] / spectral_intensities["air"]), name="glycerol")
        fig.add_scatter(x=spectral_intensities.index,
                        y=(spectral_intensities["rhodaine-2pc"] / spectral_intensities["air"]), name="rhodaine-2pc")

        fig.update_layout(
            showlegend=True,
            xaxis_title="Wavelength (nm)",
            yaxis_title="Transmittance",
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