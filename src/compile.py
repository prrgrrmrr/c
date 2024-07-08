"""Compiler main"""

import sys
from io import StringIO
from lex import tokens
from parse import parse
from codegen import gen
from emit import emit

def compile(args):
    output = None
    input_path = args[0]
    with open(input_path, "r") as input_file:
        src_string = input_file.read()
    if "-S" in args:
        # Emit assembly instructions to file
        toks = tokens(src_string)
        ast = parse(toks)
        assembly_ast = gen(ast)
        output = StringIO()
        emit(assembly_ast, output)
    elif "--codegen" in args:
        # Generate assembly tree representation and stop before emitting to file
        toks = tokens(src_string)
        ast = parse(toks)
        assembly_ast = gen(ast)
    elif "--parse" in args:
        # Generate abstract syntax tree and stop before assembly code generation
        toks = tokens(src_string)
        ast = parse(toks)
    elif "--lex" in args:
        # Stop after tokenization
        toks = tokens(src_string)
        for tok in toks:
            print(tok)
    else:
        # No args, assume user wants to emit assembly instructions to file
        toks = tokens(src_string)
        ast = parse(toks)
        assembly_ast = gen(ast)
        output = StringIO()
        emit(assembly_ast, output)
    return output
