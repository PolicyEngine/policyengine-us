from policyengine_us.model_api import *


class residential_clean_energy_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Residential clean energy credit credit limit"
    definition_period = YEAR
    documentation = "Residential clean energy tax credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25D"

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "income_tax_before_credits", period
        )
        p = parameters(period).gov.irs.credits.residential_clean_energy
        preceding_credits = add(tax_unit, period, p.preceding_credits)
        return max_(income_tax_before_credits - preceding_credits, 0)
