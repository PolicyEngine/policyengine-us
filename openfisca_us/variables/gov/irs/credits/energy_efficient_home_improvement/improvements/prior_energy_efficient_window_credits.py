from policyengine_us.model_api import *


class prior_energy_efficient_window_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Energy efficient window credits claimed in prior years"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#b_2"
