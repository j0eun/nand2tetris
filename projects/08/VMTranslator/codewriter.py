import os
import time

REGISTRY_SET = {"A", "M", "D"}

class CodeWriter():
    # 출력 파일/스트림을 열고 어셈블리 코드를 작성할 준비를 한다.
    def __init__(self, asm_file_path:str) -> None:
        self.__vm_file_name = os.path.splitext(asm_file_path)[0].split("/")[-1]
        self.f = open(asm_file_path, "w")
        self.predefined = {
            # RAM[0]~RAM[15]        : 16개의 가상 레지스터
            # RAM[16]~RAM[255]      : 정적 변수(전역 변수)
            # RAM[256]~RAM[2047]    : 스택
            # RAM[2048]~RAM[16383]  : 힙(객체와 배열 저장에 활용)
            # RAM[16384]~RAM[24575] : I/O 전용 메모리
            # RAM[24575]~RAM[32767] : 사용하지 않는 메모리 공간
            "SP": "SP", # RAM[0]
            "LCL": "LCL", # RAM[1]
            "ARG": "ARG", # RAM[2]
            "THIS": "THIS",  # RAM[3], this는 pointer 0에 의해 변경될 수 있음
            "THAT": "THAT",  # RAM[4], that은 pointer 1에 의해 변경될 수 있음
            "R0": "R0", "R1": "R1", "R2": "R2", "R3": "R3",
            "R4": "R4", "R5": "R5", "R6": "R6", "R7": "R7",
            "R8": "R8", "R9": "R9", "R10": "R10", "R11": "R11",
            "R12": "R12", "R13": "R13", "R14": "R14", "R15": "R15", # RAM[0]~RAM[15]
            "SCREEN": "SCREEN",    # RAM[16384], 스크린 I/O 전용 메모리
            "KBD": "KBD",       # RAM[24576], 키보드 I/O 전용 메모리

            "FALSE": 0,
            "TRUE": -1,
            "TEMP": 5,      # TEMP = RAM[5]~RAM[12]
            "STATIC": 16    # STATIC = RAM[16]~RAM[255]
        }
    
    # 출력 파일/스트림을 닫는다.
    def __del__(self) -> None:
        self.f.close()

    # CodeWriter에게 새로운 VM 파일 번역이 시작되었음을 알린다.
    def set_file_name(self, asm_file_path:str) -> None:
        self.__vm_file_name = os.path.splitext(asm_file_path)[0].split("/")[-1]

    # C_ARITHMETIC 타입의 명령을 작성한다.
    def write_arithmetic(self, command:str) -> None:
        code = ""
        match command.lower():
            case "add":
                code = self.__binary_add()
            case "sub":
                code = self.__binary_sub()
            case "neg":
                code = self.__unary_neg()
            case "eq":
                code = self.__binary_eq()
            case "gt":
                code = self.__binary_gt()
            case "lt":
                code = self.__binary_lt()
            case "and":
                code = self.__binary_and()
            case "or":
                code = self.__binary_or()
            case "not":
                code = self.__unary_not()
            case _:
                raise AssertionError("command is not C_ARITHMETIC type")
        self.f.write(code)
        
    # C_PUSH, C_POP 타입의 명령을 작성한다.
    # segment : 첫 번째 오퍼랜드
    # index : 두 번째 오퍼랜드
    def write_push_pop(self, command:str, segment:str, index:int) -> None:
        code = ""
        segment = segment.lower()
        match command.lower():
            case "push":
                if segment == "constant":
                    code += f"@{index}\n"
                    code += self.__push_reg("A")
                elif segment == "this":
                    code += f"@{self.predefined['THIS']}\n"
                    code += f"D=M\n"
                    code += f"@{index}\n"
                    code += f"A=D+A\n"
                    code += self.__push_reg("M")
                elif segment == "that":
                    code += f"@{self.predefined['THAT']}\n"
                    code += f"D=M\n"
                    code += f"@{index}\n"
                    code += f"A=D+A\n"
                    code += self.__push_reg("M")
                elif segment == "pointer":
                    if index == 0:      # point to THIS pointer
                        code += f"@{self.predefined['THIS']}\n"
                        code += self.__push_reg("M")
                    elif index == 1:    # point to THAT pointer
                        code += f"@{self.predefined['THAT']}\n"
                        code += self.__push_reg("M")
                    else:
                        raise AssertionError("invalid index value")
                elif segment == "local":
                    code += f"@{self.predefined['LCL']}\n"
                    code += f"D=M\n"
                    code += f"@{index}\n"
                    code += f"A=D+A\n"
                    code += self.__push_reg("M")
                elif segment == "argument":
                    code += f"@{self.predefined['ARG']}\n"
                    code += f"D=M\n"
                    code += f"@{index}\n"
                    code += f"A=D+A\n"
                    code += self.__push_reg("M")
                elif segment == "temp":
                    code += f"@{self.predefined['TEMP']+index}\n"
                    code += self.__push_reg("M")
                elif segment == "static":
                    code += f"@{self.predefined['STATIC']+index}\n"
                    code += self.__push_reg("M")
                else:
                    code += f"@{self.predefined[segment]}\n"
                    code += f"D=M\n"                # D=&segment[0]
                    code += f"@{index}\n"
                    code += f"A=D+A\n"              # A=&segment[index]
                    code += self.__push_reg("M")    # push semgent[index]
            case "pop":
                if segment == "pointer":
                    if index == 0:      # point to THIS pointer
                        code += self.__pop_reg("D")
                        code += f"@{self.predefined['THIS']}\n"
                        code += f"M=D\n"
                    elif index == 1:    # point to THAT pointer
                        code += self.__pop_reg("D")
                        code += f"@{self.predefined['THAT']}\n"
                        code += f"M=D\n"
                    else:
                        raise AssertionError("invalid index value")
                elif segment == "this":
                    code += f"@{self.predefined['THIS']}\n"
                    code += f"D=M\n"
                    code += f"@{index}\n"
                    code += f"D=D+A\n"
                    code += f"@{self.predefined['R13']}\n"
                    code += f"M=D\n"
                    code += self.__pop_reg("D")
                    code += f"@{self.predefined['R13']}\n"
                    code += f"A=M\n"
                    code += f"M=D\n"
                elif segment == "that":
                    code += f"@{self.predefined['THAT']}\n"
                    code += f"D=M\n"
                    code += f"@{index}\n"
                    code += f"D=D+A\n"
                    code += f"@{self.predefined['R13']}\n"
                    code += f"M=D\n"
                    code += self.__pop_reg("D")
                    code += f"@{self.predefined['R13']}\n"
                    code += f"A=M\n"
                    code += f"M=D\n"
                elif segment == "local":
                    code += f"@{self.predefined['LCL']}\n"
                    code += f"D=M\n"
                    code += f"@{index}\n"
                    code += f"D=D+A\n"
                    code += f"@{self.predefined['R13']}\n"
                    code += f"M=D\n"
                    code += self.__pop_reg("D")
                    code += f"@{self.predefined['R13']}\n"
                    code += f"A=M\n"
                    code += f"M=D\n"
                elif segment == "argument":
                    code += f"@{self.predefined['ARG']}\n"
                    code += f"D=M\n"
                    code += f"@{index}\n"
                    code += f"D=D+A\n"
                    code += f"@{self.predefined['R13']}\n"
                    code += f"M=D\n"
                    code += self.__pop_reg("D")
                    code += f"@{self.predefined['R13']}\n"
                    code += f"A=M\n"
                    code += f"M=D\n"
                elif segment == "temp":
                    code += self.__pop_reg("D")
                    code += f"@{self.predefined['TEMP']+index}\n"
                    code += f"M=D\n"
                elif segment == "static":
                    code += self.__pop_reg("D")
                    code += f"@{self.predefined['STATIC']+index}\n"
                    code += f"M=D\n"
                else:
                    code += f"@{self.predefined[segment]}\n"
                    code += f"D=M\n"                # D=&segment[0]
                    code += f"@{index}\n"
                    code += f"A=D+A\n"              # A=&segment[index]
                    code += self.__pop_reg("D")     # pop semgent[index]
            case _:
                raise AssertionError("command is not C_PUSH or C_POP type")
        self.f.write(code)
        return

    # 부트스트랩(최초 실행) 코드 (e.g. 일반적인 프로그래밍 언어의 main 함수)
    # 스택 포인터를 초기화하고 Sys.init 함수를 호출한다.
    def writer_init(self) -> None:
        code = ""
        code += f"@256\n"
        code += f"D=A\n"
        code += f"@SP\n"
        code += f"M=D\n"    # SP=256
        self.f.write(code)
        self.write_call("Sys.init", 0)
        return
    
    def write_label(self, label:str) -> None:
        code = ""
        code += f"({label})\n"
        self.f.write(code)
        return

    def write_goto(self, label:str) -> None:
        code = ""
        code += f"@{label}\n"
        code += f"0;JMP\n"
        self.f.write(code)
        return

    def write_if(self, label:str) -> None:
        code = ""
        code += self.__pop_reg("D")
        code += f"@{label}\n"
        code += f"D;JNE\n"
        self.f.write(code)
        return

    def write_call(self, func_name:str, numargs:int) -> None:
        ret_label = f"LABEL_RET_{self.__vm_file_name}_{func_name}.{time.time()}"    # generate an unique return-label
        code = ""
        code += f"@{ret_label}\n"
        code += self.__push_reg("A")    # push return-address
        code += f"@{self.predefined['LCL']}\n"
        code += self.__push_reg("M")    # push LCL
        code += f"@{self.predefined['ARG']}\n"
        code += self.__push_reg("M")    # push ARG
        code += f"@{self.predefined['THIS']}\n"
        code += self.__push_reg("M")    # push THIS
        code += f"@{self.predefined['THAT']}\n"
        code += self.__push_reg("M")    # push THAT
        code += f"@5\n"
        code += f"D=-A\n"
        code += f"@{numargs}\n"
        code += f"D=D-A\n"
        code += f"@{self.predefined['ARG']}\n"
        code += f"M=M-D\n"  # ARG = ARG-n-5
        code += f"@{self.predefined['SP']}\n"
        code += f"D=M\n"
        code += f"@{self.predefined['LCL']}\n"
        code += f"M=D\n"    # LCL=SP
        code += f"@{func_name}\n"
        code += f"0;JMP\n"  # goto func
        code += f"({ret_label})\n"  # define the return-label
        self.f.write(code)
        return

    def write_return(self) -> None:
        code = ""
        code += f"@{self.predefined['LCL']}\n"
        code += f"D=M\n"
        code += f"@{self.predefined['R13']}\n"
        code += f"M=D\n"    # FRAME=LCL
        code += f"@5\n"
        code += f"D=A\n"
        code += f"@{self.predefined['R13']}\n"
        code += f"A=M-D\n"
        code += f"D=M\n"
        code += f"@{self.predefined['R14']}\n"
        code += f"M=D\n"    # RET=*(FRAME-5)
        code += self.__pop_reg("D")
        code += f"@{self.predefined['ARG']}\n"
        code += f"A=M\n"
        code += f"M=D\n"    # *ARG=pop()
        code += f"@{self.predefined['ARG']}\n"
        code += f"D=M+1\n"
        code += f"@{self.predefined['SP']}\n"
        code += f"M=D\n"
        code += f"@1\n"
        code += f"D=A\n"
        code += f"@{self.predefined['R13']}\n"
        code += f"A=M-D\n"
        code += f"D=M\n"
        code += f"@{self.predefined['THAT']}\n"
        code += f"M=D\n"    # THAT=*(FRAME-1)
        code += f"@2\n"
        code += f"D=A\n"
        code += f"@{self.predefined['R13']}\n"
        code += f"A=M-D\n"
        code += f"D=M\n"
        code += f"@{self.predefined['THIS']}\n"
        code += f"M=D\n"    # THIS=*(FRAME-2)
        code += f"@3\n"
        code += f"D=A\n"
        code += f"@{self.predefined['R13']}\n"
        code += f"A=M-D\n"
        code += f"D=M\n"
        code += f"@{self.predefined['ARG']}\n"
        code += f"M=D\n"    # ARG=*(FRAME-3)
        code += f"@4\n"
        code += f"D=A\n"
        code += f"@{self.predefined['R13']}\n"
        code += f"A=M-D\n"
        code += f"D=M\n"
        code += f"@{self.predefined['LCL']}\n"
        code += f"M=D\n"    # LCL=*(FRAME-4)
        code += f"@{self.predefined['R14']}\n"
        code += f"A=M\n"
        code += f"0;JMP\n"  # goto RET
        self.f.write(code)
        return

    def write_function(self, func_name:str, numlocals:int) -> None:
        code = ""
        code += f"({func_name})\n"  # define a function-label
        for _ in range(numlocals):
            code += f"D=0\n"
            code += self.__push_reg("D")    # zeroize local variables
        self.f.write(code)
        return
        
    def __binary_add(self) -> str:
        code = ""
        code += self.__pop_reg("D")
        code += self.__pop_reg("A")
        code += f"D=A+D\n"
        code += self.__push_reg("D")
        return code
    
    def __binary_sub(self) -> str:
        code = ""
        code += self.__pop_reg("D")
        code += self.__pop_reg("A")
        code += f"D=A-D\n"
        code += self.__push_reg("D")
        return code

    def __binary_and(self) -> str:
        code = ""
        code += self.__pop_reg("D")
        code += self.__pop_reg("A")
        code += f"D=A&D\n"
        code += self.__push_reg("D")
        return code

    def __binary_or(self) -> str:
        code = ""
        code += self.__pop_reg("D")
        code += self.__pop_reg("A")
        code += f"D=A|D\n"
        code += self.__push_reg("D")
        return code

    def __binary_eq(self) -> str:
        unique_id = time.time()
        label_eq = f"EQ_{unique_id}"
        label_continue = f"CONTINUE_{unique_id}"
        code = ""
        code += self.__pop_reg("D")
        code += self.__pop_reg("A")
        code += f"D=A-D\n"
        code += f"@{label_eq}\n"
        code += f"D;JEQ\n"
        code += f"D={self.predefined['FALSE']}\n"
        code += f"@{label_continue}\n"
        code += f"0;JMP\n"
        code += f"({label_eq})\n"
        code += f"D={self.predefined['TRUE']}\n"
        code += f"({label_continue})\n"
        code += self.__push_reg("D")
        return code

    def __binary_gt(self) -> str:
        unique_id = time.time()
        label_gt = f"GT_{unique_id}"
        label_continue = f"CONTINUE_{unique_id}"
        code = ""
        code += self.__pop_reg("D")
        code += self.__pop_reg("A")
        code += f"D=A-D\n"
        code += f"@{label_gt}\n"
        code += f"D;JGT\n"
        code += f"D={self.predefined['FALSE']}\n"
        code += f"@{label_continue}\n"
        code += f"0;JMP\n"
        code += f"({label_gt})\n"
        code += f"D={self.predefined['TRUE']}\n"
        code += f"({label_continue})\n"
        code += self.__push_reg("D")
        return code

    def __binary_lt(self) -> str:
        unique_id = time.time()
        label_lt = f"LT_{unique_id}"
        label_continue = f"CONTINUE_{unique_id}"
        code = ""
        code += self.__pop_reg("D")
        code += self.__pop_reg("A")
        code += f"D=A-D\n"
        code += f"@{label_lt}\n"
        code += f"D;JLT\n"
        code += f"D={self.predefined['FALSE']}\n"
        code += f"@{label_continue}\n"
        code += f"0;JMP\n"
        code += f"({label_lt})\n"
        code += f"D={self.predefined['TRUE']}\n"
        code += f"({label_continue})\n"
        code += self.__push_reg("D")
        return code

    def __unary_neg(self) -> str:
        code = ""
        code += self.__pop_reg("D")
        code += f"D=-D\n"
        code += self.__push_reg("D")
        return code

    def __unary_not(self) -> str:
        code = ""
        code += self.__pop_reg("D")
        code += f"D=!D\n"
        code += self.__push_reg("D")
        return code

    def __push_reg(self, reg:str) -> str:
        assert reg in REGISTRY_SET
        code = ""
        code += f"D={reg}\n"  # 오염 방지를 위한 백업 (A 또는 M 레지스터가 입력된 경우)
        code += f"@{self.predefined['SP']}\n"
        code += f"A=M\n"    # A=&SP
        code += f"M=D\n"    # SP=D
        code += self.__expand_stack()
        return code

    def __pop_reg(self, reg:str) -> str:
        assert reg in REGISTRY_SET
        code = ""
        code += self.__reduce_stack()
        code += f"@{self.predefined['SP']}\n"
        code += f"A=M\n"
        code += f"{reg}=M\n"
        return code

    def __expand_stack(self) -> str:
        code = ""
        code += f"@{self.predefined['SP']}\n"
        code += f"M=M+1\n"
        return code

    def __reduce_stack(self) -> str:
        code = ""
        code += f"@{self.predefined['SP']}\n"
        code += f"M=M-1\n"
        return code
    
