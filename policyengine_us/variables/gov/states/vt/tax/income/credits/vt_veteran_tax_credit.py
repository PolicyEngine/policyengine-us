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
        # Check if anyone in tax unit is a veteran
        person = tax_unit.members
        is_veteran = person("is_veteran", period)
        veteran_present = tax_unit.any(is_veteran)

        # Get parameters for veteran credit
        p = parameters(period).gov.states.vt.tax.income.credits.veteran

        # Get adjusted gross income for phaseout
        agi = tax_unit("adjusted_gross_income", period)

        # Full credit for households under $25k AGI
        # Partial credit for households under $30k AGI

        # Calculate credit amount based on veteran status and income
        eligible_for_full_credit = veteran_present & (
            agi < p.full_credit_threshold
        )
        eligible_for_partial_credit = (
            veteran_present
            & (agi >= p.full_credit_threshold)
            & (agi < p.partial_credit_threshold)
        )

        # Calculate partial credit amount based on parameterized reduction structure
        excess_income = agi - p.full_credit_threshold
        # Number of income increments (rounded up)
        income_increments = np.ceil(excess_income / p.income_increment)
        # Reduction per increment
        reduction_amount = income_increments * p.reduction_per_increment
        # Calculate partial credit (minimum of 0)
        partial_credit_amount = max_(p.amount - reduction_amount, 0)

        return where(
            eligible_for_full_credit,
            p.amount,
            where(
                eligible_for_partial_credit,
                partial_credit_amount,
                0,
            ),
        )
