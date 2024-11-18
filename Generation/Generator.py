from VMachine.Instruction import INSTRUCTION
from Parse.Utils import is_number , is_integer , has_parameter , get_parameter
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
        self.code.append(INSTRUCTION.EXIT)
        # 生成指令文件
        self.generate_code()
        # 生成二进制文件
        self.generate_bin()
    def generate_BinaryExpression(self , node: dict , env: Environment , inFunc: bool):
        self.generate(node['left'] , env , inFunc)
        # 左部结果入栈
        self.code.append(INSTRUCTION.PUSH)
        # 右部结果在寄存器
        self.generate(node['right'] , env , inFunc)
        # 计算
        opCode = INSTRUCTION.getCode(node['operator'])
        self.code.append(opCode)

    def generate_NumericLiteral(self , node: dict):
        # 将文本转为数字
        if is_number(node['value']):
            num = eval(node['value'])
            if is_integer(num):
                self.code.append(INSTRUCTION.IMM)
            else:
                self.code.append(INSTRUCTION.IMMF)
            self.code.append(num)
        else:
            raise Exception('Invalid number cannot convert to Number')

    # 处理变量声明
    def generate_Declaration(self , node: dict , env: Environment , inFunc: bool):
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
        if inFunc:
            self.code.append(INSTRUCTION.LEA)
        else:
            self.code.append(INSTRUCTION.PUSHIMM)
        self.code.append(add)
        self.code.append(INSTRUCTION.SLV)

    def generate_AssignExpression(self , node: dict , env: Environment , inFunc: bool):
        # 判断左值是否为变量
        if node['left']['type'] != 'Identifier':
            raise Exception('Invalid left value cannot assign value')
        # 赋值的变量可能来自外部环境 ， 递归查找
        if not env.find(node['left']['value']):
            raise Exception('Variable ' + node['left']['value'] +' not known')
        # 执行右部表达式
        self.generate(node['right'] , env , inFunc)
        # 获取变量地址
        add = env.findSymbol(node['left']['value'])
        if inFunc:
            self.code.append(INSTRUCTION.LEA)
        else:
            self.code.append(INSTRUCTION.PUSHIMM)
        self.code.append(add)
        self.code.append(INSTRUCTION.SLV)

    def generate_IFStatement(self , node: dict , env: Environment , inFunc: bool):
        # 执行条件表达式
        self.generate(node['condition'] , env , inFunc)
        # 判断条件 0则跳转
        self.code.append(INSTRUCTION.JZ)
        # 需要空出来一个位置用于确定跳转位置
        self.code.append(None)
        else_index = len(self.code) - 1
        # 执行if体
        self.generate(node['ifbody'] , env , inFunc)
        # 执行完if体需要跳过else部分
        self.code.append(INSTRUCTION.JMP)
        skip_else = len(self.code)
        self.code.append(skip_else + 1)
        # 跳过if体的位置
        self.code[else_index] = skip_else + 1
        # 查看有无else
        if 'elsebody' in node:
            self.generate(node['elsebody'] , env , inFunc)
            # 有else则需要更新 if中的跳转
            self.code[skip_else] = len(self.code)

    def generate_LoopStatement(self , node: dict , env: Environment , inFunc: bool):
        # 存储 执行 条件判断语句的 起始位置
        loop_index = len(self.code)
        # 执行条件表达式
        self.generate(node['condition'] , env , inFunc)
        # 0则跳转
        self.code.append(INSTRUCTION.JZ)
        # 需要空出来一个位置用于确定跳转位置
        self.code.append(None)
        skip_index = len(self.code) - 1
        # 执行循环体
        self.generate(node['body'] , env , inFunc)
        # 执行完再跳回判断处
        self.code.append(INSTRUCTION.JMP)
        self.code.append(loop_index)

        # 确定跳出循环的位置
        self.code[skip_index] = len(self.code)

    # 和处理program相同
    def generate_BlockStatement(self , node: dict , parent_env: Environment , inFunc: bool):
        # 块内块外 环境 不同 父子关系
        env = Environment(parent_env)
        for stmt in node['body']:
            self.generate(stmt , env , inFunc)


    # 处理变量引用
    def generate_Identifier(self , node: dict , env: Environment , inFunc: bool):
        # 获取变量名
        varible = node['value']
        # 表达式右值变量 递归查找
        if env.find(varible):
            # 获取变量地址
            add = env.findSymbol(varible)
            # 生成虚拟机指令 , 将值载入寄存器
            if inFunc:
                self.code.append(INSTRUCTION.LEA)
                self.code.append(add)
                self.code.append(INSTRUCTION.POP)
            else:
                self.code.append(INSTRUCTION.IMM)
                self.code.append(add)
            self.code.append(INSTRUCTION.RLV)

    # 处理函数定义
    def generate_FunctionDeclaration(self , node: dict , env: Environment):
        # 检测重名
        if env.has(node['name']):
            raise Exception('Function already declared')

        # 防止机器码顺序执行 无条件跳转过函数声明
        self.code.append(INSTRUCTION.JMP)
        start_index = len(self.code)
        self.code.append(None)
        # 注册函数
        env.addFunction(node['name'] , start_index + 1)

        # 设置函数内符号表 函数内局部变量基于bp指针 envrionment只起到符号表作用
        fun_env = Environment()
        # 参数在 bp 指针 下 相对地址为负
        for arg in node['args']:
            fun_env.addSymbol(arg)

        # 解析函数体
        for stmt in node['body']['body']:
            self.generate(stmt , fun_env , True)

        self.code[start_index] = len(self.code)

    # 处理函数调用
    def generate_CallExpression(self , node: dict , env: Environment , inFunc: bool):
        # 判断函数是否声明
        if not env.find(node['value']):
            raise Exception('Function ' + node['value'] + ' not known')

        # 开辟栈空间
        self.code.append(INSTRUCTION.ENT)
        self.code.append(len(node['args']))
        # 逐个传参
        for i in range(len(node['args'])):
            self.generate(node['args'][i] , env , inFunc)
            self.code.append(INSTRUCTION.LEA)
            self.code.append(-(i + 1))
            self.code.append(INSTRUCTION.SLV)
        # 调用函数
        self.code.append(INSTRUCTION.CALL)
        self.code.append(env.findSymbol(node['value']))

    # 处理函数返回
    def generate_ReturnStatement(self , node: dict , env: Environment):
        self.generate(node['ret'] , env , True)
        self.code.append(INSTRUCTION.RET)

    # 处理print函数
    def generate_PrintStatement(self , node: dict , env: Environment , inFunc: bool):
        # 解析每个函数并打印
        for arg in node['args']:
            self.generate(arg , env , inFunc)
            self.code.append(INSTRUCTION.PRINT)

    def generate(self , node: dict , env: Environment = None , inFunc: bool = False):
        match node['type']:
            case 'Program':
                self.generate_program(node)
            case 'BinaryExpression':
                self.generate_BinaryExpression(node , env , inFunc)
            case 'VariableDeclaration':
                self.generate_Declaration(node , env , inFunc)
            case 'AssignExpression':
                self.generate_AssignExpression(node , env , inFunc)
            case 'IfStatement':
                self.generate_IFStatement(node , env , inFunc)
            case 'LoopStatement':
                self.generate_LoopStatement(node , env , inFunc)
            case 'BlockStatement':
                self.generate_BlockStatement(node , env , inFunc)
            case 'FunctionDeclaration':
                self.generate_FunctionDeclaration(node , env)
            case 'CallExpression':
                self.generate_CallExpression(node , env , inFunc)
            case 'ReturnStatement':
                self.generate_ReturnStatement(node , env)
            case 'PrintStatement':
                self.generate_PrintStatement(node , env , inFunc)
            case 'NumericLiteral':
                self.generate_NumericLiteral(node)
            case 'Identifier':
                self.generate_Identifier(node , env , inFunc)


    def generate_bin(self):

        with open('output.bin' , 'wb') as f:
            length = len(self.code)
            i = 0
            while i < length:
                f.write(self.code[i].to_bytes(1, 'little' , signed=True))
                if has_parameter(self.code[i]):
                    f.write(get_parameter(self.code[i + 1]))
                    i += 1
                i += 1

    def generate_code(self):
        # 把一些丑陋的语句封装到函数里
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
                if has_parameter(self.code[i]):
                    f.write(get_parameter(i + 1) + '\n')
                    i += 1
                i += 1



