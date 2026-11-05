from policyengine_us.model_api import *


class ky_ktap_incapacitated_adult_care_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP dependent care disregard for incapacitated adults"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        # Per 921 KAR 2:016 Section 5(3)(b)1.b, the disregard covers an
        # incapacitated adult living in the home and receiving KTAP.
        p = parameters(period).gov.states.ky.dcbs.ktap.income.deductions
        person = spm_unit.members
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        # Section 5(3)(b)2 caps the care of each individual. An incapacitated
        # adult receives the standard age-two-or-older rate, so evaluate the
        # schedule at the age-two boundary.
        max_per_adult = p.dependent_care.calc(p.dependent_care.thresholds[1])
        adult_care_expenses = person("care_expenses", period) * incapacitated_adult
        return spm_unit.sum(min_(adult_care_expenses, max_per_adult))
