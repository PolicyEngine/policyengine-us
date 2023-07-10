from policyengine_us.model_api import *


class vt_standard_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "VT standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Vermont standard deduction, including bonus for aged or blind."
    )
    reference = "Hold"
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.deductions.standard
        # Base deduction based on filing status.
        filing_status = tax_unit("filing_status", period)
        base_deduction = p.base[filing_status]
        # Aged/blind extra standard deduction.
        aged_blind_count = tax_unit("aged_blind_count", period)
        amount_per_aged_blind = p.extra[filing_status]
        aged_blind_deduction = aged_blind_count * amount_per_aged_blind
        return base_deduction + aged_blind_deduction
