from policyengine_us.model_api import *


class ia_liheap_targeting_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Iowa LIHEAP targeting factor points"
    documentation = (
        "Net payment matrix points from the nine targeting factors: fixed "
        "income only, elderly, disabled, young child and detached dwelling add "
        "points; a building of five or more units, subsidized housing, heating "
        "included in rent and savings above the threshold subtract points. One "
        "adjustment applies per factor per household however many members "
        "qualify. Disability is self-declared in Iowa and is approximated by "
        "is_disabled; savings are approximated by bank, stock and bond assets."
    )
    reference = (
        # Section 4.40 item 4 savings description; Definitions, Disabled,
        # Elderly, Fixed Income Household, Subsidized Housing and Young Child;
        # Appendix I item 2, Targeting Factors.
        # PDF pages 14, 80-81, 84-85, 137
        "https://hhs.iowa.gov/media/17262/download?inline#page=14",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/IA_BenefitMatrix_Heat-Crisis_2026.pdf#page=1",
        # Section 2.4: the matrix "awards additional benefit amounts for
        # households with members that are elderly, disabled, and/or have
        # young children".
        "https://liheapch.acf.gov/docs/2026/state-plans/IA_Plan_2026.pdf#page=9",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.payment.targeting
        age = spm_unit.members("age", period)
        fixed_income_only = spm_unit("ia_liheap_fixed_income_only", period)
        # Definitions: Elderly is "60 years of age or older"; Young Child is
        # "under six years of age"; Disabled: "applicants self-declare a
        # disability".
        has_elderly = spm_unit.any(age >= p.elderly_age)
        has_disabled = add(spm_unit, period, ["is_disabled"]) > 0
        has_young_child = spm_unit.any(age < p.young_child_age)
        dwelling = spm_unit("ia_liheap_dwelling_type", period)
        dwellings = dwelling.possible_values
        detached = dwelling == dwellings.DETACHED
        five_plex = dwelling == dwellings.ATTACHED_5_OR_MORE_UNITS
        # Definitions, Subsidized Housing: assistance "provided by a government
        # agency or a non-profit program" (Section 8, TBRA, Section 202, public
        # housing, VASH, income-restricted apartments).
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # Section 4.40 item 4 describes the savings test as interest and
        # dividend-bearing accounts, cash on hand, CDs and "other investments
        # that can be accessed without penalty".
        high_savings = spm_unit("spm_unit_cash_assets", period) > p.savings_threshold
        # Appendix I lists each factor once with a single point value, so each
        # factor adjusts the household total once (stacking is not addressed).
        points = p.fixed_income * fixed_income_only
        points = points + p.elderly * has_elderly
        points = points + p.disabled * has_disabled
        points = points + p.young_child * has_young_child
        points = points + p.detached_dwelling * detached
        points = points + p.five_plex * five_plex
        points = points + p.subsidized_housing * subsidized
        points = points + p.heat_in_rent * heat_in_rent
        points = points + p.savings * high_savings
        return points
