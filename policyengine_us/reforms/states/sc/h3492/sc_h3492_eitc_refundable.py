from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_sc_h3492_eitc_refundable() -> Reform:
    """
    South Carolina H.3492 - Partially Refundable EITC

    Amends SC Code Section 12-6-3632 to make a portion of the state EITC
    refundable. If the SC EITC (125% of federal) exceeds the taxpayer's
    state income tax liability, 25% of the excess is refunded.

    Reference: https://www.scstatehouse.gov/sess126_2025-2026/bills/3492.htm
    """

    class sc_h3492_total_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "SC H.3492 total EITC amount"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.scstatehouse.gov/sess126_2025-2026/bills/3492.htm",
            "https://www.scstatehouse.gov/code/t12c006.php",
        )
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            federal_eitc = tax_unit("eitc", period)
            rate = parameters(
                period
            ).gov.states.sc.tax.income.credits.eitc.rate
            return np.round(federal_eitc * rate, 1)

    class sc_h3492_other_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "SC non-refundable credits excluding EITC"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            # Sum non-refundable credits excluding EITC
            cdcc = tax_unit("sc_cdcc", period)
            two_wage = tax_unit("sc_two_wage_earner_credit", period)
            return cdcc + two_wage

    class sc_h3492_tax_liability_for_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "SC tax liability available for EITC"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            # Tax before non-refundable credits minus other credits
            tax_before = tax_unit(
                "sc_income_tax_before_non_refundable_credits", period
            )
            other_credits = tax_unit(
                "sc_h3492_other_non_refundable_credits", period
            )
            return max_(0, tax_before - other_credits)

    class sc_h3492_eitc_non_refundable(Variable):
        value_type = float
        entity = TaxUnit
        label = "SC H.3492 EITC non-refundable portion"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.scstatehouse.gov/sess126_2025-2026/bills/3492.htm",
        )
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            total_eitc = tax_unit("sc_h3492_total_eitc", period)
            tax_liability = tax_unit("sc_h3492_tax_liability_for_eitc", period)
            # Non-refundable portion is limited to tax liability
            return min_(total_eitc, tax_liability)

    class sc_h3492_eitc_refundable(Variable):
        value_type = float
        entity = TaxUnit
        label = "SC H.3492 EITC refundable portion"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.scstatehouse.gov/sess126_2025-2026/bills/3492.htm",
        )
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.sc.h3492
            total_eitc = tax_unit("sc_h3492_total_eitc", period)
            non_refundable = tax_unit("sc_h3492_eitc_non_refundable", period)
            excess = max_(0, total_eitc - non_refundable)
            return excess * p.refundable_excess_rate

    class sc_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "South Carolina non-refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            # Other non-refundable credits plus the non-refundable EITC portion
            other_credits = tax_unit(
                "sc_h3492_other_non_refundable_credits", period
            )
            eitc_non_refundable = tax_unit(
                "sc_h3492_eitc_non_refundable", period
            )
            return other_credits + eitc_non_refundable

    class sc_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "South Carolina refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.sc.tax.income.credits
            standard_credits = add(tax_unit, period, p.refundable)
            # Add refundable EITC portion from H.3492
            eitc_refundable = tax_unit("sc_h3492_eitc_refundable", period)
            return standard_credits + eitc_refundable

    class reform(Reform):
        def apply(self):
            self.update_variable(sc_h3492_total_eitc)
            self.update_variable(sc_h3492_other_non_refundable_credits)
            self.update_variable(sc_h3492_tax_liability_for_eitc)
            self.update_variable(sc_h3492_eitc_non_refundable)
            self.update_variable(sc_h3492_eitc_refundable)
            self.update_variable(sc_non_refundable_credits)
            self.update_variable(sc_refundable_credits)

    return reform


def create_sc_h3492_eitc_refundable_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_sc_h3492_eitc_refundable()

    p = parameters.gov.contrib.states.sc.h3492

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_sc_h3492_eitc_refundable()
    else:
        return None


sc_h3492_eitc_refundable = create_sc_h3492_eitc_refundable_reform(
    None, None, bypass=True
)
