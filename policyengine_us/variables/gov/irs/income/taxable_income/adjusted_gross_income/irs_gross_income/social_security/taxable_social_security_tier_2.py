from policyengine_us.model_api import *


class taxable_social_security_tier_2(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable Social Security (tier 2)"
    documentation = (
        "Current-law taxable Social Security less its first-tier component. "
        "The HI revenue allocation instead measures the increase in tax "
        "liability over the pre-1993 section 86 counterfactual."
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/86#a_2"

    # tier_2 = total_taxable - tier_1 capped at 0
    def formula(tax_unit, period, parameters):
        tier_1 = tax_unit("taxable_social_security_tier_1", period)
        total_taxable = tax_unit("tax_unit_taxable_social_security", period)
        return max_(total_taxable - tier_1, 0)
