# -*- coding: utf-8 -*-
#“#”是凡人（指鄙人）的注释，神（codex）的注释以字符串的形式展现（英文）
#宇宙免责声明：
#hook就是装不上去，真的服了
#涉及使用了codex gpt-6 astra
#codex在简化代码方面给到夯，事实证明，想要什么功能，完全可以自己定义函数，而且不用在乎调用顺序
#同时，我使用了codex来规范格式（求放过，自己实在检查不过来）
#还有，一些原有的功能齐全方面报错功能的代码，我将其删除了（太复杂了，本来就难，想简洁点，而且各位大佬应该是允许随便改这个文件的吧doge）
#最后，Q7 与 加分题 是codex完成的（它自告奋勇的，我完全不知情）
#使用了codex的地方也有免责声明，求放过，纯手搓快把电脑砸了
"""Sentry diagnostics, damage analysis, navigation, and patrol control.

Run ``python main.py`` for the supplied ASCII demonstration.
"""
import json
from collections import deque
from enum import Enum


# ---------------------------------------------------------------------------
# 仿真世界基础（已提供，勿改）
# ---------------------------------------------------------------------------
class Facing(Enum):
    """朝向枚举。世界坐标 (x, y)：x 向右增长，y 向上增长（数学系）。"""

    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    #np,我自己还没太学懂装饰器，大概理解是为函数增添新功能（通过外部访问的方式）
    @property
    def delta(self):
        """该朝向的单位位移向量 (dx, dy)。"""
        return self.value[0], self.value[1]


# ---------------------------------------------------------------------------
# Q1 机器人自检（题面 Q1·自检状态计算与报告生成）
# ---------------------------------------------------------------------------
def hp_ratio(hp, max_hp):
    """Return a clamped integer percentage without floating-point rounding."""
    #_as_int 后来在后面补的，懒得把定义过程挪到前面了
    hp = _as_int(hp)
    max_hp = _as_int(max_hp)
    if max_hp <= 0:
        return 0
    return max(0, min(hp, max_hp)) * 100 // max_hp

#这里我根据codex的建议，定义了一个函数处理数据是否为整数的合法性的问题。这比大段的if-else更np,学到了
def _as_int(value, default=0):
    """Normalize a numeric reading, falling back on invalid values."""
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return default


def status_report(name, robot_type, hp, max_hp, battery):
    """Format diagnostics using fixed field widths and battery thresholds."""

    #_as_int 太豪用了，但是关于数值取值范围的问题并未处理，利用max & min 是codex的创意，依旧薄纱if语句
    battery = max(0, min(100, _as_int(battery)))
    if battery >= 60:
        level = "OK"
    elif battery >= 20:
        level = "WARNING"
    else:
        level = "LOW"

    #佬们的格式要求太变态了，特意学习了.format()（其实没太学懂，会用个皮毛），在report中显示的对齐方式更加智能）
    return ("{:<10}|{:^10}|HP {:>3}%|BAT {:>3}%|{}".format(
        name, robot_type, hp_ratio(hp, max_hp), battery, level))


# ---------------------------------------------------------------------------
# Q2 战斗日志分析（题面 Q2·多源日志解析与统计）
# ---------------------------------------------------------------------------
#闹麻了，第二个就让我写成制杖了

