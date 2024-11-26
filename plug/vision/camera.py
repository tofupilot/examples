# plug/vision/camera.py

import cv2
import time

from openhtf.plugs import BasePlug
from openhtf.util.configuration import CONF
from plug.vision.calibration_opencv import calibrate_camera, validate_calibration


class Camera(BasePlug):
    """
    Handles communication with the camera and integrates calibration functions.
    """

    def __init__(self):
        self.simulated_mode: bool = getattr(CONF, 'simulated', False)
        self.camera_id: int = getattr(CONF, 'camera_id', 0)
        self.cap = None

    def connect(self) -> bool:
        """
        Connect to the camera.

        Returns:
            bool: True if the camera is successfully connected, False otherwise.
        """
        if self.simulated_mode:
            print("Simulated mode enabled. Mocking camera connection.")
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
        if self.simulated_mode:
            print("Simulated image capture.")
            time.sleep(0.5)
            # Return a dummy image or load from a file if needed
            return None  # Simulate no image captured in simulated mode

        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture image from camera.")
            return None
        return frame

    def save_image(self, frame, image_path: str):
        """
        Save the captured image to the specified path.

        Args:
            frame: The image frame to save.
            image_path (str): The path to save the image.
        """
        if self.simulated_mode:
            print(f"Simulated image save to {image_path}")
            time.sleep(0.1)
            return

        cv2.imwrite(image_path, frame)
        print(f"Image saved to {image_path}")

    def capture_calibration_images(self, num_images: int, image_save_path: str):
        """
        Capture a specified number of calibration images.

        Args:
            num_images (int): Number of images to capture.
            image_save_path (str): Directory to save captured images.
        """
        images_captured = 0
        while images_captured < num_images:
            frame = self.capture_image()
            if frame is None:
                continue  # Try again if capture failed

            cv2.imshow('Calibration - Press SPACE to capture', frame)
            key = cv2.waitKey(1)
            if key % 256 == 32:  # SPACE pressed
                image_path = f"{image_save_path}/calibration_image_{images_captured}.jpg"
                self.save_image(frame, image_path)
                images_captured += 1
                print(f"Captured image {images_captured}/{num_images}")
                time.sleep(0.5)
            elif key % 256 == 27:  # ESC pressed
                print('Image capture cancelled by user.')
                break

        cv2.destroyAllWindows()

    def calibrate(self, checkerboard_dims, square_size, image_save_path):
        """
        Perform camera calibration using captured images.

        Args:
            checkerboard_dims (tuple): Dimensions of the checkerboard pattern (columns, rows).
            square_size (float): Size of a square in the checkerboard pattern.
            image_save_path (str): Directory containing captured images.

        Returns:
            dict: Calibration results, or None if calibration failed.
        """
        return calibrate_camera(checkerboard_dims, square_size, image_save_path)

    def validate(self, calibration_results):
        """
        Validate the calibration results by undistorting an image.

        Args:
            calibration_results (dict): Calibration results containing camera matrix and distortion coefficients.
        """
        validate_calibration(calibration_results, self.camera_id, self.simulated_mode)
