from policyengine_us.model_api import *


class mt_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://dphhs.mt.gov/assets/hcsd/TANF/TANFStatePlan.pdf#page=10"
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dhs.tanf
        p_fpg = parameters(
            f"{int(p.income_standards.payment_fpg_year)}-01-01"
        ).gov.hhs.fpg
        capped_size = min_(
            spm_unit("mt_tanf_assistance_unit_size", period),
            p.max_unit_size,
        )
        state_group = spm_unit.household("state_group_str", period)
        monthly_fpg = (
            p_fpg.first_person[state_group]
            + p_fpg.additional_person[state_group] * (capped_size - 1)
        ) / MONTHS_IN_YEAR
        return monthly_fpg * p.income_standards.payment_fpg_rate
