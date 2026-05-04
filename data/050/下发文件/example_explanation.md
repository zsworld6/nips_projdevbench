# example.in 样例解释

约定：

- 血量写作 `(P0, P1)`，分别表示玩家 0 和玩家 1 的当前 HP。
- 这里只展开 `op` 指令；`query` 和 `supply` 不直接改变 HP。
- 概率输出保留两位小数。
- 每次 `supply` 阶段都保证：玩家 0 和玩家 1 各自恰好有 2 个道具。

查询原理：

- 未被 Magnifier 锁定时：
  - `P(live) = liveCount / (liveCount + blankCount)`
  - `P(blank) = blankCount / (liveCount + blankCount)`
- 若 Magnifier 已确定下一发，则概率为确定值（0 或 1）。

## 第 1 局

补给：`supply bullet 5 1`，并给双方各补 2 个道具。
初始 `P(live)=5/6=0.83`，`P(blank)=1/6=0.17`。

### 查询与原理

1. `query live` -> `0.83`
2. `query blank` -> `0.17`
3. `op use_magnifier live` 后，下一发确定为 `live`
4. `query live` -> `1.00`
5. `query blank` -> `0.00`
6. `op fire_opponent live` 后，剩余 `4 live, 1 blank`
7. `query live` -> `0.80`
8. `query blank` -> `0.20`
9. `op fire_self live` 后，剩余 `3 live, 1 blank`
10. `query live` -> `0.75`

### op 过程（执行者与血量）

| 步骤  | 指令                      | 执行者  | 执行后 HP (P0, P1)     |
| --- | ----------------------- | ---- | ------------------- |
| 1   | `op use_magnifier live` | 玩家 0 | `(5, 5)`            |
| 2   | `op fire_opponent live` | 玩家 0 | `(5, 4)`            |
| 3   | `op fire_self live`     | 玩家 1 | `(5, 3)`            |
| 4   | `op fire_opponent live` | 玩家 0 | `(5, 2)`            |
| 5   | `op fire_self live`     | 玩家 1 | `(5, 1)`            |
| 6   | `op fire_opponent live` | 玩家 0 | `(5, 0)` -> 玩家 0 获胜 |

## 第 2 局

补给：`supply bullet 6 0`，并给双方各补 2 个道具。
其中玩家 1 拥有两个 `cage`。

### 非法操作 1：道具不存在

- 指令：`op use_dummy live`
- 执行者：玩家 0
- 原因：玩家 0 没有 `dummy`
- 结果：输出 `error!`，状态不变。

### 非法操作 2：同回合使用两次 cage

- 玩家 1 先执行一次 `op use_cage`（合法）。
- 随后在同一回合再次执行 `op use_cage`（非法）。
- 结果：输出 `error!`，状态不变。

### 查询与原理

1. 非法操作后 `query live` -> `1.00`（仍是 `6 live, 0 blank`）
2. 第二次 `use_cage` 非法后再 `query live` -> `1.00`

### op 过程（执行者与血量）

| 步骤  | 指令                      | 执行者  | 执行后 HP (P0, P1)     | 备注             |
| --- | ----------------------- | ---- | ------------------- | -------------- |
| 1   | `op use_dummy live`     | 玩家 0 | `(5, 5)`            | 非法，输出 `error!` |
| 2   | `op fire_opponent live` | 玩家 0 | `(5, 4)`            |                |
| 3   | `op use_cage`           | 玩家 1 | `(5, 4)`            | 合法             |
| 4   | `op use_cage`           | 玩家 1 | `(5, 4)`            | 非法，输出 `error!` |
| 5   | `op fire_opponent live` | 玩家 1 | `(4, 4)`            | cage 生效，本次后不换手 |
| 6   | `op fire_opponent live` | 玩家 1 | `(3, 4)`            |                |
| 7   | `op fire_self live`     | 玩家 0 | `(2, 4)`            |                |
| 8   | `op fire_opponent live` | 玩家 1 | `(1, 4)`            |                |
| 9   | `op fire_self live`     | 玩家 0 | `(0, 4)` -> 玩家 1 获胜 |                |

## 第 3 局

补给：`supply bullet 6 0`，并给双方各补 2 个道具。

### 查询与原理

1. `query live` -> `1.00`
2. `op use_dummy live` 消耗一发实弹后仍全实弹，`query live` -> `1.00`

### op 过程（执行者与血量）

| 步骤  | 指令                      | 执行者  | 执行后 HP (P0, P1)     |
| --- | ----------------------- | ---- | ------------------- |
| 1   | `op use_dummy live`     | 玩家 0 | `(5, 5)`            |
| 2   | `op fire_opponent live` | 玩家 0 | `(5, 4)`            |
| 3   | `op fire_self live`     | 玩家 1 | `(5, 3)`            |
| 4   | `op fire_opponent live` | 玩家 0 | `(5, 2)`            |
| 5   | `op fire_self live`     | 玩家 1 | `(5, 1)`            |
| 6   | `op fire_opponent live` | 玩家 0 | `(5, 0)` -> 玩家 0 获胜 |

## 与 example.out 对应

`example.out` 输出顺序：

1. 第 1 局 `query live` -> `0.83`
2. 第 1 局 `query blank` -> `0.17`
3. 第 1 局 `query live`（magnifier 后）-> `1.00`
4. 第 1 局 `query blank`（magnifier 后）-> `0.00`
5. 第 1 局 `query live`（射击后）-> `0.80`
6. 第 1 局 `query blank`（射击后）-> `0.20`
7. 第 1 局 `query live`（再射击后）-> `0.75`
8. 第 1 局结束 -> `player 0 win!`
9. 第 2 局非法操作（无 dummy）-> `error!`
10. 第 2 局 `query live` -> `1.00`
11. 第 2 局非法操作（同回合第二次 cage）-> `error!`
12. 第 2 局 `query live` -> `1.00`
13. 第 2 局结束 -> `player 1 win!`
14. 第 3 局 `query live` -> `1.00`
15. 第 3 局 `query live`（dummy 后）-> `1.00`
16. 第 3 局结束 -> `player 0 win!`
