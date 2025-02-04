def countdown(n: int):

    print(n)

    if n == 0:
        return None
    
    countdown(n - 1)


countdown(3)
