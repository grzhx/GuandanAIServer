"""
Card module for Guandan game
Handles card representation, comparison, and level card logic
"""

from typing import List, Optional
from enum import Enum


class CardColor(Enum):
    """Card color enumeration"""
    SPADE = "Spade"      # 黑桃 ♠
    CLUB = "Club"        # 梅花 ♣
    HEART = "Heart"      # 红桃 ♥
    DIAMOND = "Diamond"  # 方块 ♦
    JOKER = "Joker"      # 王


class Card:
    """
    Represents a single card in Guandan game
    
    Attributes:
        color: Card color (Spade, Club, Heart, Diamond, Joker)
        number: Card number (1=A, 2-10, 11=J, 12=Q, 13=K, 15=Black Joker, 16=Red Joker)
    """
    
    def __init__(self, color: str, number: int):
        self.color = color
        self.number = number
    
    def __repr__(self):
        return f"Card({self.color}, {self.number})"
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.color == other.color and self.number == other.number
    
    def __hash__(self):
        return hash((self.color, self.number))
    
    def to_dict(self):
        """Convert card to dictionary format"""
        return {"color": self.color, "number": self.number}
    
    @staticmethod
    def from_dict(data: dict) -> 'Card':
        """Create card from dictionary"""
        return Card(data["color"], data["number"])
    
    def get_value(self, level: int) -> int:
        """
        Get card value for comparison
        
        Args:
            level: Current level card number (2-13 or 1 for A)
        
        Returns:
            Card value for comparison (higher is stronger)
        """
        # Jokers are always highest
        if self.number == 16:  # Red Joker
            return 100
        if self.number == 15:  # Black Joker
            return 99
        
        # Level cards are second highest (after Jokers)
        if self.number == level:
            return 50
        
        # A (1) is higher than K (13)
        if self.number == 1:
            return 14
        
        # Regular cards
        return self.number
    
    def is_level_card(self, level: int) -> bool:
        """Check if this card is a level card"""
        return self.number == level and self.number not in [15, 16]
    
    def is_red_heart_level_card(self, level: int) -> bool:
        """Check if this card is a red heart level card (wildcard)"""
        return self.color == "Heart" and self.number == level and self.number not in [15, 16]
    
    def is_joker(self) -> bool:
        """Check if this card is a Joker"""
        return self.number in [15, 16]


def parse_cards(card_list: List[dict]) -> List[Card]:
    """Parse list of card dictionaries into Card objects"""
    return [Card.from_dict(card_data) for card_data in card_list]


def cards_to_dict_list(cards: List[Card]) -> List[dict]:
    """Convert list of Card objects to dictionary list"""
    return [card.to_dict() for card in cards]
