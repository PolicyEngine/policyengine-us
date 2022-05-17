from openfisca_us.model_api import *


class marital_unit_ssi(Variable):
    value_type = float
    entity = MaritalUnit
    definition_period = YEAR
    documentation = "Supplemental Security Income"
    label = "Supplemental Security Income"
    unit = USD

    def formula(marital_unit, period, parameters):
        person = marital_unit.members
        abd = person("is_ssi_aged_blind_disabled", period)
        joint = marital_unit.sum(abd) > 1
        personal_resources = person("ssi_countable_resources", period)
        countable_resources = marital_unit.sum(personal_resources * abd)
        ssi = parameters(period).ssa.ssi
        resource_limits = ssi.eligibility.resources.limit
        resource_limit = where(
            joint, resource_limits.individual, resource_limits.couple
        )
        meets_resource_test = countable_resources <= resource_limit
        amount = MONTHS_IN_YEAR * where(
            joint, ssi.amount.couple, ssi.amount.individual
        )
        personal_income = person("ssi_countable_income", period)
        countable_income = marital_unit.sum(personal_income * abd)
        amount_if_eligible = max_(amount - countable_income, 0)
        return abd * meets_resource_test * amount_if_eligible
