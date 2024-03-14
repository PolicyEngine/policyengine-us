from policyengine_us.model_api import *


class mt_tax_unit_deductions_exemptions_indiv(Variable):
    value_type = float
    entity = TaxUnit
    label = "The total amount of Montana deductions and exemptions when married filing separately"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        standard_deduction = add(
            tax_unit, period, ["mt_standard_deduction_indiv"]
        )
        itemized_deductions = add(
            tax_unit, period, ["mt_itemized_deductions_indiv"]
        )
        itemizes = tax_unit("mt_tax_unit_itemizes", period)
        return where(itemizes, itemized_deductions, standard_deduction)
