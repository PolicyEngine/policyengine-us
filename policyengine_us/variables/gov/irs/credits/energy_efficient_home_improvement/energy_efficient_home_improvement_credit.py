from policyengine_us.model_api import *


class energy_efficient_home_improvement_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Energy efficient home improvement credit"
    documentation = "Residential clean energy credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C"

    def formula(tax_unit, period, parameters):
        credit_limit = tax_unit(
            "energy_efficient_home_improvement_credit_credit_limit", period
        )
        potential = tax_unit(
            "energy_efficient_home_improvement_credit_potential", period
        )
        return min_(credit_limit, potential)
