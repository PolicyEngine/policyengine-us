from policyengine_us.model_api import *


class il_scretd_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Senior Citizens Real Estate Tax Deferral age eligibility"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.idor.scretd
        age = person("age", period)
        return age >= p.age_threshold
