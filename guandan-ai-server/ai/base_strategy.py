"""
Base Strategy Class for Guandan AI
Defines the interface that all AI strategies must implement
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BaseStrategy(ABC):
    """AI策略基类 - 定义所有AI策略必须实现的接口"""
    
    def __init__(self):
        """初始化策略"""
        self.name = self.__class__.__name__
        self.stats = {
            "total_decisions": 0,
            "passes": 0,
            "plays": 0,
            "avg_decision_time": 0
        }
    
    @abstractmethod
    def decide_play(self, hand: List, last_play: Optional[List], game_state: Dict[str, Any]) -> Optional[List]:
        """
        决定出牌
        
        Args:
            hand: 当前手牌列表
            last_play: 上家出的牌（None表示首次出牌）
            game_state: 游戏状态信息（包括其他玩家信息、已出牌等）
        
        Returns:
            要出的牌列表，None表示过牌
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        获取策略名称
        
        Returns:
            策略的显示名称
        """
        pass
    
    def get_strategy_description(self) -> str:
        """
        获取策略描述
        
        Returns:
            策略的详细描述
        """
        return "Base strategy class"
    
    def update_stats(self, decision_type: str, decision_time: float):
        """
        更新统计信息
        
        Args:
            decision_type: 决策类型 ("play" 或 "pass")
            decision_time: 决策耗时（秒）
        """
        self.stats["total_decisions"] += 1
        if decision_type == "pass":
            self.stats["passes"] += 1
        else:
            self.stats["plays"] += 1
        
        # 更新平均决策时间
        total = self.stats["total_decisions"]
        avg = self.stats["avg_decision_time"]
        self.stats["avg_decision_time"] = (avg * (total - 1) + decision_time) / total
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            包含统计数据的字典
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "total_decisions": 0,
            "passes": 0,
            "plays": 0,
            "avg_decision_time": 0
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.get_strategy_name()} (Decisions: {self.stats['total_decisions']})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"{self.__class__.__name__}("
                f"name='{self.get_strategy_name()}', "
                f"decisions={self.stats['total_decisions']})")
