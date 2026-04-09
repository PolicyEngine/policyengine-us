from policyengine_us.model_api import *


class spm_unit_head_spouse_earned_cap(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit lower-earner cap for the reference person and spouse/partner"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_reference_person = person("is_household_head", period)
        has_reference_person = spm_unit.any(is_reference_person)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_reference_person_spouse = (
            person.tax_unit.any(is_reference_person)
            & is_head_or_spouse
            & ~is_reference_person
        )
        is_reference_person_partner = person(
            "is_unmarried_partner_of_household_head", period
        )
        has_spouse = spm_unit.any(is_reference_person_spouse)
        eligible_reference_person_or_partner = (
            is_reference_person
            | is_reference_person_spouse
            | (~has_spouse & is_reference_person_partner)
        )
        eligible_people = where(
            has_reference_person,
            eligible_reference_person_or_partner,
            is_head_or_spouse,
        )
        earned_income = person("spm_work_childcare_earnings", period)
        eligible_earnings = eligible_people * np.maximum(earned_income, 0)

        count_head_or_spouse = spm_unit.sum(eligible_people)
        total_earned = spm_unit.sum(eligible_earnings)
        max_earned = spm_unit.max(eligible_earnings)

        return where(count_head_or_spouse > 1, total_earned - max_earned, total_earned)
