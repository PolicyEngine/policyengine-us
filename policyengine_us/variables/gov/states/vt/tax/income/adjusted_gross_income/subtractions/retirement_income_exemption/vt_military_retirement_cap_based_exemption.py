from policyengine_us.model_api import *


class vt_military_retirement_cap_based_exemption(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont military retirement cap-based exemption"
    reference = "https://tax.vermont.gov/sites/tax/files/documents/IN-112-Instr-2024.pdf#page=2"
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont military retirement benefits exempt from Vermont taxation up to cap amount (pre-2025)."

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.retirement_income_exemption.military_retirement

        # Get retirement amount from military retirement system
        tax_unit_military_retirement_pay = add(
            tax_unit, period, ["military_retirement_pay"]
        )

        # Cap exemption at the specified amount
        return min_(tax_unit_military_retirement_pay, p.amount)
