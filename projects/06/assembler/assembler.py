#!/opt/homebrew/bin/python3
import sys
import code
import parser
import symtab

syms = symtab.SymbolTable()

def sympass_record_labels(p:parser.Parser)->parser.Parser:
    global syms
    rom_ptr = 0
    while p.has_more_commands() == True:
        p.advance()
        match p.command_type():
            case parser.CommandType.A_COMMAND:
                rom_ptr += 1
            case parser.CommandType.C_COMMAND:
                rom_ptr += 1
            case parser.CommandType.L_COMMAND:
                symbol = p.symbol()
                if syms.contains(symbol) == False:
                    syms.add_entry(symbol, rom_ptr)
    p.cur_line = 0
    p.cur_code = ""
    return p

def sympass_translate_symbol(p:parser.Parser)->parser.Parser:
    global syms
    ram_ptr = 16
    while p.has_more_commands() == True:
        p.advance()
        match p.command_type():
            case parser.CommandType.A_COMMAND:
                symbol = p.symbol()
                try:
                    int(symbol, 10)
                except ValueError:
                    if syms.contains(symbol) == False:
                        syms.add_entry(symbol, ram_ptr)
                        ram_ptr += 1
                    p.cur_code = "@"+str(syms.get_address(symbol))
        p.code[p.cur_line-1] = p.cur_code
    p.cur_line = 0
    p.cur_code = ""
    return p

def assemble(path)->str:
    machine_code = ""
    c = code.Code()
    p = parser.Parser(path)
    p = sympass_record_labels(p)
    p = sympass_translate_symbol(p)
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
                continue
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
        print("[-] This is not a Nand2Tetris assembly source file")
        sys.exit(1)
    asm_filepath = sys.argv[1]
    machine_code = assemble(asm_filepath)
    save_as_hack(asm_filepath, machine_code)
    print("[*] done!")
