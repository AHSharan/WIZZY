import unittest
import RPi.GPIO as GPIO
import time
from unittest.mock import patch, MagicMock

# Import the GPIO pins from test_app.py
IR_LEFT = 14    # GPIO14
IR_CENTER = 15  # GPIO15
IR_RIGHT = 24   # GPIO24

class TestIRSensors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup GPIO mode and warnings"""
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        # Setup IR sensor pins
        GPIO.setup(IR_LEFT, GPIO.IN)
        GPIO.setup(IR_CENTER, GPIO.IN)
        GPIO.setup(IR_RIGHT, GPIO.IN)

    def setUp(self):
        """Reset before each test"""
        self.sensor_values = {
            'left': 0,
            'center': 0,
            'right': 0
        }

    @classmethod
    def tearDownClass(cls):
        """Cleanup GPIO"""
        GPIO.cleanup()

    def read_all_sensors(self):
        """Read all three IR sensors"""
        return {
            'left': GPIO.input(IR_LEFT),
            'center': GPIO.input(IR_CENTER),
            'right': GPIO.input(IR_RIGHT)
        }

    def test_sensor_initialization(self):
        """Test if sensors are properly initialized"""
        # Check if pins are set up as inputs
        self.assertEqual(GPIO.gpio_function(IR_LEFT), GPIO.IN)
        self.assertEqual(GPIO.gpio_function(IR_CENTER), GPIO.IN)
        self.assertEqual(GPIO.gpio_function(IR_RIGHT), GPIO.IN)

    def test_sensor_reading_format(self):
        """Test if sensor readings return correct format"""
        readings = self.read_all_sensors()
        
        # Check if all expected keys exist
        self.assertIn('left', readings)
        self.assertIn('center', readings)
        self.assertIn('right', readings)
        
        # Check if values are boolean (0 or 1)
        for value in readings.values():
            self.assertIn(value, [0, 1])

    @patch('RPi.GPIO.input')
    def test_obstacle_detection(self, mock_gpio_input):
        """Test obstacle detection scenarios"""
        # Test case 1: No obstacles
        mock_gpio_input.side_effect = [1, 1, 1]  # Left, Center, Right (inverted)
        readings = self.read_all_sensors()
        self.assertEqual(readings, {'left': 0, 'center': 0, 'right': 0})

        # Test case 2: Center obstacle
        mock_gpio_input.side_effect = [1, 0, 1]  # Left, Center, Right (inverted)
        readings = self.read_all_sensors()
        self.assertEqual(readings, {'left': 0, 'center': 1, 'right': 0})

        # Test case 3: All obstacles
        mock_gpio_input.side_effect = [0, 0, 0]  # Left, Center, Right (inverted)
        readings = self.read_all_sensors()
        self.assertEqual(readings, {'left': 1, 'center': 1, 'right': 1})

    def test_real_sensor_reading(self):
        """Test actual sensor readings (requires physical sensors)"""
        readings = self.read_all_sensors()
        
        # Log the actual readings
        print(f"\nReal sensor readings: {readings}")
        
        # Basic validation of readings
        for key, value in readings.items():
            self.assertIn(value, [0, 1], f"Sensor {key} returned invalid value: {value}")

    def test_rapid_readings(self):
        """Test rapid consecutive readings"""
        readings = []
        for _ in range(10):  # Take 10 rapid readings
            readings.append(self.read_all_sensors())
            time.sleep(0.1)  # Small delay between readings
        
        # Verify all readings have valid values
        for reading in readings:
            self.assertEqual(len(reading), 3)  # Should have 3 sensor values
            for value in reading.values():
                self.assertIn(value, [0, 1])

    @patch('RPi.GPIO.input')
    def test_edge_cases(self, mock_gpio_input):
        """Test edge cases and error conditions"""
        # Test case 1: Alternating values
        mock_gpio_input.side_effect = [1, 0, 1, 0, 1, 0]
        readings1 = self.read_all_sensors()
        readings2 = self.read_all_sensors()
        self.assertNotEqual(readings1, readings2)

        # Test case 2: Simulate sensor failure (always returns 1)
        mock_gpio_input.return_value = 1
        readings = self.read_all_sensors()
        self.assertEqual(readings, {'left': 1, 'center': 1, 'right': 1})

    def test_sensor_consistency(self):
        """Test sensor reading consistency"""
        initial_reading = self.read_all_sensors()
        time.sleep(0.5)  # Wait half second
        second_reading = self.read_all_sensors()
        
        # If no obstacle has moved, readings should be consistent
        # Log both readings for analysis
        print(f"\nInitial reading: {initial_reading}")
        print(f"Second reading: {second_reading}")

def run_tests():
    """Run the test suite"""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        GPIO.cleanup()
    except Exception as e:
        print(f"\nError during tests: {str(e)}")
        GPIO.cleanup() 