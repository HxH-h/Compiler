from VMachine.Instruction import INSTRUCTION
from Parse.Utils import is_number
from Generation.Environment import Environment
# AST转机器码
class Generator:
    def __init__(self):
        self.code = []


    def generate_program(self , node: dict):
        # program 为 最外层 作为根环境
        env = Environment()

        for stmt in node['body']:
            self.generate(stmt , env)

        # 生成指令文件
        self.generate_code()
        # 生成二进制文件
        self.generate_bin()
    def generate_BinaryExpression(self , node: dict , env: Environment):
        self.generate(node['left'] , env)
        # 左部结果入栈
        self.code.append(INSTRUCTION.PUSH)
        # 右部结果在寄存器
        self.generate(node['right'] , env)
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
    def generate_Declaration(self , node: dict , env: Environment):
        # TODO 暂时只处理一个变量
        varible = node['child'][0]
        # 声明前 查找该变量是否存在 , 只在当前环境下查看 , 实现遮蔽的效果
        if env.has(varible['name']):
            raise Exception('Variable already declared')
        add = env.addSymbol(varible['name'])
        # 生成虚拟机指令
        # 分配栈空间 ， 否则栈指针会回退
        self.code.append(INSTRUCTION.PUSH)
        # 查看是否分配初值
        if 'operator' in varible:
            self.generate(varible['right'] , env)
        # 赋初值
        self.code.append(INSTRUCTION.PUSHIMM)
        self.code.append(add)
        self.code.append(INSTRUCTION.SLV)

    def generate_AssignExpression(self , node: dict , env: Environment):
        # 判断左值是否为变量
        if node['left']['type'] != 'Identifier':
            raise Exception('Invalid left value cannot assign value')
        # 赋值的变量可能来自外部环境 ， 递归查找
        if not env.find(node['left']['value']):
            raise Exception('Variable ' + node['left']['value'] +' not known')
        # 执行右部表达式
        self.generate(node['right'] , env)
        # 获取变量地址
        add = env.findSymbol(node['left']['value'])
        self.code.append(INSTRUCTION.PUSHIMM)
        self.code.append(add)
        self.code.append(INSTRUCTION.SLV)

    def generate_IFStatement(self , node: dict , env: Environment):
        # 执行条件表达式
        self.generate(node['condition'] , env)
        # 判断条件 0则跳转
        self.code.append(INSTRUCTION.JZ)
        # 需要空出来一个位置用于确定跳转位置
        self.code.append(None)
        else_index = len(self.code) - 1
        # 执行if体
        self.generate(node['ifbody'] , env)
        # 执行完if体需要跳过else部分
        self.code.append(INSTRUCTION.JMP)
        skip_else = len(self.code)
        self.code.append(skip_else + 1)
        # 跳过if体的位置
        self.code[else_index] = skip_else + 1
        # 查看有无else
        if 'elsebody' in node:
            self.generate(node['elsebody'] , env)
            # 有else则需要更新 if中的跳转
            self.code[skip_else] = len(self.code)

    def generate_LoopStatement(self , node: dict , env: Environment):
        # 存储 执行 条件判断语句的 起始位置
        loop_index = len(self.code)
        # 执行条件表达式
        self.generate(node['condition'] , env)
        # 0则跳转
        self.code.append(INSTRUCTION.JZ)
        # 需要空出来一个位置用于确定跳转位置
        self.code.append(None)
        skip_index = len(self.code) - 1
        # 执行循环体
        self.generate(node['body'] , env)
        # 执行完再跳回判断处
        self.code.append(INSTRUCTION.JMP)
        self.code.append(loop_index)

        # 确定跳出循环的位置
        self.code[skip_index] = len(self.code)

    # 和处理program相同
    def generate_BlockStatement(self , node: dict , parent_env: Environment):
        # 块内块外 环境 不同 父子关系
        env = Environment(parent_env)
        for stmt in node['body']:
            self.generate(stmt , env)


    # 处理变量引用
    def generate_Identifier(self , node: dict , env: Environment):
        # 获取变量名
        varible = node['value']
        # 表达式右值变量 递归查找
        if env.find(varible):
            # 获取变量地址
            add = env.findSymbol(varible)
            # 生成虚拟机指令 , 将值载入寄存器
            self.code.append(INSTRUCTION.IMM)
            self.code.append(add)
            self.code.append(INSTRUCTION.RLV)


    def generate(self , node: dict , env: Environment = None):
        match node['type']:
            case 'Program':
                self.generate_program(node)
            case 'BinaryExpression':
                self.generate_BinaryExpression(node , env)
            case 'VariableDeclaration':
                self.generate_Declaration(node , env)
            case 'AssignExpression':
                self.generate_AssignExpression(node , env)
            case 'IfStatement':
                self.generate_IFStatement(node , env)
            case 'LoopStatement':
                self.generate_LoopStatement(node , env)
            case 'BlockStatement':
                self.generate_BlockStatement(node , env)
            case 'NumericLiteral':
                self.generate_NumericLiteral(node)
            case 'Identifier':
                self.generate_Identifier(node , env)


    def generate_bin(self):
        with open('output.bin' , 'wb') as f:
            for i in self.code:
                # TODO 不能只存一个字节
                f.write(i.to_bytes(1 , 'little' , signed=True))

    def generate_code(self):
        # 把一些丑陋的语句封装到函数里
        def has_paramter(code):
            return code in ['IMM' , 'PUSHIMM' , 'JMP' , 'JZ' , 'JNZ']
        def get_code_name(index):
            return INSTRUCTION(self.code[index]).name
        def get_parameter(index):
            return str(self.code[index])

        with open('output.txt' , 'w') as f:
            lengh = len(self.code)
            i = 0
            while i < lengh:
                code = get_code_name(i)
                f.write(code + '\n')
                if has_paramter(code):
                    f.write(get_parameter(i + 1) + '\n')
                    i += 1
                i += 1




