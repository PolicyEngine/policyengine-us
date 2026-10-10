from policyengine_us.model_api import *


class taxsim_v17(Variable):
    value_type = float
    entity = TaxUnit
    label = "Itemized deductions in taxable income in TAXSIM"
    documentation = (
        "TAXSIM-35 v17, 'Itemized Deductions in taxable income': the "
        "itemized deductions when the filer itemizes, otherwise 0."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://taxsim.nber.org/taxsim35/"

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        itemized = tax_unit("itemized_taxable_income_deductions", period)
        return where(itemizes, itemized, 0)
