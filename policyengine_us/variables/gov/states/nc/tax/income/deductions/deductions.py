from policyengine_us.model_api import *


class nc_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NC deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions"
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        return max_(
            tax_unit("nc_itemized_deductions", period),
            tax_unit("nv_standard_deductions", period),
        )