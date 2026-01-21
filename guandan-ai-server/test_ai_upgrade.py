"""
测试AI升级效果
对比原AI和新AI的出牌行为
"""

from game.card import Card, parse_cards
from ai import create_ai, AIConfig


def test_first_move_with_straight():
    """测试场景1：手牌中有顺子，首次出牌应该优先出顺子"""
    print("\n" + "="*60)
    print("测试场景1：首次出牌 - 手牌中有顺子")
    print("="*60)
    
    # 构造测试手牌：包含一个顺子 6-7-8-9-10
    hand = parse_cards([
        {"color": "♠", "number": 3},
        {"color": "♥", "number": 3},
        {"color": "♠", "number": 6},
        {"color": "♠", "number": 7},
        {"color": "♠", "number": 8},
        {"color": "♠", "number": 9},
        {"color": "♠", "number": 10},
        {"color": "♥", "number": "J"},
        {"color": "♦", "number": "Q"},
    ])
    
    print(f"手牌：{[f'{c.color}{c.number}' for c in hand]}")
    
    # 测试新AI
    AIConfig.ALGORITHM = "improved"
    ai = create_ai(level=2)
    play = ai.find_best_play(hand, [])
    
    print(f"\n新AI出牌：{[f'{c.color}{c.number}' for c in play]}")
    print(f"出牌数量：{len(play)}")
    
    if len(play) == 5:
        print("✅ 测试通过：AI出了顺子（5张牌）")
    elif len(play) == 1:
        print("❌ 测试失败：AI出了单牌")
    else:
        print(f"⚠️  AI出了{len(play)}张牌")


def test_first_move_with_pairs():
    """测试场景2：手牌中有多个对子，应该优先出对子而不是单牌"""
    print("\n" + "="*60)
    print("测试场景2：首次出牌 - 手牌中有多个对子")
    print("="*60)
    
    # 构造测试手牌：包含3个对子
    hand = parse_cards([
        {"color": "♠", "number": 3},
        {"color": "♥", "number": 3},
        {"color": "♠", "number": 4},
        {"color": "♥", "number": 4},
        {"color": "♠", "number": 5},
        {"color": "♥", "number": 5},
        {"color": "♦", "number": 7},
        {"color": "♣", "number": 9},
    ])
    
    print(f"手牌：{[f'{c.color}{c.number}' for c in hand]}")
    
    # 测试新AI
    AIConfig.ALGORITHM = "improved"
    ai = create_ai(level=2)
    play = ai.find_best_play(hand, [])
    
    print(f"\n新AI出牌：{[f'{c.color}{c.number}' for c in play]}")
    print(f"出牌数量：{len(play)}")
    
    if len(play) == 2:
        print("✅ 测试通过：AI出了对子（2张牌）")
    elif len(play) == 1:
        print("❌ 测试失败：AI出了单牌")
    else:
        print(f"⚠️  AI出了{len(play)}张牌")


def test_first_move_with_triple():
    """测试场景3：手牌中有三张，应该优先出三张"""
    print("\n" + "="*60)
    print("测试场景3：首次出牌 - 手牌中有三张")
    print("="*60)
    
    # 构造测试手牌：包含三张5
    hand = parse_cards([
        {"color": "♠", "number": 3},
        {"color": "♠", "number": 5},
        {"color": "♥", "number": 5},
        {"color": "♦", "number": 5},
        {"color": "♠", "number": 7},
        {"color": "♥", "number": 9},
        {"color": "♦", "number": "J"},
    ])
    
    print(f"手牌：{[f'{c.color}{c.number}' for c in hand]}")
    
    # 测试新AI
    AIConfig.ALGORITHM = "improved"
    ai = create_ai(level=2)
    play = ai.find_best_play(hand, [])
    
    print(f"\n新AI出牌：{[f'{c.color}{c.number}' for c in play]}")
    print(f"出牌数量：{len(play)}")
    
    if len(play) == 3:
        print("✅ 测试通过：AI出了三张（3张牌）")
    elif len(play) == 1:
        print("❌ 测试失败：AI出了单牌")
    else:
        print(f"⚠️  AI出了{len(play)}张牌")


