from policyengine_us.model_api import *


class vt_military_retirement_pay_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont military retirement income exclusion"
    reference = (
        "https://tax.vermont.gov/individuals/seniors-and-retirees",
        "https://legislature.vermont.gov/statutes/section/32/151/05830e",  # Legal Code Titl. 32 V.S.A. § 5830e (d)
    )
    unit = USD
    defined_for = StateCode.VT
    documentation = (
        "Vermont military retirement benefits exempt from Vermont taxation."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.retirement_income_exemption
        # Get retirement amount from military retirement system
        tax_unit_military_retirement_pay = add(
            tax_unit, period, ["military_retirement_pay"]
        )

        # S.51 (2025): Income-based military pension exemption
        income_based_effective_date = (
            p.military_retirement.income_based_effective_date
        )
        is_income_based_system = (
            period.start.year >= income_based_effective_date
        )
        agi = tax_unit("adjusted_gross_income", period)

        # Full exemption for households under $125k AGI
        full_exemption_threshold = (
            p.military_retirement.full_exemption_threshold
        )
        # Partial exemption for households under $175k AGI
        partial_exemption_threshold = (
            p.military_retirement.partial_exemption_threshold
        )

        # 2025+ income-based exemption
        income_based_exemption = where(
            agi < full_exemption_threshold,
            # Full exemption: all military retirement pay
            tax_unit_military_retirement_pay,
            where(
                agi < partial_exemption_threshold,
                # Partial exemption: linear phaseout between $125k and $175k
                tax_unit_military_retirement_pay
                * (partial_exemption_threshold - agi)
                / (partial_exemption_threshold - full_exemption_threshold),
                # No exemption above $175k
                0,
            ),
        )

        # Pre-2025: Use the original cap-based system
        cap_based_exemption = min_(
            tax_unit_military_retirement_pay, p.military_retirement.amount
        )

        return where(
            is_income_based_system,
            income_based_exemption,
            cap_based_exemption,
        )
