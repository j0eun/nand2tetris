import io
import enum

class CommandType(enum.Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8
    C_UNKNOWN = 9

class Parser():
    # 입력 파일/스트림을 열고 VM 파일을 분석할 준비를 한다.
    def __init__(self, vm_file_path:str) -> None:
        self.f = open(vm_file_path, "r")
        self.cur_code = ""
        self.cur_line = 0

    # 입력 파일/스트림을 닫는다.
    def __del__(self) -> None:
        self.f.close()

    # 입력 파일/스트림에 명령이 더 남아있는지 확인한다.
    def has_more_commands(self) -> bool:
        origin = self.f.tell()  # 다음 행 읽기 전에 현재 오프셋 백업
        line = self.f.readline()
        if line == "":
            return False
        else:
            self.f.seek(origin, io.SEEK_SET)
            return True

    # 다음 명령을 읽는다.
    # 입력에 다음 명령이 존재할 때만 호출되어야 한다.
    def advance(self) -> None:
        assert self.has_more_commands() == True
        self.cur_line += 1
        self.cur_code = self.f.readline().rstrip()      # 마지막 개행 문자는 제거
        if self.command_type() == CommandType.C_UNKNOWN:    # 주석 또는 공백 라인은 줄번호만 증가시키고 생략
            self.cur_code = ""

    # 현재 VM 명령의 타입을 반환한다.
    def command_type(self) -> CommandType:
        command_table = {
            "add":      CommandType.C_ARITHMETIC,   # 정수 덧셈
            "sub":      CommandType.C_ARITHMETIC,   # 정수 뺄셈
            "neg":      CommandType.C_ARITHMETIC,   # 산술 NOT
            "eq":       CommandType.C_ARITHMETIC,   # ~와 같음
            "gt":       CommandType.C_ARITHMETIC,   # ~보다 큼
            "lt":       CommandType.C_ARITHMETIC,   # ~보다 작음
            "and":      CommandType.C_ARITHMETIC,   # 비트 AND
            "or":       CommandType.C_ARITHMETIC,   # 비트 OR
            "not":      CommandType.C_ARITHMETIC,   # 비트 NOT
            "push":     CommandType.C_PUSH,
            "pop":      CommandType.C_POP,
            "label":    CommandType.C_LABEL,
            "goto":     CommandType.C_GOTO,
            "if-goto":  CommandType.C_IF,
            "function": CommandType.C_FUNCTION,
            "return":   CommandType.C_RETURN,
            "call":     CommandType.C_CALL,
        }
        command = self.cur_code.split(" ")[0].lower()  # 소문자로 통일
        try:
            command_type_ = command_table[command]
        except KeyError:
            return CommandType.C_UNKNOWN
        return command_type_
        
    # 현재 명령의 첫 번째 오퍼랜드를 반환한다.
    # 명령 타입이 C_ARITHMETIC일 경우 명령 자체가 반환된다.
    # 명령 타입이 C_RETURN일 경우 호출하면 안 된다.
    def arg1(self) -> str:
        assert self.command_type() != CommandType.C_RETURN
        if self.command_type() == CommandType.C_ARITHMETIC:
            return self.cur_code.split(" ")[0]
        return self.cur_code.split(" ")[1]

    # 현재 명령의 두 번째 오퍼랜드를 반환한다.
    # 명령 타입이 C_PUSH, C_POP, C_FUNCTION, C_CALL 중 하나일 경우에만 호출 가능하다.
    def arg2(self) -> int:
        assert self.command_type() in \
            {CommandType.C_PUSH, CommandType.C_POP, CommandType.C_FUNCTION, CommandType.C_CALL}
        return int(self.cur_code.split(" ")[2], 10)
    