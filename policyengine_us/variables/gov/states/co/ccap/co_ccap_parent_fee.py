from policyengine_us.model_api import *


class co_ccap_parent_fee(Variable):
    value_type = float
    entity = TaxUnit
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

    def formula(tax_unit, period, parameters):
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p = parameters(instant_str).gov.states.co.ccap
        person = tax_unit.members
        spm_unit = tax_unit.spm_unit
        # Calculate base parent fee and add on parent fee.
        agi = tax_unit("adjusted_gross_income", period.this_year)
        hhs_fpg = spm_unit("snap_fpg", period) * MONTHS_IN_YEAR
        num_child_age_eligible = tax_unit("co_ccap_eligible_children", period)
        # The numebrs below are weights copied from government spreadsheet
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
        base_parent_fee = np.round(
            where(
                agi <= hhs_fpg,
                agi * first_multiplication_factor / MONTHS_IN_YEAR,
                (
                    hhs_fpg * first_multiplication_factor
                    + (agi - hhs_fpg) * second_multiplication_factor
                )
                / MONTHS_IN_YEAR,
            ),
            2,
        )
        add_on_parent_fee = where(
            agi > hhs_fpg,
            (num_child_age_eligible - 1) * third_multiplication_factor,
            0,
        )
        # Sum up all the parent fee for eligible children.
        child_age_eligible = person("co_ccap_child_eligible", period)
        childcare_hours_per_day = person(
            "childcare_hours_per_day", period.this_year
        )
        rate = p.parent_fee_rate_by_child_care_hours.calc(
            childcare_hours_per_day, right=True
        )
        non_discounted_fee = np.round(
            tax_unit.sum(
                child_age_eligible
                * (base_parent_fee + add_on_parent_fee)
                * rate
            ),
            2,
        )
        # Identify whether the filers are eligible for a discount.
        rating = person(
            "co_quality_rating_of_child_care_facility", period.this_year
        )
        discount_eligible = (
            tax_unit.sum(
                p.is_quality_rating_discounted.calc(rating)
                & child_age_eligible
            )
            > 0
        )

        discounted_rate = p.quality_rating_discounted_rate

        return np.round(
            where(
                discount_eligible,
                non_discounted_fee * discounted_rate,
                non_discounted_fee,
            ),
            2,
        )
