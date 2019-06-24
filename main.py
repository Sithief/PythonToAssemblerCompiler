import lexer
import my_parser


def print_tree(node, offset):
    if type(node) == int:
        print(offset, f'\\_Array length {node}')
    else:
        print(offset + '\\_', node.kind.name)
        if node.op1:
            if node.op2:
                print_tree(node.op1, offset+' |')
            else:
                print_tree(node.op1, offset+'  ')
        if node.op2:
            if node.op3:
                print_tree(node.op2, offset + ' |')
            else:
                print_tree(node.op2, offset + '  ')
        if node.op3:
            print_tree(node.op3, offset)


def print_symbol_table(sym_table):
    print('\n')
    print('symbol table:')
    for symbol in sym_table:
        print('%10s | %s' % (symbol, sym_table[symbol].name))


if __name__ == '__main__':
    filename = 'test_programm.py'
    with open(filename) as file:
        test_code = file.read()

    lex = lexer.Lexer(test_code)
    # lex.run()
    pars = my_parser.Parser(lex)
    code, sym_table = pars.parse()
    a = 1
    print_tree(code, '')
    print_symbol_table(sym_table)




