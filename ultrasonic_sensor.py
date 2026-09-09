# Ultrasonic Sensor Module - Measure hole size with HC-SR04
# Raspberry Pi 3 Model B with voltage divider for ECHO pin

import RPi.GPIO as GPIO
import time
import logging
from config import (
    ULTRASONIC_TRIG, ULTRASONIC_ECHO, GPIO_MODE,
    SOUND_SPEED, MEASUREMENT_TIMEOUT, MEASUREMENTS_PER_CYCLE,
    MEASUREMENT_DELAY, HOLE_SIZE_ZONES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltrasonicSensor:
    """HC-SR04 Ultrasonic sensor for measuring hole size"""
    
    def __init__(self):
        """Initialize ultrasonic sensor"""
        self.trig_pin = ULTRASONIC_TRIG
        self.echo_pin = ULTRASONIC_ECHO
        self.sound_speed = SOUND_SPEED
        self.timeout = MEASUREMENT_TIMEOUT
        self._setup_gpio()
        logger.info("✓ Ultrasonic Sensor initialized")
    
    def _setup_gpio(self):
        """Setup GPIO pins for ultrasonic sensor"""
        try:
            GPIO.setmode(GPIO_MODE)
            GPIO.setwarnings(False)
            
            # TRIG as OUTPUT
            GPIO.setup(self.trig_pin, GPIO.OUT)
            GPIO.output(self.trig_pin, GPIO.LOW)
            
            # ECHO as INPUT
            GPIO.setup(self.echo_pin, GPIO.IN)
            
            logger.info(f"✓ TRIG pin {self.trig_pin} (GPIO OUT) initialized")
            logger.info(f"✓ ECHO pin {self.echo_pin} (GPIO IN) initialized")
            
            # Warm up sensor
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"✗ GPIO setup failed: {e}")
            raise
    
    def _measure_distance(self):
        """
        Measure distance once using HC-SR04
        Returns: distance in cm, or None if measurement fails
        """
        try:
            # Send 10µs pulse on TRIG
            GPIO.output(self.trig_pin, GPIO.HIGH)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(self.trig_pin, GPIO.LOW)
            
            # Wait for ECHO to go HIGH
            pulse_start = time.time()
            while GPIO.input(self.echo_pin) == GPIO.LOW:
                pulse_start = time.time()
                if (time.time() - pulse_start) > self.timeout:
                    logger.warning("✗ Timeout waiting for ECHO HIGH")
                    return None
            
            # Wait for ECHO to go LOW
            pulse_end = time.time()
            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                pulse_end = time.time()
                if (pulse_end - pulse_start) > self.timeout:
                    logger.warning("✗ Timeout waiting for ECHO LOW")
                    return None
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * self.sound_speed) / 2  # Divide by 2 (round trip)
            
            return distance
            
        except Exception as e:
            logger.error(f"✗ Distance measurement error: {e}")
            return None
    
    def measure_distance(self, num_measurements=None):
        """
        Measure distance and average multiple readings
        Returns: average distance in cm
        """
        measurements = num_measurements or MEASUREMENTS_PER_CYCLE
        valid_readings = []
        
        logger.info(f"► Taking {measurements} distance measurements...")
        
        for i in range(measurements):
            distance = self._measure_distance()
            
            if distance is not None:
                valid_readings.append(distance)
                logger.debug(f"  Measurement {i+1}: {distance:.2f} cm")
            
            if i < measurements - 1:
                time.sleep(MEASUREMENT_DELAY)
        
        if not valid_readings:
            logger.error("✗ No valid distance measurements obtained")
            return None
        
        avg_distance = sum(valid_readings) / len(valid_readings)
        logger.info(f"✓ Average distance: {avg_distance:.2f} cm ({len(valid_readings)}/{measurements} valid)")
        
        return avg_distance
    
    def classify_hole_size(self, distance):
        """
        Classify hole size based on measured distance
        Returns: zone name ('small', 'medium', 'large') or None
        """
        if distance is None:
            return None
        
        zones = HOLE_SIZE_ZONES
        
        for zone_name, (min_dist, max_dist) in zones.items():
            if min_dist <= distance <= max_dist:
                logger.info(f"✓ Hole classified as '{zone_name}' (distance: {distance:.2f} cm)")
                return zone_name
        
        logger.warning(f"⚠ Hole size {distance:.2f} cm outside defined zones")
        return 'unknown'
    
    def get_hole_info(self):
        """
        Get complete hole information: distance and classification
        Returns: dict with distance and zone
        """
        distance = self.measure_distance()
        
        if distance is None:
            return {
                'distance': None,
                'zone': None,
                'status': 'FAILED'
            }
        
        zone = self.classify_hole_size(distance)
        
        info = {
            'distance': distance,
            'zone': zone,
            'status': 'SUCCESS'
        }
        
        logger.info(f"📏 Hole Info: Distance={distance:.2f}cm, Zone={zone}")
        return info
    
    def continuous_monitoring(self, interval=1):
        """
        Continuously monitor and report hole sizes
        Press Ctrl+C to stop
        """
        logger.info("► Starting continuous monitoring (Press Ctrl+C to stop)...")
        
        try:
            while True:
                hole_info = self.get_hole_info()
                print(f"[{time.strftime('%H:%M:%S')}] Distance: {hole_info['distance']:.2f} cm | Zone: {hole_info['zone']}")
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("✓ Monitoring stopped by user")
    
    def cleanup(self):
        """Cleanup GPIO"""
        try:
            GPIO.cleanup()
            logger.info("✓ GPIO cleaned up")
        except Exception as e:
            logger.error(f"✗ GPIO cleanup failed: {e}")

# Test function
if __name__ == "__main__":
    sensor = UltrasonicSensor()
    
    try:
        print("\n=== ULTRASONIC SENSOR TEST ===\n")
        
        print("Test 1: Single distance measurement")
        distance = sensor.measure_distance(num_measurements=3)
        if distance:
            print(f"Distance: {distance:.2f} cm\n")
        
        print("Test 2: Hole size classification")
        hole_info = sensor.get_hole_info()
        print(f"Hole Info: {hole_info}\n")
        
        print("Test 3: Continuous monitoring (5 seconds)")
        start_time = time.time()
        while time.time() - start_time < 5:
            info = sensor.get_hole_info()
            print(f"Distance: {info['distance']:.2f} cm | Zone: {info['zone']}")
            time.sleep(1)
        
        print("\n✓ All tests completed")
        
    except KeyboardInterrupt:
        print("\n✗ Test interrupted by user")
    finally:
        sensor.cleanup()
