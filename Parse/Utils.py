from pyecharts import options as opt
from pyecharts.charts import Tree
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
    # 判断声明
    if node['type'] == "VariableDeclaration":
        n = {"name": node["type"], "children": []}
        for child in node['child']:
            get_varible_node(child , n['children'])
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
    # TODO 处理声明同时赋值的语句
    if 'operator' in node:
        tree.append({"name": node["operator"]})
        get_node(node['right'] , tree)


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
