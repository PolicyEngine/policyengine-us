from policyengine_us.model_api import *


class sc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "sc_tanf_eligible"
    reference = (
        "https://dss.sc.gov/media/3926/tanf_policy_manual_vol-60.pdf#page=131"
    )

    def formula(spm_unit, period, parameters):
        p_income = parameters(period).gov.states.sc.tanf.income.need_standard
        p_payment = parameters(period).gov.states.sc.tanf.payment
        # Compute need standard based on ferderal poverty guidlines
        fpg = add(spm_unit, period, ["tax_unit_fpg"])
        need_standard = fpg * p_income.rate
        # G
        total_net_income = spm_unit("sc_tanf_total_net_income", period)
        # I
        return (
            (need_standard - total_net_income)
            * p_payment.rate
            / MONTHS_IN_YEAR
        )
