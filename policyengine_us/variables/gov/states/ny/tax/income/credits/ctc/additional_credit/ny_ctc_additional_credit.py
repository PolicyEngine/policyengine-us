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
        pre_reduction_base_credit = tax_unit("ny_ctc_pre_reduction_base_credit", period)
        base_credit = tax_unit("ny_ctc_base_credit", period)
        # Line 3
        reduced_base_credit = pre_reduction_base_credit - base_credit
        # Line 4
        earned_income = tax_unit("tax_unit_earned_income", period)
        if period.start.year >= 2021:
            instant_str = f"2020-01-01"
        else:
            instant_str = period
        p_gov = parameters(instant_str).gov.irs.credits.ctc.refundable.phase_in
        earned_income_over_threshold = earned_income > p_gov.threshold
        # Line 5
        reduced_earned_income = where(earned_income_over_threshold, earned_income - p_gov.threshold, 0)
        # Line 6
        earned_income_fraction = reduced_earned_income * p.match
        qualifying_children = tax_unit("ctc_qualifying_children", period)
        p_gov = parameters(period).gov.irs.credits.ctc.refundable.phase_in
        children_over_threshold = qualifying_children > p_gov.min_children_for_ss_taxes_minus_eitc
        smaller_of_earned_income_or_reduced_base = min_(reduced_base_credit, earned_income_fraction)
        