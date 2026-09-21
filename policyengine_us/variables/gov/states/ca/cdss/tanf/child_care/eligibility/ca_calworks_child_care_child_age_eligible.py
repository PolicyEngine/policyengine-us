from policyengine_us.model_api import *


class ca_calworks_child_care_child_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the California CalWORKs Child Care based on age"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260AB119",
        "https://www.cdss.ca.gov/ord/entres/getinfo/pdf/14EAS.pdf#page=34",
        "https://www.cdss.ca.gov/ord/entres/getinfo/pdf/4EAS.pdf#page=43",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.child_care.eligibility
        age = person("age", period)
        is_disabled = person("is_disabled", period)
        ordinary_age_eligible = age < p.age_threshold
        court_supervision = person("is_under_court_supervision", period)
        qualifying_supervision = person(
            "ca_calworks_child_care_has_qualifying_court_supervision", period
        )
        school_requirement = person(
            "ca_calworks_child_care_meets_age_18_school_requirement", period
        )
        # MPP 47-201.2 limits both the disabled and court-supervision routes
        # to the MPP 42-101 age: under 18, or 18 with the 42-101.2 school
        # condition.
        extended_age_eligible = (age < p.disabled_age_threshold) | (
            (age == p.disabled_age_threshold) & school_requirement
        )
        disabled_age_eligible = is_disabled & extended_age_eligible
        court_age_eligible = (
            court_supervision & qualifying_supervision & extended_age_eligible
        )
        return ordinary_age_eligible | disabled_age_eligible | court_age_eligible
