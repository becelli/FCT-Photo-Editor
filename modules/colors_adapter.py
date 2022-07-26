def get_gray_from_rgb(r: int, g: int, b: int) -> int:
    return (r + g + b) // 3


def get_rgb_from_color_integer(color: int) -> tuple[int, int, int]:
    return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
