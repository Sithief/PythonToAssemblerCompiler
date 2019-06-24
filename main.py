import lexer
import my_parser

if __name__ == '__main__':
    filename = 'test_programm.py'
    with open(filename) as file:
        test_code = file.read()

    lex = lexer.Lexer(test_code)
    # lex.run()
    pars = my_parser.Parser(lex)
    code, sym_table = pars.parse()
    a = 1
