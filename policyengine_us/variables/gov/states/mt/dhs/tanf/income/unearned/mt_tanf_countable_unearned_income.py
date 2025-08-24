from policyengine_us.model_api import *


class mt_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF501-1Jan012018.pdf"
    )
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dhs.tanf.income
        total_unearned_income = add(
            spm_unit, period, ["mt_tanf_gross_unearned_income"]
        )

        # Should this rule be modeled here?
        # Child support is excluded when:
        # 1. A household is required to turn the child support over to CSED; and
        # 2. A child support arrearage is paid in a one-time payment because it is considered a lump sum.

        return max_(0, total_unearned_income)
