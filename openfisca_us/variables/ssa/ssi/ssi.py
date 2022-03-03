from openfisca_us.model_api import *


class ssi(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income"
    label = "Supplemental Security Income"
    unit = USD

    def formula(person, period, parameters):
        abd = person("is_ssi_aged_blind_disabled", period)
        countable_resources = person("ssi_countable_resources", period)
        ssi = parameters(period).ssa.ssi
        # Only individual is modeled currently.
        resource_limit = ssi.eligibility.resources.limit.individual
        meets_resource_test = countable_resources <= resource_limit
        # Calculate amount.
        amount = ssi.amount.individual * 12
        countable_income = person("ssi_countable_income", period)
        amount_if_eligible = max_(amount - countable_income, 0)
        return abd * meets_resource_test * amount_if_eligible
