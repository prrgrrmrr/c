"""Compiler main"""

from io import StringIO
from c.lex import tokens
from c.parse import parse
from c.irgen import irgen
from c.codegen import asmgen
from c.emit import emit
from c.utils import tmp_unique_name


def compile(args):
    output = None
    input_path = args[0]
    var_name_generator = tmp_unique_name()

    with open(input_path, "r") as input_file:
        src_string = input_file.read()
    if "-S" in args:
        # Emit assembly instructions to file
        toks = tokens(src_string)
        ast = parse(toks)
        intermediate_ast = irgen(ast, var_name_generator)
        assembly_ast = asmgen(intermediate_ast)
        output = StringIO()
        emit(assembly_ast, output)
    elif "--codegen" in args:
        # Generate assembly tree representation and stop before emitting to file
        toks = tokens(src_string)
        ast = parse(toks)
        intermediate_ast = irgen(ast, var_name_generator)
        assembly_ast = asmgen(intermediate_ast)
    elif "--tacky" in args:
        # Generate intermediate tree representation and stop before assembly tree generation
        toks = tokens(src_string)
        ast = parse(toks)
        intermediate_ast = irgen(ast, var_name_generator)
    elif "--parse" in args:
        # Generate abstract syntax tree and stop before intermediate tree generation
        toks = tokens(src_string)
        ast = parse(toks)
    elif "--lex" in args:
        # Stop after tokenization
        toks = tokens(src_string)
        # for tok in toks:
        #     print(tok)
    else:
        # No args, assume user wants to emit assembly instructions to file
        toks = tokens(src_string)
        ast = parse(toks)
        intermediate_ast = irgen(ast, var_name_generator)
        assembly_ast = asmgen(intermediate_ast)
        output = StringIO()
        emit(assembly_ast, output)
    return output
