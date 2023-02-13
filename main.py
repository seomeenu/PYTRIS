import pygame
import sys
import time
import random
from copy import deepcopy

pygame.init()

screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))

clock = pygame.time.Clock()

dot_size = 24

dt = 1
last_time = time.time()

I_color = "#42AFE1"
I_block = [
    [0, 0, 0, 0],
    [I_color, I_color, I_color, I_color],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
]
J_color = "#1165B5"
J_block = [
    [J_color, 0, 0],
    [J_color, J_color, J_color],
    [0, 0, 0],
]
L_color = "#F38927"
L_block = [
    [0, 0, L_color],
    [L_color, L_color, L_color],
    [0, 0, 0],
]
O_color = "#F6D03C"
O_block = [
    [O_color, O_color],
    [O_color, O_color],
]
S_color = "#51B84D"
S_block = [
    [0, S_color, S_color],
    [S_color, S_color, 0],
    [0, 0, 0],
]
T_color = "#B94BC6"
T_block = [
    [0, T_color, 0],
    [T_color, T_color, T_color],
    [0, 0, 0],
]
Z_color = "#EB4F65"
Z_block = [
    [Z_color, Z_color, 0],
    [0, Z_color, Z_color],
    [0, 0, 0],
]

JLTSZ_blocks = [J_block, L_block, S_block, T_block, Z_block]
all_blocks = [I_block, J_block, L_block, O_block, S_block, T_block, Z_block]

soft_drop_timer = 0
gravity_timer = 0
gravity = 1

lock_delay_timer = 0
lock_delay_started = False

arr_timer = 0
das_timer = 0

arr_frames = 1
das_frames = 9
sdf_frames = 0.5

screen_offset = screen_width/2-5*dot_size

I_offsets = {
    "01": [( 0, 0),(-2, 0),(+1, 0),(-2,-1),(+1,+2)],
    "10": [( 0, 0),(+2, 0),(-1, 0),(+2,+1),(-1,-2)],
    "12": [( 0, 0),(-1, 0),(+2, 0),(-1,+2),(+2,-1)],
    "21": [( 0, 0),(+1, 0),(-2, 0),(+1,-2),(-2,+1)],
    "23": [( 0, 0),(+2, 0),(-1, 0),(+2,+1),(-1,-2)],
    "32": [( 0, 0),(-2, 0),(+1, 0),(-2,-1),(+1,+2)],
    "30": [( 0, 0),(+1, 0),(-2, 0),(+1,-2),(-2,+1)],
    "03": [( 0, 0),(-1, 0),(+2, 0),(-1,+2),(+2,-1)],
    "00": [(0, 0)],
    "11": [(0, 0)],
    "22": [(0, 0)],
    "33": [(0, 0)]
}

JLTSZ_offsets = {
    "01": [( 0, 0),(-1, 0),(-1,+1),( 0,-2),(-1,-2)],
    "10": [( 0, 0),(+1, 0),(+1,-1),( 0,+2),(+1,+2)],
    "12": [( 0, 0),(+1, 0),(+1,-1),( 0,+2),(+1,+2)],
    "21": [( 0, 0),(-1, 0),(-1,+1),( 0,-2),(-1,-2)],
    "23": [( 0, 0),(+1, 0),(+1,+1),( 0,-2),(+1,-2)],
    "32": [( 0, 0),(-1, 0),(-1,-1),( 0,+2),(-1,+2)],
    "30": [( 0, 0),(-1, 0),(-1,-1),( 0,+2),(-1,+2)],
    "03": [( 0, 0),(+1, 0),(+1,+1),( 0,-2),(+1,-2)],
    "00": [(0, 0)],
    "11": [(0, 0)],
    "22": [(0, 0)],
    "33": [(0, 0)]
}
 
def can_move(block, pos, movement):
# def check_collision(block, pos, movement, placement=True):
    for y, row in enumerate(block):
        for x, dot in enumerate(row):
            if dot != 0:
                y_index = y+pos[1]+movement[1]
                x_index = x+pos[0]+movement[0]
                if y_index < len(g.grid):
                    if 0 <= x_index < len(g.grid[y_index]):
                        if g.grid[y_index][x_index] != 0:
                            # if movement[1] > 0:
                            #     place_block()
                            return False
                    else:
                        return False
                        
                else:
                    # if placement == True:
                    #     place_block()
                    return False
    return True

