"""AST definitions for assembly instructions"""

class ASSEMBLY_AST:

    class Program:
        def __init__(self, function_definition):
            self.function_definition = function_definition
            
        def __eq__(self, other) -> bool:
            return isinstance(other, ASSEMBLY_AST.Program) and self.function_definition == other.function_definition
        
        
    class Instructions:
        def __init__(self, instructions) -> None:
            self.instructions = instructions
            
        def __eq__(self, other) -> bool:
            return isinstance(other, ASSEMBLY_AST.Instructions) and self.instructions == other.instructions

    class Function:
        def __init__(self, name, instructions):
            self.name = name
            self.instructions = instructions
            assert isinstance(self.instructions, ASSEMBLY_AST.Instructions)
            
        def __eq__(self, other) -> bool:
            return isinstance(other, ASSEMBLY_AST.Function) and self.name == other.name and self.instructions == other.instructions


    class Instruction:
    
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Instruction)


    class Mov(Instruction):
        def __init__(self, src, dest) -> None:
            super().__init__()
            self.src = src
            self.dest = dest
            
        def __eq__(self, other) -> bool:
            return isinstance(other, ASSEMBLY_AST.Mov) and self.src == other.src and self.dest == other.dest


    class Ret(Instruction):
        def __init__(self) -> None:
            super().__init__()
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Ret)
            
            
    class Operand:
    
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Operand)
    
    
    class Register(Operand):
    
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Register)
    
    
    class Imm(Operand):
        def __init__(self, value) -> None:
            super().__init__()
            self.value = value
            
        def __eq__(self, other: object) -> bool:
            return isinstance(other, ASSEMBLY_AST.Imm) and self.value == other.value
        
 # type: ignore
 