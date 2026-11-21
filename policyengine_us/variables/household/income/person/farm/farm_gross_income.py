from policyengine_us.model_api import *


class farm_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Gross farm income"
    unit = USD
    documentation = (
        "Gross income from the person's farming before farm expenses: the "
        "total of line 9 of each Schedule F, with a negative line 9 counted "
        "as zero. Chart A of the Form 1040 instructions uses this amount as "
        "gross income from farming for the filing requirement. As with the "
        "other income inputs, leave out income excluded under section 911. "
        "Without an input, farm_operations_income floored at zero stands in, "
        "which equals gross income only for a farm with no expenses. Once any "
        "person has an input for a year, enter one for every person with a "
        "farm: people without an input get zero, not farm_operations_income."
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
        return max_(person("farm_operations_income", period), 0)
