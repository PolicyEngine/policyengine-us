from policyengine_us.model_api import *


class or_wfhdc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Oregon working family household and dependent care credit"
    documentation = "Oregon Working Family Household and Dependent Care Credit household eligibility"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1",
        "https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        household_size_eligible = tax_unit(
            "or_wfhdc_household_size_eligible", period
        )
        income_eligible = tax_unit("or_wfhdc_income_eligible", period)
        has_qualified_individual = tax_unit(
            "or_wfhdc_has_qualified_individual_eligible", period
        )
        employment_eligible = tax_unit("or_wfhdc_employment_eligible", period)

        return (
            household_size_eligible
            & income_eligible
            & has_qualified_individual
            & employment_eligible
        )
