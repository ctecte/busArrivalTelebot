x = 0

def baz():
    print(x)

def foo():
    global x
    x = 2
    print(x)

def bar():
    print(x)

baz()
foo()
bar()

