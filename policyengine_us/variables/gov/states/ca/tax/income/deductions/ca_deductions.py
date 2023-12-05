from policyengine_us.model_api import *


class ca_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "California deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"
        "https://www.ftb.ca.gov/forms/2022/2022-540.pdf"
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        std_ded = tax_unit("ca_standard_deduction", period)
        itm_ded = tax_unit("ca_itemized_deductions", period)
        return where(itm_ded > std_ded, itm_ded, std_ded)
