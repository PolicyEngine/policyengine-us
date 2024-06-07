from policyengine_us.model_api import *


class co_ccap_add_on_parent_fee(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program add on parent fee"
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
        eligible_children = spm_unit("co_ccap_eligible_children", period)
        # Calculate add-on parent fee based on the number of eligible
        # children in a household and income:
        # When income <= fpg: 0
        # When income > fpg: 15 for each additional child
        add_on_parent_fee_amount = (
            eligible_children - 1
        ) * p.parent_fee.add_on
        add_on_parent_fee_applies = gross_income > snap_fpg
        return add_on_parent_fee_amount * add_on_parent_fee_applies
