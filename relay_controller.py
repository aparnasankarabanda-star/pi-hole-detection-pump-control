# Relay Module - Control 10 pumps via GPIO relays
# Raspberry Pi 3 Model B

import RPi.GPIO as GPIO
import time
import logging
from config import (
    RELAY_PINS, GPIO_MODE, RELAY_ACTIVE_STATE, 
    RELAY_INACTIVE_STATE, PUMP_ON_DURATION, PUMP_OFF_DURATION, PUMP_CYCLES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RelayController:
    """Control 10 pumps via relay channels"""
    
    def __init__(self):
        """Initialize relay controller"""
        self.relay_pins = RELAY_PINS
        self.active_state = RELAY_ACTIVE_STATE
        self.inactive_state = RELAY_INACTIVE_STATE
        self.pump_status = {i: False for i in range(1, 11)}
        self._setup_gpio()
        logger.info("✓ Relay Controller initialized")
    
    def _setup_gpio(self):
        """Setup GPIO pins for relay control"""
        try:
            GPIO.setmode(GPIO_MODE)
            GPIO.setwarnings(False)
            
            # Setup all relay pins as OUTPUT
            for pump_num, gpio_pin in self.relay_pins.items():
                GPIO.setup(gpio_pin, GPIO.OUT)
                GPIO.output(gpio_pin, self.inactive_state)
                logger.info(f"✓ GPIO {gpio_pin} (Pump {pump_num}) initialized")
                
        except Exception as e:
            logger.error(f"✗ GPIO setup failed: {e}")
            raise
    
    def activate_pump(self, pump_number):
        """Activate a single pump"""
        if pump_number not in self.relay_pins:
            logger.error(f"✗ Invalid pump number: {pump_number}")
            return False
        
        try:
            gpio_pin = self.relay_pins[pump_number]
            GPIO.output(gpio_pin, self.active_state)
            self.pump_status[pump_number] = True
            logger.info(f"✓ Pump {pump_number} (GPIO {gpio_pin}) ACTIVATED")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to activate pump {pump_number}: {e}")
            return False
    
    def deactivate_pump(self, pump_number):
        """Deactivate a single pump"""
        if pump_number not in self.relay_pins:
            logger.error(f"✗ Invalid pump number: {pump_number}")
            return False
        
        try:
            gpio_pin = self.relay_pins[pump_number]
            GPIO.output(gpio_pin, self.inactive_state)
            self.pump_status[pump_number] = False
            logger.info(f"✓ Pump {pump_number} (GPIO {gpio_pin}) DEACTIVATED")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to deactivate pump {pump_number}: {e}")
            return False
    
    def pump_cycle(self, pump_number, on_duration=None, off_duration=None, cycles=None):
        """Run pump in ON/OFF cycles"""
        if pump_number not in self.relay_pins:
            logger.error(f"✗ Invalid pump number: {pump_number}")
            return False
        
        on_time = on_duration or PUMP_ON_DURATION
        off_time = off_duration or PUMP_OFF_DURATION
        num_cycles = cycles or PUMP_CYCLES
        
        try:
            logger.info(f"► Starting pump {pump_number} cycles: {num_cycles}x ({on_time}s ON, {off_time}s OFF)")
            
            for cycle in range(num_cycles):
                # Turn ON
                self.activate_pump(pump_number)
                time.sleep(on_time)
                
                # Turn OFF
                self.deactivate_pump(pump_number)
                
                if cycle < num_cycles - 1:  # Don't sleep after last cycle
                    time.sleep(off_time)
            
            logger.info(f"✓ Pump {pump_number} cycles completed")
            return True
        except Exception as e:
            logger.error(f"✗ Pump {pump_number} cycle failed: {e}")
            self.deactivate_pump(pump_number)
            return False
    
    def activate_multiple_pumps(self, pump_numbers):
        """Activate multiple pumps simultaneously"""
        results = {}
        for pump_num in pump_numbers:
            results[pump_num] = self.activate_pump(pump_num)
        logger.info(f"✓ Activated pumps: {pump_numbers}")
        return results
    
    def deactivate_multiple_pumps(self, pump_numbers):
        """Deactivate multiple pumps"""
        results = {}
        for pump_num in pump_numbers:
            results[pump_num] = self.deactivate_pump(pump_num)
        logger.info(f"✓ Deactivated pumps: {pump_numbers}")
        return results
    
    def deactivate_all_pumps(self):
        """Emergency stop - deactivate all pumps"""
        logger.warning("⚠ EMERGENCY STOP - Deactivating all pumps")
        for pump_num in range(1, 11):
            self.deactivate_pump(pump_num)
        logger.info("✓ All pumps deactivated")
    
    def get_pump_status(self):
        """Get status of all pumps"""
        return self.pump_status.copy()
    
    def get_pump_status_string(self):
        """Get formatted pump status string"""
        status_str = "Pump Status: "
        for pump_num in range(1, 11):
            state = "ON" if self.pump_status[pump_num] else "OFF"
            status_str += f"P{pump_num}:{state} "
        return status_str
    
    def cleanup(self):
        """Cleanup GPIO"""
        try:
            self.deactivate_all_pumps()
            GPIO.cleanup()
            logger.info("✓ GPIO cleaned up")
        except Exception as e:
            logger.error(f"✗ GPIO cleanup failed: {e}")

# Test function
if __name__ == "__main__":
    relay = RelayController()
    
    try:
        print("\n=== RELAY CONTROLLER TEST ===\n")
        
        # Test individual pumps
        print("Test 1: Activate pumps 1-3 one by one")
        for i in range(1, 4):
            relay.activate_pump(i)
            time.sleep(1)
        
        print("\nTest 2: Deactivate all pumps")
        relay.deactivate_all_pumps()
        time.sleep(1)
        
        print("\nTest 3: Run pump 1 in cycles")
        relay.pump_cycle(1, on_duration=2, off_duration=1, cycles=2)
        
        print("\nTest 4: Activate multiple pumps (4,5,6)")
        relay.activate_multiple_pumps([4, 5, 6])
        time.sleep(2)
        relay.deactivate_all_pumps()
        
        print("\n✓ All tests completed")
        
    except KeyboardInterrupt:
        print("\n✗ Test interrupted by user")
    finally:
        relay.cleanup()
