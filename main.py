from Lex.Lexer import Lexer , Token , TYPE
from Parse.Parser import Parser
from Parse.Utils import AST_Visual
from Generation.Generator import Generator
from VMachine.Machine import Machine

if __name__ == '__main__':
    parser = Parser()
    tokens = [
        Token(TYPE.FUNC, "func"),
        Token(TYPE.IDENTIFIER, "sum"),
        Token(TYPE.OPENPT , "("),
        Token(TYPE.IDENTIFIER , "a"),
        Token(TYPE.COMMA , ","),
        Token(TYPE.IDENTIFIER , "b"),
        Token(TYPE.CLOSEPT , ")"),
        Token(TYPE.OPENBRACE , "{"),
        Token(TYPE.RETURN , "return"),
        Token(TYPE.IDENTIFIER, "a"),
        Token(TYPE.PLUS, "+"),
        Token(TYPE.IDENTIFIER, "b"),
        Token(TYPE.CLOSEBRACE , "}"),

        Token(TYPE.LET , "let"),
        Token(TYPE.IDENTIFIER, "a"),
        Token(TYPE.ASSIGN, "="),
        Token(TYPE.NUMBER, '5'),

        Token(TYPE.LET , "let"),
        Token(TYPE.IDENTIFIER, "b"),
        Token(TYPE.ASSIGN, "="),
        Token(TYPE.IDENTIFIER, "sum"),
        Token(TYPE.OPENPT, "("),
        Token(TYPE.IDENTIFIER, "a"),
        Token(TYPE.COMMA , ","),
        Token(TYPE.NUMBER, "2"),
        Token(TYPE.CLOSEPT, ")"),


        Token(TYPE.IF , "if"),
        Token(TYPE.OPENPT , "("),
        Token(TYPE.NUMBER, "3"),
        Token(TYPE.LESS, "<"),
        Token(TYPE.NUMBER, "3"),
        Token(TYPE.CLOSEPT , ")"),
        Token(TYPE.OPENBRACE , "{"),
        Token(TYPE.LET , "let"),
        Token(TYPE.IDENTIFIER, "a"),
        Token(TYPE.IDENTIFIER, "a"),
        Token(TYPE.ASSIGN, "="),
        Token(TYPE.NUMBER, '5'),
        Token(TYPE.PLUS, "+"),
        Token(TYPE.NUMBER, '2'),
        Token(TYPE.MULTI, "*"),
        Token(TYPE.OPENPT, "("),
        Token(TYPE.NUMBER, '120'),
        Token(TYPE.MINUS, "-"),
        Token(TYPE.NUMBER, '4'),
        Token(TYPE.CLOSEPT, ")"),
        Token(TYPE.EXDIV , "//"),
        Token(TYPE.NUMBER, '5'),
        Token(TYPE.IDENTIFIER, "a"),
        Token(TYPE.ASSIGN, "="),
        Token(TYPE.IDENTIFIER , "a"),
        Token(TYPE.PLUS, "+"),
        Token(TYPE.NUMBER, '2'),
        Token(TYPE.CLOSEBRACE , "}"),

        Token(TYPE.ELSE , "else"),
        Token(TYPE.OPENBRACE , "{"),
        Token(TYPE.LET , "let"),
        Token(TYPE.IDENTIFIER, "a"),
        Token(TYPE.ASSIGN, "="),
        Token(TYPE.NUMBER, '42'),
        Token(TYPE.CLOSEBRACE , "}"),
        Token(TYPE.LET , "let"),
        Token(TYPE.IDENTIFIER, "c"),
        Token(TYPE.ASSIGN, "="),
        Token(TYPE.NUMBER, '101'),
        Token(TYPE.EOF, None)
    ]

    parser.tokens = tokens
    json = parser.parse()

    print(json)
    AST_Visual(json)

    g = Generator()
    g.generate(json)

    m = Machine('output.bin')
    print(m.run())



