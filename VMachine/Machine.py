import struct
from Parse.Utils import has_parameter
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

    # 函数调用
    def call(self):
        self._sp -= 1
        # 下一个pc指向call函数对应的地址
        # 下下个才是函数结束后的指令
        self._stack[self._sp] = self._pc + 1
        self._pc = self._code[self._pc]

    # 函数调用开辟栈空间
    def ent(self):
        # 开辟形参个数 个 栈空间 还有一个存 old bp
        self._sp -=  (self._code[self._pc] + 1)
        # 多出的一个存储old bp
        self._stack[self._sp] = self._bp
        self._bp = self._sp

    # 函数返回
    # 需要传入函数的参数个数 释放栈空间
    def ret(self):
        # 释放 局部变量 ,函数参数 ,old bp空间
        self._sp = self._bp + self._code[self._pc] + 1
        # pc指针返回
        self._pc = self._stack[self._bp - 1]
        # 恢复bp
        self._bp = self._stack[self._bp]

    # 基址指针相对位移 入栈
    def lea(self):
        self._sp -= 1
        self._stack[self._sp] = self._bp + self._code[self._pc]

    # print
    def print(self):
        print(self._ax)

    # exit
    def exit(self):
        print("process exit")
        exit()



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
            case INSTRUCTION.IMM | INSTRUCTION.IMMF:
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
            case INSTRUCTION.CALL:
                self.call()
            case INSTRUCTION.RET:
                self.ret()
            case INSTRUCTION.ENT:
                self.ent()
                self._pc += 1
            case INSTRUCTION.POP:
                self.pop()
            case INSTRUCTION.LEA:
                self.lea()
                self._pc += 1
            case INSTRUCTION.PRINT:
                self.print()
            case INSTRUCTION.EXIT:
                self.exit()
            case o if INSTRUCTION.ADD <= o <= INSTRUCTION.GREATER:
                self.operator(op)


    # 运行程序
    def run(self):
        while True:
            op = self._code[self._pc]
            # pc总是指向下一条指令
            self._pc += 1
            self.dispatch(op)


    # 读取二进制文件
    def read_bin(self , path):

        with open(path , 'rb') as f:
            size = os.path.getsize(path)
            i = 0
            while i < size:
                code = int.from_bytes(f.read(1) , byteorder='little' , signed=True)
                self._code.append(code)
                if has_parameter(code):
                    if code == INSTRUCTION.IMMF:
                        num = struct.unpack('<f' , f.read(4))[0]
                        self._code.append(num)
                    else:
                        num = int.from_bytes(f.read(4) , byteorder='little' , signed=True)
                        self._code.append(num)
                    i += 4
                i += 1










