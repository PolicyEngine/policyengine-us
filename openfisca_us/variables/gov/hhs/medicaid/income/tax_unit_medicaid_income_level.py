from openfisca_us.model_api import *


class tax_unit_medicaid_income_level(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicaid income level"
    unit = "/1"
    documentation = (
        "Income for Medicaid as a percentage of the federal poverty line."
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income = tax_unit("medicaid_income", period)
        fpg = tax_unit("tax_unit_fpg", period)
        return income / fpg
