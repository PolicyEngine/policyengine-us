from policyengine_us.model_api import *


class nc_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    adds = ["adjusted_gross_income", "nc_additions"]
    subtracts = ["nc_deductions"]
