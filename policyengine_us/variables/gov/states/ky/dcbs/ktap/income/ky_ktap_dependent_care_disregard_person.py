from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ky.dcbs.ktap.income.ky_ktap_earned_income_helpers import (
    ky_ktap_dependent_care_share,
)


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
        return unit_dep_care * ky_ktap_dependent_care_share(person, period)
