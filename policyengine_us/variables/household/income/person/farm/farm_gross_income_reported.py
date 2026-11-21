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
        "person's farm_operations_income, whatever other people report. As "
        "with every input, Core carries an amount into a later year only "
        "when no one has an amount for that year: once anyone enters an "
        "amount for a year, a person whose amount was entered only for an "
        "earlier year gets the default in that year. Enter each person's "
        "amount for every year calculated."
    )
    reference = (
        # Chart A: "Gross income from a business means, for example, the
        # amount on Schedule C, line 7, or Schedule F, line 9."
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=9",
        "https://www.irs.gov/pub/irs-prior/f1040sf--2025.pdf#page=1",
    )
