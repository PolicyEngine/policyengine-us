from policyengine_us.model_api import *


class farm_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Gross farm income"
    unit = USD
    documentation = (
        "Gross income from the person's farming before farm expenses: "
        "Schedule F line 9, which Chart A of the Form 1040 instructions uses "
        "as gross income from farming for the filing requirement. It is "
        "farm_gross_income_reported when that is zero or more. When it is "
        "negative (its default is -1), farm_operations_income floored at "
        "zero stands in, which equals gross income only for a farm with no "
        "expenses. An entry of farm_gross_income_reported applies only to "
        "the year entered. Each person's value depends only on their own "
        "inputs, apart from the carry-over of farm_operations_income: an "
        "entry carries into a later year only when no one has an entry for "
        "that year, so once anyone enters one for a year, a person whose "
        "amount was entered only for an earlier year has zero in that year. "
        "Enter it for every year calculated. "
        "Supply farm_gross_income_reported rather than setting this variable: "
        "an input here applies to every person in the simulation, and people "
        "without a value get zero."
    )
    definition_period = YEAR
    reference = (
        # Section 61(a)(2): gross income derived from business.
        "https://www.law.cornell.edu/uscode/text/26/61#a_2",
        # Chart A: "Gross income from a business means, for example, the
        # amount on Schedule C, line 7, or Schedule F, line 9."
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=9",
        "https://www.irs.gov/pub/irs-prior/f1040sf--2025.pdf#page=1",
    )

    def formula(person, period, parameters):
        reported = person("farm_gross_income_reported", period)
        net = max_(person("farm_operations_income", period), 0)
        # Any negative amount, such as the default -1, means not supplied:
        # Schedule F line 9, with a negative line counted as zero, can't be
        # negative.
        return where(reported >= 0, reported, net)
