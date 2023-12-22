import os

# Funtions
def save_solution(dir_solution, solution):
    name = solution["name"]
    file =  os.path.join(dir_solution, f"{name}.sol")

    with open(file, "a") as outfile:
        outfile.write(str(solution))
        outfile.write("\n")