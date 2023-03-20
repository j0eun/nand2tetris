#!/opt/homebrew/bin/python3
import sys
import parser
import codewriter

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[!] Usage: ./translator.py <VM_SOURCE_PATH> [VM_SOURCE_PATH2, ...]")
        sys.exit(1)
    targets = sys.argv[1:]
    for target in targets:
        if len(target) < 3 or target[-3:].lower() != ".vm":
            print(f"[!] not VM source file : {target}")
            sys.exit(1)
    for target in targets:
        p = parser.Parser(target)
        w = codewriter.CodeWriter(target.replace(".vm", ".asm"))
        while p.has_more_commands():
            p.advance()
            match p.command_type():
                case parser.CommandType.C_ARITHMETIC:
                    w.write_arithmetic(p.arg1())
                case parser.CommandType.C_PUSH:
                    w.write_push_pop("push", p.arg1(), p.arg2())
                case parser.CommandType.C_POP:
                    w.write_push_pop("pop", p.arg1(), p.arg2())
        del w
        del p
    print("[*] done!")