from policyengine_us.model_api import *


class residential_clean_energy_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Residential clean energy credit"
    definition_period = YEAR
    documentation = "Residential clean energy tax credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25D"

    def formula(tax_unit, period, parameters):
        credit_limit = tax_unit(
            "residential_clean_energy_credit_credit_limit", period
        )
        potential = tax_unit(
            "residential_clean_energy_credit_potential", period
        )
        return min_(credit_limit, potential)
