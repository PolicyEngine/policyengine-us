from policyengine_us.model_api import *


class co_ccap_parent_fee(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program parent fee"
    reference = (
        "https://docs.google.com/spreadsheets/d/1EEc3z8Iwu_KRTlBtd2NssDDEx_FITqVq/edit#gid=468321263",
        "https://docs.google.com/spreadsheets/d/1HtPiC2qxclzWfBa7LRo2Uohrg-RCBkyZ/edit#gid=582762342",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=41",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=62",
    )
    unit = USD
    definition_period = MONTH
    defined_for = "co_ccap_eligible"

    def formula(spm_unit, period, parameters):
        year = period.start.year
        if period.start.month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p = parameters(instant_str).gov.states.co.ccap
        # Calculate base parent fee and add on parent fee.
        gross_income = spm_unit("co_ccap_countable_income", period.this_year)
        hhs_fpg = spm_unit("snap_fpg", period) * MONTHS_IN_YEAR
        eligible_children = spm_unit("co_ccap_eligible_children", period)
        # The numbers below are weights copied from government spreadsheet
        # (url: https://docs.google.com/spreadsheets/d/1EEc3z8Iwu_KRTlBtd2NssDDEx_FITqVq/edit#gid=468321263,
        #       https://docs.google.com/spreadsheets/d/1HtPiC2qxclzWfBa7LRo2Uohrg-RCBkyZ/edit#gid=582762342)
        first_multiplication_factor = (
            p.base_parent_fee.first_multiplication_factor
        )
        second_multiplication_factor = (
            p.base_parent_fee.second_multiplication_factor
        )
        third_multiplication_factor = (
            p.add_on_parent_fee.third_multiplication_factor
        )
        # Calculate base parent fee:
        # When agi <= fpg: agi * 0.01 / 12
        # When agi > fpg: [fpg * 0.01 + (agi - fpg) * 0.14]/12
        base_parent_fee = np.round(
            where(
                gross_income <= hhs_fpg,
                gross_income * first_multiplication_factor,
                hhs_fpg * first_multiplication_factor
                + (gross_income - hhs_fpg) * second_multiplication_factor,
            )
            / MONTHS_IN_YEAR,
            2,
        )
        # Calculate add-on parent fee (this is relevant to number of eligible children in a household and agi):
        # When agi <= fpg: 0
        # When agi > fpg: 15 for each additional child
        add_on_parent_fee = where(
            gross_income > hhs_fpg,
            (eligible_children - 1) * third_multiplication_factor,
            0,
        )
        # Childcare-hours-per-day also affects parent fee.
        # Since each child may need different hours of childcare per day, we have to calculate parent fee one by one and sum them up.
        child_age_eligible = spm_unit.members("co_ccap_child_eligible", period)
        childcare_hours_per_day = spm_unit.members(
            "childcare_hours_per_day", period.this_year
        )
        rate = p.parent_fee_rate_by_child_care_hours.calc(
            childcare_hours_per_day, right=True
        )
        non_discounted_fee = np.round(
            spm_unit.sum(
                child_age_eligible
                * (base_parent_fee + add_on_parent_fee)
                * rate
            ),
            2,
        )
        # Rating of child care facilities also affects parent fee.
        # For households utilizing multiple child care providers, only one child care provider is required to be eligible for the reduced parent fee to apply.
        rating = spm_unit.members(
            "co_quality_rating_of_child_care_facility", period.this_year
        )
        discount_eligible = (
            spm_unit.sum(
                p.is_quality_rating_discounted.calc(rating)
                & child_age_eligible
            )
            > 0
        )
        discounted_rate = p.quality_rating_discounted_rate
        unrounded = non_discounted_fee * where(
            discount_eligible, discounted_rate, 1
        )
        return np.round(unrounded, 2)
