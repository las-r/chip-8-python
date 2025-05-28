import os
import pygame
import random

# made by las-r on github
# v1.2

# doesnt fully work yet!

# pygame init
pygame.init()
clock = pygame.time.Clock()

# beep tone
beep = pygame.mixer.Sound(os.path.join("sounds", "beep.wav"))
beep.set_volume(0.05)

# behavior settings
LEGACYSHIFT = False
LEGACYOFFSJUMP = False
LEGACYSTORE = False
DEBUG = True
HZ = 700

# display settings
WIDTH, HEIGHT = 512, 256
PWIDTH, PHEIGHT = WIDTH // 64, HEIGHT // 32
ON = (255, 255, 255)
OFF = (0, 0, 0)
disp = [[False] * 64 for _ in range(32)]

# keyboard
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
    if DEBUG:
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
                                case 0:
                                    # clear screen
                                    disp = [[False] * 64 for _ in range(32)]
                                    
                                case 14:
                                    # return from subroutine
                                    pc = stack.pop()
                                    
        case 1:
            # jump
            pc = n4 + n3 * 16 + n2 * 256
            
        case 2:
            # jump to subroutine
            if len(stack) >= 16:
                print("Stack overflow!")
            else:
                stack.append(pc)
            pc = n4 + n3 * 16 + n2 * 256
            
        case 3:
            # skip inst if equal
            if v[n2] == n4 + n3 * 16:
                pc += 2
                
        case 4:
            # skip inst if not equal
            if v[n2] != n4 + n3 * 16:
                pc += 2
                
        case 5:
            match n4:
                case 0:
                    # skip inst if v equal
                    if v[n2] == v[n3]:
                        pc += 2
            
        case 6:
            # set vx
            v[n2] = (n4 + n3 * 16) & 255
            
        case 7:
            # add to vx
            v[n2] = (v[n2] + (n3 * 16 + n4)) & 255
            
        case 8:
            match n4:
                case 0:
                    # set
                    v[n2] = v[n3]

                case 1:
                    # or
                    v[n2] = (v[n2] | v[n3]) & 255

                case 2:
                    # and
                    v[n2] = (v[n2] & v[n3]) & 255

                case 3:
                    # xor
                    v[n2] = (v[n2] ^ v[n3]) & 255

                case 4:
                    # add
                    result = v[n2] + v[n3]
                    v[15] = 1 if result > 255 else 0
                    v[n2] = result & 255

                case 5:
                    # sub (vx - vy)
                    v[15] = 1 if v[n2] > v[n3] else 0
                    v[n2] = (v[n2] - v[n3]) & 255

                case 6:
                    # right shift
                    if LEGACYSHIFT:
                        v[n2] = v[n3]
                    v[15] = v[n2] & 1
                    v[n2] = (v[n2] >> 1) & 255

                case 7:
                    # sub (vy - vx)
                    v[15] = 1 if v[n3] > v[n2] else 0
                    v[n2] = (v[n3] - v[n2]) & 255

                case 14:
                    # left shift
                    if LEGACYSHIFT:
                        v[n2] = v[n3]
                    v[15] = (v[n2] >> 7) & 1
                    v[n2] = (v[n2] << 1) & 255
            
        case 9:
            match n4:
                case 0:
                    # skip inst if v not equal
                    if v[n2] != v[n3]:
                        pc += 2
            
        case 10:
            # set i
            i = n4 + n3 * 16 + n2 * 256
            
        case 11:
            # offset jump
            if LEGACYOFFSJUMP:
                pc = n4 + n3 * 16 + n2 * 256 + v[0]
            else:
                pc = n4 + n3 * 16 + v[n2]
                
        case 12:
            v[n2] = random.randint(0, 255) & (n4 + n3 * 16)
            
        case 13:
            # draw
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
                            # skip if key
                            if keys[v[n2]]:
                                pc += 2
                
                case 10:
                    match n4:
                        case 1:
                            # skip if not key
                            if not keys[v[n2]]:
                                pc += 2
                                
        case 15:
            match n3:
                case 0:
                    match n4:
                        case 7:
                            # set vx to dt
                            v[n2] = dtime
                            
                        case 10:
                            # get key (blocking wait)
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
                        case 5:
                            # set dt to vx
                            dtime = v[n2]
                            
                        case 8:
                            # set st to vx
                            stime = v[n2]
                            
                        case 14:
                            # i + vx
                            i += v[n2]
                            
                case 2:
                    match n4:
                        case 9:
                            # set i to font char
                            i = 0x50 + v[n2] * 5
                        
                case 3:
                    match n4:
                        case 3:
                            # decimal convert
                            ram[i] = v[n2] // 100
                            ram[i + 1] = (v[n2] % 100) // 10
                            ram[i + 2] = v[n2] % 10
                                
                case 5:
                    match n4:
                        case 5:
                            # store mem
                            for ivx in range(n2 + 1):
                                ram[i + ivx] = v[ivx]
                                if LEGACYSTORE:
                                    i += 1
                                    
                case 6:
                    match n4:
                        case 5:
                            # load mem
                            for ilx in range(n2 + 1):
                                v[ilx] = ram[i + ilx]

# pygame screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CHIP-8 Emulator")

# load file
loadRom("roms/pong.ch8")

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
    
    # keys debug
    if DEBUG:
        print(f"Keys: {keys}")
            
    # update timers
    if dtime > 0:
        dtime -= 1
    if stime > 0:
        stime -= 1
        
    # st beep
    if stime:
        beep.play()
            
    # update screen
    updScreen()
    
    # refresh rate
    os.system("cls" if os.name == "nt" else "clear")
    clock.tick(60)

# quit
pygame.quit()
