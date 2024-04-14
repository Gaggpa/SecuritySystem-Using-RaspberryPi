# SecuritySystem using Raspberry Pi

## Overview
The SecuritySystem project utilizes a Raspberry Pi 3B+ along with various components including a laser light, LDR (Light Dependent Resistor), buzzer, fingerprint sensor, and Pi camera to create a comprehensive security solution.

## Features
- **Laser Light**: Provides a visible deterrent and triggers the system upon intrusion.
- **LDR (Light Dependent Resistor)**: Detects changes in light conditions to activate the system.
- **Buzzer**: Audible alarm for alerting about security breaches.
- **Fingerprint Sensor**: Adds an extra layer of security by allowing access only to authorized individuals.
- **Pi Camera**: Captures images and videos for visual monitoring and recording.
- **Email Notification**: Sends captured images to the user's email for immediate alert and review.

## Working Process
- **Laser Interruption Detection**:
  - The system continuously monitors the laser light.
  - If the laser beam is interrupted, indicating a possible intrusion, the buzzer is activated, and an image is captured by the Pi camera.
- **Unauthorized Person Detection**:
  - When an unauthorized person is detected by the fingerprint sensor, similar actions are triggered (activating the buzzer and capturing an image).
- **Authorized Person Access**:
  - When an authorized person is authenticated via the fingerprint sensor, the laser light is deactivated to allow entry without triggering the alarm.

## Installation
1. Clone this repository to your Raspberry Pi.
2. Connect the components as per the provided circuit diagram.
3. Install the required dependencies.
4. Run the main script to start the SecuritySystem.

## Usage
- Activate the system using the provided interface or predefined triggers.
- Monitor the system's status and receive alerts for any security breaches via email.
- Access the recorded footage and captured images for further analysis if needed.

## Contributors
- [Gagpa]

## License
This project is not licensed. It is for personal use only.
