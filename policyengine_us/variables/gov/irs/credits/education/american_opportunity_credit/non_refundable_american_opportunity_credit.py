from policyengine_us.model_api import *


class non_refundable_american_opportunity_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Non-refundable American Opportunity Credit"
    unit = USD
    documentation = "Value of the non-refundable portion of the American Opportunity Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#i"

    def formula(tax_unit, period, parameters):
        credit_limit = tax_unit(
            "non_refundable_american_opportunity_credit_credit_limit", period
        )
        potential = tax_unit(
            "non_refundable_american_opportunity_credit_potential", period
        )
        return min_(credit_limit, potential)
