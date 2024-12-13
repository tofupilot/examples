import numpy as np


def compute_r2(data: np.ndarray, fit_model: np.ndarray) -> float:
    """
    Computes R-squared to evaluate how well a model fits the data.

    Parameters:
    data (numpy.ndarray): Sensor data.
    fit_model (numpy.ndarray): Fitted model values for the data.

    Returns:
    float: R-squared value.

    Use this function to quantify the goodness-of-fit of the calibration model.
    """
    residuals = data - fit_model
    total_variation = np.sum((data - np.mean(data)) ** 2)
    residual_variation = np.sum(residuals**2)
    r2 = 1 - residual_variation / total_variation
    return r2
