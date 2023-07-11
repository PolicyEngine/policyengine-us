from policyengine_us.model_api import *


class nm_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico standard deduction"
    unit = USD
    documentation = 'https://www.irs.gov/instructions/i1040gi#en_US_2022_publink24811vd0e10057'
    definition_period = YEAR
    defined_for = StateCode.NM
    # adds = ["basic_standard_deduction", "additional_standard_deduction"]

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        base_amt = p.base[filing_status]
        # is_aged or blind?
        aged_blind_count = tax_unit("aged_blind_count", period)
        extra_amt = aged_blind_count * p.elderly_blind[filing_status]
        return base_amt + extra_amt