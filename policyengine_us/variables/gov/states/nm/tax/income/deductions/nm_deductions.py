from policyengine_us.model_api import *


class nm_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        itemized_on_federal_return = tax_unit("tax_unit_itemizes", period)
        itm_ded = tax_unit("nm_itemized_deductions", period)
        standard_ded = tax_unit("standard_deduction", period)
        itemized_or_standard = where(
            itemized_on_federal_return, itm_ded, standard_ded
        )
        medical_deduction = tax_unit(
            "nm_medical_care_expense_deduction", period
        )
        capital_gains_deduction = tax_unit(
            "nm_net_capital_gains_deduction", period
        )
        return (
            itemized_or_standard + medical_deduction + capital_gains_deduction
        )
