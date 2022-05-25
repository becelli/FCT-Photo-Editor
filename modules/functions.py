def get_gray_from_rgb(r: int, g: int, b: int) -> int:
    """
    Converts a RGB image to gray.
    """
    return (r + g + b) // 3


def get_rgb_from_color_integer(color: int) -> tuple[int, int, int]:
    """
    Converts a color to RGB.
    """
    return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF


def get_color_integer_from_rgb(r: int, g: int, b: int) -> int:
    """
    Converts a RGB image to color integer.
    """
    return (r << 16) + (g << 8) + b


def get_color_integer_from_red(r: int) -> int:
    """
    Create a color integer from red value.
    """
    return (r << 16) + (0 << 8) + 0


def get_color_integer_from_green(g: int) -> int:
    """
    Create a color integer from green value.
    """
    return (0 << 16) + (g << 8) + 0


def get_color_integer_from_blue(b: int) -> int:
    """
    Create a color integer from blue value.
    """
    return (0 << 16) + (0 << 8) + b


def get_color_integer_from_gray(gray: int) -> int:
    """
    Converts a gray image to color integer.
    """
    return int((gray << 16) + (gray << 8) + gray)


def get_gray_from_color_integer(color: int) -> int:
    """
    Extract a gray value from a color integer.
    """
    return get_blue_from_color_integer(color)


def get_red_from_color_integer(color: int) -> int:
    """
    Extract a red value from a color integer.
    """
    return (color >> 16) & 0xFF


def get_green_from_color_integer(color: int) -> int:
    """
    Extract a green value from a color integer.
    """
    return (color >> 8) & 0xFF


def get_blue_from_color_integer(color: int) -> int:
    """
    Extract a blue value from a color integer.
    """
    return color & 0xFF


def get_color_integer_from_color_name(color_name: str, color_integer: int) -> int:
    """
    Get a color integer from a color name.
    """
    match color_name:
        case "red":
            return color_integer & 0xFF0000
        case "green":
            return color_integer & 0x00FF00
        case "blue":
            return color_integer & 0x0000FF
        case _:
            return color_integer
