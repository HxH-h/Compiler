from enum import IntEnum

class INSTRUCTION(IntEnum):
    # 操作栈和寄存器
    IMM = 0x01,
    IMMF = 0x02,

    RLV = 0x03,
    SLV = 0x04,
    PUSH = 0x05,
    PUSHIMM = 0x06,
    # 分支
    JMP = 0x07,
    JZ = 0x08,
    JNZ = 0x09,
    # 函数调用
    CALL = 0x0A,
    ENT = 0x0B,
    RET = 0x0C,
    LEA = 0x0D,
    POP = 0x0E,
    # 运算符
    ADD = 0x10,
    SUB = 0x11,
    MUL = 0x12,
    DIV = 0x13,
    EDIV = 0x14,
    MOD = 0x15,

    # 比较
    EQ = 0x16,
    NE = 0x17,
    LE = 0x18,
    GE = 0x19,
    LESS = 0x1A,
    GREATER = 0x1B,
    AND = 0x1C,
    OR = 0x1D,
    # 逻辑运算
    LAND = 0x1E,
    LOR = 0x1F,
    XOR = 0x20,
    SL = 0x21,
    SR = 0x22,


    # 内置函数
    PRINT = 0x30
    EXIT = 0x31
    INPUT = 0x32
    MALLOC = 0x33

    def getCode(operater: str) -> int:
        match operater:
            case '+':
                return INSTRUCTION.ADD
            case '-':
                return INSTRUCTION.SUB
            case '*':
                return INSTRUCTION.MUL
            case '/':
                return INSTRUCTION.DIV
            case '//':
                return INSTRUCTION.EDIV
            case '%':
                return INSTRUCTION.MOD
            case '==':
                return INSTRUCTION.EQ
            case '!=':
                return INSTRUCTION.NE
            case '<=':
                return INSTRUCTION.LE
            case '>=':
                return INSTRUCTION.GE
            case '<':
                return INSTRUCTION.LESS
            case '>':
                return INSTRUCTION.GREATER
            case '&&':
                return INSTRUCTION.AND
            case '||':
                return INSTRUCTION.OR
            case '&':
                return INSTRUCTION.LAND
            case '|':
                return INSTRUCTION.LOR
            case '^':
                return INSTRUCTION.XOR
            case '<<':
                return INSTRUCTION.SL
            case '>>':
                return INSTRUCTION.SR
            case '!':
                # 逻辑取反 直接跟0比较
                return INSTRUCTION.EQ

















