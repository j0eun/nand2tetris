import os
import enum

class CommandType(enum.Enum):
    A_COMMAND = 0   # @Xxx 형식. Xxx는 기호 또는 십진수를 가리킴.
    C_COMMAND = 1   # dest=comp;jump 형식
    L_COMMAND = 2   # (Xxx) 형식. Xxx는 기호를 가리킴.

class Parser():
    def __init__(self, path):
        with open(path, "r") as f:
            self.code = f.read().split("\n")
        for i in range(len(self.code)):
            comment_offset = self.code[i].find("//")
            if comment_offset != -1:
                self.code[i] = self.code[i][:comment_offset]    # 주석 제거
            self.code[i] = self.code[i].replace(" ", "")    # 공백 제거
        for i in range(len(self.code)-1, -1, -1):
            if len(self.code[i]) == 0:
                self.code.pop(i)    # 주석만 존재했던 코드줄은 삭제
                i -= 1
        self.cur_line = 0
        self.cur_code = ""
        self.source_path = path

    def has_more_commands(self)->bool:
        if self.cur_line < len(self.code):
            return True
        return False

    def advance(self)->None:
        assert self.has_more_commands() == True
        self.cur_line += 1
        self.cur_code = self.code[self.cur_line-1]

    def command_type(self)->CommandType:
        assert len(self.cur_code) > 0
        match self.cur_code[0]:
            case "@":
                return CommandType.A_COMMAND
            case "(":
                return CommandType.L_COMMAND
            case _:
                return CommandType.C_COMMAND

    def symbol(self)->str:
        cmdtype = self.command_type()
        assert cmdtype == CommandType.A_COMMAND or cmdtype == CommandType.L_COMMAND
        match cmdtype:
            case CommandType.A_COMMAND:
                return self.cur_code.replace("@", "")
            case CommandType.L_COMMAND:
                return self.cur_code.replace("(", "").replace(")", "")

    def dest(self)->str:
        assert self.command_type() == CommandType.C_COMMAND
        return self.cur_code.split("=")[0]

    def comp(self)->str:
        assert self.command_type() == CommandType.C_COMMAND
        if self.cur_code.find("=") == -1:
            return self.cur_code.split(";")[0]
        elif self.cur_code.find(";") == -1:
            return self.cur_code.split("=")[-1]
        else:
            raise RuntimeError(f"cannot translate this code at ({self.source_path}:{self.cur_line})")

    def jump(self)->str:
        assert self.command_type() == CommandType.C_COMMAND
        return self.cur_code.split(";")[-1]
        