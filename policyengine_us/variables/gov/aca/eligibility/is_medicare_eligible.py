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
        MEDICARE_ELIGILITY_AGE = 65
        return person("age", period) >= MEDICARE_ELIGILITY_AGE
