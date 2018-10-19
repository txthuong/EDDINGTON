#!/usr/bin/python

"""General helper functions."""

import re

def get_valid_filename(filename):
    """Returns the given string converted to a string that can be used for a clean
    filename. Removes leading and trailing spaces; converts other spaces to
    underscores; and removes anything that is not an alphanumeric, dash,
    underscore, or dot.

    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'

    """
    filename = str(filename).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', filename)


def contains_sublist(my_list, sublist):
    """Check is a sublist is present in a list, with the same order."""
    for i in range(len(my_list)-len(sublist)+1):
        if sublist == my_list[i:i+len(sublist)]:
            return True
    return False
