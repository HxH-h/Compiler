from VMachine.Instruction import INSTRUCTION
from Parse.Utils import is_number

# AST转机器码
class Generator:
    def __init__(self):
        self.code = []

    def generate_program(self , node: dict):
        for stmt in node['body']:
            self.generate(stmt)
        # 生成二进制文件
        self.generate_bin()
    def generate_BinaryExpression(self , node: dict):
        self.generate(node['left'])
        # 左部结果入栈
        self.code.append(INSTRUCTION.PUSH)
        # 右部结果在寄存器
        self.generate(node['right'])
        # 计算
        opCode = INSTRUCTION.getCode(node['operator'])
        self.code.append(opCode)

    def generate_NumericLiteral(self , node: dict):
        self.code.append(INSTRUCTION.IMM)
        # 将文本转为数字
        if is_number(node['value']):
            self.code.append(eval(node['value']))
        else:
            raise Exception('Invalid number cannot convert to Number')

    def generate(self , node: dict):
        match node['type']:
            case 'Program':
                self.generate_program(node)
            case 'BinaryExpression':
                self.generate_BinaryExpression(node)
            case 'NumericLiteral':
                self.generate_NumericLiteral(node)

    def generate_bin(self):
        with open('output.bin' , 'wb') as f:
            for i in self.code:
                f.write(i.to_bytes(1 , 'little'))


