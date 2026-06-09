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
        # ongoing CCA Plus limit (225% FPL); these families pay the
        # percentage-of-cost CCA Exit fee instead of the sliding unit fee.
        enrolled = spm_unit("ia_cca_enrolled", period)
        income = spm_unit("ia_cca_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        plus_limit = fpg * p.plus_basic
        return enrolled & (income > plus_limit)
