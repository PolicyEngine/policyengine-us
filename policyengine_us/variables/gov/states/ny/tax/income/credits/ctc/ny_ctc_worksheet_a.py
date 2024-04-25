from policyengine_us.model_api import *
import math


class ny_ctc_worksheet_a(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY Worksheet A for Form IT-213,"
    documentation = "New York's Empire State Child Credit Worksheet A"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf#page=2"
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
        federal_threshold = gov.irs.credits.ctc.phase_out.threshold[
            tax_unit("filing_status", period)
        ]
        # Line 4
        federal_round_amount = max_(
            math.ceil(ny_recomputed_agi - federal / p.amount.base)
            * p.amount.base,
            0,
        )
        # Line 5
        subtract_amount = federal_round_amount * p.amount.match
        # Line 6
        federal_adjusted_amount = max_(base_amount - subtract_amount, 0)
        # Line 7
        tax = tax_unit("income_tax", period)
        # Line 8 compare NY agi and NY recomputed FAGI
        ny_agi = tax_unit("ny_agi", period)
        # add come lines from form 1040
        # Line 9  = max_(line 7 - line 8, 0)
        # Line 10 = min_(line 6, line 9)
        return line 10

