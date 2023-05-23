from policyengine_us.model_api import *


class senior_head(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit head is a senior"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        senior = person("is_senior", period)
        head = person("is_tax_unit_head", period)
        return tax_unit.any(senior & head)
