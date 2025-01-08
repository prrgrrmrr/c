"""AST definitions for assembly instructions

ASDL specification

program = Program(function_definition) 
function_definition = Function(identifier name, instruction* instructions) 
instruction = Mov(operand src, operand dst) | Unary(unary_operator, operand) | AllocateStack(int) | Ret 
unary_operator = Neg | Not 
operand = Imm(int) | Stack(int) | Reg(reg) | Pseudo(identifier)
reg = AX | R10

"""

class ASSEMBLY_AST:

    class Program:
        def __init__(self, function_definition):
            self.function_definition = function_definition
            
        def __eq__(self, other) -> bool:
            return isinstance(other, ASSEMBLY_AST.Program) and self.function_definition == other.function_definition

    class Function:
        def __init__(self, name, instructions):
            self.name = name
            self.instructions = instructions
            
        def __eq__(self, other) -> bool:
            return isinstance(other, ASSEMBLY_AST.Function) and self.name == other.name and self.instructions == other.instructions

    class Instruction:
        pass

    class Mov(Instruction):
        def __init__(self, src, dst) -> None:
            super().__init__()
            self.src = src
            self.dst = dst
            
        def __eq__(self, other) -> bool:
            return isinstance(other, ASSEMBLY_AST.Mov) and self.src == other.src and self.dst == other.dst

    class Ret(Instruction):
        def __init__(self) -> None:
            super().__init__()
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Ret)
        
    class UnaryOperation(Instruction):
        def __init__(self, unary_operator, operand) -> None:
            super().__init__()
            self.unary_operator = unary_operator
            self.operand = operand
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.UnaryOperation) and self.unary_operator == other.unary_operator and self.operand == other.operand
        
    class BinaryOperation(Instruction):
        def __init__(self, binary_operator, src, dst):
            """

            :param binary_operator: instruction
            :param src: immediate value, register or stack offset
            :param dst: register or stack offset
            """
            super().__init__()
            self.binary_operator = binary_operator
            self.src = src
            self.dst = dst
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.BinaryOperation) and self.binary_operator == other.binary_operator and self.src == other.src and self.dst == other.dst
       
    class AllocateStack(Instruction):
        def __init__(self, nbytes) -> None:
            super().__init__()
            self.nbytes = nbytes
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.AllocateStack) and self.nbytes == other.nbytes
                
    class Operand:
        pass
    
    class Register(Operand):
        def __init__(self, reg) -> None: # reg is the actual register used (see below)
            super().__init__()
            self.reg = reg
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Register) and self.reg == other.reg
        
    class RegisterName:
        pass
    
    # Registers here are neither 32 bits nor 64 bits - it's just the name, actual version is chosen in code emission
    class AX(RegisterName):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.AX)
        
    class DX(RegisterName):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.DX)
        
    class R10(RegisterName):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.R10)
        
    class R11(RegisterName):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.R11)
        
    class Pseudo(Operand):
        def __init__(self, identifier) -> None:
            super().__init__()
            self.identifier = identifier
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Pseudo) and self.identifier == other.identifier
    
    class StackOffset(Operand):
        def __init__(self, offset) -> None: # Offset in bytes from RBP - this is a positive int
            super().__init__()
            self.offset = offset
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.StackOffset) and self.offset == other.offset
    
    class Imm(Operand):
        def __init__(self, value) -> None:
            super().__init__()
            self.value = value
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Imm) and self.value == other.value
        
    # Operators
    class UnaryOperator:
        pass
    
    class Negation(UnaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Negation)
        
    class Complement(UnaryOperator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Complement)
        
    class BinaryOprator:
        pass
    
    class Add(BinaryOprator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Add)
        
    class Sub(BinaryOprator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Sub)
        
    class Mult(BinaryOprator):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Mult)

    # Note that Idiv and Remainder are treated directly as instructions and they don't extend BinaryOperator
    # because converting them to assembly takes more steps than Add, Sub, Mult
    class Idiv(Instruction):
        def __init__(self, operand):
            self.operand = operand
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Idiv) and self.operand == other.operand
        
    # class Remainder(Instruction):
    #     def __init__(self, operand):
    #         self.operand = operand
            
    #     def __eq__(self, other: object) -> bool:
    #         return isinstance(other, ASSEMBLY_AST.Remainder) and self.operand == other.operand
        
    # Sign extension
    class Cdq(Instruction):
        def __init__(self) -> None:
            super().__init__()
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Cdq)
     
 # type: ignore
 