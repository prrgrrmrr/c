"""AST definitions and parsing routines

program = Program(function_definition)
function_definition = Function(identifier name, statement body)
statement = Return(exp)
exp = Constant(int) | Unary(unary_operator, exp)
unary_operator = Complement | Negate
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
        
    # Operators
    class Operator:
        pass
    
    class Complement(Operator):
        def __init__(self) -> None:
            super().__init__()
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Complement)
    
    class Negation(Operator):
        def __init__(self) -> None:
            super().__init__()
            
        def __eq__(self, other) -> bool:
            return isinstance(other, AST.Negation)
        
 # type: ignore
 