from openfisca_us.model_api import *


class meets_ssi_resource_test(Variable):
    value_type = bool
    entity = MaritalUnit
    label = "Meets SSI resource test"
    unit = USD
    definition_period = YEAR

    def formula(marital_unit, period, parameters):
        person = marital_unit.members
        abd = person("is_ssi_aged_blind_disabled", period)
        joint = marital_unit.sum(abd) > 1
        personal_resources = person("ssi_countable_resources", period)
        countable_resources = marital_unit.sum(personal_resources * abd)
        ssi = parameters(period).ssa.ssi
        resource_limits = ssi.eligibility.resources.limit
        resource_limit = where(
            joint, resource_limits.couple, resource_limits.individual
        )
        return countable_resources <= resource_limit
