from Lex.Lexer import Lexer , Token , TYPE
import json
from Utils import AST_Visual

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
        # TODO 根据Token类型进行判断 决定处理 表达式 还是 语句
        return self.parse_expression()

    # 优先级爬山 处理表达式
    # @return dict: 返回一条表达式的AST
    def parse_expression(self) -> dict:
        # TODO 调用优先级最低的 解析 运算符 的函数
        return self.parse_or()

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
            case TYPE.OPENPT:
                # 括号内 仍然是 表达式
                ret = self.parse_expression()
                self.expect(TYPE.CLOSEPT, "Expected ')' ")
                return ret
            case _:
                raise SyntaxError("Unexpected token: " + token.value)
        return ret

    def format_ast(self):
        return json.dumps(self.parse() , indent=4)


if __name__ == '__main__':
    parser = Parser()
    tokens = [
              Token(TYPE.NUMBER, '1'),
              Token(TYPE.PLUS , "+"),
              Token(TYPE.NUMBER, '2'),
              Token(TYPE.MULTI, "*"),
              Token(TYPE.OPENPT, "("),
              Token(TYPE.NUMBER, '3'),
              Token(TYPE.MINUS, "-"),
              Token(TYPE.NUMBER, '4'),
              Token(TYPE.CLOSEPT, ")"),
              Token(TYPE.LE, "<="),
              Token(TYPE.NUMBER, '5'),
              Token(TYPE.OR, "||"),
              Token(TYPE.IDENTIFIER, 'a'),
              Token(TYPE.AND, "&&"),
              Token(TYPE.IDENTIFIER, 'b'),
              Token(TYPE.AND, "&&"),
              Token(TYPE.IDENTIFIER, 'c'),
              Token(TYPE.EOF, None)
              ]
    parser.tokens = tokens
    AST_Visual(parser.parse())


