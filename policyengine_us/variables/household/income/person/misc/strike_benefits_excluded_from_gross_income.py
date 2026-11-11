from policyengine_us.model_api import *


class strike_benefits_excluded_from_gross_income(Variable):
    value_type = float
    entity = Person
    label = "strike benefits excluded from federal gross income"
    unit = USD
    documentation = (
        "The part of strike_benefits that federal gross income leaves out: "
        "the nontaxable strike benefits that Utah homeowner's and renter's "
        "relief, Montana's elderly homeowner/renter credit and Arizona's "
        "property tax credit add to federal income. It is the whole amount "
        "less strike_benefits_in_gross_income, floored at zero: the gift part "
        "(at most the whole amount) under current law, the whole amount under "
        "a reform that drops taxable_strike_benefits from gross income, and "
        "zero under one that lists strike_benefits itself."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/102#a",
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
    )

    def formula(person, period, parameters):
        strike_benefits = person("strike_benefits", period)
        in_gross_income = person("strike_benefits_in_gross_income", period)
        return max_(strike_benefits - in_gross_income, 0)
