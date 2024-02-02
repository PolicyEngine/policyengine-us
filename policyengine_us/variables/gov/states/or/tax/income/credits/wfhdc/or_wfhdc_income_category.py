from policyengine_us.model_api import *


class or_wfhdc_income_category(Variable):
    value_type = int
    entity = TaxUnit
    label = "Oregon working family household and dependent care credit percentage table row letter"
    unit = "/1"
    definition_period = YEAR
    defined_for = "or_wfhdc_eligible"
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2021.pdf#page=1"

    def formula(tax_unit, period, parameters):
        # Get the household income, considered the larger of Federal and Oregon AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        or_agi = tax_unit("or_agi", period)
        household_income = max_(federal_agi, or_agi)
        # The credit percentage is based on the percentage of the tax unit fpg
        fpg = tax_unit("tax_unit_fpg", period)
        fpg_rate = household_income / fpg
        # The rate can not drop below 0%.
        floored_fpg_rate = max_(fpg_rate, 0)
        # The rate can not exceed 300%.
        return np.ceil(floored_fpg_rate * 10)
