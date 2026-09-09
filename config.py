# Configuration file for Raspberry Pi Hole Detection & Pump Control System
# Raspberry Pi 3 Model B (40-pin GPIO)

import RPi.GPIO as GPIO

# ============================================================================
# GPIO PIN CONFIGURATION
# ============================================================================

# Relay Control Pins (10 channels)
RELAY_PINS = {
    1: 4,    # IN1 -> GPIO 4  (Pin 7)
    2: 17,   # IN2 -> GPIO 17 (Pin 11)
    3: 27,   # IN3 -> GPIO 27 (Pin 13)
    4: 22,   # IN4 -> GPIO 22 (Pin 15)
    5: 23,   # IN5 -> GPIO 23 (Pin 16)
    6: 24,   # IN6 -> GPIO 24 (Pin 18)
    7: 25,   # IN7 -> GPIO 25 (Pin 22)
    8: 5,    # IN8 -> GPIO 5  (Pin 29)
    9: 6,    # IN9 -> GPIO 6  (Pin 31)
    10: 13   # IN10 -> GPIO 13 (Pin 33)
}

# Ultrasonic Sensor Pins
ULTRASONIC_TRIG = 18  # TRIG -> GPIO 18 (Pin 12)
ULTRASONIC_ECHO = 20  # ECHO -> GPIO 20 (Pin 38) with voltage divider

# GPIO Mode
GPIO_MODE = GPIO.BCM  # Broadcom SOC channel numbering

# ============================================================================
# CAMERA CONFIGURATION
# ============================================================================

CAMERA_RESOLUTION = (640, 480)  # Resolution for hole detection
CAMERA_FRAMERATE = 30
CAMERA_ROTATION = 0  # Rotate image if needed (0, 90, 180, 270)

# ============================================================================
# HOLE DETECTION CONFIGURATION
# ============================================================================

# Hole detection thresholds
HOLE_MIN_AREA = 500      # Minimum pixel area to consider as hole
HOLE_MAX_AREA = 50000    # Maximum pixel area
HOLE_DETECTION_THRESHOLD = 100  # Gray level threshold for hole detection
MIN_CONTOUR_PERIMETER = 50  # Minimum contour perimeter

# Color range for hole detection (HSV)
# Dark/black holes
HOLE_LOWER_HSV = (0, 0, 0)
HOLE_UPPER_HSV = (180, 255, 50)  # Low value = dark colors

# ============================================================================
# ULTRASONIC SENSOR CONFIGURATION
# ============================================================================

# Speed of sound (cm/microsecond)
SOUND_SPEED = 0.0343  # cm/µs

# Measurement parameters
MEASUREMENT_TIMEOUT = 0.04  # 40ms timeout for each measurement
MEASUREMENTS_PER_CYCLE = 5   # Number of measurements to average
MEASUREMENT_DELAY = 0.1      # Delay between measurements (seconds)

# Hole size zones (based on measured distance from sensor)
# Adjust these values based on your sensor height and hole sizes
HOLE_SIZE_ZONES = {
    'small': (2, 5),      # 2-5 cm hole size -> Pump 1-3
    'medium': (5, 10),    # 5-10 cm hole size -> Pump 4-7
    'large': (10, 20)     # 10-20 cm hole size -> Pump 8-10
}

# ============================================================================
# ZONE MAPPING (Which pump for each detected hole zone)
# ============================================================================

# Map detected zones to pump numbers
ZONE_PUMP_MAP = {
    'small': [1, 2, 3],        # Small holes: use pumps 1-3
    'medium': [4, 5, 6, 7],    # Medium holes: use pumps 4-7
    'large': [8, 9, 10]        # Large holes: use pumps 8-10
}

# ============================================================================
# PUMP CONTROL CONFIGURATION
# ============================================================================

# Pump activation parameters
PUMP_ON_DURATION = 5.0   # Seconds to keep pump ON
PUMP_OFF_DURATION = 2.0  # Seconds to keep pump OFF between cycles
PUMP_CYCLES = 3          # Number of ON/OFF cycles per hole detection

# Relay activation logic
RELAY_ACTIVE_STATE = GPIO.HIGH    # HIGH = relay ON, LOW = relay OFF
RELAY_INACTIVE_STATE = GPIO.LOW

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = '/var/log/hole_detection.log'

# Detection mode
DETECTION_MODE = 'continuous'  # 'continuous' or 'triggered'
DETECTION_DELAY = 0.5  # Delay between detection cycles (seconds)

# Message configuration
SEND_MESSAGES = True  # Enable message sending to external system
MESSAGE_SERVER_IP = '192.168.1.100'  # Server IP for status messages
MESSAGE_SERVER_PORT = 8000            # Server port

# Minimum time between pump activations for same zone (seconds)
MIN_PUMP_INTERVAL = 10

# ============================================================================
# CAMERA STREAMING (Optional)
# ============================================================================

ENABLE_STREAMING = False  # Set to True for live camera stream
STREAM_PORT = 8081
STREAM_RESOLUTION = (320, 240)

# ============================================================================
# DEBUG MODE
# ============================================================================

DEBUG = True  # Enable debug prints and test mode
TEST_MODE = False  # Simulate hole detection without camera

print("✓ Configuration loaded successfully")
