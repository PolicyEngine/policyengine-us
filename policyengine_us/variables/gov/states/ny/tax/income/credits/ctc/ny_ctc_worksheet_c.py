from policyengine_us.model_api import *
import math


class ny_ctc_worksheet_c(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY Worksheet c for Form IT-213"
    documentation = "New York's Empire State Child Credit Worksheet C"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf#page=5"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        person = tax_unit.members
        # ??? Line 1 - worksheet a line 6 or worksheet b line 8: how to grab middle result?
        # federal_adjusted_amount
        # Line 2 -  Worksheet A, line 10 or Worksheet B, line 13
        # ny_ctc_worksheet_a OR ny_ctc_worksheet_b
        # Line 3
        adjusted_amount = max_(
            federal_adjusted_amount - ny_ctc_worksheet_a_or_b, 0
        )
        # Line 4a
        earned_income = tax_unit("tax_unit_earned_income", period)
        # ??? Line 4b - Nontaxable combat pay DO WE HAVE THIS???
        # Line 5
        adjusted_earned_income = max_(
            earned_income - p.amount.earned_income_adjust_amount, 0
        )
        # Line 6
        adjusted_earned_income_match = (
            adjusted_earned_income * p.amount.earned_income_match
        )
        # Line 7
        qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
        qualifying_children = tax_unit.sum(qualifies_for_federal_ctc)
        multi_children_family = (
            qualifying_children >= p.additional_number_of_children
        )
        multi_children_amount = where(
            adjusted_earned_income_match >= adjusted_amount, adjusted_amount
        )  # federal Schedule 8812, line 25)
        # Line 8
        adjusted_multi_children_amount = max_(
            multi_children_amount, adjusted_earned_income_match
        )
        # Line 9
        min_multi_children_amount = min_(
            adjusted_amount, adjusted_multi_children_amount
        )
        min_adjusted_earned_income_match = min_(
            adjusted_amount, adjusted_earned_income_match
        )
        return where(
            multi_children_family,
            min_multi_children_amount,
            min_adjusted_earned_income_match,
        )
