"""
AI Strategy module for Guandan game
方案A：渐进式改进版本 - 在原有基础上添加智能首次出牌和手牌平衡成本
"""

from typing import List, Optional, Dict, Any
from collections import Counter
from itertools import combinations
from game.card import Card
from game.pattern import Pattern, PatternType, identify_pattern
from game.comparator import can_beat, is_bomb_type, get_bomb_rank
from ai.base_strategy import BaseStrategy
from config.ai_config import AIConfig


class ImprovedGuandanAI(BaseStrategy):
    """方案A：渐进式改进的AI策略"""
    
    def __init__(self, level: int = 2):
        super().__init__()
        self.level = level
        self.config = AIConfig.IMPROVED_CONFIG
        
        # 从配置加载成本
        self.PASS_COST = self.config["thresholds"]["pass_cost"]
        pattern_costs = AIConfig.COMMON_CONFIG["pattern_costs"]
        self.COST_KING_BOMB = pattern_costs["KING_BOMB"]
        self.COST_BOMB_6PLUS = pattern_costs["BOMB_6PLUS"]
        self.COST_BOMB_5 = pattern_costs["BOMB_5"]
        self.COST_BOMB_4 = pattern_costs["BOMB_4"]
        self.COST_STRAIGHT_FLUSH = pattern_costs["STRAIGHT_FLUSH"]
        self.COST_TRIPLE_STRAIGHT = pattern_costs["TRIPLE_STRAIGHT"]
        self.COST_PAIR_STRAIGHT = pattern_costs["PAIR_STRAIGHT"]
        self.COST_STRAIGHT = pattern_costs["STRAIGHT"]
        self.COST_FULLHOUSE = pattern_costs["FULLHOUSE"]
        self.COST_TRIPLE = pattern_costs["TRIPLE"]
        self.COST_PAIR = pattern_costs["PAIR"]
    
    def get_strategy_name(self) -> str:
        """获取策略名称"""
        return "改进版AI (方案A)"
    
    def get_strategy_description(self) -> str:
        """获取策略描述"""
        return "渐进式改进：智能首次出牌 + 手牌平衡成本 + 优化的牌型选择"
    
    def decide_play(self, hand: List[Card], last_play: Optional[List[Card]], 
                   game_state: Dict[str, Any]) -> Optional[List[Card]]:
        """决定出牌 - 实现BaseStrategy接口"""
        if not last_play:
            return self.find_best_play(hand, [])
        return self.find_best_play(hand, last_play)
    
    def find_best_play(self, hand: List[Card], last_move: List[Card]) -> List[Card]:
        """
        Find the best play to beat the last move
        
        Args:
            hand: Current hand cards
            last_move: Last played cards (empty if first move)
        
        Returns:
            List of cards to play (empty for PASS)
        """
        # If no last move, use smart first move strategy
        if not last_move:
            if self.config["enable_smart_first_move"]:
                return self._play_smart_first_move(hand)
            else:
                return self._play_smallest_single(hand)
        
        # Identify the pattern to beat
        last_pattern = identify_pattern(last_move, self.level)
        if not last_pattern:
            return []  # Invalid last move, pass
        
        # Find all valid plays that can beat last_pattern
        valid_plays = self._find_all_beating_plays(hand, last_pattern)
        
        if not valid_plays:
            return []  # No valid play, pass
        
        # Return the best play considering cost
        return self._select_smallest_play(valid_plays, hand)
    
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
    
    def _analyze_hand_patterns(self, hand: List[Card]) -> List[tuple]:
        """
        Analyze hand to find all complete patterns
        Returns list of (pattern_type, cards, cost) tuples
        """
        patterns = []
        value_groups = self._group_by_value(hand)
        
        # Find bombs (4+ same cards)
        for value, cards in value_groups.items():
            if len(cards) >= 4:
                if len(cards) >= 6:
                    patterns.append(('BOMB_6PLUS', cards, self.COST_BOMB_6PLUS))
                elif len(cards) == 5:
                    patterns.append(('BOMB_5', cards, self.COST_BOMB_5))
                else:  # len(cards) == 4
                    patterns.append(('BOMB_4', cards, self.COST_BOMB_4))
        
        # Find king bomb (4 jokers)
        jokers = [c for c in hand if c.is_joker()]
        if len(jokers) == 4:
            patterns.append(('KING_BOMB', jokers, self.COST_KING_BOMB))
        
        # Find straight flushes
        straight_flushes = self._find_straight_flushes_cards(hand)
        for sf_cards in straight_flushes:
            patterns.append(('STRAIGHT_FLUSH', sf_cards, self.COST_STRAIGHT_FLUSH))
        
        # Find triple straights (钢板)
        triple_straights = self._find_triple_straights_cards(hand)
        for ts_cards in triple_straights:
            patterns.append(('TRIPLE_STRAIGHT', ts_cards, self.COST_TRIPLE_STRAIGHT))
        
        # Find pair straights (连对)
        pair_straights = self._find_pair_straights_cards(hand)
        for ps_cards in pair_straights:
            patterns.append(('PAIR_STRAIGHT', ps_cards, self.COST_PAIR_STRAIGHT))
        
        # Find straights
        straights = self._find_straights_cards(hand)
        for s_cards in straights:
            patterns.append(('STRAIGHT', s_cards, self.COST_STRAIGHT))
        
        # Find fullhouses (三带二)
        fullhouses = self._find_fullhouses_cards(hand)
        for fh_cards in fullhouses:
            patterns.append(('FULLHOUSE', fh_cards, self.COST_FULLHOUSE))
        
        # Find triples
        for value, cards in value_groups.items():
            if len(cards) >= 3 and len(cards) < 4:  # Not a bomb
                patterns.append(('TRIPLE', cards[:3], self.COST_TRIPLE))
        
        # Find pairs
        for value, cards in value_groups.items():
            if len(cards) >= 2 and len(cards) < 4:  # Not a bomb
                patterns.append(('PAIR', cards[:2], self.COST_PAIR))
        
        return patterns
    
    def _find_straight_flushes_cards(self, hand: List[Card]) -> List[List[Card]]:
        """Find all straight flush card combinations in hand"""
        results = []
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
                            results.append(combo)
        return results
    
    def _find_triple_straights_cards(self, hand: List[Card]) -> List[List[Card]]:
        """Find all triple straight (钢板) card combinations in hand"""
        results = []
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
        
        for num_triples in range(2, len(valid_values) + 1):
            for start_idx in range(len(valid_values) - num_triples + 1):
                values = valid_values[start_idx:start_idx + num_triples]
                if self._is_consecutive_list(values):
                    combo = []
                    for v in values:
                        combo.extend(value_cards[v][:3])
                    results.append(combo)
        return results
    
    def _find_pair_straights_cards(self, hand: List[Card]) -> List[List[Card]]:
        """Find all pair straight (连对) card combinations in hand"""
        results = []
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
        
        for num_pairs in range(3, len(valid_values) + 1):
            for start_idx in range(len(valid_values) - num_pairs + 1):
                values = valid_values[start_idx:start_idx + num_pairs]
                if self._is_consecutive_list(values):
                    combo = []
                    for v in values:
                        combo.extend(value_cards[v][:2])
                    results.append(combo)
        return results
    
    def _find_straights_cards(self, hand: List[Card]) -> List[List[Card]]:
        """Find all straight card combinations in hand"""
        results = []
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
        for length in range(5, len(sorted_values) + 1):
            for start_idx in range(len(sorted_values) - length + 1):
                values = sorted_values[start_idx:start_idx + length]
                if self._is_consecutive_list(values):
                    combo = [value_cards[v][0] for v in values]
                    results.append(combo)
        return results
    
    def _find_fullhouses_cards(self, hand: List[Card]) -> List[List[Card]]:
        """Find all fullhouse (三带二) card combinations in hand"""
        results = []
        value_groups = self._group_by_value(hand)
        
        # Find triples and pairs
        triples = []
        pairs = []
        for value, cards in value_groups.items():
            if len(cards) >= 3:
                triples.append((value, cards[:3]))
            if len(cards) >= 2 and len(cards) < 4:  # Don't use bombs as pairs
                pairs.append((value, cards[:2]))
        
        # Combine each triple with each pair (different values)
        for t_value, triple in triples:
            for p_value, pair in pairs:
                if t_value != p_value:
                    results.append(triple + pair)
        
        return results
    
    def _calculate_play_cost(self, play: Pattern, hand: List[Card]) -> int:
        """
        Calculate the cost of making a play
        Cost is based on whether the play breaks existing valuable patterns
        """
        # If play uses complete pattern (like using a bomb to beat another bomb), cost is 0
        if is_bomb_type(play):
            return 0  # Using a bomb as intended, no breakage cost
        
        # Analyze existing patterns in hand
        existing_patterns = self._analyze_hand_patterns(hand)
        
        # Check which patterns would be broken by this play
        play_cards_set = set(play.cards)
        total_cost = 0
        
        for pattern_type, pattern_cards, cost in existing_patterns:
            pattern_cards_set = set(pattern_cards)
            
            # Check if this play would break this pattern
            # A pattern is broken if some but not all of its cards are used
            overlap = play_cards_set & pattern_cards_set
            if overlap and overlap != pattern_cards_set:
                # This play breaks an existing pattern
                total_cost = max(total_cost, cost)
        
        return total_cost
    
    def _get_pattern_priority(self, pattern: Pattern, hand: List[Card]) -> int:
        """
        Get the priority of a pattern type (lower number = higher priority)
        Priority: STRAIGHT > TRIPLE_STRAIGHT > PAIR_STRAIGHT > FULLHOUSE > TRIPLE > PAIR/SINGLE
        For PAIR vs SINGLE: the one with more count in hand has lower priority (prefer to play it)
        """
        pattern_type = pattern.pattern_type
        
        # Base priorities (lower = prefer to play)
        priorities = {
            PatternType.STRAIGHT: 1,
            PatternType.TRIPLE_STRAIGHT: 2,
            PatternType.PAIR_STRAIGHT: 3,
            PatternType.FULLHOUSE: 4,
            PatternType.TRIPLE: 5,
            PatternType.PAIR: 6,
            PatternType.SINGLE: 6,
        }
        
        base_priority = priorities.get(pattern_type, 10)
        
        # For PAIR vs SINGLE, dynamically adjust based on count
        if pattern_type in [PatternType.PAIR, PatternType.SINGLE]:
            pair_count = self._count_pairs_in_hand(hand)
            single_count = self._count_singles_in_hand(hand)
            
            if pattern_type == PatternType.PAIR:
                # If more pairs than singles, prefer to play pairs (lower priority number)
                if pair_count >= single_count:
                    return 6  # Prefer pairs
                else:
                    return 7  # Prefer singles
            else:  # SINGLE
                # If more singles than pairs, prefer to play singles
                if single_count >= pair_count:
                    return 6  # Prefer singles
                else:
                    return 7  # Prefer pairs
        
        return base_priority
    
    def _count_pairs_in_hand(self, hand: List[Card]) -> int:
        """Count the number of pairs in hand (cards with exactly 2 of same value)"""
        value_groups = self._group_by_value(hand)
        count = 0
        for value, cards in value_groups.items():
            if len(cards) >= 2:
                count += len(cards) // 2
        return count
    
    def _count_singles_in_hand(self, hand: List[Card]) -> int:
        """Count the number of single cards in hand (cards with only 1 of same value)"""
        value_groups = self._group_by_value(hand)
        count = 0
        for value, cards in value_groups.items():
            if len(cards) == 1:
                count += 1
            elif len(cards) >= 2:
                count += len(cards) % 2  # Remaining singles after pairing
        return count
    
    def _select_smallest_play(self, valid_plays: List[Pattern], hand: List[Card]) -> List[Card]:
        """
        Select the best play considering cost, pattern priority, and value
        Will pass if the cost of playing is too high
        
        Priority order (when cost is same):
        1. Pattern type: STRAIGHT > TRIPLE_STRAIGHT > PAIR_STRAIGHT > FULLHOUSE > TRIPLE > PAIR/SINGLE
        2. For PAIR vs SINGLE: prefer the one with more count in hand
        3. Main value (lower is better)
        """
        if not valid_plays:
            return []
        
        # Calculate cost and priority for each valid play
        plays_with_info = []
        for play in valid_plays:
            cost = self._calculate_play_cost(play, hand)
            priority = self._get_pattern_priority(play, hand)
            plays_with_info.append((play, cost, priority))
        
        # Separate bombs and non-bombs
        non_bombs = [(p, c, pr) for p, c, pr in plays_with_info if not is_bomb_type(p)]
        bombs = [(p, c, pr) for p, c, pr in plays_with_info if is_bomb_type(p)]
        
        best_play = None
        best_cost = float('inf')
        
        if non_bombs:
            # Sort non-bombs by: cost, then priority, then main_value
            non_bombs.sort(key=lambda x: (x[1], x[2], x[0].main_value))
            best_play, best_cost, _ = non_bombs[0]
        
        if bombs:
            # Sort bombs by: cost, then bomb rank
            bombs.sort(key=lambda x: (x[1], get_bomb_rank(x[0])))
            if not best_play or bombs[0][1] < best_cost:
                best_play, best_cost, _ = bombs[0]
        
        # If the best play's cost exceeds PASS_COST, choose to pass
        if best_cost > self.PASS_COST:
            return []  # Pass
        
        return best_play.cards if best_play else []
    
    # ==================== 方案A新增功能：智能首次出牌 ====================
    
    def _play_smart_first_move(self, hand: List[Card]) -> List[Card]:
        """
        智能首次出牌策略 - 优先出完整牌型而不是单牌
        
        优先级顺序（从配置读取）：
        1. 顺子 (STRAIGHT)
        2. 连对 (PAIR_STRAIGHT)
        3. 钢板 (TRIPLE_STRAIGHT)
        4. 三带二 (FULLHOUSE)
        5. 三张 (TRIPLE)
        6. 对子 (PAIR) - 当对子数量>=阈值时
        7. 单牌 (SINGLE) - 最后选择，且优先出孤立的小牌
        """
        priority_order = self.config["first_move_priority"]
        
        for pattern_type in priority_order:
            if pattern_type == "straight":
                result = self._try_play_straight(hand)
                if result:
                    return result
            
            elif pattern_type == "pair_straight":
                result = self._try_play_pair_straight(hand)
                if result:
                    return result
            
            elif pattern_type == "triple_straight":
                result = self._try_play_triple_straight(hand)
                if result:
                    return result
            
            elif pattern_type == "fullhouse":
                result = self._try_play_fullhouse(hand)
                if result:
                    return result
            
            elif pattern_type == "triple":
                result = self._try_play_triple(hand)
                if result:
                    return result
            
            elif pattern_type == "pair":
                # 只有当对子数量足够多时才优先出对子
                pair_count = self._count_pairs_in_hand(hand)
                threshold = self.config["thresholds"]["min_pairs_to_play_pair"]
                if pair_count >= threshold:
                    result = self._try_play_pair(hand)
                    if result:
                        return result
            
            elif pattern_type == "single":
                # 最后才出单牌，且优先出孤立的小牌
                return self._play_smallest_isolated_single(hand)
        
        # 降级处理：如果所有策略都失败，出最小单牌
        return self._play_smallest_single(hand)
    
    def _try_play_straight(self, hand: List[Card]) -> Optional[List[Card]]:
        """尝试出顺子（最小的）"""
        straights = self._find_straights_cards(hand)
        if straights:
            # 选择最小的顺子
            best_straight = min(straights, key=lambda s: self._calculate_cards_total_value(s))
            return best_straight
        return None
    
    def _try_play_pair_straight(self, hand: List[Card]) -> Optional[List[Card]]:
        """尝试出连对（最小的）"""
        pair_straights = self._find_pair_straights_cards(hand)
        if pair_straights:
            # 选择最小的连对
            best_ps = min(pair_straights, key=lambda ps: self._calculate_cards_total_value(ps))
            return best_ps
        return None
    
    def _try_play_triple_straight(self, hand: List[Card]) -> Optional[List[Card]]:
        """尝试出钢板（最小的）"""
        triple_straights = self._find_triple_straights_cards(hand)
        if triple_straights:
            # 选择最小的钢板
            best_ts = min(triple_straights, key=lambda ts: self._calculate_cards_total_value(ts))
            return best_ts
        return None
    
    def _try_play_fullhouse(self, hand: List[Card]) -> Optional[List[Card]]:
        """尝试出三带二（最小的）"""
        fullhouses = self._find_fullhouses_cards(hand)
        if fullhouses:
            # 选择最小的三带二
            best_fh = min(fullhouses, key=lambda fh: self._calculate_cards_total_value(fh))
            return best_fh
        return None
    
    def _try_play_triple(self, hand: List[Card]) -> Optional[List[Card]]:
        """尝试出三张（最小的）"""
        value_groups = self._group_by_value(hand)
        triples = []
        for value, cards in value_groups.items():
            if len(cards) >= 3 and len(cards) < 4:  # 不是炸弹
                triples.append((value, cards[:3]))
        
        if triples:
            # 选择最小的三张
            triples.sort(key=lambda t: t[0])
            return triples[0][1]
        return None
    
    def _try_play_pair(self, hand: List[Card]) -> Optional[List[Card]]:
        """尝试出对子（最小的）"""
        value_groups = self._group_by_value(hand)
        pairs = []
        for value, cards in value_groups.items():
            if len(cards) >= 2 and len(cards) < 4:  # 不是炸弹
                pairs.append((value, cards[:2]))
        
        if pairs:
            # 选择最小的对子
            pairs.sort(key=lambda p: p[0])
            return pairs[0][1]
        return None
    
    def _play_smallest_isolated_single(self, hand: List[Card]) -> List[Card]:
        """
        出最小的孤立单牌
        孤立牌定义：该点数的牌数量<=阈值（默认2）
        """
        value_groups = self._group_by_value(hand)
        threshold = self.config["thresholds"]["isolated_card_threshold"]
        
        # 找出所有孤立牌
        isolated_cards = []
        for value, cards in value_groups.items():
            if len(cards) <= threshold:
                isolated_cards.extend(cards)
        
        if isolated_cards:
            # 返回最小的孤立牌
            sorted_isolated = sorted(isolated_cards, key=lambda c: c.get_value(self.level))
            return [sorted_isolated[0]]
        
        # 如果没有孤立牌，返回最小的单牌
        return self._play_smallest_single(hand)
    
    def _calculate_cards_total_value(self, cards: List[Card]) -> int:
        """计算一组牌的总价值（用于比较大小）"""
        return sum(c.get_value(self.level) for c in cards)
    
    # ==================== 方案A新增功能：手牌质量评估 ====================
    
    def _evaluate_hand_quality(self, hand: List[Card]) -> float:
        """
        评估手牌质量（0-100分）
        
        评分维度：
        1. 牌型完整度（40分）- 完整牌型越多越好
        2. 孤立牌惩罚（-30分）- 孤立牌越多扣分越多
        3. 炸弹奖励（20分）- 炸弹越多加分越多
        4. 出牌步数（40分）- 预计步数越少分数越高
        """
        if not hand:
            return 100.0  # 没牌了，完美！
        
        weights = self.config["quality_weights"]
        score = 0.0
        
        # 1. 牌型完整度（40分）
        patterns = self._analyze_hand_patterns(hand)
        complete_patterns = [p for p in patterns if p[0] not in ['PAIR', 'TRIPLE']]
        completeness = len(complete_patterns) / max(1, len(hand) / 5)
        score += min(weights["completeness"], completeness * weights["completeness"])
        
        # 2. 孤立牌惩罚
        isolated_count = self._count_isolated_cards(hand)
        score -= isolated_count * weights["isolated_penalty"]
        
        # 3. 炸弹奖励
        bombs = [p for p in patterns if 'BOMB' in p[0]]
        score += len(bombs) * weights["bomb_bonus"]
        
        # 4. 出牌步数评估
        estimated_steps = self._estimate_steps_to_finish(hand)
        steps_score = max(0, weights["completeness"] - estimated_steps * weights["steps_factor"])
        score += steps_score
        
        return max(0.0, min(100.0, score))
    
    def _count_isolated_cards(self, hand: List[Card]) -> int:
        """计算孤立牌数量（无法组成牌型的牌）"""
        value_groups = self._group_by_value(hand)
        threshold = self.config["thresholds"]["isolated_card_threshold"]
        
        isolated_count = 0
        for value, cards in value_groups.items():
            if len(cards) <= threshold:
                isolated_count += len(cards)
        
        return isolated_count
    
    def _estimate_steps_to_finish(self, hand: List[Card]) -> int:
        """
        估算出完手牌需要的步数
        简化算法：完整牌型算1步，剩余牌按平均3张/步计算
        """
        patterns = self._analyze_hand_patterns(hand)
        
        # 统计完整牌型覆盖的牌数
        covered_cards = set()
        for pattern_type, cards, cost in patterns:
            if pattern_type not in ['PAIR', 'TRIPLE']:  # 只计算大牌型
                covered_cards.update(cards)
        
        complete_pattern_steps = len([p for p in patterns if p[0] not in ['PAIR', 'TRIPLE']])
        remaining_cards = len(hand) - len(covered_cards)
        remaining_steps = (remaining_cards + 2) // 3  # 向上取整
        
        return complete_pattern_steps + remaining_steps
    
    # ==================== 方案A新增功能：改进的成本计算 ====================
    
    def _calculate_play_cost_improved(self, play: Pattern, hand: List[Card]) -> float:
        """
        改进的成本计算 - 考虑手牌平衡
        
        总成本 = 基础成本 + 破坏成本 + 手牌平衡成本 + 阶段成本
        """
        if not self.config["enable_hand_balance"]:
            # 如果未启用手牌平衡，使用原始成本计算
            return self._calculate_play_cost(play, hand)
        
        weights = self.config["cost_weights"]
        
        # 1. 基础成本
        base_cost = self._get_base_cost(play)
        
        # 2. 破坏成本（原有逻辑）
        break_cost = self._calculate_play_cost(play, hand)
        
        # 3. 手牌平衡成本（新增）
        balance_cost = self._calculate_balance_cost(play, hand)
        
        # 4. 阶段成本（新增）
        stage_cost = self._calculate_stage_cost(play, hand)
        
        total_cost = (
            base_cost * weights["base"] +
            break_cost * weights["break"] +
            balance_cost * weights["balance"] +
            stage_cost * weights["stage"]
        )
        
        return total_cost
    
    def _get_base_cost(self, play: Pattern) -> float:
        """获取牌型的基础成本"""
        if is_bomb_type(play):
            return 0.0  # 炸弹作为正常出牌，成本为0
        
        # 根据牌型大小设置基础成本
        pattern_type = play.pattern_type
        if pattern_type == PatternType.SINGLE:
            return 5.0  # 单牌有一定成本，避免过度出单牌
        elif pattern_type == PatternType.PAIR:
            return 3.0
        elif pattern_type == PatternType.TRIPLE:
            return 2.0
        else:
            return 1.0  # 大牌型成本低，鼓励出大牌型
    
    def _calculate_balance_cost(self, play: Pattern, hand: List[Card]) -> float:
        """
        计算手牌平衡成本
        评估出牌后手牌质量的变化
        """
        # 计算出牌前的手牌质量
        before_quality = self._evaluate_hand_quality(hand)
        
        # 模拟出牌后的手牌
        remaining = hand.copy()
        for card in play.cards:
            if card in remaining:
                remaining.remove(card)
        
        # 计算出牌后的手牌质量
        after_quality = self._evaluate_hand_quality(remaining)
        
        # 质量下降越多，成本越高
        quality_loss = max(0, before_quality - after_quality)
        
        return quality_loss * 2  # 放大系数
    
    def _calculate_stage_cost(self, play: Pattern, hand: List[Card]) -> float:
        """
        计算阶段成本
        根据游戏阶段（手牌数量）动态调整成本
        """
        hand_size = len(hand)
        
        # 开局阶段（手牌多）：鼓励出大牌型
        if hand_size > 15:
            if play.pattern_type in [PatternType.STRAIGHT, PatternType.PAIR_STRAIGHT, 
                                     PatternType.TRIPLE_STRAIGHT]:
                return -5.0  # 负成本=奖励
            elif play.pattern_type == PatternType.SINGLE:
                return 10.0  # 惩罚出单牌
        
        # 中局阶段（手牌中等）：平衡策略
        elif hand_size > 8:
            if play.pattern_type == PatternType.SINGLE:
                return 5.0
        
        # 残局阶段（手牌少）：快速出完
        else:
            return 0.0  # 残局不考虑阶段成本
        
        return 0.0
