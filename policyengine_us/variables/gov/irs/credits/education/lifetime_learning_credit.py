from policyengine_us.model_api import *


class lifetime_learning_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Lifetime Learning Credit"
    unit = USD
    documentation = "Value of the non-refundable Lifetime Learning Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#c"

    def formula(tax_unit, period, parameters):
        credit_limit = tax_unit(
            "lifetime_learning_credit_credit_limit", period
        )
        potential = tax_unit("lifetime_learning_credit_potential", period)
        return min_(credit_limit, potential)
