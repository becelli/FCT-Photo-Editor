def gray_from_rgb(r, g, b) -> int:
    return int(0.299 * r + 0.587 * g + 0.114 * b)
    # return int(0.2126 * r + 0.7152 * g + 0.0722 * b)
