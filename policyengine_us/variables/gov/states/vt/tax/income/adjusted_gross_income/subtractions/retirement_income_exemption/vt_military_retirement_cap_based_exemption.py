from policyengine_us.model_api import *


class vt_military_retirement_cap_based_exemption(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont military retirement cap-based exemption"
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-Instr-2024.pdf#page=2"
    )
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont military retirement benefits exempt from Vermont taxation up to cap amount (pre-2025)."

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.retirement_income_exemption.military_retirement

        # Get retirement amount from military retirement system
        # Dependents' income is not in federal AGI; they report it on their
        # own return, so only the head's and spouse's pay counts.
        tax_unit_military_retirement_pay = tax_unit_non_dep_sum(
            "military_retirement_pay", tax_unit, period
        )

        # Cap exemption at the specified amount
        return min_(tax_unit_military_retirement_pay, p.amount)
