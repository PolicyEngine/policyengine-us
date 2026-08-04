from policyengine_us.model_api import *


class ca_oc_general_relief_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Orange County General Relief"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2026-01/GR%20Reg%20SECTION%2020%20-%20Approved%20-%20January%202026.pdf#page=3"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.oc.general_relief.eligibility
        age_eligible = person("monthly_age", period) >= p.adult_age_threshold
        immigration_status_eligible = person(
            "ca_oc_general_relief_immigration_status_eligible",
            period,
        )
        receives_other_cash_assistance = person(
            "ca_oc_general_relief_receives_other_cash_assistance",
            period,
        )
        return (
            age_eligible & immigration_status_eligible & ~receives_other_cash_assistance
        )
