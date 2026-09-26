from policyengine_us.model_api import *


def head_or_spouse_candidates(person, period):
    """Adults who can be inferred as the tax unit head or spouse.

    People input as tax unit dependents are excluded, so a dependent parent
    or adult child cannot displace the filer or become their spouse. A tax
    unit whose adults are all input as dependents keeps every adult as a
    candidate, as before.

    ``is_tax_unit_dependent`` is derived from head and spouse status, so this
    reads only its stored value for the period and never runs its formula.
    A stored value that the formula computed can only exist after head and
    spouse were computed for the period, and it flags exactly the people who
    are neither, so excluding them leaves the head and spouse unchanged.
    """
    adult = ~person("is_child", period)
    input_dependent = person.simulation.get_array("is_tax_unit_dependent", period)
    if input_dependent is None:
        return adult
    non_dependent_adult = adult & ~input_dependent
    has_non_dependent_adult = person.tax_unit.any(non_dependent_adult)
    return where(has_non_dependent_adult, non_dependent_adult, adult)
