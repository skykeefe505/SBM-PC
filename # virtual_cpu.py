import os

#dir stuff for drives
current_dir = os.path.dirname(os.path.abspath(__file__))


#hope this is fun!
#sky 2025

#map memory to output to console
MMIO_CONSOLE = 0x1000

#cpu info
class CPU:
    def __init__(self):
        self.regs = [0] * 32 #32-bit for display regs
        self.pc = 0
        self.running = True

#memory stuff
memory = bytearray(16 * 1024 * 1024)

cpu = CPU()

#op cmds
OP_MOV = 1
OP_OUT = 2
OP_HALT = 3
OP_LOAD = 4
OP_STORE = 5
OP_JMP = 6

#display stuff
cursor_x = 0
cursor_y = 5
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 25
display_buffer = [[' ' for _ in range(SCREEN_WIDTH)] for _ in range(SCREEN_HEIGHT)]
line_buffers = {}
for r in range(5, 31):
    line_buffers[r] = []

#drive stuff
drive_names = {
    0: os.path.join(current_dir, "d.sbm")
}

#op encoding
def instr(op, reg=0, imm=0):
    return (op << 24) | (reg << 16) | (imm & 0xFFFF)

#define functions
def mmio_write(addr, value, line_reg=None):
    global cursor_x, cursor_y  # <--- this is required
    if addr == MMIO_CONSOLE:
        reg = line_reg if line_reg is not None else cursor_y
        line_buffers[reg].append(chr(value))
        cursor_x += 1
        if cursor_x >= SCREEN_WIDTH:
            cursor_x = 0
            cursor_y += 1
            if cursor_y >= 30:
                cursor_y = 5

            
def fetch():
    instr_word = int.from_bytes(memory[cpu.pc:cpu.pc+4], "little")
    cpu.pc += 4
    return instr_word

def execute(instr_word):
    op = (instr_word >> 24) & 0xFF
    reg = (instr_word >> 16) & 0xFF
    imm = instr_word &  0xFFFF

    if op == OP_MOV:
        cpu.regs[reg] = imm
    elif op == OP_OUT:
        mmio_write(MMIO_CONSOLE, imm & 0xFF, reg + 5)
    elif op == OP_HALT:
        cpu.running = False
    elif op == OP_LOAD:
        filename = drive_names.get(imm, None)
        if filename is None:
            print(f"NF")
            cpu.running = False
            return
        addr = cpu.regs[reg]
        try:
            with open(filename, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
                for mem_index, line in enumerate(lines):
                    word = eval(line, {
    "instr": instr,
    "OP_MOV": OP_MOV,
    "OP_OUT": OP_OUT,
    "OP_HALT": OP_HALT,
    "MMIO_CONSOLE": MMIO_CONSOLE
})

                    memory[addr + mem_index*4 : addr + mem_index*4 + 4] = word.to_bytes(4, "little")
        except FileNotFoundError:
                print(f"NF")
                cpu.running = False
    elif op == OP_STORE:
        filename = drive_names.get(imm, None)
        if filename is None:
            print(f"NF")
            cpu.running = False
            return
        addr = cpu.regs[reg]
        N = 16
        program = [int.from_bytes(memory[addr+i*4:addr+i*4+4], "little") for i in range(N)]
        drive[filename] = program
    elif op == OP_JMP:
        cpu.pc = cpu.regs[reg]
    else:
        print(f"Unk OPcode")
        cpu.running = False

def load_program(program):
    start = 0x00000000
    for i, word in enumerate(program):
        memory[start + i*4 : start + i*4+4] = word.to_bytes(4, "little")
    cpu.pc = start

#the display is so painful to make kill me
def render_display():
    for r in range(5, 31):
        line = ''.join(line_buffers[r])
        print(line.ljust(SCREEN_WIDTH))
        
#BIOS
program = [
    instr(OP_MOV, 1, 0x100),
    instr(OP_LOAD, 1, 0),
    instr(OP_JMP, 1),
    instr(OP_HALT)
]

def main():
    load_program(program)
    while cpu.running:
        instr_word = fetch()
        execute(instr_word)
    print("\n[HLT]")
    render_display()

if __name__ == "__main__":
    main()
