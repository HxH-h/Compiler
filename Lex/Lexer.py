from enum import Enum , auto
import re
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

    SL = auto()
    SR = auto()
    LAND = auto()
    LOR = auto()
    NOT = auto()

    EQUAL = auto()
    NE = auto()
    LESS = auto()
    GREATER = auto()
    LE = auto()
    GE = auto()

    ASSIGN = auto()

    OR = auto()
    AND = auto()
    XOR = auto()

    OPENPT = auto()
    CLOSEPT = auto()
    OPENMT = auto()
    CLOSEMT = auto()
    OPENBRACE = auto()
    CLOSEBRACE = auto()
    COMMA = auto()

    LET = auto()
    CONST = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FUNC = auto()
    RETURN = auto()

    EOF = auto()

class Token:
    def __init__(self, type, value :str = None):
        self.type = type
        self.value = value

class Lexer:
    def __init__(self, filepath: str):
        self.input_code_str = self.read_file(filepath)  # 源程序字符串
        self.code_char_list = []  # 源程序字符列表
        self.code_len = 0  # 源程序字符列表长度
        self.cp = 0  # 源程序字符列表指针，方便遍历字符串中的字符
        self.cur = ''  # 当前源程序字符列表的某个字符
        self.val = []  # 单词自身的值
        self.type = None  # 单词种别码
        self.errInfo = ""  # 错误信息
         # 关键字
        self.keyWords = ["let", 'const' ,"if", "else", "while","NULL","func","return"]

    def read_file(self, filepath) -> str:
        with open(filepath,encoding="utf-8" ,  mode="r") as file:
            code = file.read()
        return code

    def nextChar(self):  # 封装cp++，简化函数scanWord中的代码
        self.cp += 1
        self.cur = self.code_char_list[self.cp]

    def error(self, info):  # errInfo错误信息
        line = 1
        for i in range(0, self.cp + 1):
            if self.code_char_list[i] == '\n':
                line += 1
        self.errInfo = "第" + str(line) + "行报错：" + info

    def bracket_match(self):
        pattern = r'(#.*?$)'  # 匹配单行或多行注释
        comments = re.findall(pattern, self.input_code_str, flags=re.MULTILINE | re.DOTALL)
        #re.findall是Python中用于搜索字符串与正则表达式匹配子串的函数
        #re.findall函数接受三个参数，其中pattern和string是必需的，而flags是可选的。函数返回一个列表，其中包含了与正则表达式匹配的所有子串。
        #pattern：正则表达式的模式或模式字符串。
        #string：要搜索的字符串。
        #flags：可选参数，用于控制正则表达式的匹配方式，如是否区分大小写等 MULTILINE：将换行符当换行符而不是文本处理，DOTALL：匹配换行符
        #.：表示匹配任意单个字符
        #*：表示前面的字符可以出现零次或多次
        #?：表示非贪婪模式，即尽可能少地匹配字符。这是为了防止多行注释中的 * 被匹配掉
        #$：表示行的结尾。这个是为了确保匹配的是单行注释，直到行的结束
        comments = [comment[0].strip() for comment in comments]  # 处理结果，去除多余的空格
        i = 0
        code_sub_com = []  # 去除注释

        while i < len(self.input_code_str):
            ch = self.input_code_str[i]
            if ch == "#" and comments != []:
                i += len(comments[0])
                comments.pop(0)
                continue
            code_sub_com.append((i, ch))
            i += 1

        pattern2 = r'"([^"]*)"'  # 匹配双引号包裹的字符串
        strings = re.findall(pattern2, self.input_code_str)
        code_sub_com_str = []  # 去除字符串变量
        i = 0
        while i < len(code_sub_com):
            item = code_sub_com[i]
            ch = item[1]
            if ch == "\"" and comments != []:
                i += len(strings[0]) + 2
                strings.pop(0)
                continue
            code_sub_com_str.append(item)
            i += 1

        s = []
        stack = []
        mapping = {")": "(", "}": "{", "]": "["}
        for idx, char in code_sub_com_str:
            if char in mapping.keys() or char in mapping.values():
                s.append((idx, char))

        if not s:
            return "ok"
        for item in s:
            idx = item[0]
            char = item[1]
            if char in mapping.values():  # 左括号
                stack.append(item)
            elif char in mapping.keys():  # 右括号
                if not stack:  # 栈为空，当前右括号匹配不到
                    return idx
                topitem = stack[-1]
                topidx = topitem[0]
                topch = topitem[1]
                if mapping[char] != topch:  # 当前右括号匹配失败
                    return topidx
                else:
                    stack.pop()
        if not stack:  # 栈为空，匹配完毕
            return "ok"
        else:  # 栈不为空，只剩下左括号
            item = stack[0]
            idx = item[0]
            return idx

    def scanWord(self):  # 词法分析
        # 初始化value
        self.val = []
        self.type = 0

        # 获取当前有效字符
        self.cur = self.code_char_list[self.cp]
        # print(f"==={self.cp}  {self.code_len-1}===")
        while self.cur == ' ' or self.cur == '\n' or self.cur == '\t':
            self.cp += 1
            if self.cp >= self.code_len - 1:
                print(f"越界{self.cp}")
                return  # 越界直接返回
            self.cur = self.code_char_list[self.cp]

        # 首字符为数字
        if self.cur.isdigit():
            # 首先默认为整数
            i_value = 0
            while self.cur.isdigit():  # string数转int
                i_value = i_value * 10 + int(self.cur)
                self.nextChar()

            self.type = TYPE.NUMBER
            self.val = str(i_value)  # int转str

            # 有小数点，则为浮点数
            d_value = i_value * 1.0
            if self.cur == '.':
                fraction = 0.1
                self.nextChar()
                while self.cur.isdigit():  # 计算小数位上的数 形如 123.45
                    d_value += fraction * int(self.cur)
                    fraction = fraction * 0.1
                    self.nextChar()

                self.type = TYPE.NUMBER
                self.val = str(d_value)  # double转str

        # 首字符为字母
        elif self.cur.isalpha():
            # 标识符
            while self.cur.isdigit() or self.cur.isalpha() or self.cur == '_':
                self.val.append(self.cur)
                self.nextChar()
            self.type = TYPE.IDENTIFIER
            # 判断是否为关键字
            for keyword in self.keyWords:
                if ''.join(self.val) == keyword:
                    self.type = TYPE[keyword.upper()]
                    break
        # 首字符为标点
        else:
            if self.cur == '+':
                self.type = TYPE.PLUS
                self.val.append(self.cur)
                self.nextChar()

            elif self.cur == '-':
                self.type = TYPE.MINUS
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == '*':
                self.type = TYPE.MULTI
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == '/':
                self.type = TYPE.DIVIDE
                self.val.append(self.cur)
                self.nextChar()
                if self.cur == '/':
                    self.type = TYPE.EXDIV
                    self.val.append(self.cur)
                    self.nextChar()
            elif self.cur == '%':
                self.type = TYPE.MOD
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == '=':
                self.type = TYPE.ASSIGN
                self.val.append(self.cur)
                self.nextChar()
                if self.cur == '=':
                    self.type = TYPE.EQUAL
                    self.val.append(self.cur)
                    self.nextChar()
            elif self.cur == '(':
                self.type = TYPE.OPENPT
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == ')':
                self.type = TYPE.CLOSEPT
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == '[':
                self.type = TYPE.OPENMT
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == ']':
                self.type = TYPE.CLOSEMT
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == '{':
                self.type = TYPE.OPENBRACE
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == '}':
                self.type = TYPE.CLOSEBRACE
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == '>':
                self.type = TYPE.GREATER
                self.val.append(self.cur)
                self.nextChar()
                if self.cur == '=':
                    self.type = TYPE.GE
                    self.val.append(self.cur)
                    self.nextChar()
                elif self.cur == '>':
                    self.type = TYPE.SR
                    self.val.append(self.cur)
                    self.nextChar()
            elif self.cur == '<':
                self.type = TYPE.LESS
                self.val.append(self.cur)
                self.nextChar()
                if self.cur == '=':
                    self.type = TYPE.LE
                    self.val.append(self.cur)
                    self.nextChar()
                elif self.cur == '<':
                    self.type = TYPE.SL
                    self.val.append(self.cur)
                    self.nextChar()
            elif self.cur == '!':
                self.type = TYPE.NOT
                self.val.append(self.cur)
                self.nextChar()
                if self.cur == '=':
                    self.type = TYPE.NE
                    self.val.append(self.cur)
                    self.nextChar()
            elif self.cur == '&':
                self.type = TYPE.LAND
                self.val.append(self.cur)
                self.nextChar()
                if self.cur == '&':
                    self.type = TYPE.AND
                    self.val.append(self.cur)
                    self.nextChar()
            elif self.cur == '|':
                self.type = TYPE.LOR
                self.val.append(self.cur)
                self.nextChar()
                if self.cur == '|':
                    self.type = TYPE.OR
                    self.val.append(self.cur)
                    self.nextChar()
            elif self.cur == '\"':  # ”
                self.nextChar()
                haveEnd = False
                flag = 0
                for i in range(self.cp, self.code_len):
                    if self.code_char_list[i] == '"':
                        haveEnd = True
                        flag = i
                        break
                if haveEnd:
                    for j in range(self.cp, flag):
                        self.val.append(self.code_char_list[j])
                    self.cp = flag + 1
                    self.cur = self.code_char_list[self.cp]
                    self.type = TYPE.STRING
                else:
                    self.type = -999
                    self.error(" string常量没有闭合的\" ")
            elif self.cur == ',':
                self.type = TYPE.COMMA
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == '^':  # 按位异或
                self.type = TYPE.XOR
                self.val.append(self.cur)
                self.nextChar()
            elif self.cur == '#':
                self.nextChar()
                while self.cur != '\n':
                    self.nextChar()
                self.type = 0
            else:
                self.type = -999
                self.error(f" 无效字符: {self.cur}")

    def tokenize(self) -> list:
        Tokens = []
        self.code_char_list = list(self.input_code_str.strip())  # 去除头尾的空格
        self.code_char_list.append('\n')  # 末尾补充一个\n， 可在一些while判断中 防止越界
        self.code_len = len(self.code_char_list)

        if self.bracket_match() != "ok":  # 检测括号匹配
            self.cp = self.bracket_match()
            self.error(f"{self.code_char_list[self.cp]}匹配缺失！")


        while True:  # 至少执行一次，如同do while
            self.scanWord()  # 进入词法分析
            value = ''.join(self.val)  # char列表 ===> String
            new_tf = Token(self.type,  value)  # 创建二元式对象

            Tokens.append(new_tf)

            if self.cp >= (self.code_len - 1):  # 最后一个元素 为自主添加的\n，代表结束
                break

        if self.errInfo:  # 检查是否有报错
            print(self.errInfo)
            return []

        new_tf = Token(TYPE.EOF)
        Tokens.append(new_tf)

        return Tokens