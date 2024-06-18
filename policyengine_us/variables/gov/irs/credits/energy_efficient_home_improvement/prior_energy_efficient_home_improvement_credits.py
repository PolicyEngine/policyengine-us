from policyengine_us.model_api import *


class prior_energy_efficient_home_improvement_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Prior year energy efficient home improvement credit"
    documentation = (
        "Energy efficient home improvement credits claimed in prior years"
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#b_1"
