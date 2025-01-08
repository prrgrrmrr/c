"""AST definitions for intermediate representation

ASDL specification

program = Program(function_definition)
function_definition = Function(identifier, instruction* body)
instruction = Return(val) | Unary(unary_operator, val src, val dst) | Binary(binary_operator, val src1, val src2, val dst)
val = Constant(int) | Var(identifier)
unary_operator = Complement | Negate
binary_operator = Add | Subtract | Multiply | Divide | Remainder

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
            
    class BinaryOperation(Instruction):
        def __init__(self, binary_operator, src_val1, src_val2, dst_val) -> None:
            super().__init__()
            self.binary_operator = binary_operator
            self.src_val1 = src_val1
            self.src_val2 = src_val2
            self.dst_val = dst_val
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.BinaryOperation) and self.binary_operator == other.binary_operator and self.src_val1 == other.src_val1 and self.src_val2 == other.src_val2 and self.dst_val == other.dst_val
        
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
        
    class Complement(UnaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Complement)
        
    class Negation(UnaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Negation)
        
    class BinaryOperator:
        pass
        
    class Addition(BinaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Addition)
    
    class Subtraction(BinaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Subtraction)
        
    class Multiplication(BinaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Multiplication)
        
    class Division(BinaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Division)
        
    class Remainder(BinaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, INTERMEDIATE_AST.Remainder)
        
 # type: ignore 
 