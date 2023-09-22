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
    definition_period = YEAR
    defined_for = "co_ccap_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.ccap
        person = tax_unit.members
        # Calculate base parent fee and add on parent fee.
        agi = tax_unit("adjusted_gross_income", period)
        hhs_fpg = tax_unit("tax_unit_fpg", period)
        num_child_age_eligible = tax_unit(
            "co_ccap_num_child_eligible", period
        )

        # The numebrs below are weights copied from government spreadsheet (url: )
        base_parent_fee = np.round(
            where(
                agi <= hhs_fpg,
                agi * 0.01 / 12,
                (hhs_fpg * 0.01 + (agi - hhs_fpg) * 0.14) / 12,
            ),
            2,
        )
        add_on_parent_fee = where(
            agi > hhs_fpg, (num_child_age_eligible - 1) * 15, 0
        )

        # Sum up all the parent fee for eligible children.
        child_age_eligible = person("co_ccap_child_eligible", period)
        childcare_hours_per_day = person("childcare_hours_per_day", period)
        rate = p.parent_fee_rate_by_child_care_hours.calc(
            childcare_hours_per_day, right=True
        )
        non_discouted_fee = np.round(
            tax_unit.sum(
                child_age_eligible
                * (base_parent_fee + add_on_parent_fee)
                * rate
            ),
            2,
        )

        # Identify whether the filers are eligible for a discount.
        rating = person("co_quality_rating_of_child_care_facility", period)
        discount_eligible = (
            tax_unit.sum(
                p.is_quality_rating_discounted.calc(rating)
                & child_age_eligible
            )
            > 0
        )

        discounted_rate = p.quality_discounted_rate

        return np.round(
            where(
                discount_eligible,
                non_discouted_fee * discounted_rate,
                non_discouted_fee,
            ),
            2,
        )
