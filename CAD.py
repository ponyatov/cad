
import os,sys

import wx

## dynamic object environment

class Frame:
    def __init__(self,V,line=None):
        self.type = self.__class__.__name__.lower()
        self.val  = V
        self.slot = {}
        self.nest = []
        if line: self['line'] = line

    ## dump

    def __repr__(self):
        return self.dump()
    def dump(self,depth=0,prefix='',voc=True,stack=True):
        tree = self._pad(depth) + self.head(prefix=prefix)
        if voc:
            for i in self.slot:
                tree += self.slot[i].dump(depth+1,prefix='%s = '%i)
        if stack:
            for j in self.nest:
                tree += j.dump(depth+1)
        return tree
    def head(self,prefix='',showid=True):
        header = '%s<%s:%s>' % (prefix,self.type,self._val())
        if showid: header += ' @%x' % id(self)
        return header
    def _val(self):
        return '%s' % self.val
    def _pad(self,depth):
        return '\n' + '\t' * depth

    ## operators

    def __getitem__(self,key):
        return self.slot[key]
    def __setitem__(self,key,that):
        if callable(that):      self[key] = Cmd(that)
        elif type(that) == int: self[key] = Int(that)
        else:                   self.slot[key] = that
        return self
    def __floordiv__(self,that):
        self.nest.append(that) ; return self

    ## stack

    def pop(self): return self.nest.pop(-1)
    def top(self): return self.nest[-1]

    ## computer/eval

    def eval(self,ctx):
        ctx // self

## primitives

class Prim(Frame): pass

class Sym(Prim): pass

class Str(Prim):
    def _val(self):
        s = ''
        for c in self.val:
            if    c == '\t': s += r"\t"
            elif  c == '\r': s += r"\t"
            elif  c == '\n': s += r"\n"
            else:            s += c
        return s

class Num(Prim): pass

class Int(Num): pass

class Hex(Int): pass
class Bin(Int): pass

## Executable Data Structures subset

class Active(Frame): pass

class Cmd(Active):
    def __init__(self,F):
        Active.__init__(self,F.__name__)
        self.fn = F
    def eval(self,ctx):
        self.fn(ctx)

class VM(Active): pass

class Seq(Active): pass

## global FORTH machine

vm = VM('metaL')

## debug/control

def BYE(ctx): sys.exit(0)

def QQ(ctx): print(ctx) ; BYE(ctx)
vm['??'] = QQ

## manipulations

def EQ(ctx): addr = ctx.pop() ; ctx[addr.val] = ctx.pop()
vm['='] = EQ

## no-sytax parser

import ply.lex as lex

tokens = ['sym','str','num','int','hex','bin']

t_ignore = ' \t\r'
t_ignore_comment = r'[\#\\].*'

states = (('str','exclusive'),)

t_str_ignore = ''

def t_str(t):
    r"'"
    t.lexer.push_state('str') ; t.lexer.string = ''
def t_str_str(t):
    r"'"
    t.lexer.pop_state() ; return Str(t.lexer.string)
def t_str_neline(t):
    r"\n+"
    t.lexer.lineno += len(t.value) ; t.lexer.string += t.value
def t_str_any(t):
    r"."
    t.lexer.string += t.value

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_sym(t):
    r'(`)|[^ \t\r\n\#\\]+'
    return Sym(t.value,line=t.lexer.lineno)

def t_ANY_error(t):
    raise SyntaxError(t)

## interpreter

def WORD(ctx):
    token = ctx.lexer.token()
    if token: ctx // token
    return token
vm['`'] = WORD

def FIND(ctx):
    token = ctx.pop()
    try: ctx // ctx[token.val] ; return True
    except KeyError: ctx // token ; return False

def EVAL(ctx):
    ctx.pop().eval(ctx)

def INTERP(ctx):
    ctx.lexer = lex.lex() ; ctx.lexer.input(ctx.pop().val)
    while True:
        if not WORD(ctx): break
        print(ctx.top())
        if isinstance(ctx.top(),Sym):
            if not FIND(ctx): raise SyntaxError(ctx.top())
        EVAL(ctx)

## system init

if __name__ == '__main__':
    with open(sys.argv[0][:-3]+'.ini') as ini:
        vm // Str(ini.read()) ; INTERP(vm)
