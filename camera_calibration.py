# camera_calibration.py
import os
from typing import Optional

import openhtf as htf
from openhtf.plugs import plug, user_input
from openhtf.util.configuration import CONF
from tofupilot.openhtf import TofuPilot

from plug.vision.camera import Camera

# Calibration configuration
CONF.declare('calibration_pattern', default_value='checkerboard', description='Type of calibration pattern.')
CONF.declare('checkerboard_dims', default_value=(11, 7), description='Number of inner corners per chessboard row and column (columns, rows).')
CONF.declare('square_size', default_value=25.0, description='Size of a square in your defined unit (e.g., millimeters).')
CONF.declare('num_images', default_value=15, description='Number of calibration images to capture.')
CONF.declare('image_save_path', default_value='calibration_images', description='Directory to save calibration images.')

# Camera connection configuration
CONF.declare('camera_id', default_value=0, description='Camera device ID.')

# Simulated run with no hardware or real run?
CONF.declare('simulated', default_value=False, description='Simulated mode toggle.')

# Ensure the image save directory exists
os.makedirs(CONF.image_save_path, exist_ok=True)

## Step 1: Check if the camera is connected and accessible
@plug(camera=Camera)
@htf.PhaseOptions(repeat_limit=5, timeout_s=10)
def check_camera_connection(test, camera) -> htf.PhaseResult:
    if camera.connect():
        test.logger.info('Camera connected successfully.')
        return htf.PhaseResult.CONTINUE
    else:
        test.logger.warning('Camera connection failed. Retrying...')
        return htf.PhaseResult.REPEAT

## Step 2: Capture calibration images
@plug(camera=Camera)
def capture_calibration_images(test, camera):
    test.logger.info('Starting image capture for calibration.')
    camera.capture_calibration_images(CONF.num_images)
    test.logger.info('Image capture completed.')

## Step 3: Run calibration algorithm
@plug(camera=Camera)
@htf.measures(
    htf.Measurement('reprojection_error').with_units('pixel')
)
def run_calibration(test, camera) -> htf.PhaseResult:
    test.logger.info('Starting camera calibration.')
    calibration_results = camera.calibrate(CONF.checkerboard_dims, CONF.square_size)
    if calibration_results:
        reprojection_error = float(calibration_results['reprojection_error'])
        test.measurements.reprojection_error = reprojection_error
        test.logger.info(f"Calibration successful with reprojection error: {reprojection_error}")

        # Store calibration data in test state using dictionary syntax
        test.state['calibration_results'] = calibration_results
        test.attach_from_file(calibration_results['calibration_file_path'])
        return htf.PhaseResult.CONTINUE
    else:
        test.logger.error('Calibration failed.')
        return htf.PhaseResult.STOP

## Step 4: Validate calibration results
@plug(camera=Camera)
def validate_calibration(test, camera) -> htf.PhaseResult:
    test.logger.info('Validating calibration results.')
    # Retrieve calibration data from test state using dictionary syntax
    calibration_data = test.state.get('calibration_results', None)
    if not calibration_data:
        test.logger.error('Calibration data not found.')
        return htf.PhaseResult.STOP

    val_img_path=camera.validate(calibration_data)
    test.attach_from_file(val_img_path)

    # Prompt the user for validation
    answer = input("Is the calibration acceptable? (y/n): ").strip().lower()
    if answer == 'y':
        test.logger.info('Calibration validation completed.')
        return htf.PhaseResult.CONTINUE
    else:
        test.logger.error('User did not validate calibration.')
        return htf.PhaseResult.STOP


## Teardown
@plug(camera=Camera)
def teardown(test, camera) -> None:
    camera.disconnect()
    test.logger.info('Teardown completed. Camera disconnected.')

# Main test procedure with TofuPilot integration
def main():
    test = htf.Test(
        check_camera_connection,
        capture_calibration_images,
        run_calibration,
        validate_calibration,
        teardown,
        procedure_name="Camera Calibration Test",
        procedure_id="CCT-1"
    )

    with TofuPilot(test):
        test.execute(test_start=user_input.prompt_for_test_start())

if __name__ == "__main__":
    main()
