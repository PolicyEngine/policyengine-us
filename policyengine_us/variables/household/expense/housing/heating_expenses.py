from policyengine_us.model_api import *


class heating_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit heating cost"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Heating bills attach to the dwelling: read the SPM unit's heating
        # expense through the tax unit head.
        heating = person.spm_unit("heating_expense", period)
        is_head = person("is_tax_unit_head", period)
        return tax_unit.sum(heating * is_head)
