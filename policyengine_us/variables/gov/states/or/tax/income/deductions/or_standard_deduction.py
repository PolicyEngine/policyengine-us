from policyengine_us.model_api import *


class or_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Oregon standard deduction, including bonus for aged or blind and special rules for filers who are claimable as dependents."
    reference = (  # TODO: update
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=18",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",  # Subsection 316.695 (7)
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["or"].tax.income.deductions.standard
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)
        initial_core_deduction = p.amount[filing_status]
        # Replace if claimable as a dependent.
        earned_income = tax_unit("tax_unit_earned_income", period)
        claimable_dep_floor = p.claimable_as_dependent.min
        claimable_dep_earned_amount = (
            earned_income + p.claimable_as_dependent.earned_income_addition
        )
        dependent_elsewhere = tax_unit("head_is_dependent_elsewhere", period)
        # Set floor and ceiling around earned income plus additional amount.
        floored_claimable_dep_amount = max_(
            claimable_dep_earned_amount, claimable_dep_floor
        )
        capped_claimable_dep_amount = min_(
            floored_claimable_dep_amount, initial_core_deduction
        )
        core_deduction = where(
            dependent_elsewhere,
            capped_claimable_dep_amount,
            initial_core_deduction,
        )
        # Aged/blind extra standard deduction.
        blind_head = tax_unit("blind_head", period).astype(int)
        blind_spouse = tax_unit("blind_spouse", period).astype(int)
        age_threshold = p.aged_or_blind.age
        aged_head = (tax_unit("age_head", period) >= age_threshold).astype(int)
        aged_spouse = (tax_unit("age_spouse", period) >= age_threshold).astype(
            int
        )
        aged_blind_count = blind_head + blind_spouse + aged_head + aged_spouse
        amount_per_aged_blind = p.aged_or_blind.amount[filing_status]
        aged_blind_deduction = aged_blind_count * amount_per_aged_blind
        return core_deduction + aged_blind_deduction
