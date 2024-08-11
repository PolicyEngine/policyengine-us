from policyengine_us.model_api import *


class ny_additional_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York additional Empire State Child Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)(4)(A)
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states.ny.tax.income.credits.ctc.additional
        match = p.amount.calc(agi)
        base_ctc = tax_unit("ny_ctc", period)
        credit_amount = base_ctc * match
        credit_above_min_amount = base_ctc >= p.min_ctc
        return where(credit_above_min_amount, credit_amount, 0)

