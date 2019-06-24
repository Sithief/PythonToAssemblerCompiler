NUM, ID, STR, IF, ELSE, WHILE, LPAR, RPAR, MINUS, PLUS, SBL, SBR, COMMA, OR, AND, \
MUL, DIV, LESS, LEQUAL, MORE, MEQUAL, NEQUAL, EQUAL, EQ, COLON, NL, TAB, EOF = range(28)  # Список идентификаторов языка


class Token(object):
    def __init__(self, pos, lexeme, l_type):
        self.pos = pos  # Номер строки в которой находится токен
        self.lexeme = lexeme  # Лексема
        self.l_type = l_type  # Код лексемы


class Lexer(object):
    def __init__(self, text):
        self.numbers = '0123456789'
        self.letters = '_ABCDEFGHIJKLMNOPQRSTUYWXYZabcdefghijklmnopqrstuvwxyz'
        self.specials = '[]():=+-*/<>,'
        self.mode = 0  # 0 - default, 1 - text, 2 - comment, 3 - offset
        self.text = str()
        self.length = self.pos = self.str_pos = 0
        self.is_lf = False

        self.symbols = {'(': LPAR, ')': RPAR, '+': PLUS, '-': MINUS, '*': MUL, '[': SBL, ']': SBR, ',': COMMA,
                        '/': DIV, '<': LESS, '<=': LEQUAL, '>': MORE, '>=': MEQUAL, '=': EQUAL, '==': EQ, ':': COLON}
        self.words = {'if': IF, 'else': ELSE, 'while': WHILE, 'or': OR, 'and': AND}
        self.token = None

        self.text = text
        self.length = len(text)
        self.pos = 0
        self.str_pos = 0

    def step(self):
        a = str()
        # print('next step')
        while self.pos < self.length:
            c = self.text[self.pos]
            self.pos += 1
            # print('%25s | %7s | %s' % ([a], [c], self.mode))

            if c == '\n':
                self.str_pos += 1
                self.is_lf = True
                self.mode = 3
                return True, c
            else:
                self.is_lf = False

            if self.mode == 0:
                if c in ['=', '<', '>', '!']:
                    if self.pos < self.length and self.text[self.pos] == '=':
                        self.pos += 1
                        return True, c + '='

                if c in ['[', ']']:
                    return True, c

                if a and c not in self.numbers + self.letters:
                    return True, a

                if c in ['\"', '\'']:
                    a += c
                    self.mode = 1
                    continue

                elif c == '#':
                    self.mode = 2
                    continue

                elif c not in self.numbers + self.letters + self.specials + '\t \n':
                    return False, c

                elif c not in [' ', '\n']:
                    a += c

                if self.pos < self.length:
                    c = self.text[self.pos]

                if a and c not in self.numbers + self.letters:
                    return True, a

            elif self.mode == 1:
                a += c
                if self.pos < self.length and c != '\\' and self.text[self.pos] in ['\"', '\'']:
                    a += self.text[self.pos]
                    self.mode = 0
                    self.pos += 1
                    return True, a
                elif self.pos >= self.length or self.text[self.pos] == '\n':
                    return False, a

            elif self.mode == 2:
                if self.is_lf:
                    self.mode = 0

            elif self.mode == 3:
                if c == ' ':
                    a += c
                    if len(a) >= 4 and a[-4:] == '    ':
                        a = a[:-4] + '\t'
                else:
                    self.mode = 0
                    self.pos -= 1
                    if a and c in self.numbers + self.letters:
                        if ' ' not in a:
                            return True, a
                        else:
                            return False, a

                    elif c in ['\"', '\'']:
                        self.mode = 1

                    else:
                        a = ''
                    continue

        return True, a

    def step_token(self):
        status, st = self.step()
        if not status:
            print("error in line: %5s error: %s" % (self.str_pos + 1, [self.text.split('\n')[self.str_pos]]))
            print(" " * (28 + len(self.text[:self.pos].split('\n')[-1])), '^')
            return False
        if not st:
            l_type = EOF
        elif st in self.symbols:
            l_type = self.symbols[st]
        elif st in self.words:
            l_type = self.words[st]
        elif st.isdigit():
            l_type = NUM
        elif st[0].isalpha() and st.isalnum():
            l_type = ID
        elif st[0] + st[-1] in ['""', "''"]:
            l_type = STR
        elif st == '\n':
            l_type = NL
        elif all([s == '\t' for s in st]):
            l_type = TAB
        else:
            print("error in line:%5s error: %s" % (self.str_pos + 1, [self.text.split('\n')[self.str_pos]]))
            print(" " * (28 + len(self.text[:self.pos].split('\n')[-1])), '^')
            print()
            return False
        token = Token(self.str_pos, st, l_type)
        # return token
        self.token = token

    def run(self):
        result = list()
        while self.pos < self.length:
            self.step_token()
            if self.token:
                print(self.token.pos, [self.token.lexeme], self.token.l_type)
                result.append(self.token)

        return result

