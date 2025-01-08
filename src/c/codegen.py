"""Converts IR AST to another tree representation useful for assembly generation"""

from functools import reduce
from c.intermediate_tree import INTERMEDIATE_AST
from c.assembly_tree import ASSEMBLY_AST

def asm_tree(ir_ast):
    """Generates tree of assembly instructions from intermediate representation AST - this step uses pseudo registers for variables"""
    
    # Simple if-else for now
    # TODO Visitor design pattern solves this better by defining visit method for each node
    
    # Program
    if isinstance(ir_ast, INTERMEDIATE_AST.Program):
        function_definition = asm_tree(ir_ast.function_definition)
        return ASSEMBLY_AST.Program(function_definition)
    
    # Function
    elif isinstance(ir_ast, INTERMEDIATE_AST.Function):
        name = ir_ast.name
        assert isinstance(ir_ast.instructions, tuple) # TODO remove
        instructions = reduce(lambda acc, inst: acc + inst, (asm_tree(inst) for inst in ir_ast.instructions)) # TODO this is inefficient - use a O(1) list append
        return ASSEMBLY_AST.Function(name, instructions)
    
    # Expressions
    
    # Unary expressions
    elif isinstance(ir_ast, INTERMEDIATE_AST.UnaryOperation):
        # Note that vals in IR can be identifiers (Var) or constants (Constant)
        # src, dst tmp vars will be replaced by pseudo registers by recursive calls
        # constants will be converted to immediate asm values
        src = asm_tree(ir_ast.src_val)
        dst = asm_tree(ir_ast.dst_val)
        unary_operator = asm_tree(ir_ast.unary_operator)
        # If dst is converted to a immediate value, it will be fixed in later fix stages to become a register (or stack reference if that is allowed by assembly)
        return (ASSEMBLY_AST.Mov(src, dst), ASSEMBLY_AST.UnaryOperation(unary_operator, dst))
    
    # Binary expressions
    elif isinstance(ir_ast, INTERMEDIATE_AST.BinaryOperation):
        src1 = asm_tree(ir_ast.src_val1)
        src2 = asm_tree(ir_ast.src_val2)
        dst = asm_tree(ir_ast.dst_val)
        if isinstance(ir_ast.binary_operator, INTERMEDIATE_AST.Addition) or isinstance(ir_ast.binary_operator, INTERMEDIATE_AST.Subtraction) or isinstance(ir_ast.binary_operator, INTERMEDIATE_AST.Multiplication):
            binary_operator = asm_tree(ir_ast.binary_operator)
            return (ASSEMBLY_AST.Mov(src1, dst), ASSEMBLY_AST.BinaryOperation(binary_operator, src2, dst))
        elif isinstance(ir_ast.binary_operator, INTERMEDIATE_AST.Division):
            return (ASSEMBLY_AST.Mov(src1, ASSEMBLY_AST.Register(ASSEMBLY_AST.AX())), ASSEMBLY_AST.Cdq(), ASSEMBLY_AST.Idiv(src2), ASSEMBLY_AST.Mov(ASSEMBLY_AST.Register(ASSEMBLY_AST.AX()), dst))
        elif isinstance(ir_ast.binary_operator, INTERMEDIATE_AST.Remainder):
            return (ASSEMBLY_AST.Mov(src1, ASSEMBLY_AST.Register(ASSEMBLY_AST.AX())), ASSEMBLY_AST.Cdq(), ASSEMBLY_AST.Idiv(src2), ASSEMBLY_AST.Mov(ASSEMBLY_AST.Register(ASSEMBLY_AST.DX()), dst))
        
    # Operators
    
    # Unary Operators
    elif isinstance(ir_ast, INTERMEDIATE_AST.Complement):
        return ASSEMBLY_AST.Complement()
    elif isinstance(ir_ast, INTERMEDIATE_AST.Negation):
        return ASSEMBLY_AST.Negation()
    
    # Binary operators
    elif isinstance(ir_ast, INTERMEDIATE_AST.Addition):
        return ASSEMBLY_AST.Add()
    elif isinstance(ir_ast, INTERMEDIATE_AST.Subtraction):
        return ASSEMBLY_AST.Sub()
    elif isinstance(ir_ast, INTERMEDIATE_AST.Multiplication):
        return ASSEMBLY_AST.Mult()
    # Division and Remainder handled in a special way above in binary operation by using Idiv and Cdq instructions
    
    # Return instruction
    elif isinstance(ir_ast, INTERMEDIATE_AST.Return):
        val = asm_tree(ir_ast.val)
        return ((ASSEMBLY_AST.Mov(val, ASSEMBLY_AST.Register(ASSEMBLY_AST.AX())), ASSEMBLY_AST.Ret()))
    
    # IR constants
    elif isinstance(ir_ast, INTERMEDIATE_AST.Constant):
        return ASSEMBLY_AST.Imm(ir_ast.value)
    
    # IR vars (tmp identifiers)
    elif isinstance(ir_ast, INTERMEDIATE_AST.Var):
        return ASSEMBLY_AST.Pseudo(ir_ast.identifier)
    
    
