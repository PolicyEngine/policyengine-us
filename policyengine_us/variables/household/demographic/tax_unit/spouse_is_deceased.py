from policyengine_us.model_api import *


class spouse_is_deceased(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit spouse is deceased"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        deceased = person("is_deceased", period)
        spouse = person("is_tax_unit_spouse", period)
        return tax_unit.any(deceased & spouse)
