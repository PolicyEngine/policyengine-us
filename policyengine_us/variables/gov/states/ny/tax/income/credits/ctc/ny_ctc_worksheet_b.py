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
        federal_round_amount = max_(
            math.ceil(
                AGI_with_exclusion_amount - federal_threshold / p.amount.base
            )
            * p.amount.base,
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
        # line11_amount = where(foreign_tax_credit_eligible, selected_credit_amount, )
        # Line 12 = Line 9 - Line 11
        # Line 13 = min_(federal_adjusted_amount, Line 12)
        # return Line 13
