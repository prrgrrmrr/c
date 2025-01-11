"""AST definitions and parsing routines

program = Program(function_definition)
function_definition = Function(identifier name, block_item* body)
block_item = S(statement) | D(declaration)
statement = Return(exp) | Expression(exp) | Null
exp = Constant(int) | Var(identifier) | Unary(unary_operator, exp) | Binary(binary_operator, exp, exp) | Assignment(exp, exp)
unary_operator = Complement | Negate | Not
binary_operator = Add | Subtract | Multiply | Divide | Remainder | And | Or | Equal | NotEqual | LessThan | LessOrEqual | GreaterThan | GreaterOrEqual
declaration = Declaration(identifier name, exp? init)
"""


class AST:

    class Program:
        def __init__(self, function_definition):
            self.function_definition = function_definition

        def __eq__(self, other) -> bool:
            return (
                isinstance(other, AST.Program)
                and self.function_definition == other.function_definition
            )

    class Function:
        def __init__(self, name, body):
            self.name = name
            self.body = body

        def __eq__(self, other) -> bool:
            return (
                isinstance(other, AST.Function)
                and self.name == other.name
                and self.body == other.body
            )
            
    # Block items
    class BlockItem:
        pass
    
    class S(BlockItem):
        def __init__(self, statement):
            super().__init__()
            self.statement = statement
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.S) and self.statement == other.statement
        
    class D(BlockItem):
        def __init__(self, declaration):
            super().__init__()
            self.declaration = declaration
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.D) and self.declaration == other.declaration
        
    # Declarations - this is not a statement but a way to tell the compiler a variable exists
    class Declaration:
        def __init__(self, name, initializer) -> None:
            self.name = name
            self.initializer = initializer
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Declaration) and self.name == other.name and self.initializer == other.initializer

    # Statements
    class Statement:
        pass

    class Return(Statement):
        def __init__(self, exp) -> None:
            super().__init__()
            self.exp = exp

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Return) and self.exp == other.exp
        
    class Expression(Statement):
        def __init__(self, exp) -> None:
            super().__init__()
            self.exp = exp

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Expression) and self.exp == other.exp
        
    class Null(Statement):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Null)

    # Expressions
    class Exp:
        pass

    class Constant(Exp):
        def __init__(self, value) -> None:
            super().__init__()
            self.value = value

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Constant) and self.value == other.value
        
    class Var(Exp):
        def __init__(self, identifier) -> None:
            super().__init__()
            self.identifier = identifier

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Var) and self.identifier == other.identifier
        
    class Assignment(Exp):
        def __init__(self, lhs, rhs) -> None:
            super().__init__()
            self.lhs = lhs
            self.rhs = rhs

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Assignment) and self.lhs == other.lhs and self.rhs == other.rhs

    class UnaryOperation(Exp):
        def __init__(self, unary_operator, exp) -> None:
            super().__init__()
            self.unary_operator = unary_operator
            self.exp = exp

        def __eq__(self, other) -> bool:
            return (
                isinstance(other, AST.UnaryOperation)
                and self.unary_operator == other.unary_operator
                and self.exp == other.exp
            )

    class BinaryOperation(Exp):
        def __init__(self, binary_operator, lhs, rhs) -> None:
            super().__init__()
            self.binary_operator = binary_operator
            self.lhs = lhs
            self.rhs = rhs

        def __eq__(self, other) -> bool:
            return (
                isinstance(other, AST.BinaryOperation)
                and self.binary_operator == other.binary_operator
                and self.lhs == other.lhs
                and self.rhs == other.rhs
            )

    # Unary operators
    class UnaryOperator:
        pass

    class Complement(UnaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Complement)

    # Logical not
    class Negation(UnaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Negation)

    class Not(UnaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Not)

    # Binary operators
    class BinaryOperator:
        pass

    class Subtraction(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Subtraction)

    class Addition(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Addition)

    class Multiplication(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Multiplication)

    class Division(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Division)

    class Remainder(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Remainder)

    # Binary logical and relational binary operators
    class And(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.And)

    class Or(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Or)

    class Equal(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Equal)

    class NotEqual(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.NotEqual)

    class LessThan(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.LessThan)

    class LessOrEqual(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.LessOrEqual)

    class GreaterThan(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.GreaterThan)

    class GreaterOrEqual(BinaryOperator):
        def __init__(self) -> None:
            super().__init__()

        def __eq__(self, other) -> bool:
            return isinstance(other, AST.GreaterOrEqual)

# type: ignore
