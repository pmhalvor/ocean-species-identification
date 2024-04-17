def greet(x, n):
    print(x*n)
    return x*n

def write_greeting(x, n, output_file, ext="txt"):
    greeting = greet(x, n)
    with open(f"{output_file}.{ext}", "w") as f:
        f.write(x*n)

if __name__ == "__main__":
    import sys
    write_greeting(sys.argv[1], int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "output")