def replace_pseudo_registers(asm_ast, offset_dict):
    # Replace pseudo registers in asm tree from IR GEN with stack references
    # offset_dict stores stack offset in bytes for given tmp identifier
    # We don't want to rebuild an entire tree here - keep what we can
    
    # Program
    if isinstance(asm_ast, ASSEMBLY_AST.Program):
        asm_ast.function_definition = replace_pseudo_registers(asm_ast.function_definition, offset_dict)
        
    # Function
    elif isinstance(asm_ast, ASSEMBLY_AST.Function):
        # Already a list of asm instructions - no fear of getting an iterable from recursive call here
        instructions = tuple(replace_pseudo_registers(inst, offset_dict) for inst in asm_ast.instructions)
        asm_ast.instructions = instructions
        
    # asm instructions
    
    # Unary asm instruction
    elif isinstance(asm_ast, ASSEMBLY_AST.UnaryOperation):
        asm_ast.operand = replace_pseudo_registers(asm_ast.operand, offset_dict)
       
    # Binary asm instruction
    elif isinstance(asm_ast, ASSEMBLY_AST.BinaryOperation):
        asm_ast.src = replace_pseudo_registers(asm_ast.src, offset_dict)
        asm_ast.dst = replace_pseudo_registers(asm_ast.dst, offset_dict)
        
    # Idiv
    elif isinstance(asm_ast, ASSEMBLY_AST.Idiv):
        asm_ast.operand = replace_pseudo_registers(asm_ast.operand, offset_dict)
        
    # Mov
    elif isinstance(asm_ast, ASSEMBLY_AST.Mov):
        asm_ast.src = replace_pseudo_registers(asm_ast.src, offset_dict)
        asm_ast.dst = replace_pseudo_registers(asm_ast.dst, offset_dict)
    
    # Replace tmp identifier by stack reference
    elif isinstance(asm_ast, ASSEMBLY_AST.Pseudo):
        if asm_ast.identifier in offset_dict:
            offset = offset_dict[asm_ast.identifier]
        else:
            offset = 4 # 4 bytes for int
            key = max(offset_dict, key = offset_dict.get, default = None)
            if key:
                offset = 4 + offset_dict[key]
            offset_dict[asm_ast.identifier] = offset
        return ASSEMBLY_AST.StackOffset(offset)
    
    # If none of above, don't touch
    return asm_ast

