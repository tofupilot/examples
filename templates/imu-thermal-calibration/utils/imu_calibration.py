import numpy as np
import os
from .imu_plotting import plot_sensor_data

# TODO: remove save path
# TODO: remove check on max bias

def calibrate_accelerometer(data, save_path="results", polynomial_order=3, max_bias_threshold=0.5):
    data['imu.acc.z'] = data['imu.acc.z'] + 9.81
    axes = ['imu.acc.x', 'imu.acc.y', 'imu.acc.z']
    y_label = 'Acceleration (m/s^2)'
    sensor_type = 'acc'
    return calibrate_sensor(data, axes, y_label, sensor_type, save_path, polynomial_order, max_bias_threshold)

def calibrate_gyroscope(data, save_path="results", polynomial_order=3, max_bias_threshold=0.5):
    axes = ['imu.gyro.x', 'imu.gyro.y', 'imu.gyro.z']
    y_label = 'Angular Rate (deg/s)'
    sensor_type = 'gyro'
    return calibrate_sensor(data, axes, y_label, sensor_type, save_path, polynomial_order, max_bias_threshold)

# TODO: why do we have 
def calibrate_sensor(data, axes, y_label, sensor_type, save_path, polynomial_order, max_bias_threshold):
    os.makedirs(save_path, exist_ok=True)
    temp = data['imu.temperature'].values
    poly_coeffs = {}
    residuals = {}
    biases = {}
    max_bias = 0.0
    figures = []

    for axis in axes:
        sensor_data = data[axis].values
        coeffs = np.polyfit(temp, sensor_data, polynomial_order)
        poly_coeffs[axis] = coeffs

        # Compute residuals
        fitted = np.polyval(coeffs, temp)
        res = sensor_data - fitted
        residuals[axis] = res

        # Compute bias at reference temperature
        reference_temp = 25.0
        bias_at_ref_temp = np.polyval(coeffs, reference_temp)
        biases[axis] = bias_at_ref_temp

        max_bias = max(max_bias, abs(bias_at_ref_temp))
        if abs(bias_at_ref_temp) > max_bias_threshold:
            raise ValueError(f'Bias exceeds maximum threshold for {axis}.')

        # Plot data
        fig_file = plot_sensor_data(temp, sensor_data, fitted, res, axis, y_label, sensor_type, save_path)
        figures.append(fig_file)

    correction_gains = {axis: -coeffs for axis, coeffs in poly_coeffs.items()}

    return {
        'correction_gains': correction_gains,
        'polynomial_coefficients': poly_coeffs,
        'residuals': residuals,
        'biases': biases,
        'max_bias': max_bias,
        'figures': figures
    }
