class Environment:
    def __init__(self):
        self.symbolTable = {}
        self.symbolNum = 0

    # 查找变量是否存在
    def has(self , name: str) -> bool:
        return name in self.symbolTable

    # 获取变量 栈地址
    def getSymbol(self , name: str) -> int:
        return self.symbolTable[name]

    # 添加变量 并获取分配的栈地址
    def addSymbol(self , name: str) -> int:
        self.symbolNum += 1
        self.symbolTable[name] = -self.symbolNum
        return -self.symbolNum