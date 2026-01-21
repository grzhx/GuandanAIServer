"""
AI module for Guandan game
Provides factory function to create AI instances based on configuration
"""

from config.ai_config import AIConfig


def create_ai(level: int = 2):
    """
    根据配置创建AI实例
    
    Args:
        level: 当前等级（2-A）
    
    Returns:
        AI实例（ImprovedGuandanAI 或 AdvancedGuandanAI）
    """
    algorithm = AIConfig.ALGORITHM
    
    if algorithm == "improved":
        from ai.strategy import ImprovedGuandanAI
        print(f"🎮 使用方案A：渐进式改进算法")
        return ImprovedGuandanAI(level)
    elif algorithm == "advanced":
        # 方案B暂时使用方案A的实现（可以后续扩展）
        from ai.strategy import ImprovedGuandanAI
        print(f"🚀 使用方案B：高级算法（当前使用改进版实现）")
        return ImprovedGuandanAI(level)
    else:
        raise ValueError(f"未知的算法类型: {algorithm}")


# 向后兼容：保留原有的GuandanAI类名
def GuandanAI(level: int = 2):
    """向后兼容的工厂函数"""
    return create_ai(level)


__all__ = ['create_ai', 'GuandanAI', 'AIConfig']
