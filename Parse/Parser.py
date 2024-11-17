from Lex.Lexer import Lexer , Token , TYPE
import json

# token 转 AST
class Parser:
    def __init__(self):
        self.lexer = Lexer()
        self.tokens = self.lexer.tokenize()
        self.currentToken = 0

    # 返回当前Token , 并后移一位
    # @return Token: 返回当前Token
    def next(self) -> Token:
        temp = self.tokens[self.currentToken]
        self.currentToken += 1
        return temp

    # 返回当前Token
    # @return Token: 返回当前Token
    def at(self) -> Token:
        return self.tokens[self.currentToken]

    # 功能同next 但如果当前Token与传入参数不符则报错
    # @param type: TYPE枚举类
    # @param msg: 报错信息
    # @return Token: 返回当前Token
    def expect(self , type: TYPE , msg: str) -> Token:
        tk = self.tokens[self.currentToken]
        if tk.type == type:
            self.currentToken += 1
            return tk
        else:
            raise SyntaxError(msg)

    # 判断Token流是否结束
    # @return bool: 结束返回True
    def isEnd(self) -> bool:
        return self.tokens[self.currentToken].type == TYPE.EOF

    # 语法分析 递归下降 生成抽象语法树
    # @return dict: 返回语法分析结果 通过嵌套字典表示抽象语法树
    def parse(self) -> dict:
        return self.parse_program()

    # 一个程序 包含 多条语句
    # @return dict: 返回语法分析结果
    def parse_program(self) -> dict:
        ret = {
            "type": "Program",
            "body": []
        }
        # 循环解析所有语句
        while not self.isEnd():
            ret["body"].append(self.parse_statement())

        return ret

    # 一个语句 可以是表达式 也可以是语句
    # @return dict: 返回一条语句的AST
    def parse_statement(self) -> dict:
        # 根据Token类型进行判断 决定处理 表达式 还是 语句
        type = self.at().type
        match type:
            case TYPE.LET | TYPE.CONST:
                return self.parse_defination()
            case TYPE.IF:
                return self.parse_condition()
            case TYPE.WHILE:
                return self.parse_loop()
            case TYPE.FUNC:
                return self.parse_function()
            case TYPE.RETURN:
                return self.parse_return()
            case _:
                return self.parse_expression()

    # 处理定义变量语句
    # @return dict: 返回一条定义语句的AST
    def parse_defination(self) -> dict:
        ret = {
            "type": "VariableDeclaration",
            "child":[]
        }
        token = self.next()
        child = {}
        child['isConstant'] = token.type == TYPE.CONST
        child['name'] = self.expect(TYPE.IDENTIFIER,"Expect Identifier").value

        # 判断是否有赋值操作
        if self.at().type == TYPE.ASSIGN:
            child['operator'] = self.expect(TYPE.ASSIGN,"Expect Assign").value
            child['right'] = self.parse_expression()

        ret["child"].append(child)
        return ret

    # 处理函数声明
    # @return dict: 返回一条函数声明语句的AST
    def parse_function(self) -> dict:
        self.next()
        ret = {
            "type": "FunctionDeclaration",
        }
        # 函数名
        ret['name'] = self.expect(TYPE.IDENTIFIER,"Expect Identifier").value
        # 解析参数
        ret['args'] = self.parse_parameter()
        # 解析函数体
        ret['body'] = self.parse_block()
        # TODO 解析return

        return ret

    # 处理函数调用
    # @return dict: 返回一条函数调用语句的AST
    def parse_call(self) -> list:
        # 处理 (
        self.expect(TYPE.OPENPT,"Expect Open Parenthesis")
        args = []
        if self.at().type == TYPE.CLOSEPT:
            self.next()
            return args
        # 获取第一个实参
        first = self.parse_expression()
        args.append(first)
        # 循环判断是否有后续参数
        while self.at().type == TYPE.COMMA:
            self.next()
            args.append(self.parse_expression())

        self.expect(TYPE.CLOSEPT,"Expect Close Parenthesis")
        return args

    # 处理返回表达式
    # @return dict: 返回一条返回语句的AST
    def parse_return(self) -> dict:
        self.next()
        return {
            "type": "ReturnStatement",
            "ret": self.parse_expression()
        }


    # 获取函数声明形参
    def parse_parameter(self):
        self.expect(TYPE.OPENPT,"Expect Open Parenthesis")
        args = []
        # 空参直接返回
        if self.at().type == TYPE.CLOSEPT:
            self.next()
            return args
        # 获取第一个形参
        name = self.expect(TYPE.IDENTIFIER,"Expect Identifier").value
        args.append(name)
        # 循环判断是否有后续参数
        while self.at().type == TYPE.COMMA:
            self.next()
            name = self.expect(TYPE.IDENTIFIER,"Expect Identifier").value
            args.append(name)
        # 检测是否由 ) 结束
        self.expect(TYPE.CLOSEPT,"Expect Close Parenthesis")
        return args

    # 处理条件语句
    # @return dict: 返回一条条件语句的AST
    def parse_condition(self) -> dict:
        # 指针当前为 IF ， 后移
        self.next()
        ret = {
            "type": "IfStatement",
        }
        # 判断是否为 (
        self.expect(TYPE.OPENPT,"Expect Open Parenthesis")
        # 解析判断表达式
        ret['condition'] = self.parse_expression()
        self.expect(TYPE.CLOSEPT,"Expect Close Parenthesis")

        # 解析 if 语句块
        ret['ifbody'] = self.parse_block()

        # 查看是否有else
        if self.at().type == TYPE.ELSE:
            self.next()
            # 解析else 语句块
            ret['elsebody'] = self.parse_block()

        return ret

    # 处理循环语句
    # @return dict: 返回一条循环语句的AST
    def parse_loop(self) -> dict:
        # 指针当前为 WHILE ， 后移
        self.next()
        ret = {
            "type": "LoopStatement",
        }
        # 解析条件
        self.expect(TYPE.OPENPT,"Expect Open Parenthesis")
        ret['condition'] = self.parse_expression()
        self.expect(TYPE.CLOSEPT,"Expect Close Parenthesis")
        # 解析循环体
        ret['body'] = self.parse_block()

        return ret

    # 处理块语句
    # @return dict: 返回一条块语句的AST
    def parse_block(self) -> dict:
        ret = {
            "type": "BlockStatement",
            "body": []
        }
        # 检测是否由 { 开始
        self.expect(TYPE.OPENBRACE,"Expect Open Brace")

        # 循环解析语句块内的语句
        while not self.at().type == TYPE.CLOSEBRACE:
            ret["body"].append(self.parse_statement())

        # 检测是否由 } 结束
        self.expect(TYPE.CLOSEBRACE , "Expect Close Brace")
        return ret



    # 优先级爬山 处理表达式
    # @return dict: 返回一条表达式的AST
    def parse_expression(self) -> dict:
        # 调用优先级最低的 解析 运算符 的函数
        return self.parse_assign()

    # 处理赋值表达式
    def parse_assign(self) -> dict:
        left = self.parse_or()
        if self.at().type == TYPE.ASSIGN:
            op = self.next()
            right = self.parse_or()
            left = {
                "type": "AssignExpression",
                "left": left,
                "right": right,
                "operator": op.value
            }
        return left

    # 处理 或 运算符
    def parse_or(self) -> dict:
        left = self.parse_and()
        while self.at().type == TYPE.OR:
            op = self.next()
            right = self.parse_and()
            left = {
                "type": "BinaryExpression",
                "left": left,
                "right": right,
                "operator": op.value
            }
        return left

    # 处理 与 运算符
    def parse_and(self) -> dict:
        left = self.parse_equal()
        while self.at().type == TYPE.AND:
            op = self.next()
            right = self.parse_equal()
            left = {
                "type": "BinaryExpression",
                "left": left,
                "right": right,
                "operator": op.value
            }
        return left

    # 处理 相等 运算符
    def parse_equal(self) -> dict:
        left = self.parse_compare()
        if self.at().type == TYPE.EQUAL or self.at().type == TYPE.NE:
            op = self.next()
            right = self.parse_compare()
            left = {
                "type": "BinaryExpression",
                "left": left,
                "right": right,
                "operator": op.value
            }
        return left

    # 处理比较运算符
    def parse_compare(self) -> dict:
        left = self.parse_plus()
        if self.at().type == TYPE.LE or self.at().type == TYPE.GE or self.at().type == TYPE.LESS or self.at().type == TYPE.GREATER:
            op = self.next()
            right = self.parse_plus()
            left = {
                "type": "BinaryExpression",
                "left": left,
                "right": right,
                "operator": op.value
            }
        return left

    # 处理加减法表达式
    def parse_plus(self) -> dict:
        # 处理左部
        left = self.parse_multi()

        while self.at().type == TYPE.PLUS or self.at().type == TYPE.MINUS:
            # 获取操作符
            op = self.next()
            right = self.parse_multi()
            left = {
                "type": "BinaryExpression",
                "left": left,
                "right": right,
                "operator": op.value
            }

        return left

    # 处理乘 除 取余 整除表达式
    def parse_multi(self) -> dict:
        left = self.parse_primary()

        while self.at().type == TYPE.MULTI or self.at().type == TYPE.DIVIDE or self.at().type == TYPE.MOD or self.at().type == TYPE.EXDIV:
            op = self.next()
            right = self.parse_primary()
            left = {
                "type": "BinaryExpression",
                "left": left,
                "right": right,
                "operator": op.value
            }
        return left

    # 处理表达式终结符 递归出口
    # @return dict: 返回终结符
    def parse_primary(self) -> dict:
        # 处理终结符 数字 , 字符串 , 变量
        token = self.next()

        ret = {"value": token.value}

        match token.type:
            # 二元运算符正常会在对应函数中被处理 ， 这里只处理一元运算符
            case TYPE.NUMBER | TYPE.MINUS:
                ret["type"] = "NumericLiteral"
                # 匹配负数
                if token.type == TYPE.MINUS:
                    ret["value"] += self.next().value
            case TYPE.STRING:
                ret["type"] = "StringLiteral"
            case TYPE.IDENTIFIER:
                ret["type"] = "Identifier"
                if self.at().type == TYPE.OPENPT:
                    ret['type'] = "CallExpression"
                    ret['args'] = self.parse_call()
            case TYPE.OPENPT:
                # 括号内 仍然是 表达式
                ret = self.parse_expression()
                self.expect(TYPE.CLOSEPT, "Expected ')' ")
                return ret
            case _:
                raise SyntaxError("Unexpected token: " + token.value)
        return ret





