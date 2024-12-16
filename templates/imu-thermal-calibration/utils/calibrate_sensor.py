import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Dict, Tuple, List


def calibrate_sensor(
    data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    polynomial_order: int = 3,
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
    temp, *sensor_axes = data

    poly_coeffs: Dict[str, np.ndarray] = {}
    fitted_values: Dict[str, np.ndarray] = {}
    figures: List[BytesIO] = []

    for i, axis_data in enumerate(sensor_axes):
        axis_name = f"axis_{i}"

        # Fit polynomial to the data
        coeffs = np.polyfit(temp, axis_data, polynomial_order)
        poly_coeffs[axis_name] = coeffs

        # Compute fitted values
        fitted = np.polyval(coeffs, temp)
        fitted_values[axis_name] = fitted

        # Generate plot and store figure
        fig, ax = plt.subplots()
        ax.plot(temp, axis_data, "o", label="Sensor Data")
        ax.plot(temp, fitted, "-", label="Fitted Curve")
        ax.set_title(f"{axis_name} Calibration")
        ax.set_xlabel("Temperature (°C)")
        ax.set_ylabel("Sensor Value")
        ax.legend()

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
