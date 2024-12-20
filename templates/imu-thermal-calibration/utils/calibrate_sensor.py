import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Dict, Tuple, List

def calibrate_sensor(
        data: Tuple[List[float], List[float], List[float], List[float]],
        sensor: str, polynomial_order: int = 3
        ) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Fit a polynomial model to the sensor data against temperature.

    Args:
    data (tuple): A tuple containing:
    - temperature data (numpy array)
    - sensor data for each axis (numpy arrays for x, y, z)
    polynomial_order (int): The degree of the polynomial to fit.

    Returns:
    dict: A dictionary containing:
    - polynomial_coefficients: Coefficients of the fitted polynomial for each axis.
    - fitted_values: Fitted values for each axis at the given temperature points.
    - figures: Matplotlib figure objects as in-memory images for each axis.
    """

    # Define color names
    colors = {
        "dark_gray": "#09090B",
        "lime": "#bef264",
        "pink": "#f9a8d4",
        "white": "#ffffff",
        "purple": "#a78bfa"
    }

    # Convert the tuple elements to NumPy arrays
    temp, *sensor_data = (np.array(arr) for arr in data)

    poly_coeffs: Dict[str, np.ndarray] = {}
    fitted_values: Dict[str, np.ndarray] = {}
    figures: List[BytesIO] = []
    axis_list = ('x', 'y', 'z')

    for i, axis_data in enumerate(sensor_data):
        if sensor == "acc":
            sensor = "Accelerometer"
            unit = "m/s²"
        else:
            sensor = "Gyroscope"
            unit = "°/s"
        axis_name = f"{axis_list[i]}_axis"

        # Fit polynomial to the data
        coeffs = np.polyfit(temp, axis_data, polynomial_order)
        poly_coeffs[axis_name] = coeffs

        # Compute fitted values
        fitted = np.polyval(coeffs, temp)
        fitted_values[axis_name] = fitted

        # Generate plot and store figure
        fig, ax = plt.subplots()
        fig.patch.set_facecolor(colors["dark_gray"])
        ax.set_facecolor(colors["dark_gray"])

        ax.plot(temp, axis_data, "o", color=colors["lime"], label=f"{sensor} data")
        ax.plot(temp, fitted, "-", color=colors["pink"], label="Fitted Curve")
        ax.set_title(f"{sensor} {axis_name[0].capitalize()} axis calibration", color=colors["white"])
        ax.set_xlabel("Temperature (°C)", color=colors["white"])
        ax.set_ylabel(f"{sensor} value ({unit})", color=colors["white"])
        ax.tick_params(colors=colors["white"])
        ax.spines['bottom'].set_color(colors["white"])
        ax.spines['left'].set_color(colors["white"])
        ax.spines['top'].set_color(colors["white"])
        ax.spines['right'].set_color(colors["white"])
        ax.legend(facecolor=colors["dark_gray"], edgecolor=colors["white"], labelcolor=colors["white"])

        # Convert the figure to an in-memory image
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        figures.append(buffer)
        plt.close(fig)

    return {
        "polynomial_coefficients": poly_coeffs,
        "fitted_values": fitted_values,
        "figures": figures,
    }
