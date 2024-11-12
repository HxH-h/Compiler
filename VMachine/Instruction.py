from enum import IntEnum

class INSTRUCTION(IntEnum):
    # 操作栈和寄存器
    IMM = 0x01,
    RLV = 0x02,
    SLV = 0x03,
    PUSH = 0x04,
    # 运算符
    ADD = 0x06,
    SUB = 0x07,
    MUL = 0x08,
    DIV = 0x09,
    EDIV = 0x0A,
    MOD = 0x0B,
    # 比较
    EQ = 0x0C,
    NE = 0x0D,
    LE = 0x0E,
    GE = 0x0F,
    LESS = 0x10,
    GREATER = 0x11,
    # 分支
    JMP = 0x12,
    JZ = 0x13,
    JNZ = 0x14,













