from policyengine_us.model_api import *


class ia_cca_in_exit_tier(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa CCA family is in the CCA Exit tier"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=12"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.income.fpl_rate
        # CCA Exit applies to enrolled families whose income exceeds the
        # ongoing CCA Plus ceiling — the lesser of 225% FPL and 85% of Iowa
        # median family income (IAC 441-170.2(1)"a"(2)); these families pay
        # the percentage-of-cost CCA Exit fee instead of the sliding unit
        # fee. The 85% MFI cap binds below 225% FPL only at very large
        # family sizes (10 and up with current parameters).
        enrolled = spm_unit("ia_cca_enrolled", period)
        income = spm_unit("ia_cca_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        smi_cap = spm_unit("ia_cca_smi", period)
        plus_limit = min_(fpg * p.plus_basic, smi_cap)
        return enrolled & (income > plus_limit)
