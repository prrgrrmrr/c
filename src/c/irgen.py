"""Converts AST to intermediate tree"""

from c.syntax_tree import AST
from c.intermediate_tree import IR_AST


def _unop(ast_op):
    """Returns equivalent IR unary op from AST unary operator"""
    match ast_op:
        case AST.Complement():
            return IR_AST.Complement()
        case AST.Negation():
            return IR_AST.Negation()
        case AST.Not():
            return IR_AST.Not()
    return None


def _binop(ast_op):
    """Returns equivalent IR binary op from AST binary operator"""
    # Logical And/Or are handled separately in IR generation
    match ast_op:
        case AST.Addition():
            return IR_AST.Addition()
        case AST.Subtraction():
            return IR_AST.Subtraction()
        case AST.Multiplication():
            return IR_AST.Multiplication()
        case AST.Division():
            return IR_AST.Division()
        case AST.Remainder():
            return IR_AST.Remainder()
        case AST.Equal():
            return IR_AST.Equal()
        case AST.NotEqual():
            return IR_AST.NotEqual()
        case AST.LessThan():
            return IR_AST.LessThan()
        case AST.LessOrEqual():
            return IR_AST.LessOrEqual()
        case AST.GreaterThan():
            return IR_AST.GreaterThan()
        case AST.GreaterOrEqual():
            return IR_AST.GreaterOrEqual()
    return None


def _irgen_short_circuit_and(lhs, lhs_result, rhs, rhs_result, dst, uname_generator):
    """Generates IR instructions to short-circuit logical And"""
    false_label = f"_false{next(uname_generator)}"
    end_label = f"_end{next(uname_generator)}"

    if isinstance(lhs, IR_AST.Constant) and isinstance(rhs, IR_AST.Constant):
        return (
            (
                IR_AST.JumpIfZero(lhs, false_label),
                IR_AST.JumpIfZero(rhs, false_label),
                IR_AST.Copy(IR_AST.Constant(1), dst),
                IR_AST.Jump(end_label),
                IR_AST.Label(false_label),
                IR_AST.Copy(IR_AST.Constant(0), dst),
                IR_AST.Label(end_label),
            ),
            dst,
        )
    elif isinstance(lhs, IR_AST.Constant):
        return (
            (IR_AST.JumpIfZero(lhs, false_label),)
            + rhs
            + (
                IR_AST.JumpIfZero(rhs_result, false_label),
                IR_AST.Copy(IR_AST.Constant(1), dst),
                IR_AST.Jump(end_label),
                IR_AST.Label(false_label),
                IR_AST.Copy(IR_AST.Constant(0), dst),
                IR_AST.Label(end_label),
            ),
            dst,
        )
    elif isinstance(rhs, IR_AST.Constant):
        return (
            lhs
            + (
                IR_AST.JumpIfZero(lhs_result, false_label),
                IR_AST.JumpIfZero(rhs, false_label),
                IR_AST.Copy(IR_AST.Constant(1), dst),
                IR_AST.Jump(end_label),
                IR_AST.Label(false_label),
                IR_AST.Copy(IR_AST.Constant(0), dst),
                IR_AST.Label(end_label),
            ),
            dst,
        )
    else:
        return (
            lhs
            + (IR_AST.JumpIfZero(lhs_result, false_label),)
            + rhs
            + (
                IR_AST.JumpIfZero(rhs_result, false_label),
                IR_AST.Copy(IR_AST.Constant(1), dst),
                IR_AST.Jump(end_label),
                IR_AST.Label(false_label),
                IR_AST.Copy(IR_AST.Constant(0), dst),
                IR_AST.Label(end_label),
            ),
            dst,
        )


