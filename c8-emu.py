import argparse
import os
import pygame
import random

# made by las-r on github
# v1.6

# pygame init
pygame.init()
clock = pygame.time.Clock()

# beep tone
beep = pygame.mixer.Sound(os.path.join("sounds", "beep.wav"))
beep.set_volume(0.05)

# behavior
LEGACYSHIFT = False
LEGACYOFFSJUMP = False
LEGACYSTORE = False
DEBUG = 0
HZ = 700

# display
WIDTH, HEIGHT = 512, 256
PWIDTH, PHEIGHT = WIDTH // 64, HEIGHT // 32
ON = (255, 255, 255)
OFF = (0, 0, 0)
disp = [[False] * 64 for _ in range(32)]

# keypad
keys = [False] * 16
keym = {
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 12,
    pygame.K_q: 4,
    pygame.K_w: 5,
    pygame.K_e: 6,
    pygame.K_r: 13,
    pygame.K_a: 7,
    pygame.K_s: 8,
    pygame.K_d: 9,
    pygame.K_f: 14,
    pygame.K_z: 10,
    pygame.K_x: 0,
    pygame.K_c: 11,
    pygame.K_v: 15
}

# memory
pc = 0x200
i = 0
ram = [0] * 4096
v = [0] * 16
stack = []

# timers
dtime = 0
stime = 0

# font
FONT = [[0xf0, 0x90, 0x90, 0x90, 0xf0],
        [0x20, 0x60, 0x20, 0x20, 0x70],
        [0xf0, 0x10, 0xf0, 0x80, 0xf0],
        [0xf0, 0x10, 0xf0, 0x10, 0xf0],
        [0x90, 0x90, 0xf0, 0x10, 0x10],
        [0xf0, 0x80, 0xf0, 0x10, 0xf0],
        [0xf0, 0x80, 0xf0, 0x90, 0xf0],
        [0xf0, 0x10, 0x20, 0x40, 0x40],
        [0xf0, 0x90, 0xf0, 0x90, 0xf0],
        [0xf0, 0x90, 0xf0, 0x10, 0xf0],
        [0xf0, 0x90, 0xf0, 0x90, 0x90],
        [0xe0, 0x90, 0xe0, 0x90, 0xe0],
        [0xf0, 0x80, 0x80, 0x80, 0xf0],
        [0xe0, 0x90, 0x90, 0x90, 0xe0],
        [0xf0, 0x80, 0xf0, 0x80, 0xf0],
        [0xf0, 0x80, 0xf0, 0x80, 0x80]]
for idx, char in enumerate(FONT):
        for j, byte in enumerate(char):
            ram[0x50 + idx * 5 + j] = byte
            
# update screen
def updScreen():
    screen.fill(OFF)
    for r, row in enumerate(disp):
        for c, pix in enumerate(row):
            if pix:
                pygame.draw.rect(screen, ON, pygame.Rect(c * PWIDTH, r * PHEIGHT, PWIDTH, PHEIGHT))
    pygame.display.flip()

# read rom function
def loadRom(rom):
    global ram
    
    with open(rom, "rb") as f:
        romd = f.read()
        for i in range(len(romd)):
            ram[0x200 + i] = romd[i]

# execute instruction function
def execInst(inst):
    global pc, v, i, disp, dtime, stime, keys
    
    n1, n2, n3, n4 = list(f"{inst:04x}")
    n1 = int(n1, 16)
    n2 = int(n2, 16)
    n3 = int(n3, 16)
    n4 = int(n4, 16)
    
    # debug
    if DEBUG in [1, 3]:
        print(f"PC: {pc}  Opcode: {hex(inst)}")
    
    # increment pc
    pc += 2
    
    # fetch and run instruction
    match n1:
        case 0:
            match n2:
                case 0:
                    match n3:
                        case 14:
                            match n4:
                                case 0: disp = [[False] * 64 for _ in range(32)]
                                case 14: pc = stack.pop() 
        case 1: pc = n4 + n3 * 16 + n2 * 256
        case 2:
            if len(stack) >= 16:
                print("Stack overflow!")
            else:
                stack.append(pc)
            pc = n4 + n3 * 16 + n2 * 256
        case 3:
            if v[n2] == n4 + n3 * 16:
                pc += 2
        case 4:
            if v[n2] != n4 + n3 * 16:
                pc += 2
        case 5:
            match n4:
                case 0:
                    if v[n2] == v[n3]:
                        pc += 2 
        case 6: v[n2] = (n4 + n3 * 16) & 255
        case 7: v[n2] = (v[n2] + (n3 * 16 + n4)) & 255
        case 8:
            match n4:
                case 0: v[n2] = v[n3]
                case 1: v[n2] = (v[n2] | v[n3]) & 255
                case 2: v[n2] = (v[n2] & v[n3]) & 255
                case 3: v[n2] = (v[n2] ^ v[n3]) & 255
                case 4:
                    result = v[n2] + v[n3]
                    v[15] = 1 if result > 255 else 0
                    v[n2] = result & 255
                case 5:
                    v[15] = 1 if v[n2] > v[n3] else 0
                    v[n2] = (v[n2] - v[n3]) & 255
                case 6:
                    if LEGACYSHIFT:
                        v[n2] = v[n3]
                    v[15] = v[n2] & 1
                    v[n2] = (v[n2] >> 1) & 255
                case 7:
                    v[15] = 1 if v[n3] > v[n2] else 0
                    v[n2] = (v[n3] - v[n2]) & 255
                case 14:
                    if LEGACYSHIFT:
                        v[n2] = v[n3]
                    v[15] = (v[n2] >> 7) & 1
                    v[n2] = (v[n2] << 1) & 255
        case 9:
            match n4:
                case 0:
                    if v[n2] != v[n3]:
                        pc += 2
        case 10:
            i = n4 + n3 * 16 + n2 * 256
        case 11:
            if LEGACYOFFSJUMP:
                pc = n4 + n3 * 16 + n2 * 256 + v[0]
            else:
                pc = n4 + n3 * 16 + v[n2]
        case 12: v[n2] = random.randint(0, 255) & (n4 + n3 * 16)
        case 13:
            x = v[n2] % 64
            y = v[n3] % 32
            h = n4
            v[0xf] = 0
            for row in range(h):
                if i + row < len(ram):
                    spr = ram[i + row]
                else:
                    spr = 0
                for col in range(8):
                    if (spr >> (7 - col)) & 1:
                        dx = (x + col) % 64
                        dy = (y + row) % 32
                        if disp[dy][dx]:
                            v[0xf] = 1
                        disp[dy][dx] ^= True
        case 14:
            match n3:
                case 9:
                    match n4:
                        case 14:
                            if keys[v[n2]]:
                                pc += 2
                case 10:
                    match n4:
                        case 1:
                            if not keys[v[n2]]:
                                pc += 2
        case 15:
            match n3:
                case 0:
                    match n4:
                        case 7: v[n2] = dtime
                        case 10:
                            waiting = True
                            while waiting:
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        exit()
                                    elif event.type == pygame.KEYDOWN:
                                        if event.key in keym:
                                            v[n2] = keym[event.key]
                                            waiting = False
                                    updScreen()
                case 1:
                    match n4:
                        case 5: dtime = v[n2]
                        case 8: stime = v[n2] 
                        case 14: i += v[n2]
                case 2:
                    match n4:
                        case 9: i = 0x50 + v[n2] * 5
                case 3:
                    match n4:
                        case 3:
                            ram[i] = v[n2] // 100
                            ram[i + 1] = (v[n2] % 100) // 10
                            ram[i + 2] = v[n2] % 10
                case 5:
                    match n4:
                        case 5:
                            for ivx in range(n2 + 1):
                                ram[i + ivx] = v[ivx]
                                if LEGACYSTORE:
                                    i += 1 
                case 6:
                    match n4:
                        case 5:
                            for ilx in range(n2 + 1):
                                v[ilx] = ram[i + ilx]
                                
