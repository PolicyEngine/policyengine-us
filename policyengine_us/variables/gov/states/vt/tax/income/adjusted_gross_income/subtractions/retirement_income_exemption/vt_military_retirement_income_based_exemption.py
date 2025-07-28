from policyengine_us.model_api import *
import numpy as np


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

        # Check if thresholds are finite (feature is active)
        thresholds_are_finite = ~np.isinf(
            p.full_exemption_threshold
        ) & ~np.isinf(p.partial_exemption_threshold)

        # Full exemption if below the threshold AND thresholds are finite
        eligible_for_full_exemption = thresholds_are_finite & (
            agi < p.full_exemption_threshold
        )

        # Partial exemption if between the thresholds AND thresholds are finite
        eligible_for_partial_exemption = (
            thresholds_are_finite
            & (agi >= p.full_exemption_threshold)
            & (agi <= p.partial_exemption_threshold)
        )

        # Calculate partial exemption amount (linear phaseout)
        threshold_difference = (
            p.partial_exemption_threshold - p.full_exemption_threshold
        )
        agi_below_threshold = max_(p.partial_exemption_threshold - agi, 0)

        # Use mask to avoid division by zero
        valid_threshold_difference = threshold_difference != 0
        partial_exemption_amount = where(
            valid_threshold_difference,
            tax_unit_military_retirement_pay
            * agi_below_threshold
            / threshold_difference,
            0,
        )

        # Calculate exemption amounts for each case
        full_exemption_amount = tax_unit_military_retirement_pay
        partial_exemption_amount_capped = max_(partial_exemption_amount, 0)
        no_exemption_amount = 0

        # First determine if partial or no exemption
        partial_or_no_exemption = where(
            eligible_for_partial_exemption,
            partial_exemption_amount_capped,
            no_exemption_amount,
        )

        # Then determine final exemption amount
        exemption_amount = where(
            eligible_for_full_exemption,
            full_exemption_amount,
            partial_or_no_exemption,
        )

        return exemption_amount
