import numpy as np


def compute_temp_sensitivity(
    data: np.ndarray, temperatures: np.ndarray, temp_ref: float = 25
) -> dict:
    """
    Computes temperature sensitivity for sensor data.

    Parameters:
    data (numpy.ndarray): Sensor data.
    temperatures (numpy.ndarray): Corresponding temperatures for the data.
    temp_ref (float): Reference temperature for sensitivity calculations (default: 25C).

    Returns:
    dict: Maximum sensitivity and sensitivity at reference temperature.

    Use this function to assess how sensor readings change with temperature.
    """
    # Avoid division by near 0 and noise
    d_temp = np.diff(temperatures)
    valid_idx = np.abs(d_temp) > 1e-5

    # Calculate sensitivity for valid temperature changes
    d_data = np.diff(data)
    sensitivities = d_data[valid_idx] / d_temp[valid_idx]

    # Find reference temperature index and compute sensitivity around it
    ref_idx = np.argmin(np.abs(temperatures - temp_ref))
    ref_range = slice(max(ref_idx - 10, 0), min(ref_idx + 10, len(sensitivities)))
    sensitivity_ref = np.mean(sensitivities[ref_range])

    return {
        "max_sensitivity": np.max(np.abs(sensitivities)),
        "sensitivity_at_ref": abs(sensitivity_ref),
    }
