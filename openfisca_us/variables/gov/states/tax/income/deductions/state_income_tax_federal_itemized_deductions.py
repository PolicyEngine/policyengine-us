from openfisca_us.model_api import *


class state_income_tax_federal_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Federal itemized deductions also deductible from State taxable income"
    )
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        state = tax_unit.household("state_code_str", period)
        allowed_deductions = parameters(
            period
        ).states.tax.income.deductions.federal_itemized
        value = sum_list_parameter(allowed_deductions, state, tax_unit, period)
        return value * itemizes
