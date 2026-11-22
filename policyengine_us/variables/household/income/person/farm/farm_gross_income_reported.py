from policyengine_us.model_api import *


class farm_gross_income_reported(Variable):
    value_type = float
    entity = Person
    label = "Reported gross farm income"
    unit = USD
    definition_period = YEAR
    default_value = -1
    documentation = (
        "The person's gross income from farming before farm expenses, as "
        "supplied: the total of line 9 of each Schedule F, with a negative "
        "line 9 counted as zero. As with the other income inputs, leave out "
        "income excluded under section 911, which is entered separately as "
        "Form 2555 amounts. An amount of zero or more is used as entered. A "
        "negative amount, such as the default -1, means not supplied: "
        "farm_gross_income then uses this "
        "person's farm_operations_income, whatever other people report. An "
        "entry for a calendar year applies only to that year, and one keyed "
        "by a period of several years or by a year that starts after January, "
        "such as year:2024:3 or year:2025-07, applies to no year. Because of "
        "its formula, Core does not count this as an input variable, so "
        "Simulation.to_input_dict() and to_input_dataframe() leave a supplied "
        "amount out unless include_computed_variables=True; supply it in the "
        "situation or with set_input."
    )
    reference = (
        # Chart A: "Gross income from a business means, for example, the
        # amount on Schedule C, line 7, or Schedule F, line 9."
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=9",
        "https://www.irs.gov/pub/irs-prior/f1040sf--2025.pdf#page=1",
    )

    def formula(person, period, parameters):
        # The formula stops Core carrying and uprating an entry into later years.
        return person.filled_array(-1)
