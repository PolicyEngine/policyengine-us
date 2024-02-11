from policyengine_us.model_api import *


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
        year = period.start.year
        if period.start.month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p = parameters(instant_str).gov.states.co.ccap
        # Calculate base parent fee and add on parent fee.
        gross_income = spm_unit("co_ccap_countable_income", period)
        # snap_fpg is monthly.
        snap_fpg = spm_unit("snap_fpg", period)
        # Calculate base parent fee scaled (note income is monthly):
        # When income_scaled <= 1: income_scaled * 0.01
        # When income_scaled > 1: [1 * 0.01 + (income_scaled - 1) * 0.14]
        # Multiply by fpg afterward to scale back up
        gross_income_fpg_ratio = gross_income / snap_fpg
        base_parent_fee_scaled = p.parent_fee.base.calc(gross_income_fpg_ratio)
        return base_parent_fee_scaled * snap_fpg
