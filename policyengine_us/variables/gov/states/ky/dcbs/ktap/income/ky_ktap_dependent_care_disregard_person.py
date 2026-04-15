from policyengine_us.model_api import *


class ky_ktap_dependent_care_disregard_person(Variable):
    value_type = float
    entity = Person
    label = "Kentucky K-TAP dependent care disregard per person"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        # Per MS 2840 B.2.c: "only one parent's income"
        # Allocate unit-level dependent care to the primary earner.
        unit_dep_care = person.spm_unit("ky_ktap_dependent_care_disregard", period)
        gross_earned = person("tanf_gross_earned_income", period)
        max_earned = person.spm_unit.max(gross_earned)
        has_most_earnings = gross_earned == max_earned
        is_recipient = has_most_earnings & (gross_earned > 0)
        n_recipients = person.spm_unit.sum(is_recipient * 1.0)
        return where(
            n_recipients > 0,
            unit_dep_care * is_recipient / max_(n_recipients, 1),
            0,
        )
