from policyengine_us.model_api import *


class ia_fip(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa Family Investment Program (FIP)"
    unit = USD
    definition_period = MONTH
    defined_for = "ia_fip_eligible"
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf#page=20"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("ia_fip_payment_standard", period)
        countable_income = spm_unit("ia_fip_countable_income", period)
        benefit = max_(payment_standard - countable_income, 0)
        return min_(benefit, payment_standard)
