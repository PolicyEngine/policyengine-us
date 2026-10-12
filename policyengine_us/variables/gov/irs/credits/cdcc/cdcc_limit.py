from policyengine_us.model_api import *


class cdcc_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC-relevant care expense limit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#c"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.cdcc
        capped_count_cdcc_eligible = tax_unit("capped_count_cdcc_eligible", period)
        dollar_limit = p.max * capped_count_cdcc_eligible
        # IRC section 21(c) flush language: the $3,000 / $6,000 dollar limit
        # "shall be reduced by the aggregate amount excludable from gross
        # income under section 129 for the taxable year." This is the Form
        # 2441 Part III -> Part II reconciliation (line 27 minus line 28).
        exclusion = tax_unit("dependent_care_assistance_exclusion", period)
        return max_(dollar_limit - exclusion, 0)
