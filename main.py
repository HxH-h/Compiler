from Lex.Lexer import Lexer , Token , TYPE
from Parse.Parser import Parser
from Parse.Utils import AST_Visual
from Generation.Generator import Generator
from VMachine.Machine import Machine

if __name__ == '__main__':
    parser = Parser()
    tokens = [
        Token(TYPE.NUMBER, '1'),
        Token(TYPE.PLUS, "+"),
        Token(TYPE.NUMBER, '2'),
        Token(TYPE.MULTI, "*"),
        Token(TYPE.OPENPT, "("),
        Token(TYPE.NUMBER, '3'),
        Token(TYPE.MINUS, "-"),
        Token(TYPE.NUMBER, '4'),
        Token(TYPE.CLOSEPT, ")"),
        Token(TYPE.EOF, None)
    ]
    parser.tokens = tokens
    json = parser.parse()

    AST_Visual(json)

    g = Generator()
    g.generate(json)
    print(g.code)
    m = Machine(g.code)
    print(m.read_bin("output.bin"))



