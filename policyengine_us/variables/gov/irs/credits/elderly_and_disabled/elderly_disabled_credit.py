from policyengine_us.model_api import *


class elderly_disabled_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Elderly or disabled credit"
    documentation = "Schedule R credit for the elderly and the disabled"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/22"

    def formula(tax_unit, period, parameters):
        credit_limit = tax_unit("elderly_disabled_credit_credit_limit", period)
        potential = tax_unit("elderly_disabled_credit_potential", period)
        return min_(credit_limit, potential)
