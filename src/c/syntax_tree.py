"""AST definitions and parsing routines

program = Program(function_definition)
function_definition = Function(identifier name, statement body)
statement = Return(exp)
exp = Constant(int) | Unary(unary_operator, exp) | Binary(binary_operator, exp, exp)
unary_operator = Complement | Negate
binary_operator = Add | Subtract | Multiply | Divide | Remainder
"""

class AST:

    class Program:
        def __init__(self, function_definition):
            self.function_definition = function_definition
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Program) and self.function_definition == other.function_definition
            
    class Function:
        def __init__(self, name, body):
            self.name = name
            self.body = body
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Function) and self.name == other.name and self.body == other.body

    # Statements
    class Statement:
        pass

    class Return(Statement):
        def __init__(self, exp) -> None:
            super().__init__()
            self.exp = exp
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Return) and self.exp == other.exp

    # Expressions
    class Exp:
        pass

    class Constant(Exp):
        def __init__(self, value) -> None:
            super().__init__()
            self.value = value
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Constant) and self.value == other.value
        
    class UnaryOperation(Exp):
        def __init__(self, unary_operator, exp) -> None:
            super().__init__()
            self.unary_operator = unary_operator
            self.exp = exp
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.UnaryOperation) and self.unary_operator == other.unary_operator and self.exp == other.exp
        
    class BinaryOperation(Exp):
        def __init__(self, binary_operator, lhs, rhs) -> None:
            super().__init__()
            self.binary_operator = binary_operator
            self.lhs = lhs
            self.rhs = rhs
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.BinaryOperation) and self.binary_operator == other.binary_operator and self.lhs == other.lhs and self.rhs == other.rhs
        
    # Unary operators
    class UnaryOperator:
        pass
    
    class Complement(UnaryOperator):
        def __init__(self) -> None:
            super().__init__()
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Complement)
    
    class Negation(UnaryOperator):
        def __init__(self) -> None:
            super().__init__()
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Negation)
        
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
        
 # type: ignore
 