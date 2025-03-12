from policyengine_us.model_api import *


class nm_itemized_deductions(Variable):
    """
    Minimal stub so that any test input for 'nm_itemized_deductions'
    doesn't break. When the tax filer itemizes, this returns the test input;
    otherwise, it returns 0.
    """

    value_type = float
    entity = TaxUnit
    label = "New Mexico itemized deductions (stub for old tests)"
    unit = "USD"
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        # This will return the user input provided via the YAML test file.
        input_value = tax_unit("nm_itemized_deductions", period)
        return where(itemizes, input_value, 0)
