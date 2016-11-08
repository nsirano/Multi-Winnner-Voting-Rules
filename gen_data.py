import sys
from random import choice

def usage():
    '''
    Prints usage notes for the program.
    '''
    print("Usage: python3 gen_data.py <voters> <choices>")

def arg_check():
    '''
    Checks if enough arguments are passed to the function.
    '''
    if len(sys.argv) < 3:
        print("Error: Not enough arguments.")
        usage()
        sys.exit(1)

def generate_data(voters, choices):
    '''
    Generates random preference profile data given the number of voters and choices.
    '''
    f = open("data.txt", "w")
    ranking = ""
    exclude = set()
    v = 1
    for n in range(voters*choices):
        preference = int(choice([c for c in range(choices) if c not in exclude]))
        ranking = ranking + str(chr(65 + preference))
        if n%choices == choices-1:
            ranking = ranking + "\n"
            f.write(ranking)
            ranking = ""
            exclude.clear()

        else:
            ranking = ranking + ","
            exclude.add(preference)

    f.close()

def run():
    '''
    Main function to run the program.
    '''
    arg_check()
    voters =  int(sys.argv[1])
    choices = int(sys.argv[2])
    generate_data(voters, choices)

# ============================================================================ #
if __name__ == "__main__":
    run()
