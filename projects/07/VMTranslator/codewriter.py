import time

REGISTRY_SET = {"A", "M", "D"}

class CodeWriter():
    # 출력 파일/스트림을 열고 어셈블리 코드를 작성할 준비를 한다.
    def __init__(self, asm_file_path:str) -> None:
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
        }
    
    # 출력 파일/스트림을 닫는다.
    def __del__(self) -> None:
        self.f.close()

    # CodeWriter에게 새로운 VM 파일 번역이 시작되었음을 알린다.
    def set_file_name(self, asm_file_path:str) -> None:
        self.f.close()
        self.f = open(asm_file_path, "w")

    # C_ARITHMETIC 타입의 명령을 작성한다.
    def write_arithmetic(self, command:str) -> None:
        code = ""
        command = command.lower()
        match command:
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
        command = command.lower()
        segment = segment.lower()
        match command:
            case "push":
                if segment == "constant":
                    code += f"@{index}\n"
                    code += self.__push_reg("A")
            case "pop":
                pass
            case _:
                raise AssertionError("command is not C_PUSH or C_POP type")
        self.f.write(code)

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
        code += f"{reg}=M\n"    # 오염 방지를 위한 백업 (A 또는 M 레지스터가 입력된 경우)
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