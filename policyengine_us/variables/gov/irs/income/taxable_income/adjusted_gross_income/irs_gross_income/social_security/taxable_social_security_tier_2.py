from policyengine_us.model_api import *


class taxable_social_security_tier_2(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable Social Security (tier 2)"
    documentation = "Taxable Social Security from 50-85% taxation tier, credited to Medicare HI trust fund"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/86#a_2"

    def formula(tax_unit, period, parameters):
        total_taxable = tax_unit("tax_unit_taxable_social_security", period)
        tier_1 = tax_unit("taxable_social_security_tier_1", period)
        return total_taxable - tier_1