def set_bag():
    random_blocks = deepcopy(all_blocks)
    random.shuffle(random_blocks)
    g.bag_blocks+=random_blocks

def summon_block(block=None):
    if block:
        new_block_type = block
    else:
        new_block_type = g.bag_blocks.pop(0)
    if len(g.bag_blocks) == 4:
        set_bag()

    g.current_block_pos = [3, 0]
    g.current_block = new_block_type
    g.current_block_type = new_block_type
    g.current_block_state = 0


def place_block():
# if lock_delay_timer <= 0:
    for y, row in enumerate(g.current_block):
        for x, dot in enumerate(row):
            if dot != 0:
                y_index = y+g.current_block_pos[1]
                x_index = x+g.current_block_pos[0]
                g.grid[y_index][x_index] = dot
                # print(y_index, x_index)
    line_clear()
    summon_block()
    g.holded = False
    # lock_delay_timer = 0

def line_clear():
    for row in g.grid:
        clear = True
        for dot in row:
            if dot == 0:
                clear = False
        if clear:
            g.grid.remove(row)
            g.grid.insert(0, [0 for i in range(10)])

def hold():
    if not g.holded:
        if g.hold_block == None:
            g.hold_block = deepcopy(g.current_block)
            summon_block()
            g.holded = True
        else:
            temp_block = deepcopy(g.hold_block)
            g.hold_block = deepcopy(g.current_block)
            summon_block(deepcopy(temp_block))
            g.holded = True

def rotate(rotation=1):
    if rotation == 1:
        rotated_block = list(zip(*g.current_block[::-1]))
    elif rotation == -1:
        rotated_block = list(reversed(list(zip(*g.current_block))))
    elif rotation == 0:
        rotated_block = list(zip(*g.current_block[::-1]))
        rotated_block = list(zip(*rotated_block[::-1]))

    offset_pattern = I_offsets["01"]
    
    temp_state = g.current_block_state
    temp_state += rotation
    if temp_state == -1:
        temp_state = 3
    elif temp_state == 4:
        temp_state = 0
        
    if g.current_block_type == I_block:
        offset_pattern = I_offsets[f"{g.current_block_state}{temp_state}"]
    elif g.current_block_type in JLTSZ_blocks:
        offset_pattern = JLTSZ_offsets[f"{g.current_block_state}{temp_state}"]
    elif g.current_block_type == O_block:
        offset_pattern = [[0, 0]]

    # print(f"{g.current_block_state}{temp_state}")
    for offset in offset_pattern:
        real_offset = [offset[0], -offset[1]]
        if can_move(rotated_block, g.current_block_pos, real_offset):
            # print(offset)
        # if check_collision(rotated_block, current_block_pos, offset, placement=False):
            g.current_block_pos[0] += real_offset[0]
            g.current_block_pos[1] += real_offset[1]
            g.current_block = rotated_block
            g.current_block_state += rotation
            if g.current_block_state == -1:
                g.current_block_state = 3
            elif g.current_block_state == 4:
                g.current_block_state = 0
            # print(offset)
            break

class Game:
    def __init__(self):
        self.bag_blocks = []
        self.hold_block = None
        self.holded = False

        self.grid = [
            [0 for i in range(10)] for i in range(22)
        ]
        # for i in grid:
        #     print(i)

        self.current_block = I_block
        self.current_block_type = I_block
        self.current_block_state = 0
        self.current_block_pos = [0, 0]

        self.shadow_offset = [0, 0]
            
g:Game = None
def reset():
    global g
    g = Game()
    set_bag()
    summon_block()

reset()

