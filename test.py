def a():
    print 'a'
def b():
    print 'b'

def guess(f=a):
    f()
guess()