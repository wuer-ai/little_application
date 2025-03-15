import pygame
import random
import time
from collections import deque

# 初始化Pygame
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (220, 220, 220)  # 淡化网格线颜色
LIGHT_BLUE = (100, 149, 237)  # 玩家蛇的颜色
DARK_GRAY = (50, 50, 50)  # AI蛇的颜色

# 游戏设置
WINDOW_SIZE = (800, 600)
GRID_SIZE = 20
GRID_WIDTH = WINDOW_SIZE[0] // GRID_SIZE
GRID_HEIGHT = WINDOW_SIZE[1] // GRID_SIZE

# 创建游戏窗口
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('贪吃蛇大作战')

class Snake:
    def __init__(self, x, y, color, is_player=False):
        self.body = [(x, y)]
        self.direction = (1, 0)
        self.color = color
        self.score = 0
        self.growth_pending = False
        self.is_player = is_player  # 添加标记是否为玩家控制的蛇
        self.move_this_frame = True  # 所有蛇都默认移动

    def move(self):
        # 所有蛇都会移动，不再需要检查move_this_frame
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # 检查是否撞墙
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            return False

        # 检查是否撞到自己
        if new_head in self.body:
            return False

        self.body.insert(0, new_head)
        if not self.growth_pending:
            self.body.pop()
        else:
            self.growth_pending = False
            
        return True

    def change_direction(self, new_direction):
        # 防止180度转向
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def grow(self):
        self.growth_pending = True

    def get_head(self):
        return self.body[0]

class Fruit:
    def __init__(self, points=1):
        self.position = self.get_random_position()
        self.points = points
        self.spawn_time = time.time()

    def get_random_position(self):
        # 预先计算随机位置，避免在游戏循环中计算
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        return (x, y)
        
    def respawn(self, snake_bodies=[]):
        # 重新生成果实位置，避免与蛇身体重叠
        position = self.get_random_position()
        # 确保新果实不会出现在蛇身上
        attempts = 0
        while position in snake_bodies and attempts < 10:
            position = self.get_random_position()
            attempts += 1
        self.position = position

def find_path(start, target, snake_bodies):
    queue = deque([(start, [])])
    visited = set([start])
    
    while queue:
        current, path = queue.popleft()
        if current == target:
            return path

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_pos = (current[0] + dx, current[1] + dy)
            if (0 <= next_pos[0] < GRID_WIDTH and
                0 <= next_pos[1] < GRID_HEIGHT and
                next_pos not in visited and
                next_pos not in snake_bodies):
                queue.append((next_pos, path + [(dx, dy)]))
                visited.add(next_pos)
    return None

# 添加不同难度AI的移动逻辑
def get_ai_move(ai_snake, fruit_pos, snake_bodies, difficulty):
    ai_head = ai_snake.get_head()
    
    # 困难模式：使用完整的寻路算法
    if difficulty == "困难":
        path = find_path(ai_head, fruit_pos, snake_bodies)
        if path and path[0]:
            return path[0]
    
    # 一般模式：只在一定距离内使用寻路算法，否则随机移动
    elif difficulty == "一般":
        # 计算与果实的曼哈顿距离
        distance = abs(ai_head[0] - fruit_pos[0]) + abs(ai_head[1] - fruit_pos[1])
        # 只有在距离小于10格时才使用寻路算法
        if distance < 10:
            path = find_path(ai_head, fruit_pos, snake_bodies)
            if path and path[0]:
                return path[0]
    
    # 简单模式：随机移动，有一定概率改变方向
    elif difficulty == "简单":
        # 有30%的概率随机改变方向
        if random.random() < 0.3:
            # 随机选择一个有效的移动方向
            possible_directions = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_pos = (ai_head[0] + dx, ai_head[1] + dy)
                # 确保不会撞墙或撞到自己
                if (0 <= next_pos[0] < GRID_WIDTH and
                    0 <= next_pos[1] < GRID_HEIGHT and
                    next_pos not in ai_snake.body):
                    # 确保不会180度转向
                    if (dx * -1, dy * -1) != ai_snake.direction:
                        possible_directions.append((dx, dy))
            
            if possible_directions:
                return random.choice(possible_directions)
        
        # 如果没有随机改变方向，尝试使用寻路算法
        path = find_path(ai_head, fruit_pos, snake_bodies)
        if path and path[0]:
            return path[0]
    
    # 如果没有找到路径或者是简单模式随机移动，尝试避免撞墙
    possible_directions = []
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        next_pos = (ai_head[0] + dx, ai_head[1] + dy)
        if (0 <= next_pos[0] < GRID_WIDTH and
            0 <= next_pos[1] < GRID_HEIGHT and
            next_pos not in ai_snake.body):
            # 确保不会180度转向
            if (dx * -1, dy * -1) != ai_snake.direction:
                possible_directions.append((dx, dy))
    
    if possible_directions:
        return random.choice(possible_directions)
    
    # 如果没有可行的方向，返回当前方向（可能会导致游戏结束）
    return ai_snake.direction

