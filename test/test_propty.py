from kvix.util import Propty


def test_x():
    class T:
        x = Propty(str)

    t = T()
    t.x = "1"
    assert t._x == "1"
    assert t.x == "1"


def test_default_value():
    class T:
        x = Propty(str, default_value="123")

    t = T()
    assert not hasattr(t, "_x")
    assert t.x == "123"
    assert t._x == "123"
