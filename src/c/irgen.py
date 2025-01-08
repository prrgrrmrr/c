"""Converts AST to intermediate tree"""

from c.syntax_tree import AST
from c.intermediate_tree import INTERMEDIATE_AST

class BadDestinationException(Exception):
    pass

def irgen(ast, uname_generator):
    """Generates tree of intermediate representation from AST"""
    
    # Simple if-else for now
    # TODO Visitor design pattern solves this better by defining visit method for each node
    # TODO avoid costly concatenation of results, return tuples of tuples.. and flatten after the irgen finishes running
    
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
    elif isinstance(ast, AST.BinaryOperation):
        lhs = irgen(ast.lhs, uname_generator)
        rhs = irgen(ast.rhs, uname_generator)
        dst = INTERMEDIATE_AST.Var(next(uname_generator))
        
        if isinstance(ast.binary_operator, AST.Addition):
            binary_operator = INTERMEDIATE_AST.Addition()
        elif isinstance(ast.binary_operator, AST.Subtraction):
            binary_operator = INTERMEDIATE_AST.Subtraction()
        elif isinstance(ast.binary_operator, AST.Multiplication):
            binary_operator = INTERMEDIATE_AST.Multiplication()
        elif isinstance(ast.binary_operator, AST.Division):
            binary_operator = INTERMEDIATE_AST.Division()
        elif isinstance(ast.binary_operator, AST.Remainder):
            binary_operator = INTERMEDIATE_AST.Remainder()

        # lhs and rhs have to come before the binary operation for ordering to make sense (inside out)
        if isinstance(lhs, INTERMEDIATE_AST.Constant) and isinstance(rhs, INTERMEDIATE_AST.Constant):
            return (INTERMEDIATE_AST.BinaryOperation(binary_operator, lhs, rhs, dst),)
        elif isinstance(lhs, INTERMEDIATE_AST.Constant):
            return rhs + (INTERMEDIATE_AST.BinaryOperation(binary_operator, lhs, rhs[-1].dst_val, dst),)
        elif isinstance(rhs, INTERMEDIATE_AST.Constant):
            return lhs + (INTERMEDIATE_AST.BinaryOperation(binary_operator, lhs[-1].dst_val, rhs, dst),)
        else:
            return lhs + rhs + (INTERMEDIATE_AST.BinaryOperation(binary_operator, lhs[-1].dst_val, rhs[-1].dst_val, dst),)
