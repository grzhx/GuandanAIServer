# 掼蛋AI服务器 (Guandan AI Server)

一个基于WebSocket的掼蛋游戏AI服务器，能够自动分析手牌并选择最优出牌策略。

## 功能特性

- **HTTP/WebSocket接口**: 提供标准的WebSocket通信接口
- **智能出牌算法**: 自动选择能够压过上家牌的最小牌型组合
- **完整牌型支持**: 支持掼蛋所有标准牌型
- **级牌规则**: 正确处理级牌的特殊大小规则

## 支持的牌型

| 牌型类型 | 说明 | 示例 |
|---------|------|------|
| SINGLE | 单牌 | 一张牌 |
| PAIR | 对子 | 两张相同点数 |
| TRIPLE | 三同张 | 三张相同点数 |
| FULLHOUSE | 三带二 | 三张+一对 |
| STRAIGHT | 顺子 | 5张及以上连续 |
| PAIR_STRAIGHT | 三连对 | 3组及以上连续对子 |
| TRIPLE_STRAIGHT | 钢板 | 2组及以上连续三同张 |
| BOMB | 炸弹 | 4张及以上相同点数 |
| STRAIGHT_FLUSH | 同花顺 | 同花色顺子(大小介于5炸和6炸之间) |
| KING_BOMB | 天王炸 | 4张王 |

## 安装

```bash
# 创建虚拟环境 (可选)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

## 运行服务器

```bash
python main.py
```

服务器将在 `http://localhost:8000` 启动。

## API文档

### 健康检查

- **GET** `/` 或 `/health` - 检查服务器状态

### WebSocket接口

- **WebSocket** `/ws` - AI游戏交互接口

#### 请求消息格式

```json
{
  "msg": "ai_call",
  "request_id": "unique-request-id-123",
  "level": 2,
  "last_move": [
    {"color": "Spade", "number": 5},
    {"color": "Heart", "number": 5}
  ],
  "your_cards": [
    {"color": "Spade", "number": 2},
    {"color": "Heart", "number": 2},
    {"color": "Club", "number": 7},
    {"color": "Diamond", "number": 8}
  ]
}
```

**字段说明:**
- `msg`: 固定为 "ai_call"
- `level`: 当前级牌点数 (1=A, 2-10, 11=J, 12=Q, 13=K)
- `last_move`: 上一次出牌 (空数组表示主动出牌)
- `your_cards`: 当前手牌

#### 响应消息格式

**出牌响应:**
```json
{
  "action": "play_cards",
  "request_id": "unique-request-id-123",
  "cards": [
    {"color": "Club", "number": 7},
    {"color": "Diamond", "number": 7}
  ]
}
```

**过牌响应（空列表代表过牌）:**
```json
{
  "action": "play_cards",
  "request_id": "unique-request-id-123",
  "cards": []
}
```

**注意:** 如果请求中包含 `request_id` 字段，响应中会原样返回该字段。

## 卡牌编号对照表

| number | 牌面 | 说明 |
|--------|------|------|
| 1 | A | Ace（大小大于K） |
| 2-10 | 2-10 | 数字牌（2最小） |
| 11 | J | Jack |
| 12 | Q | Queen |
| 13 | K | King |
| 15 | 黑王 | Black Joker |
| 16 | 红王 | Red Joker |

## 花色对照表

| color | 花色 |
|-------|------|
| Spade | 黑桃 ♠ |
| Club | 梅花 ♣ |
| Heart | 红桃 ♥ |
| Diamond | 方块 ♦ |
| Joker | 王 |

## 级牌规则

- 点数为级牌点数的牌视为最大的数字牌（除王外最大的牌）
- 红桃级牌可视为任意数字任意花色的牌（除王牌）- *此功能待实现*

## AI策略说明

当前实现的AI策略是**最小出牌策略**：
1. 如果是主动出牌，出最小的单牌
2. 如果需要跟牌，找出所有能压过上家的牌型
3. 优先选择非炸弹牌型中最小的
4. 如果没有同类型牌型可压，考虑使用炸弹
5. 如果无法压过，则过牌

## 项目结构

```
GuandanAIServer/
├── main.py                 # 服务器入口，HTTP/WebSocket服务
├── game/
│   ├── __init__.py
│   ├── card.py            # 卡牌类定义
│   ├── pattern.py         # 牌型识别与定义
│   └── comparator.py      # 牌型比较逻辑
├── ai/
│   ├── __init__.py
│   └── strategy.py        # AI出牌策略
├── requirements.txt       # 依赖包
└── README.md             # 项目说明
```

## 测试示例

使用Python测试WebSocket连接：

```python
import asyncio
import websockets
import json

async def test_ai():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # 发送请求
        request = {
            "msg": "ai_call",
            "level": 2,
            "last_move": [{"color": "Spade", "number": 5}],
            "your_cards": [
                {"color": "Heart", "number": 7},
                {"color": "Club", "number": 8},
                {"color": "Spade", "number": 9}
            ]
        }
        await websocket.send(json.dumps(request))
        
        # 接收响应
        response = await websocket.recv()
        print(f"Response: {response}")

asyncio.run(test_ai())
```

## 许可证

MIT License
