# A_COMMAND(16-bits): 0 v v v _  v  v  v  v _  v  v  v  v _  v  v  v  v
# C_COMMAND(16-bits): 1 1 1 a _ c1 c2 c3 c4 _ c5 c6 d1 d2 _ d3 j1 j2 j3

class Code():
    def __init__(self):
        self.dest_map = {
            "null": "000",
            "M":    "001",
            "D":    "010",
            "MD":   "011",
            "A":    "100",
            "AM":   "101",
            "AD":   "110",
            "AMD":  "111",
        }
        self.jump_map = {
            "null": "000",
            "JGT":  "001",
            "JEQ":  "010",
            "JGE":  "011",
            "JLT":  "100",
            "JNE":  "101",
            "JLE":  "110",
            "JMP":  "111",
        }
        self.comp_map = {
            "0":   "0"+"101010",
            "1":   "0"+"111111",
            "-1":  "0"+"111010",
            "D":   "0"+"001100",
            "A":   "0"+"110000",
            "!D":  "0"+"001101",
            "!A":  "0"+"110001",
            "-D":  "0"+"001111",
            "-A":  "0"+"110011",
            "D+1": "0"+"011111",
            "A+1": "0"+"110111",
            "D-1": "0"+"001110",
            "A-1": "0"+"110010",
            "D+A": "0"+"000010",
            "D-A": "0"+"010011",
            "A-D": "0"+"000111",
            "D&A": "0"+"000000",
            "D|A": "0"+"010101",

            "M":   "1"+"110000",
            "!M":  "1"+"110001",
            "-M":  "1"+"110011",
            "M+1": "1"+"110111",
            "M-1": "1"+"110010",
            "D+M": "1"+"000010",
            "D-M": "1"+"010011",
            "M-D": "1"+"000111",
            "D&M": "1"+"000000",
            "D|M": "1"+"010101",
        }

    def dest(self, symbol:str)->str:
        try:
            return self.dest_map[symbol]
        except KeyError:
            raise KeyError(f"[-] cannot find {symbol} in dest table")

    def comp(self, symbol:str)->str:
        try:
            return self.comp_map[symbol]
        except KeyError:
            raise KeyError(f"[-] cannot find {symbol} in comp table")

    def jump(self, symbol:str)->str:
        try:
            return self.jump_map[symbol]
        except KeyError:
            raise KeyError(f"[-] cannot find {symbol} in jump table")