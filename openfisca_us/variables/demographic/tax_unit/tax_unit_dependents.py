from openfisca_us.model_api import *


class tax_unit_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of dependents in the tax unit"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        dependent = tax_unit.members("is_tax_unit_dependent", period)
        return tax_unit.sum(where(dependent, 1, 0))
