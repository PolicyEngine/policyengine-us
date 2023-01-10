import os
import re


def replace_style(folder):
    # Traverse the directory tree and find all files
    for root, dirs, files in os.walk(folder):
        for file in files:
            # Read the contents of the file
            with open(os.path.join(root, file), "r", errors="ignore") as f:
                contents = f.read()
            # Replace the formula line with the adds line
            contents = re.sub(
                r"(formula = sum_of_variables\()(\[[^\]]+\])(\))",
                r"adds = \2",
                contents,
            )
            # Write the modified contents back to the file
            with open(os.path.join(root, file), "w") as f:
                f.write(contents)


if __name__ == "__main__":
    # Replace the old style with the new style in the current folder
    replace_style(".")
