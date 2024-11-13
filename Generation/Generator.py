from VMachine.Instruction import INSTRUCTION
from Parse.Utils import is_number
from Generation.Environment import Environment
# AST转机器码
class Generator:
    def __init__(self):
        self.code = []
        self.env = Environment()

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

    # 处理变量声明
    def generate_Declaration(self , node: dict):
        # TODO 暂时只处理一个变量
        varible = node['child'][0]
        # 查找该变量是否存在
        if self.env.has(varible['name']):
            raise Exception('Variable already declared')
        add = self.env.addSymbol(varible['name'])
        # 生成虚拟机指令
        # 分配栈空间 ， 否则栈指针会回退
        self.code.append(INSTRUCTION.PUSH)
        # 查看是否分配初值
        if 'operator' in varible:
            self.generate(varible['right'])
        # 赋初值
        self.code.append(INSTRUCTION.PUSHIMM)
        self.code.append(add)
        self.code.append(INSTRUCTION.SLV)

    def generate_AssignExpression(self , node: dict):
        # 判断左值是否为变量
        if node['left']['type'] != 'Identifier':
            raise Exception('Invalid left value cannot assign value')
        # 判断该变量是否被声明过
        if not self.env.has(node['left']['value']):
            raise Exception('Variable not known')
        # 执行右部表达式
        self.generate(node['right'])
        # 获取变量地址
        add = self.env.getSymbol(node['left']['value'])
        self.code.append(INSTRUCTION.PUSHIMM)
        self.code.append(add)
        self.code.append(INSTRUCTION.SLV)


    # 处理变量引用
    def generate_Identifier(self , node: dict):
        # 获取变量名
        varible = node['value']
        # 查找变量是否存在
        if self.env.has(varible):
            # 获取变量地址
            add = self.env.getSymbol(varible)
            # 生成虚拟机指令 , 将值载入寄存器
            self.code.append(INSTRUCTION.IMM)
            self.code.append(add)
            self.code.append(INSTRUCTION.RLV)


    def generate(self , node: dict):
        match node['type']:
            case 'Program':
                self.generate_program(node)
            case 'BinaryExpression':
                self.generate_BinaryExpression(node)
            case 'VariableDeclaration':
                self.generate_Declaration(node)
            case 'AssignExpression':
                self.generate_AssignExpression(node)
            case 'NumericLiteral':
                self.generate_NumericLiteral(node)
            case 'Identifier':
                self.generate_Identifier(node)


    def generate_bin(self):
        with open('output.bin' , 'wb') as f:
            for i in self.code:
                # TODO 不能只存一个字节
                f.write(i.to_bytes(1 , 'little' , signed=True))


