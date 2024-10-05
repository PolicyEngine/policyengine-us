from policyengine_us.model_api import *


class or_wfhdc_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Income eligible for the Oregon working family household and dependent care credit"
    documentation = "Oregon Working Family Household and Dependent Care Credit household eligibility"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1",
        "https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["or"].tax.income.credits.wfhdc

        # Get the income threshold based on household size.
        fpg = tax_unit("tax_unit_fpg", period)
        income_threshold = fpg * p.fpg_limit

        # Get household income, the larger of federal and Oregon AGI.
        household_income = tax_unit("or_wfhdc_household_income", period)

        # Check if household income is below the threshold.
        return household_income <= income_threshold
