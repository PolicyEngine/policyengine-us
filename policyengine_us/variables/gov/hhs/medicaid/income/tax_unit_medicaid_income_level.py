from policyengine_us.model_api import *


class tax_unit_medicaid_income_level(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicaid/CHIP-related modified adjusted gross income (MAGI) level"
    unit = "/1"
    documentation = (
        "Medicaid/CHIP-related MAGI as fraction of federal poverty line."
        "Documentation: 'Federal poverty level (FPL)' at the following URL:"
        "URL: https://www.healthcare.gov/glossary/federal-poverty-level-fpl/"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income = tax_unit("medicaid_magi", period)
        fpg = tax_unit("tax_unit_fpg", period)
        return income / fpg
