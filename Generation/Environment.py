from __future__ import annotations
class Environment:
    def __init__(self , parent: Environment = None):
        self.symbolTable = {}
        self.parent = parent
        self.symbolNum = 0
        # 有父环境则算上父环境的数量
        if parent:
            self.symbolNum = parent.symbolNum

    # 查找 当前环境下 变量是否存在
    def has(self , name: str) -> bool:
        return name in self.symbolTable

    # 获取 当前环境下 变量 栈地址
    def getSymbol(self , name: str) -> dict:
        return self.symbolTable[name]

    # 添加变量 并获取分配的栈地址
    def addSymbol(self , name: str , type: str = "var") -> int:
        self.symbolNum += 1
        self.symbolTable[name] = {
            "address": -self.symbolNum,
            "type": type
                                 }
        return -self.symbolNum

    # 添加函数
    def addFunction(self , name: str, address: int):
        self.symbolTable[name] = {
            "address": address,
            "type": "func"
        }

    # 递归的查找变量是否存在
    def find(self , name: str) -> bool:
        if self.has(name):
            return True
        elif self.parent:
            return self.parent.find(name)
        else:
            return False

    # 递归的获取变量
    def findSymbol(self , name: str) -> dict:
        # 调用前会先执行find 所以不需要判断不存在的情况
        if self.has(name):
            return self.getSymbol(name)
        elif self.parent:
            return self.parent.findSymbol(name)



