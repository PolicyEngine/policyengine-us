from openfisca_us.model_api import *


class prior_nonbusiness_energy_property_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "Nonbusiness energy property credits claimed in prior years"
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#b_1"
