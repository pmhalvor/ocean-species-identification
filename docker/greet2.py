def greet(x, n):
    print(x*n)

if __name__ == "__main__":
    import sys
    greet(sys.argv[1], int(sys.argv[2]))