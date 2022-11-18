from typing import Final
import glob
import pandas as pd
from src.result_plotters import ResultPlotter
from src.transmittance_plotter import TransmittancePlotter
from src.electrical_and_thermal_power import ElectricalThermalPowerCalculator

def get_df_of_temperatures_per_metric(heat_transfer_fluid_name: str, is_cooling: bool) -> pd.DataFrame:
    data_folder: Final[str] = "cooling" if is_cooling else "heating"
    file_paths: Final[list[str]] = glob.glob(f"data/{data_folder}/{heat_transfer_fluid_name}/metrics/*")
    temperature_data: Final[pd.DataFrame] = get_temperatures_from_picolog_data(heat_transfer_fluid_name=heat_transfer_fluid_name, is_cooling=is_cooling)

    times_per_suffix = dict(zip(temperature_data["suffix"], temperature_data["time"]))

    metrics: list[pd.DataFrame] = list()
    for path in file_paths:
        file_suffix: str = path.split(" ")[-1].split(".csv")[0]
        if file_suffix == "(1)": # Measurement before light is turned on
            continue

        time_recorded: str = times_per_suffix[file_suffix]

        print(f"{file_suffix} was recorded {time_recorded} in")

        metric: pd.DataFrame = pd.read_csv(path)
        metric.index = [time_recorded]
        metric["path"] = path
        metrics.append(metric)

    metrics_df = pd.concat(metrics, axis=0, ignore_index=False)

    metrics_and_temp_df: Final[pd.DataFrame] = pd.concat([metrics_df, temperature_data], axis=1).sort_index(axis=0)
    return metrics_and_temp_df

def get_temperatures_from_picolog_data(heat_transfer_fluid_name: str, is_cooling: bool) -> pd.DataFrame:
    data_folder: Final[str] = "cooling" if is_cooling else "heating"
    temperatures: pd.DataFrame = pd.read_csv(f"data/{data_folder}/{heat_transfer_fluid_name}/temperature-by-file-end.csv")
    picolog_data: pd.DataFrame = pd.read_csv(f"data/{data_folder}/_temperatures/{heat_transfer_fluid_name}.csv", index_col=0)[["Channel 3 Ave. (C)", "Channel 7 Ave. (C)"]]

    relevant_temperatures: pd.DataFrame = picolog_data.loc[temperatures["time"]]

    temperatures = temperatures.set_index(temperatures["time"])
    combined_temp_data = pd.concat([relevant_temperatures, pd.DataFrame(data={"suffix": temperatures["suffix"], "time": temperatures["time"]})], axis=1)

    return combined_temp_data

def plot_characteristics() -> None:
    fluid_names: Final[list[str]] = ["glycerol", "rhodamine-1pc", "rhodamine-2pc", "water"]
    cooling_fluid_names: Final[list[str]] = ["rhodamine-2pc"]
    cell_area: Final[float] = 0.07*0.15  # [metres]
    ResultPlotter(fluid_name="").load_mathjax()

    for fluid_name in fluid_names:
        print(f"Processing {fluid_name}")
        metrics_and_temp_df: pd.DataFrame = get_df_of_temperatures_per_metric(heat_transfer_fluid_name=fluid_name, is_cooling=False)

        result_plotter_obj: ResultPlotter = ResultPlotter(fluid_name=fluid_name)

        result_plotter_obj.plot_characteristics_vs_cell_temperature(metrics_and_temp_df=metrics_and_temp_df, cell_area=cell_area)
        result_plotter_obj.plot_characteristics_vs_fluid_temperature(metrics_and_temp_df=metrics_and_temp_df, cell_area=cell_area, is_cooling=False)

        result_plotter_obj.plot_fluid_and_cell_temperature_vs_time(metrics_and_temp_df=metrics_and_temp_df)

    for fluid_name in cooling_fluid_names:
        result_plotter_obj: ResultPlotter = ResultPlotter(fluid_name=fluid_name)

        metrics_and_temp_cooling_df: pd.DataFrame = get_df_of_temperatures_per_metric(heat_transfer_fluid_name=fluid_name, is_cooling=True)

        if fluid_name in {"rhodamine-2pc"}:
            result_plotter_obj.plot_characteristics_vs_fluid_temperature(metrics_and_temp_df=metrics_and_temp_cooling_df,
                                                                         cell_area=cell_area, is_cooling=True)
        elif fluid_name in {"glycerol", "air"}:
            result_plotter_obj.plot_characteristics_vs_time(metrics_and_temp_df=metrics_and_temp_cooling_df,
                                                                         cell_area=cell_area, is_cooling=True)

    print(f"Processing air")
    metrics_and_temp_df: pd.DataFrame = get_df_of_temperatures_per_metric(heat_transfer_fluid_name="air", is_cooling=False)
    ResultPlotter(fluid_name="air").plot_characteristics_vs_time(
    metrics_and_temp_df=metrics_and_temp_df, cell_area=cell_area, is_cooling=False)

def plot_transmittance_and_get_spectral_intensities() -> pd.DataFrame:
    spectral_intensities: pd.DataFrame = pd.read_csv("data/spectrometer-and-final/spectral_data.csv", index_col=0)
    result_plotter_obj: Final[TransmittancePlotter] = TransmittancePlotter()
    result_plotter_obj.plot_phase(spectral_intensities=spectral_intensities)

    return spectral_intensities

def get_electrical_thermal_powers(spectral_intensities: pd.DataFrame):
    calculator_obj: Final[ElectricalThermalPowerCalculator] = ElectricalThermalPowerCalculator(spectral_intensities=spectral_intensities)
    electrical_power = calculator_obj.get_electrical_power()
    thermal_power = calculator_obj.get_thermal_power(electrical_power=electrical_power)
    print(f"Electrical power: {electrical_power}")
    print(f"Thermal power: {thermal_power}")
    #calculator_obj.plot_phase()


if __name__ == "__main__":
    plot_characteristics()
    spectral_intensities: Final[pd.DataFrame] = plot_transmittance_and_get_spectral_intensities()
    get_electrical_thermal_powers(spectral_intensities=spectral_intensities)

