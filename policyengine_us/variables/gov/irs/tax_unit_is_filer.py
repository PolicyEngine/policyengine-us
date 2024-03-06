from policyengine_us.model_api import *


class tax_unit_is_filer(Variable):
    value_type = float
    entity = TaxUnit
    label = "files taxes"
    unit = USD
    documentation = (
        "Whether this tax unit has a non-zero income tax liability."
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        total_tax = tax_unit("federal_state_income_tax", period)
        return total_tax != 0
