from policyengine_us.model_api import *


class hi_cdcc_min_head_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii minimum income between head and spouse for the CDCC"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=29"
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=41"
        "https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=2"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        earnings = person("earned_income", period)
        # Head or spouse are eligible for an income floor if disabled or a student
        # Start with case with only one floor-eligible spouse.
        qualified_children = person.tax_unit("count_cdcc_eligible", period)
        # Floor depends on number of eligible dependents
        floor = p.disabled_student_income_floor.calc(qualified_children)
        floor_eligible = person("hi_cdcc_income_floor_eligible", period)
        potential_floored_earnings = max_(floor, earnings)
        # floored_earnings = where(floor_eligible, floored_earnings, earnings)
        floored_earnings = where(
            floor_eligible, potential_floored_earnings, earnings
        )
        # To take the lesser of head or spouse floored earnings,
        # assign infinite earnings to dependents.
        lesser_floored_earnings = tax_unit.min(
            where(head_or_spouse, floored_earnings, np.inf)
        )
        # Case with two floor-eligible spouses:
        # If both spouses are students or disabled, only one can claim the floor.
        # To maximize the credit value, since the credit phases in with respect to (floored) earnings,
        # the filer should floor the spouse with the smaller earnings.
        # Note that the phase-out is separate and with respect to AGI.
        # Ignore the floor, just take the greater unfloored earnings.
        # This is equivalent to only applying the floor to one spouse (that with lesser earnings).
        head_or_spouse_earning = head_or_spouse * earnings
        greater_earnings = tax_unit.max(head_or_spouse_earning)
        # Select based on number of floored.
        count_floor_eligible = tax_unit.sum(head_or_spouse * floor_eligible)
        not_both_eligible_above_floor = (count_floor_eligible == 2) & (
            tax_unit.sum(head_or_spouse_earning > floor) != 2
        )

        return where(
            not_both_eligible_above_floor,
            greater_earnings,
            lesser_floored_earnings,
        )
