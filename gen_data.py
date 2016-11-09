import sys
from random import choice

def usage():
    """
    Prints usage notes for the program.
    """
    print("Usage: python3 gen_data.py <num_choices> <num_voters>")

def arg_check():
    """
    Checks if enough arguments are passed to the function.
    """
    if len(sys.argv) < 3:
        print("Error: Not enough arguments.")
        usage()
        sys.exit(1)

def generate_data(num_choices, num_voters):
    """
    Generates random preference profile data
    given the number of voters and choices.
    """
    f = open("data.txt", "w")
    ranking = ""
    exclude = set()
    for n in range(num_choices*num_voters):
        preference = int(choice([c for c in range(num_choices) if c not in exclude]))
        ranking = ranking + str(chr(65 + preference))
        if n%num_choices == num_choices-1:
            ranking = ranking + "\n"
            f.write(ranking)
            ranking = ""
            exclude.clear()

        else:
            ranking = ranking + ","
            exclude.add(preference)

    f.close()

def run():
    """
    Main function to run the program.
    """
    arg_check()
    num_choices =  int(sys.argv[1])
    num_voters = int(sys.argv[2])
    generate_data(num_choices, num_voters)

# ============================================================================ #
if __name__ == "__main__":
    run()
