from policyengine_us.model_api import *


class ny_ctc_additional_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York CTC additional credit"
    documentation = "New York's Empire State Child Credit Worksheet C"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf#page=5"
    defined_for = "ny_ctc_additional_credit_eligible"

    def formula(tax_unit, period, parameters):
        pre_reduction_base_credit = tax_unit(
            "ny_ctc_pre_reduction_base_credit", period
        )
        base_credit = tax_unit("ny_ctc_base_credit", period)
        # Line 3
        reduced_base_credit = pre_reduction_base_credit - base_credit
        # Line 4
        earned_income = tax_unit("tax_unit_earned_income", period)
        if period.start.year >= 2018:
            instant_str = f"2017-01-01"
        else:
            instant_str = period
        p_gov = parameters(instant_str).gov.irs.credits.ctc.refundable.phase_in
        earned_income_over_threshold = earned_income > p_gov.threshold
        # Line 5
        reduced_earned_income = where(
            earned_income_over_threshold, earned_income - p_gov.threshold, 0
        )
        # Line 6
        earned_income_fraction = reduced_earned_income * p.match
        # Line 7
        qualifying_children = tax_unit("ctc_qualifying_children", period)
        children_over_threshold = (
            qualifying_children > p_gov.min_children_for_ss_taxes_minus_eitc
        )
        smaller_of_earned_income_or_reduced_base = min_(
            reduced_base_credit, earned_income_fraction
        )
        # Calculation from federal schedule 8812 line 25
        SS_ADD_VARIABLES = [
            # Person:
            "employee_social_security_tax",
            "employee_medicare_tax",
            "unreported_payroll_tax",
            # Tax unit:
            "self_employment_tax_ald",
            "additional_medicare_tax",
        ]
        SS_SUBTRACT_VARIABLES = ["excess_payroll_tax_withheld"]
        social_security_tax = add(tax_unit, period, SS_ADD_VARIABLES) - add(
            tax_unit, period, SS_SUBTRACT_VARIABLES
        )
        eitc = tax_unit("eitc", period)
        social_security_excess = max_(0, social_security_tax - eitc)
        # Line 8
        larger_of_ss_excess_or_earned_income = max_(
            social_security_excess, earned_income_fraction
        )
        # Line 9
        smaller_of_base_credit_or_larger_of_ss_excess_or_earned_income = min_(
            reduced_base_credit, larger_of_ss_excess_or_earned_income
        )
        base_credit_over_earned_income_fraction = (
            reduced_base_credit > earned_income_fraction
        )
        equal_or_more_than_three_children_calc = where(
            base_credit_over_earned_income_fraction,
            smaller_of_base_credit_or_larger_of_ss_excess_or_earned_income,
            reduced_base_credit,
        )
        return where(
            children_over_threshold,
            equal_or_more_than_three_children_calc,
            smaller_of_earned_income_or_reduced_base,
        )
