from VMachine.Instruction import INSTRUCTION
import os
class Machine:
    def __init__(self , path):
        # 栈
        self._stack = [0] * 100
        # 栈指针
        self._sp = len(self._stack)
        # 栈基址
        self._bp = self._sp
        # 代码序列
        self._code = []
        # 读取二进制序列
        self.read_bin(path)
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

    # 弹出栈 赋给寄存器
    def pop(self):
        self._ax = self._stack[self._sp]
        self._sp += 1
    #  立即数 入栈
    def pushimm(self, value):
        self._sp -= 1
        self._stack[self._sp] = value

    # 0则跳转
    def jz(self):
        self._pc = self._pc + 1 if self._ax else self._code[self._pc]
    # 非零跳转
    def jnz(self):
        self._pc = self._code[self._pc] if self._ax else self._pc + 1

    # 无条件跳转
    def jmp(self):
        self._pc = self._code[self._pc]

    # 打印寄存器的值
    def print(self):
        print(self._ax)

    # 运算符
    def operator(self, op):
        match op:
            case INSTRUCTION.ADD:
                self._ax = self._stack[self._sp] + self._ax
            case INSTRUCTION.SUB:
                self._ax = self._stack[self._sp] - self._ax
            case INSTRUCTION.MUL:
                self._ax = self._stack[self._sp] * self._ax
            case INSTRUCTION.DIV:
                self._ax = self._stack[self._sp] / self._ax
            case INSTRUCTION.MOD:
                self._ax = self._stack[self._sp] % self._ax
            case INSTRUCTION.EDIV:
                self._ax = self._stack[self._sp] // self._ax
            case INSTRUCTION.EQ:
                self._ax = self._stack[self._sp] == self._ax
            case INSTRUCTION.NE:
                self._ax = self._stack[self._sp] != self._ax
            case INSTRUCTION.LE:
                self._ax = self._stack[self._sp] <= self._ax
            case INSTRUCTION.GE:
                self._ax = self._stack[self._sp] >= self._ax
            case INSTRUCTION.LESS:
                self._ax = self._stack[self._sp] < self._ax
            case INSTRUCTION.GREATER:
                self._ax = self._stack[self._sp] > self._ax
        self._sp += 1

    def dispatch(self , op):
        match op:
            case INSTRUCTION.IMM:
                self.imm(self._code[self._pc])
                self._pc += 1
            case INSTRUCTION.PUSH:
                self.push()
            case INSTRUCTION.PUSHIMM:
                self.pushimm(self._code[self._pc])
                self._pc += 1
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
            case INSTRUCTION.PRINT:
                self.print()
            case o if INSTRUCTION.ADD <= o <= INSTRUCTION.GREATER:
                self.operator(op)


    # 运行程序
    # AX寄存器为返回值
    def run(self):
        end = len(self._code)
        while self._pc < end:
            op = self._code[self._pc]
            # pc总是指向下一条指令
            self._pc += 1
            self.dispatch(op)
        return self._ax

    # 读取二进制文件
    def read_bin(self , path):
        with open(path , 'rb') as f:
            size = os.path.getsize(path)
            for i in range(size):
                self._code.append(int.from_bytes(f.read(1) , byteorder='little' , signed=True))

    # TODO 测试完删除
    def getCode(self):
        return self._code






