from Instruction import INSTRUCTION
from ctypes import *
class Machine:
    def __init__(self , code):
        # 栈
        self._stack = [0] * 100
        # 栈指针
        self._sp = len(self._stack)
        # 栈基址
        self._bp = self._sp
        # 代码序列
        self._code = code
        self._pc = 0
        # 通用寄存器
        self._ax = None

    # 立即数 存储到寄存器中
    def imm(self, value):
        self._ax = value

    # 将寄存器 中 地址 中的值 放入寄存器
    def rlv(self):
        self._ax = self._stack[self._ax]

    # 将当前寄存器的值 赋予 栈顶地址
    def slv(self):
        p = self._stack[self._sp]
        self._stack[p] = self._ax
        self._sp += 1

    # 寄存器的值 入栈
    def push(self):
        self._sp -= 1
        self._stack[self._sp] = self._ax

    # 0则跳转
    def jz(self):
        self._pc = self._pc + 1 if self._ax else self._code[self._pc]
    # 非零跳转
    def jnz(self):
        self._pc = self._code[self._pc] if self._ax else self._pc + 1

    # 无条件跳转
    def jmp(self):
        self._pc = self._code[self._pc]

    # 运算符
    def operator(self, op):
        match op:
            case INSTRUCTION.ADD:
                self._ax += self._stack[self._sp]
            case INSTRUCTION.SUB:
                self._ax -= self._stack[self._sp]
            case INSTRUCTION.MUL:
                self._ax *= self._stack[self._sp]
            case INSTRUCTION.DIV:
                self._ax /= self._stack[self._sp]
            case INSTRUCTION.MOD:
                self._ax %= self._stack[self._sp]
            case INSTRUCTION.EDIV:
                self._ax //= self._stack[self._sp]
            case INSTRUCTION.EQ:
                self._ax = self._ax == self._stack[self._sp]
            case INSTRUCTION.NE:
                self._ax = self._ax != self._stack[self._sp]
            case INSTRUCTION.LE:
                self._ax = self._ax <= self._stack[self._sp]
            case INSTRUCTION.GE:
                self._ax = self._ax >= self._stack[self._sp]
            case INSTRUCTION.GREATER:
                self._ax = self._ax > self._stack[self._sp]
            case INSTRUCTION.LESS:
                self._ax = self._ax < self._stack[self._sp]
        self._sp += 1

    def dispatch(self , op):
        match op:
            case INSTRUCTION.IMM:
                self.imm(self._code[self._pc])
                self._pc += 1
            case INSTRUCTION.PUSH:
                self.push()
            case INSTRUCTION.SLV:
                self.slv()
            case INSTRUCTION.RLV:
                self.rlv()
            case INSTRUCTION.JMP:
                self.jmp()
            case INSTRUCTION.JZ:
                self.jz()
            case INSTRUCTION.JNZ:
                self.jnz()
            case o if INSTRUCTION.ADD <= o <= INSTRUCTION.GREATER:
                self.operator(op)


    # 运行程序
    # 栈顶元素为返回值
    def run(self):
        end = len(self._code)
        while self._pc < end:
            op = self._code[self._pc]
            # pc总是指向下一条指令
            self._pc += 1
            self.dispatch(op)
        return self._stack[self._sp]




if __name__ == '__main__':
    code = [
        INSTRUCTION.IMM, 15,
        INSTRUCTION.PUSH,
        INSTRUCTION.IMM, 1,
        INSTRUCTION.PUSH,

        INSTRUCTION.IMM, 98,
        INSTRUCTION.RLV,
        INSTRUCTION.PUSH,

        INSTRUCTION.IMM, 99,
        INSTRUCTION.RLV,

        INSTRUCTION.EQ,
        INSTRUCTION.JNZ, 29,

        INSTRUCTION.IMM, 98,
        INSTRUCTION.PUSH,
        INSTRUCTION.IMM, 98,
        INSTRUCTION.RLV,
        INSTRUCTION.PUSH,
        INSTRUCTION.IMM, 1,
        INSTRUCTION.ADD,
        INSTRUCTION.SLV,
        INSTRUCTION.JMP, 6,

        INSTRUCTION.IMM,98,
        INSTRUCTION.RLV,
        INSTRUCTION.PUSH,

    ]

    m = Machine(code)
    print(m.run())


