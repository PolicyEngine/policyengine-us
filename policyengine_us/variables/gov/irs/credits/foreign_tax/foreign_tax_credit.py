from policyengine_us.model_api import *


class foreign_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Foreign tax credit"
    definition_period = YEAR
    documentation = "Foreign tax credit from Form 1116"
    unit = USD

    def formula(tax_unit, period, parameters):
        return min_(
            tax_unit("foreign_tax_credit_potential", period),
            tax_unit("foreign_tax_credit_credit_limit", period),
        )
