"""
AI Strategy module for Guandan game
Implements the algorithm to find the smallest card combination that beats the last play
"""

from typing import List, Optional
from collections import Counter
from itertools import combinations
from game.card import Card
from game.pattern import Pattern, PatternType, identify_pattern
from game.comparator import can_beat, is_bomb_type, get_bomb_rank


class GuandanAI:
    """AI player for Guandan game"""
    
    def __init__(self, level: int):
        self.level = level
    
    def find_best_play(self, hand: List[Card], last_move: List[Card]) -> List[Card]:
        """
        Find the best play to beat the last move
        
        Args:
            hand: Current hand cards
            last_move: Last played cards (empty if first move)
        
        Returns:
            List of cards to play (empty for PASS)
        """
        # If no last move, play the smallest single card
        if not last_move:
            return self._play_smallest_single(hand)
        
        # Identify the pattern to beat
        last_pattern = identify_pattern(last_move, self.level)
        if not last_pattern:
            return []  # Invalid last move, pass
        
        # Find all valid plays that can beat last_pattern
        valid_plays = self._find_all_beating_plays(hand, last_pattern)
        
        if not valid_plays:
            return []  # No valid play, pass
        
        # Return the smallest valid play
        return self._select_smallest_play(valid_plays)
    
    def _play_smallest_single(self, hand: List[Card]) -> List[Card]:
        """Play the smallest single card from hand"""
        if not hand:
            return []
        sorted_hand = sorted(hand, key=lambda c: c.get_value(self.level))
        return [sorted_hand[0]]
    
    def _find_all_beating_plays(self, hand: List[Card], 
                                last_pattern: Pattern) -> List[Pattern]:
        """Find all possible plays that can beat the last pattern"""
        valid_plays = []
        all_patterns = self._generate_all_patterns(hand, last_pattern)
        
        for pattern in all_patterns:
            if can_beat(pattern, last_pattern):
                valid_plays.append(pattern)
        
        return valid_plays
    
    def _generate_all_patterns(self, hand: List[Card], 
                               last_pattern: Pattern) -> List[Pattern]:
        """Generate all possible patterns from hand that match the type needed"""
        patterns = []
        
        if not is_bomb_type(last_pattern):
            patterns.extend(self._generate_same_type_patterns(hand, last_pattern))
            patterns.extend(self._generate_all_bombs(hand))
        else:
            patterns.extend(self._generate_all_bombs(hand))
        
        return patterns
    
    def _generate_same_type_patterns(self, hand: List[Card], 
                                     last_pattern: Pattern) -> List[Pattern]:
        """Generate patterns of the same type as last_pattern"""
        pattern_type = last_pattern.pattern_type
        
        if pattern_type == PatternType.SINGLE:
            return self._generate_singles(hand)
        elif pattern_type == PatternType.PAIR:
            return self._generate_pairs(hand)
        elif pattern_type == PatternType.TRIPLE:
            return self._generate_triples(hand)
        elif pattern_type == PatternType.FULLHOUSE:
            return self._generate_fullhouses(hand)
        elif pattern_type == PatternType.STRAIGHT:
            return self._generate_straights(hand, last_pattern.length)
        elif pattern_type == PatternType.PAIR_STRAIGHT:
            return self._generate_pair_straights(hand, last_pattern.length)
        elif pattern_type == PatternType.TRIPLE_STRAIGHT:
            return self._generate_triple_straights(hand, last_pattern.length)
        
        return []
    
    def _generate_singles(self, hand: List[Card]) -> List[Pattern]:
        """Generate all single card patterns"""
        return [Pattern(PatternType.SINGLE, [card], card.get_value(self.level), 1) 
                for card in hand]
    
    def _generate_pairs(self, hand: List[Card]) -> List[Pattern]:
        """Generate all pair patterns"""
        patterns = []
        value_groups = self._group_by_value(hand)
        
        for value, cards in value_groups.items():
            if len(cards) >= 2:
                for combo in combinations(cards, 2):
                    patterns.append(Pattern(PatternType.PAIR, list(combo), value, 1))
        
        return patterns
    
    def _generate_triples(self, hand: List[Card]) -> List[Pattern]:
        """Generate all triple patterns"""
        patterns = []
        value_groups = self._group_by_value(hand)
        
        for value, cards in value_groups.items():
            if len(cards) >= 3:
                for combo in combinations(cards, 3):
                    patterns.append(Pattern(PatternType.TRIPLE, list(combo), value, 1))
        
        return patterns
    
    def _generate_fullhouses(self, hand: List[Card]) -> List[Pattern]:
        """Generate all fullhouse (3+2) patterns"""
        patterns = []
        value_groups = self._group_by_value(hand)
        
        triples = []
        for value, cards in value_groups.items():
            if len(cards) >= 3:
                for combo in combinations(cards, 3):
                    triples.append((value, list(combo)))
        
        pairs = []
        for value, cards in value_groups.items():
            if len(cards) >= 2:
                for combo in combinations(cards, 2):
                    pairs.append((value, list(combo)))
        
        for t_value, triple in triples:
            for p_value, pair in pairs:
                if t_value != p_value:
                    if not any(c in triple for c in pair):
                        full = triple + pair
                        patterns.append(Pattern(PatternType.FULLHOUSE, full, t_value, 1))
        
        return patterns
    
    def _generate_straights(self, hand: List[Card], length: int) -> List[Pattern]:
        """Generate all straight patterns of given length"""
        patterns = []
        valid_cards = [c for c in hand if not c.is_joker()]
        
        value_cards = {}
        for card in valid_cards:
            val = card.get_value(self.level)
            if val >= 50:
                val = 14
            if val not in value_cards:
                value_cards[val] = []
            value_cards[val].append(card)
        
        sorted_values = sorted(value_cards.keys())
        
        for start_idx in range(len(sorted_values) - length + 1):
            values = sorted_values[start_idx:start_idx + length]
            if self._is_consecutive_list(values):
                for combo in self._generate_combo_from_values(values, value_cards, 1):
                    pattern = identify_pattern(combo, self.level)
                    if pattern and pattern.pattern_type in [PatternType.STRAIGHT, PatternType.STRAIGHT_FLUSH]:
                        patterns.append(pattern)
        
        return patterns
    
    def _generate_pair_straights(self, hand: List[Card], num_pairs: int) -> List[Pattern]:
        """Generate all pair straight patterns (连对)"""
        patterns = []
        valid_cards = [c for c in hand if not c.is_joker()]
        
        value_cards = {}
        for card in valid_cards:
            val = card.get_value(self.level)
            if val >= 50:
                val = 14
            if val not in value_cards:
                value_cards[val] = []
            value_cards[val].append(card)
        
        valid_values = [v for v, cards in value_cards.items() if len(cards) >= 2]
        valid_values.sort()
        
        for start_idx in range(len(valid_values) - num_pairs + 1):
            values = valid_values[start_idx:start_idx + num_pairs]
            if self._is_consecutive_list(values):
                for combo in self._generate_combo_from_values(values, value_cards, 2):
                    pattern = identify_pattern(combo, self.level)
                    if pattern and pattern.pattern_type == PatternType.PAIR_STRAIGHT:
                        patterns.append(pattern)
        
        return patterns
    
    def _generate_triple_straights(self, hand: List[Card], num_triples: int) -> List[Pattern]:
        """Generate all triple straight patterns (钢板)"""
        patterns = []
        valid_cards = [c for c in hand if not c.is_joker()]
        
        value_cards = {}
        for card in valid_cards:
            val = card.get_value(self.level)
            if val >= 50:
                val = 14
            if val not in value_cards:
                value_cards[val] = []
            value_cards[val].append(card)
        
        valid_values = [v for v, cards in value_cards.items() if len(cards) >= 3]
        valid_values.sort()
        
        for start_idx in range(len(valid_values) - num_triples + 1):
            values = valid_values[start_idx:start_idx + num_triples]
            if self._is_consecutive_list(values):
                for combo in self._generate_combo_from_values(values, value_cards, 3):
                    pattern = identify_pattern(combo, self.level)
                    if pattern and pattern.pattern_type == PatternType.TRIPLE_STRAIGHT:
                        patterns.append(pattern)
        
        return patterns
    
    def _generate_all_bombs(self, hand: List[Card]) -> List[Pattern]:
        """Generate all bomb patterns from hand"""
        patterns = []
        
        # Regular bombs (4+ same value)
        value_groups = self._group_by_value(hand)
        for value, cards in value_groups.items():
            if len(cards) >= 4:
                for size in range(4, len(cards) + 1):
                    for combo in combinations(cards, size):
                        patterns.append(Pattern(PatternType.BOMB, list(combo), value, size))
        
        # Straight flush
        patterns.extend(self._generate_straight_flushes(hand))
        
        # King bomb (4 jokers)
        jokers = [c for c in hand if c.is_joker()]
        if len(jokers) == 4:
            patterns.append(Pattern(PatternType.KING_BOMB, jokers, 1000, 4))
        
        return patterns
    
    def _generate_straight_flushes(self, hand: List[Card]) -> List[Pattern]:
        """Generate all straight flush patterns"""
        patterns = []
        
        suit_cards = {}
        for card in hand:
            if not card.is_joker():
                if card.color not in suit_cards:
                    suit_cards[card.color] = []
                suit_cards[card.color].append(card)
        
        for color, cards in suit_cards.items():
            if len(cards) >= 5:
                value_cards = {}
                for card in cards:
                    val = card.get_value(self.level)
                    if val >= 50:
                        val = 14
                    if val not in value_cards:
                        value_cards[val] = []
                    value_cards[val].append(card)
                
                sorted_values = sorted(value_cards.keys())
                
                for length in range(5, len(sorted_values) + 1):
                    for start_idx in range(len(sorted_values) - length + 1):
                        values = sorted_values[start_idx:start_idx + length]
                        if self._is_consecutive_list(values):
                            combo = [value_cards[v][0] for v in values]
                            pattern = identify_pattern(combo, self.level)
                            if pattern and pattern.pattern_type == PatternType.STRAIGHT_FLUSH:
                                patterns.append(pattern)
        
        return patterns
    
    def _group_by_value(self, hand: List[Card]) -> dict:
        """Group cards by their value"""
        groups = {}
        for card in hand:
            value = card.get_value(self.level)
            if value not in groups:
                groups[value] = []
            groups[value].append(card)
        return groups
    
    def _is_consecutive_list(self, values: List[int]) -> bool:
        """Check if a list of values is consecutive"""
        if len(values) < 2:
            return False
        for i in range(1, len(values)):
            if values[i] != values[i-1] + 1:
                return False
        return True
    
    def _generate_combo_from_values(self, values: List[int], value_cards: dict, 
                                    cards_per_value: int) -> List[List[Card]]:
        """Generate all combinations taking cards_per_value cards from each value"""
        if not values:
            return [[]]
        
        result = []
        first_value = values[0]
        remaining_values = values[1:]
        
        for combo in combinations(value_cards[first_value], cards_per_value):
            for rest in self._generate_combo_from_values(remaining_values, value_cards, cards_per_value):
                result.append(list(combo) + rest)
        
        return result
    
    def _select_smallest_play(self, valid_plays: List[Pattern]) -> List[Card]:
        """Select the smallest valid play (prefer non-bombs)"""
        if not valid_plays:
            return []
        
        non_bombs = [p for p in valid_plays if not is_bomb_type(p)]
        bombs = [p for p in valid_plays if is_bomb_type(p)]
        
        if non_bombs:
            non_bombs.sort(key=lambda p: p.main_value)
            return non_bombs[0].cards
        
        if bombs:
            bombs.sort(key=lambda p: get_bomb_rank(p))
            return bombs[0].cards
        
        return []
