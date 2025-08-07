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
        is_income_based_system = (
            p.military_retirement.income_based_structure.in_effect
        )
        agi = tax_unit("adjusted_gross_income", period)

        # Calculate exemption based on system type
        income_based_exemption = tax_unit(
            "vt_military_retirement_income_based_exemption", period
        )
        cap_based_exemption = tax_unit(
            "vt_military_retirement_cap_based_exemption", period
        )

        return where(
            is_income_based_system,
            income_based_exemption,
            cap_based_exemption,
        )
