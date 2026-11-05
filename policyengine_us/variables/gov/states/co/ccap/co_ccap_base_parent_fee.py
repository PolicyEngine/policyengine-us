from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_parameter_instant import (
    co_ccap_parameter_instant,
)


class co_ccap_base_parent_fee(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program base parent fee"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=41",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=62",
    )
    unit = USD
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        instant_str = co_ccap_parameter_instant(period)
        p = parameters(instant_str).gov.states.co.ccap
        # Calculate base parent fee and add on parent fee.
        gross_income = spm_unit("co_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        # Calculate base parent fee scaled (note income is monthly):
        # When income_scaled <= 1: income_scaled * 0.01
        # When income_scaled > 1: [1 * 0.01 + (income_scaled - 1) * 0.14]
        # Multiply by fpg afterward to scale back up
        gross_income_fpg_ratio = gross_income / fpg
        base_parent_fee_scaled = p.parent_fee.base.calc(gross_income_fpg_ratio)
        return base_parent_fee_scaled * fpg
