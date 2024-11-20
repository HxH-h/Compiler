from Parse.Parser import Parser
from Parse.Utils import AST_Visual , get_AST
from Generation.Generator import Generator
from VMachine.Machine import Machine
import argparse
import os

params = argparse.ArgumentParser(description='Compiler')
# 设置参数
params.add_argument('source_path' , type=str , help='source path')
params.add_argument('-o' , '--output' , type=str , help='output path' , nargs='?' , const=True)
params.add_argument('-r' , '--run' , action='store_true' , help='run code')
params.add_argument('-g' , '--generate' , type=str , help='generate code' , nargs='?' , const=True)
params.add_argument('-t' , '--tree' , type=str , help='AST' , nargs='?' , const=True)
params.add_argument('-v' , '--visual' , type=str , help='visual AST' , nargs='?' , const=True)

# -v子参数,--height 和--width
params.add_argument('--h' , '--height' , type=int , help='height')
params.add_argument('--w' , '--width' , type=int , help='width' )

# -r 子参数 -s
params.add_argument('-s' , '--size' , type=int , help='virtual memory size')


# 解析参数
args = params.parse_args()

# 检查合法性
def check_args(args):
    # 检查文件是否以.sl结尾
    if not args.source_path.endswith('.sl'):
        if not (args.run and args.source_path.endswith('.bin')):
            params.error('The source file must end with .sl or .bin')
    # 检查输入文件合法性
    if not os.access(args.source_path , os.R_OK):
        params.error('The source file does not exist')
    # -r 与其他互斥
    if args.run and (args.generate or args.output or args.visual or args.tree):
        params.error('The -r and other options are mutually exclusive')
    #只有-v存在,--height 和--width 才有效
    if not args.visual and (args.h is not None or args.w is not None):
        params.error('The --h and --w options require the -v option')
    # 只有-r存在 -s 才有效
    if not args.run and args.size is not None:
        params.error('The -s option requires the -r option')

def get_source_name() -> str:
    return os.path.splitext(args.source_path)[0]

check_args(args)


if __name__ == '__main__':
    #获取语法树
    if not args.run:
        parser = Parser(args.source_path)
        json = parser.parse()
        if args.tree:
            if args.tree is True:
                args.tree = get_source_name() + '.json'
            # 获取语法树
            get_AST(json , args.tree)

        if args.visual:
            if args.visual is True:
                args.visual = get_source_name() + '.html'
            # 可视化语法树
            AST_Visual(json , args.visual , args.h , args.w)
        # 生成中间代码
        if args.generate or args.output:
            g = Generator(get_source_name() , args.generate , args.output)
            g.generate(json)
    else:
        if args.source_path.endswith('.bin'):
            if not args.size:
                args.size = 100
            m = Machine(args.source_path , args.size)
            m.run()
        else:
            print('Please enter the binary file path')



