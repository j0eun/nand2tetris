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
    w = codewriter.CodeWriter(targets[0].replace(".vm", ".asm"))
    w.writer_init() # 부트스트랩 코드 삽입
    for target in targets:
        p = parser.Parser(target)
        w.set_file_name(target.replace(".vm", ".asm"))
        while p.has_more_commands():
            p.advance()
            match p.command_type():
                case parser.CommandType.C_ARITHMETIC:
                    w.write_arithmetic(p.arg1())
                case parser.CommandType.C_PUSH:
                    w.write_push_pop("push", p.arg1(), p.arg2())
                case parser.CommandType.C_POP:
                    w.write_push_pop("pop", p.arg1(), p.arg2())
                case parser.CommandType.C_LABEL:
                    w.write_label(p.arg1())
                case parser.CommandType.C_GOTO:
                    w.write_goto(p.arg1())
                case parser.CommandType.C_IF:
                    w.write_if(p.arg1())
                case parser.CommandType.C_CALL:
                    w.write_call(p.arg1(), p.arg2())
                case parser.CommandType.C_RETURN:
                    w.write_return()
                case parser.CommandType.C_FUNCTION:
                    w.write_function(p.arg1(), p.arg2())
        del p
    del w
    print("[*] done!")