from policyengine_us.model_api import *


class senior_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit spouse is a senior"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        senior = person("is_senior", period)
        spouse = person("is_tax_unit_spouse", period)
        return tax_unit.any(senior & spouse)
