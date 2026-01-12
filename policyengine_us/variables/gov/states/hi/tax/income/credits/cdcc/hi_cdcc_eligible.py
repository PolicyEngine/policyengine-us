from policyengine_us.model_api import *


class hi_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Hawaii child and dependent care credit eligible"
    defined_for = StateCode.HI
    definition_period = YEAR
    reference = "https://law.justia.com/codes/hawaii/title-14/chapter-235/section-235-55-6/"

    def formula(tax_unit, period, parameters):
        count_cdcc_eligible = tax_unit("count_cdcc_eligible", period)
        return count_cdcc_eligible > 0
