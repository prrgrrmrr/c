"""Converts AST to another tree representation useful for assembly generation"""

from syntax_tree import AST
from assembly_tree import ASSEMBLY_AST

def gen(ast):
    """Generates tree of assembly instructions from AST"""
    
    # Simple if-else for now
    # TODO Visitor design pattern solves this better by defining visit method for each node
    if isinstance(ast, AST.Program):
        function_definition = gen(ast.function_definition)
        return ASSEMBLY_AST.Program(function_definition)
    elif isinstance(ast, AST.Function):
        name = ast.name
        instructions = gen(ast.body)
        return ASSEMBLY_AST.Function(name, instructions)
    elif isinstance(ast, AST.Return):
        exp = gen(ast.exp)
        return ASSEMBLY_AST.Instructions(
            (ASSEMBLY_AST.Mov(exp, ASSEMBLY_AST.Register()), ASSEMBLY_AST.Ret())
        )
    elif isinstance(ast, AST.Constant):
        return ASSEMBLY_AST.Imm(ast.value)