def analyze_damage_log(lines):
    """Aggregate valid damage events, rejecting malformed lines atomically.

    Each sensor segment counts as one event. Ties use front, left, right
    order. Only valid JSON records reserve their IDs for deduplication.
    """
    by_armor = {"front": 0, "left": 0, "right": 0}
    seen_ids = set() #codex建议使用set()避免id重复，利用了集合类的性质，6
    event_count = 0

    #神建议使用迭代器替代for循环，顺序传入，挨个儿处理，减少命令遍历次数
    #iterator同时避免lines非法传入导致直接报错退出程序，将其替换为空tuple，
    # 引入稳定的空数据集，使程序继续（仅自己的理解，不确定对不对）
    try:
        source = iter(lines)
    except TypeError:
        source = iter(())
       
    for line in source:

         #很明显，isinstance()在快速的类型判断且不提供报错日志的情况下更好用（神的建议）
        if not isinstance(line, str):
            continue
        line = line.strip()

        #codex建议补充对空行和注释行的处理
        if not line or line.startswith("#"):
            continue

        try:
            #对json的判断
            #粗略解析
            if line.startswith("{"):  #神定的标准
                record = json.loads(line)
                armor = record["armor"]
                damage = record["damage"]

                #对装甲名字与damage进行合法性检验
                if armor not in by_armor or type(damage) is not int:
                    continue
                if damage <= 0:
                    continue
                
                #对id进行合法性检验
                if "id" in record:
                    event_id = record["id"]
                    if event_id in seen_ids:
                        continue
                    seen_ids.add(event_id)
                events = [(armor, damage)]

            #对非json的情况进行处理,codex建议定义新函数（_parse_sensor_damage）
            else:
                events = _parse_sensor_damage(line)

        #对所谓的“脏行”处理，直接continue
        except (TypeError, ValueError, KeyError, RecursionError):
            continue
        
        #解包tuple，遍历日志中的所有damage
        for armor, damage in events:
            by_armor[armor] += damage
            event_count += 1

    #统计
    total = sum(by_armor.values())

    #计算平均值，取近似整数
    try:
        average = round(total / event_count, 2) if event_count else 0.0  
        #神的写法，吧if与else写进同一个逻辑语句（现学）

    #codex建议加上对极端大数的审查
    except OverflowError:
        average = float("inf")

    #活学活用————if语句新用法
    #.get用法，指定对名为by_armor字典的key所对应的value访问（自己理解）
    return {
        "total": total,
        "by_armor": by_armor,
        "most_hit": max(by_armor, key=by_armor.get) if event_count else None,
        "avg": average,
    }

#这个是神写的，我只敢注释（轻点喷）
def _parse_sensor_damage(line):
    """Validate a complete sensor line before returning any events."""
    armor_names = {"F": "front", "L": "left", "R": "right"}   #codex预测的翻译表
    events = []
    for segment in line.split(","):

        #对传入数据的合法性反馈
        armor, value = (part.strip() for part in segment.split(":"))
        if not value.isascii() or not value.isdecimal():
            raise ValueError("Damage must contain decimal digits")
        
        #重伤致死反馈
        damage = int(value)
        if damage <= 0:
            raise ValueError("Damage must be positive")
        events.append((armor_names[armor], damage))
    return events


# ---------------------------------------------------------------------------
# Q3 SentryGrid（题面 Q3·载体物理规则）
# ---------------------------------------------------------------------------
#这个比Q2像人
#codex做了优化（在我写完以后）

