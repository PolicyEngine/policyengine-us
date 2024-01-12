from policyengine_us.model_api import *


class is_medicare_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for Medicare"
    definition_period = YEAR
    documentation = (
        "CMS, Original Medicare (Part A and B) Eligibility and Enrollment"
        "https://www.cms.gov/medicare/enrollment-renewal/health-plans/original-part-a-b"
        "Above link includes the following text:"
        "  Part A coverage begins the month the individual turns age 65"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.eligibility
        is_age_eligible = person("age", period) >= p.min_age
        gets_ssdi = person("social_security_disability", period) > 0
        months = person("months_receiving_social_security_disability", period)
        is_disability_eligible = gets_ssdi & (
            months >= p.min_months_receiving_social_security_disability
        )
        return is_age_eligible | is_disability_eligible
