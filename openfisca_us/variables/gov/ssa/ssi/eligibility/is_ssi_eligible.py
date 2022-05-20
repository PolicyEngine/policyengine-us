from openfisca_us.model_api import *


class is_ssi_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligibility for Supplemental Security Income"

    def formula(person, period, parameters):
        abd = person("is_ssi_aged_blind_disabled", period)
        meets_resource_test = person.marital_unit("meets_ssi_resource_test")
        return abd & meets_resource_test
