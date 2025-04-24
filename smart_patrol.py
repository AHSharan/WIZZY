import time
import threading
import logging
import random
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Direction(Enum):
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    STOP = "stop"

class SmartPatrol:
    def __init__(self, motor_control, read_sensors):
        self.motor_control = motor_control
        self.read_sensors = read_sensors
        self.is_patrolling = False
        self.patrol_thread = None
        self.last_turn = None
        self.consecutive_blocks = 0
        self.move_history = []  # Store last 5 moves for pattern detection
        
    def start_patrol(self):
        """Start the patrol thread if not already running"""
        if not self.is_patrolling:
            self.is_patrolling = True
            self.patrol_thread = threading.Thread(target=self._patrol_loop)
            self.patrol_thread.daemon = True
            self.patrol_thread.start()
            logger.info("Smart patrol started")
            return True
        return False

    def stop_patrol(self):
        """Stop the patrol thread"""
        self.is_patrolling = False
        if self.patrol_thread:
            self.patrol_thread.join(timeout=1.0)
        self.motor_control.stop()
        logger.info("Smart patrol stopped")

    def _patrol_loop(self):
        """Main patrol loop with intelligent navigation"""
        while self.is_patrolling:
            sensors = self.read_sensors()
            
            # Update move history
            if len(self.move_history) >= 5:
                self.move_history.pop(0)
            
            if not sensors['center']:  # No obstacle ahead
                self._move_forward()
                self.consecutive_blocks = 0
            else:
                self._handle_obstacle(sensors)
            
            time.sleep(0.1)  # Small delay to prevent CPU overuse

    def _handle_obstacle(self, sensors):
        """Complex obstacle avoidance logic"""
        logger.info("Obstacle detected, executing avoidance maneuver")
        
        # First backup a bit
        self.motor_control.backward(duration=0.5)
        time.sleep(0.5)
        
        # Recheck sensors after backing up
        sensors = self.read_sensors()
        
        # Increment blocked counter
        self.consecutive_blocks += 1
        
        # If we're getting blocked too often, try more dramatic maneuvers
        if self.consecutive_blocks > 3:
            self._execute_escape_maneuver()
            return

        # Decide turn direction based on sensor data and history
        turn_direction = self._decide_turn_direction(sensors)
        
        # Execute the turn
        if turn_direction == Direction.LEFT:
            self.motor_control.turn_left(duration=0.7)
            self.last_turn = Direction.LEFT
        else:
            self.motor_control.turn_right(duration=0.7)
            self.last_turn = Direction.RIGHT
        
        time.sleep(0.7)  # Wait for turn to complete
        
        # Add move to history
        self.move_history.append(turn_direction)

    def _decide_turn_direction(self, sensors):
        """Complex decision making for turn direction"""
        # If one side is clearly better, choose it
        if not sensors['left'] and sensors['right']:
            return Direction.LEFT
        if sensors['left'] and not sensors['right']:
            return Direction.RIGHT
            
        # If both sides are blocked, use history and randomness
        if sensors['left'] and sensors['right']:
            if self.last_turn and random.random() < 0.7:  # 70% chance to continue same direction
                return self.last_turn
            return random.choice([Direction.LEFT, Direction.RIGHT])
            
        # If both sides are clear, use pattern analysis
        return self._analyze_pattern()

    def _analyze_pattern(self):
        """Analyze movement history to detect and break patterns"""
        if len(self.move_history) >= 4:
            # Detect if we're turning the same direction too much
            left_turns = sum(1 for move in self.move_history if move == Direction.LEFT)
            right_turns = len(self.move_history) - left_turns
            
            if left_turns > right_turns + 2:  # If too many left turns
                return Direction.RIGHT
            elif right_turns > left_turns + 2:  # If too many right turns
                return Direction.LEFT
                
        # No clear pattern, use randomness with slight bias against last turn
        if self.last_turn == Direction.LEFT:
            return random.choice([Direction.LEFT, Direction.RIGHT, Direction.RIGHT])
        return random.choice([Direction.LEFT, Direction.LEFT, Direction.RIGHT])

    def _execute_escape_maneuver(self):
        """Execute a more complex escape maneuver when stuck"""
        logger.info("Executing escape maneuver")
        
        # Back up more than usual
        self.motor_control.backward(duration=1.0)
        time.sleep(1.0)
        
        # Do a bigger turn
        if random.random() < 0.5:
            self.motor_control.turn_left(duration=1.2)
            self.last_turn = Direction.LEFT
        else:
            self.motor_control.turn_right(duration=1.2)
            self.last_turn = Direction.RIGHT
            
        time.sleep(1.2)
        self.consecutive_blocks = 0  # Reset block counter

    def _move_forward(self):
        """Move forward with slight course corrections"""
        sensors = self.read_sensors()
        
        # If slightly off-center, make minor corrections
        if not sensors['center']:
            if sensors['left']:  # Too close to left wall
                self.motor_control.turn_right(duration=0.1)
                time.sleep(0.1)
            elif sensors['right']:  # Too close to right wall
                self.motor_control.turn_left(duration=0.1)
                time.sleep(0.1)
                
        self.motor_control.forward(duration=0.3)
        time.sleep(0.2)  # Slightly shorter than movement to allow for overlap 