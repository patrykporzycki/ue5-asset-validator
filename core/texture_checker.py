def is_power_of_two(n: int) -> bool:
    # texture dimensions from UE5 are always positive integers?
    return (n & (n - 1)) == 0

def check_power_of_two(width: int, height: int) -> str | None:
    if is_power_of_two(width) and is_power_of_two(height):
        return None
    return f"Resolution {width}x{height} is not a power of two"
