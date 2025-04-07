from policyengine_us.model_api import *


class or_wfhdc_household_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Household income for the Oregon working family household and dependent care credit"
    documentation = "Larger of federal and state AGI"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1",
        "https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # Get household income, the larger of federal and Oregon AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        or_agi = tax_unit("or_agi", period)
        return max_(federal_agi, or_agi)
