from pyecharts import options as opt
from pyecharts.charts import Tree
# 可视化语法树
# @Param ast: 语法树
def AST_Visual(ast: dict):
    # 根据AST 找出 节点 和 边
    tree = search(ast)
    print(tree)
    # echarts 画图
    draw_graph(tree)

# 搜索节点
# @Param node: 节点
def search(node: dict) -> dict:

    tree = {"name": node["type"] , "children": []}

    for child in node["body"]:
        get_node(child , tree["children"])

    return tree

# 前序遍历整棵树
def get_node(node: dict , tree: list):

    # 递归出口
    if isEnd(node):
        tree.append({"name": node["value"]})
        return
    # 创建当前节点
    n = {"name": node["type"], "children": []}

    get_node(node["left"] , n["children"])

    # 如果是表达式 还要输出符号
    if node["type"] == "BinaryExpression":
        n["children"].append({"name": node["operator"]})

    get_node(node["right"] , n["children"])

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
         .render("../AST.html")
    )