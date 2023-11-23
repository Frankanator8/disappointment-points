def get_nth(n):
    if 10 <= n % 100 < 20:
        return f"{n}th"
    else:
        if n % 10 == 1:
            return f"{n}st"
        elif n % 10 == 2:
            return f"{n}nd"
        elif n % 10 == 3:
            return f"{n}rd"
        else:
            return f"{n}th"