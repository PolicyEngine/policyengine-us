from policyengine_us.model_api import *


class vt_veteran_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont veteran tax credit"
    definition_period = YEAR
    unit = USD
    reference = [
        "https://vtdigger.org/2025/06/25/gov-phil-scott-signs-13-5-million-tax-credit-package-benefiting-low-income-workers-families-retirees-and-veterans/"
    ]
    defined_for = StateCode.VT
    documentation = "Vermont veteran tax credit providing $250 refundable credit for low-income veterans as part of S.51 (2025) tax relief package."

    def formula(tax_unit, period, parameters):
        # Only applies starting in 2025
        if period.start.year < 2025:
            return 0

        # Check if anyone in tax unit is a veteran
        person = tax_unit.members
        is_veteran = person("is_veteran", period)
        has_veteran = tax_unit.any(is_veteran)

        # Get parameters for veteran credit
        p = parameters(period).gov.states.vt.tax.income.credits.veteran

        # Get adjusted gross income for phaseout
        agi = tax_unit("adjusted_gross_income", period)

        # Full credit for households under $25k AGI
        full_credit_threshold = p.full_credit_threshold
        # Partial credit for households under $30k AGI
        partial_credit_threshold = p.partial_credit_threshold

        # Calculate credit amount
        credit_amount = where(
            has_veteran & (agi < full_credit_threshold),
            # Full credit
            p.amount,
            where(
                has_veteran & (agi < partial_credit_threshold),
                # Partial credit: linear phaseout between $25k and $30k
                p.amount
                * (partial_credit_threshold - agi)
                / (partial_credit_threshold - full_credit_threshold),
                # No credit above $30k or for non-veterans
                0,
            ),
        )

        return credit_amount
