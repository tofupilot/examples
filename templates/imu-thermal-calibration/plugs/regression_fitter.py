# plug/calibration/imu_thermal_calibration.py

import os
import numpy as np
import pandas
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend to avoid GUI operations
import matplotlib.pyplot as plt
from openhtf.plugs import BasePlug
from openhtf.util.configuration import CONF

class IMUThermalCalibration(BasePlug):
    """
    Plug for performing static thermal calibration of an IMU.

    Provides methods to calibrate accelerometer and gyroscope data.
    Reads IMU data from a DataFrame, fits polynomials to the sensor data
    as functions of temperature, computes residuals, calculates correction gains,
    and plots the data before and after correction.

    Configuration Parameters:
        - polynomial_order (int): Order of the polynomial to fit.
        - max_bias_threshold (float): Maximum acceptable bias for sensors.
        - data_save_path (str): Directory to save calibration results and plots.
    """

    def __init__(self):
        # Get configuration parameters
        self.polynomial_order = 3
        self.max_bias_threshold = 0.5
        self.data_save_path = "imu_calibration_results"
        os.makedirs(self.data_save_path, exist_ok=True)

    def calibrate_accelerometer(self, data: pandas.DataFrame) -> dict:
        # Remove gravity from the data
        data['imu.acc.z'] = data['imu.acc.z'] + 9.81

        # Define parameters specific to accelerometer
        axes = ['imu.acc.x', 'imu.acc.y', 'imu.acc.z']
        y_label = 'Acceleration (m/s^2)'
        sensor_type = 'acc'
        return self.calibrate_sensor(data, axes, y_label, sensor_type)

    def calibrate_gyroscope(self, data: pandas.DataFrame) -> dict:
        # Define parameters specific to gyroscope
        axes = ['imu.gyro.x', 'imu.gyro.y', 'imu.gyro.z']
        y_label = 'Angular Rate (deg/s)'
        sensor_type = 'gyro'
        return self.calibrate_sensor(data, axes, y_label, sensor_type)

    def calibrate_sensor(self, data, axes, y_label, sensor_type):
        """
General method to calibrate a sensor (accelerometer or gyroscope).

Args:
data (pandas.DataFrame): DataFrame containing the IMU data.
axes (list): List of axis column names.
y_label (str): Y-axis label for the plots.
sensor_type (str): Type of sensor ('acc' or 'gyro').

Returns:
dict: Calibration results including correction gains and figures.
        """
        temp = data['imu.temperature'].values
        poly_order = self.polynomial_order

        # Initialize dictionaries and variables
        poly_coeffs = {}
        residuals = {}
        biases = {}
        max_bias = 0.0
        figures = []

        for axis in axes:
            sensor_data = data[axis].values
            coeffs = np.polyfit(temp, sensor_data, poly_order)
            poly_coeffs[axis] = coeffs

            # Compute residuals
            fitted = np.polyval(coeffs, temp)
            res = sensor_data - fitted
            residuals[axis] = res

            # Compute bias at reference temperature
            reference_temp = 25.0  # Or any other reference temperature
            bias_at_ref_temp = np.polyval(coeffs, reference_temp)
            biases[axis] = bias_at_ref_temp
            max_bias = max(max_bias, abs(bias_at_ref_temp))
            if abs(bias_at_ref_temp) > self.max_bias_threshold:
                raise ValueError(f'Bias exceeds maximum acceptable threshold for {axis}.')

            # Plot data
            axis_label = axis  # You can adjust this if needed
            fig_file = self.plot_sensor_data(temp, sensor_data, fitted, res, axis_label, y_label, sensor_type)
            figures.append(fig_file)

        # Calculate correction gains
        correction_gains = {axis: -coeffs for axis, coeffs in poly_coeffs.items()}

        # Return results
        results = {
            'correction_gains': correction_gains,
            'polynomial_coefficients': poly_coeffs,
            'residuals': residuals,
            'biases': biases,
            'max_bias': max_bias,
            'figures': figures
        }
        return results

    def plot_sensor_data(self, temp, actual, fitted, residuals, axis_label, y_label, sensor_type):
        """
Plots sensor data and saves the figure.

Args:
temp (numpy.ndarray): Temperature data.
actual (numpy.ndarray): Actual sensor data.
fitted (numpy.ndarray): Fitted sensor data.
residuals (numpy.ndarray): Residuals.
axis_label (str): Label for the sensor axis.
y_label (str): Y-axis label for the plot.
sensor_type (str): Type of sensor ('acc' or 'gyro').

Returns:
str: Path to the saved figure file.
        """
        plt.figure(figsize=(10, 8))
        plt.subplot(3, 1, 1)
        plt.plot(temp, actual, label='Actual')
        plt.plot(temp, fitted, label='Fitted')
        plt.title(f'{sensor_type.capitalize()} {axis_label}')
        plt.ylabel(y_label)
        plt.legend()

        plt.subplot(3, 1, 2)
        plt.plot(temp, residuals)
        plt.title('Residuals')
        plt.ylabel('Residual')
        plt.xlabel('Temperature (°C)')

        plt.subplot(3, 1, 3)
        plt.hist(residuals, bins=50)
        plt.title('Residuals Histogram')
        plt.xlabel('Residual')
        plt.ylabel('Frequency')

        plt.tight_layout()

        # Sanitize the axis label for filenames
        axis_label_sanitized = axis_label.replace('.', '_')
        fig_file = os.path.join(self.data_save_path, f'{sensor_type}_{axis_label_sanitized}_calibration.png')
        plt.savefig(fig_file)
        plt.close()

        return fig_file
