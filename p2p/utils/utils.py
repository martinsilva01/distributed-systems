def isStringList(lst):
    """Return True if list is List of strings."""
    if isinstance(lst, list) and all(isinstance(item, str) for item in lst):
        return True
    return False

def equalLengthList(lst):
    """Returns True if all elements in array are equal in length"""
    if not lst:
        return -1
    first_len = len(lst[0])
    if all(len(s)== first_len for s in lst):
        return first_len
    else: 
        return -1
