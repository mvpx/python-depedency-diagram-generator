class E:
    pass

class D:
    def __init__(self, e: E):
        self.e = e

class C:
    def __init__(self, d: D):
        self.d = d

class CA:
    def __init__(self, d: D):
        self.d = D

class B:
    def __init__(self, c: C, ca: CA):
        self.c = c
        self.ca = ca
        test_func()

class A:
    def __init__(self, b: B):
        self.b = b


def test_func():
    pass