while True:
    dt = time.time() - last_time
    dt *= 60
    last_time = time.time()

    screen.fill("#2D3132")
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if can_move(g.current_block, g.current_block_pos, [1, 0]):
                    g.current_block_pos[0] += 1
                das_timer = das_frames
                arr_timer = 0
            if event.key == pygame.K_LEFT:
                if can_move(g.current_block, g.current_block_pos, [-1, 0]):
                    g.current_block_pos[0] -= 1
                das_timer = das_frames
                arr_timer = 0
            # if event.key == pygame.K_DOWN:
            #     if check_collision(g.current_block, g.current_block_pos, [0, 1]):
            #         g.current_block_pos[1] += 1
            if event.key == pygame.K_UP:
                rotate()
            if event.key == pygame.K_LCTRL:
                rotate(-1)
            if event.key == pygame.K_a:
                rotate(0)
            if event.key == pygame.K_LSHIFT:
                hold()
            if event.key == pygame.K_r:
                reset()
            if event.key == pygame.K_SPACE:
                while can_move(g.current_block, g.current_block_pos, [0, 1]):
                    g.current_block_pos[1] += 1
                place_block()
        # if event.type == pygame.KEYUP:
        #     if event.key == pygame.K_RIGHT:
        #         das_timer = 0
        #     if event.key == pygame.K_LEFT:
        #         das_timer = 0

    g.shadow_offset = deepcopy(g.current_block_pos)

    if keys[pygame.K_DOWN]:
        soft_drop_timer += dt
        if soft_drop_timer >= sdf_frames:
            while soft_drop_timer > 0:
                soft_drop_timer -= sdf_frames
                if can_move(g.current_block, g.current_block_pos, [0, 1]):
                # if check_collision(g.current_block, g.current_block_pos, [0, 1], placement=False):
                    g.current_block_pos[1] += 1
                    gravity_timer = 0
                else:
                    if not lock_delay_started:
                        lock_delay_timer = 30
                        lock_delay_started = True
                    elif lock_delay_timer <= 0:
                        place_block()
                        lock_delay_started = False
                    # soft_drop_timer = 0

    elif gravity_timer > 60:
        gravity_timer = 0
        if can_move(g.current_block, g.current_block_pos, [0, 1]):
            g.current_block_pos[1] += 1
        else:
            place_block()
    gravity_timer += dt
    
    if not keys[pygame.K_DOWN]:
        lock_delay_started = False
        lock_delay_timer = 0
    # if arr_timer >= 0:
    #     arr_timer -= dt

    if das_timer >= 0:
        das_timer -= dt
    elif das_timer <= 0:
        if keys[pygame.K_RIGHT]:
            while arr_timer > 0:
                arr_timer -= arr_frames
                if can_move(g.current_block, g.current_block_pos, [1, 0]):
                    g.current_block_pos[0] += 1
        if keys[pygame.K_LEFT]:
            while arr_timer > 0:
                arr_timer -= arr_frames
                if can_move(g.current_block, g.current_block_pos, [-1, 0]):
                    g.current_block_pos[0] -= 1
        arr_timer += dt

    if lock_delay_timer >= 0:
        lock_delay_timer -= dt

    for y, row in enumerate(g.grid):
        for x, dot in enumerate(row):
            if dot == 0:
                if y >= 2:
                    pygame.draw.rect(screen, "#474C4E", [screen_offset+x*dot_size, y*dot_size, dot_size, dot_size], int(dot_size/16))
            else:
                pygame.draw.rect(screen, dot, [screen_offset+x*dot_size, y*dot_size, dot_size, dot_size])

    while can_move(g.current_block, g.shadow_offset, [0, 1]):
        g.shadow_offset[1] += 1
    for y, row in enumerate(g.current_block):
        for x, dot in enumerate(row):
            if dot != 0:
                dot_rect = pygame.Rect(screen_offset+(g.shadow_offset[0]+x)*dot_size, (g.shadow_offset[1]+y)*dot_size, dot_size, dot_size)
                pygame.draw.rect(screen, "#474C4E", dot_rect)

                dot_rect = pygame.Rect(screen_offset+(g.current_block_pos[0]+x)*dot_size, (g.current_block_pos[1]+y)*dot_size, dot_size, dot_size)
                pygame.draw.rect(screen, dot, dot_rect)
    
    if g.hold_block:
        for y, row in enumerate(g.hold_block):
            for x, dot in enumerate(row):
                if dot != 0:
                    dot_rect = pygame.Rect(screen_offset+x*dot_size-5*dot_size, dot_size*2+y*dot_size, dot_size, dot_size)
                    if g.holded:
                        pygame.draw.rect(screen, "#474C4E", dot_rect)
                    else:
                        pygame.draw.rect(screen, dot, dot_rect)

    for order, block in enumerate(g.bag_blocks[:5]):
        for y, row in enumerate(block):
            for x, dot in enumerate(row):
                if dot != 0:
                    dot_rect = pygame.Rect(screen_offset+dot_size*12+x*dot_size, dot_size*2+order*dot_size*3+y*dot_size, dot_size, dot_size)
                    pygame.draw.rect(screen, dot, dot_rect)

    clock.tick(120)
    pygame.display.update()