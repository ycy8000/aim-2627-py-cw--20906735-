# AIM 2627 Python Coursework —— 哨兵 Sentry 控制模块

> **全部题目、规范、评分、提交见 [题面.pdf](题面.pdf)。** 本 README 只讲怎么把环境跑起来；没在这里出现的规格细节，一律以题面为准。

## 1. 环境要求

- Python 3.8+，仅标准库（不允许第三方运行时依赖）；
- 开发工具只需 `pytest`（测试）与 `autopep8`（风格，CI 会检查）；
- VS Code 打开仓库会推荐安装 `ms-python.autopep8` 插件（`.vscode/extensions.json`），保存即格式化即可过风格检查。

## 2. 快速开始

```bash
# 1. 用 GitHub 的 Use this template 创建你自己的仓库，然后 clone
git clone https://github.com/<你的用户名>/<你的仓库>.git
cd <你的仓库>   # 直接在 main 分支上开发

# 创建虚拟环境

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. 装依赖
python -m pip install pytest autopep8

# 3. 启用 AI 会话归档钩子（课程要求，见下方第 3 节）
python -m pip install 'agent-session-commit[pre-commit]==0.1.3' -i https://pypi.org/simple
agent-session-commit install --pre-commit   # 交互选择你的 AI 助手与会话目录

# 4. 跑测试（刚到手：全部 skip，CI 是绿的）
python -m pytest

# 5. 看演示
python main.py

# 6. 打开 题面.pdf 读题，开始实现 src/main/__init__.py 里的 TODO
```

## 3. AI 会话归档（pre-commit）

