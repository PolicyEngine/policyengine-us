from policyengine_us.model_api import *


class ny_itemized_deductions_phase_out_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether the pre-TCJA overall limitation on New York itemized deductions applies"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/68#b",  # applicable amount
        "https://www.tax.ny.gov/pdf/current_forms/it/it196i.pdf#page=19",  # Line 40 worksheet, line 7
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        # IT-196 Line 40 worksheet, lines 5-7: the limitation only applies when
        # federal AGI (Form IT-201/IT-203 line 19) exceeds the Table 1
        # applicable amount for the filing status. NY Tax Law § 615 conforms to
        # the pre-TCJA federal 26 U.S.C. § 68(b) applicable amount, which NY
        # continues to inflation-adjust.
        p = parameters(period).gov.states.ny.tax.income.deductions.itemized.phase_out
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        applicable_amount = p.start[filing_status]
        return agi > applicable_amount
