from policyengine_us.model_api import *
import math


class ny_ctc_worksheet_a(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY Worksheet A for Form IT-213"
    documentation = "New York's Empire State Child Credit Worksheet B"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf#page=3"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        person = tax_unit.members
        # Line 1
        qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
        qualifying_children = tax_unit.sum(qualifies_for_federal_ctc)
        base_amount = qualifying_children * p.amount.base
        # Line 2 NY recomputed FAGI - use normal FAGI
        fagi = tax_unit("adjusted_gross_income", period)
        # Line 3
        foreign_earned_income_exclusion = tax_unit(
            "foreign_earned_income_exclusion", period
        )
        puerto_rico_income = tax_unit("puerto_rico_income", period)
        total_exclusive_amount = (
            foreign_earned_income_exclusion + puerto_rico_income
        )
        # Line 4
        AGI_with_exclusion_amount = total_exclusive_amount + fagi
        # Line 5
        federal_threshold = gov.irs.credits.ctc.phase_out.threshold[
            tax_unit("filing_status", period)
        ]
        # Line 6
        agi_round = math.ceil(
            AGI_with_exclusion_amount - federal_threshold / p.amount.base
        )
        federal_round_amount = max_(
            agi_round * p.amount.base,
            0,
        )
        # Line 7
        subtraction_amount = federal_round_amount * p.amount.match
        # Line 8
        federal_adjusted_amount = max_(base_amount - subtraction_amount, 0)
        # Line 9
        tax = tax_unit("income_tax", period)
        # Line 10 ccompare agi and recomputed FAGI - skip here, assume they are same
        selected_credit_amount = tax_unit("ny_ctc_federal_credits", period)

        # Line 11 - assume claimed any of the mentioned federal credits
        # check if filed federal Form 2555
        foreign_tax_credit_eligible = (
            tax_unit("foreign_tax_credit", period) > 0
        )
        # Line 11 worksheet
        # Line 11 - 1: line 8 of worksheet B
        # ??? Line 11 - 2: only considering earned income here "https://www.irs.gov/pub/irs-prior/i1040s8--2021.pdf#page=10"
        earned_income_person = person("earned_income", period)
        earned_income = tax_unit.sum(earned_income_person)
        # Line 11 - 3: earned income adjustment
        earned_income_adjustment = max_(
            earned_income - p.amount.earned_income_adjust_amount, 0
        )
        # Line 11 - 4: earned income match
        earned_income_match = (
            earned_income_adjustment * p.amount.earned_income_match
        )
        # Line 11 - 5: federal adjustment amount
        # federal_adjusted_amount  > p.amount.earned_income_adjust_amount, earned_income_match >= federal_adjusted_amount: 0
        # federal_adjusted_amount  > p.amount.earned_income_adjust_amount, earned_income_match < federal_adjusted_amount: line 6
        # federal_adjusted_amount  > p.amount.earned_income_adjust_amount, earned_income_match > 0
        # ??? Line 11 - 6: credit limit line 11 "https://www.irs.gov/pub/irs-prior/i1040s8--2021.pdf#page=7"
        # Line 11 - 7: max_(earned_income_match, credit limit)
        # Line 11 - 8: federal_adjusted_amount - line 7
        # ??? Line 11 - 9: credit limit line 15 "https://www.irs.gov/pub/irs-prior/i1040s8--2021.pdf#page=7"
        # Line 11 - 10: federal_round_amount
        # Line 11 - 11: line11_amount = where(foreign_tax_credit_eligible, selected_credit_amount, federal_round_amount + credit limit line 15)

        # Line 12 = Line 9 - Line 11
        # Line 13 = min_(federal_adjusted_amount, Line 12)
        # return Line 13
