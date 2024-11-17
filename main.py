from Lex.Lexer import Lexer , Token , TYPE
from Parse.Parser import Parser
from Parse.Utils import AST_Visual
from Generation.Generator import Generator
from VMachine.Machine import Machine

if __name__ == '__main__':
    parser = Parser('test.txt')

    json = parser.parse()

    AST_Visual(json)

    g = Generator()
    g.generate(json)

    m = Machine('output.bin')
    print(m.run())



