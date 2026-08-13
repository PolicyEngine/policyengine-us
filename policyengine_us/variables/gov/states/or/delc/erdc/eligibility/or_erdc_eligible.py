from policyengine_us.model_api import *


class or_erdc_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Oregon ERDC"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0015"
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["or_erdc_eligible_child"]) > 0
        activity_eligible = spm_unit("or_erdc_activity_eligible", period)
        income_eligible = spm_unit("or_erdc_income_eligible", period)
        resource_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        copay = spm_unit("or_erdc_copay", period)
        allowable_cost = spm_unit("or_erdc_allowable_child_care_cost", period)
        return (
            has_eligible_child
            & activity_eligible
            & income_eligible
            & resource_eligible
            & (copay < allowable_cost)
        )
