from policyengine_us.model_api import *


class il_tanf_demographic_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for Illinois Temporary Assistance for Needy Families (TANF) based on demographics"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.60",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        eligible_child = person("il_tanf_eligible_child", period)
        pregnant = person("is_pregnant", period)
        return eligible_child | pregnant
