"""
Comparator module for Guandan game
Handles pattern comparison logic
"""

from typing import List, Optional
from game.pattern import Pattern, PatternType


def get_bomb_rank(pattern: Pattern) -> int:
    """
    Get the rank of a bomb pattern for comparison
    
    Bomb ranking (from lowest to highest):
    - 4-card bomb
    - 5-card bomb  
    - Straight flush (between 5 and 6 card bomb)
    - 6-card bomb
    - 7-card bomb
    - 8-card bomb
    - King bomb (highest)
    
    Returns:
        Integer rank for comparison
    """
    if pattern.pattern_type == PatternType.KING_BOMB:
        return 10000  # Highest
    
    if pattern.pattern_type == PatternType.STRAIGHT_FLUSH:
        # Straight flush is between 5-card and 6-card bomb
        # Value is 5.5 * 100 + main_value
        return 550 + pattern.main_value
    
    if pattern.pattern_type == PatternType.BOMB:
        # Regular bomb: length * 100 + main_value
        return pattern.length * 100 + pattern.main_value
    
    return 0  # Not a bomb


def is_bomb_type(pattern: Pattern) -> bool:
    """Check if a pattern is a bomb type"""
    return pattern.pattern_type in [PatternType.BOMB, PatternType.STRAIGHT_FLUSH, PatternType.KING_BOMB]


def can_beat(pattern1: Pattern, pattern2: Pattern) -> bool:
    """
    Check if pattern1 can beat pattern2
    
    Args:
        pattern1: The pattern trying to beat
        pattern2: The pattern to beat
    
    Returns:
        True if pattern1 can beat pattern2
    """
    # PASS cannot beat anything
    if pattern1.pattern_type == PatternType.PASS:
        return False
    
    # If pattern2 is PASS, any card can beat it (first move)
    if pattern2.pattern_type == PatternType.PASS:
        return True
    
    # Check if either is a bomb
    is_bomb1 = is_bomb_type(pattern1)
    is_bomb2 = is_bomb_type(pattern2)
    
    # Bomb beats non-bomb
    if is_bomb1 and not is_bomb2:
        return True
    
    # Non-bomb cannot beat bomb
    if not is_bomb1 and is_bomb2:
        return False
    
    # Both are bombs - compare bomb ranks
    if is_bomb1 and is_bomb2:
        return get_bomb_rank(pattern1) > get_bomb_rank(pattern2)
    
    # Neither is a bomb - must be same type and same length
    if pattern1.pattern_type != pattern2.pattern_type:
        return False
    
    if pattern1.length != pattern2.length:
        return False
    
    # Same type and length - compare main values
    return pattern1.main_value > pattern2.main_value


def compare_patterns(pattern1: Pattern, pattern2: Pattern) -> int:
    """
    Compare two patterns
    
    Returns:
        1 if pattern1 > pattern2
        -1 if pattern1 < pattern2
        0 if equal or incomparable
    """
    if can_beat(pattern1, pattern2):
        return 1
    if can_beat(pattern2, pattern1):
        return -1
    return 0
