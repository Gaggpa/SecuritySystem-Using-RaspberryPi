import time
import RPi.GPIO as GPIO
from picamera import PiCamera
import serial
import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint
from pyfingerprint.pyfingerprint import FINGERPRINT_CHARBUFFER1
import threading
import smtplib
from email.message import EmailMessage
import os

# Define GPIO pin numbers
ldr_pin = 11
buzzer_pin = 18
laser_pin = 16

# Setup GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ldr_pin, GPIO.IN)
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.setup(laser_pin, GPIO.OUT)
GPIO.output(buzzer_pin, GPIO.LOW)  # Initialize buzzer as off
GPIO.output(laser_pin, GPIO.HIGH)  # Initialize laser as on

print("Security System Initialized")
time.sleep(1)

# Initialize fingerprint sensor serial connection (replace port if needed)
finger = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

# Flag to indicate if an authorized person is currently detected
authorized_person_detected = False

# Functions

def check_authorized_person():
    global authorized_person_detected
    
    try:
        f = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)

        if f.verifyPassword() == False:
            raise ValueError('The given fingerprint sensor password is wrong!')

        ## Tries to search the finger and calculate hash
        print('Waiting for finger...')
        while f.readImage() == False:
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(FINGERPRINT_CHARBUFFER1)

        ## Searchs template
        result = f.searchTemplate()

        positionNumber = result[0]
        accuracyScore = result[1]

        if positionNumber == -1:
            print('No match found!')
            authorized_person_detected = False
        else:
            print("Authorized person detected")
            authorized_person_detected = True

    except ValueError as ve:
        # Log the exception without setting authorized_person_detected to False
        print('ValueError:', ve)
        log_event("Fingerprint sensor ValueError: " + str(ve))
    except Exception as e:
        if "The received packet do not begin with a valid header!" in str(e):
            # Log the exception without setting authorized_person_detected to False
            print('Ignoring exception:', e)
            log_event("Fingerprint sensor exception: " + str(e))
        else:
            # Log other exceptions and set authorized_person_detected to False
            print('Operation failed!')
            print('Exception message: ' + str(e))
            authorized_person_detected = False
            log_event("Fingerprint sensor communication error: " + str(e))

def turn_off_system():
    """Turns off the laser."""
    GPIO.output(laser_pin, GPIO.LOW)
    print("Laser off")
    

# Define global variable to store previous laser state
prev_laser_interrupted = None

def is_laser_interrupted():
    global prev_laser_interrupted, authorized_person_detected

    # Check if an authorized person is detected and laser is already off
    if authorized_person_detected and GPIO.input(laser_pin) == GPIO.LOW:
        return False

    # Read current laser state
    current_state = GPIO.input(ldr_pin)
    
    # Check if the state has changed
    if current_state != prev_laser_interrupted:
        prev_laser_interrupted = current_state
        if current_state == GPIO.HIGH:  # Check for opposite condition
            print("Laser Interrupt")
            return True  # Return True when interrupted
        else:
            print("No Laser Interrupt")
            return False  # Return False when not interrupted
    
    return False  # Return False when state hasn't changed

def activate_alarm():
    """Turns on the buzzer."""
    GPIO.output(buzzer_pin, GPIO.HIGH)
    print("Buzzer on")
    
def reset_system():
    """Resets the system after a timeout."""
    GPIO.output(buzzer_pin, GPIO.LOW)  # Turn off buzzer
    GPIO.output(laser_pin, GPIO.HIGH)  # Turn on laser
    print("Buzzer off, Laser on")

def capture_image():
    """Captures an image using the camera and saves it with a timestamp."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    image_filename = f"intrusion_{timestamp}.jpg"
    camera = None
    try:
        camera = PiCamera()
        camera.resolution = (1024, 768)  # Adjust resolution as needed
        camera.start_preview()
        time.sleep(2)  # Let the camera warm up
        camera.capture(image_filename)
        print(f"Image captured: {image_filename}")
        return image_filename  # Return the path of the captured image
    except Exception as e:
        print(f"Error capturing image: {e}")
        return None
    finally:
        if camera:
            camera.stop_preview()
            camera.close()


def log_event(message):
    """Logs a security event message to a file (implementation depends on your needs)."""
    # Replace with your preferred logging method (e.g., print to console, write to file)
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: {message}")

# Email settings
from_email_addr = "raspberypialert@gmail.com"
from_email_pass = "efrt bzdc srud mhdi"
to_email_addr = "loginforallup@gmail.com"

def send_email(subject, body, attachment_path=None):
    """Send an email with optional attachment."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['From'] = from_email_addr
    msg['To'] = to_email_addr
    msg['Subject'] = subject
    
    if attachment_path:
        with open(attachment_path, 'rb') as file:
            file_data = file.read()
            file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype='image', subtype='jpg', filename=file_name)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email_addr, from_email_pass)
    server.send_message(msg)
    print('Email sent')
    server.quit()

# Function to continuously check for laser interruption
def check_laser():
    try:
        while True: 
                if is_laser_interrupted():
                    image_path = capture_image()  # Capture image and get the path
                    activate_alarm()
                    log_event("Unauthorized access attempt")
                    send_email("Security Alert", "Unauthorized access attempt detected", image_path)
                    time.sleep(5)
                    reset_system()
                time.sleep(0.1)  # Adjust sleep duration as needed
    except KeyboardInterrupt:
        pass

# Function to continuously check for authorized person and unauthorized person
def check_authorization():
    try:
        while True:
            check_authorized_person()  # Check for authorized person
            if authorized_person_detected:
                turn_off_system()  # If authorized person detected, turn off the system
            else:
                log_event("Unauthorized access attempt")
                image_path = capture_image()  # Capture image and get the path
                activate_alarm()
                send_email("Security Alert", "Unauthorized access attempt detected", image_path)
                time.sleep(5)
                reset_system()
            time.sleep(0.1)  # Adjust sleep duration as needed
            
    except KeyboardInterrupt:
        pass

# Main function to start both threads
def main():
    laser_thread = threading.Thread(target=check_laser)
    authorization_thread = threading.Thread(target=check_authorization)

    laser_thread.start()
    authorization_thread.start()

    laser_thread.join()
    authorization_thread.join()

if __name__ == "__main__":
    main()
