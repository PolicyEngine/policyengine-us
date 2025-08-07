from policyengine_us.model_api import *


class is_tce_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Tax Counseling for the Elderly program"
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/individuals/tax-counseling-for-the-elderly"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.tce
        age = person("age", period)
        return age >= p.age_threshold
