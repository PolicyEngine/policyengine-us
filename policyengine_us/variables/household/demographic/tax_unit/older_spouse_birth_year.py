from policyengine_us.model_api import *


class older_spouse_birth_year(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Birth year of head or spouse of tax unit depending on which is greater"
    documentation = "Birth year of taxpayer (i.e. primary adult) or spouse (i.e. secondary adult if present), depending on which is greater. "
    unit = "year"

    def formula(tax_unit, period, parameters):
        return period.start.year - tax_unit("greater_age_head_spouse", period)