def draw_rounded_rect(surface, color, rect, radius=0.4):
    """绘制圆角矩形"""
    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0, 0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)

    circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)

    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)

    surface.blit(rectangle, pos)

def main():
    clock = pygame.time.Clock()
    # 使用系统默认字体以支持中文显示
    try:
        font = pygame.font.SysFont('SimHei', 36)  # 使用黑体
        small_font = pygame.font.SysFont('SimHei', 24)  # 小一点的字体用于按钮
    except:
        font = pygame.font.Font(None, 36)  # 如果找不到中文字体，使用默认字体
        small_font = pygame.font.Font(None, 24)  # 小一点的字体用于按钮

    # 游戏状态
    game_state = "menu"  # 可能的状态: "menu", "playing", "game_over", "paused"
    ai_difficulty = "一般"  # 默认难度为一般
    
    # 初始化玩家和AI蛇
    player_snake = Snake(5, GRID_HEIGHT // 2, LIGHT_BLUE, is_player=True)  # 标记为玩家蛇
    ai_snake = Snake(GRID_WIDTH - 6, GRID_HEIGHT // 2, DARK_GRAY)

    # 初始化果实
    fruit = Fruit()
    game_start_time = time.time()
    last_fruit_spawn = game_start_time
    pause_start_time = 0  # 记录暂停开始时间
    total_pause_time = 0  # 记录总暂停时间
    
    # 特殊果实标志
    special_fruit_spawned = {30: False, 60: False, 90: False}

    running = True
    game_over = False
    final_game_time = 0
    final_time_left = 120  # 初始化最终剩余时间
    game_time = 0  # 初始化游戏时间变量，确保在所有执行路径中都有定义
    
    # 游戏结束后的按钮
    continue_button = pygame.Rect(WINDOW_SIZE[0]//2 - 100, WINDOW_SIZE[1]//2 + 60, 80, 40)
    exit_button = pygame.Rect(WINDOW_SIZE[0]//2 + 20, WINDOW_SIZE[1]//2 + 60, 80, 40)
    
    # 难度选择按钮
    easy_button = pygame.Rect(WINDOW_SIZE[0]//2 - 150, WINDOW_SIZE[1]//2, 80, 40)
    normal_button = pygame.Rect(WINDOW_SIZE[0]//2 - 40, WINDOW_SIZE[1]//2, 80, 40)
    hard_button = pygame.Rect(WINDOW_SIZE[0]//2 + 70, WINDOW_SIZE[1]//2, 80, 40)
    start_button = pygame.Rect(WINDOW_SIZE[0]//2 - 40, WINDOW_SIZE[1]//2 + 60, 80, 40)
    
    while running:
        current_time = time.time()
        
        # 根据游戏状态处理逻辑
        if game_state == "playing":
            if not game_over:
                game_time = current_time - game_start_time

                # 检查游戏是否结束（2分钟时限）
                if game_time >= 120:
                    game_over = True
                    game_state = "game_over"
                    # 记录游戏结束时的时间和分数，避免后续更新
                    final_game_time = game_time
                    final_time_left = max(0, 120 - int(final_game_time))
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if game_state == "playing" and not game_over:
                    if event.key == pygame.K_UP:
                        player_snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        player_snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        player_snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        player_snake.change_direction((1, 0))
                    elif event.key == pygame.K_SPACE:
                        # 暂停游戏
                        game_state = "paused"
                        pause_start_time = current_time
                elif game_state == "paused" and event.key == pygame.K_SPACE:
                    # 继续游戏
                    game_state = "playing"
                    # 计算暂停的时间并调整游戏开始时间
                    total_pause_time += current_time - pause_start_time
                    game_start_time = game_start_time + (current_time - pause_start_time)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 主菜单状态下的按钮处理
                if game_state == "menu":
                    if easy_button.collidepoint(mouse_pos):
                        ai_difficulty = "简单"
                    elif normal_button.collidepoint(mouse_pos):
                        ai_difficulty = "一般"
                    elif hard_button.collidepoint(mouse_pos):
                        ai_difficulty = "困难"
                    elif start_button.collidepoint(mouse_pos):
                        # 开始游戏
                        game_state = "playing"
                        game_over = False
                        player_snake = Snake(5, GRID_HEIGHT // 2, LIGHT_BLUE, is_player=True)
                        ai_snake = Snake(GRID_WIDTH - 6, GRID_HEIGHT // 2, DARK_GRAY)
                        fruit = Fruit()
                        game_start_time = time.time()
                        last_fruit_spawn = game_start_time
                        special_fruit_spawned = {30: False, 60: False, 90: False}
                elif exit_button.collidepoint(mouse_pos):
                    running = False
                # 游戏结束状态下的按钮处理
                elif game_state == "game_over" and continue_button.collidepoint(mouse_pos):
                    # 重置游戏状态
                    game_state = "menu"
                    game_over = False
                    # 重新初始化游戏元素
                    player_snake = Snake(5, GRID_HEIGHT // 2, LIGHT_BLUE, is_player=True)
                    ai_snake = Snake(GRID_WIDTH - 6, GRID_HEIGHT // 2, DARK_GRAY)
                    fruit = Fruit()
                    game_start_time = time.time()
                    last_fruit_spawn = game_start_time
                    special_fruit_spawned = {30: False, 60: False, 90: False}

        if not game_over and game_state == "playing":
            # AI移动逻辑
            ai_head = ai_snake.get_head()
            fruit_pos = fruit.position
            # 使用get_ai_move函数，并传入当前难度
            ai_direction = get_ai_move(ai_snake, fruit_pos, player_snake.body + ai_snake.body[1:], ai_difficulty)
            ai_snake.change_direction(ai_direction)

            # 移动蛇
            player_move_result = player_snake.move()
            ai_move_result = ai_snake.move()
            
            if not player_move_result or not ai_move_result:
                game_over = True
                game_state = "game_over"
                # 记录游戏结束时的时间和分数，避免后续更新
                final_game_time = game_time
                final_time_left = max(0, 120 - int(game_time))

            # 检查是否吃到果实
            for snake in [player_snake, ai_snake]:
                if snake.get_head() == fruit.position:
                    snake.grow()
                    snake.score += fruit.points
                    # 重用现有果实对象，而不是创建新对象
                    fruit.respawn(player_snake.body + ai_snake.body)
                    last_fruit_spawn = current_time

            # 特殊时间点的高分值果实 - 修复闪烁问题
            if 30 <= game_time < 31 and not special_fruit_spawned[30]:
                fruit = Fruit(3)
                fruit.respawn(player_snake.body + ai_snake.body)
                special_fruit_spawned[30] = True
            elif 60 <= game_time < 61 and not special_fruit_spawned[60]:
                fruit = Fruit(5)
                fruit.respawn(player_snake.body + ai_snake.body)
                special_fruit_spawned[60] = True
            elif 90 <= game_time < 91 and not special_fruit_spawned[90]:
                fruit = Fruit(10)
                fruit.respawn(player_snake.body + ai_snake.body)
                special_fruit_spawned[90] = True
            # 每10秒刷新一次普通果实
            elif current_time - last_fruit_spawn >= 10:
                fruit.respawn(player_snake.body + ai_snake.body)
                last_fruit_spawn = current_time

        # 绘制游戏界面
        screen.fill(WHITE)

        # 根据游戏状态绘制不同的界面
        if game_state == "menu":
            # 绘制标题
            title_text = "贪吃蛇大作战"
            title_surface = font.render(title_text, True, BLACK)
            title_rect = title_surface.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//4))
            screen.blit(title_surface, title_rect)
            
            # 绘制难度选择提示
            difficulty_text = "选择AI难度:"
            difficulty_surface = font.render(difficulty_text, True, BLACK)
            difficulty_rect = difficulty_surface.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2 - 50))
            screen.blit(difficulty_surface, difficulty_rect)
            
            # 绘制难度按钮
            pygame.draw.rect(screen, LIGHT_BLUE if ai_difficulty == "简单" else GRAY, easy_button, border_radius=5)
            pygame.draw.rect(screen, LIGHT_BLUE if ai_difficulty == "一般" else GRAY, normal_button, border_radius=5)
            pygame.draw.rect(screen, LIGHT_BLUE if ai_difficulty == "困难" else GRAY, hard_button, border_radius=5)
            pygame.draw.rect(screen, BLUE, start_button, border_radius=5)
            
            # 绘制按钮文字
            easy_text = small_font.render("简单", True, BLACK)
            normal_text = small_font.render("一般", True, BLACK)
            hard_text = small_font.render("困难", True, BLACK)
            start_text = small_font.render("开始", True, WHITE)
            
            easy_text_rect = easy_text.get_rect(center=easy_button.center)
            normal_text_rect = normal_text.get_rect(center=normal_button.center)
            hard_text_rect = hard_text.get_rect(center=hard_button.center)
            start_text_rect = start_text.get_rect(center=start_button.center)
            
            screen.blit(easy_text, easy_text_rect)
            screen.blit(normal_text, normal_text_rect)
            screen.blit(hard_text, hard_text_rect)
            screen.blit(start_text, start_text_rect)
        else:
            # 绘制游戏中的界面
            # 绘制网格
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    pygame.draw.rect(screen, GRAY, 
                                   (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

            # 绘制果实 - 使用圆形
            pygame.draw.circle(screen, YELLOW,
                            (fruit.position[0] * GRID_SIZE + GRID_SIZE // 2, 
                             fruit.position[1] * GRID_SIZE + GRID_SIZE // 2),
                             GRID_SIZE // 2 - 2)

            # 绘制蛇 - 使用圆角矩形
            for snake in [player_snake, ai_snake]:
                for segment in snake.body:
                    draw_rounded_rect(screen, snake.color,
                                   (segment[0] * GRID_SIZE + 1, segment[1] * GRID_SIZE + 1,
                                    GRID_SIZE - 2, GRID_SIZE - 2), 0.5)

            # 显示得分
            score_text = f'玩家: {player_snake.score}  AI: {ai_snake.score}'
            score_surface = font.render(score_text, True, BLACK)
            screen.blit(score_surface, (10, 10))

            # 显示剩余时间和当前难度
            if not game_over:
                time_left = max(0, 120 - int(game_time))
            else:
                time_left = final_time_left
            
            time_text = f'剩余时间: {time_left}秒  难度: {ai_difficulty}'
            time_surface = font.render(time_text, True, BLACK)
            time_rect = time_surface.get_rect()
            screen.blit(time_surface, (WINDOW_SIZE[0] - time_rect.width - 10, 10))

            # 如果游戏结束，显示结果
            if game_over:
                if player_snake.score > ai_snake.score:
                    result_text = "玩家获胜！"
                elif ai_snake.score > player_snake.score:
                    result_text = "AI获胜！"
                else:
                    result_text = "平局！"

                final_score = f"{result_text} 最终比分 - 玩家: {player_snake.score}  AI: {ai_snake.score}"
                result_surface = font.render(final_score, True, BLACK)
                result_rect = result_surface.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2))
                screen.blit(result_surface, result_rect)
                
                # 绘制继续和退出按钮
                pygame.draw.rect(screen, LIGHT_BLUE, continue_button, border_radius=5)
                pygame.draw.rect(screen, DARK_GRAY, exit_button, border_radius=5)
                
                continue_text = small_font.render("继续", True, WHITE)
                exit_text = small_font.render("退出", True, WHITE)
                
                continue_text_rect = continue_text.get_rect(center=continue_button.center)
                exit_text_rect = exit_text.get_rect(center=exit_button.center)
                
                screen.blit(continue_text, continue_text_rect)
                screen.blit(exit_text, exit_text_rect)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()