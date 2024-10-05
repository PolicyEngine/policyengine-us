from policyengine_us.model_api import *


class vt_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf",  # Line4
        "http://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(C)(ii)(iii)
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.deductions.standard
        # Base deduction based on filing status.
        filing_status = tax_unit("filing_status", period)
        base_deduction = p.base[filing_status]
        # Vermont mirrors the federal definition of aged/blind by citing 26 U.S.C. § 63(f).
        # The aged_blind_count variable captures this, for head and spouse.
        aged_blind_count = tax_unit("aged_blind_count", period)
        aged_blind_deduction = aged_blind_count * p.additional
        return base_deduction + aged_blind_deduction
