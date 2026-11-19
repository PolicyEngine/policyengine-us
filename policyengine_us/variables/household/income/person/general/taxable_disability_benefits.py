from policyengine_us.model_api import *


class taxable_disability_benefits(Variable):
    value_type = float
    entity = Person
    label = "taxable disability benefits"
    unit = USD
    documentation = (
        "The part of disability_benefits included in gross income: benefits "
        "from a plan paid for by the employer, including disability pensions "
        "(IRC 105(a)). Reported on Form 1040 line 1h until minimum retirement "
        "age and as a pension on line 5 after it."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/105#a",
        "https://www.irs.gov/pub/irs-prior/p525--2024.pdf#page=18",
    )

    def formula(person, period, parameters):
        disability_benefits = person("disability_benefits", period)
        tax_exempt = person("tax_exempt_disability_benefits", period)
        return max_(0, disability_benefits - tax_exempt)
