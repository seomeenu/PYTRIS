import pygame
import sys
import time
import random
from copy import deepcopy

pygame.init()

screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PYTRIS")

clock = pygame.time.Clock()

dot_size = 24

dt = 1
last_time = time.time()

global_volume = 0.5
class Sound:
    def __init__(self, src, volume=0.5):
        self.sound = pygame.mixer.Sound(src)
        self.volume = volume
        self.sound.set_volume(self.volume * global_volume)
        
    def play(self):
        if self.sound.get_volume != self.volume * global_volume:
            self.sound.set_volume(self.volume * global_volume)
        self.sound.stop()
        self.sound.play()

move_sound = Sound("src/move.ogg")
hard_drop_sound = Sound("src/hard_drop.ogg")
line_clear_sound = Sound("src/line_clear.ogg")
hold_sound = Sound("src/hold.ogg")
rotate_sound = Sound("src/rotate.ogg", 0.3)
restart_sound = Sound("src/restart.ogg")
soft_drop_sound = Sound("src/soft_drop.ogg")
place_sound = Sound("src/place.ogg")

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

arr_timer = 0
das_timer = 0

arr_frames = 1.2
das_frames = 7
sdf_frames = 0.5

screen_offset = [screen_width/2-5*dot_size, screen_height/2-13*dot_size]

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
    for y, row in enumerate(block):
        for x, dot in enumerate(row):
            if dot != 0:
                y_index = y+pos[1]+movement[1]
                x_index = x+pos[0]+movement[0]
                if y_index < len(g.grid):
                    if 0 <= x_index < len(g.grid[y_index]):
                        if g.grid[y_index][x_index] != 0:
                            return False
                    else:
                        return False
                        
                else:
                    return False
    return True

def move(movement):
    if movement[1] == 0:
        move_sound.play()
        reset_lock_delay()
    g.current_block_pos[0] += movement[0]
    g.current_block_pos[1] += movement[1]

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
    if new_block_type == O_block:
        g.current_block_pos = [4, 0]
    if not can_move(new_block_type, g.current_block_pos, [0, 0]):
        reset()

    g.current_block = new_block_type
    g.current_block_type = new_block_type
    g.current_block_state = 0


def place_block():
    for y, row in enumerate(g.current_block):
        for x, dot in enumerate(row):
            if dot != 0:
                y_index = y+g.current_block_pos[1]
                x_index = x+g.current_block_pos[0]
                g.grid[y_index][x_index] = dot
                if y_index == 0:
                    reset()
                    return
    line_clear()
    summon_block()
    reset_lock_delay(force_reset=True)
    g.holded = False

def line_clear():
    for row in g.grid:
        clear = True
        for dot in row:
            if dot == 0:
                clear = False
        if clear:
            g.grid.remove(row)
            g.grid.insert(0, [0 for i in range(10)])
            line_clear_sound.play()

def hold():
    if not g.holded:
        if g.hold_block == None:
            g.hold_block = deepcopy(g.current_block_type)
            summon_block()
            hold_sound.play()
            g.holded = True
        else:
            temp_block = deepcopy(g.hold_block)
            g.hold_block = deepcopy(g.current_block_type)
            summon_block(deepcopy(temp_block))
            hold_sound.play()
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

    for offset in offset_pattern:
        real_offset = [offset[0], -offset[1]]
        if can_move(rotated_block, g.current_block_pos, real_offset):
            g.current_block_pos[0] += real_offset[0]
            g.current_block_pos[1] += real_offset[1]
            g.current_block = rotated_block
            g.current_block_state += rotation
            if g.current_block_state == -1:
                g.current_block_state = 3
            elif g.current_block_state == 4:
                g.current_block_state = 0
            rotate_sound.play()
            reset_lock_delay(rotating=True)
            break

lock_delay_limit = 6
def reset_lock_delay(rotating=False, force_reset=False):
    if g.lock_delay_started or not can_move(g.current_block, g.current_block_pos, [0, 1]):
        print(g.lock_delay_reset_times)
        if g.lock_delay_reset_times <= lock_delay_limit or force_reset:
            g.lock_delay_reset_times += 1
            
    if force_reset or (rotating and g.lock_delay_reset_times <= lock_delay_limit):
        g.lock_delay = 0
        g.lock_delay_started = False
        if force_reset:
            g.lock_delay_reset_times = 0

def set_lock_delay():
    if not g.lock_delay_started:
        g.lock_delay = 40
        g.lock_delay_started = True
    else:
        if g.lock_delay <= 0:
            reset_lock_delay(force_reset=True)
            place_block()

