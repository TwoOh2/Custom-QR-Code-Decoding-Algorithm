class BitStream:
    def __init__(self, bits):
        self.bits = bits
        self.idx = 0

    def read(self, n):
        if self.idx + n > len(self.bits):
            raise IndexError("Not enough bits")
        val = int(''.join(str(b) for b in self.bits[self.idx:self.idx+n]), 2)
        self.idx += n
        return val

ALPHANUMERIC_TABLE = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"

def decode_numeric(stream, char_count):
    res = ""
    while char_count >= 3:
        val = stream.read(10)
        res += f"{val:03d}"
        char_count -= 3
    if char_count == 2:
        val = stream.read(7)
        res += f"{val:02d}"
    elif char_count == 1:
        val = stream.read(4)
        res += f"{val:01d}"
    return res

def decode_alphanumeric(stream, char_count):
    res = ""
    while char_count >= 2:
        val = stream.read(11)
        res += ALPHANUMERIC_TABLE[val // 45]
        res += ALPHANUMERIC_TABLE[val % 45]
        char_count -= 2
    if char_count == 1:
        val = stream.read(6)
        res += ALPHANUMERIC_TABLE[val]
    return res

def decode_byte(stream, char_count):
    data_bytes = []
    for _ in range(char_count):
        data_bytes.append(stream.read(8))
    return bytes(data_bytes).decode('utf-8', errors='replace')

def decode_bits(bits, version):
    try:
        stream = BitStream(bits)
        result = ""
        while stream.idx < len(stream.bits) - 4:
            mode = stream.read(4)
            if mode == 0:
                break
            
            # Character count indicator length varies by mode and version
            if version <= 9:
                if mode == 1: cc_len = 10
                elif mode == 2: cc_len = 9
                elif mode == 4: cc_len = 8
                elif mode == 8: cc_len = 8
                else: return None
            else:
                return None # Only supporting up to V9
                
            char_count = stream.read(cc_len)
            
            if mode == 1:
                result += decode_numeric(stream, char_count)
            elif mode == 2:
                result += decode_alphanumeric(stream, char_count)
            elif mode == 4:
                result += decode_byte(stream, char_count)
            else:
                break
        return result
    except Exception as e:
        return None
