import lexer
import sys
from enum import Enum


class DataType(Enum):
    INT = 0
    STR = 1
    INT_ARRAY = 2
    STR_ARRAY = 3


class Node:
    def __init__(self, kind, value=None, op1=None, op2=None, op3=None):
        self.kind = kind
        self.value = value
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3


class Parser(object):
    VAR, CONST, STR_CONST, ADD, SUB, LT, LET, GT, GET, EQUAL, SET, \
    IF1, IF2, WHILE, EMPTY, SEQ, EXPR, PROG, OPEREND, ARRAY = range(20)

    def __init__(self, lexer_init):
        self.lexer = lexer_init
        self.tab_counter = 0
        self.symbol_table = dict()
        
    def error(self, msg):
        print('Parser error:', msg, 'Error in line:', self.lexer.token.pos)
        sys.exit(1)

    def term(self):
        if self.lexer.token.l_type == lexer.ID:
            n = Node(Parser.VAR, self.lexer.token.lexeme)
            self.lexer.step_token()
            return n
        elif self.lexer.token.l_type == lexer.NUM:
            n = Node(Parser.CONST, self.lexer.token.lexeme)
            self.lexer.step_token()
            return n
        elif self.lexer.token.l_type == lexer.STR:
            n = Node(Parser.STR_CONST, self.lexer.token.lexeme)
            self.lexer.step_token()
            return n
        else:
            return self.paren_expr()

    def summa(self):
        n = self.term()
        while self.lexer.token.l_type == lexer.PLUS or self.lexer.token.l_type == lexer.MINUS:
            if self.lexer.token.l_type == lexer.PLUS:
                kind = Parser.ADD
            else:
                kind = Parser.SUB
            self.lexer.step_token()
            n = Node(kind, op1=n, op2=self.term())
        return n

    def test(self):
        n = self.summa()
        if self.lexer.token.l_type == lexer.LESS:
            self.lexer.step_token()
            n = Node(Parser.LT, op1=n, op2=self.summa())
        elif self.lexer.token.l_type == lexer.MORE:
            self.lexer.step_token()
            n = Node(Parser.GT, op1=n, op2=self.summa())
        elif self.lexer.token.l_type == lexer.MEQUAL:
            self.lexer.step_token()
            n = Node(Parser.GET, op1=n, op2=self.summa())
        elif self.lexer.token.l_type == lexer.LEQUAL:
            self.lexer.step_token()
            n = Node(Parser.LET, op1=n, op2=self.summa())
        elif self.lexer.token.l_type == lexer.EQ:
            self.lexer.step_token()
            n = Node(Parser.EQUAL, op1=n, op2=self.summa())
        return n

    # def check_array(self, node, data_types):
    #     arr_len = node.op1
    #     n = node
    #     for i in range(arr_len):
    #         n = n.op2
    #         self.check_expr(n, data_types)

    def check_expr(self, node, data_types):
        if node.kind == Parser.VAR:
            if node.value not in self.symbol_table:
                self.error('Variable not initialized')
            else:
                data_types.append(self.symbol_table[node.value])
        elif node.kind == Parser.CONST:
            data_types.append(DataType.INT)
        elif node.kind == Parser.STR_CONST:
            data_types.append(DataType.STR)
        elif node.kind == Parser.ARRAY:
            array_data_types = []
            self.check_expr(node.op2, array_data_types)
            if array_data_types[0] == DataType.INT:
                data_types.append(DataType.INT_ARRAY)
            elif array_data_types[0] == DataType.STR:
                data_types.append(DataType.STR_ARRAY)
            else:
                self.error('Array type error')
            return

        if node.op1 != None:
            self.check_expr(node.op1, data_types)
        if node.op2 != None:
            self.check_expr(node.op2, data_types)
        if node.op3 != None:
            self.check_expr(node.op3, data_types)

        if not all([i == data_types[0] for i in data_types]):
            self.error('Type error')

    def check_synbol(self, node):
        if node.kind == Parser.EXPR:
            if node.op1.kind == Parser.SET:
                if node.op1.op1.kind != Parser.VAR:
                    self.error('Variable expected')
                else:
                    expr_types = []
                    self.check_expr(node.op1.op2, expr_types)
                    self.symbol_table[node.op1.op1.value] = expr_types[0]
            else:
                self.check_expr(node.op1, [])
        # else:
        #     self.error('Expression expected')

    def expr(self):
        if self.lexer.token.l_type != lexer.ID:
            return self.test()
        n = self.test()
        if n.kind == Parser.VAR and self.lexer.token.l_type == lexer.EQUAL:
            self.lexer.step_token()
            if self.lexer.token.l_type == lexer.SBL:
                array_var = n
                n = Node(Parser.ARRAY)
                self.lexer.step_token()
                n.op1 = 0  # длина массива
                n.op2 = Node(Parser.EMPTY)
                node = n.op2
                while self.lexer.token.l_type != lexer.EOF and self.lexer.token.l_type != lexer.SBR:
                    st = Node(Parser.EMPTY, op1=self.expr())
                    node.op1 = st
                    n.op1 += 1
                    node.op2 = Node(Parser.EMPTY)
                    node = node.op2
                    if self.lexer.token.l_type == lexer.SBR:
                        break
                    if self.lexer.token.l_type == lexer.COMMA:
                        self.lexer.step_token()
                    else:
                        self.error('"," expected')
                self.lexer.step_token()
                n = Node(Parser.SET, op1=array_var, op2=n)
            else:
                n = Node(Parser.SET, op1=n, op2=self.expr())
        self.check_synbol(n)
        return n

    def paren_expr(self):
        if self.lexer.token.l_type != lexer.LPAR:
            self.error('"(" expected')
        self.lexer.step_token()
        n = self.expr()
        if self.lexer.token.l_type != lexer.RPAR:
            self.error('")" expected')
        self.lexer.step_token()
        return n

    def scope_syntax(self):
        if self.lexer.token.l_type != lexer.COLON:
            self.error('":" expected')
        self.lexer.step_token()
        if self.lexer.token.l_type != lexer.NL:
            self.error('pep 8 error')
        self.lexer.step_token()
        if self.lexer.token.l_type != lexer.TAB or len(self.lexer.token.lexeme) <= self.tab_counter:
            self.error('expected an indented block')
        self.tab_counter = len(self.lexer.token.lexeme)

    def statement(self):
        if self.lexer.token.l_type == lexer.TAB:
            if len(self.lexer.token.lexeme) > self.tab_counter:
                self.error('unexpected indent')
            elif len(self.lexer.token.lexeme) < self.tab_counter:
                self.tab_counter = len(self.lexer.token.lexeme)
                self.lexer.step_token()
                return Node(Parser.OPEREND)
            else:
                self.lexer.step_token()
        elif self.tab_counter:
            return Node(Parser.OPEREND)

        if self.lexer.token.l_type == lexer.IF:
            n = Node(Parser.IF1)
            self.lexer.step_token()
            n.op1 = self.expr()
            self.scope_syntax()
            n.op2 = Node(Parser.EMPTY)
            node = n.op2
            while self.lexer.token.l_type != lexer.EOF:
                st = Node(Parser.EMPTY, op1=self.statement())
                if st.op1.kind == Parser.OPEREND:
                    break
                node.op1 = st
                node.op2 = Node(Parser.EMPTY)
                node = node.op2
            if self.lexer.token.l_type == lexer.ELSE:
                n.kind = Parser.IF2
                self.lexer.step_token()
                self.scope_syntax()
                n.op3 = Node(Parser.EMPTY)
                node = n.op3
                while self.lexer.token.l_type != lexer.EOF:
                    st = Node(Parser.EMPTY, op1=self.statement())
                    if st.op1.kind == Parser.OPEREND:
                        break
                    node.op1 = st
                    node.op2 = Node(Parser.EMPTY)
                    node = node.op2
        elif self.lexer.token.l_type == lexer.WHILE:
            n = Node(Parser.WHILE)
            self.lexer.step_token()
            n.op1 = self.expr()
            self.scope_syntax()
            n.op2 = Node(Parser.EMPTY)
            node = n.op2
            while self.lexer.token.l_type != lexer.EOF:
                st = Node(Parser.EMPTY, op1=self.statement())
                if st.op1.kind == Parser.OPEREND:
                    break
                node.op1 = st
                node.op2 = Node(Parser.EMPTY)
                node = node.op2

        elif self.lexer.token.l_type == lexer.COLON:
            n = Node(Parser.EMPTY)
            self.lexer.step_token()
        elif self.lexer.token.l_type == lexer.LPAR:
            n = Node(Parser.EMPTY)
            self.lexer.step_token()
            while self.lexer.token.l_type != lexer.RPAR:
                n = Node(Parser.SEQ, op1=n, op2=self.statement())
            self.lexer.step_token()
        else:
            n = Node(Parser.EXPR, op1=self.expr())
            self.check_synbol(n)
            self.lexer.step_token()

        return n

    def parse(self):
        self.lexer.step_token()
        node = Node(Parser.PROG)
        prog = node
        while self.lexer.token.l_type != lexer.EOF:
            st = Node(Parser.EMPTY, op1=self.statement())
            node.op1 = st
            node.op2 = Node(Parser.EMPTY)
            node = node.op2
        # if (self.lexer.token.l_type != lexer.EOF):
        #     self.error("Invalid statement syntax")
        return prog, self.symbol_table



