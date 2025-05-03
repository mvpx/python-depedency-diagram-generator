class E:
    pass

class D:
    def __init__(self, e: E):
        self.e = e

class C:
    def __init__(self, d: D):
        self.d = d

class B:
    def __init__(self, c: C):
        self.c = c

class A:
    def __init__(self, b: B):
        self.b = b