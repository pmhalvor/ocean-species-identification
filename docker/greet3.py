import os, sys

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", ".")


def greet(x, n):
    return x*n


def store_greeting(x, n, output_file, ext="txt"):
    greeting = greet(x, n)
    with open(f"{OUTPUT_DIR}/{output_file}.{ext}", "w") as f:
        f.write(greeting)

    return greeting


if __name__ == "__main__":
    # Show the current working directory
    print("Current working directory:", os.getcwd())
    print(os.listdir(), "\n")

    # Output directory store as environment variable
    print(f"Output directory: {OUTPUT_DIR}")
    print(os.listdir(OUTPUT_DIR), "\n")

    # Print any previously stored greetings
    for file in os.listdir(OUTPUT_DIR):
        if file.endswith(".txt"):
            with open(os.path.join(OUTPUT_DIR, file), "r") as f:
                print(file)
                print(f.read(), "\n")

    # Write the greeting to a file
    greeting = store_greeting(sys.argv[1], int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "output")

    print(greeting)