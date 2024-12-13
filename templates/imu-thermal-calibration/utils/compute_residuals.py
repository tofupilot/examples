import numpy as np

def compute_residuals(data: np.ndarray, fit_model: np.ndarray) -> dict:
    """
Computes residuals between sensor data and a fitted model.

Parameters:
data (numpy.ndarray): Sensor data.
fit_model (numpy.ndarray): Fitted model values for the same data.

Returns:
dict: Mean, standard deviation, and peak-to-peak residuals.

Use this function to evaluate calibration quality by analyzing deviations.
    """
    residuals = data - fit_model
    return {
        'mean_residual': np.mean(residuals),
        'std_residual': np.std(residuals),
        'p2p_residual': np.ptp(residuals)
    }
