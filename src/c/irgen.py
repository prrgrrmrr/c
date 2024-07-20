"""Converts AST to intermediate tree"""

from c.syntax_tree import AST
from c.intermediate_tree import INTERMEDIATE_AST

class BadDestinationException(Exception):
    pass

def irgen(ast, uname_generator):
    """Generates tree of intermediate representation from AST"""
    
    # Simple if-else for now
    # TODO Visitor design pattern solves this better by defining visit method for each node
    
    # Program
    if isinstance(ast, AST.Program):
        function_definition = irgen(ast.function_definition, uname_generator)
        return INTERMEDIATE_AST.Program(function_definition)
    # Function
    elif isinstance(ast, AST.Function):
        name = ast.name
        instructions = irgen(ast.body, uname_generator)
        return INTERMEDIATE_AST.Function(name, instructions)
    # Statements
    elif isinstance(ast, AST.Return):
        # Inside out instructions
        exp = irgen(ast.exp, uname_generator)
        if isinstance(exp, INTERMEDIATE_AST.Constant):
            return (INTERMEDIATE_AST.Return(exp),)
        else:
            return exp + (INTERMEDIATE_AST.Return(exp[-1].dst_val),) # TODO this is not efficient - do constant time list concat instead
    # Expressions
    elif isinstance(ast, AST.Constant):
        return INTERMEDIATE_AST.Constant(ast.value)
    elif isinstance(ast, AST.UnaryOperation):
        # Inside out instructions
        exp = irgen(ast.exp, uname_generator)
        dst = INTERMEDIATE_AST.Var(next(uname_generator))
        if isinstance(ast.unary_operator, AST.Complement):
            unary_operator = INTERMEDIATE_AST.Complement()
        elif isinstance(ast.unary_operator, AST.Negation):
            unary_operator = INTERMEDIATE_AST.Negation()
        if isinstance(exp, INTERMEDIATE_AST.Constant):
            return (INTERMEDIATE_AST.UnaryOperation(unary_operator, exp, dst),)
        else:
            return exp + (INTERMEDIATE_AST.UnaryOperation(unary_operator, exp[-1].dst_val, dst),)
