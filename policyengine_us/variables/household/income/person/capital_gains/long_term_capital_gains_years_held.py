from policyengine_us.model_api import *


class long_term_capital_gains_years_held(Variable):
    value_type = float
    entity = Person
    label = "long-term capital gains years held"
    unit = "year"
    documentation = (
        "Representative holding period, in years, associated with realized "
        "long-term capital gains for capital-gains basis indexation analysis."
    )
    definition_period = YEAR
