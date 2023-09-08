from policyengine_us.model_api import *


class greater_age_head_spouse(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Age of head or spouse of tax unit depending on which is greater"
    documentation = "Age in years of taxpayer (i.e. primary adult) or spouse (i.e. secondary adult if present), depending on which is greater. "
    unit = "year"

    def formula(tax_unit, period, parameters):
        return max_(
            tax_unit("age_head", period), tax_unit("age_spouse", period)
        )
