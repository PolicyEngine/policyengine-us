from policyengine_us.model_api import *


class ut_dependents_under_17(Variable):
    value_type = int
    entity = TaxUnit
    label = "Utah dependents under 17"
    unit = USD
    documentation = "Form TC-40, line 2a"
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_tax_unit_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        return tax_unit.sum(is_tax_unit_dependent * (age < 17))