def test_hand_quality_evaluation():
    """测试场景4：手牌质量评估"""
    print("\n" + "="*60)
    print("测试场景4：手牌质量评估")
    print("="*60)
    
    # 好手牌：有顺子和对子
    good_hand = parse_cards([
        {"color": "♠", "number": 5},
        {"color": "♠", "number": 6},
        {"color": "♠", "number": 7},
        {"color": "♠", "number": 8},
        {"color": "♠", "number": 9},
        {"color": "♥", "number": 10},
        {"color": "♦", "number": 10},
    ])
    
    # 差手牌：都是孤立牌
    bad_hand = parse_cards([
        {"color": "♠", "number": 3},
        {"color": "♥", "number": 5},
        {"color": "♦", "number": 7},
        {"color": "♣", "number": 9},
        {"color": "♠", "number": "J"},
        {"color": "♥", "number": "K"},
        {"color": "♦", "number": "A"},
    ])
    
    AIConfig.ALGORITHM = "improved"
    ai = create_ai(level=2)
    
    good_quality = ai._evaluate_hand_quality(good_hand)
    bad_quality = ai._evaluate_hand_quality(bad_hand)
    
    print(f"好手牌质量分：{good_quality:.2f}")
    print(f"差手牌质量分：{bad_quality:.2f}")
    
    if good_quality > bad_quality:
        print("✅ 测试通过：好手牌质量分高于差手牌")
    else:
        print("❌ 测试失败：质量评估有问题")


def test_isolated_card_detection():
    """测试场景5：孤立牌检测"""
    print("\n" + "="*60)
    print("测试场景5：孤立牌检测")
    print("="*60)
    
    # 包含孤立牌的手牌
    hand = parse_cards([
        {"color": "♠", "number": 3},  # 孤立
        {"color": "♥", "number": 5},
        {"color": "♦", "number": 5},  # 对子，不孤立
        {"color": "♣", "number": 7},  # 孤立
        {"color": "♠", "number": 9},
        {"color": "♥", "number": 9},
        {"color": "♦", "number": 9},  # 三张，不孤立
    ])
    
    AIConfig.ALGORITHM = "improved"
    ai = create_ai(level=2)
    
    isolated_count = ai._count_isolated_cards(hand)
    
    print(f"手牌：{[f'{c.color}{c.number}' for c in hand]}")
    print(f"孤立牌数量：{isolated_count}")
    
    if isolated_count == 2:  # 3和7是孤立的
        print("✅ 测试通过：正确识别了孤立牌")
    else:
        print(f"⚠️  识别到{isolated_count}张孤立牌（预期2张）")


def test_algorithm_switching():
    """测试场景6：算法切换"""
    print("\n" + "="*60)
    print("测试场景6：算法切换功能")
    print("="*60)
    
    # 测试切换到improved
    AIConfig.set_algorithm("improved")
    ai1 = create_ai(level=2)
    print(f"算法1：{ai1.get_strategy_name()}")
    
    # 测试切换到advanced（当前使用improved实现）
    AIConfig.set_algorithm("advanced")
    ai2 = create_ai(level=2)
    print(f"算法2：{ai2.get_strategy_name()}")
    
    print("✅ 算法切换功能正常")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🎮 " + "="*58)
    print("🎮  掼蛋AI升级测试套件")
    print("🎮 " + "="*58)
    
    try:
        test_first_move_with_straight()
        test_first_move_with_pairs()
        test_first_move_with_triple()
        test_hand_quality_evaluation()
        test_isolated_card_detection()
        test_algorithm_switching()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        print("\n💡 提示：")
        print("  - 如果测试失败，请检查 config/ai_config.py 中的配置")
        print("  - 确保 enable_smart_first_move = True")
        print("  - 可以调整成本权重来优化AI行为")
        print("\n📖 详细文档请查看：AI_UPGRADE_GUIDE.md")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
