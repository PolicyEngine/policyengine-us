from policyengine_us.model_api import *


class ky_ktap_dependent_care_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP dependent care disregard"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        # NOTE: Full-time/part-time distinction not modeled.
        p = parameters(period).gov.states.ky.dcbs.ktap.income.deductions
        person = spm_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        # Per 921 KAR 2:016 Section 5(3)(b)1.b, the disregard covers an
        # incapacitated adult living in the home and receiving KTAP.
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        age = person("age", period.this_year)
        # Children use their age-based rate; the older-age zero-out reflects
        # children aging out of care. An incapacitated adult instead receives
        # the standard age-two-or-older rate per 921 KAR 2:016 Section
        # 5(3)(b)2, so evaluate the schedule at the age-two boundary for them.
        cap_age = where(incapacitated_adult, p.dependent_care.thresholds[1], age)
        care_recipient = is_dependent | incapacitated_adult
        max_per_person = p.dependent_care.calc(cap_age) * care_recipient
        total_max_disregard = spm_unit.sum(max_per_person)
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        return min_(childcare_expenses + adult_care_expenses, total_max_disregard)
