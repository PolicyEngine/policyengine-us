from policyengine_us.model_api import *


class nm_works_earned_income_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "New Mexico Works earned income deduction (person)"
    unit = USD
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
    defined_for = StateCode.NM

    def formula(person, period, parameters):
        # Per 8.102.520.12 NMAC, earned income deduction is:
        # Flat amount + 50% of remainder
        p = parameters(period).gov.states.nm.hca.nm_works.income.deductions

        gross_earned = person("tanf_gross_earned_income", period)
        is_parent = person("is_parent", period.this_year)

        # Count parents in the SPM unit to determine single vs two-parent
        spm_unit = person.spm_unit
        parent_count = add(spm_unit, period, ["is_parent"])

        # Flat deduction depends on single vs two-parent
        single_parent_flat = p.work_incentive.single_parent.amount
        two_parent_flat = p.work_incentive.two_parent.amount
        other_member_flat = p.work_incentive.other_member.amount
        disregard_rate = p.work_incentive.rate

        # Parents get $225 in two-parent families, $125 in single-parent
        # Non-parents get $125 flat (other member)
        is_two_parent = parent_count >= 2
        parent_flat = where(is_two_parent, two_parent_flat, single_parent_flat)
        flat_amount = where(is_parent, parent_flat, other_member_flat)

        # Step 1: Subtract flat amount (not to exceed earnings)
        flat_deduction = min_(flat_amount, gross_earned)
        after_flat = max_(gross_earned - flat_deduction, 0)

        # Step 2: 50% disregard on remainder
        percentage_deduction = after_flat * disregard_rate

        return flat_deduction + percentage_deduction
