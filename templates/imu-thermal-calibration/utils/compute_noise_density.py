import numpy as np

def compute_noise_density(data: np.ndarray, sampling_rate: int = 100) -> float:
    """
Computes noise density for sensor data.

Parameters:
data (numpy.ndarray): The raw sensor data.
sampling_rate (int): Sampling rate of the sensor in Hz.

Returns:
float: Estimated noise density in units/sqrt(Hz).

Use this function to evaluate sensor precision by measuring noise levels.
    """
    # Detrend the first 50 samples to remove bias or drift, isolating sensor noise.
    # The initial samples are assumed stable, making them ideal for estimating noise density.
    # Short duration ensures minimal environmental variation or long-term drift effects.
    detrended_data = data[:50] - np.mean(data[:50])
    noise_std = np.std(detrended_data)
    noise_density = noise_std / np.sqrt(sampling_rate)
    return noise_density
