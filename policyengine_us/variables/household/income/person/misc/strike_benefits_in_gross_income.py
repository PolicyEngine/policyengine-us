from policyengine_us.model_api import *


class strike_benefits_in_gross_income(Variable):
    value_type = float
    entity = Person
    label = "strike benefits in federal gross income"
    unit = USD
    documentation = (
        "The part of a person's strike_benefits that federal gross income "
        "counts, on whichever return reports it (a tax unit dependent's on "
        "their own): "
        "taxable_strike_benefits while it is among the gross income sources "
        "(as it is under current law), or the whole amount under a reform "
        "that lists strike_benefits itself. States that subtract strike "
        "benefits from federal income, such as Pennsylvania, subtract this, "
        "so a reform that drops them from federal gross income never takes "
        "other income out of a state base."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/61#a",
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
    )

    def formula(person, period, parameters):
        sources = parameters(period).gov.irs.gross_income.sources
        listed = [
            source
            for source in ["strike_benefits", "taxable_strike_benefits"]
            if source in sources
        ]
        return add(person, period, listed)
