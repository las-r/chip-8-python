import os
import pygame
import winsound

# made by las-r on github
# v0.0.1

# doesnt fully work yet!

# pygame init
pygame.init()
clock = pygame.time.Clock()

inst = 0x00e0 # test

# beep tone
beep = pygame.mixer.Sound(os.path.join("sounds", "beep.wav"))
beep.set_volume(0.05)

# display settings
WIDTH, HEIGHT = 512, 256
PWIDTH, PHEIGHT = WIDTH // 64, HEIGHT // 32
ON = (255, 255, 255)
OFF = (0, 0, 0)
disp = [[False] * 64 for _ in range(32)]

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
FONT = [[0xF0, 0x90, 0x90, 0x90, 0xF0],
        [0x20, 0x60, 0x20, 0x20, 0x70],
        [0xF0, 0x10, 0xF0, 0x80, 0xF0],
        [0xF0, 0x10, 0xF0, 0x10, 0xF0],
        [0x90, 0x90, 0xF0, 0x10, 0x10],
        [0xF0, 0x80, 0xF0, 0x10, 0xF0],
        [0xF0, 0x80, 0xF0, 0x90, 0xF0],
        [0xF0, 0x10, 0x20, 0x40, 0x40],
        [0xF0, 0x90, 0xF0, 0x90, 0xF0],
        [0xF0, 0x90, 0xF0, 0x10, 0xF0],
        [0xF0, 0x90, 0xF0, 0x90, 0x90],
        [0xE0, 0x90, 0xE0, 0x90, 0xE0],
        [0xF0, 0x80, 0x80, 0x80, 0xF0],
        [0xE0, 0x90, 0x90, 0x90, 0xE0],
        [0xF0, 0x80, 0xF0, 0x80, 0xF0],
        [0xF0, 0x80, 0xF0, 0x80, 0x80]]
for i, char in enumerate(FONT):
        for j, byte in enumerate(char):
            ram[i * 5 + j] = byte

# read rom function
def loadRom(rom):
    global ram
    
    with open(rom, "rb") as f:
        romd = f.read()
        for i in range(len(romd)):
            ram[0x200 + i] = romd[i]

# execute instruction function
def execInst(inst):
    global pc, v, i, disp
    
    n1, n2, n3, n4 = list(f"{inst:04x}")
    n1 = int(n1, 16)
    n2 = int(n2, 16)
    n3 = int(n3, 16)
    n4 = int(n4, 16)
    
    # debug
    print(f"PC: {pc}  Opcode: {hex(inst)}")
    
    # increment pc
    pc += 2
    
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
                                    
        case 1:
            # jump
            pc = n4 + n3 * 16 + n2 * 256
            
        case 6:
            # set vx
            v[n2] = n4 + n3 * 16
            
        case 7:
            # add to vx
            v[n2] += n4 + n3 * 16
            
        case 10:
            # set i
            i = n4 + n3 * 16 + n2 * 256
            
        case 13:
            # draw
            x = v[n2] % 64
            y = v[n3] % 32
            h = n4
            v[0xf] = 0
            for row in range(h):
                spr = ram[i + row]
                for col in range(8):
                    if (spr >> (7 - col)) & 1:
                        dx = (x + col) % 64
                        dy = (y + row) % 32
                        if disp[dy][dx]:
                            v[0xf] = 1
                        disp[dy][dx] ^= True

# pygame screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CHIP-8 Emulator")

# load file
loadRom("2-ibm-logo.ch8")

# main loop
run = True
while run and pc < len(ram):
    # input
    for event in pygame.event.get():
        # quit event
        if event.type == pygame.QUIT:
            run = False
            
    # execute
    execInst((ram[pc] << 8) | ram[pc + 1])
            
    # update timers
    if dtime > 0:
        dtime -= 1
    if stime > 0:
        stime -= 1
        
    # st beep
    if stime:
        beep.play()
            
    # update screen
    screen.fill(OFF)
    for r, row in enumerate(disp):
        for c, pix in enumerate(row):
            if pix:
                pygame.draw.rect(screen, ON, pygame.Rect(c * PWIDTH, r * PHEIGHT, PWIDTH, PHEIGHT))
    
    # refresh rate
    pygame.display.flip()
    clock.tick(60)

# quit
pygame.quit()
