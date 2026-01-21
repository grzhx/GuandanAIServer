"""
AI Configuration for Guandan Game
Supports switching between different AI algorithms
"""


class AIConfig:
    """AI配置类 - 支持算法切换"""
    
    # ==================== 算法选择 ====================
    # 可选值: "improved" (方案A-渐进式改进) 或 "advanced" (方案B-完全重构)
    ALGORITHM = "improved"
    
    # ==================== 方案A配置（渐进式改进）====================
    IMPROVED_CONFIG = {
        # 功能开关
        "enable_smart_first_move": True,      # 启用智能首次出牌
        "enable_hand_balance": True,          # 启用手牌平衡成本
        "enable_sequence_planning": False,    # 启用序列规划（可逐步启用）
        
        # 成本权重
        "cost_weights": {
            "base": 1.0,        # 基础成本权重
            "break": 2.0,       # 破坏牌型成本权重
            "balance": 1.5,     # 手牌平衡成本权重
            "stage": 1.0        # 阶段成本权重
        },
        
        # 首次出牌策略
        "first_move_priority": [
            "straight",          # 顺子
            "pair_straight",     # 连对
            "triple_straight",   # 钢板
            "fullhouse",         # 三带二
            "triple",            # 三张
            "pair",              # 对子（当对子>=3时）
            "single"             # 单牌（最后选择）
        ],
        
        # 手牌质量评估权重
        "quality_weights": {
            "completeness": 40,   # 牌型完整度
            "isolated_penalty": 5, # 孤立牌惩罚
            "bomb_bonus": 20,     # 炸弹奖励
            "steps_factor": 5     # 出牌步数因子
        },
        
        # 阈值设置
        "thresholds": {
            "min_pairs_to_play_pair": 3,  # 对子数量>=此值时优先出对子
            "pass_cost": 125,              # 过牌成本阈值
            "isolated_card_threshold": 2   # 孤立牌判定阈值
        }
    }
    
    # ==================== 方案B配置（完全重构）====================
    ADVANCED_CONFIG = {
        # 三层架构开关
        "enable_strategic_layer": True,   # 启用战略层
        "enable_tactical_layer": True,    # 启用战术层
        "enable_execution_layer": True,   # 启用执行层
        
        # 预测深度
        "lookahead_depth": 2,             # 出牌序列预测深度（步数）
        "max_branches": 10,               # 每步最大分支数（控制计算量）
        
        # 手牌质量评估权重
        "quality_weights": {
            "completeness": 0.4,   # 牌型完整度
            "distribution": 0.3,   # 牌型分布
            "steps": 0.2,          # 出牌步数
            "bombs": 0.1           # 炸弹价值
        },
        
        # 游戏阶段判定
        "stage_thresholds": {
            "early_cards": 15,     # 手牌>15张为开局
            "late_cards": 5        # 手牌<=5张为残局
        },
        
        # 策略选择
        "strategies": {
            "early": "control",    # 开局：控制节奏
            "mid": "optimize",     # 中局：优化手牌
            "late": "rush"         # 残局：快速出完
        },
        
        # 序列评估权重
        "sequence_weights": {
            "final_quality": 0.5,   # 最终手牌质量
            "step_efficiency": 0.3, # 步数效率
            "risk": 0.2            # 风险评估
        }
    }
    
    # ==================== 通用配置 ====================
    COMMON_CONFIG = {
        # 调试模式
        "debug_mode": False,
        
        # 日志级别
        "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
        
        # 性能配置
        "max_computation_time": 1000,  # 最大计算时间（毫秒）
        "enable_caching": True,        # 启用缓存
        
        # 牌型保护成本（两种方案共用）
        "pattern_costs": {
            "KING_BOMB": 10000,      # 天王炸
            "BOMB_6PLUS": 2000,      # 6+张炸弹
            "BOMB_5": 1500,          # 5张炸弹
            "BOMB_4": 1000,          # 4张炸弹
            "STRAIGHT_FLUSH": 800,   # 同花顺
            "TRIPLE_STRAIGHT": 300,  # 钢板
            "PAIR_STRAIGHT": 200,    # 连对
            "STRAIGHT": 150,         # 顺子
            "FULLHOUSE": 100,        # 三带二
            "TRIPLE": 50,            # 三张
            "PAIR": 10               # 对子
        }
    }
    
    @classmethod
    def get_config(cls):
        """获取当前算法的配置"""
        if cls.ALGORITHM == "improved":
            return cls.IMPROVED_CONFIG
        elif cls.ALGORITHM == "advanced":
            return cls.ADVANCED_CONFIG
        else:
            raise ValueError(f"未知的算法类型: {cls.ALGORITHM}")
    
    @classmethod
    def set_algorithm(cls, algorithm: str):
        """设置算法类型"""
        if algorithm not in ["improved", "advanced"]:
            raise ValueError(f"算法类型必须是 'improved' 或 'advanced'，当前值: {algorithm}")
        cls.ALGORITHM = algorithm
        print(f"✅ 已切换到算法: {algorithm}")
    
    @classmethod
    def get_pattern_cost(cls, pattern_type: str) -> int:
        """获取牌型保护成本"""
        return cls.COMMON_CONFIG["pattern_costs"].get(pattern_type, 0)
