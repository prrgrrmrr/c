"""AST definitions for intermediate representation

ASDL specification

program = Program(function_definition)
function_definition = Function(identifier, instruction* body)
instruction = Return(val)
    | Unary(unary_operator, val src, val dst)
    | Binary(binary_operator, val src1, val src2, val dst)
    | Copy(val src, val dst)
    | Jump(identifier target)
    | JumpIfZero(val condition, identifier target)
    | JumpIfNotZero(val condition, identifier target)
    | Label(identifier)
val = Constant(int) | Var(identifier)
unary_operator = Complement | Negate | Not
binary_operator = Add | Subtract | Multiply | Divide | Remainder | Equal | NotEqual | LessThan | LessOrEqual | GreaterThan | GreaterOrEqual

Constraints

The dst val in Unary cannot be a constant

"""


class IR_AST:

    class Program:
        def __init__(self, function_definition):
            self.function_definition = function_definition

        def __eq__(self, other) -> bool:
            return (
                isinstance(other, IR_AST.Program)
                and self.function_definition == other.function_definition
            )

    class Function:
        def __init__(self, name, instructions):
            self.name = name
            self.instructions = instructions

        def __eq__(self, other) -> bool:
            return (
                isinstance(other, IR_AST.Function)
                and self.name == other.name
                and self.instructions == other.instructions
            )

    class Instruction:
        pass

    class Return(Instruction):
        def __init__(self, val) -> None:
            super().__init__()
            self.val = val

        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Return) and self.val == other.val

    class UnaryOperation(Instruction):
        def __init__(self, unary_operator, src_val, dst_val) -> None:
            super().__init__()
            self.unary_operator = unary_operator
            self.src_val = src_val
            self.dst_val = dst_val

        def __eq__(self, other: object) -> bool:
            return (
                isinstance(other, IR_AST.UnaryOperation)
                and self.unary_operator == other.unary_operator
                and self.src_val == other.src_val
                and self.dst_val == other.dst_val
            )

    class BinaryOperation(Instruction):
        def __init__(self, binary_operator, src_val1, src_val2, dst_val) -> None:
            super().__init__()
            self.binary_operator = binary_operator
            self.src_val1 = src_val1
            self.src_val2 = src_val2
            self.dst_val = dst_val

        def __eq__(self, other: object) -> bool:
            return (
                isinstance(other, IR_AST.BinaryOperation)
                and self.binary_operator == other.binary_operator
                and self.src_val1 == other.src_val1
                and self.src_val2 == other.src_val2
                and self.dst_val == other.dst_val
            )

    class Val:
        pass

    class Constant(Val):
        def __init__(self, value) -> None:
            super().__init__()
            self.value = value

        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Constant) and self.value == other.value

    class Var(Val):
        def __init__(self, identifier) -> None:
            super().__init__()
            self.identifier = identifier

        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Var) and self.identifier == other.identifier

    class UnaryOperator:
        pass

    class Complement(UnaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Complement)

    class Negation(UnaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Negation)

    # Logical Not
    class Not(UnaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Not)

    class BinaryOperator:
        pass

    class Addition(BinaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Addition)

    class Subtraction(BinaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Subtraction)

    class Multiplication(BinaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Multiplication)

    class Division(BinaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Division)

    class Remainder(BinaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, IR_AST.Remainder)

    # Binary logical and relational binary operators
    # Note: logical And/Or are implemented using jump instructions, no need to add nodes for them in IR
    # class And(BinaryOperator):
    #     def __init__(self) -> None:
    #         super().__init__()

    #     def __eq__(self, other) -> bool:
    #         return isinstance(other, IR_AST.And)

    # class Or(BinaryOperator):
    #     def __init__(self) -> None:
    #         super().__init__()

    #     def __eq__(self, other) -> bool:
    #         return isinstance(other, IR_AST.Or)

    class Equal(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, IR_AST.Equal)

    class NotEqual(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, IR_AST.NotEqual)

    class LessThan(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, IR_AST.LessThan)

    class LessOrEqual(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, IR_AST.LessOrEqual)

    class GreaterThan(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, IR_AST.GreaterThan)

    class GreaterOrEqual(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, IR_AST.GreaterOrEqual)

    # Instructions to ease implementation of short-circuiting
    class Copy(Instruction):
        def __init__(self, src, dst) -> None:
            super().__init__()
            self.src = src
            self.dst = dst

        def __eq__(self, other) -> bool:
            return (
                isinstance(other, IR_AST.Copy)
                and self.src == other.src
                and self.dst == other.dst
            )

    class Jump(Instruction):
        def __init__(self, target) -> None:
            super().__init__()
            self.target = target

        def __eq__(self, other) -> bool:
            return isinstance(other, IR_AST.Jump) and self.target == other.target

    class JumpIfZero(Instruction):
        def __init__(self, condition, target) -> None:
            super().__init__()
            self.condition = condition  # Val
            self.target = target

        def __eq__(self, other) -> bool:
            return (
                isinstance(other, IR_AST.JumpIfZero)
                and self.condition == other.condition
                and self.target == other.target
            )

    class JumpIfNotZero(Instruction):
        def __init__(self, condition, target) -> None:
            super().__init__()
            self.condition = condition  # Val
            self.target = target

        def __eq__(self, other) -> bool:
            return (
                isinstance(other, IR_AST.JumpIfNotZero)
                and self.condition == other.condition
                and self.target == other.target
            )

    class Label(Instruction):
        def __init__(self, name) -> None:
            super().__init__()
            self.name = name  # Identifier

        def __eq__(self, other) -> bool:
            return isinstance(other, IR_AST.Label) and self.name == other.name


# type: ignore
