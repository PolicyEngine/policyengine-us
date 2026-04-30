from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class tax_unit_medicaid_income_level(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicaid/CHIP-related modified adjusted gross income (MAGI) level"
    unit = "/1"
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.603",
        "https://www.healthcare.gov/glossary/federal-poverty-level-fpl/",
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income = tax_unit("medicaid_magi", period)
        pregnant_count = add(tax_unit, period, ["current_pregnancies"])
        tax_unit_size = tax_unit("tax_unit_size", period)
        state_group = tax_unit.household("state_group_str", period)
        return income / fpg(
            pregnant_count + tax_unit_size, state_group, period, parameters
        )
