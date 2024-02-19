from policyengine_us.model_api import *


class co_ccap_parent_fee(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program parent fee"
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
        eligible_children = spm_unit("co_ccap_eligible_children", period)
        base_parent_fee = spm_unit("co_ccap_base_parent_fee", period)
        add_on_parent_fee = spm_unit("co_ccap_add_on_parent_fee", period)

        # Childcare-hours-per-day also affects parent fee.
        # Since each child may need different hours of childcare per day, we
        # have to calculate parent fee one by one and sum them up.
        person = spm_unit.members
        child_age_eligible = person("co_ccap_child_eligible", period)
        childcare_hours_per_day = person(
            "childcare_hours_per_day", period.this_year
        )
        rate = p.parent_fee_rate_by_child_care_hours.calc(
            childcare_hours_per_day, right=True
        )
        childs_parent_fee = spm_unit.project(
            base_parent_fee + add_on_parent_fee
        )
        unrounded_non_discounted_fee = spm_unit.sum(
            child_age_eligible * childs_parent_fee * rate
        )

        non_discounted_fee = np.round(unrounded_non_discounted_fee, 2)
        # Rating of child care facilities also affects parent fee.
        # For households utilizing multiple child care providers, only one
        # child care provider is required to be eligible for the reduced
        # parent fee to apply.
        rating = person(
            "co_quality_rating_of_child_care_facility", period.this_year
        )
        maximum_rating = spm_unit.max(rating * child_age_eligible)
        discounted_rate = p.is_quality_rating_discounted.calc(maximum_rating)
        unrounded = non_discounted_fee * discounted_rate
        return np.round(unrounded, 2)