本课程允许使用 AI，提交的 commit 需要携带 AI 会话归档作为透明化记录：每次 `git commit` 后，钩子会把新增会话自动 amend 进同一个提交（`.agent-sessions/bundles/`），不产生额外的归档提交。支持 Claude Code、OpenAI Codex CLI、GitHub Copilot CLI、Qoder、ZCode、Trae、Tencent CodeBuddy 等（完整名单见 [AgentLedger](https://github.com/Gentle-Lijie/AgentLedger)）。

- 配置是仓库本地的：每个 clone 运行一次 `agent-session-commit install --pre-commit`，方向键选择 agent、确认其会话目录即可；
- 不想用 TUI 可手动配置：`git config --local agent-session.agent claude`、`git config --local agent-session.source "<会话目录>"`，然后 `python -m pip install 'pre-commit>=3.2.0' && pre-commit install`；
- 归档是普通 Git 内容且会推送到公开仓库——不要在 AI 会话里粘贴令牌等敏感信息；
- 换了 agent 或目录就重跑一次安装命令；卸载：从 `.pre-commit-config.yaml` 移除该条目后重跑 `pre-commit install`。

## 4. 本地开发循环

- **写代码**：全部作业在 `src/main/__init__.py`，按题面各题规范补全每个标有 TODO 的函数；注释里标注了对应的题面主题，推荐顺序 Q1 → Q6。
- **跑测试**：`python -m pytest` —— 可见测试是规格书的一部分，未实现的函数自动 skip，实现一个、对应测试亮一个。本地全绿 ≠ 满分（见题面）。
- **看演示**：`python main.py`（等价于 `PYTHONPATH=src python -m main`），随实现进度逐段点亮，不进测试。
- **Q6 自测**：`python tools/run_seeds.py --q6`（200 张固定地图统计），单 seed 渲染 `python tools/run_seeds.py --q6 --seed <N> --render`，Bonus 模式 `python tools/run_seeds.py --bonus`。

## 5. 仓库结构（哪些能改）

| 路径 | 说明 | 能否修改 |
|---|---|---|
| `src/main/__init__.py` | 你的全部作业（TODO 所在） | ✅ |
| `README.md` | 仅末尾两个"你来写"小节 | ✅ |
| `题面.pdf` | 题面（唯一规格说明） | ❌ 勿改 |
| `src/main/legacy_patrol.py` | Q7 模块（与主体同步发布，修复其缺陷） | Q7 时 ✅ |
| `.pre-commit-config.yaml` | AI 会话归档钩子配置 | ❌ 勿改 |
| `src/tests/`、`tools/`、`.github/`、`conftest.py`、`pytest.ini`、`main.py` | 测试与基础设施 | ❌ 勿改 |

CI 只允许修改 `src/main/**`、`README.md` 与 `.agent-sessions/**`（AI 会话归档）——其余文件改了直接红；autopep8 `--diff` 非空即败。提交方式（push、问卷、commit 粒度）见题面"提交与验收"一节。

## 6. 实现与设计说明 (codex跑测试并做出总结)

Q1–Q7 与 Bonus 均已实现。运行时代码仅使用 Python 标准库。

### 各题实现（神的总结，感觉这样比较嘉豪）

- **Q1 自检**：血量先转换为整数、限制到合法范围，再用整数乘除计算百分比，避免浮点误差使 `29/100` 被错误截断为 28%。报告使用题面的字段宽度，电量规范化到 0–100。
- **Q2 日志**：逐行解析 JSON 和传感器格式。整行通过校验后才累计，避免 `F:10,L:bad` 中的前半段污染统计。JSON 的 `damage` 必须为严格正整数，布尔值、浮点数和数字字符串均不接受。只有有效 JSON 事件才占用去重 ID。
- **Q3 载体**：位置先验证容器类型和长度，再转整数、夹到地图范围、排除障碍，最后赋值。构造函数复用 setter。每次有电的前进尝试消耗一单位电量；撞障碍或边界保持位置、朝向并增加碰撞计数。断电后前进不再改变任何状态，原地转向不耗电。
- **Q4 贪心**：只考虑能严格缩短曼哈顿距离的方向，优先绝对坐标差较大的轴；该轴受阻时再检查另一轴，无候选则保持朝向。
- **Q5 决策**：先验证输入契约、规范化字段，再按 R1–R7 的顺序返回首个命中结果。R4 与 R6 共用交火动作函数，保证同样的敌距和机型产生同样的动作。规则表没有热量拦截条款，所以 `heat` 不覆盖规则结果；R1 仍优先于近距离射击和返航。
- **Q6 巡逻**：每轮读取位置、调用 Q4 选方向、对齐朝向并前进。贪心无有效减距方向时，临时添加地图边界并执行 BFS，保存绕行路径；到目标的距离小于进入死角时的距离后恢复贪心。BFS 已确认目标不可达时直接返回失败，不继续空耗动作。代码不重置电量、不直接改写位置，也不修改原障碍集合。
- **Bonus**：使用 `deque` 实现 BFS，入队时记录已访问格和父节点，找到目标后还原最短路径并返回长度。起终点相同返回 0，不可达返回 -1。地图边界由调用方提供；`tools/run_seeds.py --bonus` 已内置将导航替换为 BFS 的流程。

设日志有 `L` 个字符、`K` 个独立 ID，Q2 的常规时间复杂度为 O(L)、额外空间为 O(K)。单次贪心选向为 O(1)，单次 BFS 的时间与空间均为 O(V + E)；四邻域网格中 E 为 O(V)。Q6 只在失速时搜索，缓存脱困路径，避免普通移动时重复搜索整张地图。

some questions：（主要是神的疑问）

|血量与满血量 | 可转换值使用 `int`；转换失败按 0；满血量不为正时百分比为 0；百分比向下取整并限制到 0–100 |
| 电量档位 | `< 20` 为 LOW，`20–59` 为 WARNING，`>= 60` 为 OK |
| 日志平均值 | 一段有效传感器伤害算一个事件，一条有效 JSON 算一个事件；按有效事件数取平均并 `round(..., 2)`；空日志为 `0.0` |
| 日志平局与 ID | 同伤害按 front、left、right 顺序取首个；ID 必须可哈希，按 Python 集合的相等性去重；无 ID 的行不去重 |
| 传感器格式 | 允许分隔符周围的空白；伤害只接受 ASCII 十进制正整数字符；重复部位段分别累计 |
| 极大日志数值 | 伤害总和保留精确整数；平均值超出浮点范围时返回正无穷，避免抛出异常 |
| 贪心平局 | x、y 轴差的绝对值相等时优先 x 轴 |
| 撤退恢复与持续丢失 | 血量达到 60% 转入 RETURN；ENGAGE 连续末三帧不可见时转入 SUSPECT |
| 异常感知值 | 非 tuple/list 的帧历史按单帧不可见处理；tuple/list 长度不在 1–6 时抛 `ValueError`；各元素按真值解释 |
| 敌距与机型 | 敌距无法转换或为 `None` 时按无限远处理，负值夹到 0；机型去除首尾空白并转大写，未知值按 INFANTRY |
| 巡逻统计 | `steps` 计前进尝试，不计转向；`visited_count` 含起点并去重；`collisions` 返回载体累计碰撞数；`found_enemy` 与 `success` 同义 |

### 本地验证

| 仓库提供的 pytest | 35 项通过，无跳过 |
| Q6，seed 1–200 | 成功率 100%，平均碰撞 0，成功案例平均步数 / BFS 最短路为 1.03，全部达到题面阈值 |
| Q6，额外 seed 1001–1200 | 成功率 100%，平均碰撞 0，平均步数 / BFS 最短路为 1.0429 |
| Bonus，seed 1–200 | 成功率 100%，平均步数 29.5，平均碰撞 0 |
| 补充边界检查 | 92 项通过，包括 100 张随机小地图与独立有界 BFS 的对照、状态优先级、无电与步数上限、日志原子性、Q7 终止语义 |
| 格式、范围与兼容语法 | autopep8 无差异，isort 和 `git diff --check` 通过；只修改允许的三个文件；Python 3.8 语法解析通过（未运行 3.8 环境测试） |
| 演示入口 | 正常运行；Q6 演示 15 步到达目标、零碰撞 |

## 7. Q7 缺陷定位与修复

按函数 docstring 对照输入、单位、边界和循环状态，定位到六处主要缺陷：

| 缺陷 | 定位依据与修复 |
| --- | --- |
| 路线单位不一致 | `segment_length_cm` 正确返回厘米，但 `total_route_meters` 直接累加导致结果大 100 倍。路线 `(0,0) → (3,0) → (3,4)` 应为 7 米而非 700 米；在累计处除以 100，保留底层厘米契约。 |
| 无正样本时对 `None` 做减法 | `first_positive([-1, -2])` 按契约返回 `None`，`calibrate` 却继续计算。增加 `baseline is None` 分支，空样本或没有正样本时返回 0。 |
| 遗漏 `id == max_id` 的事件 | “不超过”要求 `<=`，原代码使用 `<`。用恰好等于上限的事件定位后改为 `<=`。 |
| 默认历史列表跨调用共享 | 默认参数 `history=[]` 只创建一次，第二次无参数调用会读到前次日志。改成默认 `None`，在每次调用内创建新列表；显式传入列表时仍在原列表上追加。 |
| 体力终止比较反向 | 原代码在 `stamina > 20` 时停止，导致高体力运行一轮就退出；按契约改为每轮结束后 `stamina <= 20` 才停止。`run_legacy_sim(2, 28)` 必须在剩余 20 时结束。 |
| 循环轮号没有推进 | `round_` 始终为 0，轮数上限和第 4 轮额外消耗都无法生效。每轮记录 trace 后增加轮号；`run_legacy_sim(10, 100)` 的体力依次为 92、84、76、63、50、37、24、11，共 8 轮。 |

两组遮蔽关系：`id < max_id` 可能把“无正样本”的事件过滤掉，修复边界后才暴露 `calibrate` 的异常；错误的体力比较使常规输入首轮退出，掩盖了轮号不递增的问题。只修复比较后，虽然体力终止可生效，轮数上限、trace 和额外消耗仍不正确，因此必须成对验证。

另外按“脏行不得抛异常”的契约加固了 `parse_event`：非字符串、不能安全转换的数值文本返回 `None`。例如 `"MOVE,²"` 可通过原来的 `isdigit()`，但 `int("²")` 会失败；现在先检查 ASCII 十进制数字，并捕获整数转换异常。


