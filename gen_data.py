import sys
from random import randrange

def usage():
    '''
    Prints usage notes for the program.
    '''
    print("Usage: python gen_data.py <voters> <choices>")

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
    v = 1
    for n in range(voters*choices):
        ranking = ranking + str(chr(65 + int(randrange(choices))))
        if n%choices == choices-1:
            ranking = ranking + "\n"
            f.write(ranking)
            ranking = ""

        else:
            ranking = ranking + ","

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