class SentryGrid:
    """A grid vehicle with collision detection and finite movement fuel."""

    def __init__(self, width, height, obstacles, enemy_pos,
                 start_pos=(0, 0), facing=Facing.UP, fuel=100):

        self._width = int(width)
        self._height = int(height)
        if self._width <= 0 or self._height <= 0:
            raise ValueError("地图尺寸必须为正")

        # 障碍坐标存入 set，查询 O(1)——已有实现，勿改。
        self._obstacles = set()
        for ob in obstacles:
            x, y = ob
            self._obstacles.add((int(x), int(y)))
        if not isinstance(enemy_pos, (tuple, list)) or len(enemy_pos) != 2:
            raise TypeError("enemy_pos 需要长度为 2 的 tuple/list")
        self._enemy_pos = self._clamp_cell(enemy_pos)
        if self._enemy_pos in self._obstacles:
            raise ValueError("enemy_pos 不能位于障碍物上")
        if not isinstance(facing, Facing):
            facing = Facing.UP
        self._facing = facing
        self._fuel = int(fuel)
        self._collision_count = 0
        self.current_pos = start_pos

    def _clamp_cell(self, cell):
        """已提供：元素转 int 并夹回地图范围（供 __init__ 使用）。"""
        x = int(cell[0])
        y = int(cell[1])
        x = max(0, min(self._width - 1, x))
        y = max(0, min(self._height - 1, y))
        return (x, y)

    # -- 只读属性（已提供，勿改） ------------------------------------------
    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def enemy_pos(self):
        return self._enemy_pos

    @property
    def facing(self):
        return self._facing

    @property
    def fuel(self):
        return self._fuel

    @property
    def collision_count(self):
        return self._collision_count

    @property
    def obstacles(self):
        """障碍集合的只读视图（内部 set 引用，不要修改它）。"""
        return self._obstacles

    @property
    def found_enemy(self):
        return self._pos == self._enemy_pos

    def is_blocked(self, x, y):
        """已提供：坐标是否为障碍或越界（O(1)）。"""
        return ((x, y) in self._obstacles
                or not (0 <= x < self._width and 0 <= y < self._height))

    # -- 你要实现的部分 ------------------------------------------------------
    #WC，语法糖？！
    #词难，主要是

    @property
    def current_pos(self):
        """当前位置 (x, y) 的 tuple。"""
        return self._pos

    @current_pos.setter
    def current_pos(self, value):
        """Convert and clamp a coordinate pair, rejecting obstacle cells."""
        
        #报错提示词是codex写的
        if not isinstance(value, (tuple, list)) or len(value) != 2:   
            raise TypeError("Position must be a tuple or list of length two")

        position = self._clamp_cell(value)
        if position in self._obstacles:
            raise ValueError("Position cannot be on an obstacle")

        self._pos = position

    def move_forward(self):
        """Spend one fuel per powered attempt; walls leave position intact."""

        if self._fuel <= 0:
            return self._pos

        self._fuel -= 1
        dx, dy = self._facing.delta
        position = (self._pos[0] + dx, self._pos[1] + dy)

        #关于*的拆包用法，当然也是codex的建议      
        if self.is_blocked(*position):
            self._collision_count += 1
        else:
            self._pos = position

        return self._pos

    def turn_left(self):
        """Rotate counterclockwise without consuming fuel."""

        dx, dy = self._facing.delta
        self._facing = Facing((-dy, dx))
        return self._facing

    def turn_right(self):
        """Rotate clockwise without consuming fuel."""

        dx, dy = self._facing.delta
        self._facing = Facing((dy, -dx))
        return self._facing


# ---------------------------------------------------------------------------
# Q4 贪心导航（题面 Q4·单步贪心导航策略）
# ---------------------------------------------------------------------------
def next_step_toward(pos, target, obstacles, current_facing=Facing.UP):
    """Choose a distance-reducing step, preferring the x axis on ties."""

    dx, dy = target[0] - pos[0], target[1] - pos[1]  #列表就是好访问

    horizontal = Facing.RIGHT if dx > 0 else Facing.LEFT  #if else逻辑语句太豪用辣
    vertical = Facing.UP if dy > 0 else Facing.DOWN

    candidates = [(dx, horizontal), (dy, vertical)]  

    if abs(dy) > abs(dx):  #有一说一，只看绝对值大小是真的人机
        candidates.reverse()

    for difference, direction in candidates:  #使用difference与direction来解包，贪就贪到底
        if difference == 0:
            continue

        step_x, step_y = direction.delta
        if (pos[0] + step_x, pos[1] + step_y) not in obstacles:
            return direction

    return current_facing


# ---------------------------------------------------------------------------
# Q5 哨兵决策机（题面 Q5·裁判系统决策规则表）
# ---------------------------------------------------------------------------
#后半截不难