class Game:
    def __init__(self):
        self.bag_blocks = []
        self.hold_block = None
        self.holded = False

        self.grid = [
            [0 for i in range(10)] for i in range(22)
        ]

        self.current_block = I_block
        self.current_block_type = I_block
        self.current_block_state = 0
        self.current_block_pos = [0, 0]

        self.shadow_offset = [0, 0]

        self.lock_delay = 0
        self.lock_delay_started = False
        self.lock_delay_reset_times = 0

g:Game = None
def reset():
    global g
    g = Game()
    set_bag()
    summon_block()
    restart_sound.play()

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
                    move([1, 0])
                das_timer = das_frames
                arr_timer = 0
            if event.key == pygame.K_LEFT:
                if can_move(g.current_block, g.current_block_pos, [-1, 0]):
                    move([-1, 0])
                das_timer = das_frames
                arr_timer = 0
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
                    move([0, 1])
                place_block()
                hard_drop_sound.play()

    g.shadow_offset = deepcopy(g.current_block_pos)

    if keys[pygame.K_DOWN]:
        soft_drop_timer += dt
        if soft_drop_timer >= sdf_frames:
            while soft_drop_timer > 0:
                soft_drop_timer -= sdf_frames
                if can_move(g.current_block, g.current_block_pos, [0, 1]):
                    move([0, 1])
                    soft_drop_sound.play()
                    gravity_timer = 0
                else:
                    set_lock_delay()

    elif gravity_timer > 60:
        gravity_timer = 0
        if can_move(g.current_block, g.current_block_pos, [0, 1]):
            move([0, 1])
        else:
            set_lock_delay()
            
    gravity_timer += dt

    if g.lock_delay >= 0:
        g.lock_delay -= dt

    if das_timer >= 0:
        das_timer -= dt
    elif das_timer <= 0:
        if keys[pygame.K_RIGHT]:
            if arr_frames == 0:
                while can_move(g.current_block, g.current_block_pos, [1, 0]):
                    move([1, 0])
            else:
                while arr_timer > 0:
                    arr_timer -= arr_frames
                    if can_move(g.current_block, g.current_block_pos, [1, 0]):
                        move([1, 0])
        if keys[pygame.K_LEFT]:
            if arr_frames == 0:
                while can_move(g.current_block, g.current_block_pos, [-1, 0]):
                    move([-1, 0])
            else:
                while arr_timer > 0:
                    arr_timer -= arr_frames
                    if can_move(g.current_block, g.current_block_pos, [-1, 0]):
                        move([-1, 0])
        arr_timer += dt

    for y, row in enumerate(g.grid):
        for x, dot in enumerate(row):
            if dot == 0:
                if y >= 2:
                    pygame.draw.rect(screen, "#474C4E", [screen_offset[0]+x*dot_size, y*dot_size+screen_offset[1], dot_size, dot_size], int(dot_size/16))
            else:
                pygame.draw.rect(screen, dot, [screen_offset[0]+x*dot_size, y*dot_size+screen_offset[1], dot_size, dot_size])

    while can_move(g.current_block, g.shadow_offset, [0, 1]):
        g.shadow_offset[1] += 1
    for y, row in enumerate(g.current_block):
        for x, dot in enumerate(row):
            if dot != 0:
                if g.shadow_offset != g.current_block_pos:
                    dot_rect = pygame.Rect(screen_offset[0]+(g.shadow_offset[0]+x)*dot_size, (g.shadow_offset[1]+y)*dot_size+screen_offset[1], dot_size, dot_size)
                    pygame.draw.rect(screen, "#474C4E", dot_rect)

                dot_rect = pygame.Rect(screen_offset[0]+(g.current_block_pos[0]+x)*dot_size, (g.current_block_pos[1]+y)*dot_size+screen_offset[1], dot_size, dot_size)
                pygame.draw.rect(screen, dot, dot_rect)
    
    if g.hold_block:
        for y, row in enumerate(g.hold_block):
            for x, dot in enumerate(row):
                if dot != 0:
                    dot_rect = pygame.Rect(screen_offset[0]+x*dot_size-5*dot_size, dot_size*2+y*dot_size+screen_offset[1], dot_size, dot_size)
                    if g.holded:
                        pygame.draw.rect(screen, "#474C4E", dot_rect)
                    else:
                        pygame.draw.rect(screen, dot, dot_rect)

    for order, block in enumerate(g.bag_blocks[:5]):
        for y, row in enumerate(block):
            for x, dot in enumerate(row):
                if dot != 0:
                    dot_rect = pygame.Rect(screen_offset[0]+dot_size*12+x*dot_size, dot_size*2+order*dot_size*3+y*dot_size+screen_offset[1], dot_size, dot_size)
                    pygame.draw.rect(screen, dot, dot_rect)

    clock.tick(120)
    pygame.display.update()