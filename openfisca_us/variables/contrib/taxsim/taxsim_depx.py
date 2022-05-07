from openfisca_us.model_api import *


class taxsim_depx(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of dependents"
    unit = "person"
    documentation = "Number of dependents (for personal exemption calculation). In the case of a file submission, if no age1 or dep19 variable is present, depx is used for the number of eligible children. You can negate this assumption by putting a large number (such as 99) in the age1 field."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        return tax_unit.sum(is_dependent)
