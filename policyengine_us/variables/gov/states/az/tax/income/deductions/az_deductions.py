from policyengine_us.model_api import *


class az_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = "https://azdor.gov/sites/default/files/2023-08/FORMS_INDIVIDUAL_2022_140f.pdf"  # Line 43

    def formula(tax_unit, period, parameters):
        itemized_ded = tax_unit("az_itemized_deductions", period)
        standard_ded = tax_unit("az_standard_deduction", period)
        return max_(itemized_ded, standard_ded)
