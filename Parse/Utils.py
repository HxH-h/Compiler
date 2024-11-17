from pyecharts import options as opt
from pyecharts.charts import Tree
import struct
from VMachine.Instruction import INSTRUCTION
# 可视化语法树
# @Param ast: 语法树
def AST_Visual(ast: dict):
    # 根据AST 找出 节点 和 边
    tree = search(ast)
    # echarts 画图
    draw_graph(tree)

# 搜索节点
# @Param node: 节点
def search(node: dict) -> dict:

    tree = {"name": node["type"] , "children": []}

    for child in node["body"]:
        get_node(child , tree["children"])

    return tree

# 遍历整棵树 , 构建节点
def get_node(node: dict , tree: list):
    # 判断声明语句
    if node['type'] == "VariableDeclaration":
        n = {"name": node["type"], "children": []}
        for child in node['child']:
            get_varible_node(child , n['children'])
        tree.append(n)
        return
    # 判断IF语句
    if node['type'] == "IfStatement":
        get_if_node(node , tree)
        return
    # 判断循环语句
    if node['type'] == "LoopStatement":
        get_while_node(node , tree)
        return

    # 判断函数声明
    if node['type'] == "FunctionDeclaration":
        get_function_node(node , tree)
        return

    # 判断函数调用
    if node['type'] == "CallExpression" or node['type'] == "PrintStatement":
        get_call_node(node , tree)
        return

    # 函数返回值
    if node['type'] == "ReturnStatement":
        n = {"name": node["type"], "children": []}
        get_node(node['ret'] , n['children'])
        tree.append(n)
        return

    # 递归出口
    if isEnd(node):
        tree.append({"name": node["value"]})
        return
    # 创建当前节点
    n = {"name": node["type"], "children": []}

    get_node(node["left"] , n["children"])

    # 如果是表达式 还要输出符号
    if node["type"] == "BinaryExpression" or node["type"] == "AssignExpression":
        n["children"].append({"name": node["operator"]})

    get_node(node["right"] , n["children"])

    tree.append(n)

# 构建变量声明的节点
def get_varible_node(node: dict , tree: list):
    key = 'const' if node["isConstant"] else 'let'
    tree.append({"name": key})
    tree.append({"name": node["name"]})
    # 处理声明同时赋值的语句
    if 'operator' in node:
        tree.append({"name": node["operator"]})
        get_node(node['right'] , tree)

def get_if_node(node: dict , tree: list):
    n = {"name": node["type"] , "children": []}
    # 获取 if体
    get_block_node(node['ifbody'] , n['children'] , 'if_statement')
    # 获取条件
    get_node(node['condition'] , n['children'])
    # 获取else体
    if 'elsebody' in node:
        get_block_node(node['elsebody'] , n['children'] , 'else_statement')
    tree.append(n)

def get_while_node(node: dict , tree: list):
    n = {"name": node["type"] , "children": []}
    # 获取条件
    get_node(node['condition'] , n['children'])
    # 获取循环体
    get_block_node(node['body'] , n['children'] , 'while_statement')

    tree.append(n)

def get_function_node(node: dict , tree: list):
    n = {"name": node["type"] , "children": []}
    # 获取函数名
    n['children'].append({"name": node['name']})
    # 获取参数
    if 'args' in node:
        get_parameter_node(node['args'] , n['children'])
    # 获取函数体
    get_block_node(node['body'] , n['children'] , 'function_body')
    tree.append(n)

def get_parameter_node(args: list , tree: list):
    n = {"name": "parameter" , "children": []}
    for arg in args:
        n['children'].append({"name": arg})
    tree.append(n)

def get_call_node(node: dict , tree: list):
    n = {"name": node["value"] , "children": []}
    if 'args' in node:
        for arg in node['args']:
            get_node(arg , n['children'])
    tree.append(n)


def get_block_node(node: dict , tree: list , name: str):
    n = {"name": name , "children": []}
    for child in node['body']:
        get_node(child , n['children'])
    tree.append(n)


# 判断叶子节点
def isEnd(node: dict):
    return node["type"] in ['NumericLiteral' , 'StringLiteral' , 'Identifier']

def draw_graph(tree: dict):

    t = (Tree(init_opts=opt.InitOpts(width="1500px", height="800px"))
         .add("", [tree],
          orient="TB",
          edge_fork_position = '10%',
          initial_tree_depth = -1,
          symbol = 'none',
          is_roam = True,
          label_opts=opt.LabelOpts(font_size=18),
          leaves_opts = opt.TreeLeavesOpts(
              label_opts=opt.LabelOpts(font_size=18)
          )
        )
         .set_global_opts(title_opts=opt.TitleOpts(title="抽象语法树"))
         .render("./AST.html")
    )


# 判断是否为数字

def is_number(s):
    try:  # 如果能运行float(s)语句，返回True（字符串s是浮点数）
        float(s)
        return True
    except ValueError:  # ValueError为Python的一种标准异常，表示"传入无效的参数"
        pass  # 如果引发了ValueError这种异常，不做任何事情（pass：不做任何事情，一般用做占位语句）
    try:
        import unicodedata  # 处理ASCii码的包
        unicodedata.numeric(s)  # 把一个表示数字的字符串转换为浮点数返回的函数
        return True
    except (TypeError, ValueError):
        pass
    return False
def is_integer(s):
    return s %1 == 0

def get_parameter(num):
    if is_integer(num):
        return num.to_bytes(4, byteorder='little' , signed=True)
    else:
        return struct.pack('<f', num)

def has_parameter(code: INSTRUCTION):
    return code in [INSTRUCTION.IMM,
                    INSTRUCTION.IMMF,
                    INSTRUCTION.PUSHIMM,
                    INSTRUCTION.JMP,
                    INSTRUCTION.JZ,
                    INSTRUCTION.JNZ,
                    INSTRUCTION.LEA,
                    INSTRUCTION.CALL,
                    INSTRUCTION.RET,
                    INSTRUCTION.ENT]
