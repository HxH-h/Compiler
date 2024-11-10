from enum import Enum , auto

# 枚举
class TYPE(Enum):
    # 在此填写所有的token类型的枚举
    # auto() 自动分配一个值
    IDENTIFIER = auto()


class Lexer:

    # TODO 实现文件读取,优先相对路径
    # return str 返回值为字符串形式
    def read_file(self, filename) -> str:
        pass

    # TODO 实现词法分析
    # return list 返回值样式需要为[{},{},...]  即字典的列表，
    # 每个token是一个字典，{'type': TYPE, 'value': VALUE} , TYPE为枚举类型，VALUE为字符串值
    # 形如：{'type': IDENTIFIER, 'value': 'a'}
    def tokenize(self) -> list:
        pass