from enum import Enum , auto

# 枚举
class TYPE(Enum):
    # 在此填写所有的token类型的枚举
    # auto() 自动分配一个值
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    PLUS = auto()
    MINUS = auto()
    MULTI = auto()
    DIVIDE = auto()
    MOD = auto()
    EXDIV = auto()

    EQUAL = auto()
    NE = auto()
    LESS = auto()
    GREATER = auto()
    LE = auto()
    GE = auto()

    ASSIGN = auto()

    OR = auto()
    AND = auto()

    OPENPT = auto()
    CLOSEPT = auto()
    OPENBRACE = auto()
    CLOSEBRACE = auto()
    COMMA = auto()

    LET = auto()
    CONST = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FUNC = auto()


    EOF = auto()

class Token:
    def __init__(self, type, value :str = None):
        self.type = type
        self.value = value

class Lexer:

    # TODO 实现文件读取,优先相对路径
    # return str 返回值为字符串形式
    def read_file(self, filename) -> str:
        pass

    # TODO 实现词法分析
    # return list 返回值样式需要为即Token类的列表
    def tokenize(self) -> list:
        pass