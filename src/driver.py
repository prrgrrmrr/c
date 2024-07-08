import subprocess
import sys
import shutil
from compile import compile

args = sys.argv[1:]
input_path = [a for a in args if a not in ("--lex", "--parse", "--codegen", "-S")][0]

assert input_path.endswith(".c")
preprocessor_output_path = input_path[:-2] + ".i"
subprocess.run(["gcc", "-E", "-P", input_path, "-o", preprocessor_output_path])

other_args = [a for a in args if a != input_path]
args = [preprocessor_output_path] + other_args
output = compile(args)
if output:
    # Emit
    assembly_output_path = input_path[:-2] + ".s"
    with open(assembly_output_path, "w") as fd:
        output.seek(0)
        shutil.copyfileobj(output, fd)
    # Assemble and link
    subprocess.run(["gcc", assembly_output_path, "-o", input_path[:-2]])
