from policyengine_us.model_api import *


class ri_property_tax_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Rhode Island total household income for the property tax computation"
    )
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%20RI-1040H_v2_w.pdf#page=2"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR
    adds = ["ri_household_income"]
    subtracts = ["above_the_line_deductions"]
