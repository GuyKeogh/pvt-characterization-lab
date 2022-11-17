import pandas as pd
from typing import Final
import numpy as np
import os
import plotly.express as px
import scipy.integrate as integrate
from math import floor, isnan

class ElectricalThermalPowerCalculator:
    def __init__(self, spectral_intensities: pd.DataFrame):
        self.output_folder: Final[str] = "output/"
        self.spectral_response_df: Final[pd.DataFrame] = pd.read_csv("data/PV Solar Cell Spectral Response and AM1.5D Spectra.csv", index_col=0)["AM1.5D (W m-2 nm-1)"]
        spectra_df: pd.DataFrame = pd.read_csv(
            "data/PV Solar Cell Spectral Response and AM1.5D Spectra.csv", index_col=2)["Spectral Response of solar cell (A W-1)"]
        self.spectra_df: Final[pd.DataFrame] = spectra_df[spectra_df.index.notnull()]

        self.spectral_response_and_spectra_df: Final[pd.DataFrame] = pd.DataFrame(data={"AM1.5D (W m-2 nm-1)": self.spectral_response_df, "Spectral Response of solar cell (A W-1)": self.spectra_df})

        self.am1_5g_spectra_df: Final[pd.DataFrame] = pd.read_csv("data/am1-5g.csv", index_col=0)
        self.spectral_intensities: Final[pd.DataFrame] = spectral_intensities
        print("aaa")

    def calculate_electrical_power(self):

        max_wavelength: Final[int] = len(self.am1_5g_spectra_df.index) - 1 if len(self.am1_5g_spectra_df.index) < 2000 else 2000
        result = integrate.quad(lambda wavelength: self.electrical_power_integral_functions(wavelength), 250, max_wavelength)
        # p.g. 10 Article 1
        print(result)
        pass

    def electrical_power_integral_functions(self, wavelength: float) -> float:
        return self.phi_am1point5d(wavelength) * self.SR(wavelength) * self.T_liquid(wavelength)

    def calculate_thermal_power(self):
        #p.g. 10 Article 1
        pass

    def phi_am1point5d(self, wavelength: float) -> float:
        """Photon flux contained in the standardised AM1.5G solar spectrum"""
        """
        ratio: Final[float] = wavelength % 1
        num_1 = self.spectral_response_and_spectra_df.iloc[round(wavelength)]["Spectral Response of solar cell (A W-1)"]
        num_2 = self.spectral_response_and_spectra_df.iloc[round(wavelength) + 1]["Spectral Response of solar cell (A W-1)"]

        y = ((num_1-num_2)/1)*ratio
        """
        phi_am1point5d: float = self.spectral_response_and_spectra_df.iloc[round(wavelength)]["Spectral Response of solar cell (A W-1)"]
        if isnan(phi_am1point5d):
            return 0
        else:
            return phi_am1point5d

    def SR(self, wavelength: float) -> float:
        """Spectral response of cell"""
        return self.am1_5g_spectra_df.iloc[round(wavelength)]["Cumulative photon flux (cm–2⋅s–1)"]

    def T_liquid(self, wavelength: float) -> float:
        """Optical transmittance of the filter, in absence of interactions
        with interface"""
        return self.spectral_intensities.iloc[round(wavelength)]["air"]

    def plot_phase(self) -> None:
        fig = px.scatter(
            y=self.spectral_response_and_spectra_df["AM1.5D (W m-2 nm-1)"],
            x=self.spectral_response_and_spectra_df["WL (nm)"],
            title="Plot of Spectral Irradiance from the Sun per Wavelength"
        )
        fig['data'][0]['showlegend'] = True
        fig['data'][0]['name'] = 'Spectral Irradiance from the Sun'

        fig.add_scatter(y=self.spectral_response_and_spectra_df["Spectral Response of solar cell (A W-1)"],
                        x=self.spectral_response_and_spectra_df["WL (nm).1"], name="Solar Cell")

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