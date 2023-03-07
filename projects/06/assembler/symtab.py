class SymbolTable():
    def __init__(self):
        self.symbol_map = {
            # 사전 정의된 심볼 목록
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KBD": 24576,

            # 사용자 정의 심볼은 패스를 거치면서 추가
        }

    def add_entry(self, symbol:str, address:int)->None:
        assert symbol not in self.symbol_map
        self.symbol_map[symbol] = address

    def contains(self, symbol:str)->bool:
        if symbol in self.symbol_map:
            return True
        return False

    def get_address(self, symbol:str)->int:
        assert symbol in self.symbol_map
        return self.symbol_map[symbol]
