'''
Utility functions used with MoviePy
'''


def text_center(text, font, x1, x2, y):
    '''
    Centers a text in the given space, between x1 and x1
    and at y, using the given font. Returns the position
    of the top-left corner to be used with moviepy.

    font must be a PIL.ImageFont instance.
    '''
    x_center = int((float(abs(x2 - x1)) / 2.0) + min(x1, x2))
    text_box = font.getsize(text)
    return (x_center - (float(text_box[0]) / 2.0), y)


def text_align_right(text, font, x, y):
    '''
    Returns the position a text should have, for it to
    ends at the given position.

    font must be a PIL.ImageFont instance.
    '''
    text_box = font.getsize(text)
    return (x - text_box[0], y)
