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
        "property tax credit add to federal income. With "
        "taxable_strike_benefits among the gross income sources, this is the "
        "gift part, at most the whole amount; without it, the whole amount."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/102#a",
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
    )

    def formula(person, period, parameters):
        strike_benefits = person("strike_benefits", period)
        sources = parameters(period).gov.irs.gross_income.sources
        if "taxable_strike_benefits" not in sources:
            return strike_benefits
        # taxable_strike_benefits is max(0, strike - gift part), so this is the
        # gift part capped at the whole amount.
        taxable = person("taxable_strike_benefits", period)
        return max_(strike_benefits - taxable, 0)