def _irgen_short_circuit_or(lhs, lhs_result, rhs, rhs_result, dst, uname_generator):
    """Generates IR instructions to short-circuit logical Or"""
    true_label = f"_true{next(uname_generator)}"
    end_label = f"_end{next(uname_generator)}"

    if isinstance(lhs, IR_AST.Constant) and isinstance(rhs, IR_AST.Constant):
        return (
            (
                IR_AST.JumpIfNotZero(lhs, true_label),
                IR_AST.JumpIfNotZero(rhs, true_label),
                IR_AST.Copy(IR_AST.Constant(0), dst),
                IR_AST.Jump(end_label),
                IR_AST.Label(true_label),
                IR_AST.Copy(IR_AST.Constant(1), dst),
                IR_AST.Label(end_label),
            ),
            dst,
        )
    elif isinstance(lhs, IR_AST.Constant):
        return (
            (IR_AST.JumpIfNotZero(lhs, true_label),)
            + rhs
            + (
                IR_AST.JumpIfNotZero(rhs_result, true_label),
                IR_AST.Copy(IR_AST.Constant(0), dst),
                IR_AST.Jump(end_label),
                IR_AST.Label(true_label),
                IR_AST.Copy(IR_AST.Constant(1), dst),
                IR_AST.Label(end_label),
            ),
            dst,
        )
    elif isinstance(rhs, IR_AST.Constant):
        return (
            lhs
            + (
                IR_AST.JumpIfNotZero(lhs_result, true_label),
                IR_AST.JumpIfNotZero(rhs, true_label),
                IR_AST.Copy(IR_AST.Constant(0), dst),
                IR_AST.Jump(end_label),
                IR_AST.Label(true_label),
                IR_AST.Copy(IR_AST.Constant(1), dst),
                IR_AST.Label(end_label),
            ),
            dst,
        )
    else:
        return (
            lhs
            + (IR_AST.JumpIfNotZero(lhs_result, true_label),)
            + rhs
            + (
                IR_AST.JumpIfNotZero(rhs_result, true_label),
                IR_AST.Copy(IR_AST.Constant(0), dst),
                IR_AST.Jump(end_label),
                IR_AST.Label(true_label),
                IR_AST.Copy(IR_AST.Constant(1), dst),
                IR_AST.Label(end_label),
            ),
            dst,
        )


def _irgen_unary_operation(ast, uname_generator):
    """Generates IR instructions for unary operation, returns pair (instructions, result_destination)"""
    # Inside out instructions
    exp, exp_result = irgen(ast.exp, uname_generator)
    dst = IR_AST.Var(next(uname_generator))

    unary_operator = _unop(ast.unary_operator)

    if isinstance(exp, IR_AST.Constant):
        return ((IR_AST.UnaryOperation(unary_operator, exp, dst),), dst)
    else:
        return (exp + (IR_AST.UnaryOperation(unary_operator, exp_result, dst),), dst)


def _irgen_binary_operation(ast, uname_generator):
    """Generates IR instructions for binary operation, returns pair (instructions, result_destination)"""
    lhs, lhs_result = irgen(ast.lhs, uname_generator)
    rhs, rhs_result = irgen(ast.rhs, uname_generator)
    dst = IR_AST.Var(next(uname_generator))

    # Handle short-circuiting binary logical operators
    if isinstance(ast.binary_operator, AST.And):
        return _irgen_short_circuit_and(
            lhs, lhs_result, rhs, rhs_result, dst, uname_generator
        )
    elif isinstance(ast.binary_operator, AST.Or):
        return _irgen_short_circuit_or(
            lhs, lhs_result, rhs, rhs_result, dst, uname_generator
        )

    # Other binary operators
    binary_operator = _binop(ast.binary_operator)

    # lhs and rhs have to come before the binary operation for ordering to make sense (inside out)
    if isinstance(lhs, IR_AST.Constant) and isinstance(rhs, IR_AST.Constant):
        return (IR_AST.BinaryOperation(binary_operator, lhs, rhs, dst),), dst
    elif isinstance(lhs, IR_AST.Constant):
        return (
            rhs + (IR_AST.BinaryOperation(binary_operator, lhs, rhs_result, dst),),
            dst,
        )
    elif isinstance(rhs, IR_AST.Constant):
        return (
            lhs + (IR_AST.BinaryOperation(binary_operator, lhs_result, rhs, dst),),
            dst,
        )
    else:
        return (
            lhs
            + rhs
            + (IR_AST.BinaryOperation(binary_operator, lhs_result, rhs_result, dst),),
            dst,
        )


def irgen(ast, uname_generator):
    """Generates IR tree from AST"""

    # Simple if-else for now
    # TODO Visitor design pattern solves this better by defining visit method for each node
    # TODO avoid costly concatenation of results, linked list could be useful here

    # Program
    if isinstance(ast, AST.Program):
        function_definition = irgen(ast.function_definition, uname_generator)
        return IR_AST.Program(function_definition)

    # Function
    elif isinstance(ast, AST.Function):
        name = ast.name
        instructions = irgen(ast.body, uname_generator)
        return IR_AST.Function(name, instructions)

    # Statements
    elif isinstance(ast, AST.Return):
        # Inside out instructions
        exp, exp_result = irgen(ast.exp, uname_generator)
        if isinstance(exp, IR_AST.Constant):
            return (IR_AST.Return(exp),)
        else:
            return exp + (IR_AST.Return(exp_result),)

    # Expressions - return instructions and the destination where result is stored
    # (instructions, result_destination)

    # Constants
    elif isinstance(ast, AST.Constant):
        return (IR_AST.Constant(ast.value), None)

    # Unary operations
    elif isinstance(ast, AST.UnaryOperation):
        return _irgen_unary_operation(ast, uname_generator)

    # Binary operations
    elif isinstance(ast, AST.BinaryOperation):
        return _irgen_binary_operation(ast, uname_generator)
