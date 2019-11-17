# Importing external libraries


# Importing internal libraries




def largestNumber(in_str):
    l=[int(x) for x in in_str.split() if x.isdigit()]
    return max(l) if l else None