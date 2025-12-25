
class OutputBuffer:
    def __init__(self):
        self.buffer = []
    
    def print(self, text=""):
        self.buffer.append(str(text))
    
    def clear(self):
        self.buffer = []
    
    def get_output(self):
        return "\n".join(self.buffer)

    def flush(self):
        out = self.get_output()
        self.clear()
        return out
