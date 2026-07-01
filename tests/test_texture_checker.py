from Content.Python.core.texture_checker import check_power_of_two

def test_pot():
    result = check_power_of_two(1024, 1024)
    assert result is None

def test_mixed():
    result = check_power_of_two(1024, 512)
    assert result is None

def test_not_pot():
    result = check_power_of_two(100, 100)
    assert result is not None

def test_zero_width():
    result = check_power_of_two(0, 256)
    assert result is not None
