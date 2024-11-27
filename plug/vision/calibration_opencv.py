# plug/vision/calibration_opencv.py
import glob
import os
from typing import Optional

import cv2
import matplotlib.pyplot as plt
import numpy as np


def calibrate_camera(checkerboard_dims, square_size, image_path):
    """
    Calibrate the camera using the captured images.

    Args:
        checkerboard_dims (tuple): Number of inner corners per chessboard row and column (columns, rows).
        square_size (float): Size of a square in your defined unit (e.g., millimeters).
        image_path (str): Directory containing calibration images.

    Returns:
        dict: Calibration results including reprojection error, camera matrix, and distortion coefficients.
    """
    # Prepare object points
    objp = np.zeros((checkerboard_dims[1] * checkerboard_dims[0], 3), np.float32)
    objp[:, :2] = np.mgrid[0:checkerboard_dims[0], 0:checkerboard_dims[1]].T.reshape(-1, 2)
    objp *= square_size

    # Arrays to store object points and image points
    objpoints = []  # 3D points in real-world space
    imgpoints = []  # 2D points in image plane

    # Get list of images
    images = glob.glob(os.path.join(image_path, '*.jpg'))\
             + glob.glob(os.path.join(image_path, '*.png'))

    if not images:
        print('No calibration images found.')
        return None

    for fname in images:
        img = cv2.imread(fname)
        if img is None:
            print(f'Failed to load image {fname}')
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, checkerboard_dims, None)

        # If found, add object points, image points
        if ret:
            objpoints.append(objp)
            corners_subpix = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1),
                criteria=(cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)
            )
            imgpoints.append(corners_subpix)
        else:
            print(f'Chessboard not found in image {fname}')

    if not objpoints:
        print('No valid chessboard corners were found in any image.')
        return None

    # Camera calibration
    ret, camera_matrix, distortion_coefficients, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )

    if ret:
        print(f'Calibration successful with reprojection error: {ret}')
    else:
        print('Calibration failed.')
        return None

    # Save calibration parameters
    calibration_file = os.path.join(image_path, 'calibration_parameters.yaml')
    cv_file = cv2.FileStorage(calibration_file, cv2.FILE_STORAGE_WRITE)
    cv_file.write('camera_matrix', camera_matrix)
    cv_file.write('distortion_coefficients', distortion_coefficients)
    cv_file.write('reprojection_error', ret)
    cv_file.release()
    print(f'Calibration parameters saved to {calibration_file}')

    return {
        'reprojection_error': ret,
        'camera_matrix': camera_matrix,
        'distortion_coefficients': distortion_coefficients,
        'calibration_file_path': os.path.abspath(calibration_file)
    }


def validate_calibration(calibration_results: dict, image_path: str = None) -> Optional[np.ndarray]:
    """
    Validate the calibration results by displaying the original and undistorted images side by side.

    Args:
        calibration_results (dict): Calibration results containing camera matrix and distortion coefficients.
        image_path (str, optional): Path to the image to validate.
    """

    camera_matrix = calibration_results['camera_matrix']
    distortion_coefficients = calibration_results['distortion_coefficients']

    if image_path is None:
        print('Image path not provided for validation.')
        return

    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        print('Failed to load image for validation.')
        return

    # Undistort the image
    h, w = img.shape[:2]
    new_camera_matrix, _ = cv2.getOptimalNewCameraMatrix(
        camera_matrix, distortion_coefficients, (w, h), 1, (w, h)
    )
    undistorted_img = cv2.undistort(img, camera_matrix, distortion_coefficients, None, new_camera_matrix)

    # Combine images side by side
    combined = np.hstack((img, undistorted_img))

    # Convert BGR to RGB for Matplotlib
    combined_rgb = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)

    # Display the image using Matplotlib
    plt.figure(figsize=(10, 6))  # Adjust the figsize as needed
    plt.imshow(combined_rgb)
    plt.title('Validation - Original (Left) vs Undistorted (Right)', fontsize=16)
    plt.axis('off')  # Hide the axes
    plt.tight_layout()
    plt.show()

    return undistorted_img