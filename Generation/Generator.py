import sys

from Parse.Utils import *
from Generation.Environment import Environment

# AST转机器码
class Generator:
    def __init__(self , path , generateCode , generateBin):
        self.code = []
        self.generateCode = generateCode
        self.generateBin = generateBin
        # 查看是否需要生成文件 并设置默认的文件名
        if generateCode:
            if generateCode is True:
                self.generateCode = path + '.txt'
        if generateBin:
            if generateBin is True:
                self.generateBin = path + '.bin'

    # 解析语法树最外层
    def generate_program(self , node: dict):
        # program 为 最外层 作为根环境
        env = Environment()

        # 遍历语法树
        for stmt in node['body']:
            self.generate(stmt , env)
        self.code.append(INSTRUCTION.EXIT)
        if self.generateCode:
            # 生成机器码
            self.generate_code()
        if self.generateBin:
            # 生成二进制文件
            self.generate_bin()

    # 处理二元表达式
    def generate_BinaryExpression(self , node: dict , env: Environment , inFunc: bool):
        self.generate(node['left'] , env , inFunc)
        # 左部结果入栈
        self.code.append(INSTRUCTION.PUSH)
        # 右部结果在寄存器
        self.generate(node['right'] , env , inFunc)
        # 计算
        opCode = INSTRUCTION.getCode(node['operator'])
        self.code.append(opCode)

    # 处理一元表达式 - 和 ！
    def generate_SingleExpression(self , node: dict , env: Environment , inFunc: bool):
        self.code.append(INSTRUCTION.PUSHIMM)
        self.code.append(0)
        self.generate(node['right'] , env , inFunc)
        opCode = INSTRUCTION.getCode(node['value'])
        self.code.append(opCode)
    # 处理数字
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
            self.error('Invalid number cannot convert to Number')

    # 处理变量声明
    def generate_Declaration(self , node: dict , env: Environment , inFunc: bool):
        # 只处理一个变量
        varible = node['child'][0]
        # 声明前 查找该变量是否存在 , 只在当前环境下查看 , 实现遮蔽的效果
        if env.has(varible['name']):
            self.error('Variable already declared')

        # 查看是否为常量
        if varible['isConstant']:
            add = env.addSymbol(varible['name'] , 'const')
            # 判断是否赋值
            if not 'operator' in varible:
                self.error('Constant must be initialized')
        else:
            add = env.addSymbol(varible['name'])

        # 生成虚拟机指令
        # 分配栈空间 ， 否则栈指针会回退
        self.code.append(INSTRUCTION.PUSH)
        # 查看是否分配初值
        if 'operator' in varible:
            self.generate(varible['right'] , env , inFunc)
        # 赋初值
        if inFunc:
            self.code.append(INSTRUCTION.LEA)
        else:
            self.code.append(INSTRUCTION.PUSHIMM)
        self.code.append(add)
        self.code.append(INSTRUCTION.SLV)

    # 处理数组定义
    def generate_Array_Declaration(self , node: dict , env: Environment , inFunc: bool):
        # 检查重名
        if env.has(node['name']):
             self.error('Variable already declared')
        # 获取地址
        add = env.addSymbol(node['name'] , 'array')
        # 分配空间
        if node['size']['type'] != 'NumericLiteral':
            self.error('Invalid array size')

        self.generate(node['size'] , env , inFunc)
        # 确保是整数
        size = int(self.code[len(self.code) - 1])
        self.code[len(self.code) - 1] = size
        self.code.append(INSTRUCTION.MALLOC)
        # 符号表要占位
        for i in range(size - 1):
            env.addSymbol(str(i) + node['name'] , 'array')
        # 查看是否分配初值
        if 'member' in node:
            # 检查成员数量书否超过分配值
            cnt = len(node['member'])
            if size < cnt:
                self.error('Too many initializers')
            for i in range(cnt):
                # 赋初值
                self.generate(node['member'][i] , env , inFunc)
                # 赋值
                if inFunc:
                    self.code.append(INSTRUCTION.LEA)
                else:
                    self.code.append(INSTRUCTION.PUSHIMM)
                self.code.append(add)
                add -= 1
                self.code.append(INSTRUCTION.SLV)

    # 处理数组引用
    def generate_array(self , node: dict , env: Environment , inFunc: bool):
        name = node['value']
        if env.find(name):
            sym = env.findSymbol(name)
            # 判断是否为数组
            if sym['type'] != 'array':
                self.error('Variable ' + name + ' is not array')
            # 处理偏移
            self.generate(node['offset'] , env , inFunc)
            if inFunc:
                self.code.append(INSTRUCTION.LEA)
            else:
                self.code.append(INSTRUCTION.PUSHIMM)
            self.code.append(sym['address'])
            self.code.append(INSTRUCTION.SUB)
            self.code.append(INSTRUCTION.RLV)

    def generate_AssignExpression(self , node: dict , env: Environment , inFunc: bool):
        # 判断左值是否为变量
        if node['left']['type'] != 'Identifier' and node['left']['type'] != 'ArrayMember':
            self.error('Invalid left value cannot assign value')
        # 赋值的变量可能来自外部环境 ， 递归查找
        if not env.find(node['left']['value']):
            self.error('Variable ' + node['left']['value'] +' not known')
        # 获取变量
        sym = env.findSymbol(node['left']['value'])
        # 判断是否为常量
        if sym['type'] == 'const':
            self.error('Cannot assign value to constant')
        if inFunc:
            self.code.append(INSTRUCTION.LEA)
        else:
            self.code.append(INSTRUCTION.PUSHIMM)
        self.code.append(sym['address'])
        # 判断是否为数组
        if node['left']['type'] == 'ArrayMember':
            self.generate(node['left']['offset'] , env , inFunc)
            self.code.append(INSTRUCTION.SUB)
            self.code.append(INSTRUCTION.PUSH)

        # 执行右部表达式
        self.generate(node['right'] , env , inFunc)

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
            # 获取变量
            sym= env.findSymbol(varible)
            # 生成虚拟机指令 , 将值载入寄存器
            if inFunc:
                self.code.append(INSTRUCTION.LEA)
                self.code.append(sym['address'])
                self.code.append(INSTRUCTION.POP)
            else:
                self.code.append(INSTRUCTION.IMM)
                self.code.append(sym['address'])
            self.code.append(INSTRUCTION.RLV)
        else:
            self.error('Variable ' + varible + ' not known')

    # 处理函数定义
    def generate_FunctionDeclaration(self , node: dict , env: Environment):
        # 检测重名
        if env.has(node['name']):
            self.error('Function ' + node['name'] + ' already defined')

        # 防止机器码顺序执行 无条件跳转过函数声明
        self.code.append(INSTRUCTION.JMP)
        start_index = len(self.code)
        self.code.append(None)
        # 注册函数
        env.addFunction(node['name'] , start_index + 1)

        # 设置函数内符号表 函数内局部变量基于bp指针 envrionment只起到符号表作用
        fun_env = Environment(env)
        symbolNum = len(node['args']) + 2
        # 参数在 bp 指针 上 相对地址为负
        for arg in node['args']:
            fun_env.symbolTable[arg] = {
                'address': symbolNum,
                'type': 'var'
            }
            symbolNum -= 1
        fun_env.symbolNum = 0

        # 解析函数体
        for stmt in node['body']['body']:
            self.generate(stmt , fun_env , True)

        self.code[start_index] = len(self.code)

    # 处理函数调用
    def generate_CallExpression(self , node: dict , env: Environment , inFunc: bool):
        # 判断函数是否声明
        if not env.find(node['value']):
            self.error('Function ' + node['value'] + ' not known')
        # 逐个传参
        num = len(node['args'])
        for i in range(num):
            self.generate(node['args'][i] , env , inFunc)
            self.code.append(INSTRUCTION.PUSH)
        # 存储参数个数
        self.code.append(INSTRUCTION.PUSHIMM)
        self.code.append(num)
        # 开辟栈空间
        self.code.append(INSTRUCTION.ENT)

        # 调用函数
        self.code.append(INSTRUCTION.CALL)
        sym = env.findSymbol(node['value'])
        # 判断是否为函数类型
        if sym['type'] != 'func':
            self.error(node['value'] + ' not a function')
        self.code.append(sym['address'])

    # 处理函数返回
    def generate_ReturnStatement(self , node: dict , env: Environment):
        self.generate(node['ret'] , env , True)
        self.code.append(INSTRUCTION.RET)

    # 处理print函数
    def generate_PrintStatement(self , node: dict , env: Environment , inFunc: bool):
        # 解析每个函数并打印
        for arg in node['args']:
            if arg['type'] == 'StringLiteral':
                self.error('print function do not support string')
            self.generate(arg , env , inFunc)
            self.code.append(INSTRUCTION.PRINT)

    # 处理input函数
    def generate_InputStatement(self , node: dict):
        self.code.append(INSTRUCTION.INPUT)
        if len(node['args']) == 1:
            arg = node['args'][0]['value']
            self.code.extend(encode(arg))
        self.code.append(0)




    def generate(self , node: dict , env: Environment = None , inFunc: bool = False):
        match node['type']:
            case 'Program':
                self.generate_program(node)
            case 'BinaryExpression':
                self.generate_BinaryExpression(node , env , inFunc)
            case 'SingleExpression':
                self.generate_SingleExpression(node , env , inFunc)
            case 'VariableDeclaration':
                self.generate_Declaration(node , env , inFunc)
            case 'ArrayDeclaration':
                self.generate_Array_Declaration(node , env , inFunc)
            case 'ArrayMember':
                self.generate_array(node , env , inFunc)
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
            case 'InputStatement':
                self.generate_InputStatement(node)
            case 'NumericLiteral':
                self.generate_NumericLiteral(node)
            case 'Identifier':
                self.generate_Identifier(node , env , inFunc)
            case _:
                self.error('NotSupported node type ' + node['type'] +' can not generate code')


    def generate_bin(self):

        with open(self.generateBin , 'wb') as f:
            length = len(self.code)
            i = 0
            while i < length:
                f.write(self.code[i].to_bytes(1, 'little' , signed=True))
                if has_parameter(self.code[i]):
                    f.write(get_parameter(self.code[i + 1]))
                    i += 1
                elif self.code[i] == INSTRUCTION.INPUT:
                    i += 1
                    while self.code[i] != 0:
                        f.write(self.code[i].to_bytes(4, 'little' , signed=True))
                        i += 1
                    f.write(self.code[i].to_bytes(4, 'little' , signed=True))

                i += 1

    def generate_code(self):
        # 把一些丑陋的语句封装到函数里
        def get_code_name(index):
            return INSTRUCTION(self.code[index]).name
        def get_parameter(index):
            return str(self.code[index])

        with open(self.generateCode , encoding='utf-8' ,mode='w') as f:
            length = len(self.code)
            i = 0
            while i < length:
                code = get_code_name(i)
                f.write(code + '\n')
                if has_parameter(self.code[i]):
                    f.write(get_parameter(i + 1) + '\n')
                    i += 1
                if self.code[i] == INSTRUCTION.INPUT:
                    i += 1
                    l = []
                    while self.code[i] != 0:
                        l.append(self.code[i])
                        i += 1
                    f.write(decode(l) + '\n')
                i += 1

    def error(self , info):
        print("Code Exception: " + str(info))
        sys.exit(0)
