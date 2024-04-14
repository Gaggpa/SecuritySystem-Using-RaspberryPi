import os
import time
from picamera import PiCamera

def capture_image():
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Define file name
    file_name = "captured_image.jpg"

    # Construct full file path
    file_path = os.path.join(current_dir, file_name)

    # Initialize PiCamera
    camera = PiCamera()

    try:
        # Adjust camera settings if needed
        # For example:
        # camera.resolution = (1920, 1080)  # Set resolution to 1920x1080

        # Wait for the camera to warm up (optional)
        time.sleep(2)

        # Capture image
        camera.capture(file_path)
        print(f"Image captured and saved to: {file_path}")

    finally:
        # Close PiCamera to release resources
        camera.close()

# Main function
if __name__ == "__main__":
    # Capture image and save it to the current directory
    capture_image()