def fix_instructions(asm_ast, stack_alloc):
    # Keep tree and change only what needs to be changed
    
    # Program
    if isinstance(asm_ast, ASSEMBLY_AST.Program):
        asm_ast.function_definition = fix_instructions(asm_ast.function_definition, stack_alloc)
        
    # Function
    elif isinstance(asm_ast, ASSEMBLY_AST.Function):
        # Add stack frame allocation for function (this is a high level asm tree instruction, actual asm instructions emitted by asm code emitter)
        instructions = [ASSEMBLY_AST.AllocateStack(stack_alloc)]
        for inst in asm_ast.instructions:
            fixed = fix_instructions(inst, stack_alloc)
            if isinstance(fixed, tuple):
                instructions.extend(fixed)
            else:
                instructions.append(fixed)
        asm_ast.instructions = tuple(instructions)
        
    # Fix Mov asm instruction - src and dst cannot be both stack references so we use our scratch register R10 as intermediate
    elif isinstance(asm_ast, ASSEMBLY_AST.Mov):
        if isinstance(asm_ast.src, ASSEMBLY_AST.StackOffset) and isinstance(asm_ast.dst, ASSEMBLY_AST.StackOffset):
            return (
                ASSEMBLY_AST.Mov(asm_ast.src, ASSEMBLY_AST.Register(ASSEMBLY_AST.R10())),
                ASSEMBLY_AST.Mov(ASSEMBLY_AST.Register(ASSEMBLY_AST.R10()), asm_ast.dst)
            )
            
    # Fix Add, Sub and Mult
    elif isinstance(asm_ast, ASSEMBLY_AST.BinaryOperation):
        # Fix Add and Sub like Mov above
        if isinstance(asm_ast.binary_operator, ASSEMBLY_AST.Add) or isinstance(asm_ast.binary_operator, ASSEMBLY_AST.Sub):
            if isinstance(asm_ast.src, ASSEMBLY_AST.StackOffset) and isinstance(asm_ast.dst, ASSEMBLY_AST.StackOffset):
                return (
                    ASSEMBLY_AST.Mov(asm_ast.src, ASSEMBLY_AST.Register(ASSEMBLY_AST.R10())),
                    ASSEMBLY_AST.BinaryOperation(
                        ASSEMBLY_AST.Add() if isinstance(asm_ast.binary_operator, ASSEMBLY_AST.Add) else ASSEMBLY_AST.Sub(),
                        ASSEMBLY_AST.Register(ASSEMBLY_AST.R10()),
                        asm_ast.dst
                    )
                )
                
        # Fix Mult
        elif isinstance(asm_ast.binary_operator, ASSEMBLY_AST.Mult):
            # Mult instruction can’t use a memory address as its destination, regardless of its source operand
            # To fix an instruction’s destination operand, we use the R11 register instead of R10
            if isinstance(asm_ast.dst, ASSEMBLY_AST.StackOffset):
                return (
                    ASSEMBLY_AST.Mov(asm_ast.dst, ASSEMBLY_AST.Register(ASSEMBLY_AST.R11())),
                    ASSEMBLY_AST.BinaryOperation(
                        ASSEMBLY_AST.Mult(),
                        asm_ast.src,
                        ASSEMBLY_AST.Register(ASSEMBLY_AST.R11())
                    ),
                    ASSEMBLY_AST.Mov(ASSEMBLY_AST.Register(ASSEMBLY_AST.R11()), asm_ast.dst),
                )
          
    # Fix Idiv asm instruction - Whenever idiv needs to operate on a constant, we copy that constant into our scratch register first
    elif isinstance(asm_ast, ASSEMBLY_AST.Idiv):
        if isinstance(asm_ast.operand, ASSEMBLY_AST.Imm):
            return (
                ASSEMBLY_AST.Mov(asm_ast.operand, ASSEMBLY_AST.Register(ASSEMBLY_AST.R10())),
                ASSEMBLY_AST.Idiv(ASSEMBLY_AST.Register(ASSEMBLY_AST.R10()))
            )
    
    # Else, don't touch
    return asm_ast

def asmgen(ir_ast):
    asm_ast = asm_tree(ir_ast)
    offset_dict = {} # Stack offset in bytes for given identifier key
    asm_ast = replace_pseudo_registers(asm_ast, offset_dict)
    stack_alloc = 0
    key = max(offset_dict, key = offset_dict.get, default = None)
    if key:
        stack_alloc = offset_dict[key]
    asm_ast = fix_instructions(asm_ast, stack_alloc)
    return asm_ast
