from policyengine_us.model_api import *


class earned_disability_benefits(Variable):
    value_type = float
    entity = Person
    label = "disability benefits counted as earned income"
    unit = USD
    documentation = (
        "Taxable disability benefits that count as earned income: those "
        "received under an employer's disability retirement plan before the "
        "plan's minimum retirement age, limited to the benefits included in "
        "gross income."
    )
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-prior/p596--2024.pdf#page=8",
        "https://www.irs.gov/pub/irs-prior/i1040gi--2024.pdf#page=25",
    )

    def formula(person, period, parameters):
        before_minimum_retirement_age = person(
            "disability_benefits_before_minimum_retirement_age", period
        )
        taxable_disability_benefits = person("taxable_disability_benefits", period)
        return min_(max_(0, before_minimum_retirement_age), taxable_disability_benefits)
