from policyengine_us.model_api import *


class ut_personal_exemption_additional_dependent_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Utah additional dependent personal exemption eligible"
    defined_for = StateCode.UT
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1018.html"  # 59-10-1018 (1)(g)

    def formula(person, period, parameters):
        is_dependent = person("is_tax_unit_dependent", period)
        birth_year = person("birth_year", period)
        born_this_year = birth_year == period.start.year
        return is_dependent & born_this_year
