from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_wa_sb6346() -> Reform:
    """
    WA SSB 6346 - 9.9% income tax on high earners.

    Imposes a 9.9% tax on Washington taxable income (federal AGI minus
    a $1M standard deduction and capped charitable deduction).

    Reference: https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/6346-S.pdf
    """

    class wa_income_tax_base_income(Variable):
        value_type = float
        entity = TaxUnit
        label = "Washington base income under SSB 6346"
        unit = USD
        definition_period = YEAR
        reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/6346-S.pdf#page=5"
        defined_for = StateCode.WA
        adds = ["adjusted_gross_income"]

    class wa_income_tax_charitable_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Washington income tax charitable deduction under SSB 6346"
        unit = USD
        definition_period = YEAR
        reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/6346-S.pdf#page=10"
        defined_for = StateCode.WA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.wa.sb6346.charitable_deduction.cap
            filing_status = tax_unit("filing_status", period)
            charitable = add(
                tax_unit,
                period,
                ["charitable_cash_donations", "charitable_non_cash_donations"],
            )
            is_joint = filing_status == filing_status.possible_values.JOINT
            cap = where(is_joint, p.joint, p.individual)
            return min_(charitable, cap)

    class wa_income_tax_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Washington income tax standard deduction under SSB 6346"
        unit = USD
        definition_period = YEAR
        reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/6346-S.pdf#page=10"
        defined_for = StateCode.WA
        adds = ["gov.contrib.states.wa.sb6346.standard_deduction.amount"]

    class wa_income_tax_taxable_income(Variable):
        value_type = float
        entity = TaxUnit
        label = "Washington taxable income under SSB 6346"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/6346-S.pdf#page=10",
            "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/6346-S.pdf#page=11",
        )
        defined_for = StateCode.WA

        def formula(tax_unit, period, parameters):
            in_effect = parameters(period).gov.contrib.states.wa.sb6346.in_effect
            base_income = tax_unit("wa_income_tax_base_income", period)
            charitable_deduction = tax_unit(
                "wa_income_tax_charitable_deduction", period
            )
            standard_deduction = tax_unit("wa_income_tax_standard_deduction", period)
            return where(
                in_effect,
                max_(base_income - charitable_deduction - standard_deduction, 0),
                0,
            )

    class wa_income_tax_before_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Washington income tax before refundable credits"
        unit = USD
        definition_period = YEAR
        reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/6346-S.pdf#page=6"
        defined_for = StateCode.WA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.wa.sb6346
            in_effect = p.in_effect
            taxable_income = tax_unit("wa_income_tax_taxable_income", period)
            sb6346_tax = taxable_income * p.rate
            capital_gains_tax = tax_unit("wa_capital_gains_tax", period)
            return where(in_effect, sb6346_tax + capital_gains_tax, capital_gains_tax)

    class wa_income_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "Washington income tax"
        unit = USD
        definition_period = YEAR
        reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/6346-S.pdf#page=6"
        defined_for = StateCode.WA
        adds = ["wa_income_tax_before_refundable_credits"]
        subtracts = ["wa_refundable_credits"]

    class wa_working_families_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Washington Working Families Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://app.leg.wa.gov/RCW/default.aspx?cite=82.08.0206",
            "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/6346-S.pdf#page=53",
        )
        defined_for = StateCode.WA

        def formula(tax_unit, period, parameters):
            eitc = tax_unit("eitc", period)
            eitc_eligible = eitc > 0
            # SSB 6346 Sec. 901(2)(a)(ii)(C): individuals who do not meet
            # the EITC age requirement but are at least age 18.
            reform_in_effect = parameters(period).gov.contrib.states.wa.sb6346.in_effect
            sb6346_p = parameters(period).gov.contrib.states.wa.sb6346.wftc
            expansion_in_effect = reform_in_effect & sb6346_p.in_effect
            age_head = tax_unit("age_head", period)
            age_spouse = tax_unit("age_spouse", period)
            filer_at_least_min_age = expansion_in_effect & (
                (age_head >= sb6346_p.min_age) | (age_spouse >= sb6346_p.min_age)
            )
            earned_income = tax_unit("filer_adjusted_earnings", period)
            has_earned_income = earned_income > 0
            eligible = eitc_eligible | (filer_at_least_min_age & has_earned_income)
            p = parameters(
                period
            ).gov.states.wa.tax.income.credits.working_families_tax_credit
            eitc_child_count = tax_unit("eitc_child_count", period)
            max_amount = p.amount.calc(eitc_child_count)
            eitc_agi_limit = tax_unit("eitc_agi_limit", period)
            phase_out_start_reduction = p.phase_out.start_below_eitc.calc(
                eitc_child_count
            )
            phase_out_start = eitc_agi_limit - phase_out_start_reduction
            phase_out_rate = (max_amount - p.min_amount) / phase_out_start_reduction
            excess = max_(0, earned_income - phase_out_start)
            reduction = max_(0, excess * phase_out_rate)
            phased_out_amount = max_amount - reduction
            amount_if_eligible = where(
                phased_out_amount > 0,
                max_(p.min_amount, phased_out_amount),
                0,
            )
            return amount_if_eligible * eligible

    class reform(Reform):
        def apply(self):
            self.update_variable(wa_income_tax_base_income)
            self.update_variable(wa_income_tax_charitable_deduction)
            self.update_variable(wa_income_tax_standard_deduction)
            self.update_variable(wa_income_tax_taxable_income)
            self.update_variable(wa_income_tax_before_refundable_credits)
            self.update_variable(wa_income_tax)
            self.update_variable(wa_working_families_tax_credit)

    return reform


def create_wa_sb6346_reform(parameters, period, bypass=False):
    if bypass:
        return create_wa_sb6346()

    p = parameters.gov.contrib.states.wa.sb6346

    reform_active = False
    current_period = period_(period)

    # Match the standard five-year structural reform lookahead used across
    # the repo so future-year simulations can pick up contributed reforms.
    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_wa_sb6346()
    else:
        return None


wa_sb6346 = create_wa_sb6346_reform(None, None, bypass=True)
