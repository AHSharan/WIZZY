import time
import threading
import logging
import random
from enum import Enum
from collections import deque

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
        self.move_history = deque(maxlen=10)  # Store last 10 moves for better pattern detection
        self.obstacle_history = deque(maxlen=5)  # Store recent obstacle positions
        self.last_clear_direction = None  # Store the last direction that was clear
        self.stuck_counter = 0  # Counter for when robot is stuck
        self.area_coverage = set()  # Track covered areas (simplified)
        
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
            
            # Update obstacle history
            self.obstacle_history.append(sensors)
            
            # Check if we're stuck in a loop
            if self._is_stuck():
                self._execute_escape_maneuver()
                continue
            
            if not sensors['center']:  # No obstacle ahead
                self._move_forward()
                self.consecutive_blocks = 0
                self.stuck_counter = 0
            else:
                self._handle_obstacle(sensors)
            
            time.sleep(0.1)  # Small delay to prevent CPU overuse

    def _is_stuck(self):
        """Check if the robot is stuck in a pattern or loop"""
        if len(self.move_history) < 5:
            return False
            
        # Check for repeated patterns
        recent_moves = list(self.move_history)
        if len(recent_moves) >= 4:
            # Check for alternating left-right pattern
            if all(move == Direction.LEFT for move in recent_moves[-4:]):
                return True
            if all(move == Direction.RIGHT for move in recent_moves[-4:]):
                return True
                
        # Check for too many consecutive blocks
        if self.consecutive_blocks > 5:
            return True
            
        # Check if we're making the same turn repeatedly
        if len(self.move_history) >= 3:
            last_three = list(self.move_history)[-3:]
            if all(move == self.last_turn for move in last_three):
                return True
                
        return False

    def _handle_obstacle(self, sensors):
        """Enhanced obstacle avoidance logic"""
        logger.info("Obstacle detected, executing avoidance maneuver")
        
        # First backup a bit
        self.motor_control.backward(duration=1.0)
        time.sleep(1.0)
        
        # Recheck sensors after backing up
        sensors = self.read_sensors()
        
        # Increment blocked counter
        self.consecutive_blocks += 1
        
        # If we're getting blocked too often, try more dramatic maneuvers
        if self.consecutive_blocks > 3:
            self._execute_escape_maneuver()
            return

        # Analyze the environment
        turn_direction = self._analyze_environment(sensors)
        
        # Execute the turn
        if turn_direction == Direction.LEFT:
            self.motor_control.turn_left(duration=1.5)
            self.last_turn = Direction.LEFT
        else:
            self.motor_control.turn_right(duration=1.5)
            self.last_turn = Direction.RIGHT
        
        time.sleep(1.5)  # Wait for turn to complete
        
        # Add move to history
        self.move_history.append(turn_direction)

    def _analyze_environment(self, sensors):
        """Enhanced environment analysis for better decision making"""
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
            
        # If both sides are clear, use pattern analysis and history
        return self._decide_best_turn()

    def _decide_best_turn(self):
        """Decide the best turn direction based on history and patterns"""
        if not self.move_history:
            return random.choice([Direction.LEFT, Direction.RIGHT])
            
        # Count recent turns
        recent_moves = list(self.move_history)
        left_turns = sum(1 for move in recent_moves if move == Direction.LEFT)
        right_turns = len(recent_moves) - left_turns
        
        # If we've been turning one way too much, go the other way
        if left_turns > right_turns + 2:
            return Direction.RIGHT
        elif right_turns > left_turns + 2:
            return Direction.LEFT
            
        # If we have a last clear direction, prefer that
        if self.last_clear_direction:
            return self.last_clear_direction
            
        # Otherwise, use randomness with slight bias against last turn
        if self.last_turn == Direction.LEFT:
            return random.choice([Direction.LEFT, Direction.RIGHT, Direction.RIGHT])
        return random.choice([Direction.LEFT, Direction.LEFT, Direction.RIGHT])

    def _execute_escape_maneuver(self):
        """Execute a more complex escape maneuver when stuck"""
        logger.info("Executing escape maneuver")
        
        # Back up more than usual
        self.motor_control.backward(duration=1.5)
        time.sleep(1.5)
        
        # Choose turn direction based on history
        if self._should_turn_left():
            self.motor_control.turn_left(duration=2.0)
            self.last_turn = Direction.LEFT
        else:
            self.motor_control.turn_right(duration=2.0)
            self.last_turn = Direction.RIGHT
            
        time.sleep(2.0)
        
        # Reset counters
        self.consecutive_blocks = 0
        self.stuck_counter = 0
        self.move_history.clear()  # Clear history to break patterns

    def _should_turn_left(self):
        """Determine if we should turn left based on history"""
        if not self.move_history:
            return random.random() < 0.5
            
        recent_moves = list(self.move_history)
        left_turns = sum(1 for move in recent_moves if move == Direction.LEFT)
        right_turns = len(recent_moves) - left_turns
        
        if left_turns > right_turns:
            return False
        elif right_turns > left_turns:
            return True
        return random.random() < 0.5

    def _move_forward(self):
        """Move forward with enhanced course corrections"""
        sensors = self.read_sensors()
        
        # If slightly off-center, make minor corrections
        if not sensors['center']:
            if sensors['left']:  # Too close to left wall
                self.motor_control.turn_right(duration=0.2)
                time.sleep(0.2)
            elif sensors['right']:  # Too close to right wall
                self.motor_control.turn_left(duration=0.2)
                time.sleep(0.2)
                
        # Move forward
        self.motor_control.forward(duration=3.0)
        time.sleep(0.2)  # Slightly shorter than movement to allow for overlap
        
        # Update last clear direction
        if not sensors['left']:
            self.last_clear_direction = Direction.LEFT
        elif not sensors['right']:
            self.last_clear_direction = Direction.RIGHT 