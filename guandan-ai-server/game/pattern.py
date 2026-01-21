"""
Pattern module for Guandan game
Handles pattern recognition and generation
"""

from typing import List, Optional, Tuple
from enum import Enum
from collections import Counter
from game.card import Card


class PatternType(Enum):
    """Card pattern types in Guandan"""
    PASS = "PASS"                      # 过牌
    SINGLE = "SINGLE"                  # 单牌
    PAIR = "PAIR"                      # 对子
    TRIPLE = "TRIPLE"                  # 三同张
    FULLHOUSE = "FULLHOUSE"            # 三带二
    STRAIGHT = "STRAIGHT"              # 顺子 (5+)
    PAIR_STRAIGHT = "PAIR_STRAIGHT"    # 三连对 (3+)
    TRIPLE_STRAIGHT = "TRIPLE_STRAIGHT"  # 钢板 (2+)
    BOMB = "BOMB"                      # 炸弹 (4+)
    STRAIGHT_FLUSH = "STRAIGHT_FLUSH"  # 同花顺
    KING_BOMB = "KING_BOMB"            # 天王炸


class Pattern:
    """Represents a card pattern"""
    
    def __init__(self, pattern_type: PatternType, cards: List[Card], 
                 main_value: int = 0, length: int = 0):
        self.pattern_type = pattern_type
        self.cards = cards
        self.main_value = main_value  # Main value for comparison
        self.length = length  # Length for straights, bombs, etc.
    
    def __repr__(self):
        return f"Pattern({self.pattern_type.value}, cards={len(self.cards)}, value={self.main_value})"


def identify_pattern(cards: List[Card], level: int) -> Optional[Pattern]:
    """
    Identify the pattern type of given cards
    
    Args:
        cards: List of cards to identify
        level: Current level card number
    
    Returns:
        Pattern object or None if invalid
    """
    if not cards:
        return Pattern(PatternType.PASS, [])
    
    n = len(cards)
    
    # Get card values for comparison
    values = [card.get_value(level) for card in cards]
    values.sort()
    
    # Count occurrences
    counter = Counter(values)
    counts = sorted(counter.values(), reverse=True)
    
    # KING_BOMB: 4 Jokers
    if n == 4 and all(card.is_joker() for card in cards):
        return Pattern(PatternType.KING_BOMB, cards, 1000, 4)
    
    # SINGLE
    if n == 1:
        return Pattern(PatternType.SINGLE, cards, values[0], 1)
    
    # PAIR
    if n == 2 and counts == [2]:
        return Pattern(PatternType.PAIR, cards, values[0], 1)
    
    # TRIPLE
    if n == 3 and counts == [3]:
        return Pattern(PatternType.TRIPLE, cards, values[0], 1)
    
    # BOMB: 4+ same cards
    if counts[0] >= 4 and len(counter) == 1:
        return Pattern(PatternType.BOMB, cards, values[0], n)
    
    # FULLHOUSE: 3+2
    if n == 5 and counts == [3, 2]:
        triple_value = [v for v, c in counter.items() if c == 3][0]
        return Pattern(PatternType.FULLHOUSE, cards, triple_value, 1)
    
    # Check for straights
    straight_result = check_straight(cards, level)
    if straight_result:
        return straight_result
    
    return None


def check_straight(cards: List[Card], level: int) -> Optional[Pattern]:
    """Check if cards form a straight pattern"""
    n = len(cards)
    
    # Get normalized values (for straight checking, A=14, level cards need special handling)
    normalized_values = []
    for card in cards:
        if card.is_joker():
            return None  # Jokers can't be in straights
        val = card.get_value(level)
        if val >= 50:  # Level card
            val = 14  # Treat as highest regular card for straight
        elif val == 14:  # A
            val = 14
        normalized_values.append(val)
    
    normalized_values.sort()
    counter = Counter(normalized_values)
    
    # STRAIGHT: 5+ consecutive singles
    if n >= 5 and all(c == 1 for c in counter.values()):
        if is_consecutive(list(counter.keys())):
            # Check if same suit (STRAIGHT_FLUSH)
            colors = [card.color for card in cards]
            if len(set(colors)) == 1 and colors[0] != "Joker":
                # Straight flush: value between 5-bomb and 6-bomb
                return Pattern(PatternType.STRAIGHT_FLUSH, cards, normalized_values[-1], n)
            return Pattern(PatternType.STRAIGHT, cards, normalized_values[-1], n)
    
    # PAIR_STRAIGHT: 3+ consecutive pairs
    if n >= 6 and n % 2 == 0 and all(c == 2 for c in counter.values()):
        if is_consecutive(list(counter.keys())):
            return Pattern(PatternType.PAIR_STRAIGHT, cards, normalized_values[-1], len(counter))
    
    # TRIPLE_STRAIGHT: 2+ consecutive triples
    if n >= 6 and n % 3 == 0 and all(c == 3 for c in counter.values()):
        if is_consecutive(list(counter.keys())):
            return Pattern(PatternType.TRIPLE_STRAIGHT, cards, normalized_values[-1], len(counter))
    
    return None


def is_consecutive(values: List[int]) -> bool:
    """Check if values are consecutive"""
    if len(values) <= 1:
        return False
    values = sorted(values)
    for i in range(1, len(values)):
        if values[i] != values[i-1] + 1:
            return False
    return True
