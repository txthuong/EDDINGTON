from pytest_expect import expect

def test_func():
    expect('a' == 'b')
    expect(1 != 1)
    a = 1
    b = 2
    expect(a == b, 'a:%s b:%s' % (a,b))