class SentryState(Enum):
    """哨兵状态机（已提供，勿改）。"""

    PATROL = "PATROL"
    SUSPECT = "SUSPECT"
    ENGAGE = "ENGAGE"
    RETREAT = "RETREAT"
    RETURN = "RETURN"

#依旧神写报告词
def decide(sensor, state, hp, heat):
    """Apply R1-R7 in order; heat does not override the specified rules."""

    fields = {"enemy_frames", "enemy_dist", "robot_type", "max_hp"}

    #下面全当是鄙人使用isinstance的实践，在神的帮助下
    if not isinstance(state, SentryState):
        raise ValueError("State must be a SentryState member")

    #codex指导使用issubset函数代替 if 判断语句
    if not isinstance(sensor, dict) or not fields.issubset(sensor):
        raise ValueError("Sensor is missing required fields")

    frames = sensor["enemy_frames"]
    if not isinstance(frames, (tuple, list)):
        frames = (False,)
    elif not 1 <= len(frames) <= 6:
        raise ValueError("Enemy history must contain one to six frames")

    #神写的，强制转换为bool
    #唯一一段自己写的还被神改成了一句，不过确实np
    frames = tuple(bool(frame) for frame in frames)
    visible = frames[-1]
    distance = _as_int(sensor["enemy_dist"], default=None)
    distance = float("inf") if distance is None else max(0, distance)
    robot_type = sensor["robot_type"]

    if isinstance(robot_type, str):
        robot_type = robot_type.strip().upper()
    if robot_type != "HERO":
        robot_type = "INFANTRY"
    hp_pct = hp_ratio(hp, sensor["max_hp"])

    if hp_pct <= 30:  # R1: survival takes precedence over every state.
        return "RETREAT", SentryState.RETREAT

    if state is SentryState.RETREAT:  # R2: use recovery hysteresis.
        if hp_pct >= 60:
            return "RETURN", SentryState.RETURN
        return "RETREAT", SentryState.RETREAT

    if state is SentryState.RETURN:  # R3: return lasts one frame.
        return "MOVE_BASE", SentryState.PATROL

    if state is SentryState.ENGAGE:
        if visible:  # R4
            return _engagement_action(distance, robot_type)
        if len(frames) >= 3 and not any(frames[-3:]):  # R5
            return "SCAN", SentryState.SUSPECT
        return "HOLD_FIRE", SentryState.ENGAGE

    if visible:  # R6: require consecutive confirmation frames.
        if len(frames) >= 2 and frames[-2]:
            return _engagement_action(distance, robot_type)
        return "SCAN", SentryState.SUSPECT

    if state is SentryState.PATROL:  # R7
        return "PATROL_MOVE", SentryState.PATROL
    return "SCAN", SentryState.SUSPECT


def _engagement_action(distance, robot_type):
    """Share the identical engagement behavior required by R4 and R6."""
    if distance <= 3:
        return "SHOOT", SentryState.ENGAGE
    action = "MOVE_RIGHT" if robot_type == "HERO" else "MOVE_LEFT"
    return action, SentryState.ENGAGE


# ---------------------------------------------------------------------------
# Q6 巡逻任务（题面 Q6·巡逻契约与验收阈值）
# ---------------------------------------------------------------------------

#大量使用神定义的函数

