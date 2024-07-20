"""AST definitions for intermediate representation

ASDL specification

program = Program(function_definition)
function_definition = Function(identifier, instruction* body)
instruction = Return(val) | Unary(unary_operator, val src, val dst)
val = Constant(int) | Var(identifier)
unary_operator = Complement | Negate

Constraints

The dst val in Unary cannot be a constant
"""

class INTERMEDIATE_AST:

    class Program:
        def __init__(self, function_definition):
            self.function_definition = function_definition
            
        def __eq__(self, other) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Program) and self.function_definition == other.function_definition


    class Function:
        def __init__(self, name, instructions):
            self.name = name
            self.instructions = instructions
            
        def __eq__(self, other) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Function) and self.name == other.name and self.instructions == other.instructions


    class Instruction:
        pass

    class Return(Instruction):
        def __init__(self, val) -> None:
            super().__init__()
            self.val = val
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Return) and self.val == other.val
            
            
    class UnaryOperation(Instruction):
        def __init__(self, unary_operator, src_val, dst_val) -> None:
            super().__init__()
            self.unary_operator = unary_operator
            self.src_val = src_val
            self.dst_val = dst_val
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.UnaryOperation) and self.unary_operator == other.unary_operator and self.src_val == other.src_val and self.dst_val == other.dst_val
        
    class Val:
        pass
        
    class Constant(Val):
        def __init__(self, value) -> None:
            super().__init__()
            self.value = value
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Constant) and self.value == other.value
        
    class Var(Val):
        def __init__(self, identifier) -> None:
            super().__init__()
            self.identifier = identifier
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Var) and self.identifier == other.identifier
        
    class UnaryOperator:
        pass
        
    class Complement:
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Complement)
        
    class Negation:
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Negation)
    
 # type: ignore
 