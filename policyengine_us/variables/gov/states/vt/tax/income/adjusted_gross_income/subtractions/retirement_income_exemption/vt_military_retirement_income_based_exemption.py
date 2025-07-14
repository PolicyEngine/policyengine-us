from policyengine_us.model_api import *


class vt_military_retirement_income_based_exemption(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont military retirement income-based exemption"
    reference = "https://legislature.vermont.gov/Documents/2026/Docs/BILLS/S-0051/S-0051%20As%20Passed%20by%20Both%20House%20and%20Senate%20Official.pdf#page=10"
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont military retirement benefits exempt from Vermont taxation based on AGI thresholds (2025+)."

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.retirement_income_exemption.military_retirement

        # Get retirement amount from military retirement system
        tax_unit_military_retirement_pay = add(
            tax_unit, period, ["military_retirement_pay"]
        )

        agi = tax_unit("adjusted_gross_income", period)

        # Full exemption for households under $125k AGI
        full_exemption_threshold = p.full_exemption_threshold
        # Partial exemption for households under $175k AGI
        partial_exemption_threshold = p.partial_exemption_threshold

        # Full exemption if below $125k
        eligible_for_full_exemption = agi < full_exemption_threshold

        # Partial exemption if between $125k and $175k
        eligible_for_partial_exemption = (agi >= full_exemption_threshold) & (
            agi < partial_exemption_threshold
        )

        # Calculate partial exemption amount (linear phaseout)
        partial_exemption_amount = (
            tax_unit_military_retirement_pay
            * (partial_exemption_threshold - agi)
            / (partial_exemption_threshold - full_exemption_threshold)
        )

        return where(
            eligible_for_full_exemption,
            tax_unit_military_retirement_pay,
            where(
                eligible_for_partial_exemption,
                partial_exemption_amount,
                0,
            ),
        )
