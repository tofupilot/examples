# plug/vision/camera.py
import glob
import os
import time
from typing import Optional

import cv2
from openhtf.plugs import BasePlug
from openhtf.util.configuration import CONF

from plug.vision.calibration_opencv import calibrate_camera, validate_calibration


class Camera(BasePlug):
    """
    Handles communication with the camera and integrates calibration functions.
    """
    simulated_mode: bool
    camera_id: int

    def __init__(self):
        self.simulated_mode: bool = getattr(CONF, 'simulated', False)
        self.camera_id: int = getattr(CONF, 'camera_id', 0)
        self.cap = None
        self.sample_images_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'sample_data', 'calibration_images')
        self.real_image_path = getattr(CONF, 'image_save_path')

    def connect(self) -> bool:
        """
        Connect to the camera.

        Returns:
            bool: True if the camera is successfully connected, False otherwise.
        """
        if self.simulated_mode:
            print("Simulated mode enabled. Skipping camera connection.")
            return True

        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            print(f"Cannot open camera with ID {self.camera_id}")
            return False
        print(f"Camera with ID {self.camera_id} opened successfully.")
        return True

    def disconnect(self):
        """
        Release the camera resource.
        """
        if self.cap:
            self.cap.release()
            print("Camera released.")

    def capture_image(self):
        """
        Capture an image from the camera.

        Returns:
            frame: Captured image frame, or None if capture failed.
        """
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture image from camera.")
            return None
        return frame

    @staticmethod
    def save_image(frame, image_path: str):
        """
        Save the captured image to the specified path.

        Args:
            frame: The image frame to save.
            image_path: Path to save it to
        """
        cv2.imwrite(image_path, frame)
        print(f"Image saved to {image_path}")

    def capture_calibration_images(self, num_images: int):
        """
        Capture a specified number of calibration images.

        Args:
            num_images (int): Number of images to capture.
        """
        if self.simulated_mode:
            print("Simulated mode: Using sample calibration images.")
            # No need to capture images; calibration will use sample images directly
            return

        images_captured = 0
        while images_captured < num_images:
            frame = self.capture_image()
            if frame is None:
                continue  # Try again if capture failed

            cv2.imshow('Calibration - Press SPACE to capture', frame)
            key = cv2.waitKey(1)
            if key % 256 == 32:  # SPACE pressed
                image_path = os.path.join(self.real_image_path, f'calibration_image_{images_captured}.jpg')
                self.save_image(frame, image_path)
                images_captured += 1
                print(f"Captured image {images_captured}/{num_images}")
                time.sleep(0.5)
            elif key % 256 == 27:  # ESC pressed
                print('Image capture cancelled by user.')
                break

        cv2.destroyAllWindows()

    def calibrate(self, checkerboard_dims: tuple, square_size: float) -> Optional[dict]:
        """
        Perform camera calibration using captured images.

        Args:
            checkerboard_dims (tuple): Dimensions of the checkerboard pattern (columns, rows).
            square_size (float): Size of a square in the checkerboard pattern.

        Returns:
            dict: Calibration results, or None if calibration failed.
        """
        if self.simulated_mode:
            # Use sample images for calibration
            return calibrate_camera(checkerboard_dims, square_size, self.sample_images_path)
        else:
            return calibrate_camera(checkerboard_dims, square_size, self.real_image_path)

    def validate(self, calibration_results: dict) -> str:
        """
        Validate the calibration results by undistorting an image.

        Args:
            calibration_results (dict): Calibration results containing camera matrix and distortion coefficients.
        """
        if self.simulated_mode:
            undistorted_img_path = os.path.join(self.sample_images_path, f'undistorted_image.jpg')
            undistorted_frame = validate_calibration(calibration_results,
                                                     image_path=( glob.glob(os.path.join(self.sample_images_path, '*.jpg'))
                                                                  + glob.glob(os.path.join(self.sample_images_path, '*.png')) )[0])
        else:
            undistorted_img_path = os.path.join(self.real_image_path, f'undistorted_image.jpg')
            undistorted_frame = validate_calibration(calibration_results,
                                                     image_path=( glob.glob(os.path.join(self.real_image_path, '*.jpg'))
                                                                  + glob.glob(os.path.join(self.real_image_path, '*.png')) )[0])
        self.save_image(undistorted_frame, undistorted_img_path)

        return os.path.abspath(undistorted_img_path)
