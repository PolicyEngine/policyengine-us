from policyengine_us.model_api import *


class ny_ctc_worksheet_a(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY Worksheet A for Form IT-213"
    documentation = "New York's Empire State Child Credit Worksheet A"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf#page=2"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        person = tax_unit.members
        # Line 1
        ctc_qualifying_child = person("ctc_qualifying_child", period)
        qualifying_children = tax_unit.sum(ctc_qualifying_child)
        base_credit = qualifying_children * p.amount.base
        # Line 2 NY State AGI - Line 19a from Form IT-201
        fagi = tax_unit("adjusted_gross_income", period)
        # Line 3
        federal_threshold = gov.irs.credits.ctc.phase_out.threshold[
            tax_unit("filing_status", period)
        ]
        # Line 4
        agi_over_threshold = fagi > federal_threshold
        # The reduced AGI is rounded up to the nearest NY CTC base amount
        rounded_reduced_agi_multiple = np.ceil(
            ny_agi - federal_threshold / p.amount.base
        )
        rounded_reduced_agi_amount = (
            rounded_reduced_agi_multiple * p.amount.base
        )
        rounded_reduced_agi = where(
            agi_over_threshold, rounded_reduced_agi_amount, 0
        )
        # Line 5
        fraction_credit = rounded_reduced_agi * p.amount.match
        # Line 6
        base_credit_over_fraction_credit = base_credit > fraction_credit
        reduced_credit = where(
            base_credit_over_fraction_credit, base_credit - fraction_credit, 0
        )
        # Part 2 from Worksheet A
        # Line 7
        tax = tax_unit("income_tax", period)
        # Line 8 - Line 19 and 19a from Form IT-201 - these are the same in our model
        selected_credit_amount = tax_unit("ny_ctc_federal_credits", period)
        # Line 9 check if line 7 and line 8 have the same amount
        tax_over_credit = max_(0, tax - selected_credit_amount)
        # Line 10 = min_(line 6, line 9)
        return min_(reduced_credit, tax_over_credit)
