from eodhp_web_presence.home.utils import my_function


def test_pass():
    assert True


def test_my_function():
    x = my_function()

    assert x == 3
