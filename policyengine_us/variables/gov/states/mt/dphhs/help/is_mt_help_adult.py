from policyengine_us.model_api import *


class is_mt_help_adult(Variable):
    value_type = bool
    entity = Person
    label = "Montana HELP adult"
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = "https://dphhs.mt.gov/assets/MedicaidTribalConsultation/December2022/MedicaidExpansionProgramFactSheet2023.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.adult.age_range
        age = person("age", period)
        return p.calc(age)
