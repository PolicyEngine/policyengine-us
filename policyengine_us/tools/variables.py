from policyengine_us.system import system
from IPython.display import Markdown

variables = system.variables


def add_n(word):
    if word[0] in ["a", "e", "i", "o", "u"]:
        return " "
    else:
        return "n "


def print_variable_summary(variable_name: str):
    variable = variables.get(variable_name)
    return Markdown(
        f"""
        ## {variable.name}
        This variable models a{add_n(variable.entity.label)}**{variable.entity.label}**'s **{variable.label}**.
        """
    )
