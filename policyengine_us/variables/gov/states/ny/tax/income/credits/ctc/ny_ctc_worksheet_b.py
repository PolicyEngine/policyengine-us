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
        # Line 2 NY recomputed FAGI - DO WE HAVE THIS?
        # some years use this while some are not
        ny_recomputed_agi
        # Line 3
        foreign_earned_income_exclusion = tax_unit(
            "foreign_earned_income_exclusion", period
        )
        puerto_rico_income = tax_unit("puerto_rico_income", period)
        total_exclusive = foreign_earned_income_exclusion + puerto_rico_income
        # Line 4
        total = total_exclusive + ny_recomputed_agi
        # Line 5
        federal_threshold = gov.irs.credits.ctc.phase_out.threshold[
            tax_unit("filing_status", period)
        ]
        # Line 6
        federal_round_amount = max_(
            math.ceil(total - federal_threshold / p.amount.base)
            * p.amount.base,
            0,
        )
        # Line 7
        subtract_amount = federal_round_amount * p.amount.match
        # Line 8
        federal_adjusted_amount = max_(base_amount - subtract_amount, 0)
        # Line 9
        tax = tax_unit("income_tax", period)
        # Line 10 compare NY agi and NY recomputed FAGI
        ny_agi = tax_unit("ny_agi", period)
        # add come lines from form 1040
        # Line 11 - maybe = line 10, need eligibility check
        # Line 12 = Line 9 - Line 11
        # Line 13 = min_(federal_adjusted_amount, Line 12)
        # return Line 13