def run_patrol(grid, max_steps=500):
    """Follow greedy steps and use a BFS detour to escape local minima.

    Resume greedy navigation once closer than the stalled position. Steps
    count forward attempts; visited cells include the initial position.
    """
    #依旧神的变量，自己根本记不住
    #codex优化
    steps = 0
    visited = {grid.current_pos}
    detour = deque()
    entry_distance = 0
    
    #这次使用while循环
    while (steps < max_steps and grid.fuel > 0 and not grid.found_enemy):

        position = grid.current_pos
        distance = _manhattan(position, grid.enemy_pos)
        direction = next_step_toward(position, grid.enemy_pos, grid.obstacles, grid.facing)

        if detour and distance < entry_distance:
            detour.clear()

        if not detour:
            dx, dy = direction.delta
            neighbor = (position[0] + dx, position[1] + dy)

            if (grid.is_blocked(*neighbor) or _manhattan(neighbor, grid.enemy_pos) >= distance):
                obstacles = set(grid.obstacles)
                obstacles.update(_border_ring(grid.width, grid.height))
                path = _bfs_path(position, grid.enemy_pos, obstacles)

                if path is None:
                    break
                detour.extend(path)
                entry_distance = distance

        if detour:
            direction = detour.popleft()
        _face_direction(grid, direction)
        grid.move_forward()
        steps += 1
        visited.add(grid.current_pos)

    return {
        "steps": steps,
        "collisions": grid.collision_count,
        "visited_count": len(visited),
        "found_enemy": grid.found_enemy,
        "success": grid.found_enemy,
    }


def _manhattan(start, target):
    """Return distance on an obstacle-free four-neighbor grid."""
    return abs(start[0] - target[0]) + abs(start[1] - target[1])


def _border_ring(width, height):
    """Enclose a finite grid for searches that only inspect obstacles."""
    ring = {(x, -1) for x in range(-1, width + 1)}
    ring.update((x, height) for x in range(-1, width + 1))
    ring.update((-1, y) for y in range(-1, height + 1))
    ring.update((width, y) for y in range(-1, height + 1))
    return ring


def _face_direction(grid, direction):
    """Align the vehicle using at most two quarter turns."""
    clockwise = (Facing.UP, Facing.RIGHT, Facing.DOWN, Facing.LEFT)
    turns = (clockwise.index(direction) - clockwise.index(grid.facing)) % 4
    if turns == 3:
        grid.turn_left()
    else:
        for _ in range(turns):
            grid.turn_right()


def report_to_json(stats):
    """Serialize with sorted keys and stable, compact separators."""
    return json.dumps(stats, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


# ---------------------------------------------------------------------------
# Bonus：BFS 全局最短路（题面 Bonus·BFS 语义与排行榜）
# ---------------------------------------------------------------------------
def bfs_path_length(start, target, obstacles):
    """Return the shortest distance, or -1 if the target is unreachable.

    The caller must enclose the search space with boundary obstacles.
    Identical endpoints have distance zero, even if that cell is blocked.
    """
    path = _bfs_path(start, target, set(obstacles))
    return -1 if path is None else len(path)


def _bfs_path(start, target, obstacles):
    """Find a shortest sequence of headings using a FIFO frontier."""
    if start == target:
        return []
    if start in obstacles or target in obstacles:
        return None
    frontier = deque([start])
    parents = {start: None}
    while frontier:
        position = frontier.popleft()
        for direction in Facing:
            dx, dy = direction.delta
            neighbor = (position[0] + dx, position[1] + dy)
            if neighbor in obstacles or neighbor in parents:
                continue
            parents[neighbor] = (position, direction)
            if neighbor == target:
                path = []
                while neighbor != start:
                    neighbor, heading = parents[neighbor]
                    path.append(heading)
                path.reverse()
                return path
            frontier.append(neighbor)
    return None


# ---------------------------------------------------------------------------
# 渲染（已提供，demo 专用，不进测试）
# ---------------------------------------------------------------------------
def render_frame(grid, trail=()):
    """ASCII 渲染一帧战场；trail 为走过的格子集合。返回 list[str]。"""
    trail = set(trail)
    rows = []
    for y in range(grid.height - 1, -1, -1):
        row = []
        for x in range(grid.width):
            if (x, y) == grid.current_pos:
                row.append("◉")
            elif (x, y) == grid.enemy_pos:
                row.append("▲")
            elif (x, y) in grid.obstacles:
                row.append("█")
            elif (x, y) in trail:
                row.append("·")
            else:
                row.append(".")
        rows.append("".join(row))
    return rows
