#!/opt/homebrew/bin/python3
import sys
import code
import parser

def assemble(path)->str:
    machine_code = ""
    p = parser.Parser(path)
    c = code.Code()
    while p.has_more_commands() == True:
        line = ""
        p.advance()
        match p.command_type():
            case parser.CommandType.A_COMMAND:
                address = int(p.symbol(), 10)
                assert address < 2**15
                line += "0"
                line += bin(address)[2:].zfill(15)
            case parser.CommandType.C_COMMAND:
                line += "111"
                if p.cur_code.find("=") == -1:
                    line += c.comp_map[p.comp()]
                    line += c.dest_map["null"]
                    line += c.jump_map[p.jump()]
                elif p.cur_code.find(";") == -1:
                    line += c.comp_map[p.comp()]
                    line += c.dest_map[p.dest()]
                    line += c.jump_map["null"]
                else:
                    line += ""
            case parser.CommandType.L_COMMAND:
                pass
        assert len(line) == 16
        machine_code += f"{line}\n"
    return machine_code

    

def save_as_hack(original_path:str, machine_code:str)->None:
    assert len(machine_code) > 0
    hack_filepath = original_path.replace(".asm", ".hack")
    with open(hack_filepath, "w") as f:
        f.write(machine_code)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[-] Usage: ./assembler.py <asm_filepath>")
        sys.exit(1)
    if sys.argv[1][-4:] != ".asm":
        print("[-] This is not an Nand2Tetris assembly source file")
        sys.exit(1)
    asm_filepath = sys.argv[1]
    machine_code = assemble(asm_filepath)
    save_as_hack(asm_filepath, machine_code)
    print("[*] done!")