# boot function
def boot():
    global DEBUG, LEGACYSHIFT, LEGACYOFFSJUMP, LEGACYSTORE, HZ
    global WIDTH, HEIGHT, PWIDTH, PHEIGHT, ON, OFF, screen

    # declare arguments
    parser = argparse.ArgumentParser(description="CHIP-8 Emulator")
    parser.add_argument("rom", help="Path to CHIP-8 ROM file")
    parser.add_argument("--debug", default=0, help="Debug level [1: execution, 2: keypad, 3: both] (default: 0)")
    parser.add_argument("--legacy-bit-shift", action="store_true", help="Use legacy bit shift behavior")
    parser.add_argument("--legacy-offset-jump", action="store_true", help="Use legacy offset jump behavior")
    parser.add_argument("--legacy-store", action="store_true", help="Use legacy memory store behavior")
    parser.add_argument("--hz", type=int, default=700, help="Instructions executed per second (default: 700)")
    parser.add_argument("--width", type=int, default=512, help="Display width in pixels (default: 512)")
    parser.add_argument("--height", type=int, default=256, help="Display height in pixels (default: 256)")
    parser.add_argument("--pixel-color-on", nargs=3, type=int, default=(255, 255, 255), help="Color of on pixels (default: (255, 255, 255))")
    parser.add_argument("--pixel-color-off", nargs=3, type=int, default=(0, 0, 0), help="Color of off pixels (default: (0, 0, 0))")
    args = parser.parse_args()

    # apply cl opts
    DEBUG = args.debug
    LEGACYSHIFT = args.legacy_bit_shift
    LEGACYOFFSJUMP = args.legacy_offset_jump
    LEGACYSTORE = args.legacy_store
    HZ = args.hz
    WIDTH = args.width
    HEIGHT = args.height
    ON = tuple(args.pixel_color_on)
    OFF = tuple(args.pixel_color_off)
    PWIDTH, PHEIGHT = WIDTH // 64, HEIGHT // 32

    # init display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CHIP-8 Emulator")

    # load rom
    loadRom(args.rom)

# boot  
boot()

# main loop
run = True
while run and pc < len(ram):
    # input
    for event in pygame.event.get():
        # quit event
        if event.type == pygame.QUIT:
            run = False
        
        # keys
        elif event.type == pygame.KEYDOWN:
            if event.key in keym:
                keys[keym[event.key]] = True
        elif event.type == pygame.KEYUP:
            if event.key in keym:
                keys[keym[event.key]] = False
        
    # execute
    for _ in range(HZ // 60):
        execInst((ram[pc] << 8) | ram[pc + 1])
    
    # debug
    if DEBUG in [2, 3]:
        print(f"Keys:")
        print(f"{keys[0]} {keys[1]} {keys[2]} {keys[3]}\n{keys[4]} {keys[5]} {keys[6]} {keys[7]}\n{keys[8]} {keys[9]} {keys[10]} {keys[11]}\n{keys[12]} {keys[13]} {keys[14]} {keys[15]}")
            
    # timers
    if dtime > 0:
        dtime -= 1
    if stime > 0:
        stime -= 1
    if stime:
        beep.play()
            
    # update screen
    updScreen()
    clock.tick(60)

# quit
pygame.quit()
