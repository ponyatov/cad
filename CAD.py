
import os,sys

## dynamic object environment

class Frame:
    def __init__(self,V):
        self.type = self.__class__.__name__.lower()
        self.val  = V
        self.slot = {}
        self.nest = []

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
    def head(self,prefix='',id=True):
        header = '%s<%s:%s>' % (prefix,self.type,self.val,id(self))
        if id: header += ' @%x' % id(self)
        return header

    ## operators

    def __getitem__(self,key):
        return self.slot[key]

    def __floordiv__(self,that):
        self.nest.append(that) ; return self

    ## stack

    def pop(self): return self.nest.pop(-1)
    def top(self): return self.nest[-1]

## primitives

class Prim(Frame): pass

class Sym(Prim): pass

class Str(Prim): pass

class Num(Prim): pass

class Int(Num): pass

class Hex(Int): pass
class Bin(Int): pass

## Executable Data Structures subset

class Active(Frame): pass

class Cmd(Active): pass

class VM(Active): pass

class Seq(Active): pass

## global FORTH machine

vm = VM('metaL')

## no-sytax parser

import ply.lex as lex

tokens = ['sym','str','num','int','hex','bin']

t_ignore = ' \t\r\n'
t_ignore_comment = r'[\#\\].*'

def t_sym(t):
    r'[^ \t\r\n\#\\]+'
    return Sym(t.value)

def t_ANY_error(t):
    raise SyntaxError(t)

## interpreter

def WORD(ctx):
    token = ctx.lexer.token()
    if token: ctx // token
    return token

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
        if isinstance(ctx.top(),Sym):
            if not FIND(ctx): raise SyntaxError(ctx)
        EVAL(ctx)

## system init

if __name__ == '__main__':
    with open(sys.argv[0][:-3]+'.ini') as ini:
        vm // Str(ini.read()) ; INTERP(vm)
