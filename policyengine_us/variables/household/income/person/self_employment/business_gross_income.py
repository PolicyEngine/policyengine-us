from policyengine_us.model_api import *


class business_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Gross income from businesses"
    unit = USD
    documentation = (
        "Gross income from the person's businesses before business expenses: "
        "the total of line 7 of each Schedule C, gross receipts less returns "
        "and cost of goods sold plus other business income, with a negative "
        "line 7 counted as zero. Chart A of the Form 1040 instructions uses "
        "this amount as gross income from a business for the filing "
        "requirement. As with the other income inputs, leave out income "
        "excluded under section 911. Without an input, the net amounts "
        "stand in: self_employment_income plus sstb_self_employment_income, "
        "each floored at zero, which equal gross income only for a business "
        "with no expenses. Once any person has an input for a year, enter one "
        "for every person with a business: people without an input get zero, "
        "not the net amounts."
    )
    definition_period = YEAR
    reference = (
        # Section 61(a)(2): gross income derived from business.
        "https://www.law.cornell.edu/uscode/text/26/61#a_2",
        # Chart A: "Gross income from a business means, for example, the
        # amount on Schedule C, line 7, or Schedule F, line 9."
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=9",
        "https://www.irs.gov/pub/irs-prior/f1040sc--2025.pdf#page=1",
    )

    def formula(person, period, parameters):
        regular = person("self_employment_income", period)
        sstb = person("sstb_self_employment_income", period)
        return max_(regular, 0) + max_(sstb, 0)
