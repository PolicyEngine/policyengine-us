from policyengine_us.model_api import *


class id_income_tax_liable(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Liable to pay income taxes in Idaho"
    definition_period = YEAR
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=10"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        gross_income = add(tax_unit, period, ["irs_gross_income"])
        standard_deduction = tax_unit("standard_deduction", period)
        return gross_income > standard_deduction
