from policyengine_us.model_api import *


class is_ssi_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Is SSI eligible person"
    definition_period = YEAR

    def formula(person, period, parameters):
        abd_person = person("is_ssi_aged_blind_disabled", period)
        meets_resource_test = person("meets_ssi_resource_test", period)
        is_qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)
        immigration_status = person("immigration_status", period)
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
        meets_immigration_status = is_qualified_noncitizen | is_citizen

        return abd_person & meets_resource_test & meets_immigration_status
